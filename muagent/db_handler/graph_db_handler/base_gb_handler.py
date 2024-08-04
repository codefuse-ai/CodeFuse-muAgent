from typing import List, Dict
import uuid
from loguru import logger
import json

from muagent.schemas.common import *




class GBHandler:

    def __init__(self) -> None:
        pass

    def add_node(self, node: GNode):
        return self.add_nodes([node])

    def add_nodes(self, nodes: List[GNode]):
        pass

    def add_edge(self, edge: GEdge):
        return self.add_edges([edge])

    def add_edges(self, edges: List[GEdge]):
        pass

    def update_node(self, attributes: dict, set_attributes: dict, node_type: str = None, ID: int = None):
        pass

    def update_edge(self, src_id, dst_id, set_attributes: dict, edge_type: str = None):
        pass
    
    def delete_node(self, attributes: dict, node_type: str = None, ID: int = None):
        pass

    def delete_nodes(self, attributes: dict, node_type: str = None, ID: int = None):
        pass

    def delete_edge(self, src_id, dst_id, edge_type: str = None):
        pass

    def delete_edges(self, src_id, dst_id, edge_type: str = None):
        pass

    def search_node_by_nodeid(self, nodeid: str, node_type: str = None) -> GNode:
        pass

    def search_edges_by_nodeid(self, nodeid: str, node_type: str = None) -> List[GEdge]:
        pass
        
    def search_edge_by_nodeids(self, start_id: str, end_id: str, edge_type: str = None) -> GEdge:
        pass
        
    def search_nodes_by_attr(self, attributes: dict) -> List[GNode]:
        pass

    def search_edges_by_attr(self, attributes: dict, edge_type: str = None) -> List[GEdge]:
        pass
    
    def get_current_node(self, attributes: dict, node_type: str = None, return_keys: list = []) -> GNode:
        pass

    def get_current_nodes(self, attributes: dict, node_type: str = None, return_keys: list = []) -> List[GNode]:
        pass
    
    def get_current_edge(self, src_id, dst_id, edge_type:str = None, return_keys: list = []) -> GEdge:
        pass
    
    def get_neighbor_nodes(self, attributes: dict, node_type: str = None, return_keys: list = []) -> List[GNode]:
        pass
    
    def get_neighbor_edges(self, attributes: dict, node_type: str = None, return_keys: list = []) -> List[GEdge]:
        pass

    def get_hop_infos(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: dict = {}, select_attributes: dict = {}) -> Graph:
        pass        
