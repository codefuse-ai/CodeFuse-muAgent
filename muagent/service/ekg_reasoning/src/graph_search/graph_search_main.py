# -*- coding: utf-8 -*-
#此代码为在aistudio上运行的代码

#路径增加
import sys
import os
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
# print(src_dir)
sys.path.append(src_dir)


src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
)
sys.path.append(src_dir)
# print(src_dir)




#一般依赖包
import json
import requests
import time
# import logging
from ..utils.logger import logging
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
from muagent.schemas.ekg.ekg_reason import LingSiResponse, ResToLingsi
if os.environ['operation_mode'] == 'antcode': # 'open_source' or 'antcode'
    from muagent.service.web_operation.web_act_ant import WebAgent



#内部其他函数
from src.utils.call_llm import call_llm,  extract_final_result
from src.geabase_handler.geabase_handlerplus import GB_handler
from src.graphstructure.graphstrcturesearchfun import graph_structure_search
from src.utils.normalize import hash_id
from src.graph_search.geabase_search_plus import graph_search_tool
if os.environ['operation_mode'] == 'antcode': # 'open_source' or 'antcode'
    #内部的意图识别接口调用函数
    from src.intention_recognition.intention_recognition_tool import intention_recognition_ekgfunc, intention_recognition_querypatternfunc, intention_recognition_querytypefunc
    from src.generalization_reasoning.generalization_reason import GeneralizationReason
from src.question_answer.qa_function import qa_class
from src.memory_handler.ekg_memory_handler import memory_handler_ekg
from src.graph_search.call_old_fuction import call_old_fuction



# # 配置logging模块
# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s - %(lineno)d', level=logging.INFO)




