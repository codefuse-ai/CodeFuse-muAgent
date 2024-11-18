# -*- coding: utf-8 -*-
#此代码为在开源环境下，测试parallel的代码


#路径增加
import sys
import os
src_dir = os.path.join(
    os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
#/home/user/muagent
print(src_dir)

sys.path.append(src_dir + '/muagent/service/ekg_reasoning')
sys.path.append(src_dir ) 
sys.path.append(src_dir + '/muagent/service/ekg_reasoning/src/utils')
sys.path.append(src_dir + '/examples')

#配置依赖
import test_config  

#一般依赖包
import json
import requests
import time
import logging
import copy
import sys
import os,  base64
from loguru import logger
import uuid

# #geabase 依赖包
# from gdbc2.geabase_client import GeaBaseClient#, Node, Edge, MutateBatchOperation, GeaBaseUtil
# from gdbc2.geabase_env import GeaBaseEnv

#muagent 依赖包
from muagent.connector.schema import Message
from muagent.schemas.db import TBConfig
from muagent.db_handler import *
from muagent.connector.memory_manager import TbaseMemoryManager
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.schemas.db import GBConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.service.ekg_inference import IntentionRouter

#内部其他函数
from src.utils.call_llm import call_llm,  extract_final_result
from src.geabase_handler.geabase_handlerplus import GB_handler
from src.graphstructure.graphstrcturesearchfun import graph_structure_search
from src.utils.normalize import hash_id
from src.graph_search.geabase_search_plus import graph_search_tool
if os.environ['operation_mode'] == 'antcode': # 'open_source' or 'antcode'
    #内部的意图识别接口调用函数
    from src.intention_recognition.intention_recognition_tool import intention_recognition_ekgfunc, intention_recognition_querypatternfunc, intention_recognition_querytypefunc
from src.question_answer.qa_function import qa_class
from src.memory_handler.ekg_memory_handler import memory_handler_ekg
from src.graph_search.call_old_fuction import call_old_fuction
from src.graph_search.graph_search_main import main


# 配置logging模块
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s - %(lineno)d', level=logging.INFO)






if __name__ == '__main__':
    #1、 LLM 和 Embedding Model 配置
    llm_config = LLMConfig(
            model_name      =os.environ["model_name"], 
            model_engine    =os.environ["model_engine"], 
            api_key         =os.environ["OPENAI_API_KEY"], 
            api_base_url    =os.environ["API_BASE_URL"], 
            temperature     =float(os.environ["llm_temperature"]),
        )
    
    #llm = CustomizedModel()
    #llm_config_modelops = LLMConfig(llm=llm)
        
    # 2、自定义向量模型配置接口
    embeddings = None
    #embeddings = CustomizedEmbeddings()
    embed_config = EmbedConfig(
        embed_model="default",
        langchain_embeddings=embeddings
    )
    
    
    # 3、tbase接口配置
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
    # th = TbaseHandler(TBASE_ARGS, index_name, definition_value="message")
    # th = TbaseHandler(tb_config, index_name, definition_value="message")
    # th = TbaseHandler(tb_config, index_name, definition_value="message_test_new")
    th = TbaseHandler(tb_config, index_name, definition_value=os.environ['tb_definition_value'])
    
    # # drop index
    # th.drop_index(index_name)
    
    
    
    
    # 5、memory 接口配置
    # create tbase memory manager
    memory_manager = TbaseMemoryManager(
                unique_name="EKG", 
                embed_config=embed_config, 
                llm_config=llm_config,
                tbase_handler=th,
                use_vector=False
            )
    
    
    
    #6 geabase 接口配置
    if os.environ['operation_mode'] == 'antcode': # 'open_source' or 'antcode'
        gb_config = GBConfig(
            gb_type="GeaBaseHandler", 
            extra_kwargs={
                'metaserver_address': os.environ['metaserver_address'],
                'project': os.environ['project'],
                'city': os.environ['city'],
                # 'lib_path':  '%s/geabase/geabase-client-0.0.1/libs'%(tar_path),
                'lib_path': os.environ['lib_path']
            }
        )
    else:
        # 初始化 NebulaHandler 实例
        gb_config = GBConfig(
            gb_type="NebulaHandler",
            extra_kwargs={
                'host': os.environ['nb_host'],
                'port': os.environ['nb_port'],
                'username': os.environ['nb_username'] ,
                'password': os.environ['nb_password'],
                "space": os.environ['nb_space'],
                #'definition_value': os.environ['nb_definition_value']
    
            }
        )
    
    #7 构建ekg_construct_service
    
    ekg_construct_service = EKGConstructService(
            embed_config        =   embed_config,
            llm_config          =   llm_config,
            tb_config           =   tb_config,
            gb_config           =   gb_config,
            initialize_space    =  False
        )
        
    intention_router = IntentionRouter(
        ekg_construct_service.model,
        ekg_construct_service.gb,
        ekg_construct_service.tb,
        embed_config
    )
    
    #8 获取main需要的内容
    memory_manager = memory_manager
    #geabase_handler    =     GeaBaseHandler(gb_config)
    geabase_handler    =     ekg_construct_service.gb
    intention_router   =     intention_router
    
    

    


    goc_test_sessionId = "TS_GOC_103346456601_0709002_sswd_45"


    #debugmode 调试，谁是卧底初次输入
    params_string = {'observation': {'content': '一起来玩谁是卧底'},
        'sessionId': goc_test_sessionId,
        'scene': 'UNDERCOVER'}
    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    print('res_to_lingsi', res_to_lingsi)

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
    

    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    print('res_to_lingsi', res_to_lingsi)

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

    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    print('res_to_lingsi', res_to_lingsi)

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
    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    print('UNDERCOVER', res_to_lingsi)

    ## step 4-1 讨论输入 
    params_string =\
      {'observation': {'toolResponse': '我的单词是一个机械'},
      'agentName': 'agent_2',
      'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/开始新一轮的讨论'),
      'sessionId': goc_test_sessionId,
      'type': 'reactExecution',
      'scene': 'UNDERCOVER'}
    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    print('UNDERCOVER', res_to_lingsi)


    # # step 4-2 讨论输入 
    # params_string =\
    # {'observation': {'toolResponse': '我的单词可以用于交通运输'},
    # 'agentName': '人类agent_a',
    # 'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/开始新一轮的讨论'),
    # 'sessionId': goc_test_sessionId,
    # 'type': 'reactExecution',
    # 'scene': 'UNDERCOVER'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('UNDERCOVER', res_to_lingsi)

    # ## step 4-3 讨论输入 
    # params_string =\
    # {'observation': {'toolResponse': '我的单词是一种工业品'},
    #   'agentName': 'agent_3',
    # 'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/开始新一轮的讨论'),
    # 'sessionId': goc_test_sessionId,
    # 'type': 'reactExecution',
    # 'scene': 'UNDERCOVER'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('UNDERCOVER', res_to_lingsi)

    # ## step 4-4 讨论输入 
    # params_string =\
    # {'observation': {'toolResponse': '我的单词可以载人'},
    # 'agentName': 'agent_1',
    # 'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/开始新一轮的讨论'),
    # 'sessionId': goc_test_sessionId,
    # 'type': 'reactExecution',
    # 'scene': 'UNDERCOVER'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('UNDERCOVER', res_to_lingsi)






 #    #step 4 剧本杀/谁是卧底/智能交互/关键信息_2
 #    params_string =\
 #    {'observation': {'toolResponse': 'ok'},
 # 'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/关键信息_2'),
 # 'sessionId': goc_test_sessionId,
 # 'type': 'onlyTool',
 # 'scene': 'UNDERCOVER'}
 #    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
 #    print('UNDERCOVER', res_to_lingsi)


 #    ## step 5-1 投票 agent 2  player_1  1号座位
 #    params_string =\
 #    {'observation': {'toolResponse': '我投player_2'},
 # 'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/票选卧底_1'),
 # 'sessionId': goc_test_sessionId,
 # 'type': 'reactExecution',
 # 'scene': 'UNDERCOVER'}
 #    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
 #    print('UNDERCOVER', res_to_lingsi)

 #    ## step 5-2 投票 人类agent  李四 2号
 #    params_string =\
 #    {'observation': {'toolResponse': '我投player_1'},
 # 'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/票选卧底_1'),
 # 'sessionId': goc_test_sessionId,
 # 'type': 'reactExecution',
 # 'scene': 'UNDERCOVER'}
 #    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
 #    print('UNDERCOVER', res_to_lingsi)

 #    ## step 5-3 投票    agent3 player_2 3No
 #    params_string =\
 #    {'observation': {'toolResponse': '我投player_1'},
 # 'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/票选卧底_1'),
 # 'sessionId': goc_test_sessionId,
 # 'type': 'reactExecution',
 # 'scene': 'UNDERCOVER'}
 #    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
 #    print('UNDERCOVER', res_to_lingsi)

 #    # step 5-3 投票   agent1 player_3 4号
 #    params_string =\
 #    {'observation': {'toolResponse': '我也投play_1'},
 # 'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/票选卧底_1'),
 # 'sessionId': goc_test_sessionId,
 # 'type': 'reactExecution',
 # 'scene': 'UNDERCOVER'}
 #    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
 #    print('UNDERCOVER', res_to_lingsi)

 #    #step 6 剧本杀/谁是卧底/智能交互/关键信息_4
 #    params_string =\
 #    {'observation': {'toolResponse': 'ok'},
 # 'currentNodeId': hash_id('剧本杀/谁是卧底/智能交互/关键信息_4'),
 # 'sessionId': goc_test_sessionId,
 # 'type': 'onlyTool',
 # 'scene': 'UNDERCOVER'}
 #    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
 #    print('UNDERCOVER', res_to_lingsi)


