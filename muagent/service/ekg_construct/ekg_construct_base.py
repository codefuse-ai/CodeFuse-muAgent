from loguru import logger
import re
import json
from typing import List, Dict, Optional, Tuple, Literal

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

import time

from muagent.schemas.ekg import *
from muagent.schemas.db import *
from muagent.schemas.common import *
from muagent.db_handler import *
from muagent.orm import table_init

from muagent.connector.configs.generate_prompt import *

from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.llm_models import *


from muagent.base_configs.env_config import KB_ROOT_PATH

from muagent.service.ekg_inference.intention_router import IntentionRouter
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
            intention_router: Optional[IntentionRouter] = None,
            do_init: bool = False,
            kb_root_path: str = KB_ROOT_PATH,
            initialize_space=True
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
        self.node_indexname = "opsgptkg_node"
        self.edge_indexname = "opsgptkg_edge"

        # get llm model
        self.model = getChatModelFromConfig(self.llm_config) if llm_config else None
        self.intention_router = intention_router or IntentionRouter(
            self.model, embed_config=self.embed_config)
        # init db handler
        self.initialize_space = initialize_space
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
            VectorField("description_vector",
                        'FLAT',
                        {
                            "TYPE": "FLOAT32",
                            "DIM": DIM,
                            "DISTANCE_METRIC": "COSINE"
                        }),
            TextField("ekg_type",),
            TextField("graph_id",),
            TagField(name='name_keyword', separator='|'),
            TagField(name='description_keyword', separator='|')
        ]

        EDGE_SCHEMA = [
            TextField("edge_id", ),
            TextField("edge_type", ),
            TextField("edge_source", ),
            TextField("edge_target", ),
            TextField("edge_str", ),
            TextField("ekg_type",),
        ]


        if self.tb_config:
            tb_dict = {"TbaseHandler": TbaseHandler}
            tb_class =  tb_dict.get(self.tb_config.tb_type, TbaseHandler)
            self.tb: TbaseHandler = tb_class(
                tb_config=self.tb_config, 
                index_name=self.tb_config.index_name, 
                definition_value=self.tb_config.extra_kwargs.get(
                    "definition_value", "muagent_ekg")
            )
            # # create index
            if not self.tb.is_index_exists(self.node_indexname):
                res = self.tb.create_index(
                    index_name=self.node_indexname, schema=NODE_SCHEMA)
                logger.info(f"tb init: {res}")

            if not self.tb.is_index_exists(self.edge_indexname):
                res = self.tb.create_index(
                    index_name=self.edge_indexname, schema=EDGE_SCHEMA)
                logger.info(f"tb init: {res}")
        else:
            self.tb = None

    def init_gb(self, do_init: bool=None):
        if self.gb_config:
            gb_dict = {
                "NebulaHandler": NebulaHandler, 
                "NetworkxHandler": NetworkxHandler, 
                "GeaBaseHandler": GeaBaseHandler,
            }
            gb_class =  gb_dict.get(self.gb_config.gb_type, NebulaHandler)
            self.gb: GBHandler = gb_class(self.gb_config)

            initialize_space = self.initialize_space  # True or False
            if initialize_space and self.gb_config.gb_type=="NebulaHandler":
                self.gb.add_hosts('storaged0', 9779)
                print('增加NebulaGraph Storage主机中，等待20秒')
                time.sleep(20)
                # 初始化space
                self.gb.drop_space('client')
                self.gb.create_space('client')
                
                # 创建node tags和edge types
                self.create_gb_tags_and_edgetypes()

                print('Node Tags和Edge Types初始化中，等待20秒......')
                time.sleep(20)
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
            self.vb: LocalFaissHandler = vb_class(
                self.embed_config, vb_config=self.vb_config)
        else:
            self.vb = None

    def init_sls(self, do_init: bool=None):
        if self.sls_config:
            sls_dict = {"AliYunSLSHandler": AliYunSLSHandler}
            sls_class =  sls_dict.get(self.sls_config.sls_type, AliYunSLSHandler)
            self.sls: AliYunSLSHandler = sls_class(
                self.embed_config, vb_config=self.vb_config)
        else:
            self.sls = None
    
    def _get_local_graph(
            self, nodes: List[GNode], edges: List[GEdge], rootid
        ) -> Tuple[List[str], Graph]:
        # search and delete unconnect nodes and edges
        connections = {}
        for edge in edges:
            connections.setdefault(edge.start_id, []).append(edge.end_id)
        
        for node in nodes:
            connections.setdefault(node.id, [])

        if rootid not in connections and len(nodes)>0:
            raise Exception(f"Error: rootid not in this graph")

        # dfs for those nodes from rootid
        visited = set()
        rootid_can_arrive_nodeids = []
        paths = []
        def _dfs(node, current_path: List):
            if node not in visited:
                visited.add(node)
                current_path.append(node)
                rootid_can_arrive_nodeids.append(node)
                # stop condition, there is no more neightbos
                if not connections.get(node, []):
                    # when arrive the endpoiond, save the copy of current path
                    paths.append(list(current_path))
                else:
                    for neighbor in connections.get(node, []):
                        _dfs(neighbor, current_path)

                # recursive：remove the last node
                current_path.pop()

        # init DFS
        _dfs(rootid, [])
        logger.info(f"graph paths, {paths}")
        logger.info(f"rootid can not arrive nodeids, "
                    f"{[n for n in nodes if n.id not in rootid_can_arrive_nodeids]}")

        graph = Graph(
            nodes=[n for n in nodes if n.id in rootid_can_arrive_nodeids], 
            edges=[
                e for e in edges
                if e.start_id in rootid_can_arrive_nodeids and 
                   e.end_id in rootid_can_arrive_nodeids
            ],
            paths=paths
        )
        return rootid_can_arrive_nodeids, graph


    def create_gb_tags_and_edgetypes(self):
        # 节点标签和属性 (done)
        for node_type, schema in TYPE2SCHEMA.items():
            if node_type == 'edge':
                continue
            node_attributes = schema.schema().get('properties', {})
            # 将属性转换为适用于 Nebula Graph 的字典格式
            attributes_dict = {}
            for k, v in node_attributes.items():
                # 判断属性类型并修改
                if v.get('type') == 'integer':
                    attributes_dict[k] = 'int'
                elif v.get('type') == 'boolean':
                    attributes_dict[k] = 'bool'
                else:
                    attributes_dict[k] = v.get('type')
            self.gb.create_tag(node_type, attributes_dict)

        # 边属性
        for edge_type, schema in TYPE2SCHEMA.items():
            if schema == EKGEdgeSchema:  # 假设边由 EdgeSchema 识别
                edge_attributes = schema.schema().get('properties', {})
                # logger.info(edge_attributes)
                # 将属性转换为适用于 Nebula Graph 的字典格式
                edge_attributes_dict = {}
                for k, v in edge_attributes.items():
                    # 判断属性类型并修改
                    if v.get('type') == 'integer':
                        edge_attributes_dict[k] = 'int'
                    else:
                        edge_attributes_dict[k] = v.get('type')

        # 边类型(名称)
        node_types = list(TYPE2SCHEMA.keys())
        logger.info(node_types)
        for i in range(len(node_types)):
            for j in range(len(node_types)):
                if node_types[i] != 'edge' and node_types[j] != 'edge':  # 排除 node_type 为 'edge'
                    edge_type = f"{node_types[i]}_route_{node_types[j]}"
                    self.gb.create_edge_type(edge_type, edge_attributes_dict)
                    edge_type2 = f"{node_types[i]}_extend_{node_types[j]}" # 有可能用extend来连接，后续修改可再添加
                    self.gb.create_edge_type(edge_type2, edge_attributes_dict)
                    edge_type3 = f"{node_types[i]}_conclude_{node_types[j]}"
                    self.gb.create_edge_type(edge_type3, edge_attributes_dict)


        

    def update_graph(
            self, 
            origin_nodes: List[GNode], origin_edges: List[GEdge], 
            new_nodes: List[GNode], new_edges: List[GEdge], 
            teamid: str, rootid: str
        ):
        rootid_can_arrive_nodeids, _ = self._get_local_graph(
            new_nodes, new_edges, rootid=rootid)
        _, _ = self._get_local_graph(origin_nodes, origin_edges, rootid=rootid)
        # logger.info(new_nodes)
        # rootid_can_arrive_node = [n for n in new_nodes if n.id in rootid_can_arrive_nodeids]
        # rootid_can_arrive_edge = [e for e in new_edges if (e.start_id in rootid_can_arrive_nodeids) and (e.end_id in rootid_can_arrive_nodeids)]

        origin_nodeids = set([node.id for node in origin_nodes])
        origin_edgeids = set([f"{edge.start_id}__{edge.end_id}" for edge in origin_edges])
        nodeids = set([node.id for node in new_nodes])
        edgeids = set([f"{edge.start_id}__{edge.end_id}" for edge in new_edges])

        logger.info(edgeids)

        unique_nodeids = origin_nodeids&nodeids
        unique_edgeids = origin_edgeids&edgeids
        nodeid2nodes_dict = {}
        for node in origin_nodes + new_nodes:
            nodeid2nodes_dict.setdefault(node.id, []).append(node)

        edgeid2edges_dict = {}
        for edge in origin_edges + new_edges:
            edgeid2edges_dict.setdefault(f"{edge.start_id}__{edge.end_id}", []).append(edge)

        # get add nodes & edges and filter those nodes/edges cant be arrived from rootid
        add_nodes = [node for node in new_nodes if node.id not in origin_nodeids]
        add_nodes = [n for n in add_nodes if n.id in rootid_can_arrive_nodeids]
        # logger.info(add_nodes)
        add_edges = [
            edge for edge in new_edges 
            if f"{edge.start_id}__{edge.end_id}" not in origin_edgeids
        ]
        add_edges = [
            edge for edge in add_edges 
            if (edge.start_id in rootid_can_arrive_nodeids) and 
            (edge.end_id in rootid_can_arrive_nodeids)
        ]
        # logger.info(add_edges)

        # get delete nodes & edges
        delete_nodes = [node for node in origin_nodes if node.id not in nodeids]
        delete_edges = [
            edge for edge in origin_edges 
            if f"{edge.start_id}__{edge.end_id}" not in edgeids
        ]
        
        logger.info(delete_edges)

        delete_nodeids = [node.id for node in delete_nodes]
        

        node_neighbor_lens = [
            len([
                n.id # reverse neighbor nodes which are not in delete nodes
                for n in self.gb.get_neighbor_nodes({"id": node.id}, node.type, reverse=True)
                if n.id not in delete_nodeids])
            for node in delete_nodes
        ]
        
        delete_nodes = [n for n, n_len in zip(delete_nodes, node_neighbor_lens) if n_len==0]
        

        undelete_nodeids = [
            n.id for n, n_len in zip(delete_nodes, node_neighbor_lens) if n_len>0]
        delete_edges = [e for e in delete_edges if e.start_id not in undelete_nodeids]
        logger.info(delete_edges)

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
        # logger.info(add_nodes)
        # execute action
        add_node_result = self.add_nodes(add_nodes, teamid)
        add_edge_result = self.add_edges(add_edges, teamid)

        logger.info("需要删除的节点")
        logger.info(delete_nodes) # []
        logger.info("需要删除的边")
        logger.info(delete_edges) # 有边
        delete_edge_result = self.delete_edges(delete_edges, teamid)
        delete_node_result = self.delete_nodes(delete_nodes, teamid)

        update_node_result = self.update_nodes(update_nodes, teamid)
        update_edge_result = self.update_edges(update_edges, teamid)

        # 返回明确更新的graph
        add_fail_edge_ids = []
        add_edge_dict = {}
        for add_edge, gb_res in zip(add_edges, add_edge_result["gb_result"]):
            add_edge_dict["__".join([add_edge.start_id, add_edge.end_id])] = add_edge
            if gb_res.errorCode not in [0, 1]:
                add_fail_edge_ids.append("__".join([add_edge.start_id, add_edge.end_id]))

        delete_fail_edge_ids = []
        for delete_edge, gb_res in zip(delete_edges, delete_edge_result["gb_result"]):
            if gb_res.errorCode != 0:
                delete_fail_edge_ids.append("__".join([delete_edge.start_id, delete_edge.end_id]))

        add_fail_node_ids = []
        add_node_dict = {}
        for add_node, gb_res in zip(add_nodes, add_node_result["gb_result"]):
            add_node_dict[add_node.id] = add_node
            if gb_res.errorCode not in [0, 1]:
                add_fail_node_ids.append(add_node.id)

        delete_fail_node_ids = []
        for delete_node, gb_res in zip(delete_nodes, delete_node_result["gb_result"]):
            if gb_res.errorCode != 0:
                delete_fail_node_ids.append(delete_node.id)

        new_nodes_copy = []
        for n in new_nodes:
            if n.id not in add_fail_node_ids:
                new_nodes_copy.append(add_node_dict.get(n.id,  n))
        
        for n in delete_nodes:
            if n.id in delete_fail_node_ids:
                new_nodes_copy.append(n)

        new_edges_copy = []
        for e in new_edges:
            if "__".join([e.start_id, e.end_id]) not in add_fail_edge_ids:
                new_edges_copy.append(
                    add_edge_dict.get("__".join([e.start_id, e.end_id]), e))
        for e in delete_edges:
            if "__".join([e.start_id, e.end_id]) in delete_fail_edge_ids:
                new_edges_copy.append(e)

        _, old_graph = self._get_local_graph(
            self._normalized_nodes_type(new_nodes_copy), 
            self._normalized_edges_type(new_edges_copy), rootid=rootid
        )
        return old_graph, {
            "add_node_result": add_node_result, 
            "add_edge_result": add_edge_result, 
            "delete_edge_result": delete_edge_result, 
            "delete_node_result": delete_node_result, 
            "update_node_result": update_node_result, 
            "update_edge_result": update_edge_result
        }


    def add_nodes(self, nodes: List[GNode], teamid: str, ekg_type: str="ekgnode") -> Dict:
        '''
        add new nodes into tbase and graph base
        :param nodes: new nodes
        :param teamid: teamid
        '''
        nodes = self._update_new_attr_for_nodes(nodes, teamid, do_check=True)

        tbase_nodes = []
        for node in nodes:
            # get the node's teamids
            r = self.tb.search(
                f"@node_id: *{node.id}*", index_name=self.node_indexname
            )
            
            teamids = [
                i.strip()
                for i in r.docs[0]["node_str"].replace("graph_id=", "").split(",")
                if i.strip()
            ] if r.docs else []
            teamids = list(set(teamids+[teamid]))

            tbase_nodes.append({
                **{
                    "ID": node.attributes.get("ID", 0) or double_hashing(node.id),
                    "node_id": node.id,
                    "node_type": node.type, 
                    "node_str": ', '.join(teamids),
                    "graph_id": ', '.join(teamids),
                    "ekg_type": ekg_type,
                }, 
                **self._update_tbase_attr_for_nodes(node.attributes)
            })

        tb_result, gb_result = [], []
        try: 
            gb_result = [self.gb.add_node(node) for node in nodes]
            tb_result.append(
                self.tb.insert_data_hash(tbase_nodes, key='node_id', need_etime=False)
            )
        except Exception as e:
            logger.error(e)

        # todo return nodes' infomation
        return {"gb_result": gb_result, "tb_result": tb_result}

    def add_edges(self, edges: List[GEdge], teamid: str, ekg_type: str="ekgedge"):
        edges = self._update_new_attr_for_edges(edges)
        
        tbase_edges = [{
            'edge_id': f"{edge.start_id}__{edge.end_id}",
            'edge_type': edge.type,
            'edge_source': edge.start_id,
            'edge_target': edge.end_id,
            'edge_str': f'graph_id={teamid}',
            "ekg_type": ekg_type,
            }
            for edge in edges
        ]

        tb_result, gb_result = [], []
        try:
            # bug: there is gap between zhizhu and geabase
            gb_result = [self.gb.add_edge(edge) for edge in edges]
            tb_result.append(
                self.tb.insert_data_hash(tbase_edges, key="edge_id", need_etime=False)
                )
        except Exception as e:
            logger.error(e)

        # todo return nodes' infomation
        return {"gb_result": gb_result, "tb_result": tb_result}

    def delete_nodes(self, nodes: List[GNode], teamid: str=''):
        # delete tbase nodes
        r = self.tb.search(
            f"@node_str: *{teamid}*", index_name=self.node_indexname, limit=len(nodes)
            )

        tbase_nodeids = [data['node_id'] for data in r.docs] # 附带了definition信息
        delete_nodeids = [node.id for node in nodes]
        tbase_missing_nodeids = [
            nodeid for nodeid in delete_nodeids 
            if nodeid not in tbase_nodeids
            ]

        if len(tbase_missing_nodeids) > 0:
            logger.error(
                f"there must something wrong! ID not match, such as {tbase_missing_nodeids}"
                )

        # node_neighbor_lens = [
        #     len([
        #         n.id # reverse neighbor nodes which are not in delete nodes
        #         for n in self.gb.get_neighbor_nodes({"id": node.id}, node.type, reverse=True)
        #         if n.id not in delete_nodeids])
        #     for node in nodes
        # ]
        
        # extra_delete_nodes, extra_delete_edges = [], []
        # extra_delete_nodeids = set()
        # for node in nodes:
        #     if node.id in extra_delete_nodeids: continue

        #     extra_delete_nodeids.add(node.id)
        #     # 
        #     graph = self.gb.get_hop_infos(attributes={"id": node.id,}, node_type=node.type, hop=30)
        #     extra_delete_nodes.extend(graph.nodes)
        #     extra_delete_edges.extend(graph.edges)
        #     for _node in graph.nodes:
        #         extra_delete_nodeids.add(_node.id)

        
        # # directly delete extra_delete_nodes in tbase
        # tb_result = []
        # for edge in extra_delete_edges:
        #     resp = self.tb.delete(f"{edge.start_id}__{edge.end_id}")
        #     tb_result.append(resp)

        # delete the nodeids in tbase
        # tb_result = []
        # for node, node_len in zip(nodes, node_neighbor_lens):
        #     if node_len >= 1: continue
        #     resp = self.tb.delete(node.id)
        #     tb_result.append(resp)

        # delete the nodeids in tbase
        tb_result = []
        for node in nodes:
            resp = self.tb.delete(node.id)
            tb_result.append(resp)

        # delete the nodeids in geabase
        gb_result = []
        # for node, node_len in zip(nodes, node_neighbor_lens):
        #     if node_len >= 1: continue
        for node in nodes:
            gb_result.append(self.gb.delete_node(
                {"id": node.id}, node.type, 
                ID=node.attributes.get("ID") or double_hashing(node.id)
            ))
        return {"gb_result": gb_result, "tb_result": tb_result}
    
    def delete_edges(self, edges: List[GEdge], teamid: str):
        # delete tbase nodes
        r = self.tb.search(
            f"@edge_str: *{teamid}*", 
            index_name=self.edge_indexname, 
            limit=len(edges)
        )

        tbase_edgeids = [data['edge_id'] for data in r.docs]
        delete_edgeids = [f"{edge.start_id}__{edge.end_id}" for edge in edges]
        tbase_missing_edgeids = [
            edgeid for edgeid in delete_edgeids if edgeid not in tbase_edgeids]

        if len(tbase_missing_edgeids) > 0:
            logger.error(
                f"there must something wrong! ID not match, such as {tbase_missing_edgeids}")
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
        return {"gb_result": gb_result, "tb_result": tb_result}
    
    def update_nodes(self, nodes: List[GNode], teamid: str):
        '''
        update nodes with new attributes and teamid
        :param nodes:
        :param teamid:
        '''
        r = self.tb.search(
            f"@node_str: *{teamid}*", 
            index_name=self.node_indexname, 
            limit=len(nodes)
        )
        teamids_by_nodeid = {data['node_id']: data["node_str"]  for data in r.docs}

        tbase_nodeids = [data['node_id'] for data in r.docs]
        update_nodeids = [node.id for node in nodes]
        tbase_missing_nodeids = [
            nodeid for nodeid in update_nodeids if nodeid not in tbase_nodeids]

        if len(tbase_missing_nodeids) > 0:
            logger.error(f"there must something wrong! "
                         f"ID not match, such as {tbase_missing_nodeids}")
            for nodeid in tbase_missing_nodeids:
                r = self.tb.search(
                    f"@node_id: {nodeid.replace('-', '_')}", 
                    index_name=self.node_indexname)
                teamids_by_nodeid.update(
                    {data['node_id']: data["node_str"]  for data in r.docs})

        tbase_datas = []
        for node in nodes:
            tbase_data = {}
            tbase_data["node_id"] = node.id
            
            if node.id not in teamids_by_nodeid:
                raise ValueError(f"this id {node.id} not in graph, please check your input")
            
            if teamid not in teamids_by_nodeid[node.id]:
                teamids = [
                    i.strip() 
                    for i in teamids_by_nodeid[node.id].replace("graph_id=", "").split(",") 
                    if i.strip()
                ]
                teamids = list(set(teamids+[teamid]))
                tbase_data["node_str"] = ', '.join(teamids)
                # tbase_data["teamids"] = f"graph_id={', '.join(teamids)}",
            tbase_data.update(self._update_tbase_attr_for_nodes(node.attributes))
            tbase_datas.append(tbase_data)

        tb_result = []
        for tbase_data in tbase_datas:
            resp = self.tb.insert_data_hash(tbase_data, key="node_id", need_etime=False)
            tb_result.append(resp)

        # update the nodeids in geabase
        nodes = self._update_new_attr_for_nodes(
            nodes, teamid, teamids_by_nodeid, do_check=False)
        gb_result = []
        for node in nodes:
            ID = node.attributes.pop("ID", None) or double_hashing(node.id)
            resp = self.gb.update_node(
                # {}, node.attributes, node_type=node.type, 
                {"id":node.id}, node.attributes, node_type=node.type, 
                ID=ID
            )
            gb_result.append(resp)
        return {"gb_result": gb_result, "tb_result": tb_result}

    def update_edges(self, edges: List[GEdge], teamid: str):
        r = self.tb.search(
            f"@edge_str: *{teamid}*", 
            index_name=self.node_indexname, 
            limit=len(edges)
        )
        tbase_edgeids = [data['edge_id'] for data in r.docs]
        delete_edgeids = [f"{edge.start_id}__{edge.end_id}" for edge in edges]
        tbase_missing_edgeids = [
            edgeid for edgeid in delete_edgeids if edgeid not in tbase_edgeids]

        if len(tbase_missing_edgeids) > 0:
            logger.error(f"there must something wrong! "
                         f"ID not match, such as {tbase_missing_edgeids}")

        # update the nodeids in geabase
        edges = self._update_new_attr_for_edges(edges, do_check=False, do_update=True)
        logger.info(edges)
        gb_result = []
        for edge in edges:
            # todo bug, there is gap between zhizhu and graph base
            SRCID = edge.attributes.pop("SRCID", None) or double_hashing(edge.start_id)
            DSTID = edge.attributes.pop("DSTID", None) or double_hashing(edge.end_id)
            resp = self.gb.update_edge(
                SRCID, DSTID,
                edge.attributes, edge_type=edge.type
            )
            gb_result.append(resp)
        return {"gb_result": gb_result, "tb_result": []}

    def delete_nodes_v2(self, nodes: List[GNode], teamid: str=''):
        '''
        delete tbase nodes
        :param nodes:
        :param teamid:
        '''
        r = self.tb.search(
            f"@node_str: *{teamid}*", 
            index_name=self.node_indexname, 
            limit=len(nodes)
        )

        tbase_nodeids = [data['node_id'] for data in r.docs]
        delete_nodeids = [node.id for node in nodes]
        tbase_missing_nodeids = [
            nodeid for nodeid in delete_nodeids if nodeid not in tbase_nodeids
            ]

        if len(tbase_missing_nodeids) > 0:
            logger.error(f"there must something wrong! "
                         f"ID not match, such as {tbase_missing_nodeids}")

        node_upstream_nodes = {
            node.id: [
                n.id # reverse neighbor nodes which are not in delete nodes
                for n in self.gb.get_neighbor_nodes(
                    {"id": node.id}, node.type, reverse=True)
                if n.id not in delete_nodeids]
            for node in nodes
        }
        node_downstream_nodes = {
            node.id: [
                n.id # reverse neighbor nodes which are not in delete nodes
                for n in self.gb.get_neighbor_nodes(
                    {"id": node.id}, node.type, reverse=False)
                if n.id not in delete_nodeids]
            for node in nodes
        }

        # delete the nodeids in tbase
        tb_result = []
        for node in nodes:
            if len(node_upstream_nodes.get(node.id, []))>0: continue
            resp = self.tb.delete(node.id)
            tb_result.append(resp)

        # delete the nodeids in geabase
        gb_result = []
        for node in nodes:
            if len(node_upstream_nodes.get(node.id, []))>0 or \
                len(node_downstream_nodes.get(node.id, []))>0: 
                continue
            gb_result.append(self.gb.delete_node(
                {"id": node.id}, node.type, 
                ID=node.attributes.get("ID") or double_hashing(node.id)
            ))
        return {"gb_result": gb_result, "tb_result": tb_result}
    
    def get_node_by_id(
            self, nodeid: str, 
            node_type:str = None, 
            service_type: Literal["gbase", "tbase"]="gbase",
        ) -> GNode:
        if service_type=="gbase":
            node = self.gb.get_current_node({'id': nodeid}, node_type=node_type)
            node = self._normalized_nodes_type(nodes=[node])[0]
        else:
            node = GNode(id=nodeid, type="", attributes={})
        # tbase search
        r = self.tb.search(f"@node_id: *{nodeid}*", index_name=self.node_indexname)
        teamids = [
                i.strip()
                for i in r.docs[0]["node_str"].replace("graph_id=", "").split(",")
                if i.strip()
            ] if r.docs else []

        node.attributes["teamids"] = teamids
        return node
    
    def get_graph_by_nodeid(
            self, 
            nodeid: str, 
            node_type: str, 
            hop: int = 10, 
            block_attributes: List[dict] = {}
        ) -> Graph:
        if hop<2:
            raise Exception(f"hop must be smaller than 2, now hop is {hop}")
        if hop >= 30:
            raise Exception(f"hop can't be larger than 30, now hop is {hop}")
        # filter the node which dont match teamid
        result = self.gb.get_hop_infos(
            {'id': nodeid}, node_type=node_type, 
            hop=hop, block_attributes=block_attributes
        )
        # logger.info(result)
        if result.nodes == []:
            current_node = self.gb.get_current_node({"id": nodeid}, node_type=node_type)
            # nebula current_node查询不到会返回None
            if current_node != None:
                result.nodes.append(current_node)
        # logger.info(result)
        if block_attributes:
            leaf_nodeids = [
                node.id for node in result.nodes if node.type=="opsgptkg_schedule"
            ]
        else:
            leaf_nodeids = [path[-1] for path in result.paths if len(path)==hop+1]

        nodes = self._normalized_nodes_type(result.nodes)
        for node in nodes:
            if node.id in leaf_nodeids:
                neighbor_nodes = self.gb.get_neighbor_nodes(
                    {"id": node.id}, node_type=node.type)
                node.attributes["cnode_nums"] = len(neighbor_nodes)
        
        edges = self._normalized_edges_type(result.edges)
        result.nodes = nodes
        result.edges = edges
        # logger.info(edges)
        return result

    def search_nodes_by_text(
            self, text: str, node_type: str = None, teamid: str = None, top_k=5
        ) -> List[GNode]:
        '''
        text: Matches the attribute name and description of the node
        '''
        if text is None: return []

        nodeids = []
        # 
        if self.embed_config:
            vector_dict = self._get_embedding(text)
            query_embedding = np.array(vector_dict[text]).astype(dtype=np.float32).tobytes()

            nodeid_with_dist = []
            for key in ["name_vector", "description_vector"]:
                
                base_query = f'(*)=>[KNN {top_k} @{key} $vector AS distance]' if teamid is None \
                        else f'(@node_str: *{teamid}*)=>[KNN {top_k} @{key} $vector AS distance]'
                # base_query = f'(*)=>[KNN {top_k} @{key} $vector AS distance]'
                query_params = {"vector": query_embedding}
                r = self.tb.vector_search(
                    base_query, index_name=self.node_indexname, query_params=query_params
                )

                for i in r.docs:
                    data_dict = i.__dict__
                    if "ID" not in data_dict: continue # filter data
                    nodeid_with_dist.append((data_dict["ID"], float(data_dict["distance"])))
            
            nodeid_with_dist = sorted(nodeid_with_dist, key=lambda x:x[1], reverse=False)
            for nodeid, dis in nodeid_with_dist:
                if nodeid not in nodeids:
                    nodeids.append(nodeid)

        # search keyword by jieba spliting text
        keywords = extract_tags(text)
        keyword = "|".join(keywords)
        for key in ["name_keyword", "description_keyword"]:
            query = f"(@node_str: *{teamid}*)(@{key}:{{{keyword}}})"
            r = self.tb.search(query, index_name=self.node_indexname, limit=30)
            for i in r.docs:
                if i["ID"] not in nodeids:
                    nodeids.append(i["ID"])

        nodes = self.gb.get_nodes_by_ids(nodeids)
        nodes = self._normalized_nodes_type(nodes)
        # tmp iead to filter by teamid 
        nodes = [node for node in nodes if str(teamid) in str(node.attributes)]
        # select the node which can connect the rootid
        nodes = [
            node for node in nodes 
            if len(self.search_rootpath_by_nodeid(
                node.id, node.type, f"ekg_team_{teamid}"
            ).paths) > 0
        ]
        return nodes

    def search_rootpath_by_nodeid(
            self, nodeid: str, node_type: str, rootid: str
        ) -> Graph:
        result = self.gb.get_hop_infos(
            {"id": nodeid}, node_type=node_type, hop=15, reverse=True
        )
        # logger.info(result.nodes)

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
        new_edges = [
            edge for edge in result.edges 
            if edge.start_id in nodeid_set and edge.end_id in nodeid_set
        ]

        new_nodes = self._normalized_nodes_type(new_nodes)
        new_edges = self._normalized_edges_type(new_edges) 
        return Graph(nodes=new_nodes, edges=new_edges, paths=new_paths)

    def create_ekg(
            self, 
            text: str, 
            teamid: str, 
            service_name: str, 
            rootid: str,
            graphid: str = "",
            intent_text: str = None, 
            intent_nodes: List[str] = [], 
            all_intent_list: List=[],
            do_save: bool = False,
        ):

        if intent_nodes:
            ancestor_list = intent_nodes
        elif intent_text or text:
            ancestor_list, all_intent_list = self.get_intents(rootid, intent_text or text)
        else:
            raise Exception(f"must have intent infomation")
        
        if service_name == "dsl2graph":
            reuslt = self.dsl2graph()
        else: 
            # text2graph
            result = self.text2graph(text, ancestor_list, all_intent_list, teamid)

        # do write
        graph = self.write2kg(result["sls_graph"], teamid, graphid, do_save=do_save)
        result["graph"] = graph
        return result
    
    def dsl2graph(self, ):
        pass

    def text2graph(
            self, text: str, intents: List[str], all_intent_list: List[str], teamid: str
        ) -> dict:
        # generate graph by llm
        result = self.get_graph_by_text(text, ) 
        # convert llm contet to database schema
        sls_graph = self.transform2sls(result, intents, teamid=teamid)
        tbase_graph = self.transform2tbase(sls_graph, teamid=teamid)
        dsl_graph = self.transform2dsl(sls_graph, intents, all_intent_list, teamid=teamid)
        return {"tbase_graph": tbase_graph, "sls_graph": sls_graph, "dsl_graph": dsl_graph}
    
    def write2kg(
            self, 
            ekg_sls_data: EKGSlsData, 
            teamid: str, 
            graphid: str="", 
            do_save: bool=False
        ) -> Graph:
        '''
        :param graphid: str, use for record the new path
        '''
        # everytimes, it will add new nodes and edges

        gbase_nodes: List[EKGNodeSchema] = [
            TYPE2SCHEMA.get(node.type,)(**node.dict()) for node in ekg_sls_data.nodes
        ]
        gbase_nodes: List[GNode] = [
            GNode(
                id=node.id, type=node.type, 
                attributes=node.attributes() if graphid else {**node.attributes(), **{"graphid": f"{graphid}"}}
            ) for node in gbase_nodes]

        gbase_edges: List[EKGEdgeSchema] = [
            TYPE2SCHEMA.get("edge",)(**edge.dict()) for edge in ekg_sls_data.edges
        ]
        gbase_edges = [
            GEdge(start_id=edge.original_src_id1__, end_id=edge.original_dst_id2__, 
                type="opsgptkg_"+edge.type.split("_")[2] + "_route_" + "opsgptkg_"+edge.type.split("_")[3], 
                attributes=edge.attributes()) 
            for edge in gbase_edges
        ]

        if do_save:
            node_result = self.add_nodes(gbase_nodes, teamid)
            edge_result = self.add_edges(gbase_edges, teamid)
            logger.info(f"{node_result}\n{edge_result}")

        return Graph(nodes=gbase_nodes, edges=gbase_edges, paths=[])

    def returndsl(self, graph_datas_by_path: dict, intents: List[str], ) -> dict:
        # 返回值需要返回 dsl 结构的数据用于展示，这里稍微做下数据处理，但主要就需要 dsl 对应的值
        res = {'dsl': '', 'details': {}, 'intent_node_list': intents}

        merge_dsl_nodes, merge_dsl_edges = [], []
        merge_gbase_nodes, merge_gbase_edges = [], []
        id_sets = set()
        gid_sets = set()
        for path_id, graph_datas in graph_datas_by_path.items():
            res['details'][path_id] = {
                'dsl': graph_datas["dsl_graph"],
                'sls': graph_datas["sls_graph"],
            }
            merge_dsl_nodes.extend([
                node for node in graph_datas["dsl_graph"].nodes if node.id not in id_sets
            ])
            id_sets.update([i.id for i in graph_datas["dsl_graph"].nodes])
            merge_dsl_edges.extend([
                edge for edge in graph_datas["dsl_graph"].edges if edge.id not in id_sets
            ])
            id_sets.update([i.id for i in graph_datas["dsl_graph"].edges])
            
            merge_gbase_nodes.extend([
                node for node in graph_datas["graph"].nodes if node.id not in gid_sets
            ])
            gid_sets.update([i.id for i in graph_datas["graph"].nodes])
            merge_gbase_edges.extend([
                edge for edge in graph_datas["graph"].edges 
                if f"{edge.start_id}__{edge.end_id}" not in gid_sets
            ])
            gid_sets.update([f"{i.start_id}__{i.end_id}" for i in graph_datas["graph"].edges])

        res["dsl"] = {"nodes": merge_dsl_nodes, "edges": merge_dsl_edges}
        res["graph"] = Graph(nodes=merge_gbase_nodes, edges=merge_gbase_edges, paths=[])
        return res

    def get_intents(self, rootid, text: str):
        '''according contents search intents'''
        if rootid is None or rootid=="":
            raise Exception(f"rootid={rootid}, it is empty")
        
        result = self.intention_router.get_intention_by_node_info_nlp(
            root_node_id=rootid,
            query=text,
            start_from_root=True,
            gb_handler=self.gb,
            tb_handler=self.tb,
            agent=self.model
        )
        return result.get("node_id", ), []
    
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
    
    def transform2sls(
            self, node_edge_dict: dict, pnode_ids: List[str], teamid: str=''
        ) -> EKGSlsData:
        # type类型处理也要注意下
        sls_nodes, sls_edges = [], []
        for node_idx, node_info in node_edge_dict['nodes'].items():
            node_type = node_info['type'].lower()
            node_id = str(uuid.uuid4()).replace("-", "_")
            node_info['node_id_new'] = node_id

            ekg_slsdata = EKGGraphSlsSchema(
                id=node_id,
                type='opsgptkg_' + node_type,
                name=node_info['content'],
                description=node_info['content'],
                need_check='false',
                operation_type='ADD',
                teamids=teamid,
                gdb_timestamp=getCurrentTimestap(),
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
                            teamids=teamid,
                            original_src_id1__=pid,
                            original_dst_id2__=node_id,
                            gdb_timestamp=getCurrentTimestap(),
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
                    teamids=teamid,
                    original_src_id1__=start_id,
                    original_dst_id2__=end_id,
                    gdb_timestamp=getCurrentTimestap(),
                )
            )
        return EKGSlsData(nodes=sls_nodes, edges=sls_edges)
    
    def transform2tbase(self, ekg_sls_data: EKGSlsData, teamid: str) -> EKGTbaseData:
        tbase_nodes, tbase_edges = [], []

        for node in ekg_sls_data.nodes:
            name = node.name
            description = node.description
            name_vector = self._get_embedding(name)
            description_vector = self._get_embedding(description)
            tbase_nodes.append(
                EKGNodeTbaseSchema(
                    node_id=node.id,
                    node_type=node.type,
                    node_str=teamid,
                    name_keyword=" | ".join(extract_tags(name, topK=None)),
                    description_keyword=" | ".join(extract_tags(description, topK=None)),
                    name_vector= name_vector[name],
                    description_vector= description_vector[description],
                )
            )
        for edge in ekg_sls_data.edges:
            edge_type = "opsgptkg_"+edge.type.split("_")[2] +\
                "_route_" + "opsgptkg_"+edge.type.split("_")[3]
            tbase_edges.append(
                EKGEdgeTbaseSchema(
                    edge_id=f"{edge.start_id}__{edge.end_id}",
                    edge_type=edge_type,
                    edge_source=edge.start_id,
                    edge_target=edge.end_id,
                    edge_str=f'graph_id={teamid}',
                )
            )
        return EKGTbaseData(nodes=tbase_nodes, edges=tbase_edges)

    def transform2dsl(
            self, 
            ekg_sls_data: EKGSlsData, 
            pnode_ids: List[str], 
            all_intents: List[str], 
            teamid: str
        ) -> YuqueDslDatas:
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
        # schedule_id = ''
        for node in ekg_sls_data.nodes:
            # 需要注意下 dsl的id md编码
            nodes.append(
                YuqueDslNodeData(
                    id=f"ekg_node:{node.type}:{node.id}", 
                    type=type_dict.get(node.type.split("opsgptkg_")[-1]), 
                    label=node.description
                )
            )

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
                    id=dsl_pid, type='display',
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
            start_type, end_type = edge.type.split("_")[2:]
            edges.append(
                YuqueDslEdgeData(
                    id=f'{start_type}:{edge.start_id}___{end_type}:{edge.end_id}',
                    source=f"{start_type}:{edge.start_id}",
                    target=f"{end_type}:{edge.end_id}",
                    label=''
                )
            )
        # # 添加意图边
        added_edges = set()
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
                edge_id = f'intent:{start_id}___intent:{end_id}'

                if edge_id not in added_edges:
                    edges.append(
                        YuqueDslEdgeData(
                            id=edge_id,
                            source=f"intent:{start_id}",
                            target=f"intent:{end_id}",
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

    def _update_tbase_attr_for_nodes(self, attrs):
        tbase_attrs = {}
        for k in ["name", "description"]:
            if k in attrs:
                text = attrs.get(k, "")
                text_vector = self._get_embedding(text)
                tbase_attrs[f"{k}_vector"] = np.array(text_vector[text]).\
                        astype(dtype=np.float32).tobytes()
                tbase_attrs[f"{k}_keyword"] = " | ".join(
                    extract_tags(text, topK=None)
                )
        return tbase_attrs
    
    def _update_new_attr_for_nodes(
            self, nodes: List[GNode], teamid: str, teamids_by_nodeid={}, do_check=False
        ):
        '''update new attributes for nodes'''
        nodetype2fields_dict = {}
        for node in nodes:
            node_type = node.type
            
            # match tugraph client, if no error should dumps
            node.attributes["description"] = node.attributes.get("description", "").replace("\n", "\\n")
            if node.id in teamids_by_nodeid:
                teamids = list(set([teamid] +
                    [i.strip() for i in teamids_by_nodeid[node.id].split(",") if i.strip()]
                ))
                node.attributes["teamids"] = ", ".join(teamids)
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

            fields = [field for field in fields if field not in ["__slots__"]]
            missing_fields = [
                field
                for field in fields 
                if field not in ["type", "start_id", "end_id", "ID", "id", "extra"] 
                and field not in node.attributes 
            ]
            if len(missing_fields)>0 and do_check:
                raise Exception(
                    f"node is wrong, type is {node_type}, missing_fields is {missing_fields}, "
                    f"fields is {fields}, data is {node.attributes}"
                )
        
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
    
    def _update_new_attr_for_edges(self, edges: List[GEdge], do_check=True, do_update=False):
        '''update new attributes for nodes'''
        edgetype2fields_dict = {}
        for edge in edges:
            edge_type = edge.type

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

            fields = [field for field in fields if field not in ["__slots__"]]
            check_fields = ["type", "dst_id", "src_id", "DSTID", "SRCID", "timestamp", "ID", "id", "extra"]
            missing_fields = [
                field
                for field in fields 
                if field not in check_fields
                and field not in edge.attributes
            ]
            if len(missing_fields)>0 and do_check:
                raise Exception(
                    f"edge is wrong, type is {edge_type}, missing_fields is {missing_fields}, "
                    f"fields is {fields}, data is {edge.attributes}"
                )

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
            # edge.attributes.pop("extra")
        return edges

    def _normalized_nodes_type(self, nodes: List[GNode]) -> List[GNode]:
        '''将数据进行格式转换'''
        valid_nodes = []
        for node in nodes:
            node_type = node.type
            node_data_dict = {**{"id": node.id, "type": node_type}, **node.attributes}
            node_data_dict = {
                k: 'False' if k in ["enable", "summaryswitch"] and v=="" else v 
                for k,v in node_data_dict.items()
            }
            node_data: EKGNodeSchema = TYPE2SCHEMA[node_type](**node_data_dict)
            valid_node = GNode(id=node.id, type=node_type, attributes=node_data.attributes())
            # match tugraph client, if no error should dumps

            valid_nodes.append(valid_node)
        return valid_nodes

    def _normalized_edges_type(self, edges: List[GEdge]) -> GEdge:
        valid_edges = []
        for edge in edges:
            edge_data: EKGEdgeSchema = TYPE2SCHEMA["edge"](
                **{
                    **{
                        "original_src_id1__": edge.start_id, 
                        "original_dst_id2__": edge.end_id, 
                        "type": edge.type}, 
                    **edge.attributes
                }
            )
            valid_edge = GEdge(
                start_id=edge_data.original_src_id1__, end_id=edge_data.original_dst_id2__, 
                type=edge.type, attributes=edge_data.attributes()
            )
            valid_edges.append(valid_edge)
        return valid_edges