class graph_search_process():
    '''
        图谱推理主流程class
    '''
    def __init__(self, geabase_handler, memory_manager,  intention_router, lingsi_response, scene , sessionId, currentNodeId, 
                observation, userAnswer, inputType, startRootNodeId, intentionRule, intentionData,
                startFromRoot = True,
                index_name = 'ekg_migration_new', unique_name="EKG",
                llm_config=None
                ):
        self.memory_manager =  memory_manager #memory_init(index_name = 'ekg_migration', unique_name="EKG")

        self.lingsi_response = lingsi_response
        self.scene = scene
        self.sessionId = sessionId
        self.currentNodeId = currentNodeId
        self.observation = observation
        if type(self.observation) == str:
            self.observation = json.loads(self.observation)
        
        self.userAnswer = userAnswer
        self.inputType = inputType

        #意图识别需要的依赖
        self.startRootNodeId = startRootNodeId
        self.intentionRule = intentionRule
        self.intentionData= intentionData
        self.startFromRoot = startFromRoot

        #封装好的辅助class/函数
        self.llm_config = llm_config
        self.geabase_handler = geabase_handler
        self.gb_handler = GB_handler(geabase_handler)
        self.gst = graph_search_tool(geabase_handler, self.memory_manager, llm_config=llm_config)
        self.memory_handler  = memory_handler_ekg(memory_manager, geabase_handler)

        #意图识别相关的状态标记
        self.queryPattern = None
        self.queryType    = None
        self.intentionRecognitionSituation = 'None'
        #意图识别相关函数
        self.intention_router = intention_router



        #计算起始时间
        self.start_datetime = int(time.time()*1000)
    # def scene_judgement(self, scene:str)->str:
    #     if scene == 'generalizationReasoning':
    #         return 'generalizationReasoning'

    def state_judgement(self, inputType:str)->str:
        '''
            根据当前情况，判断当前算法输入所处的状态
                {
                "FIRST_INPUT",                      #第一次输入
                "INTENT_QUESTION_RETURN_ANSWER",    #意图识别期间，用户提问的返回
                "TOOL_EXECUTION_RESULT",            #tool 执行的返回
                "REACT_EXECUTION_RESULT",           #react 执行的返回
                "tool_QUESTION_RETURN_ANSWER"       #task阶段，不执行tool，而是向用户问填空题/选择题
                }
        '''
        if inputType == None:
            #self.algorithm_State = 'FIRST_INPUT' 
            return 'FIRST_INPUT'

        elif inputType == 'intentQuestion':#INTENT_QUESTION
            #self.algorithm_State = 'INTENT_QUESTION_RETURN_ANSWER'
            return "INTENT_QUESTION_RETURN_ANSWER"

        elif inputType == 'onlyTool':
            #self.algorithm_State = "TOOL_EXECUTION_RESULT"
            return "TOOL_EXECUTION_RESULT"

        elif inputType == 'reactExecution':#REACT_EXECUTION_RESULT
            #self.algorithm_State = "REACT_EXECUTION_RESULT"
            return "REACT_EXECUTION_RESULT"

        elif inputType == 'userProblem':
            #self.algorithm_State = "TOOL_QUESTION_RETURN_ANSWER"
            return "TOOL_QUESTION_RETURN_ANSWER"

    def intentionRecongnition(self):
        #意图识别

        inputType   = self.scene
        bizCode     = self.observation.get('bizCode', None)
        self.observation_bizCode = bizCode
        title       = self.observation.get('title', None)
        self.observation_title   = title
        errorType   = self.observation.get('errorType', None)
        self.observation_errorType = errorType
        content     = self.observation.get('content', None)
        self.observation_content = content
        occurTime   = self.observation.get('occurTime', None)
        self.observation_occurTime = self.observation.get('occurTime', None)

        debug_mode  = self.observation.get('debug_mode', None)# debug_mode 模式
        self.observation_debug_mode = debug_mode
        Designated_intent = self.observation.get('Designated_intent', None)# 在debug_mode模式下， 直接指定intention_path
        self.Designated_intent = Designated_intent


        # bizCode     = self.observation['bizCode']
        # title       = self.observation['title']
        # errorType   = self.observation['errorType']
        # content     = self.observation['content']
        
        if debug_mode == True and Designated_intent != None:
            self.intention_recognition_path = Designated_intent
            return Designated_intent


        if self.scene == 'GOC_DINGTALK' :# errorType 缺失， 应该是goc-agent场景
            userInput = {"dialog": content}
        elif errorType in ['customer_complaint', 'normal_question_alarm', 'user_feedback']:#舆情不需要将content给意图识别
            userInput = {"bizCode": bizCode, "title": title, 
                "execute_type": "dsl2", "errorType": errorType} 

        elif errorType in ['biz_monitor_alarm']:
            userInput = {"bizCode": bizCode, "title": title, 
                "execute_type": "dsl2", "errorType": errorType,  "content": self.observation}

        else:##goc需要将content给意图识别
            userInput = {"bizCode": bizCode, "title": title, 
                "execute_type": "dsl2", "errorType": errorType, "content":content} 
        logging.info(f'inputType {inputType}')
        logging.info(f'userInput {userInput}')

        self.intention_recognition_path = intention_recognition_func(inputType, userInput) 
        logging.info(f'意图识别结果为 {self.intention_recognition_path}')
        return self.intention_recognition_path

    def intentionRecongnitionProcess(self):

        #debug_mode
        debug_mode  = self.observation.get('debug_mode', None)# debug_mode 模式
        self.observation_debug_mode = debug_mode
        Designated_intent = self.observation.get('Designated_intent', None)# 在debug_mode模式下， 直接指定intention_path
        self.Designated_intent = Designated_intent
        if debug_mode == True and self.algorithm_State == "FIRST_INPUT":
            logging.info(f'现在是调试模式,intention_recognition_path 为 {Designated_intent}')
            self.queryPattern = 'executePattern'
            self.intentionRecognitionSituation = 'success'
            self.intention_recognition_path    = Designated_intent
            return 1 #直接结束
        logging.info(f'self.scene is {self.scene}, self.algorithm_State is {self.algorithm_State}' )
        if self.scene ==   'WEREWOLF' and self.algorithm_State == "FIRST_INPUT":
            logging.info(f'现在直接到狼人杀模式')
            Designated_intent = ['剧本杀/狼人杀']
            if os.environ['operation_mode'] == 'antcode':
                node_id = '剧本杀/狼人杀'
                Designated_intent = [node_id]
                self.queryPattern = 'executePattern'
                self.intentionRecognitionSituation = 'success'
                self.intention_recognition_path    = Designated_intent
                self.currentNodeId = '剧本杀/狼人杀'
            else:
                node_id = hash_id('剧本杀/狼人杀')
                Designated_intent = [node_id]
                self.queryPattern = 'executePattern'
                self.intentionRecognitionSituation = 'success'
                self.intention_recognition_path    = Designated_intent
                self.currentNodeId = hash_id('剧本杀/狼人杀')
            return 1 #直接结束
        if self.scene ==   'UNDERCOVER' and self.algorithm_State == "FIRST_INPUT":
            logging.info(f'现在直接到谁是卧底模式')
            #Designated_intent = ['剧本杀/谁是卧底']
            if os.environ['operation_mode'] == 'antcode':
                node_id = '剧本杀/谁是卧底'
                Designated_intent = [node_id]
                logging.info(f'意图识别结果为:{Designated_intent}')
                self.queryPattern = 'executePattern'
                self.intentionRecognitionSituation = 'success'
                self.intention_recognition_path    = Designated_intent
                self.currentNodeId = '剧本杀/谁是卧底'
            else:
                node_id = hash_id('剧本杀/谁是卧底')
                Designated_intent = [node_id]
                logging.info(f'意图识别结果为:{Designated_intent}')
                self.queryPattern = 'executePattern'
                self.intentionRecognitionSituation = 'success'
                self.intention_recognition_path    = Designated_intent
                self.currentNodeId = hash_id('剧本杀/谁是卧底')
            return 1 #直接结束
        if self.lingsi_response.usingRootNode ==  True and self.algorithm_State == "FIRST_INPUT":
            logging.info(f'现在直接到fatherIntention {self.startRootNodeId}')

            node_id = self.startRootNodeId
            Designated_intent = [node_id]
            logging.info(f'意图识别结果为:{Designated_intent}')
            self.queryPattern = 'executePattern'
            self.intentionRecognitionSituation = 'success'
            self.intention_recognition_path    = Designated_intent
            self.currentNodeId = node_id

            return 1 #直接结束


        if self.algorithm_State == "FIRST_INPUT":
            '''
            #第一次输入， 第一次调用 意图识别
                #step 1 判断是执行式还是答疑式输入 self.queryPattern, self.queryType
                #step 2 调用 ekg func 主函数， self.intentionRecognitionSituation ,  self.intentionRecognitionRes
                #step 3 写入memory
            #不是第一次输入， 接受的是意图识别问题用户给的答案

            self.queryPattern  有两种 'executePattern'  or  'qaPattern'
            self.queryType     整体计划查询； 'allPlan'， 下一步任务查询；'nextStep'， 闲聊; 'justChat'


            '''
            #step 1.1 判断是执行式还是答疑式输入
            if  self.intentionRule != ['nlp']:
                self.queryPattern = 'executePattern'
            else:
                logging.info(f'self.intentionData is {self.intentionData}')
                #self.intention_router.get_intention_whether_execute(    query='执行周六的任务',)
                if os.environ['operation_mode'] == 'open_source' and self.intention_router.get_intention_whether_execute(  self.intentionData) == True:
                    
                    self.queryPattern = 'executePattern'
                    
                elif os.environ['operation_mode'] == 'antcode' and intention_recognition_querypatternfunc(self.intentionData) == True:
                    self.queryPattern = 'executePattern'
                else:
                    self.queryPattern = 'qaPattern'

            #step 1.2  判断是 整体计划查询； 'allPlan'， 下一步任务查询；'nextStep'， 闲聊; 'justChat'
            if os.environ['operation_mode'] == 'antcode' :
                self.queryType    = intention_recognition_querytypefunc( self.intentionData )
            elif os.environ['operation_mode'] == 'open_source' :
                self.queryType    = self.intention_router.get_intention_consult_which( self.intentionData )
    

            logging.info(f'意图分析的结果为 queryType is {self.queryType},  self.queryPattern  is {self.queryPattern}')

            #step 2 调用 ekg func 主函数 (无论是执行式还是答疑式，都需要进行意图识别)
            if os.environ['operation_mode']  == 'antcode': #ant内部代码，调用接口函数
                intentionRecognitionRes =   intention_recognition_ekgfunc(
                                                    root_node_id = self.startRootNodeId, 
                                                    rule = self.intentionRule, 
                                                    query= self.intentionData, 
                                                    start_from_root = self.startFromRoot,
                                                    memory = 'None')
            else:
                intentionRecognitionRes =   self.intention_router.get_intention_by_node_info(
                                                    root_node_id = self.startRootNodeId,
                                                    rule = self.intentionRule, 
                                                    query= self.intentionData, 
                                                    start_from_root = self.startFromRoot,
                                                    # memory = 'None'  #函数暂时没有这个接口
                                                )
            if 'intentionRecognitionSituation' not in intentionRecognitionRes.keys():
                intentionRecognitionRes['intentionRecognitionSituation'] = intentionRecognitionRes['status']
            logging.info(f'意图识别结果为:{intentionRecognitionRes}')
            # exit()

            self.intentionRecognitionRes = intentionRecognitionRes
            if intentionRecognitionRes['intentionRecognitionSituation'] == 'success':
                self.intentionRecognitionSituation = 'success'
                self.currentNodeId  = intentionRecognitionRes['node_id']
                self.intention_recognition_path = [ intentionRecognitionRes['node_id'] ]

            elif intentionRecognitionRes['intentionRecognitionSituation'] == 'noMatch':
                self.intentionRecognitionSituation = 'noMatch'
                return 'intention_error'
                #raise ValueError('意图识别noMatch ，退出')
            elif intentionRecognitionRes['intentionRecognitionSituation'] == 'toChoose':
                self.intentionRecognitionSituation = 'toChoose'
                #raise ValueError('反问逻辑尚未构建，退出')
                return 'intention_error'
            else:
                return 'intention_error'
                #raise ValueError('意图识别得到了意料之外的状态值，退出')
                

            #step 3 存储原始输入的query到memory
            # service_name, root_node_id, rule, query, memory

            # service_name = 'node_info_match'
            intentionRecongnitionQuery = {}
            intentionRecongnitionQuery['service_name']  = 'node_info_match'
            intentionRecongnitionQuery['root_node_id']  = self.startRootNodeId
            intentionRecongnitionQuery['memory']        = 'None'
            intentionRecongnitionQuery['rule']          = self.intentionRule
            intentionRecongnitionQuery['query']         = self.intentionData
            query_jsonstr = json.dumps(intentionRecongnitionQuery, ensure_ascii=False)

            if self.currentNodeId == None or  self.currentNodeId == 'None':
                currentNodeId = self.startRootNodeId   #这个时候还在意图识别中， self.currentNodeId = None, 故强行给定一个节点ID，便于写memory
            else:
                currentNodeId = self.currentNodeId
            self.memory_handler.intention_first_input_save( self.sessionId, currentNodeId, query_jsonstr)


            #step 4 存储question 到memory
            if intentionRecognitionRes['intentionRecognitionSituation'] == 'toChoose':
                irMemorySaveId = intentionRecognitionRes['nodes_to_choose'][0]['currentNodeId'] 
                #存问题
                self.memory_handler.intention_problem_save(self.sessionId, irMemorySaveId, json.dumps(intentionRecognitionRes['nodes_to_choose'],  ensure_ascii=False))


                #存选项id
                self.memory_handler.intention_idinfo_save(self.sessionId, irMemorySaveId, json.dumps(intentionRecognitionRes['canditate_id'], ensure_ascii=False))

        elif self.algorithm_State == 'INTENT_QUESTION_RETURN_ANSWER':
            #step 0 存储用户返回的答案
            self.memory_handler.intention_save_return_answer(self.sessionId, self.currentNodeId, self.userAnswer['toolResponse'])
            #step 1 获取该session下的memory
            intention_refere_memory_str = self.memory_handler.intention_get_all(self.sessionId)
            #step 2 调用 ekg func 主函数 (只给memory即可， query 为 用户的回答)

            if os.environ['operation_mode']  == 'antcode': #ant内部代码，调用接口函数
                intentionRecognitionRes =   intention_recognition_ekgfunc(
                                                root_node_id = None, 
                                                rule = None, 
                                                query= json.loads(self.userAnswer)['toolResponse'],  #self.userAnswer 是以 tool的格式返回的，虽然是用户的回答，用户的NLP回答在 toolResponse中
                                                start_from_root = self.startFromRoot,
                                                memory = intention_refere_memory_str )

            else:
                intentionRecognitionRes =   self.intention_router.get_intention_by_node_info(
                                                    root_node_id    = None,
                                                    rule            = None, 
                                                    query           = json.loads(self.userAnswer)['toolResponse'],  #self.userAnswer 是以 tool的格式返回的，虽然是用户的回答，用户的NLP回答在 toolResponse中
                                                    start_from_root = self.startFromRoot,
                                                    memory          = intention_refere_memory_str,#函数暂时没有这个接口,运行到此处会报错， 但是由于当前没有返回逻辑，故先保留在这里
                                                )
            if 'intentionRecognitionSituation' not in intentionRecognitionRes.keys():
                intentionRecognitionRes['intentionRecognitionSituation'] = intentionRecognitionRes['status']
            self.intentionRecognitionRes = intentionRecognitionRes
            if intentionRecognitionRes['intentionRecognitionSituation'] == 'success':
                self.intentionRecognitionSituation = 'success'
                self.currentNodeId  = intentionRecognitionRes['node_id']
                self.intention_recognition_path = [ intentionRecognitionRes['node_id'] ]

            elif intentionRecognitionRes['intentionRecognitionSituation'] == 'noMatch':
                self.intentionRecognitionSituation = 'noMatch'
                return 'intention_error'
            elif intentionRecognitionRes['intentionRecognitionSituation'] == 'toChoose':
                self.intentionRecognitionSituation = 'toChoose'
                return 'intention_error'
            
            #step 3 存储question 到memory
            if intentionRecognitionRes['intentionRecognitionSituation'] == 'toChoose':
                irMemorySaveId = intentionRecognitionRes['nodes_to_choose'][0]['currentNodeId'] 
                #存问题
                self.memory_handler.intention_problem_save(self.sessionId, irMemorySaveId, 
                    json.dumps(intentionRecognitionRes['nodes_to_choose'], ensure_ascii=False))

                #存选项id
                self.memory_handler.intention_idinfo_save(self.sessionId, irMemorySaveId, json.dumps(intentionRecognitionRes['canditate_id'], ensure_ascii=False))
        else:
            logging.info(f'该算法阶段为{self.algorithm_State}不需要意图识别')
    def summary_check(self, nodeid_in_subtree):
        '''
            #根据nodeid_in_subtree 和 memory 判断所有的task节点是否已经有了返回值
            #假设以task为结尾，似乎也能正确的进行check
        '''
        for i in range(len(nodeid_in_subtree)):
            nodeId      = nodeid_in_subtree[i]['nodeId']
            nodeType    = nodeid_in_subtree[i]['nodeType']
            if nodeType == 'opsgptkg_task':# 只有opsgptkg_task 节点才有obsevation
                #这里实质上是在查看这个task tool 是否执行完毕了
                # memory_res = self.memory_manager.get_memory_pool_by_all({ 
                #     "message_index": hash_id(nodeId, self.sessionId), # nodeId.replace(":", "_").replace("-", "_") , 
                #     "chat_index": self.sessionId, "role_name": "function_caller", "role_type": "observation"})
                # message_res = memory_res.get_messages()
                # if message_res == []:
                #     return False     #只要有一个节点没有observation，即不能summary

                message_res = self.memory_handler.nodecount_get( sessionId, currentNodeId)  #查看这个节点的count计数
                if message_res == []:
                    return False
        return True #所有task节点都有observation，则需要summary


    def initialize_replacements(self, nodeId: str, nodeType: str) -> bool:
        """
        初始化变量，调用self.memory_manager.init_global_msg实现
        """
        # nodeId, nodeType = "剧本杀/谁是卧底/智能交互", "opsgptkg_schedule"
        #cur_node = self.geabase_handler.get_current_node(attributes={"id": nodeId}, node_type=nodeType)
        #cur_node_envdescription = json.loads(cur_node.attributes['envdescription'])
        
        try:
            node_envdescription = self.gb_handler.get_tag(rootNodeId = nodeId, rootNodeType = nodeType, key = 'envdescription')
            cur_node_envdescription = json.loads(node_envdescription)
        except Exception as e:
            logging.info(f"发生了一个错误：{e}")
            logging.info(f"变量初始化失败，略过")
            #logging.info(f"node_envdescription：{node_envdescription}")
            return False
            
            #raise ValueError(f"node_envdescription is {node_envdescription}")
            
        
        # cur_node_envdescription = json.loads('{"witch_poision": "当前女巫的毒药个数为1"}')

        try:
            node_envdescription = self.gb_handler.get_tag(rootNodeId = nodeId, rootNodeType = nodeType, key = 'envdescription')
            cur_node_envdescription = json.loads(node_envdescription)
        except Exception as e:
            logging.info(f"发生了一个错误：{e}")
            logging.info(f"输入不是json格式或者为空，变量初始化失败，略过")
            logging.info(f"node_envdescription: {node_envdescription}")
            return False

        
        init_flag = False
        try:
            for role_name, role_content in cur_node_envdescription.items():
                if role_name and role_content:
                    init_flag = self.memory_manager.init_global_msg(self.sessionId, role_name, role_content)
        except Exception as e:
            logging.info(f"变量初始化错误！{e}")
        return init_flag


    def first_user_memory_write(self):
        #如果当前是第一次输入，memory如何填写

        #1 写入信息
        last_intention_nodeid = self.intention_recognition_path[-1] #取意图识别的最后一个节点，将初始的信息放在这里



        role_content = self.observation
        role_content_str = json.dumps(role_content, ensure_ascii=False)
        # print('=====', self.sessionId, last_intention_nodeid,  role_content_str)
        self.memory_handler.first_query_save( self.sessionId, last_intention_nodeid, role_content_str)#第一次query input save

        logger.info(f' sessionID {self.sessionId} 的firstUserInput，不指定nodeId')

        #2 写入 所有子节点信息
        logging.info(f'last_intention_nodeid: {last_intention_nodeid}')
        # gsran = type(last_intention_nodeid)
        # logging.info(f'type(geabase_search_return_all_node) is {gsran}')

        nodeid_in_subtree, _ = self.gb_handler.geabase_search_return_all_nodeandedge(  last_intention_nodeid,  'opsgptkg_intent')
        nodeid_in_subtree_str = json.dumps(nodeid_in_subtree, ensure_ascii=False)
        logging.info(f'整条链路上的节点个数是 len(nodeid_in_subtree) is {len(nodeid_in_subtree)}')
        logging.info(f'整条连路上的节点信息是：{nodeid_in_subtree}')
        
        #nodeid_in_subtree_list = self.gb_handler.geabase_search_reture_nodeslist(  last_intention_nodeid,  'opsgptkg_intent')
        #nodeid_in_subtree_list_str = json.dumps(nodeid_in_subtree_list, ensure_ascii=False)
        
        # 获取 `nodeType` 为 `opsgptkg_schedule` 的 `nodeId`
        try:
            nodeId = [item['nodeId'] for item in nodeid_in_subtree if item['nodeType'] == 'opsgptkg_schedule'][0]
        except Exception as e:
            logging.info("不存在opsgptkg_schedule节点")
        init_flag = self.initialize_replacements(nodeId, nodeType='opsgptkg_schedule')
        if init_flag:
            logging.info('变量初始化完成！')
        else:
            logging.info('变量初始化失败！')
        # logging.info(f'=============================================')
        # logging.info(f'nodeid_in_subtree_str {nodeid_in_subtree_str}')
        # logging.info(f'=============================================')

        self.memory_handler.nodeid_in_subtree_save( self.sessionId, last_intention_nodeid, nodeid_in_subtree_str)


        logging.info('first_user_memory_write over')
        return 1
    def memorywrite(self):
        '''
            这里的memory 需要修改为支持重复访问的情况， 此外， 检索的时候也需要修改
            对于task节点，可以memory先检索，再写入
            对于phenomenon节点， 覆盖写入？ 每次只保留一条数据？
        '''
        # 开始处理
        if self.algorithm_State == 'FIRST_INPUT':# 如果为第一次输入
            logging.info('first_user_memory_write start')
            self.first_user_memory_write()
            logging.info('first_user_memory_write over')
        # elif self.inputType in ["onlyTool", "toolAndPresentation", 'onlyToolOrUserProblem']:# tool执行结果返回
        elif  self.algorithm_State == "TOOL_EXECUTION_RESULT": # tool执行结果返回
            logging.info('当前不为第一次输入，是一个tool执行的返回， 进行memory写入')
            #1.1 先加count
            logging.info('1.1 先加count')
            self.memory_handler.tool_nodecount_add_chapter(self.sessionId, self.currentNodeId)

            user_input_memory_tag = self.gb_handler.user_input_memory_tag(self.currentNodeId, 'opsgptkg_task') #获取任务节点上的用户标注的memory tag
            #1.2 再写 task description
            logging.info('1.2 再写 task description')
            task_description = self.gb_handler.geabase_getDescription(
                    self.currentNodeId, 
                     'opsgptkg_task')
                    
            self.memory_handler.tool_nodedescription_save(self.sessionId, self.currentNodeId, task_description, user_input_memory_tag)
            # 1.3 再写 observation
            logging.info('1.3 再写 observation')
            tool_infomation = self.observation
            
            self.memory_handler.tool_observation_save(self.sessionId, self.currentNodeId, tool_infomation, user_input_memory_tag)


        elif self.algorithm_State == "TOOL_QUESTION_RETURN_ANSWER" and self.gb_handler.geabase_is_react_node == False:  # 用户问答返回，task tool节点
                logging.info('当前不为第一次输入，是一个用户回答问题的返回， 进行memory写入')
                user_input_memory_tag = self.gb_handler.user_input_memory_tag(self.currentNodeId, 'opsgptkg_task') #获取任务节点上的用户标注的memory tag

                #1.1 先加count
                logging.info('1.1 先加count 只有对于tool task 才加')
                
                self.memory_handler.tool_nodecount_add_chapter(self.sessionId, self.currentNodeId)
                #1.2 再写 问用户的问题
                logging.info('1.2 再写 ask_user_question')
                ask_user_question = json.dumps(self.gb_handler.geabase_getnodequestion( rootNodeId = self.currentNodeId, rootNodeType = 'opsgptkg_task'), ensure_ascii=False)
                self.memory_handler.tool_nodedescription_save(self.sessionId, self.currentNodeId, ask_user_question, user_input_memory_tag)
                # 1.3 再写 observation
                logging.info('1.3 再写 observation')
                tool_infomation = self.userAnswer
                self.memory_handler.tool_observation_save(self.sessionId, self.currentNodeId, tool_infomation, user_input_memory_tag)


        elif self.algorithm_State == "REACT_EXECUTION_RESULT": # react 执行结果返回
            # 需要更新count，写入用户返回的memory， 写入新生成的memory。
            # 此时一定不是 最开始运行的时刻，肯定是中间等待其他agent返回结果的时刻
            # 对于结果memory的填写，放在react_running中

            pass  

            

    def get_summary(self):
        #后续待优化，当前只输出所有激活的summary节点
        summary_list = [] 
        #nodeid_in_subtree_memory    = self.memory_manager.get_memory_pool_by_all({ "chat_index": self.sessionId, "role_type": "nodeid_in_subtree"})
        #nodeid_in_subtree           = json.loads( nodeid_in_subtree_memory.get_messages()[0].role_content )
        
        nodeid_in_subtree = self.get_nodeid_in_subtree(self.sessionId, self.currentNodeId)
        for i in range(len(nodeid_in_subtree)):
            if nodeid_in_subtree[i]['nodeType'] == 'opsgptkg_analysis':  #从nodeid_in_subtree中找到analysis的节点
                nodeId = nodeid_in_subtree[i]['nodeId']
                #print(self.sessionId)
                #print(nodeId.replace(":", "_").replace("-", "_"))
                memory_manager_res = self.memory_manager.get_memory_pool_by_all({  
                "chat_index": self.sessionId, 
                "message_index":   hash_id(nodeId, self.sessionId), #nodeId.replace(":", "_").replace("-", "_") + self.sessionId,
                "role_type": "analysis_res"})

                get_messages_res = memory_manager_res.get_messages()
                if len(get_messages_res) == 0:
                    #logging.info(f'现在正在 get_summary， 在这个analysis节点中，未找到相关memory.即该analysis节点未被探索。节点id为{nodeId}')
                    pass
                else:
                    if get_messages_res[-1].role_content == '激活': 
                            #提取analysis节点上的描述信息
                            if self.gst.geabase_judgeNodeReachability(  self.sessionId, 
                                     nodeId,  'opsgptkg_analysis') == True:
                                    
                                    logging.info(f'现在正在 get_summary，结论节点{nodeId} 节点可达')

                                    current_description = self.gb_handler.geabase_getDescription(
                                        nodeId, 
                                        'opsgptkg_analysis')
                                    summary_list.append( current_description )
                            else:
                                #logging.info(f'现在正在 get_summary，结论节点{nodeId} 节点不可达')
                                pass
                    else:
                        #logging.info(f'此summary节点未激活。节点id为{nodeId}')
                        pass
        if len(summary_list) == 0:
            try:
                current_description =self.gb_handler.geabase_getDescription(
                     self.currentNodeId, 
                     'opsgptkg_task')
            except:
                logging.info('在summary时，在memory中未找到激活的summary节点。且最后一个节点不是task节点')
                current_description = ''
            

            logging.info('在summary时，在memory中未找到激活的summary节点。 可能原因是最后节点为task节点，直接返回当前的tool作为返回结果')
            #summary_list = ['任务是:'+current_description, '结果是:' + self.observation['toolResponse']]
            summary_list = [self.observation['toolResponse']]
            

        summary_str = ';'.join(summary_list)

        return summary_str

    def get_nodeid_in_subtree(self, sessionId, nodeId):
        #logging.info(f' sessionId is {self.sessionId},  nodeId is {nodeId}')
        nodeid_in_subtree_memory    = self.memory_manager.get_memory_pool_by_all({ "chat_index": self.sessionId, "role_type": "nodeid_in_subtree"})
        nodeid_in_subtree           = json.loads( nodeid_in_subtree_memory.get_messages()[0].role_content )
        return nodeid_in_subtree
        

        
        # if nodeId == None:
        #     logging.info(f' nodeId == None, 为第一次输入，调用 geabase_search_return_all_nodeandedge  取 nodeid_in_subtree的值' )
        #     nodeid_in_subtree, _ = self.gb_handler.geabase_search_return_all_nodeandedge(  last_intention_nodeid,  'opsgptkg_intent')
        #     return nodeid_in_subtree
        

        # # nodeid_in_subtree_memory= self.memory_manager.get_memory_pool_by_all({ "chat_index": self.sessionId, "role_type": "nodeid_in_subtree"})
        # nodeid_in_subtree_memory= self.memory_manager.get_memory_pool_by_all({ "chat_index": sessionId, "role_type": "nodeid_in_subtree"})

        
        # logging.info(f'nodeid_in_subtree_memory is {nodeid_in_subtree_memory}')

        # nodeid_in_subtree_list = json.loads( nodeid_in_subtree_memory.get_messages()[0].role_content )
        # if len(nodeid_in_subtree_list) == 0:
        #     return nodeid_in_subtree_list[0]
        # for nodeid_in_subtree in nodeid_in_subtree_list:
        #     for one_node_info in nodeid_in_subtree:
        #         if one_node_info['nodeId'] == nodeId:
        #             return nodeid_in_subtree
                    
        # raise ValueError('len(nodeid_in_subtree_list)>0 但是当前节点不在nodeid_in_subtree_list 中')
    
    def qaProcess(self, nodeid_in_subtree):
        '''
            调用qa模块
        '''
        for i in range(len(nodeid_in_subtree)):
            start_nodeid    = nodeid_in_subtree[i]['nodeId']
            start_nodetype  = nodeid_in_subtree[i]['nodeType']
            if start_nodetype == 'opsgptkg_intent':
                break

        qce = qa_class( memory_manager = self.memory_manager, 
            geabase_handler = self.geabase_handler,
            uesr_query = self.intentionData,  #只出现在第一次用户输入的地方
            start_nodeid = start_nodeid, #
            start_nodetype =  'opsgptkg_intent',
            llm_config=self.llm_config
            )
        if self.queryType == 'allPlan':
            res = qce.full_link_summary()
        elif  self.queryType == 'nextStep':
            res = qce.next_step_summary()
        else:
            res = '输入为闲聊，暂不做回复'
        return res


    def grProcess(self, scene:str, sessionId:str, currentNodeId:str, algorithm_State:bool,
            lingsi_response:LingSiResponse,
            geabase_handler,
            memory_handler, llm_config)->dict:
            '''
                调用 泛化推理
            '''
            logging.info(f'当前scene为{scene}')
            if  scene == 'generalizationReasoning_nonretrieval':
                generalizaiton_reasoning = GeneralizationReason(    sessionId     = sessionId,
                    currentNodeId = currentNodeId,
                    memory_handler = memory_handler,   
                    geabase_handler = geabase_handler,       
                    llm_config=llm_config,
                    retrieval_flag = False)
            elif scene == 'generalizationReasoning_test':
                generalizaiton_reasoning = GeneralizationReason(    sessionId     = sessionId,
                    currentNodeId = currentNodeId,
                    memory_handler = memory_handler,      
                    geabase_handler = geabase_handler,     
                    llm_config=llm_config,
                    retrieval_flag = True)
            elif scene == 'generalizationReasoning' or scene =='NEXA':
                generalizaiton_reasoning = GeneralizationReason(    sessionId     = sessionId,
                    currentNodeId = currentNodeId,
                    memory_handler = memory_handler,      
                    geabase_handler = geabase_handler,     
                    llm_config=llm_config,
                    retrieval_flag = True)
            else:
                raise ValueError(f'scene if {scene}')
            if algorithm_State == 'FIRST_INPUT':
                if type(lingsi_response.observation) == str:
                    lingsi_response.observation  = json.loads(lingsi_response.observation)
                input_str_gr = lingsi_response.observation['content']
            else:
                if type(lingsi_response.observation) == str:
                    lingsi_response.observation  = json.loads(lingsi_response.observation)
                input_str_gr = lingsi_response.observation['toolResponse']

            res_to_lingsi = generalizaiton_reasoning.process(
                sessionId           = sessionId, 
                currentNodeId       = 'generalization_reason', 
                input_str           =  input_str_gr)
            return res_to_lingsi

    def outputFuc(self):
        try:
            tool_plan  = self.tool_plan
            tool_plan_3 = self.tool_plan_3
        except:
            pass
        summary_flag = self.summary_flag

        #终止时间戳
        self.end_datetime = int(time.time()*1000)
        currentNodeType = self.gst.search_node_type(self.nodeid_in_subtree, self.currentNodeId )
        logging.info(f"currentNodeId is {self.currentNodeId}  ")
        logging.info(f"currentNodeType is {currentNodeType} , currentNodeId is {self.currentNodeId}")
        if self.gb_handler.get_extra_tag(rootNodeId = self.currentNodeId, rootNodeType = currentNodeType, key = 'dodisplay') == 'True'   \
            or self.gb_handler.get_extra_tag(rootNodeId = self.currentNodeId, rootNodeType = currentNodeType, key = 'dodisplay') == 'Ture' \
                or self.gb_handler.get_tag(rootNodeId = self.currentNodeId, rootNodeType = currentNodeType, key = 'dodisplay') == 'True' :
            outputinfo_str = self.memory_handler.get_output(self.sessionId, self.start_datetime, self.end_datetime, self.lingsi_response.agentName)
        else:
            dodisplaystr = self.gb_handler.get_tag(rootNodeId = self.currentNodeId, rootNodeType = currentNodeType, key = 'dodisplay') 
            logging.info(f" 查询dodisplay字段结果为空, 或者为{dodisplaystr}，本次不对外输出")
            outputinfo_str = None


        if self.queryPattern == 'qaPattern' and self.qaProcessRes!= None :
            # qa result
            logging.info('qa has result')
            res_to_lingsi = {
                'intentionRecognitionSituation': self.intentionRecognitionSituation,
                "sessionId": self.sessionId,
                "type": "None",
                "summary" :   self.qaProcessRes,  # qa Answer 返还给用户f
                "toolPlan":  None ,
                "userInteraction": outputinfo_str,
                }
        elif self.queryPattern == 'qaPattern' and self.qaProcessRes== None :
            # qa result
            logging.info('qa has  None  result')
            res_to_lingsi = {
                'intentionRecognitionSituation': 'queryTypeNoSupport',
                "sessionId": self.sessionId,
                "type": "None",
                "summary" :    None,
                "toolPlan": None ,
                "userInteraction": outputinfo_str,
                }
        # elif len(tool_plan_3) == 1 and 'type' in res_4_1['toolPlan'][0] and  res_4_1['toolPlan'][0]['type'] == 'reactExecution'

        elif len(tool_plan_3) > 0:
            # only_tool
            logging.info('only_tool')
            res_to_lingsi = {
                'intentionRecognitionSituation': self.intentionRecognitionSituation,
                "sessionId": self.sessionId,
                "type": "onlyTool",
                "summary" :    None,
                "toolPlan":tool_plan_3 ,
                "userInteraction": outputinfo_str,
                }
            '''
                toolPlan = [ {'toolDescription': '请用户回答',
                'currentNodeId': nodeId,
                'memory': None,
                'type': 'userProblem',
                'questionDescription': {'questionType': 'essayQuestion',
                'questionContent': {'question': '请玩家根据当前情况发言',
                'candidate': None }}} ]
                
                如果 既有 userInteraction  又有  userProblem
            '''
  
            
        elif len(tool_plan_3) == 0 and len(tool_plan)>0:
            # 后续tool 不可达, "None"
            logging.info("后续tool 不可达, None")
            res_to_lingsi = {
                'intentionRecognitionSituation': self.intentionRecognitionSituation,
                "sessionId": self.sessionId,
                "type": "None",
                "summary" :     None,
                "toolPlan":     None ,
                "userInteraction": outputinfo_str,
                }
        elif len(tool_plan) ==0 and summary_flag == False:
            # 到达某个分支的终点，但是还不是整个子图的终点
            logging.info("到达某个分支的终点，但是还不是整个子图的终点")
            res_to_lingsi = {
                'intentionRecognitionSituation': self.intentionRecognitionSituation,
                "sessionId": self.sessionId,
                "type": "None",
                "summary" :     None,
                "toolPlan":     None ,
                "userInteraction": outputinfo_str,
                }
        elif len(tool_plan) ==0 and summary_flag == True:
            # 所有分支到达终点，summary
            logging.info("所有分支到达终点，summary")
            res_to_lingsi = {
                'intentionRecognitionSituation': self.intentionRecognitionSituation,
                "sessionId": self.sessionId,
                "type": "summary",
                "summary" :     self.get_summary(),
                "toolPlan":     None ,
                "userInteraction": outputinfo_str,
                }
        elif self.toolResponseError_flag == True:
            logging.info("出现了tool 执行错误，终止， 当前能返回什么summary就返回什么summary")
            res_to_lingsi = {
                'intentionRecognitionSituation': self.intentionRecognitionSituation,
                "sessionId": self.sessionId,
                "type": "summary",
                "summary" :     self.get_summary(),
                "toolPlan":     None ,
                "userInteraction": outputinfo_str,
                }
            
        else:
            raise ValueError('图谱扩散得到了预料之外的情况，退出')
        return res_to_lingsi
    
    
    def process(self):
        #step1  根据当前情况，判断当前算法输入所处的状态
        logging.info(f'#step1  根据当前情况，判断当前算法输入所处的状态  self.inputType is {self.inputType}')
        self.algorithm_State = self.state_judgement(self.inputType)  
        logging.info(f'#step1 over，当前算法状态为{self.algorithm_State}')

        #step1.1  其他情况， 泛化推理 或者  WebAgent
        html = None
        task_query = None

        gr_flag =   self.memory_handler.message_get( 
                     sessionId = self.sessionId,
                     nodeId = 'gr', 
                     hashpostfix='gr', 
                     role_name='gr', 
                     role_type='gr')
        logging.info(f'gr_flag is {gr_flag}')

        if self.scene == 'WebAgent':
            logging.info(f'当前scene为{self.scene}')

            if type(self.lingsi_response.observation) == str:
                self.lingsi_response.observation  = json.loads(self.lingsi_response.observation)
                
            if self.algorithm_State == 'FIRST_INPUT':
                task_query  = self.lingsi_response.observation['content']
                html        = self.lingsi_response.observation['toolResponse']
               
            else:
                html = self.lingsi_response.observation['toolResponse']
            #html = html[0:50000]

            agent = WebAgent(memory_manager=self.memory_manager, llm_model_name = 'Qwen2_72B_Instruct_OpsGPT')
            logging.info(f'self.sessionId is {self.sessionId}')
            res_to_lingsi = agent.web_action(chat_index=self.sessionId , 
                html = html, task_query = task_query)

            return res_to_lingsi
            # example :[{
            #     "toolDescription": "toolDescriptionA",
            #     "currentNodeId": "INT_1",
            #     "memory": JsonStr,
            #     "type":"onlyTool",
            #         }]



        elif self.scene == 'generalizationReasoning_test' or  \
            self.scene == 'generalizationReasoning_nonretrieval' or \
            self.scene == 'generalizationReasoning' or \
            gr_flag == 'gr':
            #print(f'scene is {self.scene}')
            #根据scene 直接触发 grProcess

            self.memory_handler.message_save( 
                     sessionId = self.sessionId,
                     nodeId = 'gr', 
                     role_content='gr',
                     hashpostfix='gr', 
                     user_name='gr', 
                     role_name='gr', 
                     role_type='gr')

            res_to_lingsi = self.grProcess(scene = self.scene, sessionId = self.sessionId, 
                currentNodeId   = self.currentNodeId, algorithm_State = self.algorithm_State,
                lingsi_response = self.lingsi_response,
                geabase_handler = self.geabase_handler,
                memory_handler  = self.memory_handler,
                llm_config      = self.llm_config)

            return res_to_lingsi



        #step2 意图识别
        logging.info('#step2  意图识别')
        intention_error_flag = self.intentionRecongnitionProcess()  
        if intention_error_flag == 'intention_error':
            # 意图识别查询失败
    
            if self.queryType != 'justChat' and os.environ['operation_mode'] == 'antcode':
                logging.info(f'意图识别查询失败, 表示没有数据，同时现在不是闲聊 需要泛化推理')

                self.memory_handler.message_save( 
                     sessionId = self.sessionId,
                     nodeId = 'gr', 
                     role_content='gr',
                     hashpostfix='gr', 
                     user_name='gr', 
                     role_name='gr', 
                     role_type='gr')

                res_to_lingsi = self.grProcess(scene = self.scene, sessionId = self.sessionId, 
                    currentNodeId = self.currentNodeId, algorithm_State = self.algorithm_State,
                    lingsi_response= self.lingsi_response,
                    geabase_handler = self.geabase_handler,
                    memory_handler = self.memory_handler, llm_config = self.llm_config)
                return res_to_lingsi
            
            else:
                logging.info('意图识别查询失败, 表示没有数据，且现在是闲聊。直接终止')
                res_to_lingsi = {
                    'intentionRecognitionSituation': self.intentionRecognitionSituation,
                    "sessionId": self.sessionId,
                    "type": "summary",
                    "summary" :     '意图识别未检验到相关数据，且提问和已沉淀知识无关，终止',
                    "toolPlan":     None ,
                    "userInteraction": None,
                    }
                return  res_to_lingsi


        logging.info(f'#step2 意图识别 over，')

        #step3 memory 写入
        logging.info('#step3  memory 写入')
        self.memorywrite()
        logging.info('#step3  memory 写入 over')

        #step4 #get_nodeid_in_subtree
        logging.info('#step4  get_nodeid_in_subtree')
        nodeid_in_subtree = self.get_nodeid_in_subtree(self.sessionId, self.currentNodeId)
        self.nodeid_in_subtree = nodeid_in_subtree
        logging.info('#step4  get_nodeid_in_subtree')

        #step5 #summary_flag 判断
        logging.info(f'step5 #summary_flag 判断')
        self.summary_flag = self.gst.geabase_summary_check(self.sessionId, nodeid_in_subtree)
        logging.info(f'step5 over, summary_flag is {self.summary_flag}')

        #step5.1 #toolResponseError_flag 判断
        logging.info(f'step5 #toolResponseError_flag 判断')
        self.toolResponseError_flag = self.gst.toolResponseError_check(self.lingsi_response)
        logging.info(f'step5 over, toolResponseError_flag is {self.summary_flag}')
        
        #step 6 self.currentNodeId 更新 得到 start_nodetype
        logging.info(f'step 6 self.currentNodeId 更新 得到 start_nodetype')
        logging.info(f'currentNodeId is {self.currentNodeId }')
        if self.currentNodeId == None: #表示第一次输入
            logging.info(f'表示第一次输入')
            # last_intention_nodeid = self.intention_recognition_path[-1]
            # logging.info(f'last_intention_nodeid is {last_intention_nodeid}')
            # start_nodetype = search_node_type(nodeid_in_subtree, last_intention_nodeid )
            currentNodeId  = self.intention_recognition_path[-1]
            start_nodetype = 'opsgptkg_intent'
        else:
            logging.info(f'表示不是第一次输入')
            currentNodeId = self.currentNodeId
            start_nodetype = self.gst.search_node_type(nodeid_in_subtree, self.currentNodeId )
            self.start_nodetype = start_nodetype
        logging.info(f'start_nodetype is {start_nodetype}')
        logging.info(f'step 6 over')

        #step 7 执行QA  
        if self.queryPattern == 'qaPattern':
            logging.info(f'step 7 图谱扩散 执行qaPattern 开始')
            self.qaProcessRes = self.qaProcess(nodeid_in_subtree)
            logging.info(f'step 7 图谱扩散 执行qaPattern 结束')
        else:
            #step 8  图谱扩散
            logging.info(f'step 8 图谱扩散 开始')
            if self.algorithm_State == "REACT_EXECUTION_RESULT": # agent执行输入
                agent_respond = self.observation['toolResponse']
            elif self.algorithm_State == "TOOL_QUESTION_RETURN_ANSWER": # 人类agent的输入
                try:
                    agent_respond = self.observation['toolResponse']
                except:
                    agent_respond = self.userAnswer['toolResponse']
            else:
                agent_respond = None


                
            logging.info(f'图谱扩散的输入 self.sessionId {self.sessionId}; currentNodeId {currentNodeId}; start_nodetype {start_nodetype}')
            tool_plan, tool_plan_3 = self.gst.geabase_nodediffusion_plus(self.sessionId, 
currentNodeId,  start_nodetype, agent_respond  , self.lingsi_response)
            self.tool_plan = tool_plan
            self.tool_plan_3 = tool_plan_3
            logging.info(f'step 8 图谱扩散 over')


        #step 9 输出
        logging.info(f'step 9 输出')
        res_to_lingsi = self.outputFuc()
        logging.info(f'step 9 输出 over')

        

        return res_to_lingsi







