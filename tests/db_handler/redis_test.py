import redis

# 连接到Redis
client = redis.Redis(host='redis-stack', port=6379)

# print('host:', '172.18.0.3')
# 检查连接是否成功
try:
    pong = client.ping()
    if pong:
        print("Connected to Redis")
    else:
        print("Failed to connect to Redis")
except redis.ConnectionError as e:
    print(f"Connection error: {e}")



# from nebula3.gclient.net import ConnectionPool
# from nebula3.Config import Config

# from loguru import logger

# # 配置
# config = Config()
# config.max_connection_pool_size = 10

# # 初始化连接池
# connection_pool = ConnectionPool()


# # 连接到NebulaGraph，假设NebulaGraph服务运行在本地

# connection_pool.init([('127.0.0.1', 9669)], config)

# # 创建会话
# username = 'root'
# password = 'nebula'
# session = connection_pool.get_session(username, password)