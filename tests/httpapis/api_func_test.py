# 导入必要的库
import requests
import json
from pydantic import BaseModel

#from muagent.schemas.apis.ekg_api_schema import *

# 定义 API 基本 URL
base_url = "http://localhost:3737"

# 测试获取嵌入模型参数
response = requests.get(f"{base_url}/embeddings/params")
print(response.json())

#### 测试 ~/ekg/graph/update 需求5-增/删/改 点/边 api ##### 

teamid = "default"

request_data = {
    "features": {
        "query": {
            'originNodes': [
                
            ],
            'originEdges': [
                
            ],
            'nodes': [
                {
                    "id": "ekg_team_yunjiu_test",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "开始",
                        "description": "团队起始节点",
                        "ID": 4.617441492992E12,
                        "isTeamRoot": True,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 1729587508
                    }
                }
            ],
            'edges': [
                
            ],
            'teamid': "yunjiu_test",
            'rootNodeId': "ekg_team_yunjiu_test"
            
        }
    }
}

request_data_update = {
    "features": {
        "query": {
            'originNodes': [
                {
                    "id": "ekg_team_yunjiu_test",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "开始",
                        "description": "团队起始节点(更新)",
                        "ID": 4.617441492992E12,
                        "isTeamRoot": True,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 1729587508
                    }
                }
            ],
            'originEdges': [
                
            ],
            'nodes': [
                {
                    "id": "ekg_team_yunjiu_test",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "开始",
                        "description": "团队起始节点",
                        "ID": 4.617441492992E12,
                        "isTeamRoot": True,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 1729587508
                    }
                }
            ],
            'edges': [
                
            ],
            'teamid': "yunjiu_test",
            'rootNodeId': "ekg_team_yunjiu_test"
            
        }
    }
}

request_data2 = {
    "features": {
        "query": {
            'originNodes': [
                {
                    "id": "ekg_team_yunjiu_test",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "开始",
                        "description": "团队起始节点",
                        "ID": 4.617441492992E12,
                        "isTeamRoot": True,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 1729587533
                    }
                }
                
            ],
            'originEdges': [
                
            ],
            'nodes': [
                {
                    "id": "ekg_team_yunjiu_test",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "开始",
                        "description": "团队起始节点",
                        "ID": 4.617441492992E12,
                        "isTeamRoot": True,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 1729587508
                    }
                },
                {
                    "id": "DyI9sEWjEQ1Cr0AdXi2GhDic8lqxHGR8",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "场景意图",
                        "description": "场景意图",
                        "ID": 6.617441492992E12,
                        "isTeamRoot": False,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 2729587508
                    }
                    
                }
            ],
            'edges': [
                {
                    "start_id": "ekg_team_yunjiu_test",
                    "end_id": "DyI9sEWjEQ1Cr0AdXi2GhDic8lqxHGR8",
                    # "type": "opsgptkg_intent_route_opsgptkg_schedule",
                    "attributes": {
                        "sourceHandle": "0",
                        "targetHandle": "2"
                    }
                }
            ],
            'teamid': "yunjiu_test",
            'rootNodeId': "ekg_team_yunjiu_test"
            
        }
    }
}


# 删除一个节点
request_data3 = {
    "features": {
        "query": {
            'originNodes': [
                {
                    "id": "ekg_team_yunjiu_test",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "开始",
                        "description": "团队起始节点",
                        "ID": 4.617441492992E12,
                        "isTeamRoot": True,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 1729587508
                    }
                },
                {
                    "id": "DyI9sEWjEQ1Cr0AdXi2GhDic8lqxHGR8",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "场景意图",
                        "description": "场景意图",
                        "ID": 6.617441492992E12,
                        "isTeamRoot": False,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 2729587508
                    }
                    
                }
                
            ],
            'originEdges': [
                {
                    "start_id": "ekg_team_yunjiu_test",
                    "end_id": "DyI9sEWjEQ1Cr0AdXi2GhDic8lqxHGR8",
                    # "type": "opsgptkg_intent_route_opsgptkg_schedule",
                    "attributes": {
                        "sourceHandle": "0",
                        "targetHandle": "2"
                    }
                }
                
            ],
            'nodes': [
                {
                    "id": "ekg_team_yunjiu_test",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "开始",
                        "description": "团队起始节点",
                        "ID": 4.617441492992E12,
                        "isTeamRoot": True,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 1729587533
                    }
                }
            ],
            'edges': [
                
            ],
            'teamid': "yunjiu_test",
            'rootNodeId': "ekg_team_yunjiu_test"
            
        }
    }
}

