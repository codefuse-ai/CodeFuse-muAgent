from loguru import logger
import re
import json
from typing import List, Dict
import numpy as np
import random
import uuid
from redis.commands.search.field import (
    TextField,
    NumericField,
    VectorField,
    TagField
)
from jieba.analyse import extract_tags


from muagent.schemas.ekg import *
from muagent.schemas.db import *
from muagent.schemas.common import *
from muagent.db_handler import *
from muagent.orm import table_init

from muagent.connector.configs.generate_prompt import *

from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.llm_models import *


from muagent.base_configs.env_config import KB_ROOT_PATH

from muagent.llm_models.get_embedding import get_embedding
from muagent.utils.common_utils import getCurrentDatetime, getCurrentTimestap
from muagent.utils.common_utils import double_hashing


def getClassFields(model):
    # 收集所有字段，包括继承自父类的字段
    all_fields = set(model.__annotations__.keys())
    for base in model.__bases__:
        if hasattr(base, '__annotations__'):
            all_fields.update(getClassFields(base))
    return all_fields


class EKGConstructService:

    def __init__(
            self, 
            embed_config: EmbedConfig,
            llm_config: LLMConfig,
            db_config: DBConfig = None,
            vb_config: VBConfig = None,
            gb_config: GBConfig = None,
            tb_config: TBConfig = None,
            sls_config: SLSConfig = None,
            do_init: bool = False,
            kb_root_path: str = KB_ROOT_PATH,
        ):

        self.db_config = db_config
        self.vb_config = vb_config
        self.gb_config = gb_config
        self.tb_config = tb_config
        self.sls_config = sls_config
        self.do_init = do_init
        self.kb_root_path = kb_root_path
        self.embed_config: EmbedConfig = embed_config
        self.llm_config: LLMConfig = llm_config
        self.node_indexname = "shanshi_node" # "opsgptkg_node"
        self.edge_indexname = "shanshi_edge" # "opsgptkg_edge"

        # get llm model
        self.model = getChatModelFromConfig(self.llm_config)
        # init db handler
        self.init_handler()

    def init_handler(self, ):
        """Initializes Database VectorBase GraphDB TbaseDB"""
        self.init_vb()
        # self.init_db()
        self.init_tb()
        self.init_gb()

    def reinit_handler(self, do_init: bool=False):
        self.init_vb()
        # self.init_db()
        self.init_tb()
        self.init_gb()

    def init_tb(self, do_init: bool=None):

        DIM = 768 # it depends on your embedding model vector
        NODE_SCHEMA = [
            NumericField("ID", ),
            TextField("node_id", ),
            TextField("node_type", ),
            TextField("node_str", ),
            VectorField("name_vector",
                        'FLAT',
                        {
                            "TYPE": "FLOAT32",
                            "DIM": DIM,
                            "DISTANCE_METRIC": "COSINE"
                        }),
            VectorField("desc_vector",
                        'FLAT',
                        {
                            "TYPE": "FLOAT32",
                            "DIM": DIM,
                            "DISTANCE_METRIC": "COSINE"
                        }),
            TagField(name='name_keyword', separator='|'),
            TagField(name='desc_keyword', separator='|')
        ]

        EDGE_SCHEMA = [
            TextField("edge_id", ),
            TextField("edge_type", ),
            TextField("edge_source", ),
            TextField("edge_target", ),
            TextField("edge_str", ),
        ]


        if self.tb_config:
            tb_dict = {"TbaseHandler": TbaseHandler}
            tb_class =  tb_dict.get(self.tb_config.tb_type, TbaseHandler)
            self.tb: TbaseHandler = tb_class(
                tb_config=self.tb_config, index_name=self.tb_config.index_name, 
                definition_value=self.tb_config.extra_kwargs.get("definition_value", "muagent_ekg")
            )
            # # create index
            if not self.tb.is_index_exists(self.node_indexname):
                res = self.tb.create_index(index_name=self.node_indexname, schema=NODE_SCHEMA)
                logger.info(f"tb init: {res}")

            if not self.tb.is_index_exists(self.edge_indexname):
                res = self.tb.create_index(index_name=self.edge_indexname, schema=EDGE_SCHEMA)
                logger.info(f"tb init: {res}")
        else:
            self.tb = None

    def init_gb(self, do_init: bool=None):
        if self.gb_config:
            gb_dict = {"NebulaHandler": NebulaHandler, "NetworkxHandler": NetworkxHandler, "GeaBaseHandler": GeaBaseHandler,}
            gb_class =  gb_dict.get(self.gb_config.gb_type, NebulaHandler)
            self.gb: GBHandler = gb_class(self.gb_config)
        else:
            self.gb = None

    def init_db(self, do_init: bool=None):
        if self.db_config:
            table_init()
            db_dict = {"LocalFaissHandler": LocalFaissHandler}
            db_class =  db_dict.get(self.db_config.db_type)
            self.db = db_class(self.db_config)
        else:
            self.db = None

    def init_vb(self, do_init: bool=None):
        if self.vb_config:
            vb_dict = {"LocalFaissHandler": LocalFaissHandler}
            vb_class =  vb_dict.get(self.vb_config.vb_type, LocalFaissHandler)
            self.vb: LocalFaissHandler = vb_class(self.embed_config, vb_config=self.vb_config)
        else:
            self.vb = None

    def init_sls(self, do_init: bool=None):
        if self.sls_config:
            sls_dict = {"AliYunSLSHandler": AliYunSLSHandler}
            sls_class =  sls_dict.get(self.sls_config.sls_type, AliYunSLSHandler)
            self.sls: AliYunSLSHandler = sls_class(self.embed_config, vb_config=self.vb_config)
        else:
            self.sls = None
    
    def update_graph(
            self, 
            origin_nodes: List[GNode], origin_edges: List[GEdge], 
            new_nodes: List[GNode], new_edges: List[GEdge],  teamid: str
        ):
        # 
        origin_nodeids = set([node["id"] for node in origin_nodes])
        origin_edgeids = set([f"{edge['start_id']}__{edge['end_id']}" for edge in origin_edges])
        nodeids = set([node["id"] for node in new_nodes])
        edgeids = set([f"{edge['start_id']}__{edge['end_id']}" for edge in new_edges])
        unique_nodeids = origin_nodeids&nodeids
        unique_edgeids = origin_edgeids&edgeids
        nodeid2nodes_dict = {}
        for node in origin_nodes + new_nodes:
            nodeid2nodes_dict.setdefault(node["id"], []).append(node)

        edgeid2edges_dict = {}
        for edge in origin_edges + new_edges:
            edgeid2edges_dict.setdefault(f"{edge['start_id']}__{edge['end_id']}", []).append(edge)

        # get add nodes & edges 
        add_nodes = [node for node in new_nodes if node["id"] not in origin_nodeids]
        add_edges = [edge for edge in new_edges if f"{edge['start_id']}__{edge['end_id']}" not in origin_edgeids]

        # get delete nodes & edges
        delete_nodes = [node for node in origin_nodes if node["id"] not in nodeids]
        delete_edges = [edge for edge in origin_edges if f"{edge['start_id']}__{edge['end_id']}" not in edgeids]

        # get update nodes & edges
        update_nodes = [
            nodeid2nodes_dict[nodeid][1] 
            for nodeid in unique_nodeids 
            if nodeid2nodes_dict[nodeid][0]!=nodeid2nodes_dict[nodeid][1]
        ]
        update_edges = [
            edgeid2edges_dict[edgeid][1] 
            for edgeid in unique_edgeids 
            if edgeid2edges_dict[edgeid][0]!=edgeid2edges_dict[edgeid][1]
        ]
        
        # 
        add_node_result = self.add_nodes([GNode(**n) for n in add_nodes], teamid)
        add_edge_result = self.add_edges([GEdge(**e) for e in add_edges], teamid)

        delete_edge_result = self.delete_nodes([GNode(**n) for n in delete_nodes], teamid)
        delete_node_result = self.delete_edges([GEdge(**e) for e in delete_edges], teamid)

        update_node_result = self.update_nodes([GNode(**n) for n in update_nodes], teamid)
        update_edge_result = self.update_edges([GEdge(**e) for e in update_edges], teamid)

        return [add_node_result, add_edge_result, delete_edge_result, delete_node_result, update_node_result, update_edge_result]


    def add_nodes(self, nodes: List[GNode], teamid: str):
        nodes = self._update_new_attr_for_nodes(nodes, teamid, do_check=True)

        tbase_nodes = []
        for node in nodes:
            tbase_nodes.append({
                **{
                    "ID": node.attributes.get("ID", 0) or double_hashing(node.id),
                    "node_id": f"{node.id}",
                    "node_type": node.type, 
                    "node_str": f"graph_id={teamid}",
                }, 
                **self._update_tbase_attr_for_nodes(node.attributes)
                })

        tb_result, gb_result = [], []
        try: 
            gb_result = [self.gb.add_node(node) for node in nodes]
            tb_result.append(self.tb.insert_data_hash(tbase_nodes, key='node_id', need_etime=False))
        except Exception as e:
            logger.error(e)
        return gb_result + tb_result

    def add_edges(self, edges: List[GEdge], teamid: str):
        edges = self._update_new_attr_for_edges(edges, teamid)
        tbase_edges = [{
            # 'edge_id': f"ekg_edge:{teamid}{edge.start_id}:{edge.end_id}",
            'edge_id': f"{edge.start_id}__{edge.end_id}",
            'edge_type': edge.type,
            'edge_source': edge.start_id,
            'edge_target': edge.end_id,
            'edge_str': f'graph_id={teamid}'
            }
            for edge in edges
        ]

        tb_result, gb_result = [], []
        try:
            gb_result = [self.gb.add_edge(edge) for edge in edges]
            tb_result.append(self.tb.insert_data_hash(tbase_edges, key="edge_id", need_etime=False))
        except Exception as e:
            logger.error(e)
        return gb_result + tb_result

    def delete_nodes(self, nodes: List[GNode], teamid: str=''):
        # delete tbase nodes
        # r = self.tb.search(f"@node_str: 'graph_id={teamid}'", index_name=self.node_indexname)
        r = self.tb.search(f"@node_str: *{teamid}*", index_name=self.node_indexname, limit=len(nodes))

        tbase_nodeids = [data['node_id'] for data in r.docs] # 附带了definition信息
        # tbase_nodeids_dict = {data["node_id"]:data['id'] for data in r.docs} # 附带了definition信息
        delete_nodeids = [node.id for node in nodes]
        tbase_missing_nodeids = [nodeid for nodeid in delete_nodeids if nodeid not in tbase_nodeids]
        # delete_tbase_nodeids = [nodeid for nodeid in delete_nodeids if nodeid in tbase_nodeids]
        # delete_tbase_nodeids = [tbase_nodeids_dict[nodeid] for nodeid in delete_nodeids if nodeid in tbase_nodeids]

        if len(tbase_missing_nodeids) > 0:
            logger.error(f"there must something wrong! ID not match, such as {tbase_missing_nodeids}")

        node_neighbor_lens = [
            len([
                n.id # reverse neighbor nodes which are not in delete nodes
                for n in self.gb.get_neighbor_nodes({"id": node.id}, node.type, reverse=False)
                if n.id not in delete_nodeids])
            for node in nodes
        ]
        # delete the nodeids in tbase
        tb_result = []
        for node, node_len in zip(nodes, node_neighbor_lens):
            if node_len >= 1: continue
            resp = self.tb.delete(node.id)
            tb_result.append(resp)

        # # delete the nodeids in geabase
        gb_result = []
        for node, node_len in zip(nodes, node_neighbor_lens):
            if node_len >= 1: continue
            gb_result.append(self.gb.delete_node(
                {"id": node.id}, node.type, ID=node.attributes.get("ID") or double_hashing(node.id)
            ))
        return gb_result + tb_result
    
    def delete_edges(self, edges: List[GEdge], teamid: str):
        # delete tbase nodes
        # r = self.tb.search(f"@edge_str: 'graph_id={teamid}'", index_name=self.edge_indexname)
        r = self.tb.search(f"@edge_str: *{teamid}*", index_name=self.edge_indexname, limit=len(edges))

        tbase_edgeids = [data['edge_id'] for data in r.docs]
        # tbase_edgeids_dict = {data["edge_id"]:data['id'] for data in r.docs} # id附带了definition信息
        delete_edgeids = [f"{edge.start_id}__{edge.end_id}" for edge in edges]
        tbase_missing_edgeids = [edgeid for edgeid in delete_edgeids if edgeid not in tbase_edgeids]
        # delete_tbase_edgeids = [edgeid for edgeid in delete_edgeids if edgeid in tbase_edgeids]
        # delete_tbase_edgeids = [tbase_edgeids_dict[edgeid] for edgeid in delete_edgeids if edgeid in tbase_edgeids]

        if len(tbase_missing_edgeids) > 0:
            logger.error(f"there must something wrong! ID not match, such as {tbase_missing_edgeids}")
        # delete the edgeids in tbase
        tb_result = []
        for edgeid in delete_edgeids:
            resp = self.tb.delete(edgeid)
            tb_result.append(resp)

        # # delete the nodeids in geabase
        gb_result = []
        for edge in edges:
            gb_result.append(self.gb.delete_edge(
                edge.attributes.get("SRCID") or double_hashing(edge.start_id), 
                edge.attributes.get("DSTID") or double_hashing(edge.end_id), 
                edge.type
            ))
        return gb_result + tb_result
    
    def update_nodes(self, nodes: List[GNode], teamid: str):
        # delete tbase nodes
        # r = self.tb.search(f"@node_str: 'graph_id={teamid}'", index_name=self.node_indexname)
        r = self.tb.search(f"@node_str: *{teamid}*", index_name=self.node_indexname, limit=len(nodes))
        teamids_by_nodeid = {data['node_id']: data["node_str"]  for data in r.docs}

        tbase_nodeids = [data['node_id'] for data in r.docs] # 附带了definition信息
        update_nodeids = [node.id for node in nodes]
        tbase_missing_nodeids = [nodeid for nodeid in update_nodeids if nodeid not in tbase_nodeids]
        # update_tbase_nodeids = [nodeid for nodeid in update_nodeids if nodeid in tbase_nodeids]

        if len(tbase_missing_nodeids) > 0:
            logger.error(f"there must something wrong! ID not match, such as {tbase_missing_nodeids}")
            for node in nodes:
                r = self.tb.search(f"@node_id: {node.id}", index_name=self.node_indexname)
                teamids_by_nodeid.update({data['node_id']: data["node_str"]  for data in r.docs})

        tb_result = []
        for node in nodes:
            # 
            tbase_data = {}
            tbase_data["node_id"] = node.id
            if teamid not in teamids_by_nodeid[node.id]:
                tbase_data["teamids"] = teamids_by_nodeid[node.id] + f", {teamid}"
            tbase_data.update(self._update_tbase_attr_for_nodes(node.attributes))
            # 
            resp = self.tb.insert_data_hash(tbase_data, key="node_id", need_etime=False)
            tb_result.append(resp)

        # update the nodeids in geabase
        nodes = self._update_new_attr_for_nodes(nodes, teamid, teamids_by_nodeid, do_check=False)
        gb_result = []
        for node in nodes:
            # if node.id not in update_tbase_nodeids: continue
            resp = self.gb.update_node(
                {}, node.attributes, node_type=node.type, 
                ID=node.attributes.get("ID") or double_hashing(node.id)
            )
            gb_result.append(resp)
        return gb_result or tb_result

    def update_edges(self, edges: List[GEdge], teamid: str):
        r = self.tb.search(f"@edge_str: *{teamid}*", index_name=self.node_indexname, limit=len(edges))
        teamids_by_edgeid = {data['edge_id']: data["edge_str"]  for data in r.docs}

        tbase_edgeids = [data['edge_id'] for data in r.docs]
        delete_edgeids = [f"{edge.start_id}__{edge.end_id}" for edge in edges]
        tbase_missing_edgeids = [edgeid for edgeid in delete_edgeids if edgeid not in tbase_edgeids]

        if len(tbase_missing_edgeids) > 0:
            logger.error(f"there must something wrong! ID not match, such as {tbase_missing_edgeids}")
            for edge in edges:
                r = self.tb.search(f"@edge_id: {edge.start_id}__{edge.end_id}", index_name=self.node_indexname)
                teamids_by_edgeid.update({data['edge_id']: data["node_str"]  for data in r.docs})

        # update the nodeids in geabase
        edges = self._update_new_attr_for_edges(edges, teamid, teamids_by_edgeid, do_check=False, do_update=True)
        gb_result = []
        for edge in edges:
            # if node.id not in update_tbase_nodeids: continue
            resp = self.gb.update_edge(
                edge.attributes.get("SRCID") or double_hashing(edge.start_id), 
                edge.attributes.get("DSTID") or double_hashing(edge.end_id), 
                edge.attributes, edge_type=edge.type
            )
            gb_result.append(resp)
        return gb_result

    def get_node_by_id(self, nodeid: str, node_type:str = None) -> GNode:
        node = self.gb.get_current_node({'id': nodeid}, node_type=node_type)
        extra_attrs = json.loads(node.attributes.pop("extra", "{}"))
        node.attributes.update(extra_attrs)
        return node
    
    def get_graph_by_nodeid(self, nodeid: str, node_type: str, teamid: str=None, hop: int = 10) -> Graph:
        if hop > 14:
            raise Exception(f"hop can't be larger than 14, now hop is {hop}")
        # filter the node which dont match teamid
        result = self.gb.get_hop_infos({'id': nodeid}, node_type=node_type, hop=hop)
        for node in result.nodes:
            extra_attrs = json.loads(node.attributes.pop("extra", "{}"))
            node.attributes.update(extra_attrs)
        for edge in result.edges:
            extra_attrs = json.loads(edge.attributes.pop("extra", "{}"))
            edge.attributes.update(extra_attrs)
        return result

    def search_nodes_by_text(self, text: str, node_type: str = None, teamid: str = None, top_k=5) -> List[GNode]:

        if text is None: return []

        nodeids = []
        # 
        if self.embed_config:
            vector_dict = self._get_embedding(text)
            query_embedding = np.array(vector_dict[text]).astype(dtype=np.float32).tobytes()

            nodeid_with_dist = []
            for key in ["name_vector", "desc_vector"]:
                # base_query = f'(@node_str: graph_id={teamid})=>[KNN {top_k} @{key} $vector AS distance]'
                base_query = f'(*)=>[KNN {top_k} @{key} $vector AS distance]'
                query_params = {"vector": query_embedding}
                r = self.tb.vector_search(base_query, query_params=query_params)

                for i in r.docs:
                    nodeid_with_dist.append((i["ID"], float(i["distance"])))
            
            nodeid_with_dist = sorted(nodeid_with_dist, key=lambda x:x[1], reverse=False)
            for nodeid, dis in nodeid_with_dist:
                if nodeid not in nodeids:
                    nodeids.append(nodeid)

        # search keyword by jieba spliting text
        keywords = extract_tags(text)
        keyword = "|".join(keywords)
        for key in ["name_keyword", "desc_keyword"]:
            r = self.tb.search(f"(@{key}:{{{keyword}}})", index_name=self.node_indexname, limit=30)
            for i in r.docs:
                if i["ID"] not in nodeids:
                    nodeids.append(i["ID"])

        nodes_by_name = self.gb.get_current_nodes({"name": text}, node_type=node_type)
        nodes_by_desc = self.gb.get_current_nodes({"description": text}, node_type=node_type)
        nodes = self.gb.get_nodes_by_ids(nodeids)
        for node in nodes:
            extra_attrs = json.loads(node.attributes.pop("extra", "{}"))
            node.attributes.update(extra_attrs)
        return nodes_by_name + nodes_by_desc + nodes

    def search_rootpath_by_nodeid(self, nodeid: str, node_type: str, rootid: str) -> Graph:
        # rootid = f"{teamid}" # todo check the rootid
        result = self.gb.get_hop_infos({"id": nodeid}, node_type=node_type, hop=15, reverse=True)
        for node in result.nodes:
            extra_attrs = json.loads(node.attributes.pop("extra", "{}"))
            node.attributes.update(extra_attrs)
        for edge in result.edges:
            extra_attrs = json.loads(edge.attributes.pop("extra", "{}"))
            edge.attributes.update(extra_attrs)

        # paths must be ordered from start to end
        paths = result.paths
        new_paths = []
        for path in paths:
            try:
                start_idx = path.index(rootid)
                end_idx = path.index(nodeid)
                new_paths.append(path[start_idx:end_idx+1])
            except:
                pass
        
        nodeid_set = set([nodeid for path in paths for nodeid in path])
        new_nodes = [node for node in result.nodes if node.id in nodeid_set]
        new_edges = [edge for edge in result.edges if edge.start_id in nodeid_set and edge.end_id in nodeid_set]
        return Graph(nodes=new_nodes, edges=new_edges, paths=new_paths)

    def create_ekg(
            self, 
            text: str, 
            teamid: str, 
            service_name: str, 
            intent_text: str = None, 
            intent_nodes: List[str] = [], 
            all_intent_list: List=[],
            do_save: bool = False
        ):

        if intent_nodes:
            ancestor_list = intent_nodes
        elif intent_text:
            ancestor_list, all_intent_list = self.get_intents(intent_text)
        else:
            raise Exception(f"must have intent infomation")
        
        if service_name == "dsl2graph":
            reuslt = self.dsl2graph()
        else: 
            # text2graph
            result = self.text2graph(text, ancestor_list, all_intent_list, teamid)

        # do write
        if do_save:
            self.write2kg(result)

        return result

    def alarm2graph(
            self, 
            alarms: List[dict],
            alarm_analyse_content: dict,
            teamid: str,   
            do_save: bool = False
        ):
        ancestor_list, all_intent_list = self.get_intents_by_alarms(alarms)
        
        graph_datas_by_pathid = {}
        for path_id, diagnose_path in enumerate(alarm_analyse_content["diagnose_path"]):

            content = f"路径:{diagnose_path['name']}\n"
            cur_count = 1
            for idx, step in enumerate(diagnose_path['diagnose_step']):
                step_text = step['content'] if type(step['content']) == str else \
                    step['content']['textInfo']['text']
                step_text = step_text.strip('[').strip(']')
                step_text_no_time = EKGConstructService.remove_time(step_text)
                # continue update
                content += f'''{cur_count}. {step_text_no_time}\n'''
                cur_count += 1
            
            result = self.create_ekg(
                content, teamid, service_name="text2graph", 
                intent_nodes=ancestor_list, all_intent_list=all_intent_list, 
                do_save= do_save
            )
            graph_datas_by_pathid[path_id] = result
        
        return self.returndsl(graph_datas_by_pathid, intents=ancestor_list)

    def yuque2graph(self, **kwargs):
        # get yuque loader
        
        # 
        self.create_ekg()
        # yuque_url, write2kg, intent_node

        # get_graph(yuque_url)
        # graph_id from md(yuque_content)

        # yuque_dsl ==|code2graph|==> node_dict, edge_list, abnormal_dict

        # dsl2graph => write2kg
        pass

    def text2graph(self, text: str, intents: List[str], all_intent_list: List[str], teamid: str) -> dict:
        # generate graph by llm
        result = self.get_graph_by_text(text, ) 
        # convert llm contet to database schema
        sls_graph = self.transform2sls(result, intents, teamid=teamid)
        tbase_graph = self.transform2tbase(sls_graph, teamid=teamid)
        dsl_graph = self.transform2dsl(sls_graph, intents, all_intent_list, teamid=teamid)
        return {"tbase_graph": tbase_graph, "sls_graph": sls_graph, "dsl_graph": dsl_graph}
    
    def dsl2graph(self, ) -> dict:
        # dsl, write2kg, intent_node, graph_id

        # dsl ==|code2graph|==> node_dict, edge_list, abnormal_dict

        # dsl2graph => write2kg
        pass

    def write2kg(self, ekg_sls_data: EKGSlsData, ekg_tbase_data: EKGTbaseData):
        # everytimes, it will add new nodes and edges

        nodes = [TYPE2SCHEMA.get(node.type,)(**node.dict()) for node in ekg_sls_data.nodes]
        nodes = [GNode(id=node.id, type=node.type, attributes=node.attrbutes()) for node in nodes]
        gb_result = self.gb.add_nodes(nodes)

        edges = [TYPE2SCHEMA.get("edge",)(**edge.dict()) for edge in ekg_sls_data.edges]
        edges = [GEdge(start_id=edge.start_id, end_id=edge.end_id, type=edge.type, attributes=edge.attrbutes()) for edge in edges]
        gb_result = self.gb.add_edges(edges)

        nodes = [node.dict() for node in ekg_tbase_data.nodes]
        tb_result = self.tb.insert_data_hash(nodes)
        
        edges = [edge.dict() for edge in ekg_tbase_data.edges]
        tb_result = self.tb.insert_data_hash(edges)

        # dsl2graph => write2kg
        ## delete tbase/graph by graph_id
        ### diff the tabse within newest by graph_id
        ### diff the graph within newest by graph_id
        ## update tbase/graph by graph_id
        pass

    def returndsl(self, graph_datas_by_path: dict, intents: List[str], ) -> dict:
        # 返回值需要返回 dsl 结构的数据用于展示，这里稍微做下数据处理，但主要就需要 dsl 对应的值
        res = {'dsl': '', 'details': {}, 'intent_node_list': intents}

        merge_dsl_nodes, merge_dsl_edges = [], []
        id_sets = set()
        for path_id, graph_datas in graph_datas_by_path.items():
            res['details'][path_id] = {
                'dsl': graph_datas["dsl_graph"],
                'sls': graph_datas["sls_graph"]
            }
            merge_dsl_nodes.extend([node for node in graph_datas["dsl_graph"].nodes if node.id not in id_sets])
            id_sets.update([i.id for i in graph_datas["dsl_graph"].nodes])
            merge_dsl_edges.extend([edge for edge in graph_datas["dsl_graph"].edges if edge.id not in id_sets])
            id_sets.update([i.id for i in graph_datas["dsl_graph"].edges])
        res["dsl"] = {"nodes": merge_dsl_nodes, "edges": merge_dsl_edges}
        return res

    def get_intents(self, alarm_list: list[dict], ) -> EKGIntentResp:
        '''according contents search intents'''
        ancestor_list = set()
        all_intent_list = []
        for alarm in alarm_list:
            ancestor, all_intent = self.get_intent_by_alarm(alarm)
            if ancestor is None:
                continue
            ancestor_list.add(ancestor)
            all_intent_list.append(all_intent)

        return list(ancestor_list), all_intent_list

    def get_intents_by_alarms(self, alarm_list: list[dict], ) -> EKGIntentResp:
        '''according contents search intents'''
        ancestor_list = set()
        all_intent_list = []
        for alarm in alarm_list:
            ancestor, all_intent = self.get_intent_by_alarm(alarm)
            if ancestor is None:
                continue
            ancestor_list.add(ancestor)
            all_intent_list.append(all_intent)

        return list(ancestor_list), all_intent_list
    
    def get_graph_by_text(self, text: str) -> EKGSlsData:
        '''according text generate ekg's raw datas'''
        prompt = createText2EKGPrompt(text)
        content = self.model.predict(prompt)
        # logger.debug(f"{prompt}")
        # logger.debug(f"{content}")
        # get json part from answer
        pat_str = r'\{.*\}'
        match = re.search(pat_str, content, re.DOTALL)
        json_str = match.group(0)
        try:
            node_edge_dict = json.loads(json_str)
        except:
            node_edge_dict = eval(json_str)

        return node_edge_dict
    
    def transform2sls(self, node_edge_dict: dict, pnode_ids: List[str], teamid: str='') -> EKGSlsData:
        # type类型处理也要注意下
        sls_nodes, sls_edges = [], []
        for node_idx, node_info in node_edge_dict['nodes'].items():
            node_type = node_info['type'].lower()
            node_id = str(uuid.uuid4())
            node_info['node_id_new'] = node_id

            ekg_slsdata = EKGGraphSlsSchema(
                id=node_id,
                type='node_' + node_type,
                name=node_info['content'],
                description=node_info['content'],
                tool='',
                need_check='false',
                operation_type='ADD',
                teamids=teamid
            )
            sls_nodes.append(ekg_slsdata)

            # 追加边关系
            if node_idx == '0':
                for pid in pnode_ids:
                    sls_edges.append(
                        EKGGraphSlsSchema(
                            start_id=pid,
                            type=f'edge_route_intent_{node_type}', # 需要注意与老逻辑的兼容
                            end_id=node_id,
                            operation_type='ADD',
                            teamids=teamid
                        )
                    )
        # edges
        for node_pair in node_edge_dict['edges']:
            start_node = node_edge_dict['nodes'][node_pair['start']]
            end_node = node_edge_dict['nodes'][node_pair['end']]
            # 
            start_id = start_node['node_id_new']
            end_id = end_node['node_id_new']
            src_type, dst_type = start_node['type'].lower(), end_node['type'].lower()
            # 需要注意与老逻辑的兼容
            edge_type = f'edge_route_{src_type}_{dst_type}'
            sls_edges.append(
                EKGGraphSlsSchema(
                    start_id=start_id,
                    type=edge_type,
                    end_id=end_id,
                    operation_type='ADD',
                    teamids=teamid
                )
            )
        return EKGSlsData(nodes=sls_nodes, edges=sls_edges)
    
    def transform2tbase(self, ekg_sls_data: EKGSlsData, teamid: str) -> EKGTbaseData:
        tbase_nodes, tbase_edges = [], []

        for node in ekg_sls_data.nodes:
            name = node.name
            description = node.description
            name_vector = self._get_embedding(name)
            desc_vector = self._get_embedding(description)
            tbase_nodes.append(
                EKGNodeTbaseSchema(
                    node_id=node.id,
                    node_type=node.type,
                    node_str=f'graph_id={teamid}',
                    name_keyword=" | ".join(extract_tags(name, topK=None)),
                    desc_keyword=" | ".join(extract_tags(description, topK=None)),
                    name_vector=np.array(name_vector[name]).astype(dtype=np.float32).tobytes(),
                    desc_vector= np.array(desc_vector[description]).astype(dtype=np.float32).tobytes(),
                )
            )
        for edge in ekg_sls_data.edges:
            tbase_edges.append(
                EKGEdgeTbaseSchema(
                    edge_id=edge.id,
                    edge_type=edge.type,
                    edge_source=edge.start_id,
                    edge_target=edge.end_id,
                    edge_str=f'graph_id={teamid}',
                )
            )
        return EKGTbaseData(nodes=tbase_nodes, edges=tbase_edges)

    def transform2dsl(self, ekg_sls_data: EKGSlsData, pnode_ids: List[str], all_intents: List[str], teamid: str) -> YuqueDslDatas:
        '''define your personal dsl format and code'''
        def get_md5(s):
            import hashlib
            md = hashlib.md5()
            md5_content = s
            md.update(md5_content.encode('utf-8'))
            res = md.hexdigest()
            return res
        
        type_dict = {
            'schedule': 'start-end',
            'task': 'process',
            'analysis': 'data',
            'phenomenon': 'decision'
        }

        nodes, edges = [], []
        schedule_id = ''
        for node in ekg_sls_data.nodes:
            # 需要注意下 dsl的id md编码
            nodes.append(
                YuqueDslNodeData(id=node.id, type=type_dict.get(node.type.split("node_")[-1]), label=node.description)
            )
            # 记录 schedule id 用于添加意图节点的边
            if node.type.split("node_")[-1] == 'schedule':
                schedule_id = node.id

        # 添加意图节点
        # 需要记录哪些是被添加过的
        added_intent = set()
        intent_names_dict = {}
        for pid in pnode_ids:
            dsl_pid = get_md5(pid)
            dsl_pid = f'ekg_node:{teamid}:intent:{dsl_pid}'
            dsl_pid = f'ekg_node:intent:{dsl_pid}'
            if dsl_pid not in intent_names_dict:
                intent_names_dict[dsl_pid] = self.gb.get_current_node(
                    {'id': pid}, 'opsgptkg_intent').attributes["name"]

            nodes.append(
                YuqueDslNodeData(
                    id=node.id, type='display',
                    label=intent_names_dict.get(dsl_pid, pid),)
            )
            added_intent.add(dsl_pid)


        for intent_list in all_intents:
            for intent in intent_list:
                # 存在业务逻辑需要注意
                if 'SRE_Agent' in intent: continue

                intent_id = get_md5(intent)
                intent_id = f'ekg_node:{teamid}:intent:{intent_id}'
                intent_id = f'ekg_node:intent:{intent_id}'
                if intent_id not in intent_names_dict:
                    intent_names_dict[intent_id] = self.gb.get_current_node(
                            {'id': intent}, 'opsgptkg_intent').attributes["name"]

                if intent_id not in added_intent:
                    nodes.append(
                        YuqueDslNodeData(
                            id=intent_id, type='display',
                            label=intent_names_dict.get(intent_id, intent),)
                    )
                    added_intent.add(intent_id)
        
        for edge in ekg_sls_data.edges:
            edges.append(
                YuqueDslEdgeData(
                    id=f'{edge.start_id}___{edge.end_id}',
                    source=edge.start_id,
                    target=edge.end_id,
                    label=''
                )
            )
        
        # 添加意图边
        added_edges = set()
        for pid in pnode_ids:
            # 处理意图节点展示样式
            dsl_pid = get_md5(pid)
            dsl_pid = f'ekg_node:{teamid}:intent:{dsl_pid}'

            # 处理意图节点展示样式
            edge_id = f'{dsl_pid}___{schedule_id}'
            if edge_id not in added_edges:
                edges.append(
                    YuqueDslEdgeData(
                        id=edge_id,
                        source=dsl_pid,
                        target=schedule_id,
                        label=''
                    )
                )
                added_edges.add(edge_id)
        
        for intent_list in all_intents:
            for idx in range(len(intent_list[0:-1])):
                if 'SRE_Agent' in intent_list[idx]:
                    continue
            
                if 'SRE_Agent' in intent_list[idx+1]:
                    continue

                start_id = get_md5(intent_list[idx])
                start_id = f'ekg_node:{teamid}:intent:{start_id}'

                end_id = get_md5(intent_list[idx+1])
                end_id = f'ekg_node:{teamid}:intent:{end_id}'
                edge_id = f'{start_id}___{end_id}'

                if edge_id not in added_edges:
                    edges.append(
                        YuqueDslEdgeData(
                            id=edge_id,
                            source=start_id,
                            target=end_id,
                            label=''
                        )
                    )
                    added_edges.add(edge_id)

        return YuqueDslDatas(nodes=nodes, edges=edges)
    
    def _get_embedding(self, text):
        text_vector = {}
        if self.embed_config and text:
            text_vector = get_embedding(
                self.embed_config.embed_engine, [text],
                self.embed_config.embed_model_path, self.embed_config.model_device,
                self.embed_config
            )
        else:
            text_vector = {text: [random.random() for _ in range(768)]}
        return text_vector

    @staticmethod
    def preprocess_json_contingency(content_dict, remove_time_flag=True):
        # 专门处理告警数据合并成文本
        # 将对应的 content json 预处理为需要的样子，由于可能含有多个 path，用 dict 存储结果
        diagnose_path_list = content_dict.get('diagnose_path', [])
        res = {}
        if diagnose_path_list:
            for idx, diagnose_path in enumerate(diagnose_path_list):
                path_id = idx
                path_name = diagnose_path['name']
                content = f'路径:{path_name}\n'
                cur_count = 1

                for idx, step in enumerate(diagnose_path['diagnose_step']):
                    step_name = step['name']

                    if type(step['content']) == str:
                        step_text = step['content']
                    else:
                        step_text = step['content']['textInfo']['text']
                    
                    step_text = step_text.strip('[')
                    step_text = step_text.strip(']')

                    # step_text = step['step_summary']

                    step_text_no_time = EKGConstructService.remove_time(step_text)
                    to_append = f'''{cur_count}. {step_text_no_time}\n'''
                    cur_count += 1

                    content += to_append
                    
                res[path_id] = {
                    'path_id': path_id,
                    'path_name': path_name,
                    'content': content
                }
        return res
    
    @staticmethod
    def remove_time(text):
        re_pat = '''\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}(:\d{2})*'''
        text_res = re.split(re_pat, text)
        res = ''
        for i in text_res:
            if i:
                i_strip = i.strip('，。\n')
                i_strip = f'{i_strip}'
                res += i_strip
        return res

    def _update_tbase_attr_for_nodes(self, attrs):
        tbase_attrs = {}
        for k in ["name", "description"]:
            if k in attrs:
                text = attrs.get(k, "")
                text_vector = self._get_embedding(text)
                tbase_attrs[f"{k}_vector"] = np.array(text_vector[text]).astype(dtype=np.float32).tobytes()
                tbase_attrs[f"{k}_keyword"] = " | ".join(extract_tags(text, topK=None))
        return tbase_attrs
    
    def _update_new_attr_for_nodes(self, nodes: List[GNode], teamid: str, teamids_by_nodeid={}, do_check=False):
        '''update new attributes for nodes'''
        nodetype2fields_dict = {}
        for node in nodes:
            node_type = node.type

            if node.id in teamids_by_nodeid:
                node.attributes["teamids"] = teamids_by_nodeid.get(node.id, "").split("=")[1] + f", {teamid}"
            else:
                node.attributes["teamids"] = f"{teamid}"

            node.attributes["gdb_timestamp"] = getCurrentTimestap()
            # node.attributes["version"] = getCurrentDatetime()

            # check the data's key-value by node_type
            schema = TYPE2SCHEMA.get(node_type,)
            if node_type in nodetype2fields_dict:
                fields = nodetype2fields_dict[node_type]
            else:
                fields = list(getClassFields(schema))
                nodetype2fields_dict[node_type] = fields

            flag = any([
                field not in node.attributes 
                for field in fields 
                if field not in ["start_id", "end_id", "ID", "id", "extra"]
            ])
            if flag and do_check:
                raise Exception(f"node is wrong, type is {node_type}, fields is {fields}, data is {node.attributes}")
        
            # update extra infomations to extra
            extra_fields = [k for k in node.attributes.keys() if k not in fields]
            node.attributes.setdefault(
                "extra", 
                json.dumps({
                    k: node.attributes.pop(k, "")
                    for k in extra_fields
                }, ensure_ascii=False)
            )
        return nodes
    
    def _update_new_attr_for_edges(self, edges: List[GEdge], teamid: str, teamids_by_edgeid={}, do_check=True, do_update=False):
        '''update new attributes for nodes'''
        edgetype2fields_dict = {}
        for edge in edges:
            edge_type = edge.type
            edge_id = f"{edge.start_id}__{edge.end_id}"
            if edge_id in teamids_by_edgeid:
                edge.attributes["teamids"] = teamids_by_edgeid.get(edge_id, "").split("=")[1] + f", {teamid}"
            else:
                edge.attributes["teamids"] = f"{teamid}"

            edge.attributes["@timestamp"] = edge.attributes.pop("timestamp", 0) or 1 # getCurrentTimestap()
            edge.attributes["gdb_timestamp"] = getCurrentTimestap()
            edge.attributes['original_dst_id2__'] = edge.end_id
            edge.attributes['original_src_id1__'] = edge.start_id
            # edge.attributes["version"] = getCurrentDatetime()
            # edge.attributes["extra"] = '{}'

            # check the data's key-value by edge_type
            schema = TYPE2SCHEMA.get("edge",)
            if edge_type in edgetype2fields_dict:
                fields = edgetype2fields_dict[edge_type]
            else:
                fields = list(getClassFields(schema))
                edgetype2fields_dict[edge_type] = fields

            flag = any([
                field not in edge.attributes for field in fields 
                if field not in ["dst_id", "src_id", "DSTID", "SRCID", "timestamp", "ID", "id", "extra"]])
            if flag and do_check:
                raise Exception(f"edge is wrong, type is {edge_type}, fields is {fields}, data is {edge.attributes}")

            # update extra infomations to extra
            extra_fields = [k for k in edge.attributes.keys() if k not in fields+["@timestamp"]]
            edge.attributes.setdefault(
                "extra", 
                json.dumps({
                    k: edge.attributes.pop(k, "")
                    for k in extra_fields
                }, ensure_ascii=False)
            )
            if do_update:
                edge.attributes.pop("@timestamp")
            edge.attributes.pop("extra")
        return edges

