from typing import List, Dict
import uuid
from loguru import logger
import json

try:
    from gdbc2.geabase_client import GeaBaseClient, Node, Edge, MutateBatchOperation, GeaBaseUtil
    from gdbc2.geabase_env import GeaBaseEnv
except:
    logger.error("ignore this sdk")

from .base_gb_handler import GBHandler
from muagent.db_handler.utils import deduplicate_dict
from muagent.schemas.db import GBConfig
from muagent.schemas.common import *
from muagent.utils.common_utils import double_hashing, func_timer


class GeaBaseHandler(GBHandler):
    def __init__(
        self,
        gb_config: GBConfig = None
    ):
        self.metaserver_address = gb_config.extra_kwargs.get("metaserver_address")
        self.project = gb_config.extra_kwargs.get("project")
        self.city = gb_config.extra_kwargs.get("city")
        self.lib_path = gb_config.extra_kwargs.get("lib_path")
        self.graph_name = gb_config.extra_kwargs.get("graph_name")

        try:
            GeaBaseEnv.init(self.lib_path)
        except Exception as e:
            logger.error(f"{e}")

        if self.graph_name:
            self.geabase_client = GeaBaseClient(
                self.metaserver_address, self.project,self.city,
                graph_name=self.graph_name
            )
            self.hop_max = 6
        else:
            self.geabase_client = GeaBaseClient(
                self.metaserver_address, self.project,self.city,
            )
            self.hop_max = 8

        # option 指定
        self.option = GeaBaseEnv.QueryRequestOption.newBuilder().gqlType(GeaBaseEnv.QueryProtocol.GQLType.GQL_ISO).build()

    def execute(self, gql: str, option=None, return_keys: list = []) -> Dict:
        option = option or self.option
        logger.info(f"{gql}")
        # return {"error": True}
        result = self.geabase_client.executeGQL(gql, option)
        result = json.loads(str(result.getJsonGQLResponse()))
        return result

    def add_node(self, node: GNode) -> GbaseExecStatus:
        return self.add_nodes([node])

    def add_nodes(self, nodes: List[GNode]) -> GbaseExecStatus:
        node_str_list = []
        for node in nodes:
            node_type = node.type
            node_attributes = {"id": node.id}
            node_attributes["@id"] = node.attributes.pop("ID", "") or double_hashing(node.id)
            node_attributes.update(node.attributes)

            node_str = ", ".join([f"{k}: '{v}'" if isinstance(v, (str, bool)) else f"{k}: {v}" for k, v in node_attributes.items()])
            node_str_list.append(f"(:{node_type} {{{node_str}}})")

        gql = f"INSERT {','.join(node_str_list)}"
        return self._get_crud_status(self.execute(gql))

    def add_edge(self, edge: GEdge) -> GbaseExecStatus:
        return self.add_edges([edge])

    def add_edges(self, edges: List[GEdge]) -> GbaseExecStatus:
        '''不支持批量edge插入'''
        edge_str_list = []
        for edge in edges:
            edge_type = edge.type
            edge_attributes = {
                "@src_id": edge.attributes.pop("SRCID", 0) or double_hashing(edge.start_id,),
                "@dst_id": edge.attributes.pop("DSTID", 0) or double_hashing(edge.end_id,)
            }
            edge_attributes.update(edge.attributes)

            edge_str = ", ".join([f"{k}: '{v}'" if isinstance(v, (str, bool)) else f"{k}: {v}" for k, v in edge_attributes.items()])
            edge_str_list.append(f"()-[:{edge_type} {{{edge_str}}}]->()")

        gql = f"INSERT {','.join(edge_str_list)}"
        return self._get_crud_status(self.execute(gql))

    def update_node(self, attributes: dict, set_attributes: dict, node_type: str = None, ID: int = None) -> GbaseExecStatus:
        # demo: "MATCH (n:opsgptkg_employee {@ID: xxxx}) SET n.originname = 'xxx', n.description = 'xxx'"
        set_str = ", ".join([
            f"n.{k}='{v}'" if isinstance(v, (str, bool)) else f"n.{k}={v}"
            for k, v in set_attributes.items()
            if k not in ["ID"]
        ])

        if (ID is None) or (not isinstance(ID, int)):
            ID = self.get_current_nodeID(attributes, node_type)
            # ID = double_hashing(ID)
        gql = f"MATCH (n:{node_type}) WHERE n.@ID={ID} SET {set_str}"
        return self._get_crud_status(self.execute(gql))

    def update_edge(self, src_id, dst_id, set_attributes: dict, edge_type: str = None) -> GbaseExecStatus:
        # geabase 不支持直接根据边关系进行检索
        src_id, dst_id, timestamp = self.get_current_edgeID(src_id, dst_id, edge_type)
        src_type, dst_type = self.get_nodetypes_by_edgetype(edge_type)
        # src_id, dst_id = double_hashing(src_id), double_hashing(dst_id)
        set_str = ", ".join([
            f"e.{k}='{v}'"  if isinstance(v, (str, bool)) else f"e.{k}={v}" 
            for k, v in set_attributes.items()
        ])
        # demo： MATCH ()-[r:PlayFor{@src_id:1, @dst_id:100, @timestamp:0}]->() SET r.contract = 0;
        # gql = f"MATCH ()-[e:{edge_type}{{@src_id:{src_id}, @dst_id:{dst_id}, timestamp:{timestamp}}}]->() SET {set_str}"
        gql = f"MATCH (n0:{src_type} {{@id: {src_id}}})-[e]->(n1:{dst_type} {{@id:{dst_id}}}) SET {set_str}"
        return self._get_crud_status(self.execute(gql))
    
    def delete_node(self, attributes: dict, node_type: str = None, ID: int = None) -> GbaseExecStatus:
        if (ID is None) or (not isinstance(ID, int)):
            ID = self.get_current_nodeID(attributes, node_type)
            # ID = double_hashing(ID)
        gql = f"MATCH (n:{node_type}) WHERE n.@ID={ID} DELETE n"
        return self._get_crud_status(self.execute(gql))

    def delete_nodes(self, attributes: dict, node_type: str = None, IDs: List[int] = []) -> GbaseExecStatus:
        if (IDs is None) or len(IDs)==0:
            IDs = self.get_nodeIDs(attributes, node_type)
            # ID = double_hashing(ID)
        gql = f"MATCH (n:{node_type}) WHERE n.@ID in {IDs} DELETE n"
        return self._get_crud_status(self.execute(gql))

    def delete_edge(self, src_id, dst_id, edge_type: str = None) -> GbaseExecStatus:
        # geabase 不支持直接根据边关系进行检索
        src_id, dst_id, timestamp = self.get_current_edgeID(src_id, dst_id, edge_type)
        src_type, dst_type = self.get_nodetypes_by_edgetype(edge_type)
        # src_id, dst_id = double_hashing(src_id), double_hashing(dst_id)
        # demo： MATCH ()-[r:PlayFor{@src_id:1, @dst_id:100, @timestamp:0}]->() SET r.contract = 0;
        gql = f"MATCH (n0:{src_type} {{@id: {src_id}}})-[e]->(n1:{dst_type} {{@id:{dst_id}}}) DELETE e"
        return self._get_crud_status(self.execute(gql))
    
    def delete_edges(self, id_pairs: List, edge_type: str = None) -> GbaseExecStatus:
        # geabase 不支持直接根据边关系进行检索
        src_id, dst_id, timestamp = self.get_current_edgeID(src_id, dst_id, edge_type)
        # src_id, dst_id = double_hashing(src_id), double_hashing(dst_id)
        gql = f"MATCH ()-[e:{edge_type}{{@src_id:{src_id}, @dst_id:{dst_id}}}]->() DELETE e"
        gql = f"MATCH (n:opsgptkg_intent )-[r]->(t1) DELETE r"
        return self._get_crud_status(self.execute(gql))
    
    def get_nodeIDs(self, attributes: dict, node_type: str) -> List[int]:
        result = self.get_current_nodes(attributes, node_type)
        return [i.attributes.get("ID") for i in result]

    def get_current_nodeID(self, attributes: dict, node_type: str) -> int:
        result = self.get_current_node(attributes, node_type)
        return result.attributes.get("ID")
    
    def get_current_edgeID(self, src_id, dst_id, edeg_type:str = None):
        if not isinstance(src_id, int) or not isinstance(dst_id, int):
            result = self.get_current_edge(src_id, dst_id, edeg_type)
            return result.attributes.get("SRCID"), result.attributes.get("DSTID"), result.attributes.get("timestamp")
        else:
            return src_id, dst_id, 1
    
    def get_current_node(self, attributes: dict, node_type: str = None, return_keys: list = []) -> GNode:
        return self.get_current_nodes(attributes, node_type, return_keys)[0]
    
    def get_nodes_by_ids(self, ids: List[int] = []) -> List[GNode]:
        where_str = f'@id in {ids}'
        gql = f"MATCH (n0 WHERE {where_str}) RETURN n0"
        # 
        result = self.execute(gql, return_keys=[])
        result = self.decode_result(result, gql)
        nodes = result.get("n0", []) or result.get("n0.attr", []) 
        return [GNode(id=node["id"], type=node["type"], attributes=node) for node in nodes]

    def get_current_nodes(self, attributes: dict, node_type: str = None, return_keys: list = []) -> List[GNode]:
        # 
        extra_keys = list(set(return_keys + ["@ID", "id", "@node_type"]))
        return_str = ", ".join([f"n0.{k}" for k in extra_keys]) if return_keys else "n0"
        where_str = ' and '.join([f"n0.{k}='{v}'" for k,v in attributes.items()])
        gql = f"MATCH (n0:{node_type}) WHERE {where_str} RETURN {return_str}"
        # 
        result = self.execute(gql, return_keys=return_keys)
        result = self.decode_result(result, gql)

        nodes = result.get("n0", []) or result.get("n0.attr", [])
        return self.convert2GNodes(nodes)
    
    def get_current_edge(self, src_id, dst_id, edge_type:str = None, return_keys: list = []) -> GEdge:
        # todo 业务逻辑
        src_type, dst_type = self.get_nodetypes_by_edgetype(edge_type)
        # todo 看是否能调整不需要节点类型
        gql = f"MATCH (n0: {src_type} {{id: '{src_id}'}})-[e]->(n1: {dst_type} {{id: '{dst_id}'}}) RETURN e"
        # 
        result = self.execute(gql, return_keys=return_keys)
        result = self.decode_result(result, gql)

        edges = result.get("e", []) or result.get("e.attr", [])
        return self.convert2GEdges(edges)[0]
    
    def get_neighbor_nodes(self, attributes: dict, node_type: str = None, return_keys: list = [], reverse=False) -> List[GNode]:
        # 
        extra_keys = list(set(return_keys + ["@ID", "id", "@node_type"]))
        return_str = ", ".join([f"n1.{k}" for k in extra_keys]) if return_keys else "n1"
        where_str = ' and '.join([f"n0.{k}='{v}'" for k, v in attributes.items()])
        if reverse:
            gql = f"MATCH (n0:{node_type} WHERE {where_str})<-[e]-(n1) RETURN {return_str}"
        else:
            gql = f"MATCH (n0:{node_type})-[e]->(n1) WHERE {where_str} RETURN {return_str}"
        # 
        result = self.execute(gql, return_keys=return_keys)
        result = self.decode_result(result, gql)
        nodes = result.get("n1", []) or result.get("n1.attr", [])
        return self.convert2GNodes(nodes)
    
    def get_neighbor_edges(self, attributes: dict, node_type: str = None, return_keys: list = []) -> List[GEdge]:
        # 
        extra_keys = list(set(return_keys + ["@SRCID", "@DSTID", "@edge_type"]))
        return_str = ", ".join([f"e.{k}" for k in extra_keys]) if return_keys else "e"
        where_str = ' and '.join([f"n0.{k}='{v}'" for k, v in attributes.items()])
        gql = f"MATCH (n0:{node_type})-[e]->(n1) WHERE {where_str} RETURN {return_str}"
        # 
        result = self.execute(gql, return_keys=return_keys)
        result = self.decode_result(result, gql)

        edges = result.get("e", []) or result.get("e.attr", [])
        return self.convert2GEdges(edges)

    def check_neighbor_exist(self, attributes: dict, node_type: str = None, check_attributes: dict = {}) -> bool:
        result = self.get_neighbor_nodes(attributes, node_type,)
        filter_result = [i for i in result if all([item in i.attributes.items() for item in check_attributes.items()])]
        return len(filter_result) > 0

    def get_hop_infos(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: List[dict] = [], select_attributes: dict = {}, reverse=False) -> Graph:
        '''
        hop >= 2， 表面需要至少两跳
        '''
        hop_max = self.hop_max
        # 
        where_str = ' and '.join([f"n0.{k}='{v}'" for k, v in attributes.items()])
        if reverse:
            gql = f"MATCH p = (n0:{node_type} WHERE {where_str})<-[e]-{{1,{min(hop, hop_max)}}}(n1) RETURN n0, n1, e, p"
        else:
            gql = f"MATCH p = (n0:{node_type} WHERE {where_str})-[e]->{{1,{min(hop, hop_max)}}}(n1) RETURN n0, n1, e, p"
        last_node_ids, last_node_types = [], []

        result = {}
        iter_index = 0
        while hop > 1:
            if last_node_ids == [] and iter_index==0:
                # 
                result = self.execute(gql)
                result = self.decode_result(result, gql)
            elif last_node_ids == []:
                pass
            else:
                for _node_id, _node_type in zip(last_node_ids, last_node_types):
                    where_str = f"n0.id='{_node_id}'"
                    if reverse:
                        gql = f"MATCH p = (n0:{_node_type} WHERE {where_str})<-[e]-{{1,{min(hop, hop_max)}}}(n1) RETURN n0, n1, e, p"
                    else:
                        gql = f"MATCH p = (n0:{_node_type} WHERE {where_str})-[e]->{{1,{min(hop, hop_max)}}}(n1) RETURN n0, n1, e, p"
                    # 
                    _result = self.execute(gql)
                    _result = self.decode_result(_result, gql)
                    # logger.info(f"p_lens: {_result['p']}")
        
                    result = self.merge_hotinfos(result, _result, reverse=reverse)
            # 
            last_node_ids, last_node_types, result = self.deduplicate_paths(result, block_attributes, select_attributes, hop=min(hop, hop_max)+iter_index*hop_max, reverse=reverse)
            hop -= hop_max
            iter_index += 1

        nodes = self.convert2GNodes(result.get("n1", [])+result.get("n0", []))
        edges = self.convert2GEdges(result.get("e", []))
        return Graph(nodes=nodes, edges=edges, paths=result.get("p", []))
    
    def get_hop_nodes(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: List[dict] = []) -> List[GNode]:
        # 
        result = self.get_hop_infos(attributes, node_type, hop, block_attributes)
        return result.nodes

    def get_hop_edges(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: List[dict] = []) -> List[GEdge]:
        # 
        result = self.get_hop_infos(attributes, node_type, hop, block_attributes)
        return result.edges

    def get_hop_paths(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: List[dict] = []) -> List[str]:
        # 
        result = self.get_hop_infos(attributes, node_type, hop, block_attributes)
        return result.paths

    def deduplicate_paths(self, result, block_attributes: List[dict] = {}, select_attributes: dict = {}, hop:int=None, reverse=False):
        # 获取数据
        n0, n1, e, p = result["n0"], result["n1"], result["e"], result["p"]
        block_node_ids = [
            i["id"]
            for i in n0+n1
            for block_attribute in block_attributes
            # 这里block为空时也会生效，属于合理情况
            # if block_attributes=={} or all(item in i.items() for item in block_attributes.items())
            if block_attribute and all(item in i.items() for item in block_attribute.items())
        ] + [
            i["id"]
            for i in n0+n1
            if select_attributes and not all(item not in i.items() for item in select_attributes.items())
        ]
        p = [_p for _p in p if all([_pid not in block_node_ids for _pid in _p])]
        # deduplicate the paths
        path_strs = ["&&".join(_p) for _p in p]
        new_p = []
        add_path_strs = set()
        for path_str, _p in zip(path_strs, p):
            if path_str in add_path_strs: continue
            if not any(path_str in other for other in path_strs if path_str != other):
                new_p.append(_p)
                add_path_strs.add(path_str)
            
        # 根据保留路径进行合并
        nodeid2type = {i["id"]: i["type"] for i in n0+n1}
        unique_node_ids = [j for i in new_p for j in i]
        if reverse:
            last_node_ids = list(set([i[0] for i in new_p if len(i)>=hop and i[0] not in i[1:]]))
        else:
            last_node_ids = list(set([i[-1] for i in new_p if len(i)>=hop and i[-1] not in i[:-1]]))

        last_node_types = [nodeid2type[i] for i in last_node_ids]
        new_n0 = deduplicate_dict([i for i in n0 if i["id"] in unique_node_ids])
        new_n1 = deduplicate_dict([i for i in n1 if i["id"] in unique_node_ids])
        new_e = deduplicate_dict([i for i in e if i["start_id"] in unique_node_ids and i["end_id"] in unique_node_ids])

        return last_node_ids, last_node_types, {"n0": new_n0, "n1": new_n1, "e": new_e, "p": new_p}

    def merge_hotinfos(self, result1, result2, reverse=False) -> Dict:
        old_n0_sets = set([n["id"] for n in result1["n0"]])
        old_n1_sets = set([n["id"] for n in result1["n1"]])
        new_n0 = result1["n0"] + [n for n in result2["n0"] if n["id"] not in old_n0_sets]
        new_n1 = result1["n1"] + [n for n in result2["n1"] if n["id"] not in old_n1_sets]
        new_e = result1["e"] + result2["e"]
        if reverse:
            new_p = result1["p"] + [
                p_old_2[:-1] + p_old_1
                for p_old_1 in result1["p"] 
                for p_old_2 in result2["p"] 
                if p_old_2[-1] == p_old_1[0]
            ] # + result2["p"]
        else:
            new_p = result1["p"] + [
                p_old_1 + p_old_2[1:]
                for p_old_1 in result1["p"] 
                for p_old_2 in result2["p"] 
                if p_old_2[0] == p_old_1[-1]
            ] # + result2["p"]
        new_result = {"n0": new_n0, "n1": new_n1, "e": new_e, "p": new_p}
        return new_result
    
    def decode_result(self, geabase_result, gql: str) -> Dict:
        return_keys = gql.split("RETURN")[-1].split(',')
        save_keys = [k.strip() if "." not in k else k.strip().split(".")[0]+".attr" for k in return_keys]
        
        decode_geabase_result_func_by_key = {
            "p": self.decode_path,
            "n0": self.decode_vertex,
            "n1": self.decode_vertex,
            "e": self.decode_edge,
            "n0.attr": self.decode_attribute,
            "n1.attr": self.decode_attribute,
            "e.attr": self.decode_attribute,
         }
        
        output = {k: [] for k in save_keys}
        if "resultSet" in geabase_result:
            # decode geabase result
            for row in geabase_result['resultSet']['rows']:
                attr_dict = {}
                for col_data, rk, sk in zip(row["columns"], return_keys, save_keys):
                    _decode_func = decode_geabase_result_func_by_key.get(sk, self.decode_attribute)
                    # print(sk, json.dumps(col_data, ensure_ascii=False, indent=2))
                    decode_reuslt = _decode_func(col_data, rk)
                    if ".attr" in sk:
                        attr_dict.setdefault(sk, {}).update(decode_reuslt)
                        
                    # print(sk, decode_reuslt)
                
                    if sk=="e":
                        output[sk].extend(decode_reuslt)
                    elif ".attr" in sk:
                        pass
                    else:
                        output[sk].append(decode_reuslt)

                for sk, v in attr_dict.items():
                    v = {kk.split(".")[-1]: vv for kk, vv in v.items()}
                    if "@node_type" in v:
                        v["type"] = v.pop("@node_type")

                    if "@edge_type" in v:
                        v["type"] = v.pop("@edge_type")
                    
                    output[sk].append(v)

        return output

    def decode_path(self, col_data, k) -> List:
        steps = col_data.get("pathVal", {}).get("steps", [])
        connections = {}
        head = None
        path = []
        for idx, step in enumerate(steps):
            props = step["props"]
            start = props["original_src_id1__"].get("strVal", "") or props["original_src_id1__"].get("intVal", -1)
            end = props["original_dst_id2__"].get("strVal", "") or props["original_dst_id2__"].get("intVal", -1)
            connections[start] = end

            head = start if idx==0 else head
            path = [start] if idx==0 else path

        # 找到头部（1）
        for k in connections:
            if k not in connections.values():
                head = k
                path = [head]

        # 根据连通关系构建路径
        while head in connections:
            head = connections[head]
            if head in path: break
            path.append(head)
            if head == path[0]: break
        return path
    
    def decode_vertex(self, col_data, k) -> Dict:
        vertextVal = col_data.get("vertexVal", {})
        node_val_json = {
            **{"ID": int(vertextVal.get("id", "")), "type": vertextVal.get("type", "")}, 
            **{k: v.get("strVal", "") if "strVal" in v else v.get("intVal", "0") for k, v in vertextVal.get("props", {}).items()}
        }
        node_val_json.pop("biz_node_id", "")
        return node_val_json
    
    def decode_edge(self, col_data, k) -> Dict:
        def _decode_edge(data):
            edgeVal= data.get("edgeVal", {})
            edge_val_json = {
                **{"SRCID": int(edgeVal.get("srcId", "")), "DSTID": int(edgeVal.get("dstId", "")), "type": edgeVal.get("type", "")}, 
                **{k: v.get("strVal", "") if "strVal" in v else v.get("intVal", "0") for k, v in edgeVal.get("props", {}).items()}
            }
            # 存在业务逻辑
            edge_val_json["start_id"] = edge_val_json.pop("original_src_id1__")
            edge_val_json["end_id"] = edge_val_json.pop("original_dst_id2__")
            return edge_val_json
    
        edge_val_jsons = []
        if "listVal" in col_data:
            for val in col_data["listVal"].get("vals", []):
                edge_val_jsons.append(_decode_edge(val))
        elif "edgeVal" in col_data:
            edge_val_jsons = [_decode_edge(col_data)]
    
        return edge_val_jsons
    
    def decode_attribute(self, col_data, k) -> Dict:
        return {k: col_data.get("strVal", "") or col_data.get("intVal", "0")}
    
    def _get_crud_status(self, result: Dict) -> GbaseExecStatus:
        '''Mapping error messages to error codes.'''
        text2code = {
            "lack error message": -1,
            "GDB_SUCCEED": 0,
            "GDB_ENGINE_PRIMARY_KEY_DUPLICATE": 1,
            "GDB_ENGINE_PROP_INVALID": 2,
            "GDB_SCHEMA_LACK_GRAPH_PROP": 3,
            "GDB_COMMON_PARSE_ERROR": 4,
            "GDB_SCHEMA_GRAPH_PROP_NOT_EXIST": 5,
        }
        error_message = result.get("status", {}).get("errorMessage", "lack error message")
        return GbaseExecStatus(
            errorMessage=error_message, 
            errorCode=text2code[error_message], 
        )

    def get_nodetypes_by_edgetype(self, edge_type: str):
        src_type, dst_type = edge_type.split("_opsgptkg")[0], "opsgptkg_" + edge_type.split("_opsgptkg_")[1]
        for edge_bridge in ["_route_", "_extend_"]:
            if edge_bridge in edge_type:
                src_type, dst_type = edge_type.split(edge_bridge)
                break
        return src_type, dst_type
    
    def convert2GNodes(self, raw_nodes: List[Dict]) -> List[GNode]:
        nodes = []
        nodeids_set = set()
        for node in raw_nodes:
            node_id = node.pop("id")
            node_type = node.pop("type")
            if node_id not in nodeids_set:
                nodes.append(GNode(id=node_id, type=node_type, attributes=node))
                nodeids_set.add(node_id)
        return nodes
    
    def convert2GEdges(self, raw_edges: List[Dict]) -> List[GEdge]:
        edges = []
        for edge in raw_edges:
            start_id = edge.pop("start_id")
            end_id = edge.pop("end_id")
            edge_type = edge.pop("type")
            edges.append(GEdge(start_id=start_id, end_id=end_id, type=edge_type, attributes=edge))
        return edges