def main(params_string,   memory_manager, geabase_handler, intention_router = None, llm_config=None):
   

    
        # 读取对应的传参和配置
        print(params_string)
        params      = params_string
        if type(params) == str:
            params = json.loads(params)
        logging.info(f'=======开始新一轮输入=============')
        logging.info(f'=======开始新一轮输入=============')
        logging.info(f'=======开始新一轮输入=============')
        logging.info(f'=======开始新一轮输入=============')
        logging.info(f'=======开始新一轮输入=============')
        logging.info(f'params={params}')
        logging.info(f'llm_config={llm_config}')

        lingsi_response = LingSiResponse(**params)
        lingsi_response = lingsi_response_process(lingsi_response) # process，currentnodeid 和 agentname都放到currentnodeid里，需要分割开来
        logging.info(f'lingsi_response is {lingsi_response}')
        #params = lingsi_response.dict()
        

        scene           = params.get('scene', None)
        sessionId       = params.get('sessionId', None) #
        #currentNodeId   = params.get('currentNodeId', None) #
        currentNodeId   = lingsi_response.currentNodeId
        observation     = params.get('observation', None) #
        userAnswer      = params.get('userAnswer', None) #
        inputType       = params.get('type', None) #
        startRootNodeId = params.get('startRootNodeId', None) #
        intentionRule   = params.get('intentionRule', None) #
        intentionData   = params.get('intentionData', None) #
        startFromRoot   = params.get('startFromRoot', True) #
        
        

        


        if scene  in ['WEREWOLF' , 'NEXA', 'UNDERCOVER', 
            'generalizationReasoning_nonretrieval', 'generalizationReasoning', 'WebAgent']:

            #标注这个sessionId属于新逻辑
            message = Message(
                chat_index= sessionId,  #self.sessionId
                message_index=  hash_id(sessionId, 'new'),  
                user_name = 'None',
                role_name = 'None', # agent 名字，
                role_type = 'None',
                role_content = 'new', # 第一次意图识别的输入
            )
            memory_manager.append(message)
            logging.info('调用新算法')
        elif scene in ['graphStructureSearch']:
            pass
            #交给后续逻辑判断
        else:
            #标注这个sessionId属于老逻辑
            message = Message(
                chat_index= sessionId,  #self.sessionId
                message_index=  hash_id(sessionId, 'old'),  
                user_name = 'None',
                role_name = 'None', # agent 名字，
                role_type = 'None', 
                role_content = 'old', # 第一次意图识别的输入
            )
            memory_manager.append(message)

            logging.info('调用老的算法逻辑')
            old_res = call_old_fuction(params_string)
            return old_res


    

        
        # abnormal_and_retry()



        if scene == 'graphStructureSearch' :
            
            '''
                graphStructure 模式下，需要判断 改sessionId 是否为 new，以区别是否调用新老算法
            '''
            memory_manager_res= memory_manager.get_memory_pool_by_all({ 
                                                        #    "chat_index": sessionId, 
                                                           "message_index" : hash_id(sessionId, 'new'),
                                                        #    "role_type": "nodeid_in_subtree",
                                                          })
            get_messages_res = memory_manager_res.get_messages()

            if get_messages_res != []:
                logging.info('调用新算法')
            else:
                logging.info('调用老的算法逻辑')
                old_res = call_old_fuction(params_string)
                return old_res


            logging.info(f'当前为graphStructureSearch模式')  
            gss = graph_structure_search( geabase_handler = geabase_handler, 
                memory_manager=memory_manager,  scene= scene, 
                sessionId=sessionId, currentNodeId = currentNodeId, 
                observation = observation, userAnswer = userAnswer, inputType = inputType, 
                index_name = 'ekg_migration_new', unique_name="EKG",
                llm_config=llm_config)
            res_to_lingsi = gss.process()

        else:
            logging.info(f'当前不为graphStructureSearch模式， 正常EKG')  

            # #重试逻辑，如果返回值 observation中没有toolresponse， 则进行重试
            # state, last_res_to_lingsi = abnormal_and_retry(inputType, observation, sessionId, memory_manager)
            # if state == 'retry_now':
            #     logging.info('现在进行重试，返回上一次在memory存储的结果')
            #     return last_res_to_lingsi



            gsp_entity = graph_search_process(
                geabase_handler = geabase_handler, 
                memory_manager=memory_manager, 
                intention_router = intention_router,
                lingsi_response = lingsi_response,
                scene= scene, 
                sessionId=sessionId, currentNodeId = currentNodeId, 
                observation = observation, userAnswer = userAnswer, inputType = inputType, 
                startRootNodeId = startRootNodeId,
                intentionRule   = intentionRule,
                intentionData   = intentionData,
                startFromRoot   = startFromRoot,
                index_name = 'ekg_migration_new', unique_name="EKG",
                llm_config=llm_config)

            res_to_lingsi = gsp_entity.process()

            save_res_to_memory(res_to_lingsi,  sessionId, memory_manager)


        return res_to_lingsi
    
    
