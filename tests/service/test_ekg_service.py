# -*- coding: utf-8 -*-
#此代码为在aistudio上运行的代码

# -*- coding: utf-8 -*-
#此代码为在aistudio上运行的代码

#路径增加
import sys
from typing import List
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
from muagent.schemas.ekg.ekg_graph import TYPE2SCHEMA
from muagent.schemas.common import GNode, GEdge
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
        
    # # 2、自定义向量模型配置接口
    # embeddings = None
    # #embeddings = CustomizedEmbeddings()
    # embed_config = EmbedConfig(
    #     embed_model="default",
    #     langchain_embeddings=embeddings
    # )
    
    
    # # 3、tbase接口配置
    # if os.environ['operation_mode'] == 'antcode': # 'open_source' or 'antcode'
    #     tb_config = TBConfig(
    #         tb_type     = os.environ["tb_type"],
    #         index_name  = os.environ["tb_index_name"],
    #         host        = os.environ['tb_host'],
    #         port        = int(os.environ['tb_port']),
    #         username    = os.environ['tb_username'],
    #         password    = os.environ['tb_password'],
    #         extra_kwargs={
    #             'host': os.environ['tb_host'],
    #             'port': int(os.environ['tb_port']),
    #             'username': os.environ['tb_username'],
    #             'password': os.environ['tb_password'],
    #             'definition_value': os.environ['tb_definition_value'],
    #             'expire_time': int(os.environ['tb_expire_time']) ,
    #         }
    #     )
    # else:
    #     # 初始化 TbaseHandler 实例
    #     tb_config = TBConfig(
    #         tb_type="TbaseHandler",
    #         index_name="shanshi_node",
    #         host=os.environ['tb_host'],
    #         port=os.environ['tb_port'],
    #         username=os.environ['tb_username'],
    #         password=os.environ['tb_password'],
    #         extra_kwargs={
    #             'host': os.environ['tb_host'],
    #             'port': os.environ['tb_port'],
    #             'username': os.environ['tb_username'] ,
    #             'password': os.environ['tb_password'],
    #             'definition_value': os.environ['tb_definition_value']
    #         }
    #     )
    # # 指定index_name
    # index_name = os.environ["tb_index_name"]
    # # th = TbaseHandler(TBASE_ARGS, index_name, definition_value="message")
    # # th = TbaseHandler(tb_config, index_name, definition_value="message")
    # # th = TbaseHandler(tb_config, index_name, definition_value="message_test_new")
    # th = TbaseHandler(tb_config, index_name, definition_value=os.environ['tb_definition_value'])
    
    # # # drop index
    # # th.drop_index(index_name)
    
    
    
    
    # # 5、memory 接口配置
    # # create tbase memory manager
    # memory_manager = TbaseMemoryManager(
    #             unique_name="EKG", 
    #             embed_config=embed_config, 
    #             llm_config=llm_config,
    #             tbase_handler=th,
    #             use_vector=False
    #         )
    
    
    
    # #6 geabase 接口配置
    # if os.environ['operation_mode'] == 'antcode': # 'open_source' or 'antcode'
    #     gb_config = GBConfig(
    #         gb_type="GeaBaseHandler", 
    #         extra_kwargs={
    #             'metaserver_address': os.environ['metaserver_address'],
    #             'project': os.environ['project'],
    #             'city': os.environ['city'],
    #             # 'lib_path':  '%s/geabase/geabase-client-0.0.1/libs'%(tar_path),
    #             'lib_path': os.environ['lib_path']
    #         }
    #     )
    # else:
    #     # 初始化 NebulaHandler 实例
    #     gb_config = GBConfig(
    #         gb_type="NebulaHandler",
    #         extra_kwargs={
    #             'host': os.environ['nb_host'],
    #             'port': os.environ['nb_port'],
    #             'username': os.environ['nb_username'] ,
    #             'password': os.environ['nb_password'],
    #             "space": os.environ['nb_space'],
    #             #'definition_value': os.environ['nb_definition_value']
    
    #         }
    #     )
    
    # #7 构建ekg_construct_service
    
    # ekg_construct_service = EKGConstructService(
    #         embed_config        =   embed_config,
    #         llm_config          =   llm_config,
    #         tb_config           =   tb_config,
    #         gb_config           =   gb_config,
    #         initialize_space    =  False
    #     )
        
    # intention_router = IntentionRouter(
    #     ekg_construct_service.model,
    #     ekg_construct_service.gb,
    #     ekg_construct_service.tb,
    #     embed_config
    # )
    
    # #8 获取main需要的内容
    # memory_manager = memory_manager
    # #geabase_handler    =     GeaBaseHandler(gb_config)
    # geabase_handler    =     ekg_construct_service.gb
    # intention_router   =     intention_router
    
    # 初始化 NebulaHandler 实例
    gb_config = GBConfig(
        gb_type="NebulaHandler", 
        extra_kwargs={
            'host': os.environ["nb_host"], # config_data["nebula_config"]['host'],
            'port': os.environ["nb_port"], # config_data["nebula_config"]['port'],
            'username': os.environ["nb_username"], # config_data["nebula_config"]['username'] ,
            'password': os.environ["nb_password"], # config_data["nebula_config"]['password'],
            "space": os.environ["nb_space"], # config_data["nebula_config"]['space_name'],    
        }
    )
    
    # 初始化 TbaseHandler 实例
    tb_config = TBConfig(
        tb_type="TbaseHandler",
        index_name="muagent_test",
        host=os.environ["tb_host"], # config_data["tbase_config"]["host"],
        port=os.environ["tb_port"], # config_data["tbase_config"]['port'],
        username=os.environ["tb_username"], # config_data["tbase_config"]['username'],
        password=os.environ["tb_password"], # config_data["tbase_config"]['password'],
        extra_kwargs={
            'host': os.environ["tb_host"], # config_data["tbase_config"]['host'],
            'port': os.environ["tb_port"], # config_data["tbase_config"]['port'],
            'username': os.environ["tb_username"], # config_data["tbase_config"]['username'] ,
            'password': os.environ["tb_password"], # config_data["tbase_config"]['password'],
            'definition_value': os.environ["tb_definition_value"], # config_data["tbase_config"]['definition_value']
        }
    )
    

    
    #embeddings = CustomEmbeddings()
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
        initialize_space    =  False
    )

    
    
    ekg_service = ekg_construct_service
    teamid = "default"
    # node_id = '剧本杀/谁是卧底/智能交互/关键信息_4'
    # start_nodetype    ='opsgptkg_task'
    
    
    #测试加节点
    #one_node= GNode(id=node_id, type='opsgptkg_task', attributes={'ID': 8901447933395410622, 'extra': '{"pattern": "react","dodisplay":"True"}', 'action':'single', 'teamids': '', 'gdb_timestamp': '1728912141060', 'executetype': '', 'description': '##角色##\n你正在参与“谁是卧底”这个游戏，你的角色是[主持人]。你熟悉“谁是卧底”游戏的完整流程，你需要完成[任务]，保证游戏的顺利进行。\n目前已经完成 1)位置分配; 2)角色分配和单词分配。\n##任务##\n向所有玩家通知信息他们的 座位信息和单词信息。\n发送格式是： 【身份通知】你是{player_name}, 你的位置是{位置号}号， 你分配的单词是{单词}\n##详细步骤##\nstep1.依次向所有玩家通知信息他们的 座位信息和单词信息。发送格式是： 你是{player_name}, 你的位置是{位置号}号， 你分配的单词是{单词}\nstpe2.所有玩家信息都发送后，结束\n\n##注意##\n1. 每条信息只能发送给对应的玩家，其他人无法看到。\n2. 不要告诉玩家的角色信息，即不要高斯他是平民还是卧底角色\n3. 在将每个人的信息通知到后，本阶段任务结束\n##输出##\n请以列表的形式，给出参与者的所有行动。每个行动表示为JSON，格式为\n[{"action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}, ...]\n\n关键词含义如下：\n_ player_name (str): 行动方的 player_name，若行动方为主持人，为空，否则为玩家的 player_name；\n_ agent_name (str): 行动方的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。\n_ content (str): 行动方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。\n_ memory_tag (List[str]): 无论行动方是主持人还是玩家，memory_tag 固定为**所有**信息可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]\n\n#example#\n如果是玩家发言，则用 {"action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{ "memory_tag":["agent_name_a","agent_name_b"],"content": "str"}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description\n\n如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["agent_name_a","agent_name_b"], "content": "str",}]}\n\n##注意事项##\n1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。\n2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。\n3. 输出列表的最后一个元素一定是{"action": "taskend"}。\n4. 整个list是一个jsonstr，请输出jsonstr，不用输出markdown格式\n5. 结合已有的步骤，每次只输出下一个步骤，即一个 {"action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}', 'name': '通知身份', 'accesscriteria': ''})
    one_node=   GNode(id='剧本杀/谁是卧底/智能交互/统计票数', type='opsgptkg_task', attributes={'ID': -6836070348442528830, 'teamids': '', 'action':'react','gdb_timestamp': '1728913701092', 'executetype': '', 'description': '##以上为本局游戏历史记录##\n##角色##\n你是一个统计票数大师，你非常擅长计数以及统计信息。你正在参与“谁是卧底”这个游戏，你的角色是[主持人]。你熟悉“谁是卧底”游戏的完整流程，你需要完成[任务]，保证游戏的顺利进行。 现在是票数统计阶段\n\n##任务##\n以结构化的语句来模拟进行 谁是卧底的票数统计阶段， 也仅仅只票数统计阶段环节，票数统计阶段结束后就本阶段就停止了，由后续的阶段继续进行游戏。 在这一个环节里，由主持人根据上一轮存活的玩家投票结果统计票数。 \n##详细步骤##\n你的任务如下:\nstep1. 主持人感知上一轮投票环节每位玩家的发言, 统计投票结果，格式为[{"player_name":票数}]. \nstep2  然后，主持人宣布死亡的玩家，以最大票数为本轮被投票的目标，如果票数相同，则取座位号高的角色死亡。并告知所有玩家本轮被投票玩家的player_name。（格式为【重要通知】本轮死亡的玩家为XXX）同时向所有玩家宣布，被投票中的角色会视为立即死亡（即不再视为存活角色）\nstep3. 在宣布死亡玩家后，本阶段流程结束，由后续阶段继续推进游戏\n该任务的参与者为主持人和所有存活的玩家，信息可见对象是所有玩家。\n##注意##\n1.如果有2个或者两个以上的被玩家被投的票数相同，则取座位号高的玩家死亡。并告知大家原因：票数相同，取座位号高的玩家死亡\n2.在统计票数时，首先确认存活玩家的数量，再先仔细回忆，谁被投了。 最后统计每位玩家被投的次数。 由于每位玩家只有一票，所以被投次数的总和等于存活玩家的数量 \n3.通知完死亡玩家是谁后，本阶段才结束，由后续阶段继续推进游戏。输出 {"action": "taskend"}即可\n4.主持人只有当通知本轮死亡的玩家时，才使用【重要通知】的前缀，其他情况下不要使用【重要通知】前缀\n5.只统计上一轮投票环节的情况\n##example##\n{"thought": "在上一轮中, 存活玩家有 小北,李光,赵鹤,张良 四个人。 其中 小北投了李光, 赵鹤投了小北, 张良投了李光, 李光投了张良。总结被投票数为： 李光:2票; 小北:1票,张良:1票. Check一下，一共有四个人投票了，被投的票是2（李光）+1（小北）+1（张良）=4，总结被投票数没有问题。 因此李光的票最多", "action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["all"], "content": "李光:2票; 小北:1票,张良:1票 .因此李光的票最多.【重要通知】本轮死亡玩家是李光",}]}\n\n##example##\n{"thought": "在上一轮中, 存活玩家有 小北,人类玩家,赵鹤,张良 四个人。 其中 小北投了人类玩家, 赵鹤投了小北, 张良投了小北, 人类玩家投了张良。总结被投票数为：小北:2票,人类玩家:1票,张良:0票 .Check一下，一共有四个人投票了，被投的票是2（小北）+1（人类玩家）+张良（0）=3，总结被投票数有问题。 更正总结被投票数为：小北:2票,人类玩家:1票,张良:1票。因此小北的票最多", "action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["all"], "content": "小北:2票,人类玩家:1票,张良:1票 .因此小北的票最多.【重要通知】本轮死亡玩家是小北",}]}\n\n\n', 'name': '统计票数', 'accesscriteria': '', 'extra': '{"pattern": "react", "endcheck": "True", "memory_tag":"all","model_name":"gpt_4","dodisplay":"True"}','updaterule':'{"存活的玩家":"请根据当前游戏记录更新存活玩家，只输出存活玩家的姓名，不要包含其他信息。"}'})

    def autofill_nodes(nodes: List[GNode]):
        '''
        兼容
        '''
        new_nodes = []
        for node in nodes:
            schema = TYPE2SCHEMA.get(node.type,)
            logger.info(schema)
            logger.info(node)
            extra = node.attributes.pop("extra", {})
            if extra == "":
                extra = {}
    
            if isinstance(extra, str):
                extra = json.loads(extra)  # 尝试将字符串 "extra" 转换为字典
            # logger.info(extra)
    
            node.attributes.update(extra)
            logger.info(node)
            node_data = schema(
                **{**{"id": node.id, "type": node.type}, **node.attributes}
            )
            node_data = {
                k:v
                for k, v in node_data.dict().items()
                if k not in ["type", "ID", "id", "extra"]
            }
            new_nodes.append(GNode(**{
                "id": node.id, 
                "type": node.type,
                "attributes": {**node_data, **node.attributes}
            }))
        return new_nodes
    
    
    def add_nodes(ekg_service, nodes: list[GNode]):
        newnodes = autofill_nodes(nodes)
        logger.info('尝试查插入节点')
        for one_node  in newnodes:   
            one_node.attributes['description']  = one_node.attributes['description']
            one_node.attributes['gdb_timestamp'] = int(one_node.attributes['gdb_timestamp'] )
            if one_node.id != "ekg_team_default":
                one_node.id = hash_id(one_node.id )
            
            if one_node.type == 'opsgptkg_analysis':
                
                one_node.attributes['summaryswitch'] = False
                
            if one_node.type == 'opsgptkg_schedule':
                one_node.attributes['enable'] = True
    
            ekg_service.add_nodes([one_node], teamid=teamid)
            # ekg_service.gb.add_node(one_node)
            
    add_nodes(ekg_service, [one_node])
    
    
    
    
    
    ## 测试 get_neighbor_nodes 和  get_current_nodes
    #node_id = '剧本杀/谁是卧底/智能交互/关键信息_4'
    node_id = '剧本杀/谁是卧底/智能交互/统计票数'
    #node_id = '剧本杀/谁是卧底/智能交互/开始新一轮的讨论'
    start_nodetype    ='opsgptkg_task'
    
    ekg_service = ekg_construct_service
    logger.info(node_id)
    start_nodetype    =start_nodetype
    start_nodeid = hash_id(node_id)

    neighbor_nodes = ekg_service.gb.get_neighbor_nodes(attributes={"id": start_nodeid,}, 
                                    node_type=start_nodetype)

    current_nodes = ekg_service.gb.get_current_nodes(attributes={"id": start_nodeid,}, 
                                    node_type=start_nodetype)

    logger.info(f'neighbor_nodes is {neighbor_nodes}')
    logger.info(f'current_nodes is {current_nodes}')