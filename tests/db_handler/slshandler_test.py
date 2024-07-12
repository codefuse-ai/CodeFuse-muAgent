import sys, os
from loguru import logger

try:
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
    endpoint = os.environ["endpoint"]
    accessKeyId = os.environ["accessKeyId"]
    accessKey = os.environ["accessKey"]
except Exception as e:
    # set your config
    endpoint = ""
    accessKeyId = ""
    accessKey = ""
    logger.error(f"{e}")


src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
print(src_dir)
sys.path.append(src_dir)
from muagent.db_handler.sls_db_handler import AliYunSLSHandler
from muagent.schemas.db import SLSConfig


# 使用示例
project = "ls_devops_eg_node_edge"
logstore = "wyp311395_test"



# 初始化 SLSHandler 实例
sls_config = SLSConfig(
    sls_Type="AliYunSLSHandler", 
    extra_kwargs={
        'project': project,
        'logstore': logstore,
        'accessKeyId': accessKeyId,
        'accessKey': accessKey,
        'endpoint': endpoint
    }
)
sls = AliYunSLSHandler(sls_config)


# list_logstores
print(sls.list_logstores())

# pull logs
print(sls.list_shards())

# add datas
t = [{
        'type': 'node_intent',
        'name': 'wenjin',
        'id': 'wenjin_id',
        'description': 'wenjin_description',
        'operation_type': 'ADD',
        'path': '',
        'start_id': '',
        'end_id': ''
}]

write_data_list = [
    [(key, v) for key, v in tt.items()]
    for tt in t
]

# sls.add_data(write_data_list[0])
sls.add_datas(write_data_list)

# get logs
print(sls.get_logs())

# pull logs
print(sls.pull_logs())