def lingsi_response_process(lingsi_response:LingSiResponse)->LingSiResponse:
    '''
        # currentnodeid 和 agentname都放到currentnodeid里，需要分割开来
        # 是在agentname字段未上线的临时方案
        # 后续可以去除
    '''
    
    currentNodeId_add_agentName = lingsi_response.currentNodeId
    if currentNodeId_add_agentName == None:
        #不做任何处理
        return lingsi_response
    elif '%%@@#' not in currentNodeId_add_agentName:
        #lingsi_response.currentNodeId = lingsi_response.currentNodeId
        #lingsi_response.agentName = None
        return lingsi_response
    else:
        currentNodeId, agentName = currentNodeId_add_agentName.split('%%@@#')
        lingsi_response.currentNodeId = currentNodeId
        lingsi_response.agentName = agentName
    return lingsi_response

def save_res_to_memory(res_to_lingsi, sessionId, memory_manager):
    '''
        运行成功了， 保存结果，同时重置重试值
    '''
    if type(res_to_lingsi)!= str:
        res_to_lingsi = json.dumps(res_to_lingsi,  ensure_ascii=False)
    message = Message(
            chat_index= sessionId,  #self.sessionId
            message_index=  hash_id(sessionId, 'last_res_to_lingsi'),  
            user_name = 'None',
            role_name = 'None', # agent 名字，
            role_type = 'None', 
            role_content = res_to_lingsi, #上一次的结果
        )
    memory_manager.append(message)

    message = Message(
            chat_index= sessionId,  #self.sessionIdretry_num
            message_index=  hash_id(sessionId, 'retry_num'),  
            user_name = 'None',
            role_name = 'None', # agent 名字，
            role_type = 'None', 
            role_content = '0', #上一次的结果
        )
    memory_manager.append(message)

