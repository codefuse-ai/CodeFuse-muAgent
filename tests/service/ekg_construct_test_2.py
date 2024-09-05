import time
import sys, os
from loguru import logger

try:
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
    api_key = os.environ["OPENAI_API_KEY"]
    api_base_url= os.environ["API_BASE_URL"]
    model_name = os.environ["model_name"]
    model_engine = os.environ["model_engine"]
    embed_model = os.environ["embed_model"]
    embed_model_path = os.environ["embed_model_path"]
except Exception as e:
    # set your config
    api_key = ""
    api_base_url= ""
    model_name = ""
    model_engine = os.environ["model_engine"]
    embed_model = ""
    embed_model_path = ""
    logger.error(f"{e}")

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)

import os, sys
from loguru import logger

sys.path.append("/ossfs/workspace/muagent")
from muagent.schemas.common import GNode, GEdge
from muagent.schemas.db import GBConfig, TBConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig





# 初始化 GeaBaseHandler 实例
gb_config = GBConfig(
    gb_type="GeaBaseHandler", 
    extra_kwargs={
        'metaserver_address': os.environ['metaserver_address'],
        'project': os.environ['project'],
        'city': os.environ['city'],
        'lib_path': os.environ['lib_path'],
    }
)


# 初始化 TbaseHandler 实例
tb_config = TBConfig(
    tb_type="TbaseHandler",
    index_name="muagent_test",
    host=os.environ['host'],
    port=os.environ['port'],
    username=os.environ['username'],
    password=os.environ['password'],
    extra_kwargs={
        'host': os.environ['host'],
        'port': os.environ['port'],
        'username': os.environ['username'] ,
        'password': os.environ['password'],
        'definition_value': os.environ['definition_value']
    }
)

# llm config
llm_config = LLMConfig(
    model_name=model_name, model_engine=model_engine, api_key=api_key, api_base_url=api_base_url, temperature=0.3,
)


# emebdding config
# embed_config = EmbedConfig(
#     embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
# )

# embed_config = EmbedConfig(
#     embed_model="default",
#     langchain_embeddings=embeddings
# )
embed_config = None

ekg_construct_service = EKGConstructService(
    embed_config=embed_config,
    llm_config=llm_config,
    tb_config=tb_config,
    gb_config=gb_config,
)



def generate_node(id, type):
    extra_attr = {"tmp": "hello"}
    if type == "opsgptkg_schedule":
        extra_attr["enable"] = False
        
    if type == "opsgptkg_task":
        extra_attr["accesscriteria"] = "hello"
        extra_attr["executetype"] = "hello"
        
    if type == "opsgptkg_analysis":
        extra_attr["accesscriteria"] = "hello"
        extra_attr["summaryswitch"] = False
        extra_attr['dsltemplate'] = "hello"             
        
    return GNode(**{
        "id": id, 
        "type": type,
        "attributes": {**{
            "path": id,
            "name": id,
            "description": id, 
        }, **extra_attr}
    })


def generate_edge(node1, node2):
    type_connect = "extend" if node1.type == "opsgptkg_intent" and node2.type == "opsgptkg_intent" else "route"
    return GEdge(**{
        "start_id": node1.id, 
        "end_id": node2.id, 
        "type": f"{node1.type}_{type_connect}_{node2.type}",
        "attributes": {
            "lat": "hello",
            "attr": "hello"
        }
    })


nodetypes = [
    'opsgptkg_intent', 'opsgptkg_schedule', 'opsgptkg_task',
    'opsgptkg_phenomenon', 'opsgptkg_analysis'
]

nodes_dict = {}
for nodetype in nodetypes:
    for i in range(8):
        # print(f"shanshi_{nodetype}_{i}")
        nodes_dict[f"shanshi_{nodetype}_{i}"] = generate_node(f"shanshi_{nodetype}_{i}", nodetype)

