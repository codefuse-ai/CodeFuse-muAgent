import time
import sys, os
from loguru import logger

try:
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
    # endpoint = os.environ["endpoint"]
    # accessKeyId = os.environ["accessKeyId"]
    # accessKey = os.environ["accessKey"]
except Exception as e:
    # set your config
    # endpoint = ""
    # accessKeyId = ""
    # accessKey = ""
    logger.error(f"{e}")

# import muagent
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)
from muagent.db_handler import GeaBaseHandler
from muagent.schemas.common import GNode, GEdge
from muagent.schemas.db import GBConfig

import copy



# init SLSHandler instance
gb_config = GBConfig(
    gb_type="GeaBaseHandler", 
    extra_kwargs={
        'metaserver_address': os.environ['metaserver_address'],
        'project': os.environ['project'],
        'city': os.environ['city'],
        'lib_path': os.environ['lib_path'],
    }
)
geabase_handler = GeaBaseHandler(gb_config)

# it's a case, you should use your node and edge attributes
node1 = GNode(**{
    "id": "antshanshi311395_1", 
    "type": "opsgptkg_intent",
    "attributes": {
        "path": "shanshi_test",
        "name": "shanshi_test",
        "description":'shanshi_test', 
        "gdb_timestamp": 1719276995619
    }
})

edge1 = GEdge(**{
    "start_id": "antshanshi311395_1", 
    "end_id": "antshanshi311395_2", 
    "type": "opsgptkg_intent_route_opsgptkg_intent",
    "attributes": {
        "@timestamp": 1719276995619,
        "original_src_id1__": "antshanshi311395_1",  
        "original_dst_id2__": "antshanshi311395_2", 
        "gdb_timestamp": 1719276995619
    }
})

edge2 = GEdge(**{
    "start_id": "antshanshi311395_2", 
    "end_id": "antshanshi311395_3", 
    "type": "opsgptkg_intent_route_opsgptkg_intent",
    "attributes": {
        "@timestamp": 1719276995619,
        "original_src_id1__": "antshanshi311395_2",  
        "original_dst_id2__": "antshanshi311395_3", 
        "gdb_timestamp": 1719276995619
    }
})

node2 = copy.deepcopy(node1)
node2.id = "antshanshi311395_2"

node3 = copy.deepcopy(node1)
node3.id = "antshanshi311395_3"

# 添加节点
t = geabase_handler.add_node(node1)
print(t)

t = geabase_handler.add_nodes([node2, node3])
print(t)

t = geabase_handler.add_edges([edge1, edge2])
print(t)

# 测试节点的查改删
t = geabase_handler.get_current_node(attributes={"id": "antshanshi311395_1",}, node_type="opsgptkg_intent", )
print(t)

t = geabase_handler.update_node(attributes={"id": "antshanshi311395_1",}, node_type="opsgptkg_intent", set_attributes={"name": "shanshi_test_rename"}, )
print(t)

t = geabase_handler.get_current_node(attributes={"id": "antshanshi311395_1",}, node_type="opsgptkg_intent", )
print(t)

t = geabase_handler.delete_node(attributes={"id": "antshanshi311395_1",}, node_type="opsgptkg_intent", )
print(t)

t = geabase_handler.get_current_node(attributes={"id": "antshanshi311395_1",}, node_type="opsgptkg_intent", )
print(t)

# 测试边的查改删
t = geabase_handler.get_current_edge(
    edge_type="opsgptkg_intent_route_opsgptkg_intent", src_id="antshanshi311395_1", dst_id="antshanshi311395_2")
print(t)

t = geabase_handler.update_edge(
    edge_type="opsgptkg_intent_route_opsgptkg_intent", set_attributes={"gdb_timestamp": 1719276995623}, src_id="antshanshi311395_1", dst_id="antshanshi311395_2")
print(t)

t = geabase_handler.get_current_edge(
    edge_type="opsgptkg_intent_route_opsgptkg_intent", src_id="antshanshi311395_1", dst_id="antshanshi311395_2")
print(t)

t = geabase_handler.delete_edge(
    edge_type="opsgptkg_intent_route_opsgptkg_intent", src_id="antshanshi311395_1", dst_id="antshanshi311395_2")
print(t)

t = geabase_handler.get_current_edge(
    edge_type="opsgptkg_intent_route_opsgptkg_intent", src_id="antshanshi311395_1", dst_id="antshanshi311395_2")
print(t)
