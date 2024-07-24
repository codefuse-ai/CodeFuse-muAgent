import time

from tqdm import tqdm
from loguru import logger

import sys, os

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
print(src_dir)
sys.path.append(src_dir)
from  muagent import db_handler
from muagent.db_handler import NetworkxHandler
from muagent.schemas.memory import GNode, GRelation


node1 = GNode(**{"id": "node1", "attributes": {"name": "test" }})
node2 = GNode(**{"id": "node2", "attributes": {"name": "test" }})
node3 = GNode(**{"id": "node3", "attributes": {"name": "test3" }})
node4 = GNode(**{"id": "node4", "attributes": {"name": "test3" }})

edge1 = GRelation(**{"start_id": "node1", "end_id": "node2", "attributes": {"id": "edge1", "name": "test" }})
edge2 = GRelation(**{"start_id": "node2", "end_id": "node3", "attributes": {"id": "edge2", "name": "test2" }})


nh = NetworkxHandler()
nh.add_node(node1)
nh.add_nodes([node2])
nh.add_nodes([node3, node4])

nh.add_edge(edge1)
nh.add_edges([edge2])

# 
print("search by nodeid")
print(nh.search_nodes_by_nodeid("node1"))
print(nh.search_edges_by_nodeid("node2"))
print(nh.search_edges_by_nodeids("node1", "node2"))

# 
print("search by attr")
print(nh.search_nodes_by_attr(**{"name": "test3"}))
print(nh.search_edges_by_attr(**{"name": "test2"}))

# 
print("save to local")
nh.save_to_local("networkx_test")

#
print("clear cache for search by attr")
nh.clear()
print(nh.search_nodes_by_attr(**{"name": "test3"}))
print(nh.search_edges_by_attr(**{"name": "test2"}))

#
print("load from local for search by attr")
nh.load_from_local("networkx_test")
print(nh.search_nodes_by_attr(**{"name": "test3"}))
print(nh.search_edges_by_attr(**{"name": "test2"}))

#
print("search by nodeid after delete")
nh.delete_node("node1")
print(nh.search_nodes_by_nodeid("node1"))

#
print("search by nodeids after delete")
nh.delete_nodes(["node1", "node2"])
print(nh.search_nodes_by_nodeid("node1"))
print(nh.search_nodes_by_nodeid("node2"))

#
print("search edge by nodeids after delete")
nh.delete_edge("node1", "node2")
print(nh.search_edges_by_nodeids("node1", "node2"))

#
print("search edge by nodeid after delete")
nh.delete_edges_by_nodeid("node1")
print(nh.search_edges_by_nodeids("node1", "node2"))

#
print("search edge by nodeids after delete")
nh.delete_edges([("node1", "node2")])
print(nh.search_edges_by_nodeids("node1", "node2"))