# #========================
# ## step 7-1 第二轮讨论输入 
#     params_string =\
#     {'observation': {'toolResponse': '我的单词是一个机械 agent'},
#  'currentNodeId': '剧本杀/谁是卧底/智能交互/开始新一轮的讨论',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'UNDERCOVER'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('UNDERCOVER', res_to_lingsi)

#     # step 7-2  第二轮讨论输入 
#     params_string =\
#     {'observation': {'toolResponse': '我的单词可以用于交通运输 agent'},
#  'currentNodeId': '剧本杀/谁是卧底/智能交互/开始新一轮的讨论',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'UNDERCOVER'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('UNDERCOVER', res_to_lingsi)

#     ## step 7-3  第二轮讨论输入
#     params_string =\
#     {'observation': {'toolResponse': '我的单词是一种工业品 agent'},
#  'currentNodeId': '剧本杀/谁是卧底/智能交互/开始新一轮的讨论',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'UNDERCOVER'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('UNDERCOVER', res_to_lingsi)

#     #step 4 剧本杀/谁是卧底/智能交互/关键信息_2
#     params_string =\
#     {'observation': {'toolResponse': 'ok'},
#  'currentNodeId': '剧本杀/谁是卧底/智能交互/关键信息_2',
#  'sessionId': goc_test_sessionId,
#  'type': 'onlyTool',
#  'scene': 'UNDERCOVER'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('UNDERCOVER', res_to_lingsi)


