from typing import List, Dict
import numpy as np
import random

from .ekg_construct_base import *
from muagent.schemas.common import *

from muagent.llm_models.get_embedding import get_embedding
from muagent.utils.common_utils import getCurrentDatetime, getCurrentTimestap


def getClassFields(model):
    # 收集所有字段，包括继承自父类的字段
    all_fields = set(model.__annotations__.keys())
    for base in model.__bases__:
        if hasattr(base, '__annotations__'):
            all_fields.update(getClassFields(base))
    return all_fields


class EKGDBService(EKGConstructService):

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
            kb_root_path: str = KB_ROOT_PATH
    ):
        super().__init__(embed_config, llm_config, db_config, vb_config, gb_config, tb_config, sls_config, do_init, kb_root_path)

    def add_nodes(self, nodes: List[GNode], teamid: str):
        nodetype2fields_dict = {}
        for node in nodes:
            node_type = node.type
            node.attributes["teamid"] = teamid
            node.attributes["gdb_timestamp"] = getCurrentTimestap()
            node.attributes["version"] = getCurrentDatetime()
            node.attributes.setdefault("extra", '{}')

            # todo 根据节点类型进行数据校验
            schema = node_type
            if node_type in nodetype2fields_dict:
                fields = nodetype2fields_dict[node_type]
            else:
                fields = list(getClassFields(schema))
                nodetype2fields_dict[node_type] = fields

            flag = any([
                field not in node.attributes 
                for field in fields 
                if field not in ["start_id", "end_id", "id"]
            ])
            if flag:
                raise Exception(f"node is wrong, type is {node_type}, fields is {fields}, data is {node.attributes}")
        
        tbase_nodes = [{
            "node_id": f'''ekg_node:{teamid}:{node.id}''',
            "node_type": node.type, 
            "node_str": f"graph_id={teamid}", 
            "node_vector": np.array([random.random() for _ in range(768)]).astype(dtype=np.float32).tobytes()
            }
            for node in nodes
        ]

        try:
            gb_result = self.gb.add_nodes(nodes)
            tb_result = self.tb.insert_data_hash(tbase_nodes, key_name='node_id', need_etime=False)
        except Exception as e:
            pass

        return gb_result or tb_result

    def add_edges(self, edges: List[GEdge], teamid: str):
        edgetype2fields_dict = {}
        for edge in edges:
            edge_type = edge.type
            edge.attributes["teamid"] = teamid
            edge.attributes["@timestamp"] = getCurrentTimestap()
            edge.attributes["gdb_timestamp"] = getCurrentTimestap()
            edge.attributes["version"] = getCurrentDatetime()
            edge.attributes["extra"] = '{}'

            # todo 根据边类型进行数据校验
            schema = edge_type
            if edge_type in edgetype2fields_dict:
                fields = edgetype2fields_dict[edge_type]
            else:
                fields = list(getClassFields(schema))
                edgetype2fields_dict[edge_type] = fields

            flag = any([field not in edge.attributes for field in fields if field not in ["start_id", "end_id", "id"]])
            if flag:
                raise Exception(f"edge is wrong, type is {edge_type}, data is {edge.attributes}")
            
        tbase_edges = [{
            'edge_id': f"ekg_edge:{teamid}{edge.start_id}:{edge.end_id}",
            'edge_type': edge.type,
            'edge_source': edge.start_id,
            'edge_target': edge.end_id,
            'edge_str': f'graph_id={teamid}'
            }
            for edge in edges
        ]

        try:
            gb_result = self.gb.add_edges(edges)
            tb_result = self.tb.insert_data_hash(tbase_edges, key="edge_id", need_etime=False)
        except Exception as e:
            pass

        return gb_result or tb_result

    def delete_nodes(self, nodes: List[GNode], teamid: str):
        # delete tbase nodes
        r = self.tb.search(f"@node_str: 'graph_id={teamid}'", index_name='ekg_node')
        tbase_nodeids = [data['id'] for data in r.docs] # 存疑
        delete_nodeids = [node.id for node in nodes]
        tbase_missing_nodeids = [nodeid for nodeid in delete_nodeids if nodeid not in tbase_nodeids]
        delete_tbase_nodeids = [nodeid for nodeid in delete_nodeids if nodeid in tbase_nodeids]

        if len(tbase_missing_nodeids) > 0:
            logger.error(f"there must something wrong! ID not match, such as {tbase_missing_nodeids}")

        # delete the nodeids in tbase
        tb_result = []
        for nodeid in delete_tbase_nodeids:
            self.tb.delete(nodeid)
            resp = self.tb.delete(nodeid)
            tb_result.append(resp)
        # logger.info(f'id={nodeid}, delete resp={resp}')

        # delete the nodeids in geabase
        gb_result = self.gb.delete_nodes(delete_tbase_nodeids)
        
        return gb_result or tb_result
    
    def delete_edges(self, edges: List[GEdge], teamid: str):
        # delete tbase nodes
        r = self.tb.search(f"@edge_str: 'graph_id={teamid}'", index_name='ekg_edge')
        tbase_edgeids = [data['id'] for data in r.docs] # 存疑
        delete_edgeids = [f"edge:{edge.start_id}:{edge.end_id}" for edge in edges]
        tbase_missing_edgeids = [edgeid for edgeid in delete_edgeids if edgeid not in tbase_edgeids]
        delete_tbase_edgeids = [edgeid for edgeid in delete_edgeids if edgeid in tbase_edgeids]

        if len(tbase_missing_edgeids) > 0:
            logger.error(f"there must something wrong! ID not match, such as {tbase_missing_edgeids}")

        # delete the edgeids in tbase
        tb_result = []
        for edgeid in delete_tbase_edgeids:
            self.tb.delete(edgeid)
            resp = self.tb.delete(edgeid)
            tb_result.append(resp)
        # logger.info(f'id={edgeid}, delete resp={resp}')

        # delete the nodeids in geabase
        gb_result = self.gb.delete_edges(delete_tbase_edgeids)
    
    def update_nodes(self, nodes: List[GNode], teamid: str):
        # delete tbase nodes
        r = self.tb.search(f"@node_str: 'graph_id={teamid}'", index_name='ekg_node')
        tbase_nodeids = [data['id'] for data in r.docs] # 存疑
        update_nodeids = [node.id for node in nodes]
        tbase_missing_nodeids = [nodeid for nodeid in update_nodeids if nodeid not in tbase_nodeids]
        update_tbase_nodeids = [nodeid for nodeid in update_nodeids if nodeid in tbase_nodeids]

        if len(tbase_missing_nodeids) > 0:
            logger.error(f"there must something wrong! ID not match, such as {tbase_missing_nodeids}")

        # delete the nodeids in tbase
        tb_result = []
        for node in nodes:
            if node.id not in update_tbase_nodeids: continue
            data = node.attributes
            data.update({"node_id": node.id})
            resp = self.tb.insert_data_hash(data, key="node_id", need_etime=False)
            tb_result.append(resp)
        # logger.info(f'id={nodeid}, delete resp={resp}')

        # update the nodeids in geabase
        gb_result = []
        for node in nodes:
            if node.id not in update_tbase_nodeids: continue
            resp = self.gb.update_node({}, node.attributes, node_type=node.type, ID=node.id)
            gb_result.append(resp)
        return gb_result or tb_result

    def get_node_by_id(self, nodeid: str, node_type:str = None) -> GNode:
        result = self.gb.get_current_node({'id': nodeid}, node_type=node_type)
        nodeid = result.pop("id")
        node_type = result.pop("node_type")
        return GNode(id=nodeid, type=node_type, attributes=result)
    
    def get_graph_by_nodeid(self, nodeid: str, node_type: str, teamid: str, hop: int = 10) -> Graph:
        if hop >= 15:
            raise Exception(f"hop can't be larger than 15, now hop is {hop}")
        # filter the node which dont match teamid
        result = self.gb.get_hop_infos({'id': nodeid}, node_type=node_type, hop=hop, select_attributes={"teamid": teamid})
        return result

    def search_nodes_by_text(self, text: str, node_type: str = None, teamid: str = None, top_k=5) -> List[GNode]:

        if text is None: return []

        # if self.embed_config:
        #     raise Exception(f"can't use vector search, because there is no {self.embed_config}")

        # 直接检索文本
        # r = self.tb.search(text)
        # nodes_by_name = self.gb.get_current_nodes({"name": text}, node_type=node_type)
        # nodes_by_desc = self.gb.get_current_nodes({"description": text}, node_type=node_type)
        
        if self.embed_config:
            vector_dict = get_embedding(
                self.embed_config.embed_engine, [text],
                self.embed_config.embed_model_path, self.embed_config.model_device,
                self.embed_config
            )
            query_embedding = np.array(vector_dict[text]).astype(dtype=np.float32).tobytes()
            base_query = f'(@teamid:{teamid})=>[KNN {top_k} @vector $vector AS distance]'
            query_params = {"vector": query_embedding}
        else:
            query_embedding = np.array([random.random() for _ in range(768)]).astype(dtype=np.float32).tobytes()
            base_query = f'(@teamid:{teamid})'
            query_params = {}

        r = self.tb.vector_search(base_query, query_params=query_params)

        return 

    def search_rootpath_by_nodeid(self, nodeid: str, node_type: str, teamid: str):
        rootid = f"{teamid}"
        result = self.gb.get_hop_infos({"@ID": nodeid}, node_type=node_type, hop=15)

        # 根据nodeid和teamid来检索path
        

