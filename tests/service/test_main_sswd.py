# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
#此代码为在aistudio上运行的代码





#路径增加
import sys
import os
src_dir = os.path.join(
    os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
#/home/user/muagent
print(src_dir)

sys.path.append(src_dir + '/muagent/service/ekg_reasoning')
sys.path.append(src_dir ) #/Users/zhangqi/codes/antcodes/muagent/muagent
sys.path.append(src_dir + '/muagent/examples')


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
                'definition_value': os.environ['nb_definition_value']

            }
        )

    #7 构建ekg_construct_service

    ekg_construct_service = EKGConstructService(
            embed_config        =   embed_config,
            llm_config          =   llm_config,
            tb_config           =   tb_config,
            gb_config           =   gb_config,
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

    # logger.info('尝试查找一阶近邻')
    # start_nodeid = hash_id('GM00001931_goc' )
    # start_nodetype    =' opsgptkg_intent'

    # neighbor_nodes = ekg_construct_service.gb.get_neighbor_nodes(attributes={"id": start_nodeid,}, 
    #                                   node_type=start_nodetype)

    # current_nodes = ekg_construct_service.gb.get_current_nodes(attributes={"id": start_nodeid,}, 
    #                                   node_type=start_nodetype)

    # print(neighbor_nodes)
    # print(current_nodes)
    
    # exit()
    #########
    #新版意图识别测试 & 第一次用户输入
    # goc_test_sessionId = "TS_GOC_103346456601_0709001_401"
    


    # # params_string = {
    # #   "observation": "{\"content\":\"开始游戏\"}",
    # #   "scene": "UNDERCOVER",
    # #   "sessionId": goc_test_sessionId
    # # }
    

    # #谁是卧底 通用
    # params_string = {
    #       "scene": "NEXA",
    #       "startRootNodeId": '4bf08f20487bfb3d34048ddf455bf5dd', #hash_id('剧本杀' ),
    #       "intentionRule": ["nlp"],
    #       "intentionData": "执行谁是卧底进程",
    #       "observation": "{\"content\":\"开始游戏\"}",
    #       "sessionId": goc_test_sessionId
    #     }




    # params_string = json.dumps(params_string, ensure_ascii=False)
    # res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    # print('res_to_lingsi', res_to_lingsi)
    # # #########




    sessionId = '349579720439752097847_25'
    #谁是卧底 通用
    params_string = \
    {

          "scene": "NEXA",
          "startRootNodeId": '4bf08f20487bfb3d34048ddf455bf5dd', #hash_id('剧本杀' ),
          "intentionRule": ["nlp"],
          "intentionData": "执行谁是卧底进程",
          "observation": "{\"content\":\"开始游戏\"}",
          "sessionId": sessionId
        }
    # params_string = {
    #   "observation": "{\"content\":\"开始游戏\"}",
    #   "scene": "UNDERCOVER",
    #   "sessionId": goc_test_sessionId
    # }
    
        
    params_string = json.dumps(params_string, ensure_ascii=False)
    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    print('res_to_lingsi', res_to_lingsi)
    ##########
    
    
    #====== step 1 result ===
    params_string = \
    {'currentNodeId': '756c3707f53991fb2118ab5d92d28539',
       'type': 'onlyTool',
       'observation': '{"toolResponse":"\\n\\n| 座位 | 玩家 |\\n|---|---|\\n| 1 | **王鹏** |\\n| 2 | **人类玩家** |\\n| 3 | **李静** |\\n| 4 | **张伟** |","toolKey":"undercover.dispatch_position","toolParam":"分配座位"}',
       'scene': 'UNDERCOVER',
       'sessionId': sessionId}
    
    params_string = json.dumps(params_string, ensure_ascii=False)
    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    print('res_to_lingsi', res_to_lingsi)
    ##########



    #====== step 2  result ===
    params_string = \
    {
          "currentNodeId": "7703bd47cc2dbdebb0a5151b83c26a11",
          "type": "onlyTool",
          "observation": "{\"toolResponse\":\"[{\\\"单词\\\":\\\"虾\\\",\\\"agent_name\\\":\\\"agent_人类玩家\\\",\\\"agent_description\\\":\\\"平民_1\\\",\\\"player_name\\\":\\\"人类玩家\\\"},{\\\"单词\\\":\\\"鱼\\\",\\\"agent_name\\\":\\\"agent_李静\\\",\\\"agent_description\\\":\\\"卧底_1\\\",\\\"player_name\\\":\\\"李静\\\"},{\\\"单词\\\":\\\"虾\\\",\\\"agent_name\\\":\\\"agent_张伟\\\",\\\"agent_description\\\":\\\"平民_3\\\",\\\"player_name\\\":\\\"张伟\\\"},{\\\"单词\\\":\\\"虾\\\",\\\"agent_name\\\":\\\"agent_王鹏\\\",\\\"agent_description\\\":\\\"平民_2\\\",\\\"player_name\\\":\\\"王鹏\\\"}]\",\"toolKey\":\"undercover.dispatch_keyword\",\"toolParam\":\"角色分配和单词分配\"}",
          "scene": "UNDERCOVER",
          "sessionId": sessionId

    }
    params_string = json.dumps(params_string, ensure_ascii=False)
    res_to_lingsi = main(params_string,  memory_manager, geabase_handler, intention_router)
    print('res_to_lingsi', res_to_lingsi)
    ##########


