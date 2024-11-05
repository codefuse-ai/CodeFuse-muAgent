# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# 导入必要的库
import requests
import json
import time
#from muagent.schemas.apis.ekg_api_schema import *

# 定义 API 基本 URL
base_url = "http://localhost:3737"




#配置依赖
import sys
sys.path.append("/home/user/muagent/muagent/service/ekg_reasoning")  #依赖地址
from src.utils.normalize import hash_id




# #谁是卧底 定制
# request = \
# {
#   "features": {
#     "query": {
#       "observation": "{\"content\":\"开始游戏\"}",
#       "scene": "UNDERCOVER",
#       "sessionId": "41faeed1_39ba_414b_dcad_f22e7b32caae00x"
#     }
#   }
# }


# sessionId = '349579720439752097847_26'
# #谁是卧底 通用
# request = \
# {
#   "features": {
#     "query": {
#       "scene": "NEXA",
#       "startRootNodeId": '4bf08f20487bfb3d34048ddf455bf5dd', #hash_id('剧本杀' ),
#       "intentionRule": ["nlp"],
#       "intentionData": "执行谁是卧底进程",
#       "observation": "{\"content\":\"开始游戏\"}",
#       "sessionId": sessionId
#     }
#   }
# }



    
    
    
# # 测试获取嵌入模型参数
# response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
# print(response.json())
# print(response)


# #====== step 1 result ===
# request = \
# {'features': {'query': {'currentNodeId': '756c3707f53991fb2118ab5d92d28539',
#    'type': 'onlyTool',
#    'observation': '{"toolResponse":"\\n\\n| 座位 | 玩家 |\\n|---|---|\\n| 1 | **王鹏** |\\n| 2 | **人类玩家** |\\n| 3 | **李静** |\\n| 4 | **张伟** |","toolKey":"undercover.dispatch_position","toolParam":"分配座位"}',
#    'scene': 'UNDERCOVER',
#    'sessionId': sessionId}}}

# # 测试获取嵌入模型参数
# response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
# print(response.json())
# print(response)



# #====== step 2  result ===
# request = \
# {
#   "features": {
#     "query": {
#       "currentNodeId": "7703bd47cc2dbdebb0a5151b83c26a11",
#       "type": "onlyTool",
#       "observation": "{\"toolResponse\":\"[{\\\"单词\\\":\\\"虾\\\",\\\"agent_name\\\":\\\"agent_人类玩家\\\",\\\"agent_description\\\":\\\"平民_1\\\",\\\"player_name\\\":\\\"人类玩家\\\"},{\\\"单词\\\":\\\"鱼\\\",\\\"agent_name\\\":\\\"agent_李静\\\",\\\"agent_description\\\":\\\"卧底_1\\\",\\\"player_name\\\":\\\"李静\\\"},{\\\"单词\\\":\\\"虾\\\",\\\"agent_name\\\":\\\"agent_张伟\\\",\\\"agent_description\\\":\\\"平民_3\\\",\\\"player_name\\\":\\\"张伟\\\"},{\\\"单词\\\":\\\"虾\\\",\\\"agent_name\\\":\\\"agent_王鹏\\\",\\\"agent_description\\\":\\\"平民_2\\\",\\\"player_name\\\":\\\"王鹏\\\"}]\",\"toolKey\":\"undercover.dispatch_keyword\",\"toolParam\":\"角色分配和单词分配\"}",
#       "scene": "UNDERCOVER",
#       "sessionId": sessionId
#     }
#   }
# }
# # 测试获取嵌入模型参数
# response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
# print(response.json())
# print(response)


# #===== step 3 result ====






# ####### long test######
# #######################
# #######################





goc_test_sessionId = "TS_GOC_103346456601_0709001_sswd_081"


#debugmode 调试，谁是卧底初次输入
params_string = {'observation': {'content': '一起来玩谁是卧底'},
    'sessionId': goc_test_sessionId,
    'scene': 'UNDERCOVER'}


# 测试获取嵌入模型参数
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


time.sleep(1)


#step 1  位置选择tool 返回

params_string = {'observation': {'toolResponse': '{"座位分配结果": [{"player_name": "player_1", "seat_number": 1}, {"player_name": "player_2", "seat_number": 2}, {"player_name": "player_3", "seat_number": 3}, {"player_name": "player_4", "seat_number": 4}, {"player_name": "player_5", "seat_number": 5}, {"player_name": "player_6", "seat_number": 6}, {"player_name": "李四", "seat_number": 7}]}'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/分配座位'),
  'sessionId': goc_test_sessionId,
  'type': 'onlyTool',
  'scene': 'UNDERCOVER'}

params_string['observation']['toolResponse'] = json.dumps( {
"座位分配结果": [
    {"player_name": "player_1", "seat_number": 1},
    {"player_name": "李四(人类玩家)", "seat_number": 2},
    {"player_name": "player_2", "seat_number": 3},
    {"player_name": "player_3", "seat_number": 4}
]
}, ensure_ascii=False)

request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)

time.sleep(1)


#step 2  角色分配和单词分配

