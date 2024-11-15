import json
import os
import sys
import logging
import re
src_dir = os.path.join(
    os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
sys.path.append(src_dir + '/muagent/service/ekg_reasoning')
sys.path.append(src_dir ) 
sys.path.append(src_dir + '/muagent/service/ekg_reasoning/src/utils')
sys.path.append(src_dir + '/examples')

import test_config
from src.utils.normalize import hash_id
from muagent.connector.memory_manager import TbaseMemoryManager
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.schemas.db import TBConfig
from muagent.db_handler import *
from muagent.connector.memory_manager import TbaseMemoryManager


llm_config = LLMConfig(
    model_name      =os.environ["model_name"], 
    model_engine    =os.environ["model_engine"], 
    api_key         =os.environ["OPENAI_API_KEY"], 
    api_base_url    =os.environ["API_BASE_URL"], 
    temperature     =float(os.environ["llm_temperature"]),
)

embeddings = None
embed_config = EmbedConfig(
    embed_model="default",
    langchain_embeddings=embeddings
)

if os.environ['operation_mode'] == 'antcode': # 'open_source' or 'antcode'
    tb_config = TBConfig(
        tb_type     = os.environ["tb_type"],
        index_name  = os.environ["tb_index_name"],
        host        = os.environ['tb_host'],
        port        = int(os.environ['tb_port']),
        username    = os.environ['tb_username'],
        password    = os.environ['tb_password'],
        extra_kwargs={
            'host': os.environ['tb_host'],
            'port': int(os.environ['tb_port']),
            'username': os.environ['tb_username'],
            'password': os.environ['tb_password'],
            'definition_value': os.environ['tb_definition_value'],
            'expire_time': int(os.environ['tb_expire_time']) ,
        }
    )
else:
    # 初始化 TbaseHandler 实例
    tb_config = TBConfig(
        tb_type="TbaseHandler",
        index_name="shanshi_node",
        host=os.environ['tb_host'],
        port=os.environ['tb_port'],
        username=os.environ['tb_username'],
        password=os.environ['tb_password'],
        extra_kwargs={
            'host': os.environ['tb_host'],
            'port': os.environ['tb_port'],
            'username': os.environ['tb_username'] ,
            'password': os.environ['tb_password'],
            'definition_value': os.environ['tb_definition_value']
        }
    )

# 指定index_name
index_name = os.environ["tb_index_name"]
th = TbaseHandler(tb_config, index_name, definition_value=os.environ['tb_definition_value'])
memory_manager = TbaseMemoryManager(
    unique_name="EKG", 
    embed_config=embed_config, 
    llm_config=llm_config,
    tbase_handler=th,
    use_vector=False
)

sessionId = "11bd346358a54c1081ebfeab894cee70"
def initialize_replacements(nodeId: str, nodeType: str) -> bool:
    """
    初始化变量，调用eplacements_func实现。
    """
    # nodeId, nodeType = "剧本杀/谁是卧底/智能交互", "opsgptkg_schedule"
    # cur_node = self.geabase_handler.get_current_node(attributes={"id": nodeId}, node_type=nodeType)
    # cur_node_envdescription = json.loads(cur_node.attributes['envdescription'])
    cur_node_envdescription = json.loads('{"witch_poision": "当前女巫的毒药个数为1"}')
    init_flag = False
    for role_name, role_content in cur_node_envdescription.items():
        init_flag = memory_manager.init_global_msg(sessionId, role_name, role_content)
    return init_flag



init_flag = initialize_replacements(hash_id("剧本杀/谁是卧底/智能交互"),"opsgptkg_schedule")

if init_flag:
    print("初始化变量成功")
else:
    print("初始化变量失败")


def fill_replacements(node_description: str, sessionId: str) -> str:
    """
    构建替换后的 prompt 字符串。
    :param sessionId: 一个函数，接收占位符名称并返回对应的值
    :return prompt: 替换后的 prompt 字符串 
    :return placeholders 涉及到的变量
    """
    prompt = node_description
    logging.info(f'prompt:{prompt}')
    placeholders = re.findall(r"#\$\#(.*?)#\$\#", prompt)
    for placeholder in placeholders:
        value = memory_manager.get_msg_content_by_rule_name(sessionId, placeholder)
        logging.info("开始变量替换")
        if value != None:
            prompt = prompt.replace(f'#$#{placeholder}#$#', value)
    return prompt

node_description = "现在开始玩狼人杀游戏，女巫：#$#witch_poision#$#."
print(fill_replacements(node_description,sessionId))

def update_replacement(sessionId: str, nodeId: str) -> bool:
    """
    更新变量名，
    :param sessionId: 对话id
    :param nodeId: 节点id
    """
    cur_node_memory = self.get_cur_node_memory(sessionId, nodeId)
    nodeType =  "opsgptkg_task"
    cur_node = self.geabase_handler.get_current_node(attributes={"id": nodeId}, node_type=nodeType)
    # cur_node_updaterule = json.loads(cur_node.attributes['updaterule'])
    cur_node_updaterule = json.loads('{"witch_poision": ""}')
    update_flag = False
    for placeholder, update_role in cur_node_updaterule.items():
        update_flag = memory_manager.update_msg_content_by_rule(sessionId, placeholder, cur_node_memory, update_role)
    return update_flag