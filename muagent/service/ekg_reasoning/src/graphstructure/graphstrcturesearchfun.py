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



#内部其他函数
from src.utils.call_llm import call_llm,  extract_final_result
from src.geabase_handler.geabase_handlerplus import GB_handler
from src.utils.normalize import hash_id
from src.graph_search.geabase_search_plus import graph_search_tool
from src.intention_recognition.intention_recognition_tool import intention_recognition_ekgfunc, intention_recognition_querypatternfunc, intention_recognition_querytypefunc
from src.question_answer.qa_function import qa_class
#/ossfs/node_46264344/workspace/DevOpsEG_POC/src/question_answer/qa_function.py
from src.memory_handler.ekg_memory_handler import memory_handler_ekg
#/ossfs/node_46264344/workspace/DevOpsEG_POC/src/memory_handler/ekg_memory_handler.py
from src.graph_search.call_old_fuction import call_old_fuction



# # 配置logging模块
# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s - %(lineno)d', level=logging.INFO)









class graph_structure_search():
    def __init__(self,   geabase_handler, memory_manager,  scene , sessionId, currentNodeId, observation, 
            userAnswer, inputType, index_name = 'ekg_migration', unique_name="EKG",
            llm_config=None):
        self.memory_manager =  memory_manager #memory_init(index_name = 'ekg_migration', unique_name="EKG")

        self.gst = graph_search_tool(geabase_handler, self.memory_manager, llm_config=llm_config)
        # self.option  = option #geabase option
        # self.GeaBaseClient = GeaBaseClient
        self.scene = scene
        self.sessionId = sessionId
        self.currentNodeId = currentNodeId
        self.observation = observation
        if type(self.observation) == str:
            self.observation = json.loads(self.observation)
        
        self.userAnswer = userAnswer
        self.inputType = inputType
        self.gb_handler = GB_handler(geabase_handler)
    
    def getMemory(self, sessionId = 'TS_GOC_103346456601#1718525400799', rootNodeId = 'None',
             rootNodeType = 'opsgptkg_analysis'):
        '''
            根据sessionId ，rootNodeId 和 nodetype， 得到memory
            以如下形式记录， 下面是一个结论节点的例子
            {'role_type': 'analysis_res', 'role_name': 'None', 'role_content': '激活'}
        '''

        nodeId   =  rootNodeId
        nodeType =  rootNodeType
        logging.info(f'【查询】memory message_index {nodeId}; sessionId {sessionId} ; hash_id  {hash_id(nodeId, sessionId)}')

        if nodeType == 'opsgptkg_task':
            #先记录task的user
            
            memory_res = self.memory_manager.get_memory_pool_by_all({ 
                #  "message_index": hash_id(nodeId, sessionId), #nodeId.replace(":", "_").replace("-", "_"), 
                 "message_index": hash_id(nodeId, sessionId, f'_chapter1'), #nodeId.replace(":", "_").replace("-", "_"), 
                 "chat_index": sessionId, 
                 "role_type": "userinput"})
            message_res = memory_res.get_messages()
            if   len(message_res) > 1:
                #raise ValueError(f'对于{sessionId}对话的{nodeId}节点的tool执行结果查询出现了多个结果')
                pass
            elif len(message_res) == 0:
                #raise ValueError(f'对于{sessionId}对话的{nodeId}节点的tool执行结果查询没有找到结果')
                logging.info((f'对于{sessionId}对话的{nodeId}节点的user查询没有找到结果'))
                return None
            else:
                memory=({
                    "roleType": message_res[-1].role_type,
                    "roleName": message_res[-1].role_name,
                    "roleContent": message_res[-1].role_content})

            #再记录task的observation
            memory_res = self.memory_manager.get_memory_pool_by_all({ 
                "message_index": hash_id(nodeId, sessionId, '_chapter1'),# nodeId.replace(":", "_").replace("-", "_"), 
                "chat_index": sessionId, 
                "role_name": "function_caller", "role_type": "observation"})
            message_res = memory_res.get_messages()
            if   len(message_res) > 1:
                #raise ValueError(f'对于{sessionId}对话的{nodeId}节点的tool执行结果查询出现了多个结果')
                logging.info((f'对于{sessionId}对话的{nodeId}节点的user查询没有找到结果'))
                pass
            elif len(message_res) == 0:
                #raise ValueError(f'对于{sessionId}对话的{nodeId}节点的tool执行结果查询没有找到结果')
                logging.info((f'对于{sessionId}对话的{nodeId}节点的user查询没有找到结果'))
                memory = None
            else:
                memory=({
                    "roleType": message_res[-1].role_type,
                    "roleName": message_res[-1].role_name,
                    "roleContent": message_res[-1].role_content})



        elif nodeType == 'opsgptkg_intent':
            memory_res = self.memory_manager.get_memory_pool_by_all({
                "message_index": hash_id(nodeId, sessionId), #nodeId.replace(":", "_").replace("-", "_"), 
                 "chat_index": sessionId, 
                 "role_type": "user"})

            message_res = memory_res.get_messages()
            if   len(message_res) > 1:
                #raise ValueError(f'对于{sessionId}对话的{nodeId}节点的tool执行结果查询出现了多个结果')
                pass
            elif len(message_res) == 0:
                #raise ValueError(f'对于{sessionId}对话的{nodeId}节点的user查询没有找到结果')
                memory = None
                logging.info((f'对于{sessionId}对话的{nodeId}节点的user查询没有找到结果'))
            else:
                memory = ({
                    "roleType": message_res[-1].role_type,
                    "roleName": message_res[-1].role_name,
                    "roleContent": message_res[-1].role_content})

        elif nodeType == 'opsgptkg_phenomenon':
            memory_res = self.memory_manager.get_memory_pool_by_all({ 
                "message_index": hash_id(nodeId, sessionId),# nodeId.replace(":", "_").replace("-", "_"), 
                 "chat_index": sessionId, 
                 "role_type": "phenomenon_res"})
            message_res = memory_res.get_messages()
            if len(message_res) == 0:
                #raise ValueError(f'对于{sessionId}对话的{nodeId}节点的tool执行结果查询没有找到结果')
                logging.info((f'对于{sessionId}对话的{nodeId}节点的user查询没有找到结果'))
                memory = None
            else:
                memory=({
                    "roleType": message_res[-1].role_type,
                    "roleName": message_res[-1].role_name,
                    "roleContent": message_res[-1].role_content})

        elif nodeType == 'opsgptkg_analysis':
            print('hash_id(nodeId, sessionId)', hash_id(nodeId, sessionId))
            memory_res = self.memory_manager.get_memory_pool_by_all({ 
                "message_index": hash_id(nodeId, sessionId), #nodeId.replace(":", "_").replace("-", "_"), 
                 "chat_index": sessionId, 
                 #"role_type": "analysis_res",
                 })
            message_res = memory_res.get_messages()
            if len(message_res) == 0:
                #raise ValueError(f'对于{sessionId}对话的{nodeId}节点的tool执行结果查询没有找到结果')
                logging.info((f'对于{sessionId}对话的{nodeId}节点的opsgptkg_analysis查询没有找到结果'))
                memory = None
            else:
                memory=({
                    "roleType": message_res[-1].role_type,
                    "roleName": message_res[-1].role_name,
                    "roleContent": message_res[-1].role_content})

        elif nodeType == 'opsgptkg_schedule':
            #return None
            memory=({
                    "roleType": '执行',
                    "roleName": '执行',
                    "roleContent": '执行'})
            return memory

        else: #意料之外的节点格式
            return None
        return memory
    
    def format_conversion(self, res_to_lingsi):

        res_to_lingsi_dict = {'nodes':{}, 'edges':{}}

        nodes_dict = {}
        for i in range(len(res_to_lingsi['nodes'])):

            key = res_to_lingsi['nodes'][i]['nodeId']

            
            if res_to_lingsi['nodes'][i]['nodeType'] == 'opsgptkg_analysis':
                if res_to_lingsi['nodes'][i]['toolResponse'] == None:
                    pass
                elif res_to_lingsi['nodes'][i]['toolResponse']['roleContent'] != '激活':
                    res_to_lingsi['nodes'][i]['toolResponse'] = None

                elif self.gst.geabase_judgeNodeReachability( sessionId = self.sessionId, 
                                    start_nodeid = res_to_lingsi['nodes'][i]['nodeId'], 
                                    start_nodetype = 'opsgptkg_analysis') ==False:

                # elif  geabase_judgeAnalysisReachability(option = self.option,  GeaBaseClient = self.GeaBaseClient,
                #                 memory_manager = self.memory_manager, sessionId = self.sessionId, 
                #                     start_nodeid = res_to_lingsi['nodes'][i]['nodeId'], start_nodetype = 'opsgptkg_analysis') == False:
                    
                    logging.info(f'nodeid {key} 的可达性判断为False')
                    res_to_lingsi['nodes'][i]['toolResponse'] = None
                else:
                    if res_to_lingsi['nodes'][i]['name'] != res_to_lingsi['nodes'][i]['description']:
                         res_to_lingsi['nodes'][i]['toolResponse']['roleContent'] = res_to_lingsi['nodes'][i]['name'] + res_to_lingsi['nodes'][i]['description']
                    else:
                        res_to_lingsi['nodes'][i]['toolResponse']['roleContent'] = res_to_lingsi['nodes'][i]['description']
            
            if res_to_lingsi['nodes'][i]['nodeType'] == 'opsgptkg_phenomenon':
                if res_to_lingsi['nodes'][i]['toolResponse'] == None:
                    pass
                elif res_to_lingsi['nodes'][i]['toolResponse']['roleContent'] != '选中':
                     res_to_lingsi['nodes'][i]['toolResponse'] = None

                else:
                    if res_to_lingsi['nodes'][i]['name'] != res_to_lingsi['nodes'][i]['description']:
                        res_to_lingsi['nodes'][i]['toolResponse']['roleContent'] = res_to_lingsi['nodes'][i]['name'] + res_to_lingsi['nodes'][i]['description']
                    else:
                        res_to_lingsi['nodes'][i]['toolResponse']['roleContent'] = res_to_lingsi['nodes'][i]['description']

            nodes_dict[key] = {
                'nodeType':res_to_lingsi['nodes'][i]['nodeType'],
                'name':res_to_lingsi['nodes'][i]['name'],
                'description':res_to_lingsi['nodes'][i]['description'],
                'toolResponse':res_to_lingsi['nodes'][i]['toolResponse']       , 
            }
        edges_dict = {}
        for i in range(len(res_to_lingsi['edges'])):
            key = f'edge_{i}'
            edges_dict[key] = {
                "startNodeId": 	res_to_lingsi['edges'][i]['startNodeId'] ,
                "endNodeId": 	res_to_lingsi['edges'][i]['endNodeId'] ,
            }    



        
        res_to_lingsi_dict = {'nodes':nodes_dict, 'edges':edges_dict}
        return res_to_lingsi_dict

    def process(self):
        nodes = []
        edges = []

        #只展示灰色图结构，不展示运行态结果
        print(self.sessionId)
        print('=========================')
        if self.sessionId.startswith('___') == True: #约定好的情况，以___开头，即只展示灰色图结构，不展示运行态结果
            input_info = self.sessionId[3:]
            intent_nodeid = input_info.split('##__##')[0]
            try:
                intent_nodetype = input_info.split('##__##')[1]
            except:
                intent_nodetype = 'opsgptkg_intent'
            self.intent_nodeid = intent_nodeid
            self.sessionId = 'None' #sessionId 之后就没用了，放置其中有特殊字符导致tbase查询出错
        else:
            #1 检索nodeid_in_subtree
            logging.info(f'1 检索nodeid_in_subtree')
            memory_manager_res= self.memory_manager.get_memory_pool_by_all({  "chat_index": self.sessionId, 
                                                            "role_type": "nodeid_in_subtree",
                                                            })
            get_messages_res = memory_manager_res.get_messages()
            nodeid_in_subtree = json.loads( get_messages_res[0].role_content)
            logging.info(f'1 nodeid_in_subtree 里的节点个数为{len(nodeid_in_subtree)}')

            #2 找到intent 节点
            logging.info(f'2 找到intent 节点')
            for i in range(len(nodeid_in_subtree)):
                if nodeid_in_subtree[i]['nodeType'] == 'opsgptkg_intent':
                    intent_nodeid =  nodeid_in_subtree[i]['nodeId']
                    break
            self.intent_nodeid = intent_nodeid

        #3 从intent节点开始扩散，把边的信息构建出来
        logging.info(f'3 从intent节点开始扩散，把边的信息构建出来')
        nodeid_in_subtree_add, edge_in_subtree = self.gb_handler.geabase_search_return_all_nodeandedge( start_nodeid = self.intent_nodeid, 
        start_nodetype = 'opsgptkg_intent', block_search_nodetype = [])


        logging.info(f'3 nodeid_in_subtree_add 里的节点个数为{len(nodeid_in_subtree_add)}')
        logging.info(f'3 nodeid_in_subtree_add 为{(nodeid_in_subtree_add)}')

        #4 对节点的信息做填充
        logging.info(f'4 对节点的信息做填充')
        #nodeid_in_subtree_add_copy = copy.copy(nodeid_in_subtree_add)
        for i in range(len(nodeid_in_subtree_add)):
            nodeId   =  nodeid_in_subtree_add[i]['nodeId']
            nodeType =  nodeid_in_subtree_add[i]['nodeType']
            if nodeid_in_subtree_add[i]['nodeDescription'] == None:
                nodeid_in_subtree_add[i]['description'] = self.gb_handler.geabaseGetOnlyOneNodeInfoWithKey(rootNodeId = nodeId, rootNodeType = nodeType, key = 'description')
            else:
                nodeid_in_subtree_add[i]['description'] = nodeid_in_subtree_add[i]['nodeDescription']

            if nodeid_in_subtree_add[i]['nodeName'] == None:
                nodeid_in_subtree_add[i]['name'] = self.gb_handler.geabaseGetOnlyOneNodeInfoWithKey(rootNodeId = nodeId, rootNodeType = nodeType, key = 'name')
            else:
                nodeid_in_subtree_add[i]['name'] = nodeid_in_subtree_add[i]['nodeName']
            nodeid_in_subtree_add[i]['toolResponse'] = self.getMemory(sessionId = self.sessionId, rootNodeId = nodeId, rootNodeType = nodeType)

        #5 最终结果
        logging.info(f'#5 最终结果')
        res = {"nodes" : nodeid_in_subtree_add, 'edges':edge_in_subtree}

        # 6 格式转换
        logging.info(f'#6 格式转换')
        res = self.format_conversion(res)
        return res
        

def main(params_string,  geabase_handler, memory_manager):
   

    
        # 读取对应的传参和配置
        print(params_string)
        params      = params_string
        if type(params) == str:
            params = json.loads(params)
        logging.info(f'params={params}')


        scene           = params.get('scene', None)
        sessionId       = params.get('sessionId', None) #
        currentNodeId   = params.get('currentNodeId', None) #
        observation     = params.get('observation', None) #
        userAnswer      = params.get('userAnswer', None) #
        inputType       = params.get('type', None) #

        if scene == 'graphStructureSearch' :
            gss = graphStructureSearch( 
            memory_manager=memory_manager, sessionId=sessionId)
            res_to_lingsi = gsp_entity.process()

        else:
            gsp_entity = graph_search_process( geabase_handler = geabase_handler,
                memory_manager=memory_manager, scene= scene, 
                sessionId=sessionId, currentNodeId = currentNodeId, 
                observation = observation, userAnswer = userAnswer, inputType = inputType, index_name = 'ekg_migration', unique_name="EKG")

        res_to_lingsi = gsp_entity.process()


        return res_to_lingsi


if __name__ == '__main__':

    pass