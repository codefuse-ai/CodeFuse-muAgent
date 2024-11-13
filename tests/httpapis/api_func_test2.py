# 导入必要的库
import requests
import json
from pydantic import BaseModel

# 定义 API 基本 URL
base_url = "http://localhost:3737"

import os, sys
from loguru import logger

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)
from muagent.schemas.common import GNode, GEdge
from muagent.schemas.db import GBConfig, TBConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.schemas.ekg import *


def generate_node(id, type):
    extra_attr = {"tmp": "hello"}
    if type == "opsgptkg_schedule":
        extra_attr["enable"] = False
        extra_attr["extra"] = {"test": "dsadsa"}
        
    if type == "opsgptkg_task":
        extra_attr["accesscriteria"] = "hello"
        extra_attr["executetype"] = "hello"
        extra_attr["tools"] = [
            {
                "id": '_'.join([id, "tool"]), 
                "type": "opsgptkg_tool",
                "name": "工具节点",
                "description": '_'.join([id, "工具节点"]),
            }
        ]
        extra_attr["agents"] = [
            {
                "id": '_'.join([id, "agent"]),  
                "type": "opsgptkg_agent",
                "name": "智能体节点",
                "description": '_'.join([id, "智能体节点"]),
            }
        ]

        
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

nodes_dict[f"ekg_team_default"] = generate_node("ekg_team_default", "opsgptkg_intent")
graph_path = [
    "ekg_team_default",
    "teamida_opsgptkg_intent_0", 
    "teamida_opsgptkg_intent_1",
    "teamida_opsgptkg_intent_2",
    "teamida_opsgptkg_schedule_0",
    "teamida_opsgptkg_task_0",
    "teamida_opsgptkg_task_1",
    "teamida_opsgptkg_analysis_0"
]

nodeid_set = set()
origin_edges = []
origin_nodes = []
for src_id, dst_id in zip(graph_path[:-1], graph_path[1:]):
    origin_edges.append(generate_edge(nodes_dict[src_id], nodes_dict[dst_id]))
    if src_id not in nodeid_set:
        nodeid_set.add(src_id)
        origin_nodes.append(nodes_dict[src_id])
    if dst_id not in nodeid_set:
        nodeid_set.add(dst_id)
        origin_nodes.append(nodes_dict[dst_id])


print("############ 测试 ~/ekg/graph/update 需求5-图谱的增/删/改 点/边 api ################")
request_data = {
    "features": {
        "query": {
            'originNodes': [],
            'originEdges': [],
            'nodes': [n.dict() for n in origin_nodes],
            'edges': [e.dict() for e in origin_edges],
            'teamid': "default",
            'rootNodeId': "ekg_team_default"
            
        }
    }
}
try:
    response = requests.post(
        f"{base_url}/ekg/graph/update",
        json=request_data  # 将请求数据作为 JSON 发送
    )

    # 打印响应结果
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print(f"Error: {response.status_code}, {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")


# ### 测试/ekg/node 端点 ####
# print('############ 节点查询 /ekg/node api ################')
# # 准备请求数据
# request_data = {
#     "features": {
#         "query": {
#             "nodeid": "teamida_opsgptkg_task_0",  # 查询的节点ID
#             "nodeType": "opsgptkg_task",  # 节点的类型
#             "serviceType": "gbase"
#         }
#     }
# }

# # 发起 GET 请求到 /ekg/node 端点
# response = requests.post(
#     f"{base_url}/ekg/node",
#     json=request_data  # 将请求数据作为 JSON 发送
# )

# # 打印响应结果
# if response.status_code == 200:
#     print("Response:", response.json())
# else:
#     print(f"Error: {response.status_code}, {response.text}")


# #### 测试 需求9-图谱：节点+关系查询 /ekg/graph api #####
# print('############ 测试 需求9-图谱：节点+关系查询 /ekg/graph api ################')

# request_data = {
#     "features": {
#         "query": {
#             "nodeid": "ekg_team_default",  # 查询的节点ID
#             "nodeType": "opsgptkg_intent",  # 节点的类型
#             "layer": "first"
#         }
#     }
# }

# # 发起 GET 请求到 /ekg/graph 端点
# response = requests.post(
#     f"{base_url}/ekg/graph",
#     json=request_data  # 将请求数据作为 JSON 发送
# )

# # 打印响应结果
# if response.status_code == 200:
#     print("Response:", response.json())
# else:
#     print(f"Error: {response.status_code}, {response.text}")


# request_data = {
#     "features": {
#         "query": {
#             "nodeid": "teamida_opsgptkg_schedule_0",  # 查询的节点ID
#             "nodeType": "opsgptkg_schedule",  # 节点的类型
#             "layer": "second"
#         }
#     }
# }

# # 发起 GET 请求到 /ekg/graph 端点
# response = requests.post(
#     f"{base_url}/ekg/graph",
#     json=request_data  # 将请求数据作为 JSON 发送
# )

# # 打印响应结果
# if response.status_code == 200:
#     print("Response:", response.json())
# else:
#     print(f"Error: {response.status_code}, {response.text}")


# #### 测试 需求10-节点搜索(含父子节点链路) /ekg/node/search api ##### done
# request_data = {
#     "features": {
#         "query": {
#             "text": "task_0",  
#             "nodeType": "opsgptkg_task",  # 节点的类型
#             "teamid": "default",
#             "topK": 5
#         }
#     }
# }

# try:
#     response = requests.post(
#         f"{base_url}/ekg/node/search",
#         json=request_data  # 将请求数据作为 JSON 发送
#     )

#     # 打印响应结果
#     if response.status_code == 200:
#         print("Response:", response.json())
#     else:
#         print(f"Error: {response.status_code}, {response.text}")
# except requests.exceptions.RequestException as e:
#     print(f"Request failed: {e}")


# ### 测试 ekg/graph/ancestor 查询根节点到当前节点的路径（顺序:父->子） api ##### done

# teamid = "default"
# request_data = {
#     "features": {
#         "query": {
#             "nodeid": "teamida_opsgptkg_task_0",  
#             "nodeType": "opsgptkg_task",  # 节点的类型
#             "rootid": f"ekg_team_{teamid}"  # 根节点id
#         }
#     }
# }

# try:
#     response = requests.post(
#         f"{base_url}/ekg/graph/ancestor",
#         json=request_data  # 将请求数据作为 JSON 发送
#     )

#     # 打印响应结果
#     if response.status_code == 200:
#         print("Response:", response.json())
#     else:
#         print(f"Error: {response.status_code}, {response.text}")
# except requests.exceptions.RequestException as e:
#     print(f"Request failed: {e}")

