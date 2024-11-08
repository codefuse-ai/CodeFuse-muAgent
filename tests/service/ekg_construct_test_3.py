######################################################
###################### 校验原子能力#####################
######################################################


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
from muagent.schemas.ekg import *




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
    index_name="teamida_test",
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
        extra_attr["extra"] = {"test": "dsadsa"}
        
    if type == "opsgptkg_task":
        extra_attr["accesscriteria"] = "hello"
        extra_attr["executetype"] = "hello"
        
    if type == "opsgptkg_analysis":
        extra_attr["accesscriteria"] = "hello"
        extra_attr["summaryswitch"] = False
        extra_attr['dsltemplate'] = "hello"             

    if "extra" in extra_attr:
        extra_attr.update(extra_attr.pop("extra", {}))

    node = GNode(**{
        "id": id, 
        "type": type,
        "attributes": {**{
            "name": id,
            "description": id, 
        }, **extra_attr}
    })
    schema = TYPE2SCHEMA.get(type,)
    node_data = schema(
        **{**{"id": node.id, "type": node.type}, **node.attributes}
    )
    node_data = {
        k:v
        for k, v in node_data.dict().items()
        if k not in ["type", "start_id", "end_id", "ID", "id", "extra"]
    }
    return GNode(**{
        "id": id, 
        "type": type,
        "attributes": {**node_data, **extra_attr}
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
        nodes_dict[f"teamida_{nodetype}_{i}"] = generate_node(f"teamida_{nodetype}_{i}", nodetype)

for nodetype in nodetypes:
    for i in range(8):
        nodes_dict[f"teamidb_{nodetype}_{i}"] = generate_node(f"teamidb_{nodetype}_{i}", nodetype)

for nodetype in nodetypes:
    for i in range(8):
        nodes_dict[f"teamidc_{nodetype}_{i}"] = generate_node(f"teamidc_{nodetype}_{i}", nodetype)



edge_ids = [
    ["teamida_opsgptkg_intent_0", "teamida_opsgptkg_intent_1"],
    ["teamida_opsgptkg_intent_1", "teamida_opsgptkg_intent_2"],
    ["teamida_opsgptkg_intent_2", "teamida_opsgptkg_schedule_0"],
    ["teamida_opsgptkg_intent_2", "teamida_opsgptkg_schedule_1"],
    ["teamida_opsgptkg_schedule_1", "teamida_opsgptkg_analysis_3"],
    ["teamida_opsgptkg_schedule_0", "teamida_opsgptkg_task_0"],
    ["teamida_opsgptkg_task_0", "teamida_opsgptkg_task_1"],
    ["teamida_opsgptkg_task_1", "teamida_opsgptkg_analysis_0"],
    ["teamida_opsgptkg_task_1", "teamida_opsgptkg_phenomenon_0"],
    ["teamida_opsgptkg_task_1", "teamida_opsgptkg_phenomenon_1"],
    ["teamida_opsgptkg_phenomenon_0", "teamida_opsgptkg_task_2"],
    ["teamida_opsgptkg_phenomenon_1", "teamida_opsgptkg_task_3"],
    ["teamida_opsgptkg_task_2", "teamida_opsgptkg_analysis_1"],
    ["teamida_opsgptkg_task_3", "teamida_opsgptkg_analysis_2"],
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


flags = []
### 测试原子能力
teamid = "teamida"

# 测试边的添加功能
## 1、先加节点
for node in origin_nodes:
    result = ekg_construct_service.add_nodes([node], teamid)

error_cnt = 0
for node in origin_nodes:
    try:
        result = ekg_construct_service.get_node_by_id(node.id, node.type)
    except:
        error_cnt+=1
flags.append(error_cnt==0)
print("节点添加功能正常" if error_cnt==0 else "节点添加功能异常")

## 2、添加边
for edge in origin_edges:
    result = ekg_construct_service.add_edges([edge], teamid)

neighbors_by_nodeid = {}
for edge in origin_edges:
    neighbors_by_nodeid.setdefault(edge.start_id, []).append(edge.end_id)
    
error_cnt = 0
for nodeid, neighbors in neighbors_by_nodeid.items():

    result = ekg_construct_service.gb.get_neighbor_nodes(
        {"id": nodeid}, nodes_dict[nodeid].type)
    if set(neighbors)!=set([n.id for n in result]):
        error_cnt += 1
flags.append(error_cnt==0)
print("边添加功能正常" if error_cnt==0 else "边添加功能异常")


## 3、修改节点
for node in origin_nodes:
    node.attributes["name"] = "muagenttest"
    result = ekg_construct_service.update_nodes([node], teamid)

error_cnt = 0
for node in origin_nodes:
    try:
        result = ekg_construct_service.get_node_by_id(node.id, node.type)
        error_cnt += result.attributes["name"] != "muagenttest"
    except:
        error_cnt+=1
flags.append(error_cnt==0)
print("节点修改功能正常" if error_cnt==0 else "节点修改功能异常")

## 4、路径查询
connections = {}
for edge in origin_edges:
    connections.setdefault(edge.start_id, []).append(edge.end_id)

visited = set()
rootid_can_arrive_nodeids = []
paths = []
def _dfs(node, current_path):
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
_dfs("teamida_opsgptkg_intent_0", [])
graph = ekg_construct_service.get_graph_by_nodeid("teamida_opsgptkg_intent_0", "opsgptkg_intent", 29)
set([', '.join(i) for i in graph.paths])==set([', '.join(i) for i in paths])
flags.append(set([', '.join(i) for i in graph.paths])==set([', '.join(i) for i in paths]))
print("路径查询功能正常" if set([', '.join(i) for i in graph.paths])==set([', '.join(i) for i in paths]) else "路径查询功能异常")




## 5、测试边的删除功能
for edge in origin_edges:
    result = ekg_construct_service.delete_edges([edge], teamid)
    
neighbors_by_nodeid = {}
for edge in origin_edges:
    neighbors_by_nodeid.setdefault(edge.start_id, []).append(edge.end_id)
    
error_cnt = 0
for nodeid, neighbors in neighbors_by_nodeid.items():

    result = ekg_construct_service.gb.get_neighbor_nodes(
        {"id": nodeid}, nodes_dict[nodeid].type)
    if set(neighbors)==set([n.id for n in result]):
        error_cnt += 1
flags.append(error_cnt==0)
print("边删除功能正常" if error_cnt==0 else "边删除功能异常")

## 6、测试节点的删除功能
for node in origin_nodes:
    result = ekg_construct_service.delete_nodes([node], teamid)
    
error_cnt = 0
for node in origin_nodes:
    try:
        result = ekg_construct_service.get_node_by_id(node.id, node.type)
    except:
        error_cnt += 1
flags.append(error_cnt==len(origin_nodes))
print("节点删除功能正常" if error_cnt==len(origin_nodes) else "节点删除功能异常")



if sum(flags) != len(flags):
    sys.exit(f"存在功能异常, {flags}")


##############################
###### 测试交叉团队的增删改 #####
##############################

edge_ids_by_teamid = {
    "teamida": [
        ["teamida_opsgptkg_intent_0", "teamida_opsgptkg_intent_1"],
        ["teamida_opsgptkg_intent_1", "teamida_opsgptkg_intent_2"],
        ["teamida_opsgptkg_intent_2", "teamida_opsgptkg_schedule_0"],
        ["teamida_opsgptkg_intent_2", "teamida_opsgptkg_schedule_1"],
        ["teamida_opsgptkg_schedule_1", "teamida_opsgptkg_analysis_3"],
        ["teamida_opsgptkg_schedule_0", "teamida_opsgptkg_task_0"],
        ["teamida_opsgptkg_task_0", "teamida_opsgptkg_task_1"],
        ["teamida_opsgptkg_task_1", "teamida_opsgptkg_analysis_0"],
        ["teamida_opsgptkg_task_1", "teamida_opsgptkg_phenomenon_0"],
        ["teamida_opsgptkg_task_1", "teamida_opsgptkg_phenomenon_1"],
        ["teamida_opsgptkg_phenomenon_0", "teamida_opsgptkg_task_2"],
        ["teamida_opsgptkg_phenomenon_1", "teamida_opsgptkg_task_3"],
        ["teamida_opsgptkg_task_2", "teamida_opsgptkg_analysis_1"],
        ["teamida_opsgptkg_task_3", "teamida_opsgptkg_analysis_2"],
    ],
    "teamidb": [
        ["teamidb_opsgptkg_intent_0", "teamidb_opsgptkg_intent_1"],
        ["teamidb_opsgptkg_intent_1", "teamidb_opsgptkg_intent_2"],
        ["teamidb_opsgptkg_intent_2", "teamidb_opsgptkg_schedule_0"],
        ["teamidb_opsgptkg_intent_2", "teamidb_opsgptkg_schedule_1"],
        ["teamidb_opsgptkg_schedule_1", "teamidb_opsgptkg_analysis_3"],
        ["teamidb_opsgptkg_schedule_0", "teamidb_opsgptkg_task_0"],
        ["teamidb_opsgptkg_task_0", "teamidb_opsgptkg_task_1"],
        ["teamidb_opsgptkg_task_1", "teamidb_opsgptkg_analysis_0"],
        ["teamidb_opsgptkg_task_1", "teamidb_opsgptkg_phenomenon_0"],
        ["teamidb_opsgptkg_task_1", "teamidb_opsgptkg_phenomenon_1"],
        ["teamidb_opsgptkg_phenomenon_0", "teamidb_opsgptkg_task_2"],
        ["teamidb_opsgptkg_phenomenon_1", "teamidb_opsgptkg_task_3"],
        ["teamidb_opsgptkg_task_2", "teamidb_opsgptkg_analysis_1"],
        ["teamidb_opsgptkg_task_3", "teamidb_opsgptkg_analysis_2"],
    ],
    "teamidc": [
        ["teamidc_opsgptkg_intent_0", "teamidc_opsgptkg_intent_1"],
        ["teamidc_opsgptkg_intent_1", "teamidc_opsgptkg_intent_2"],
        ["teamidc_opsgptkg_intent_2", "teamidc_opsgptkg_schedule_0"],
        ["teamidc_opsgptkg_intent_2", "teamidc_opsgptkg_schedule_1"],
        ["teamidc_opsgptkg_schedule_1", "teamidc_opsgptkg_analysis_3"],
        ["teamidc_opsgptkg_schedule_0", "teamidc_opsgptkg_task_0"],
        ["teamidc_opsgptkg_task_0", "teamidc_opsgptkg_task_1"],
        ["teamidc_opsgptkg_task_1", "teamidc_opsgptkg_analysis_0"],
        ["teamidc_opsgptkg_task_1", "teamidc_opsgptkg_phenomenon_0"],
        ["teamidc_opsgptkg_task_1", "teamidc_opsgptkg_phenomenon_1"],
        ["teamidc_opsgptkg_phenomenon_0", "teamidc_opsgptkg_task_2"],
        ["teamidc_opsgptkg_phenomenon_1", "teamidc_opsgptkg_task_3"],
        ["teamidc_opsgptkg_task_2", "teamidc_opsgptkg_analysis_1"],
        ["teamidc_opsgptkg_task_3", "teamidc_opsgptkg_analysis_2"],
    ],
    "mixer": [
        ["teamida_opsgptkg_intent_2", "teamidb_opsgptkg_schedule_0"],
        ["teamida_opsgptkg_intent_2", "teamidc_opsgptkg_schedule_0"],
        ["teamidb_opsgptkg_intent_2", "teamidc_opsgptkg_schedule_0"],
        ["teamidb_opsgptkg_schedule_1", "teamidc_opsgptkg_task_0"],
        ["teamidb_opsgptkg_schedule_0", "teamidc_opsgptkg_task_1"],
    ],
}

neighbors_by_nodeid = {}
for teamid, origin_edges in edge_ids_by_teamid.items():
    for edge in origin_edges:
        neighbors_by_nodeid.setdefault(edge[0], []).append(edge[1])

origin_edges = []
origin_nodes = []
for teamid, edge_ids in edge_ids_by_teamid.items():
    for src_id, dst_id in edge_ids:
        origin_edges.append(generate_edge(nodes_dict[src_id], nodes_dict[dst_id]))
        if src_id not in nodeid_set:
            nodeid_set.add(src_id)
            origin_nodes.append(nodes_dict[src_id])
        if dst_id not in nodeid_set:
            nodeid_set.add(dst_id)
            origin_nodes.append(nodes_dict[dst_id])


flags = []
# 测试边的添加功能
## 1、先加节点
for node in origin_nodes:
    teamid = node.id.split("_")[0]
    result = ekg_construct_service.add_nodes([node], teamid)

error_cnt = 0
for node in origin_nodes:
    try:
        result = ekg_construct_service.get_node_by_id(node.id, node.type)
    except:
        error_cnt+=1
flags.append(error_cnt==0)
print("节点添加功能正常" if error_cnt==0 else "节点添加功能异常")

## 2、添加边
for edge in origin_edges:
    teamid = edge.start_id.split("_")[0]
    result = ekg_construct_service.add_edges([edge], teamid)

neighbors_by_nodeid = {}
for edge in origin_edges:
    neighbors_by_nodeid.setdefault(edge.start_id, []).append(edge.end_id)
    
error_cnt = 0
for nodeid, neighbors in neighbors_by_nodeid.items():

    result = ekg_construct_service.gb.get_neighbor_nodes(
        {"id": nodeid}, nodes_dict[nodeid].type)
    if set(neighbors)!=set([n.id for n in result]):
        error_cnt += 1
flags.append(error_cnt==0)
print("边添加功能正常" if error_cnt==0 else "边添加功能异常")




delete_edges_by_teamid = {
    "teamidc": ["teamidb_opsgptkg_schedule_0", "teamidc_opsgptkg_task_1"],
}
# delete edge: teamidb_opsgptkg_schedule_0, teamidc_opsgptkg_task_1
delete_edgeid = ["teamidb_opsgptkg_schedule_0", "teamidc_opsgptkg_task_1"]
nodeid = "teamidb_opsgptkg_schedule_0"
for edge in origin_edges:
    do_delete = False
    if delete_edgeid[0]==edge.start_id and delete_edgeid[1] == edge.end_id:
        do_delete = True
        break

result = ekg_construct_service.delete_edges([edge], teamid="teamida")
# check
result = ekg_construct_service.gb.get_neighbor_nodes(
        {"id": nodeid}, nodes_dict[nodeid].type)
print("跨团队删除边功能正常" if set(neighbors_by_nodeid[nodeid])!=set([n.id for n in result]) else "跨团队删除边功能正常")
# add back to test other functions
ekg_construct_service.add_edges([edge], teamid="teamida")


delete_nodes_by_teamid = {
    "teamida": ["teamida_opsgptkg_intent_2", "teamida_opsgptkg_analysis_3"],
    "teamidb": ["teamidb_opsgptkg_schedule_1"],
    "teamidc": ["teamidc_opsgptkg_intent_1", "teamidc_opsgptkg_schedule_0"],
}

# delete teamida_opsgptkg_intent_2
delete_edgeids = [
    ["teamida_opsgptkg_intent_1", "teamida_opsgptkg_intent_2"],
    ["teamida_opsgptkg_intent_2", "teamida_opsgptkg_schedule_0"],
    ["teamida_opsgptkg_intent_2", "teamida_opsgptkg_schedule_1"]
]
delete_nodeid = "teamida_opsgptkg_intent_2"
delete_edges = []
for edge in origin_edges:
    do_delete = False
    for delete_edgeid in delete_edgeids:
        if delete_edgeid[0]==edge.start_id and delete_edgeid[1] == edge.end_id:
            delete_edges.append(edge)
            break

result = ekg_construct_service.delete_edges(delete_edges, teamid="teamida")
result = ekg_construct_service.delete_nodes_v2([nodes_dict[delete_nodeid]], teamid="teamida")
try:
    result = ekg_construct_service.get_node_by_id(delete_nodeid, nodes_dict[delete_nodeid].type)
    print("删除节点逻辑正常")
except Exception as e:
    print(e)
    print("删除节点逻辑异常")

result = ekg_construct_service.add_nodes([nodes_dict[delete_nodeid]], teamid="teamida")
result = ekg_construct_service.add_edges(delete_edges, teamid="teamida")





# delete teamida_opsgptkg_analysis_3
delete_edgeids = [
    ["teamida_opsgptkg_schedule_1", "teamida_opsgptkg_analysis_3"],
]
delete_nodeid = "teamida_opsgptkg_analysis_3"
delete_edges = []
for edge in origin_edges:
    do_delete = False
    for delete_edgeid in delete_edgeids:
        if delete_edgeid[0]==edge.start_id and delete_edgeid[1] == edge.end_id:
            delete_edges.append(edge)
            break

result = ekg_construct_service.delete_edges(delete_edges, teamid="teamida")
result = ekg_construct_service.delete_nodes_v2([nodes_dict[delete_nodeid]], teamid="teamida")
try:
    result = ekg_construct_service.get_node_by_id(delete_nodeid, nodes_dict[delete_nodeid].type)
    print("删除节点逻辑异常")
except Exception as e:
    print(e)
    print("删除节点逻辑正常")

result = ekg_construct_service.add_nodes([nodes_dict[delete_nodeid]], teamid="teamida")
result = ekg_construct_service.add_edges(delete_edges, teamid="teamida")


# delete node: teamidb_opsgptkg_schedule_1
delete_edgeids = [
    ["teamidb_opsgptkg_schedule_1", "teamidb_opsgptkg_analysis_3"],
    ["teamidb_opsgptkg_intent_2", "teamidb_opsgptkg_schedule_1"],
]
delete_nodeid = "teamidb_opsgptkg_schedule_1"
teamid = "teamidb"
delete_edges = []
for edge in origin_edges:
    do_delete = False
    for delete_edgeid in delete_edgeids:
        if delete_edgeid[0]==edge.start_id and delete_edgeid[1] == edge.end_id:
            delete_edges.append(edge)
            break

result = ekg_construct_service.delete_edges(delete_edges, teamid=teamid)
result = ekg_construct_service.delete_nodes_v2([nodes_dict[delete_nodeid]], teamid=teamid)
try:
    result = ekg_construct_service.get_node_by_id(delete_nodeid, nodes_dict[delete_nodeid].type)
    print("删除节点逻辑正常")
except Exception as e:
    print(e)
    print("删除节点逻辑异常")

result = ekg_construct_service.add_nodes([nodes_dict[delete_nodeid]], teamid=teamid)
result = ekg_construct_service.add_edges(delete_edges, teamid=teamid)


# delete node: teamidc_opsgptkg_intent_1
delete_edgeids = [
        ["teamidc_opsgptkg_intent_0", "teamidc_opsgptkg_intent_1"],
        ["teamidc_opsgptkg_intent_1", "teamidc_opsgptkg_intent_2"],
]
delete_nodeid = "teamidc_opsgptkg_intent_1"
teamid = "teamidc"
delete_edges = []
for edge in origin_edges:
    do_delete = False
    for delete_edgeid in delete_edgeids:
        if delete_edgeid[0]==edge.start_id and delete_edgeid[1] == edge.end_id:
            delete_edges.append(edge)
            break

result = ekg_construct_service.delete_edges(delete_edges, teamid=teamid)
result = ekg_construct_service.delete_nodes_v2([nodes_dict[delete_nodeid]], teamid=teamid)
try:
    result = ekg_construct_service.get_node_by_id(delete_nodeid, nodes_dict[delete_nodeid].type)
    print("删除节点逻辑异常")
except Exception as e:
    print(e)
    print("删除节点逻辑正常")

result = ekg_construct_service.add_nodes([nodes_dict[delete_nodeid]], teamid=teamid)
result = ekg_construct_service.add_edges(delete_edges, teamid=teamid)



# delete node: teamidc_opsgptkg_schedule_0
delete_edgeids = [
    ["teamidc_opsgptkg_schedule_0", "teamidc_opsgptkg_task_0"],
    ["teamidc_opsgptkg_intent_2", "teamidc_opsgptkg_schedule_0"],
]
delete_nodeid = "teamidc_opsgptkg_schedule_0"
teamid = "teamidc"
delete_edges = []
for edge in origin_edges:
    do_delete = False
    for delete_edgeid in delete_edgeids:
        if delete_edgeid[0]==edge.start_id and delete_edgeid[1] == edge.end_id:
            delete_edges.append(edge)
            break

result = ekg_construct_service.delete_edges(delete_edges, teamid=teamid)
result = ekg_construct_service.delete_nodes_v2([nodes_dict[delete_nodeid]], teamid=teamid)
try:
    result = ekg_construct_service.get_node_by_id(delete_nodeid, nodes_dict[delete_nodeid].type)
    print("删除节点逻辑正常")
except Exception as e:
    print(e)
    print("删除节点逻辑异常")

result = ekg_construct_service.add_nodes([nodes_dict[delete_nodeid]], teamid=teamid)
result = ekg_construct_service.add_edges(delete_edges, teamid=teamid)


# 保证数据全部被删除
## 5、测试边的删除功能
for edge in origin_edges:
    teamid = edge.start_id.split("_")[0]
    result = ekg_construct_service.delete_edges([edge], teamid)
    
neighbors_by_nodeid = {}
for edge in origin_edges:
    neighbors_by_nodeid.setdefault(edge.start_id, []).append(edge.end_id)
    
error_cnt = 0
for nodeid, neighbors in neighbors_by_nodeid.items():

    result = ekg_construct_service.gb.get_neighbor_nodes(
        {"id": nodeid}, nodes_dict[nodeid].type)
    if set(neighbors)==set([n.id for n in result]):
        error_cnt += 1
flags.append(error_cnt==0)
print("边删除功能正常" if error_cnt==0 else "边删除功能异常")

## 6、测试节点的删除功能
for node in origin_nodes:
    teamid = node.id.split("_")[0]
    result = ekg_construct_service.delete_nodes([node], teamid)
    
error_cnt = 0
for node in origin_nodes:
    try:
        result = ekg_construct_service.get_node_by_id(node.id, node.type)
    except:
        error_cnt += 1
flags.append(error_cnt==len(origin_nodes))
print("节点删除功能正常" if error_cnt==len(origin_nodes) else "节点删除功能异常")