from fastapi import FastAPI
import asyncio
import uvicorn
import time

from pydantic import BaseModel


app = FastAPI()

# get node by nodeid and nodetype
class GetNodeRequest(BaseModel):
    nodeid: str
    nodeType: str


# get node by nodeid and nodetype
class GetNodeResponse(BaseModel):
    test: str


# ~/ekg/node/search
@app.get("/ekg/node", response_model=GetNodeResponse)
def get_node(request: GetNodeRequest):
    # 添加预测逻辑的代码
    print(request)
    return GetNodeResponse(
        test="test"
    )
# # 一个异步路由
# @app.get("/")
# async def read_root():
#     await asyncio.sleep(1)  # 模拟一个异步操作
#     return {"message": "Hello, World!"}

# # 另一个异步路由
# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: str = None):
#     await asyncio.sleep(5)  # 模拟延迟
#     return {"item_id": item_id, "q": q}

# # 另一个异步路由
# @app.get("/itemstest/{item_id}")
# def read_item(item_id: int, q: str = None):
#     time.sleep(5)  # 模拟延迟
#     return {"item_id": item_id, "q": q}


# 均能并发触发，好像对于io操作会默认管理
uvicorn.run(app, host="localhost", port=3737)