###################### 测试 Error: rootid not in this graph

request_data_a = {
    "features": {
        "query": {
            "originNodes": [
                {
                    "id": "ekg_team_hhh",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "ID": 9522373689344,
                        "name": "开始",
                        "description": "团队起始节点",
                        "gdb_timestamp": 1729676623,
                        "teamids": "hhh",
                        "isTeamRoot": True
                    }
                }
            ],
            "nodes": [
                {
                    "id": "ekg_team_hhh",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "ID": 9522373689344,
                        "name": "开始",
                        "description": "团队起始节点",
                        "gdb_timestamp": 1729676623,
                        "teamids": "hhh",
                        "isTeamRoot": True
                    }
                },
                {
                    "id": "X3wm9oNqxvlSAg5WD667ouI",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "场景意图",
                        "description": ""
                    }
                }
            ],
            "rootNodeId": "ekg_default_hhh",
            "originEdges": [
                
            ],
            "teamid": "hhh",
            "edges": [
                {
                    "start_id": "ekg_team_hhh",
                    "end_id": "X3wm9oNqxvlSAg5WD667ouI",
                    "attributes": {
                        "sourceHandle": "2",
                        "targetHandle": "1"
                    }
                }
            ]
        }
    }
}

request_data_a1 = {
    "features": {
        "query": {
            "originNodes": [
                {
                    "id": "ekg_team_default",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "ID": 4617441492992,
                        "name": "开始",
                        "description": "团队起始节点",
                        "gdb_timestamp": 1729652643,
                        "teamids": "default",
                        "isTeamRoot": True
                    }
                },
                {
                    "id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "ID": 390950363136,
                        "name": "场景意图",
                        "description": "",
                        "gdb_timestamp": 1729652633,
                        "teamids": "default"
                    }
                },
                {
                    "id": "h0JC4iCY2NGVwsChj7jhHszZnJuPE07b",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "ID": 5958513614848,
                        "name": "场景意图",
                        "description": "",
                        "gdb_timestamp": 1729663172,
                        "teamids": "default"
                    }
                },
                {
                    "id": "vCPMMrxprW9D6zcHofYAs2JP2YGyBXRk",
                    "type": "opsgptkg_schedule",
                    "attributes": {
                        "ID": 1588980703232,
                        "name": "操作计划",
                        "description": "操作计划",
                        "gdb_timestamp": 1729653290,
                        "teamids": "default",
                        "enable": True,
                        "cnode_nums": 1
                    }
                }
            ],
            "nodes": [
                {
                    "id": "ekg_team_default",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "ID": 4617441492992,
                        "name": "开始",
                        "description": "团队起始节点",
                        "gdb_timestamp": 1729652643,
                        "teamids": "default",
                        "isTeamRoot": True
                    }
                },
                {
                    "id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "ID": 390950363136,
                        "name": "场景意图",
                        "description": "",
                        "gdb_timestamp": 1729652633,
                        "teamids": "default"
                    }
                },
                {
                    "id": "vCPMMrxprW9D6zcHofYAs2JP2YGyBXRk",
                    "type": "opsgptkg_schedule",
                    "attributes": {
                        "ID": 1588980703232,
                        "name": "操作计划",
                        "description": "操作计划",
                        "gdb_timestamp": 1729653290,
                        "teamids": "default",
                        "enable": True,
                        "cnode_nums": 1
                    }
                }
            ],
            "rootNodeId": "ekg_team_default",
            "originEdges": [
                {
                    "start_id": "ekg_team_default",
                    "end_id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
                    "attributes": {
                        "timestamp": 1,
                        "gdb_timestamp": 1729652633,
                        "sourceHandle": "0",
                        "targetHandle": "2"
                    }
                },
                {
                    "start_id": "ekg_team_default",
                    "end_id": "h0JC4iCY2NGVwsChj7jhHszZnJuPE07b",
                    "attributes": {
                        "timestamp": 1,
                        "gdb_timestamp": 1729663172,
                        "sourceHandle": "2",
                        "targetHandle": "3"
                    }
                },
                {
                    "start_id": "ekg_team_default",
                    "end_id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
                    "attributes": {
                        "timestamp": 1,
                        "gdb_timestamp": 1729652633,
                        "sourceHandle": "0",
                        "targetHandle": "2"
                    }
                },
                {
                    "start_id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
                    "end_id": "vCPMMrxprW9D6zcHofYAs2JP2YGyBXRk",
                    "attributes": {
                        "timestamp": 1,
                        "gdb_timestamp": 1729653290,
                        "sourceHandle": "0",
                        "targetHandle": "2"
                    }
                }
            ],
            "teamid": "default",
            "edges": [
                {
                    "start_id": "ekg_team_default",
                    "end_id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
                    "attributes": {
                        "timestamp": 1,
                        "gdb_timestamp": 1729652633,
                        "sourceHandle": "0",
                        "targetHandle": "2"
                    }
                },
                {
                    "start_id": "ekg_team_default",
                    "end_id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
                    "attributes": {
                        "timestamp": 1,
                        "gdb_timestamp": 1729652633,
                        "sourceHandle": "0",
                        "targetHandle": "2"
                    }
                },
                {
                    "start_id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
                    "end_id": "vCPMMrxprW9D6zcHofYAs2JP2YGyBXRk",
                    "attributes": {
                        "timestamp": 1,
                        "gdb_timestamp": 1729653290,
                        "sourceHandle": "0",
                        "targetHandle": "2"
                    }
                }
            ]
        }
    }
}

