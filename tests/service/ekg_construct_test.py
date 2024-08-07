import time
import sys, os
from loguru import logger

try:
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
    api_key = os.environ["OPENAI_API_KEY"]
    api_base_url= os.environ["API_BASE_URL"]
    model_name = os.environ["model_name"]
    model_engine = os.environ["model_engine"]
    embed_model = os.environ["embed_model"]
    embed_model_path = os.environ["embed_model_path"]
except Exception as e:
    # set your config
    api_key = ""
    api_base_url= ""
    model_name = ""
    model_engine = os.environ["model_engine"]
    embed_model = ""
    embed_model_path = ""
    logger.error(f"{e}")

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)

import os, sys
from loguru import logger

sys.path.append("/ossfs/workspace/muagent")
sys.path.append("/ossfs/workspace/notebooks/custom_funcs")
from muagent.db_handler import GeaBaseHandler
from muagent.schemas.common import GNode, GEdge
from muagent.schemas.db import GBConfig, TBConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig





# 初始化 GeaBaseHandler 实例
gb_config = GBConfig(
    gb_type="GeaBaseHandler", 
    extra_kwargs={
        'metaserver_address': os.environ['metaserver_address'],
        'project': os.environ['project'],
        'city': os.environ['city'],
        'lib_path': os.environ['lib_path'],
    }
)


# 初始化 TbaseHandler 实例
tb_config = TBConfig(
    tb_type="TbaseHandler",
    index_name="muagent_test",
    host=os.environ['host'],
    port=os.environ['port'],
    username=os.environ['username'],
    password=os.environ['password'],
    extra_kwargs={
        'host': os.environ['host'],
        'port': os.environ['port'],
        'username': os.environ['username'] ,
        'password': os.environ['password'],
        'definition_value': os.environ['definition_value']
    }
)

# llm config
llm_config = LLMConfig(
    model_name=model_name, model_engine=model_engine, api_key=api_key, api_base_url=api_base_url, temperature=0.3,
)


# emebdding config
# embed_config = EmbedConfig(
#     embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
# )

# embed_config = EmbedConfig(
#     embed_model="default",
#     langchain_embeddings=embeddings
# )
embed_config = None

ekg_construct_service = EKGConstructService(
    embed_config=embed_config,
    llm_config=llm_config,
    tb_config=tb_config,
    gb_config=gb_config,
)


import copy
# it's a case, you should use your node and edge attributes
node1 = GNode(**{
    "id": "antshanshi311395_1", 
    "type": "opsgptkg_intent",
    "attributes": {
        "path": "shanshi_test",
        "name": "shanshi_test",
        "description":'shanshi_test', 
        "gdb_timestamp": 1719276995619
    }
})

edge1 = GEdge(**{
    "start_id": "antshanshi311395_1", 
    "end_id": "antshanshi311395_2", 
    "type": "opsgptkg_intent_route_opsgptkg_intent",
    "attributes": {
        "@timestamp": 1719276995619,
        "original_src_id1__": "antshanshi311395_1",  
        "original_dst_id2__": "antshanshi311395_2", 
        "gdb_timestamp": 1719276995619
    }
})

edge2 = GEdge(**{
    "start_id": "antshanshi311395_2", 
    "end_id": "antshanshi311395_3", 
    "type": "opsgptkg_intent_route_opsgptkg_intent",
    "attributes": {
        "@timestamp": 1719276995619,
        "original_src_id1__": "antshanshi311395_2",  
        "original_dst_id2__": "antshanshi311395_3", 
        "gdb_timestamp": 1719276995619
    }
})

node2 = copy.deepcopy(node1)
node2.id = "antshanshi311395_2"

node3 = copy.deepcopy(node1)
node3.id = "antshanshi311395_3"

node1_copy = copy.deepcopy(node1)
node1_copy.attributes = {
    "description":'nav 表示 "文档"和"社区" 导航栏，order 表示 "文档" 和 "社区"的顺序', 
}
node2_copy = copy.deepcopy(node2)
node2_copy.attributes = {
    "description":'用于两种模式，一种是根据语雀url去更新图谱（已发布），一种是应急经验沉淀直接传一个流程图json来更新图谱,文档,文档,文档', 
}

# 需要修改数据库属性后才可以进行测试
t = ekg_construct_service.add_nodes([node1, node2, node3], teamid="shanshi_test")

# 需要修改数据库属性后才可以进行测试
t = ekg_construct_service.add_edges([edge1, edge2], teamid="shanshi_test")

# 需要修改数据库属性后才可以进行测试
t = ekg_construct_service.update_nodes([node1_copy, node2_copy], teamid="shanshi_test")
t

# search_nodes_by_text
text = 'nav 表示 "文档"和"社区" 导航栏，order 表示 "文档" 和 "社区"的顺序'
text = '用于两种模式，一种是根据语雀url去更新图谱（已发布），一种是应急经验沉淀直接传一个流程图json来更新图谱,文档,文档,文档'
teamid = "shanshi_test"
t = ekg_construct_service.search_nodes_by_text(text, teamid=teamid)
t

# 
t = ekg_construct_service.search_rootpath_by_nodeid(nodeid="antshanshi311395_3", node_type="opsgptkg_intent", rootid="antshanshi311395_2")
t


# # 根据节点ID查询节点明细,需要修改数据库属性后才可以进行测试
# t = ekg_construct_service.get_node_by_id('antshanshi311395_2', 'opsgptkg_intent')
# t

# # 根据节点ID查询后续节点/边/路径的明细,需要修改数据库属性后才可以进行测试
# t = ekg_construct_service.get_graph_by_nodeid('antshanshi311395_2', 'opsgptkg_intent', teamid="shanshi_test", hop = 10)
# t

# # 删除节点和边
# t = ekg_construct_service.delete_edges([edge1, edge2], teamid="shanshi_test")
# t = ekg_construct_service.delete_nodes([node1, node2, node3], teamid="shanshi_test")