#  ## step 8-1 投票 agent 2  player_1  1号座位
#     params_string =\
#     {'observation': {'toolResponse': '我投player_2'},
#  'currentNodeId': '剧本杀/谁是卧底/智能交互/票选卧底',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'UNDERCOVER'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('UNDERCOVER', res_to_lingsi)

#     ## step 8-2 投票 人类agent  李四 2号
#     params_string =\
#     {'observation': {'toolResponse': '我投player_3'},
#  'currentNodeId': '剧本杀/谁是卧底/智能交互/票选卧底',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'UNDERCOVER'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('UNDERCOVER', res_to_lingsi)

#     ## step 8-3 投票    agent3 player_2 3No
#     params_string =\
#     {'observation': {'toolResponse': '我投player_2'},
#  'currentNodeId': '剧本杀/谁是卧底/智能交互/票选卧底',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'UNDERCOVER'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('UNDERCOVER', res_to_lingsi)
##########################33
#     #step 2 角色选择tool 结果返回
#     params_string =\
#     {'observation': {'toolResponse': '[{"player_name": "player_1", "seat_number": 1, "agent_name": "agent_1", "agent_description": "狼人_1"}, {"player_name": "player_2", "seat_number": 2, "agent_name": "agent_2", "agent_description": "平民_1"}, {"player_name": "player_3", "seat_number": 3, "agent_name": "agent_3", "agent_description": "平民_2"}, {"player_name": "player_4", "seat_number": 4, "agent_name": "agent_4", "agent_description": "猎人_1"}, {"player_name": "player_5", "seat_number": 5, "agent_name": "agent_5", "agent_description": "狼人_2"}, {"player_name": "player_6", "seat_number": 6, "agent_name": "agent_6", "agent_description": "女巫_1"}, {"player_name": "李四", "seat_number": 7, "agent_name": "人类agent_a", "agent_description": "预言家_1"}]'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/角色选择',
#  'sessionId': goc_test_sessionId,
#  'type': 'onlyTool',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)

#     time.sleep(1)

#     ## step 3 角色分配隐藏不可见 自动执行

#     ## step 4-1 狼人时刻输入 
#     params_string =\
#     {'observation': {'toolResponse': '我建议击杀player_2'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/狼人时刻',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)

#     ## step 4-2 狼人时刻输入
#     params_string =\
#     {'observation': {'toolResponse': '我也建议击杀player_2'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/狼人时刻',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)


#     ## step 5-1 平民输入
#     params_string =\
#     {'observation': {'toolResponse': '我也什么都不知道，我是好人'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/天亮讨论',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)

    ## step 5-2 猎人输入