edge_ids = [
    ["shanshi_opsgptkg_intent_0", "shanshi_opsgptkg_intent_1"],
    ["shanshi_opsgptkg_intent_1", "shanshi_opsgptkg_intent_2"],
    ["shanshi_opsgptkg_intent_2", "shanshi_opsgptkg_schedule_0"],
    ["shanshi_opsgptkg_intent_2", "shanshi_opsgptkg_schedule_1"],
    ["shanshi_opsgptkg_schedule_1", "shanshi_opsgptkg_analysis_3"],
    ["shanshi_opsgptkg_schedule_0", "shanshi_opsgptkg_task_0"],
    ["shanshi_opsgptkg_task_0", "shanshi_opsgptkg_task_1"],
    ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_analysis_0"],
    ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_phenomenon_0"],
    ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_phenomenon_1"],
    ["shanshi_opsgptkg_phenomenon_0", "shanshi_opsgptkg_task_2"],
    ["shanshi_opsgptkg_phenomenon_1", "shanshi_opsgptkg_task_3"],
    ["shanshi_opsgptkg_task_2", "shanshi_opsgptkg_analysis_1"],
    ["shanshi_opsgptkg_task_3", "shanshi_opsgptkg_analysis_2"],
]

nodeid_set = set()
origin_edges = []
origin_nodes = []
for src_id, dst_id in edge_ids:
    origin_edges.append(generate_edge(nodes_dict[src_id], nodes_dict[dst_id]))
    if src_id not in nodeid_set:
        nodeid_set.add(src_id)
        origin_nodes.append(nodes_dict[src_id])
    if dst_id not in nodeid_set:
        nodeid_set.add(dst_id)
        origin_nodes.append(nodes_dict[dst_id])




new_edge_ids = [
    ["shanshi_opsgptkg_intent_0", "shanshi_opsgptkg_intent_1"],
    ["shanshi_opsgptkg_intent_1", "shanshi_opsgptkg_intent_2"],
    ["shanshi_opsgptkg_intent_2", "shanshi_opsgptkg_schedule_0"],
    # 新增
    ["shanshi_opsgptkg_intent_2", "shanshi_opsgptkg_schedule_2"],
    ["shanshi_opsgptkg_schedule_2", "shanshi_opsgptkg_analysis_4"],
    # 
    ["shanshi_opsgptkg_schedule_0", "shanshi_opsgptkg_task_0"],
    ["shanshi_opsgptkg_task_0", "shanshi_opsgptkg_task_1"],
    ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_analysis_0"],
    ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_phenomenon_0"],
    ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_phenomenon_1"],
    ["shanshi_opsgptkg_phenomenon_0", "shanshi_opsgptkg_task_2"],
    ["shanshi_opsgptkg_phenomenon_1", "shanshi_opsgptkg_task_3"],
    ["shanshi_opsgptkg_task_2", "shanshi_opsgptkg_analysis_1"],
    ["shanshi_opsgptkg_task_3", "shanshi_opsgptkg_analysis_2"],
]

nodeid_set = set()
edges = []
nodes = []
for src_id, dst_id in new_edge_ids:
    edges.append(generate_edge(nodes_dict[src_id], nodes_dict[dst_id]))
    if src_id not in nodeid_set:
        nodeid_set.add(src_id)
        nodes.append(nodes_dict[src_id])
    if dst_id not in nodeid_set:
        nodeid_set.add(dst_id)
        nodes.append(nodes_dict[dst_id])

for node in nodes:
    if node.type == "opsgptkg_task":
        node.attributes["name"] += "_update"
        node.attributes["tmp"] += "_update"
        node.attributes["description"] += "_update"

for edge in edges:
    if edge.type == "opsgptkg_task_route_opsgptkg_task":
        edge.attributes["lat"] += "_update"
        

# 
teamid = "shanshi_test"
origin_nodes = [GNode(**n) for n in origin_nodes]
origin_edges = [GEdge(**e) for e in origin_edges]
ekg_construct_service.add_nodes(origin_nodes, teamid)
ekg_construct_service.add_edges(origin_edges, teamid)


# 
teamid = "shanshi_test_2"
ekg_construct_service.update_graph(origin_nodes, origin_edges, nodes, edges, teamid)



# do search
node = ekg_construct_service.get_node_by_id(nodeid="shanshi_opsgptkg_task_3", node_type="opsgptkg_task")
print(node)
graph = ekg_construct_service.get_graph_by_nodeid(nodeid="shanshi_opsgptkg_intent_0", node_type="opsgptkg_intent")
print(len(graph.nodes), len(graph.edges))


# search nodes by text
text = 'shanshi_test'
teamid = "shanshi_test"
nodes = ekg_construct_service.search_nodes_by_text(text, teamid=teamid)
print(len(nodes))

# search path by node and rootid
graph = ekg_construct_service.search_rootpath_by_nodeid(nodeid="shanshi_opsgptkg_analysis_2", node_type="opsgptkg_analysis", rootid="shanshi_opsgptkg_intent_0")
print(len(graph.nodes), len(graph.edges))