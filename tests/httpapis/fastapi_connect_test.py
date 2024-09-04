# 导入必要的库
import requests
import json

#from muagent.schemas.apis.ekg_api_schema import *

# 定义 API 基本 URL
base_url = "http://localhost:3737"

# 测试获取嵌入模型参数
response = requests.get(f"{base_url}/embeddings/params")
print(response.json())

