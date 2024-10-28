from typing import List, Dict
import uuid
from loguru import logger
import json

from muagent.schemas.common import *




class GBHandler:

    def __init__(self) -> None:
        pass

    def add_node(self, node: GNode) -> GbaseExecStatus:
        return self.add_nodes([node])

    def add_nodes(self, nodes: List[GNode]) -> GbaseExecStatus:
        pass

    def add_edge(self, edge: GEdge) -> GbaseExecStatus:
        return self.add_edges([edge])

    def add_edges(self, edges: List[GEdge]) -> GbaseExecStatus:
        pass

    def update_node(self, attributes: dict, set_attributes: dict, node_type: str = None, ID: int = None) -> GbaseExecStatus:
        pass

    def update_edge(self, src_id, dst_id, set_attributes: dict, edge_type: str = None) -> GbaseExecStatus:
        pass
    
    def delete_node(self, attributes: dict, node_type: str = None, ID: int = None) -> GbaseExecStatus:
        pass

    def delete_nodes(self, attributes: dict, node_type: str = None, IDs: List[int] = []) -> GbaseExecStatus:
        pass

    def delete_edge(self, src_id, dst_id, edge_type: str = None) -> GbaseExecStatus:
        pass
    
    def delete_edges(self, id_pairs: List, edge_type: str = None) -> GbaseExecStatus:
        pass
    
    def get_nodeIDs(self, attributes: dict, node_type: str) -> List[int]:
        pass

    def get_current_node(self, attributes: dict, node_type: str = None, return_keys: list = []) -> GNode:
        pass
        
    def get_nodes_by_ids(self, ids: List[int] = []) -> List[GNode]:
        pass

    def get_current_nodes(self, attributes: dict, node_type: str = None, return_keys: list = []) -> List[GNode]:
        pass
    
    def get_current_edge(self, src_id, dst_id, edge_type:str = None, return_keys: list = []) -> GEdge:
        pass
    
    def get_neighbor_nodes(self, attributes: dict, node_type: str = None, return_keys: list = [], reverse=False) -> List[GNode]:
        pass
    
    def get_neighbor_edges(self, attributes: dict, node_type: str = None, return_keys: list = []) -> List[GEdge]:
        pass

    def get_hop_infos(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: List[dict] = {}, select_attributes: dict = {}, reverse=False) -> Graph:
        pass