params_string = {'observation': {'toolResponse': '{"座位分配结果": [{"player_name": "player_1", "seat_number": 1}, {"player_name": "player_2", "seat_number": 2}, {"player_name": "player_3", "seat_number": 3}, {"player_name": "player_4", "seat_number": 4}, {"player_name": "player_5", "seat_number": 5}, {"player_name": "player_6", "seat_number": 6}, {"player_name": "李四", "seat_number": 7}]}'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/角色分配和单词分配'),
  'sessionId': goc_test_sessionId,
  'type': 'onlyTool',
  'scene': 'UNDERCOVER'}

params_string['observation']['toolResponse'] = json.dumps( [
{
    "player_name": "player_1",
    "seat_number": 1,
    "agent_name": "agent_2",
    "agent_description": "平民_1",
    "单词": "汽车"
},
{
    "player_name": "李四(人类玩家)",
    "seat_number": 2,
    "agent_name": "人类agent_a",
    "agent_description": "平民_1",
    "单词": "汽车"
},
{
    "player_name": "player_2",
    "seat_number": 3,
    "agent_name": "agent_3",
    "agent_description": "平民_2",
    "单词": "汽车"
},
{
    "player_name": "player_3",
    "seat_number": 4,
    "agent_name": "agent_1",
    "agent_description": "卧底_1",
    "单词": "摩托车"
}
], ensure_ascii=False)

request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


time.sleep(1)
'''
{'intentionRecognitionSituation': 'None', 'sessionId': 'TS_GOC_103346456601_0709001_lrs_105', 'type': 'onlyTool', 'summary': None, 'toolPlan': [{'toolDescription': 'agent_2', 'currentNodeId': '剧本杀/谁是卧底/智能交互/开始新一轮的讨论', 'memory': '[{"role_type": "user", "role_name": "firstUserInput", "role_content": "{\\"content\\": \\"一起来玩谁是卧底\\"}"}, {"role_type": "observation", "role_name": "function_caller", "role_content": "{\\"座位分配结果\\": [{\\"player_name\\": \\"player_1\\", \\"seat_number\\": 1}, {\\"player_name\\": \\"李四(人类玩家)\\", \\"seat_number\\": 2}, {\\"player_name\\": \\"player_2\\", \\"seat_number\\": 3}, {\\"player_name\\": \\"player_3\\", \\"seat_number\\": 4}]}"}, {"role_type": "userinput", "role_name": "user", "role_content": "分配座位"}, {"role_type": "userinput", "role_name": "user", "role_content": "通知身份"}, "主持人 : 你是player_1, 你的位置是1号， 你分配的单词是汽车", {"role_type": "userinput", "role_name": "user", "role_content": "开始新一轮的讨论"}, "主持人 : 当前存活的玩家有4位，他们是player_1, 李四(人类玩家), player_2, player_3", "主持人 : 现在我们开始发言环节，按照座位顺序由小到大进行发言，首先是1号位的player_1"]', 'type': 'reactExecution'}], 'userInteraction': '["通知身份", "主持人 : 你是李四(人类玩家), 你的位置是2号， 你分配的单词是汽车", "开始新一轮的讨论", "主持人 : 现在我们开始发言环节，按照座位顺序由小到大进行发言，首先是1号位的player_1", "主持人 : 当前存活的玩家有4位，他们是player_1, 李四(人类玩家), player_2, player_3"]'}
'''
#step 4 剧本杀/谁是卧底/智能交互/关键信息_1
params_string =\
{'observation': {'toolResponse': 'ok'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/关键信息_1'),
  'sessionId': goc_test_sessionId,
  'type': 'onlyTool',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


## step 4-1 讨论输入 
params_string =\
{'observation': {'toolResponse': '我的单词是一个机械'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/开始新一轮的讨论'),
  'sessionId': goc_test_sessionId,
  'type': 'reactExecution',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


# step 4-2 讨论输入 
params_string =\
{'observation': {'toolResponse': '我的单词可以用于交通运输'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/开始新一轮的讨论'),
  'sessionId': goc_test_sessionId,
  'type': 'reactExecution',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


## step 4-3 讨论输入 
params_string =\
{'observation': {'toolResponse': '我的单词是一种工业品'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/开始新一轮的讨论'),
  'sessionId': goc_test_sessionId,
  'type': 'reactExecution',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


## step 4-4 讨论输入 
params_string =\
{'observation': {'toolResponse': '我的单词可以载人'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/开始新一轮的讨论'),
  'sessionId': goc_test_sessionId,
  'type': 'reactExecution',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)



#step 4 剧本杀/谁是卧底/智能交互/关键信息_2
params_string =\
{'observation': {'toolResponse': 'ok'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/关键信息_2'),
  'sessionId': goc_test_sessionId,
  'type': 'onlyTool',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)



## step 5-1 投票 agent 2  player_1  1号座位
params_string =\
{'observation': {'toolResponse': '我投player_2'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/票选卧底_1'),
  'sessionId': goc_test_sessionId,
  'type': 'reactExecution',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


## step 5-2 投票 人类agent  李四 2号
params_string =\
{'observation': {'toolResponse': '我投player_1'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/票选卧底_1'),
  'sessionId': goc_test_sessionId,
  'type': 'reactExecution',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


## step 5-3 投票    agent3 player_2 3No
params_string =\
{'observation': {'toolResponse': '我投player_1'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/票选卧底_1'),
  'sessionId': goc_test_sessionId,
  'type': 'reactExecution',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


# step 5-3 投票   agent1 player_3 4号
params_string =\
{'observation': {'toolResponse': '我也投play_1'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/票选卧底_1'),
  'sessionId': goc_test_sessionId,
  'type': 'reactExecution',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


#step 6 剧本杀/谁是卧底/智能交互/关键信息_4
params_string =\
{'observation': {'toolResponse': 'ok'},
  'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/关键信息_4'),
  'sessionId': goc_test_sessionId,
  'type': 'onlyTool',
  'scene': 'UNDERCOVER'}
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)

