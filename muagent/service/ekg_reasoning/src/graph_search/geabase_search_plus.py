# -*- coding: utf-8 -*-
#此代码为在aistudio上运行的代码

#路径增加
import sys
import os
import re
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
import logging
import copy
import sys
import os,  base64
from loguru import logger
import uuid



#muagent 依赖包
from muagent.connector.schema import Message
from muagent.schemas.db import TBConfig
from muagent.db_handler import *
from muagent.connector.memory_manager import TbaseMemoryManager
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.schemas.db import GBConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.service.ekg_inference import IntentionRouter

# from loguru import logger as logging
from src.utils.call_llm import call_llm,  extract_final_result , robust_call_llm
from src.geabase_handler.geabase_handlerplus import GB_handler
from src.utils.normalize import hash_id
from src.memory_handler.ekg_memory_handler import memory_handler_ekg
from src.graph_search.task_node_agent import TaskNodeAgent






class graph_search_tool():
    '''
        在图谱推理过程中使用到的一些 tool / function
        需要同时 使用memory and geabase，   或者都不使用
    '''
    def __init__(self, geabase_handler, memory_manager, llm_config=None):
        self.geabase_handler = geabase_handler
        self.memory_manager  = memory_manager
        self.gb_handler = GB_handler(self.geabase_handler) #gb_handler 以  geabase_handler 为基础，封装了一些处理逻辑
        self.memory_handler  = memory_handler_ekg(memory_manager, geabase_handler)
        self.llm_config = llm_config
        self.task_node_agent = TaskNodeAgent(self.geabase_handler, self.memory_manager, self.llm_config)
 
    
    def search_node_type(self, nodeid_in_subtree, nodeId ):
        '''
            #返回nodeid_in_subtree 中 nodeId 的nodeType
            # 根据nodeId， 返回其nodetype。但是假设在有了nodeid_in_subtree的情况下
        '''
        for i in range(len(nodeid_in_subtree)):
            if nodeid_in_subtree[i]['nodeId'] == nodeId:
                return nodeid_in_subtree[i]['nodeType']
        return 'not found'

    def geabase_judgeNodeReachability(self,  sessionId, 
            start_nodeid = 'None', start_nodetype = 'opsgptkg_task'):
        '''
        #判断这个 nodeid对应的tool 是否可达, 即他的父辈节点是否都执行完了
        '''
        gb_handler = self.gb_handler
        tool_parent = []
        nodeid_in_search = [{'nodeId':start_nodeid, 'nodeType':start_nodetype}]

        while len(nodeid_in_search)!= 0:
            nodedict_now = nodeid_in_search.pop()
            nodeid_now      = nodedict_now['nodeId']
            nodetype_now    = nodedict_now['nodeType']
            #nodetype   = 'opsgptkg_intent'
            # iso_gql = "MATCH (n0:%s)<-[e]-(n1) WHERE n0.id = '%s' RETURN n1.id,n1.@node_type,n1.description"%(nodetype_now, nodeid_now)
            # #print('iso_gql', iso_gql)
            # res = GeaBaseClient.executeGQL(iso_gql, option)
            # res = json.loads(str(res.getJsonGQLResponse()))

            neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes={"id": nodeid_now,}, node_type=nodetype_now, reverse=True)
            #print('res', res)
            # if 'resultSet' not in res.keys():
            #     continue

            for i in range(len(neighborNodes) ):
                # if  res['resultSet']['rows'][i]['columns'][0] == {}:
                #     continue
                # else:
                    nodeid_new = neighborNodes[i].id
                    nodetype_new = neighborNodes[i].type
                    if nodetype_new == 'opsgptkg_task' or nodetype_new == 'opsgptkg_phenomenon':  #如果是task 或者 phenomenon节点，则加入到tool_plan中，但是不往后续延展了。
                        tool_parent.append({'nodeId':nodeid_new, 'nodeType': nodetype_new})
                    elif nodetype_new == 'opsgptkg_intent':
                        #向前追述到了意图节点，终止
                        pass

                    else:##如果是不是task节点，也不是意图节点，不加入到tool_plan中，往后续延展
                        nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
        
        #tool_parent = list(set(tool_parent))
        # 将字典转化为元组，然后放入set中去重
        unique_set = set(tuple(d.items()) for d in tool_parent)
        # 再将元组转回字典
        tool_parent = [{k: v for k, v in t} for t in unique_set]

        node_description = self.gb_handler.geabase_getDescription( rootNodeId = start_nodeid, rootNodeType = start_nodetype)

        if gb_handler.geabaseGetOnlyOneNodeInfoWithKey( rootNodeId = start_nodeid, rootNodeType = start_nodetype,key = 'accesscriteria') == 'AND' \
            or gb_handler.geabaseGetOnlyOneNodeInfoWithKey( rootNodeId = start_nodeid, rootNodeType = start_nodetype,key = 'accesscriteria') == '{"type":"AND"}' \
            or gb_handler.geabaseGetOnlyOneNodeInfoWithKey( rootNodeId = start_nodeid, rootNodeType = start_nodetype,key = 'accesscriteria') == None or \
            gb_handler.geabaseGetOnlyOneNodeInfoWithKey( rootNodeId = start_nodeid, rootNodeType = start_nodetype,key = 'accesscriteria') == '':
            logging.info('#此节点为and处理逻辑')
            #此节点为and处理逻辑
            logging.info(f'{start_nodeid}的tool_parent为{tool_parent}')
            for nodeDict in tool_parent:
                nodeId = nodeDict['nodeId']
                nodeid = nodeId
                nodeType = nodeDict['nodeType']
                if nodeType  == 'opsgptkg_task':
                    # memory_res = self.memory_manager.get_memory_pool_by_all({ 
                    #     "message_index": hash_id(nodeId, sessionId), # nodeId.replace(":", "_").replace("-", "_"), 
                    #     "chat_index": sessionId, "role_name": "function_caller", "role_type": "observation"})
                    # message_res = memory_res.get_messages()
                    # if message_res == []:
                    #     return False     #只要有一个节点没有observation，即不可达
                    message_res = self.memory_handler.nodecount_get( sessionId, nodeid)  #查看这个节点的count计数
                    if message_res == []:
                        return False
                elif nodeType  == 'opsgptkg_phenomenon': #对于 opsgptkg_phenomenon 只维护一个最新的记忆
                    memory_res = self.memory_manager.get_memory_pool_by_all({ 
                        "message_index": hash_id(nodeid, sessionId), # nodeId.replace(":", "_").replace("-", "_"), 
                        "chat_index": sessionId})
                    message_res = memory_res.get_messages()
                    if message_res == [] or message_res[0].input_query != '选中':
                        return False     #只要有一个节点没有observation，即不可达
                else:
                    raise ValueError(f'geabase_judgeNodeReachability 是出现意料之外的nodetype: {nodeType}')
            return True
        else:#此节点为or处理逻辑
            logging.info('#此节点为or处理逻辑')
            logging.info(f'{start_nodeid}的tool_parent为{tool_parent}')
            for nodeDict in tool_parent:
                nodeId = nodeDict['nodeId']
                nodeid = nodeId
                nodeType = nodeDict['nodeType']
                if nodeType  == 'opsgptkg_task':
                    # memory_res = self.memory_manager.get_memory_pool_by_all({ 
                    #     "message_index": hash_id(nodeId, sessionId), #nodeId.replace(":", "_").replace("-", "_"), 
                    #     "chat_index": sessionId, "role_name": "function_caller", "role_type": "observation"})
                    # message_res = memory_res.get_messages()
                    # if message_res != []:
                    #     return True     #只要有一个节点有observation，可达

                    message_res = self.memory_handler.nodecount_get( sessionId, nodeId)  #查看这个节点的count计数
                    if message_res != []:
                        return True
                elif nodeType  == 'opsgptkg_phenomenon': #对于 opsgptkg_phenomenon 只维护一个最新的记忆，在判断可达性时，可能会读取到上一次的状态。有可能会有问题
                    memory_res = self.memory_manager.get_memory_pool_by_all({ 
                        "message_index": hash_id(nodeid, sessionId), # nodeId.replace(":", "_").replace("-", "_"), 
                        "chat_index": sessionId})
                    message_res = memory_res.get_messages()
                    if message_res != [] and message_res[0].input_query == '选中':
                        return True     #只要有一个节点有observation，可达
                else:
                    raise ValueError(f'geabase_judgeNodeReachability 是出现意料之外的nodetype: {nodeType}')
            return False


    




    def subintention_option_generation(self, neighbor_node_description_list = ['a','b','c'] , 
            neighbor_node_id_list =['id_a','id_b','id_c'] ):
        ## 在子意图确认环节，生成内部可以处理的数据结构 inner_option 和 写在prompt里大模型看的chatbot_prompt_option

        chatbot_prompt_option = ''



    def subintention_option_generation(self, neighbor_node_description_list = ['a','b','c'] , 
            neighbor_node_id_list =['id_a','id_b','id_c'] ):
        ## 在子意图确认环节，生成内部可以处理的数据结构 inner_option 和 写在prompt里大模型看的chatbot_prompt_option

        chatbot_prompt_option = ''
        inner_option = {}
        # if len(neighbor_node_description_list)>26:
        #     raise ValueError("子意图太多，超过了26个")
        # def generate_alphabet_list(n):
        #     if n>26:
        #         raise ValueError("子意图太多，超过了26个")
        #     return [chr(i) for i in range(65, 65 + n)]
        for i in range(len(neighbor_node_id_list)):
            chatbot_prompt_option = chatbot_prompt_option  + chr(i+65) + ' '+ neighbor_node_description_list[i] + '; '
            inner_option[chr(i+65)] = {'description': neighbor_node_description_list[i],  'node_id': neighbor_node_id_list[i]}
        
        #新增一个以上情况均不满足的情况
        i = i + 1 
        chatbot_prompt_option   = chatbot_prompt_option  + chr(i+65) + ' '+ '以上情况均不满足' + '; '
        inner_option[chr(i+65)] = {'description': '以上情况均不满足',  'node_id': 'virtual_terminal_node'}

        return chatbot_prompt_option, inner_option

    def fact_branch_judgment(self, current_task, neighbor_node_id_list, next_node_description_list, observation='None'):
        #执行 分支事实判断的逻辑
        #print('next_node_description_list',next_node_description_list)
        chatbot_prompt_option, inner_option = self.subintention_option_generation(neighbor_node_description_list = next_node_description_list , 
               neighbor_node_id_list = neighbor_node_id_list )
        #print('chatbot_prompt_option',chatbot_prompt_option)

        prompt_temp = \
            f'''
            你是一个计算机开发运维领域的专家，现在有一个状态确认问题，需要根据当前的task，和执行完task后的observation，判断现在所处的状态。
            请结合子状态选项， 用 最终结果：【选项】 的格式作为结尾。thought的思考一定要简略，尽量不要超过40个字。
            以下是几个例子：
            -------
            task：判断失败数是否正常。如果当前失败数大于等于八十，则失败数异常；否则，失败数正常
            observation：当前失败数为48
            子状态选项是：A 失败数异常; B 失败数正常
            thought(尽量不要超过40个字)：当前失败数为48，48小于80，所以现在的状态是失败数正常。
            最终结果为：B
            -------
            task：判断现在水温是否偏高
            observation："result":"是\n","exeSuccess":true
            子状态选项是：A 是; B 否
            thought(尽量不要超过40个字)：根据observation的结果，result为 是， 表示肯定的结果， 因此结果选A
            最终结果为：A
            -------
            task：{current_task}
            observation：{observation}
            子状态选项是：{chatbot_prompt_option}
            thought(尽量不要超过40个字)：
            '''
        logging.info(prompt_temp)
        response = call_llm(input_content = prompt_temp, llm_model = 'default' , llm_config=self.llm_config)# qwen_chat_14b #Qwen_72B_Chat_vLLM
        logging.info(f'大模型的结果为：{response}')
        #final_choice =  extract_final_result(json.loads(response.text)['data'], special_str = "最终结果为：" )
        final_choice =  extract_final_result(response, special_str = "最终结果为：" )

        if final_choice == 'Substring not found':
            #raise ValueError("大模型进行分支事实判断时，没有按标准输出选项结果")
            logging.info("大模型进行分支事实判断时，没有按标准输出选项结果。")
            raise ValueError(f'大模型进行分支事实判断时，没有按标准输出选项结果。  大模型的输出为{final_choice}')
            #return next_node_description_list[0]

        next_nodeid = inner_option[final_choice]['node_id']
        return next_nodeid
    def write_phenomenon_memory(self, sessionId, neighbor_node_id_list, chosen_nodeid):
            logging.info(f'neighbor_node_id_list is{neighbor_node_id_list}, chosen_nodeid is {chosen_nodeid} ')
            for nodeid in neighbor_node_id_list:
                if nodeid == chosen_nodeid:
                    message = Message(
                    chat_index= sessionId,
                    #message_index=  nodeid.replace(":", "_").replace("-", "_") + f"-{uuid.uuid4()}",
                    message_index=  hash_id(nodeid, sessionId, '-phenomenon'), #nodeid.replace(":", "_").replace("-", "_") + '-phenomenon' ,
                    #message_index= f"{nodeid}-{uuid.uuid4()}".replace(":", "_").replace("-", "_"),
                    user_name = "None",
                    role_name = "None", # agent 名字，
                    role_type = "phenomenon_res", # agent 类型，默认assistant，可选observation
                    ## llm output
                    role_content = "选中", # 输入
                    )

                    self.memory_manager.append(message)
                else:
                    message = Message(
                    chat_index= sessionId,
                    #message_index=  nodeid.replace(":", "_").replace("-", "_") + f"-{uuid.uuid4()}",
                    #message_index= f"{nodeid}-{uuid.uuid4()}".replace(":", "_").replace("-", "_"),
                    message_index=  hash_id(nodeid, sessionId, '-phenomenon'), #nodeid.replace(":", "_").replace("-", "_") + '-phenomenon',
                    user_name = "None",
                    role_name = "None", # agent 名字，
                    role_type = "phenomenon_res", # agent 类型，默认assistant，可选observation
                    ## llm output
                    role_content = "未选中", # 输入
                    )

                    self.memory_manager.append(message)
            return 1

    def write_analysis_memory(self, sessionId, neighbor_node_id_list, chosen_nodeid):
        for nodeid in neighbor_node_id_list:
            #print(nodeid, sessionId)
            if nodeid == chosen_nodeid or  chosen_nodeid == None:
                message = Message(
                chat_index= sessionId,
                #message_index=  nodeid.replace(":", "_").replace("-", "_") + f"-{uuid.uuid4()}",
                #message_index= f"{nodeid}-{uuid.uuid4()}".replace(":", "_").replace("-", "_"),
                message_index=  hash_id(nodeid, sessionId, '-analysis'), #nodeid.replace(":", "_").replace("-", "_") + '-analysis',
                user_name = "None",
                role_name = "None", # agent 名字，
                role_type = "analysis_res", # agent 类型，默认assistant，可选observation
                ## llm output
                role_content = "激活", # 输入
                )

                self.memory_manager.append(message)
            else:
                message = Message(
                chat_index= sessionId,
                #message_index=  nodeid.replace(":", "_").replace("-", "_") + f"-{uuid.uuid4()}",
                #message_index= f"{nodeid}-{uuid.uuid4()}".replace(":", "_").replace("-", "_"),
                message_index=  hash_id(nodeid, sessionId, '-analysis'), # nodeid.replace(":", "_").replace("-", "_") +'-analysis',
                user_name = "None",
                role_name = "None", # agent 名字，
                role_type = "analysis_res", # agent 类型，默认assistant，可选observation
                ## llm output
                role_content = "未激活", # 输入
                )

                self.memory_manager.append(message)
        return 1

    



    def geabase_summary_check(self, sessionId, nodeid_in_subtree):
        logging.info('geabase_summary_check start 判断当前状态下是不是已经走到了需要进行summary的情况')
        # 判断当前状态下是不是已经走到了需要进行summary的情况
        
        #从nodeid_in_subtree获取叶子意图节点
        for i in range(len(nodeid_in_subtree)):
            start_nodeid    = nodeid_in_subtree[i]['nodeId']
            start_nodetype  = nodeid_in_subtree[i]['nodeType']
            if start_nodetype == 'opsgptkg_intent':
                break
        
        check_tool_plan = []
        nodeid_in_search = [{'nodeId':start_nodeid, 'nodeType':start_nodetype}]
        nodeid_in_search_all = []

        #进行探索
        while len(nodeid_in_search)!= 0:
                nodedict_now = nodeid_in_search.pop()
                nodeid_now      = nodedict_now['nodeId']
                nodetype_now    = nodedict_now['nodeType']
 
                neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes={"id": nodeid_now,}, node_type=nodetype_now, reverse=False)
 
                # if 'resultSet' not in res.keys():
                #     #logging.info('后续为空,continue')
                #     #后续为空
                #     continue

                if self.gb_handler.all_nodetype_check(rootNodeId = nodeid_now, rootNodeType = nodetype_now, 
        neighborNodeType = 'opsgptkg_phenomenon') == True:
                    #后续所有节点都是判断节点, 依次判断这些节点是否已经激活选中
                    neighbor_node_id_list       = self.gb_handler.get_children_id(nodeid_now, nodetype_now)
                    #next_node_description_list  = get_nodedescription_from_res(res)

                    for nnode_id in neighbor_node_id_list:
                        memory_res = self.memory_manager.get_memory_pool_by_all({ 
                            "message_index": hash_id(nnode_id, sessionId), #nnode_id.replace(":", "_").replace("-", "_"), 
                            "chat_index": sessionId, 
                            "role_type": "phenomenon_res"})
                        message_res = memory_res.get_messages()
                        if message_res == []:
                            #logging.info(f'判断summary条件， 事实节点{nnode_id}没有探索到，不再进行后续探索 ')
                            continue
                        
                        #logging.info(f'message_res[-1].role_content is  {message_res[-1].role_content}')
                        elif message_res[-1].role_content != '选中': # 这个事实节点没有激活
                            #logging.info(f'判断summary条件， 事实节点{nnode_id} 没有激活, 不再进行后续探索 ')
                            continue

                        logging.info(f'判断summary条件， 事实节点{nnode_id} 被选中激活, 进行后续探索 ')
                        
                        if {'nodeId':nnode_id, 'nodeType':'opsgptkg_phenomenon'} in nodeid_in_search_all:
                            continue 
                        else:
                            nodeid_in_search_all.append({'nodeId':nnode_id, 'nodeType':'opsgptkg_phenomenon'})
                            nodeid_in_search.append({'nodeId':nnode_id, 'nodeType':'opsgptkg_phenomenon'})

                # elif all_analysis_check(res) == True:#是否后续所有节点均为analysis，一般只有analysis是单个出现
                elif self.gb_handler.all_nodetype_check(rootNodeId = nodeid_now, rootNodeType = nodetype_now, 
        neighborNodeType = 'opsgptkg_analysis') == True:
                    #扩散到了结论节点, 均往后扩展
                    #写memory，write_analysis_memory，
                    neighbor_node_id_list       = self.gb_handler.get_children_id(nodeid_now, nodetype_now)  #取后续事实节点，假设事实节点一定只有一个
                    logging.info(f'neighbor_node_id_list is  {neighbor_node_id_list}, ')
                    # self.write_analysis_memory( sessionId, neighbor_node_id_list, None)
                    #继续往后面扩散，虽然大概率后面为空
                    for i in range(len(neighbor_node_id_list)):
                        if {'nodeId':neighbor_node_id_list[i], 'nodeType':'opsgptkg_analysis'} in nodeid_in_search_all:
                            continue 
                        else:
                            nodeid_in_search_all.append({'nodeId':neighbor_node_id_list[i], 'nodeType':'opsgptkg_analysis'})
                            nodeid_in_search.append({'nodeId':neighbor_node_id_list[i], 'nodeType':'opsgptkg_analysis'})



                else:
                    for i in range(len( neighborNodes ) ):
                        # if  res['resultSet']['rows'][i]['columns'][0] == {}:
                        #     # Geabase的bug
                        #     continue
                        # else:
                            nodeid_new = neighborNodes[i].id
                            nodetype_new = neighborNodes[i].type
                            if nodetype_new == 'opsgptkg_task':  #如果是task节点，则加入到tool_plan中，同时往后续延展了。
                                check_tool_plan.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})

                                if {'nodeId':nodeid_new, 'nodeType':nodetype_new} in nodeid_in_search_all:
                                    continue #重复了，有环
                                else:
                                    nodeid_in_search_all.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                                    nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})

                            else: ##如果是不是task节点，不加入到tool_plan中，往后续延展
                                # nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                                if {'nodeId':nodeid_new, 'nodeType':nodetype_new} in nodeid_in_search_all:
                                    continue 
                                else:
                                    nodeid_in_search_all.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                                    nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})

        unique_set = set(tuple(sorted(d.items())) for d in check_tool_plan)
        # 将去重后的元组转换回字典形式，得到去重后的list
        check_tool_plan = [dict(t) for t in unique_set]

        for i in range(len(check_tool_plan)):

            nodeId      = check_tool_plan[i]['nodeId']
            nodeType    = check_tool_plan[i]['nodeType']
            if nodeType == 'opsgptkg_task':# 只有opsgptkg_task 节点才有obsevation
                # memory_res = self.memory_manager.get_memory_pool_by_all({ 
                #     "message_index": hash_id(nodeId, sessionId), #nodeId.replace(":", "_").replace("-", "_"), 
                #     "chat_index": sessionId, "role_name": "function_caller", "role_type": "observation"})
                # message_res = memory_res.get_messages()
                message_res = self.memory_handler.nodecount_get( sessionId, nodeId)  #查看这个节点的count计数
                if message_res == []:
                    logging.info(f'geabase_summary_check end 只要有一个opsgptkg_task节点{nodeId}没有observation，即不能summary')
                    return False     #只要有一个节点没有observation，即不能summary
        
        logging.info('geabase_summary_check end 所有task节点都有observation，则需要summary')
        return True #所有task节点都有observation，则需要summary


   

    def geabase_nodediffusion_plus(self,  sessionId, 
            start_nodeid = 'complaint', start_nodetype = 'opsgptkg_intent',  
            agent_respond = None, lingsi_response = None):
        '''
            增加了react模块的逻辑
            进行单步的向后扩散， 得到下一步应该执行的计划
        '''
        logging.info('===================================')
        logging.info('===================================')
        logging.info('================geabase_nodediffusion_plus start===================')
        logging.info('===================================')
        logging.info('===================================')
        # 0 创建 GB_handler的实例
        gb_handler = self.gb_handler
        self.memory_handler = memory_handler_ekg(self.memory_manager, self.geabase_handler)


        # 1 判断当前节点是否执行完。 如果是tool task节点，肯定执行完了， 如果是react task节点，肯定没执行完
        logging.info('判断当前节点是否执行完。 如果是tool task节点，肯定执行完了， 如果是react task节点，肯定没执行完, 如果是其他类型的节点，也是执行完了')
        node_completed_flag = self.memory_handler.is_nodetask_completed(sessionId ,start_nodeid, start_nodetype)
        
        if self.gb_handler.geabase_is_react_node(start_nodeid, start_nodetype) == False:
            node_completed_flag = True #这里表示 对于tool类型的task节点， 只要得到了返回值，就能认为执行完毕了。因为一个tool节点只会执行一次
            # self.memory_handler.init_react_count( sessionId, start_nodeid) #  对于task tool节点，这次是得到了返回值。需要对count进行初始化，或者 chapter+1

        if node_completed_flag == False: #没有执行完，需要继续执行
            #
            logging.info(f'类react节点{start_nodeid}没有执行完，需要继续执行')
            runningFlag, reactPlan = self.task_node_agent.task_running(sessionId, start_nodeid, start_nodetype, lingsi_response )

            #继续执行还是没有执行完
            if runningFlag == 'waiting_other_agent':
                logging.info('继续执行还是没有执行完')
                logging.info('后面还是需要运行这个节点，无需进行后续探索。tool_plan就是这个节点了')
                #表示后面还是需要运行这个节点，无需进行后续探索。tool_plan就是这个节点了
                tool_plan = [{'nodeId':start_nodeid, 'nodeType':start_nodetype}] #还是执行这个tool
                tool_return_plan= reactPlan            
                return tool_plan, tool_return_plan
            else:
                logging.info('继续执行,执行完了, 向后探索')
            
        
        logging.info(f'判断当前节点{start_nodeid}为执行完了， 往后探索')
        #进入这里有两种情况
        #1 一开始这个节点已经运行结束了，需要往后面进行探索。 tool 节点，或者其他类型节点
        #2 一开始这个节点还在执行，但是这次返回是它的最后一次执行，到end，执行完了。 react 节点


        #1.假设当前节点已经运行完，得到后面的tool. 如果为事实节点，则需要采用大模型进行判断, 如果为react节点，需要runing react模块
        tool_plan = []
        nodeid_in_search = [{'nodeId':start_nodeid, 'nodeType':start_nodetype}]

        while len(nodeid_in_search)!= 0:
            nodedict_now = nodeid_in_search.pop()
            nodeid_now      = nodedict_now['nodeId']
            nodetype_now    = nodedict_now['nodeType']

            neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes={"id": nodeid_now,}, node_type=nodetype_now, reverse=False)
            
            if self.gb_handler.all_nodetype_check(rootNodeId = nodeid_now, rootNodeType = nodetype_now, 
        neighborNodeType = 'opsgptkg_phenomenon') == True:
                #后续所有节点都是判断节点, 则进行大模型判断，选中其中一个 phenomenon 进入后续，同时在phenomenons节点上记录memory
                logging.info(f'##后续所有节点都是判断节点, 则进行大模型判断，选中其中一个 phenomenon 进入后续，同时在phenomenons节点上记录memory')
                neighbor_node_id_list       =self.gb_handler.get_children_id(nodeid_now, nodetype_now)
                next_node_description_list  = self.gb_handler.get_children_description(nodeid_now, nodetype_now)
                #logging.info(f'nodeid_now {nodeid_now}')
                observation = self.memory_handler.get_nodeobservation_current(  sessionId, nodeid_now,  nodetype_now)
                logging.info(f'在给大模型判断前，得到obsevation的输入。 sessionId {sessionId}, nodeid_now {nodeid_now}, nodetype_now, {nodetype_now} ')
                current_task = self.gb_handler.geabase_getDescription(  nodeid_now,  nodetype_now)
                chosen_nodeid = self.fact_branch_judgment( current_task, neighbor_node_id_list, 
                    next_node_description_list, observation=observation)

                #write memory
                self.write_phenomenon_memory( sessionId, neighbor_node_id_list, chosen_nodeid)
                #继续往被选中的分支后面扩散
                nodeid_in_search.append({'nodeId':chosen_nodeid, 'nodeType':'opsgptkg_phenomenon'})

            # elif all_analysis_check(res) == True:#是否后续所有节点均为analysis，一般只有analysis是单个出现
            elif self.gb_handler.all_nodetype_check(rootNodeId = nodeid_now, rootNodeType = nodetype_now, 
        neighborNodeType = 'opsgptkg_analysis') == True:#是否后续所有节点均为analysis，一般只有analysis是单个出现
                logging.info(f'#扩散到了结论节点, 均往后扩展')
                #扩散到了结论节点, 均往后扩展
                #写memory，write_analysis_memory，
                # neighbor_node_id_list       = get_nodeid_from_res(res)  #取后续事实节点，假设事实节点一定只有一个
                neighbor_node_id_list = self.gb_handler.getNeighborNodeids(nodeid_now , nodetype_now)
                # logging.info(f'neighbor_node_id_list is  {neighbor_node_id_list}, ')
                self.write_analysis_memory( sessionId, neighbor_node_id_list, None)
                #继续往后面扩散，虽然大概率后面为空
                for i in range(len(neighbor_node_id_list)):
                    nodeid_in_search.append({'nodeId':neighbor_node_id_list[i], 'nodeType':'opsgptkg_analysis'})

            

            else:
                for i in range(len( neighborNodes ) ):
                        nodeid_new      = neighborNodes[i].id
                        nodetype_new    = neighborNodes[i].type
                        if nodetype_new == 'opsgptkg_task':  #如果是task节点，

                            if self.gb_handler.geabase_is_react_node(nodeid_new, nodetype_new) == False:
                                # logging.info(f'{nodeid_new}是task 节点中的  tool 节点 则加入到tool_plan中，但是不往后续延展了。表示找到了后续的plan')
                                #是task 节点中的  tool 节点 则加入到tool_plan中，但是不往后续延展了。表示找到了后续的plan
                                tool_plan.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                            else:
                                # logging.info(f'{nodeid_new}#是task 节点中的 react,  节点尝试执行')
                                #是task 节点中的 react,  节点尝试执行  
                                # logging.info(f'sessionId {sessionId}, nodeid_new {nodeid_new}, nodetype_new {nodetype_new}')
                                
                                runningFlag, reactPlan = self.task_node_agent.task_running( sessionId, nodeid_new, nodetype_new, None )
                                #这种时候是react节点第一次运行，一定是主持人，一定要看到全局信息

                                # logging.info(f'{nodeid_new}#继续执行还是没有执行完, 需要留下 reactPlan，且不往后面扩展')
                                #继续执行还是没有执行完, 需要留下 reactPlan，且不往后面扩展
                                if runningFlag == 'waiting_other_agent':
                                    #表示现在还需要运行这个节点，无需进行后续探索,还是执行这个tool，返回应该返回的plan即可

                                    tool_plan.append({'nodeId':nodeid_new, 'nodeType':nodetype_new, 
                                    'reactPlan':reactPlan, 'reactFlag': True})  
                                else:
                                    #这个react 执行了一下执行完了. 继续， tool_plan中不标记这个节点，往后探索即可。
                                    nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})

                                
                        else:##如果是不是task节点，不加入到tool_plan中，往后续延展
                            nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})


        # unique_set = set(tuple(sorted(d.items())) for d in tool_plan) #暂时去掉去重，但不知有何问题
        # 将去重后的元组转换回字典形式，得到去重后的list
        # tool_plan = [dict(t) for t in unique_set] #暂时去掉去重，但不知有何问题
        # logging.info('====tool_plan===在去重之后===')
        # logging.info(f'tool_plan {tool_plan}')
        # logging.info('====tool_plan======')
        
        #2 判断这些tool的父节点是否都已经有observation, 即判断可达性， 进行筛选
        tool_plan_2 = []
        for i in range(len(tool_plan)):
            nodeId = tool_plan[i]['nodeId']
            nodeType = tool_plan[i]['nodeType']
            if self.geabase_judgeNodeReachability( sessionId, 
                nodeId,  nodeType) == True:
                tool_plan_2.append({'nodeId':nodeId, 'nodeType':nodeType})
        # logging.info(f'tool_plan_2 经过可达性判断删选后的 {tool_plan_2}')

        #3 获取每个tool的memory
        tool_plan_return = []
        #     {
        # 		"toolDescription": "toolDescriptionA",
        # 		"currentNodeId": "INT_1",
        #    "memory": JsonStr,
        # 	}


        for i in range(len(tool_plan_2)):
            nodeId      = tool_plan[i]['nodeId']
            nodeType    = tool_plan[i]['nodeType']
            if 'reactFlag' not in tool_plan[i].keys():
                # memory = self.geabase_getmemory( sessionId,  nodeId,  nodeType)
                #获取memory， 这个是task tool的memory，
                # tool_ancestor = self.get_tool_ancestor( sessionId, nodeId, nodeType)
                # logging.info(f'{nodeId}的  tool_ancestor is {tool_ancestor}')
                # get_messages_res_sorted = self.get_memory_from_ancestor( tool_ancestor, sessionId, role_tags = None) #此时是nodeId是一个tool，假设tool一定是主持人的工具，能看到所有tag的memory

                # memory = self.assemble_memory( nodeId, nodeType, get_messages_res_sorted)
                memory = self.task_node_agent.get_memory_for_tool(sessionId, nodeId)
                # logging.info(f'{nodeId}的  memory is {memory}')

                toolDescription = self.gb_handler.geabase_getDescription( rootNodeId = nodeId, rootNodeType = nodeType)

                tool_plan_return.append(
                            {
                    "toolDescription":  toolDescription,
                    "currentNodeId":    nodeId,
                    "memory":           json.dumps(memory, ensure_ascii=False),
                    "type" : self.gb_handler.geabase_getnodetype( rootNodeId = nodeId , rootNodeType = nodeType) ,
                    "questionDescription": self.gb_handler.geabase_getnodequestion( rootNodeId = nodeId, rootNodeType = nodeType)
                }
                )
            else:
                #对于react 模块的 memory，另有方法提取，在制定plan的时候就提取了。

                tool_plan_return.append( tool_plan[i]['reactPlan'][0]   )   #tool_plan[i]['reactPlan'] 本身就是一个list, 必须先取元素，否则格式会出错



        return  tool_plan, tool_plan_return
if __name__ == "__main__":


    pass

    #