#     params_string =\
#     {'observation': {'toolResponse': '我也什么都不知道，我是好人'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/天亮讨论',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)

#     ## step 5-3 
#     params_string =\
#     {'observation': {'toolResponse': '我也什么都不知道，我是好人'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/天亮讨论',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)

#     ## step 5-4
#     params_string =\
#     {'observation': {'toolResponse': '我也什么都不知道，我是好人'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/天亮讨论',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)

#     ## step 5-5
#     params_string =\
#     {'observation': {'toolResponse': '我也什么都不知道，我是好人'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/天亮讨论',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)

#     ## step 5-6
#     params_string =\
#     {'observation': {'toolResponse': '我也什么都不知道，我是好人'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/天亮讨论',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)


    # ## step 6-1
    # params_string =\
    #     {'observation': {'toolResponse': '我提议投player_1'},
    # 'currentNodeId': '剧本杀/狼人杀/智能交互/票选凶手',
    # 'sessionId': goc_test_sessionId,
    # 'type': 'reactExecution',
    # 'scene': 'ANTEMC_DINGTALK'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)

    # ## step 6-2
    # params_string =\
    #     {'observation': {'toolResponse': '我提议投player_1'},
    # 'currentNodeId': '剧本杀/狼人杀/智能交互/票选凶手',
    # 'sessionId': goc_test_sessionId,
    # 'type': 'reactExecution',
    # 'scene': 'ANTEMC_DINGTALK'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)

    # ## step 6-3
    # params_string =\
    #     {'observation': {'toolResponse': '我提议投player_1'},
    # 'currentNodeId': '剧本杀/狼人杀/智能交互/票选凶手',
    # 'sessionId': goc_test_sessionId,
    # 'type': 'reactExecution',
    # 'scene': 'ANTEMC_DINGTALK'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)

    # ## step 6-4
    # params_string =\
    #     {'observation': {'toolResponse': '我提议投player_1'},
    # 'currentNodeId': '剧本杀/狼人杀/智能交互/票选凶手',
    # 'sessionId': goc_test_sessionId,
    # 'type': 'reactExecution',
    # 'scene': 'ANTEMC_DINGTALK'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)

    # ## step 6-5 #人类agent
    # params_string =\
    #     {'observation': {'toolResponse': '我提议投player_1'},
    # 'currentNodeId': '剧本杀/狼人杀/智能交互/票选凶手',
    # 'sessionId': goc_test_sessionId,
    # 'type': 'userProblem',
    # 'scene': 'ANTEMC_DINGTALK'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)

    # ## step 6-6 
    # params_string =\
    #     {'observation': {'toolResponse': '我提议投player_1'},
    # 'currentNodeId': '剧本杀/狼人杀/智能交互/票选凶手',
    # 'sessionId': goc_test_sessionId,
    # 'type': 'userProblem',
    # 'scene': 'ANTEMC_DINGTALK'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)


    # ## step 7-1 判断游戏是否结束
    # params_string =\
    #     {'observation': {'toolResponse': '否'},
    # 'currentNodeId': '剧本杀/狼人杀/智能交互/判断游戏是否结束',
    # 'sessionId': goc_test_sessionId,
    # 'type': 'onlyTool',
    # 'scene': 'ANTEMC_DINGTALK'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)



#     ## step 8-1 狼人时刻输入 
#     params_string =\
#     {'observation': {'toolResponse': '我建议击杀player_3'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/狼人时刻',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)

#     ## step 8-2 狼人时刻输入 
#     params_string =\
#     {'observation': {'toolResponse': '我也建议击杀player_3'},
#  'currentNodeId': '剧本杀/狼人杀/智能交互/狼人时刻',
#  'sessionId': goc_test_sessionId,
#  'type': 'reactExecution',
#  'scene': 'ANTEMC_DINGTALK'}
#     res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
#     print('res_to_lingsi', res_to_lingsi)



    #     ## step end 判断游戏是否结束
    # params_string =\
    #     {'observation': {'toolResponse': '是'},
    # 'currentNodeId': '剧本杀/狼人杀/智能交互/判断游戏是否结束',
    # 'sessionId': goc_test_sessionId,
    # 'type': 'onlyTool',
    # 'scene': 'ANTEMC_DINGTALK'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)


    # ## step end 宣布游戏胜利者
    # params_string =\
    #     {'observation': {'toolResponse': '狼人胜利了 狼人胜利了！！！'},
    # 'currentNodeId': '剧本杀/l狼人杀/智能交互/宣布游戏胜利者',
    # 'sessionId': goc_test_sessionId,
    # 'type': 'onlyTool',
    # 'scene': 'ANTEMC_DINGTALK'}
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)