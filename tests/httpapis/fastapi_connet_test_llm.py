# -*- coding: utf-8 -*-



# 导入必要的库
import requests
import json

#from muagent.schemas.apis.ekg_api_schema import *

# 定义 API 基本 URL
base_url = "http://localhost:3737"








# #谁是卧底 定制
# request = \
# {
#   "features": {
#     "query": {
#       "observation": "{\"content\":\"开始游戏\"}",
#       "scene": "UNDERCOVER",
#       "sessionId": "41faeed1_39ba_414b_dcad_f22e7b32caae006"
#     }
#   }
# }


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
#       "sessionId": "41faeed1_39ba_414b_dcad_f22e7b32caae003"
#     }
#   }
# }

#llm 调用
request = \
{
  "text": "你是谁？",
  "stop":"aaa"
    }
    
    
# 测试获取嵌入模型参数
response = requests.post(f"{base_url}/llm/generate", json = request)
print(response.json())
print(response)


