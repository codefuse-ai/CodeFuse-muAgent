from fastapi import FastAPI
import asyncio
import uvicorn
import time

app = FastAPI()

# 一个异步路由
@app.get("/")
async def read_root():
    await asyncio.sleep(1)  # 模拟一个异步操作
    return {"message": "Hello, World!"}

# 另一个异步路由
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    await asyncio.sleep(5)  # 模拟延迟
    return {"item_id": item_id, "q": q}

# 另一个异步路由
@app.get("/itemstest/{item_id}")
def read_item(item_id: int, q: str = None):
    time.sleep(5)  # 模拟延迟
    return {"item_id": item_id, "q": q}


# 均能并发触发，好像对于io操作会默认管理
uvicorn.run(app, host="localhost", port=3737)
