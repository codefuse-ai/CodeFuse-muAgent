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





goc_test_sessionId = "TS_GOC_103346456601_0709001_sswd_091"


#debugmode 调试，谁是卧底初次输入
params_string =     \
    {
    "scene": "NEXA",
    "sessionId": goc_test_sessionId,
    "startRootNodeId": hash_id("ekg_team_default"),
    "intentionData": ["预约医生的总结是什么？"],
    "intentionRule":['nlp'],
    "observation": "{\"content\":\"预约医生的总结是什么？\"}"
    }

# 测试获取嵌入模型参数
request = {}
request['features'] = {}
request['features']['query'] = params_string
response = requests.post(f"{base_url}/ekg/graph/ekg_migration_reasoning", json = request)
print(response.json())
print(response)


time.sleep(1)