def abnormal_and_retry(inputType, observation, sessionId, memory_manager):
    '''
        异常和重试
    '''
    state = 'None'
    last_res_to_lingsi = 'None'
    if  type(observation) == str:
        observation = json.loads(observation)
    
    if inputType != None :
        if 'toolResponse' not in observation.keys():
            time.sleep(0.5) #沉睡0.5s
            logging.info('返回值异常，进行重试')
            logging.info('获取last_res_to_lingsi')
            #获取last_res_to_lingsi
            memory_manager_res= memory_manager.get_memory_pool_by_all({ 
                                                        #    "chat_index": sessionId, 
                                                           "message_index" : hash_id(sessionId, 'last_res_to_lingsi'),
                                                        #    "role_type": "nodeid_in_subtree",
                                                          })
            get_messages_res = memory_manager_res.get_messages()
            last_res_to_lingsi = get_messages_res[0].role_content
            last_res_to_lingsi = json.loads(last_res_to_lingsi)
            logging.info('相同的消息不用吐出两次')
            last_res_to_lingsi['userInteraction'] = None

            logging.info('获取retry_num')
            memory_manager_res= memory_manager.get_memory_pool_by_all({ 
                                                        #    "chat_index": sessionId, 
                                                           "message_index" : hash_id(sessionId, 'retry_num'),
                                                        #    "role_type": "nodeid_in_subtree",
                                                          })
            get_messages_res = memory_manager_res.get_messages()
            retry_num = int(get_messages_res[0].role_content)
            if retry_num >= 8:
                logging.info('超过了最大重试次数')
                state =  'Maximum number of retries exceeded'
                raise ValueError('超过了最大重试次数 ，退出')
                return state, last_res_to_lingsi
            else:
                logging.info('没有超过了最大重试次数，需要重试')
                state = 'retry_now'
                #重试值+1
                message = Message(
                chat_index= sessionId,  #self.sessionIdretry_num
                message_index=  hash_id(sessionId, 'retry_num'),  
                user_name = 'None',
                role_name = 'None', # agent 名字，
                role_type = 'None', 
                role_content = str(retry_num + 1), #重试值+1
                )
                memory_manager.append(message)
                return state, last_res_to_lingsi

        
        
        
        else:
            state = 'normal'
            return state, last_res_to_lingsi

    state = 'firstInput'
    return state, last_res_to_lingsi



if __name__ == '__main__':


    
    pass


#     