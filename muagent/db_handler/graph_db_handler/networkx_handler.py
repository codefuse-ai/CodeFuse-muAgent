import os
import networkx as nx
from typing import List, Tuple, Dict

from muagent.schemas.memory import *
from muagent.base_configs.env_config import KB_ROOT_PATH
from muagent.schemas.db import GBConfig



class NetworkxHandler:
    def __init__(
            self, 
            kb_root_path: str = KB_ROOT_PATH,
            gb_config: GBConfig = None,
        ):
        self.graph = nx.Graph()  # 使用有向图，根据需要也可以使用无向图 nx.Graph()
        self.kb_root_path = kb_root_path
        self.gb_config = gb_config
        self.kb_name = "default"

    def add_node(self, node: GNode):
        insert_nodes = self.node_process([node])
        self.graph.add_nodes_from(insert_nodes)

    def add_nodes(self, nodes: List[GNode]):
        insert_nodes = self.node_process(nodes)
        self.graph.add_nodes_from(insert_nodes)

    def add_edge(self, grelation: GRelation):
        insert_relations = self.relation_process([grelation])
        self.graph.add_edges_from(insert_relations)

    def add_edges(self, grelations: List[GRelation]):
        insert_relations = self.relation_process(grelations)
        self.graph.add_edges_from(insert_relations)

    def search_nodes_by_nodeid(self, nodeid: str) -> GNode:
        if self.missing_node(nodeid): return None
 
        node_attrs = self.graph.nodes.get(nodeid, {})
        return GNode(id=nodeid, attributes=node_attrs)

    def search_edges_by_nodeid(self, nodeid: str) -> List[GRelation]:
        if self.missing_node(nodeid): return []
            
        return [
            GRelation(
                id=f"{nodeid}-{neighbor}",
                left=self.search_nodes_by_nodeid(nodeid),
                right=self.search_nodes_by_nodeid(neighbor),
                attributes=self.graph.get_edge_data(nodeid, neighbor)
            )
            for neighbor, attr in self.graph.adj[nodeid].items()
        ]
        
    def search_edges_by_nodeids(self, left: str, right: str) -> GRelation:
        if self.missing_node(left) or self.missing_node(right): return None
        if self.missing_edge(left, right): return None

        return GRelation(
                id=f"{left}-{right}",
                left=self.search_nodes_by_nodeid(left),
                right=self.search_nodes_by_nodeid(right),
                attributes=self.graph.get_edge_data(left, right)
            )
        
    def search_nodes_by_attr(self, **attributes) -> List[GNode]:
        return [GNode(id=node, attributes=attr) for node, attr in self.graph.nodes(data=True) if all(attr.get(k) == v for k, v in attributes.items())]

    def search_edges_by_attr(self, **attributes) -> List[GRelation]:
        return [GRelation(
                id=f"{left}-{right}",
                left=self.search_nodes_by_nodeid(left),
                right=self.search_nodes_by_nodeid(right),
                attributes=attr
            ) for left, right, attr in self.graph.edges(data=True) if all(attr.get(k) == v for k, v in attributes.items())]
    
    def save(self, kb_name: str):
        self.kb_name = kb_name or self.kb_name
        self.save_to_local(self.kb_name)

    def load(self, kb_name: str):
        if self.kb_name != kb_name:
            self.kb_name = kb_name if self.kb_name == "default" else self.kb_name
            self.load_from_local(kb_name)

    def save_to_local(self, kb_name: str):
        dir_path = os.path.join(self.kb_root_path, kb_name)
        # 将图保存到本地文件
        nx.write_graphml(self.graph, os.path.join(dir_path, 'graph.graphml'))
        
    def load_from_local(self, kb_name: str):
        dir_path = os.path.join(self.kb_root_path, kb_name)
        # 从本地文件加载图
        if os.path.exists(os.path.join(dir_path, 'graph.graphml')):
            self.graph = nx.read_graphml(os.path.join(dir_path, 'graph.graphml'))

    def delete_node(self, nodeid: str):
        self.graph.remove_node(nodeid)

    def delete_nodes(self, nodeids: List[str]):
        self.graph.remove_nodes_from(nodeids)
        
    def delete_edges_by_nodeid(self, nodeid: str):
        edges = list(self.graph.edges(nodeid))
        self.graph.remove_edges_from(edges)

    def delete_edge(self, left: str, right: str):
        self.graph.remove_edges_from([(left, right)])
        
    def delete_edges(self, edges: List[Tuple]):
        self.graph.remove_edges_from(edges)

    def clear(self):
        self.graph.clear()

    def node_process(self, nodes: List[GNode]) -> List[Tuple]:
        node_list = []
        for node in nodes:
            node_id = node.id
            node_attrs = node.attributes
            node_list.append((node_id, node_attrs))

        return node_list

    def relation_process(self, relations: List[GRelation]) -> List[Tuple]:
        relation_list = []
        for relation in relations:
            edge_attrs = relation.attributes
            relation_list.append((relation.left.id, relation.right.id, edge_attrs))
        return relation_list

    def missing_edge(self, left: str, right: str) -> bool:
        return not self.graph.has_edge(left, right)
        
    def missing_node(self, nodeid: str) -> bool:
        return nodeid not in self.graph.nodes