if True: # True or False
    print("############ 测试 ~/ekg/graph/update 需求5-图谱的增/删/改 点/边 api ################")
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


# ### 测试/ekg/node/search ####

# # 准备请求数据
# request_data = {
#     "features": {
#         "query": {
#             "nodeid": "",  # 查询的节点ID
#             "nodeType": "",  # 节点的类型
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


#### 测试 需求9-图谱：节点+关系查询 /ekg/graph api #####
print('############ 测试 需求9-图谱：节点+关系查询 /ekg/graph api ################')

request_data = {
    "features": {
        "query": {
            "nodeid": "ekg_team_yunjiu_test",  # 查询的节点ID
            "nodeType": "opsgptkg_intent",  # 节点的类型
            # "serviceType": "gbase",
            "layer": "first"
        }
    }
}

# request_data = {
#     "features": {
#         "query": {
#             "nodeid": "36t2e1qURPB714rRfw9jAslEs39AsSlt",  # 查询的节点ID
#             "nodeType": "opsgptkg_schedule",  # 节点的类型
#             # "serviceType": "gbase",
#             "layer": "second"
#         }
#     }
# }

if True: # True or False
    # 发起 GET 请求到 /ekg/graph 端点
    response = requests.post(
        f"{base_url}/ekg/graph",
        json=request_data  # 将请求数据作为 JSON 发送
    )

    # 打印响应结果
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print(f"Error: {response.status_code}, {response.text}")


# #### 测试 需求10-节点搜索(含父子节点链路) /ekg/node/search api ##### done

request_data = {
    "features": {
        "query": {
            "text": "结束",  
            "nodeType": "opsgptkg_intent",  # 节点的类型
            "teamid": "yunjiu_test",
            "topK": 5
        }
    }
}

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


### 测试 ekg/graph/ancestor 查询根节点到当前节点的路径（顺序:父->子） api ##### done

teamid = "yunjiu_test"

request_data = {
    "features": {
        "query": {
            "nodeid": "yunjiu_3",  
            "nodeType": "opsgptkg_intent",  # 节点的类型
            "rootid": f"ekg_team_{teamid}"  # 根节点id
        }
    }
}

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

