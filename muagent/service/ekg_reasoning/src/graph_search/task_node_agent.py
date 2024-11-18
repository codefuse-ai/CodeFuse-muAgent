# -*- coding: utf-8 -*-
#此代码为在aistudio上运行的代码

#路径增加
import sys
import os
import re
from typing import List, Dict, Optional, Tuple, Literal,Union
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
from muagent.schemas.ekg.ekg_reason import LingSiResponse, ToolPlanOneStep, PlanningRunningAgentReply, ActionOneStep, ActionPlan

from src.graph_search.task_node_prompt import REACT_RUNNING_PROMPT, PLANNING_RUNNING_PROMPT, PLANNING_RUNNING_PROMPT_SUFFIX_1,PLANNING_RUNNING_PROMPT_SUFFIX_2, PLANNING_RUNNING_AGENT_REPLY_TEMPLATE
# from loguru import logger as logging
from src.utils.call_llm import call_llm,  extract_final_result , robust_call_llm
from src.geabase_handler.geabase_handlerplus import GB_handler
from src.utils.normalize import hash_id
from src.memory_handler.ekg_memory_handler import memory_handler_ekg





def is_valid_json(string):
    try:
        json.loads(string)
        return True
    except ValueError:
        return False
def robust_json_loads(llm_result):
    '''
        将llm的输出转换为json， 有一定的概率这个json 在格式上是不完备的。不然少了 } 或者]
    '''

    try:
        llm_result_json = json.loads(llm_result)
    except:
        # for _ in range(2):
            try:
                logging.info('大模型的输出转换json报错， 现在再用大模型修正一遍')
                input_query = f'''
                ##输入##
                {llm_result}
                ##任务##
                上述**输入**可能是一个不完整的dict，如果是这种情况，请将上述转换**输入**为完整的 dict。 不要新增任何内容，只将格式补全/修正为一个完整dict格式即可
                上述**输入**也可能是包含多个dict，如果是这种情况，只保留第一个dict即可。 不要新增任何内容，只将格式补全/修正为一个完整dict格式即可
                ##直接输出结果##
                ''' + '以{开头，任何其他内容都是不允许的！'
                ouput_result = robust_call_llm(input_query )
                logging.info(f'修正后的输出为{ouput_result}')
                llm_result_json = json.loads(ouput_result)


            except:
                logging.info('大模型的输出转换json报错， 现在再用大模型修正一遍')
                input_query = f'''
                ##输入##
                {llm_result}
                ##任务##
                上述**输入**可能是一个不完整的dict，如果是这种情况，请将上述转换**输入**为完整的 dict。 不要新增任何内容，只将格式补全/修正为一个完整dict格式即可
                上述**输入**也可能是包含多个dict，如果是这种情况，只保留第一个dict即可。 不要新增任何内容，只将格式补全/修正为一个完整dict格式即可
                ##直接输出结果##
                ''' + '以{开头，任何其他内容都是不允许的！'
                ouput_result = robust_call_llm(input_query, None , temperature = 0.1)
                logging.info(f'修正后的输出为{ouput_result}')
                llm_result_json = json.loads(ouput_result)
    if type(llm_result_json)!=dict:
        llm_result_json = llm_result_json[0]
        logging.info('llm的输出应该是一个dict才对, 有时候出现[{one step}], 所以尝试选其中一个元素转换为dict')
        raise  ValueError(f'llm的输出应该是一个dict才对 ,经过修正仍然报错')
    return llm_result_json

def agent_respond_extract_output(input_str):
    if 'output' not in input_str:
        return input_str
    input_str = input_str.split('output')[-1]  #取output后面的值
    input_str = input_str.replace('"', '').replace(':', '').replace('}', '').replace('{', '') #去除掉可能的符号
    return input_str
    


class TaskNodeAgent():
    '''
        在图谱推理过程中task node 的运行agent
        需要同时 使用memory and geabase
    '''
    def __init__(self, geabase_handler, memory_manager, llm_config=None):
        self.geabase_handler = geabase_handler
        self.memory_manager  = memory_manager
        self.gb_handler = GB_handler(self.geabase_handler) #gb_handler 以  geabase_handler 为基础，封装了一些处理逻辑
        self.memory_handler  = memory_handler_ekg(memory_manager, geabase_handler)
        self.llm_config = llm_config
    
    
    
 
    def robust_call_llm_with_llmname(self, input_query, rootNodeId, stop = None, temperature = 0, presence_penalty=0):

        #logging.info('using a gpt_4')
        res = call_llm(input_content = input_query, llm_model = None ,  
                       stop = stop,temperature=temperature, presence_penalty=presence_penalty,
                       llm_config=self.llm_config)
        return res


        # model_name = self.gb_handler.get_extra_tag(  rootNodeId = rootNodeId, rootNodeType = 'opsgptkg_task', key = 'model_name')
        # logging.info(f'model_name is {model_name}')
        # if model_name == None:
        #     model_name = 'gpt_4'
        # if model_name == 'gpt_4':
        #     try:
        #         logging.info('using a gpt_4')
        #         res = call_llm(input_content = input_query, llm_model = 'gpt_4',  stop = stop,temperature=temperature, presence_penalty=presence_penalty)
        #     except:
        #         logging.info('using Qwen2_72B_Instruct_OpsGPT')
        #         res = call_llm(input_content = input_query, llm_model = 'Qwen2_72B_Instruct_OpsGPT',stop = stop, temperature=temperature,presence_penalty=presence_penalty)
        #     return res
        # else:
        #     try:
        #         logging.info('using Qwen2_72B_Instruct_OpsGPT')
        #         res = call_llm(input_content = input_query, llm_model = 'Qwen2_72B_Instruct_OpsGPT',stop = stop, temperature=temperature,presence_penalty=presence_penalty)
        #     except:
        #         logging.info('using a gpt_4')
        #         res = call_llm(input_content = input_query, llm_model = 'gpt_4',  stop = stop,temperature=temperature, presence_penalty=presence_penalty)
        #     return res

    def stop_at_observation(self, historytext, llm_text):


        # 检查llm_text是否完全不包含"observation"
        if "observation" not in llm_text:
            return llm_text
        
        # 检查historytext中是否有"observation"
        if "observation" not in historytext:
            return llm_text.split("observation", 1)[0]
        
        # 统计historytext中的"observation"数量
        n_hist = historytext.count("observation")
        
        # 统计llm_text中的"observation"数量
        n_llm = llm_text.count("observation")
        
        # 如果两者数量相等，返回第n个observation之后的文本
        if n_hist == n_llm:
            parts = llm_text.rsplit("observation", n_hist)
            return parts[-1]  # 返回最后一个部分（即最后一个"observation"之后的文本）
        
        # 如果上述条件都不满足，找到第n个和第n+1个"observation"之间的文本
        else:
            parts = llm_text.split("observation", n_hist + 1)  # 分割出n+1个部分
            if len(parts) > n_hist + 1:  # 确保有足够多的部分来获取所需范围
                return parts[n_hist]  # 返回第n个和第n+1个observation之间的文本
            else:
                return ""  # 如果没有找到合适的范围，则返回空字符串或其他适当处理



    def sort_messages_by_time(self, messages):
        # 使用 sorted() 对列表进行排序，key 参数指定排序依据
        return sorted(messages, key=lambda msg: msg.start_datetime)
    
    

    def endcheck(self, nodeId, nodeType, oneNodeName='None', oneNodeDescription='None', current_node_history_json='None'):
        '''
            借助gpt4 来帮忙判断本阶段任务是否结束
        '''
        oneNode = self.geabase_handler.get_current_node(attributes={"id": nodeId,}, 
                                  node_type=nodeType)
        extra = oneNode.attributes['extra'] 
        print(extra)
        try:

            extra_json = json.loads(extra)
            if extra_json['endcheck'] == 'True':
                endcheck_flag = True
            else:
                endcheck_flag = False
        except:
            endcheck_flag= False
        
        if endcheck_flag == False:
            return True #endcheck 通过
        
        else:
            endcheck_llm_input =       oneNodeName + '\n' +oneNodeDescription+ '\n##已有步骤##\n' + json.dumps(current_node_history_json,ensure_ascii=False) + \
            '\n##请结合已有步骤，判断本阶段任务是否结束，只返回中文的 是 或者 否即可，不要输出其他内容:##\n'
            
            logging.info('=============endcheck_llm_result==================')
            logging.info(endcheck_llm_input)
            llm_result = self.robust_call_llm_with_llmname(endcheck_llm_input, nodeId)
            logging.info('=============endcheck_llm_result==================')
            logging.info(llm_result)

            if '是' in llm_result:
                return False
            else:
                return True
    
    
    def naive_agent_input_prompt(self, histroy:str, node_name:str, node_decription:str,  running_type_prompt:str, 
                                 suffix_1:str = '', suffix_2:str = '')    ->  str:
            llm_input = histroy + '\n' + node_name + '\n' + node_decription + '\n' + running_type_prompt\
                + suffix_1 + suffix_2
            return llm_input
        
    
    def task_running(self, sessionId : str, nodeId: str, nodeType:str, lingsi_respond: LingSiResponse):
        '''
        通用的节点task_running 模块， 根据情况，当前分为  react， parallel，planning
        '''

        if self.gb_handler.get_tag(rootNodeId = nodeId, rootNodeType = nodeType, key = 'action') == 'react':
            logging.info(f'======对于节点{nodeId},当前节点为 react 模式======')
            return self.react_running( sessionId  ,nodeId , nodeType , lingsi_respond )
        elif self.gb_handler.get_tag(rootNodeId = nodeId, rootNodeType = nodeType, key = 'action') == 'parallel':
            logging.info(f'======对于节点{nodeId}, 当前节点为 parallel 模式======')
            return self.parallel_running( sessionId  ,nodeId , nodeType , lingsi_respond )
        elif self.gb_handler.get_tag(rootNodeId = nodeId, rootNodeType = nodeType, key = 'action') == 'plan':
            logging.info(f'======对于节点{nodeId}, 当前节点为 plan 模式======')
            return self.planning_running( sessionId  ,nodeId , nodeType , lingsi_respond )
        else:
            action = self.gb_handler.get_tag(rootNodeId = nodeId, rootNodeType = nodeType, key = 'action')
            logging.info(f'action当前字段为{action}')
            raise ValueError('action 字段格式不合法，当前仅支持 react  parallel  plan 三种模式')

    
    def judge_running_state(self, sessionId: str, nodeId: str)-> bool :
        '''
            判断当前节点是否是第一次运行
        '''
        get_messages_res = self.memory_handler.nodecount_get(  sessionId, nodeId)
        
        if get_messages_res == [] :
            logging.info('当前这个{sessionId} react节点 是第一次运行')
            first_run_flag = True
        else:
            if json.loads(get_messages_res[0].role_content)['nodestage'] == 'end' :#在上一轮已经结束了，这一轮还未开始
                logging.info('当前这个{sessionId} react节点在上一轮已经结束了，这一轮还未开始，在这一轮也算是第一次执行')
                first_run_flag  = True
            else:
                logging.info('当前这个{sessionId} react节点 不是第一次执行')
                first_run_flag = False
        return first_run_flag
    
    
    def parallel_running(self, sessionId : str, nodeId: str, nodeType:str, lingsi_respond: LingSiResponse):
        '''
            parallel 模块 
            
        '''
        #step0 根据返回值，得到实际agent执行内容

        logging.info(f'react_running 接受到的 lingsi_respond  is {lingsi_respond}')
        try:
            if lingsi_respond == None:#第一次该该节点被调用是，输入式将lingsi_respond设置为None
                agent_respond = None
            else:
                if type(lingsi_respond.observation) ==str:
                    agent_respond = json.loads(lingsi_respond.observation)['toolResponse']
                else:
                    agent_respond = lingsi_respond.observation['toolResponse']
        except Exception as e:
            logging.info(f'lingsi_respond is {lingsi_respond}' )
            raise ValueError(f'从lingsi_respond中提取 agent_respond报错, 报错信息：{e}')


        
        #stpe1 判断当前状态, 看是否是第一次运行
        first_run_flag = self.judge_running_state( sessionId,nodeId)
        if  first_run_flag == True:  
            # 当react的状态是 end 或者为空的时候调用此函数，进行初始化 或者 chapter + 1
            self.memory_handler.init_react_count(sessionId, nodeId)    
        
        
        #step2 获取节点名字 + 节点描述
        oneNode = self.geabase_handler.get_current_node(attributes={"id": nodeId,}, 
                                  node_type=nodeType)
        oneNodeName  = oneNode.attributes['name']
        oneNodeDescription  = oneNode.attributes['description']
        oneNodeDescription = self.fill_replacements(oneNodeDescription, sessionId)

        # 变量替换
        
        
        #step3.1 获取memory， 构成给大模型的输入
        #获取memory， 主持人能看到的memory， 和获取tool的memory类似
        assembled_memory = self.get_memory_for_dm(sessionId, nodeId)
        assembled_memory = json.dumps(assembled_memory, ensure_ascii=False)
        logging.info(f'assembled_memory is {assembled_memory}')
        
        #step3.2 获取当前节点的历史运行情况。如果是第一次运行，需要将react node 的name 存入到 memory中
        if first_run_flag == True:
            current_node_history = ''
            current_node_history_json = []
            #第一次运行，对于react模块，只将标题放置在memory里， 因为对于react模块，description太多了，循环的情况下，很罗嗦且超过上下文
            self.memory_handler.react_nodedescription_save(sessionId, nodeId, oneNodeName)
        else:
            #不是第一次运行。那么肯定历史history进来
            logging.info(f'#不是第一次运行。那么肯定存储了plan')
            current_node_history  = self.memory_handler.react_current_history_get(sessionId, nodeId)
            current_node_history_json = json.loads(current_node_history) 
            
            action_plan = json.loads( self.memory_handler.current_plan_get(sessionId, nodeId ) )
            #action_plan = json.loads(json.dumps(action_plan,  ensure_ascii=False)) #去除乱码
            logging.info(f'对于parallel， 之前存储的action_plan is {action_plan} ，type(action_plan) is {type(action_plan) } ') 
            action_plan =ActionPlan(**action_plan)
 
            
        #step4 执行 llm(如果是第一次调用)
        if first_run_flag == True:

            llm_input = self.naive_agent_input_prompt(assembled_memory, oneNodeName, oneNodeDescription ,PLANNING_RUNNING_PROMPT
                , PLANNING_RUNNING_PROMPT_SUFFIX_1 , PLANNING_RUNNING_PROMPT_SUFFIX_2)

            logging.info('=============llm_input==================')
            logging.info(llm_input)
            
            llm_result = self.robust_call_llm_with_llmname(llm_input, nodeId)
            
            logging.info('=============llm_result==================')
            logging.info(llm_result)
            llm_result_json = robust_json_loads(llm_result)
            llm_result_PRAR = PlanningRunningAgentReply(**llm_result_json)
            
            current_node_history_json.append(llm_result_json) #将当前记录放到current_node_history_json里

            logging.info('planning_running 第一次大模型调用结束')

            
            
            #此时的action_plan 是一个string
            #action_plan = llm_result_json["action_plan"]
            # 将 sss 中的字典转换为 ActionOneStep 对象
            #action_steps = [ActionOneStep(**step) for step in sss]
            
            # 创建 ActionPlan 对象并设置 data 属性
            action_plan = llm_result_PRAR.action_plan

            
            
        else:
            logging.info('不是第一次调用，无需执行大模型, 将已运行的agent_name 存下来')
            self.memory_handler.processed_agentname_save(sessionId, nodeId, lingsi_respond.agentName )
            
        
        
        #step5 分析 llm_result 执行结果
        
        if first_run_flag == True and  len(action_plan.data) >0 :
            react_flag = 'waiting_other_agent'
    
            logging.info(f'当前为{react_flag}, 因为初次运行且plan不为空')
            execute_agent_names =  [action_plan.data[i].agent_name for i in range(len(action_plan.data))]
            #将该节点的count 设置为 runninng
            self.memory_handler.nodecount_set_key(sessionId, nodeId, 'nodestage', 'running')
            
            
        else:
            processed_agentname = self.memory_handler.processed_agentname_get(sessionId, nodeId)#list
            logging.info(f'已经处理的agent_name 为 {processed_agentname}')
            if processed_agentname == []:
                raise  ValueError(f'此时不是第一次运行，在memory中应该已经有processed_agentname才对，但是processed_agentname is {processed_agentname} ')
            
            remain_action_plan = []
            for i in range(len(action_plan.data)):
                if action_plan.data[i].agent_name not in processed_agentname:
                    remain_action_plan.append(action_plan.data[i])
                    
            logging.info(f'剩余待处理的的agent_name 为 {remain_action_plan}')
            if len(remain_action_plan) == 0:
                execute_agent_names = []
                react_flag = 'end'
                logging.info(f'当前为{react_flag}, 将本次节点的count设置为end, 因为remain_action_plan 为空 ')
                self.memory_handler.nodecount_set_key(sessionId, nodeId, 'nodestage', 'end')
            else:
                react_flag = 'waiting_other_agent'
                logging.info(f'当前为{react_flag}, 因为第一次大模型生成的plan还没有执行成完,还需等待其他步骤执行完毕 ')
                execute_agent_names = [] #对于parallel 模式，中途的结果不给下一步指示，因为tool_plan在第一次就并行执行了
                
                #将该节点的count 设置为 runninng
                self.memory_handler.nodecount_set_key(sessionId, nodeId, 'nodestage', 'running')
    
        
        #step6 分析 llm_result 执行结果, 并保存
    
        if first_run_flag == True:
            action_plan_json = llm_result_json["action_plan"]
            # 将 sss 中的字典转换为 ActionOneStep 对象
            action_steps = [ActionOneStep(**step) for step in action_plan_json]
            
            # 创建 ActionPlan 对象并设置 data 属性
            action_plan = ActionPlan(data=action_steps)
            action_plan_json_str = json.dumps(action_plan.dict() ,ensure_ascii=False)
            
            logging.info(f'将要存储action_plan, action_plan_json_str is {action_plan_json_str}')
            #存plan
            self.memory_handler.current_plan_save(sessionId, nodeId, json.dumps(action_plan.dict() ,ensure_ascii=False)  )
            #存对话
            self.memory_handler.react_current_history_save(sessionId, nodeId, json.dumps(current_node_history_json ,ensure_ascii=False)  )
            
        else:
            #存agent返回结果的对话
            #agent_respond_template = self.plan_running_agent_responds_build()
    

            agent_respond_template = PLANNING_RUNNING_AGENT_REPLY_TEMPLATE

            agent_respond_template['action']['agent_name']  = lingsi_respond.agentName
            agent_respond_template['action']['player_name'] = action_plan.get_player_name_by_agent_name(lingsi_respond.agentName)
            #agent_respond_template['observation'] = [{ "memory_tag":[nodeId],"content": agent_respond}] #
            agent_respond_template['observation'] = [{ "memory_tag":['all'],"content": agent_respond}] 
            ## TODO: 这是一个临时解决方案，需要在后续版本中替换为更优的算法,具体为 无论是planning还是parallel，可见范围都最好需要时立即能知道。所以不能等到玩家发言后，再到前端显示
            ## 当前设置为all了，但是这是不对的， 有一个解决方案是，将主持人最开始的memory_tag作为后续所有的memory_tag，有一个风险是需要区分 信息的可见范围以及 plan的区别
            ## 可以看见这些memory不一定表示 要参与行动。
            
            
            current_node_history_json.append(agent_respond_template)
            self.memory_handler.react_current_history_save(sessionId, nodeId, json.dumps(current_node_history_json ,ensure_ascii=False)  )
            logging.info(f'current_node_history_json is  {current_node_history_json}' )
    

        #step7 存储 memory # for other agent
        self.memory_handler.react_memory_save(sessionId, nodeId,  current_node_history_json)
        
        update_flag = self.update_replacement(sessionId, nodeId)
        if update_flag:
            logging.info("变量更新成功！")
        else:
            logging.info("无变量更新或变量更新失败")
        #step8 返回 question_plan
        if react_flag == 'end':
            question_plan = []
        elif react_flag == 'waiting_other_agent':
            question_plan = self.react_get_question_plan(sessionId, nodeId, execute_agent_names)
            logging.info(f'parallel question_plan is {question_plan}')
        else:
            question_plan = []
        return react_flag, question_plan    
    

    def planning_running(self, sessionId : str, nodeId: str, nodeType:str, lingsi_respond: LingSiResponse):

        '''
            planning 模块
            
        '''
        #step0 根据返回值，得到实际agent执行内容

        logging.info(f'react_running 接受到的 lingsi_respond  is {lingsi_respond}')
        try:
            if lingsi_respond == None:#第一次该该节点被调用是，输入式将lingsi_respond设置为None
                agent_respond = None
            else:
                if type(lingsi_respond.observation) ==str:
                    agent_respond = json.loads(lingsi_respond.observation)['toolResponse']
                else:
                    agent_respond = lingsi_respond.observation['toolResponse']
        except Exception as e:
            logging.info(f'lingsi_respond is {lingsi_respond}' )
            raise ValueError(f'从lingsi_respond中提取 agent_respond报错, 报错信息：{e}')

        
        #stpe1 判断当前状态, 看是否是第一次运行
        first_run_flag = self.judge_running_state( sessionId,nodeId)
        if  first_run_flag == True:  
            # 当react的状态是 end 或者为空的时候调用此函数，进行初始化 或者 chapter + 1
            self.memory_handler.init_react_count(sessionId, nodeId)    
        
        
        #step2 获取节点名字 + 节点描述
        oneNode = self.geabase_handler.get_current_node(attributes={"id": nodeId,}, 
                                  node_type=nodeType)
        oneNodeName  = oneNode.attributes['name']
        oneNodeDescription  = oneNode.attributes['description']


        oneNodeDescription = self.fill_replacements(oneNodeDescription, sessionId)

        # 变量替换
        
        
        #step3.1 获取memory， 构成给大模型的输入
        #获取memory， 主持人能看到的memory， 和获取tool的memory类似
        assembled_memory = self.get_memory_for_dm(sessionId, nodeId)
        assembled_memory = json.dumps(assembled_memory, ensure_ascii=False)
        logging.info(f'assembled_memory is {assembled_memory}')
        
        #step3.2 获取当前节点的历史运行情况。如果是第一次运行，需要将react node 的name 存入到 memory中
        if first_run_flag == True:
            current_node_history = ''
            current_node_history_json = []
            #第一次运行，对于react模块，只将标题放置在memory里， 因为对于react模块，description太多了，循环的情况下，很罗嗦且超过上下文
            self.memory_handler.react_nodedescription_save(sessionId, nodeId, oneNodeName)
        else:
            #不是第一次运行。那么肯定历史history进来
            logging.info(f'#不是第一次运行。那么肯定存储了plan')
            current_node_history  = self.memory_handler.react_current_history_get(sessionId, nodeId)
            current_node_history_json = json.loads(current_node_history)
            
            action_plan = json.loads( self.memory_handler.current_plan_get(sessionId, nodeId ) )
            logging.info(f'对于 planning 之前存储的action_plan is {action_plan} ，type(action_plan) is {type(action_plan) } ') 
            action_plan =ActionPlan(**action_plan)
            
        #step4 执行 llm(如果是第一次调用)
        if first_run_flag == True:

            llm_input = self.naive_agent_input_prompt(assembled_memory, oneNodeName, oneNodeDescription ,PLANNING_RUNNING_PROMPT
                , PLANNING_RUNNING_PROMPT_SUFFIX_1 , PLANNING_RUNNING_PROMPT_SUFFIX_2)

            logging.info('=============llm_input==================')
            logging.info(llm_input)
            
            llm_result = self.robust_call_llm_with_llmname(llm_input, nodeId)
            
            logging.info('=============llm_result==================')
            logging.info(llm_result)
            llm_result_json = robust_json_loads(llm_result)
            
            current_node_history_json.append(llm_result_json) #将当前记录放到current_node_history_json里

            logging.info('planning_running 第一次大模型调用结束')

            
            
            action_plan = llm_result_json["action_plan"]
            
            
        else:
            logging.info('不是第一次调用，无需执行大模型, 将已运行的agent_name 存下来')
            self.memory_handler.processed_agentname_save(sessionId, nodeId, lingsi_respond.agentName )
        
        
        #step5 分析 llm_result 执行结果
        
        if first_run_flag == True and  len(action_plan) >0 :
            react_flag = 'waiting_other_agent'

            logging.info(f'当前为{react_flag}, 因为初次运行且plan不为空')
            # llm_result_truncation_json = json.loads(current_node_history +  llm_result_truncation + '":[]}]')
            # llm_result_truncation_json = json.loads(current_node_history +  llm_result_truncation + '":[]}]')

            #提取此时应该执行的agent_name
            execute_agent_name = action_plan[0]['agent_name']
            execute_player_name = action_plan[0]['player_name']

            #将该节点的count 设置为 runninng
            self.memory_handler.nodecount_set_key(sessionId, nodeId, 'nodestage', 'running')
            
            
        else:
            processed_agentname = self.memory_handler.processed_agentname_get(sessionId, nodeId)#list
            logging.info(f'已经处理的agent_name 为 {processed_agentname}')
            if processed_agentname == []:
                raise  ValueError(f'此时不是第一次运行，在memory中应该已经有processed_agentname才对，但是processed_agentname is {processed_agentname} ')
            
            remain_action_plan = []
            for i in range(len(action_plan)):
                if action_plan[i]['agent_name'] not in processed_agentname:
                    remain_action_plan.append(action_plan[i])
            
            logging.info(f'剩余待处理的的agent_name 为 {remain_action_plan}')
            if len(remain_action_plan) == 0:
            
                react_flag = 'end'
                logging.info(f'当前为{react_flag}, 将本次节点的count设置为end, 因为remain_action_plan 为空 ')
                self.memory_handler.nodecount_set_key(sessionId, nodeId, 'nodestage', 'end')
            else:
                react_flag = 'waiting_other_agent'
                logging.info(f'当前为{react_flag}, 因为第一次大模型生成的plan还没有执行成完 ')
                
                #提取此时应该执行的agent_name
                execute_agent_name = remain_action_plan[0]['agent_name']
                execute_player_name = remain_action_plan[0]['player_name']

                #将该节点的count 设置为 runninng
                self.memory_handler.nodecount_set_key(sessionId, nodeId, 'nodestage', 'running')

        
        #step6 分析 llm_result 执行结果, 并保存
 
        if first_run_flag == True:
            action_plan = llm_result_json["action_plan"]
            #存plan
            self.memory_handler.current_plan_save(sessionId, nodeId, json.dumps(action_plan ,ensure_ascii=False)  )
            #存对话
            self.memory_handler.react_current_history_save(sessionId, nodeId, json.dumps(current_node_history_json ,ensure_ascii=False)  )
            
        else:
            #存agent返回结果的对话
            #agent_respond_template = self.plan_running_agent_responds_build()


            agent_respond_template = PLANNING_RUNNING_AGENT_REPLY_TEMPLATE

            agent_respond_template['action']['agent_name']  = lingsi_respond.agentName
            #agent_respond_template['action']['player_name'] = self.get_player_name_from_action_plan(action_plan, lingsi_respond.agentName)
            agent_respond_template['action']['player_name'] = action_plan.get_player_name_by_agent_name(lingsi_respond.agentName)
            agent_respond_template['observation'] = [{ "memory_tag":['all'],"content": agent_respond}]# TODO
            current_node_history_json.append(agent_respond_template)
            self.memory_handler.react_current_history_save(sessionId, nodeId, json.dumps(current_node_history_json ,ensure_ascii=False)  )


        #step7 存储 memory # for other agent
        self.memory_handler.react_memory_save(sessionId, nodeId,  current_node_history_json)
        
        update_flag = self.update_replacement(sessionId, nodeId)
        if update_flag:
            logging.info("变量更新成功！")
        else:
            logging.info("无变量更新或变量更新失败")
        #step8 返回 question_plan
        if react_flag == 'end':
            question_plan = []
        elif react_flag == 'waiting_other_agent':
            question_plan = self.react_get_question_plan(sessionId, nodeId, execute_agent_name)
        else:
            question_plan = []
        return react_flag, question_plan

    def get_player_name_from_action_plan(self, action_plan, agent_name):
        '''
            从action_plan中获取agent_name
        '''
        for i in range(len(action_plan)):
            if action_plan[i]['agent_name'] == agent_name:
                return action_plan[i]['player_name']
        raise ValueError(f'action plan {action_plan }中未找到 对应的 agent name {agent_name}')
        
    def fill_replacements(self, node_description: str, sessionId: str) -> str:
        """
        构建替换后的 prompt 字符串。
        :param sessionId: 一个函数，接收占位符名称并返回对应的值
        :return prompt: 替换后的 prompt 字符串 
        :return placeholders 涉及到的变量
        """
        prompt = node_description
        logging.info(f'prompt:{prompt}')
        placeholders = re.findall(r"#\$\#(.*?)#\$\#", prompt)
        logging.info("开始变量替换")
        logging.info(f'需要替换的变量{placeholders}')
        try:
            for placeholder in placeholders:
                logging.info(f'placeholder为{placeholder}')
                value = self.memory_manager.get_msg_content_by_rule_name(sessionId, placeholder)
                logging.info(f'value为{value}')
                if value != None:
                    prompt = prompt.replace(f'#$#{placeholder}#$#', value)
                logging.info(f'替换后的prompt{prompt}')
        except Exception as e:
            logging.info(f"变量替换出现错误！{e}")

        return prompt


    def update_replacement(self, sessionId: str, nodeId: str) -> bool:
        """
        更新变量名，
        :param sessionId: 对话id
        :param nodeId: 节点id
        """
        cur_node_memory = self.get_cur_node_memory(sessionId, nodeId)
        logging.info(f'当前节点游戏记录:{cur_node_memory}')
        cur_node_memory = "当前节点游戏记录:" + ''.join(cur_node_memory)

        try:
            updaterule = self.gb_handler.get_tag(rootNodeId = nodeId, rootNodeType = "opsgptkg_task", key = 'updaterule')
            cur_node_updaterule = json.loads(updaterule)
        except Exception as e:
            logging.info(f"出现错误: {e}")
            logging.info(f"输入不是json格式或者为空，变量更新失败，略过.")
            logging.info(f"node_envdescription: {updaterule}")
            return False
        
        update_flag = False
        try:
            for placeholder, update_role in cur_node_updaterule.items():
                logging.info(f'更新的变量为:{placeholder}')
                logging.info(f'当前节点游戏记录为:{cur_node_memory}')
                update_flag = self.memory_manager.update_msg_content_by_rule(sessionId, placeholder, cur_node_memory, update_role)
                logging.info(f'update_flag:{update_flag}')
        except Exception as e:
            logging.info(f"变量更新出现错误！{e}")
        return update_flag
    

    def react_running(self, sessionId : str, nodeId: str, nodeType:str, lingsi_respond: LingSiResponse):
        '''
            react 模块 运行
        '''

        
        logging.info(f'react_running 接受到的 lingsi_respond  is {lingsi_respond}')
        try:
            if lingsi_respond == None:#第一次该该节点被调用是，输入式将lingsi_respond设置为None
                agent_respond = None
            else:
                if type(lingsi_respond.observation) ==str:
                    agent_respond = json.loads(lingsi_respond.observation)['toolResponse']
                else:
                    agent_respond = lingsi_respond.observation['toolResponse']
        except Exception as e:
            logging.info(f'lingsi_respond is {lingsi_respond}' )
            raise ValueError(f'从lingsi_respond中提取 agent_respond报错, 报错信息：{e}')


        

        if agent_respond == None:
            agent_respond = ''
        if type(agent_respond) == str:
            agent_respond = agent_respond.replace('"', '').replace("'", "") #需要去除agent返回中的  " 和 '
        agent_respond = agent_respond_extract_output(agent_respond) # 去除 agent_respond 中的 thought 和 output
        #stpe1 判断当前状态
        get_messages_res = self.memory_handler.nodecount_get(  sessionId, nodeId)
        
        if get_messages_res == [] :
            logging.info('当前这个{sessionId} react节点 是第一次运行')
            first_run_react_flag = True
        else:
            if json.loads(get_messages_res[0].role_content)['nodestage'] == 'end' :#在上一轮已经结束了，这一轮还未开始
                logging.info('当前这个{sessionId} react节点在上一轮已经结束了，这一轮还未开始，在这一轮也算是第一次执行')
                first_run_react_flag  = True
            else:
                logging.info('当前这个{sessionId} react节点 不是第一次执行')
                first_run_react_flag = False
        
        if  first_run_react_flag == True:  
            # 当react的状态是 end 或者为空的时候调用此函数，进行初始化 或者 chapter + 1
            self.memory_handler.init_react_count(sessionId, nodeId)
        
        #step2 获取节点名字 + 节点描述
        oneNode = self.geabase_handler.get_current_node(attributes={"id": nodeId,}, 
                                  node_type=nodeType)
        
        oneNodeName  = oneNode.attributes['name']
        oneNodeDescription  = oneNode.attributes['description']
        
        #step3.1 获取memory， 构成给大模型的输入
        #获取memory， 主持人能看到的memory， 和获取tool的memory类似
        
        # tool_ancestor = self.get_tool_ancestor(sessionId, nodeId, nodeType)
        # get_messages_res_sorted = self.get_memory_from_ancestor( tool_ancestor, sessionId, role_tags = None) #此时是主持人，所以需要看到所有的memory，无需加tag。 对于在我这一侧需要运行的llm，一定是看到所有信息，因为我就是主持人
        # assembled_memory = self.assemble_memory(nodeId, nodeType, get_messages_res_sorted)
        assembled_memory = self.get_memory_for_dm(sessionId, nodeId)
        assembled_memory = json.dumps(assembled_memory, ensure_ascii=False)
        logging.info(f'assembled_memory is {assembled_memory}')
        
        #step3.2 获取当前节点的历史运行情况。如果是第一次运行，需要将react node 的name 存入到 memory中
        if first_run_react_flag == True:
            current_node_history = ''
            #第一次运行，对于react模块，只将标题放置在memory里， 因为对于react模块，description太多了，循环的情况下，很罗嗦且超过上下文
            self.memory_handler.react_nodedescription_save(sessionId, nodeId, oneNodeName)
        
        else:
            #不是第一次运行。那么肯定历史history进来
            logging.info(f'#不是第一次运行。那么肯定历史history进来{sessionId}, {nodeId}')
            current_node_history  = self.memory_handler.react_current_history_get(sessionId, nodeId)
            # llm_result_truncation + '": [{"content": ' + user_responds
        
        '''
            history 里存储 observation的截断，不包含observation， 
            llm_output 输出整个完整的流程（如果是gpt_4, 不能有停用词，因为每次都是从头开始录的），
            self.stop_at_observation，需要接受 current_node_history  ，先分析里面有几个observation（N个）， 然后我可以往后扩展一个observation， 不包含observation
        
            jsonstring 就转全量的， 但是录入到memory中的时候，注意只录入 N+1 个 observation的信息。
        
        
        
        '''
        #step4 执行 llm，
        oneNodeDescription += REACT_RUNNING_PROMPT
        logging.info("react 模式 prompt 分离完成")
        oneNodeDescription = self.fill_replacements(oneNodeDescription, sessionId)
        logging.info("变量替换完成")
        if first_run_react_flag == True:
            llm_input = assembled_memory + '\n' + oneNodeName + '\n' + oneNodeDescription + '\n##已有步骤##\n无' + '\n##请输出下一个步骤,切记只输出一个步骤，它应该只是一个dict ##\n'
            logging.info('=============llm_input==================')
            logging.info(llm_input)
            llm_result = self.robust_call_llm_with_llmname(llm_input, nodeId)
            current_node_history_json = []
            logging.info('=============llm_result==================')
            logging.info(llm_result)
            llm_result_json = robust_json_loads(llm_result)
            if type(llm_result_json)!=dict:
                llm_result_json = llm_result_json[0]
                logging.info('llm的输出应该是一个dict才对, 有时候出现[{one step}], 所以尝试选其中一个元素转换为dict')
                # raise  ValueError(f'llm的输出应该是一个dict才对 ')
            current_node_history_json.append(llm_result_json)
        else:
            # current_node_history[-1]["observation"]['content'] = agent_respond
            # llm_input = assembled_memory + '\n' + oneNodeName + '\n' +oneNodeDescription+ '\n' + current_node_history + '": [{"content":" ' + agent_respond + '"'
            # llm_input = assembled_memory + '\n' + oneNodeName + '\n' +oneNodeDescription+ '\n' + current_node_history + '": [{"content":" ' + agent_respond + '", "memory_tag:' \
            #     + '\n '
            
            current_node_history_json = json.loads(current_node_history) #历史记录里可能包含虚假信息
            logging.info(f'current_node_history_json is {current_node_history_json}')
            if current_node_history_json[-1]['action']['agent_name'] != '主持人':
                current_node_history_json[-1]["observation"][0]['content'] = agent_respond #将历史中最后一次主持人幻觉的输出，转换为用户补充的输入
                try:
                    current_node_history_json[-1]["thought"] = '' #在非主持人环节时，应该将thought 设置为''
                except:
                    pass
            llm_input = assembled_memory + '\n' + oneNodeName + '\n' +oneNodeDescription+ '\n##已有步骤##\n' + json.dumps(current_node_history_json,ensure_ascii=False) + \
                '\n##请输出下一个步骤,切记只输出一个步骤，它应该只是一个dict ##\n'
            logging.info('=============llm_input==================')
            logging.info(llm_input)
            llm_result = self.robust_call_llm_with_llmname(llm_input, nodeId)
            logging.info('=============llm_result==================')
            logging.info(llm_result)
            llm_result_json = robust_json_loads(llm_result)
            if type(llm_result_json)!=dict:
                llm_result_json = llm_result_json[0]
                logging.info('llm的输出应该是一个dict才对, 有时候出现[{one step}], 所以尝试选其中一个元素转换为dict')
                # raise  ValueError(f'llm的输出应该是一个dict才对 ')
            current_node_history_json.append(llm_result_json)
        
        retry_llm = 0
        while(( retry_llm <= 8)  and  ("taskend" not in  llm_result) and  (llm_result_json['action']['agent_name'] == '主持人' )):
            logging.info('由于是主持人发言，情况继续')
            
            endcheck_res = self.endcheck( nodeId, nodeType, oneNodeName, oneNodeDescription, current_node_history_json)
            if endcheck_res== False:
                logging.info('endchek没有通过，主持人发言终止, 强行将 llm_result == {"action": "taskend"}')
                llm_result = json.dumps({"action": "taskend"})
                llm_result_json = robust_json_loads(llm_result)
                current_node_history_json.append(llm_result_json)
                break
        
        
        
            llm_input = assembled_memory + '\n' + oneNodeName + '\n' +oneNodeDescription+ '\n##已有步骤##\n' + json.dumps(current_node_history_json,ensure_ascii=False) + \
            '\n##请输出下一个步骤,切记只输出一个步骤，它应该只是一个dict ##\n'
            logging.info('=============llm_input==================')
            logging.info(llm_input)
            llm_result = self.robust_call_llm_with_llmname(llm_input, nodeId)
            logging.info('=============llm_result==================')
            logging.info(llm_result)
            llm_result_json = robust_json_loads(llm_result)
            current_node_history_json.append(llm_result_json)
            if type(llm_result_json)!=dict:
                llm_result_json = llm_result_json[0]
                logging.info('llm的输出应该是一个dict才对, 有时候出现[{one step}], 所以尝试选其中一个元素转换为dict')
                raise  ValueError(f'llm的输出应该是一个dict才对 ')
            retry_llm = retry_llm + 1
        
        logging.info('大模型调用结束')
        
        
        
        #step5 分析 llm_result 执行结果
        #llm_result 为最后一次llm的输出
        if 'taskend' in llm_result:
            react_flag = 'end'
            logging.info(f'当前为{react_flag}, 将本次节点的count设置为end ')
            self.memory_handler.nodecount_set_key(sessionId, nodeId, 'nodestage', 'end')
        elif 'observation' in llm_result:
            react_flag = 'waiting_other_agent'
        
            logging.info(f'当前为{react_flag}, 尝试补充字符使得llm_result_truncation能转为json格式 ')
            # llm_result_truncation_json = json.loads(current_node_history +  llm_result_truncation + '":[]}]')
            # llm_result_truncation_json = json.loads(current_node_history +  llm_result_truncation + '":[]}]')
        
            #提取此时应该执行的agent_name
            execute_agent_name = current_node_history_json[-1]['action']['agent_name']
            execute_player_name = current_node_history_json[-1]['action']['player_name']
        
            #将该节点的count 设置为 runninng
            self.memory_handler.nodecount_set_key(sessionId, nodeId, 'nodestage', 'running')
        
        
        
        
        #step6 存储 history #  for DM
        logging.info(f'存储 history #  for DM')
        if react_flag == 'waiting_other_agent' and first_run_react_flag == True:
            #step6.1 存储 llm_result_truncation
        
            self.memory_handler.react_current_history_save(sessionId, nodeId,  json.dumps(current_node_history_json ,ensure_ascii=False)  )
            
        elif react_flag == 'waiting_other_agent' and first_run_react_flag == False:
            self.memory_handler.react_current_history_save(sessionId, nodeId, json.dumps(current_node_history_json ,ensure_ascii=False))
         
        elif react_flag == 'end' and first_run_react_flag == True: #第一次运行就运行到结尾了
        
            self.memory_handler.react_current_history_save(sessionId, nodeId, json.dumps(current_node_history_json ,ensure_ascii=False))
        
        elif react_flag == 'end' and first_run_react_flag == False: #第N次运行 运行到结尾了
            self.memory_handler.react_current_history_save(sessionId, nodeId, json.dumps(current_node_history_json ,ensure_ascii=False))
        
        
        #step7 存储 memory # for other agent
        logging.info(f'存储 memory # for other agent')
        if react_flag == 'waiting_other_agent' and first_run_react_flag == True:
            logging.info('#第一次运行 等待agent返回')
            self.memory_handler.react_memory_save(sessionId, nodeId,  current_node_history_json)
        if react_flag == 'waiting_other_agent' and first_run_react_flag == False:
            logging.info('#第N次运行 等待agent返回')
            self.memory_handler.react_memory_save(sessionId, nodeId, current_node_history_json)
        
        elif react_flag == 'end' and first_run_react_flag == True: #第一次运行就运行到结尾了:
            logging.info('#第一次运行就运行到结尾了:')
            self.memory_handler.react_memory_save(sessionId, nodeId,  current_node_history_json)
        
        elif react_flag == 'end' and first_run_react_flag == False: #第N次运行 运行到结尾了
            logging.info('#第N次运行 运行到结尾了')
            self.memory_handler.react_memory_save(sessionId, nodeId, current_node_history_json)
        
        update_flag = self.update_replacement(sessionId, nodeId)
        if update_flag:
            logging.info("变量更新成功！")
        else:
            logging.info("无变量更新或变量更新失败")
        #step8 返回 question_plan
        if react_flag == 'end':
            question_plan = []
        elif react_flag == 'waiting_other_agent':
            question_plan = self.react_get_question_plan(sessionId, nodeId, execute_agent_name)
        else:
            question_plan = []
        return react_flag, question_plan
         



    def get_memory_for_tool(self,sessionId, nodeId):
        '''
                react 节点中 对于一个 主持人， 构建memory的函数。
                只需要将祖先节点弄好即可，不需要加自己，因为自己有 history进行维护
        '''
        nodeType = 'opsgptkg_task' #假设一定是task节点
        tool_ancestor = self.get_tool_ancestor(sessionId, nodeId, nodeType)
        get_messages_res_sorted = self.get_memory_from_ancestor( tool_ancestor, sessionId, role_tags = None) #对于tool,假设都是主持人的工具，所以需要看到所有的memory，无需加tag。
        assembled_memory = self.assemble_memory_for_tool(nodeId, nodeType, get_messages_res_sorted) # tool 的memory需要兼顾以前的格式
        return assembled_memory


    def get_memory_for_dm(self,sessionId, nodeId):
        '''
                react 节点中 对于一个 主持人， 构建memory的函数。
                只需要将祖先节点弄好即可，不需要加自己，因为自己有 history进行维护
        '''
        nodeType = 'opsgptkg_task' #假设一定是task节点
        tool_ancestor = self.get_tool_ancestor(sessionId, nodeId, nodeType)
        get_messages_res_sorted = self.get_memory_from_ancestor( tool_ancestor, sessionId, role_tags = None) #此时是主持人，所以需要看到所有的memory，无需加tag。 对于在我这一侧需要运行的llm，一定是看到所有信息，因为我就是主持人
        assembled_memory = self.assemble_memory_for_reactagent(nodeId, nodeType, get_messages_res_sorted)
        return assembled_memory

    def get_memory_for_computer_agent(self,sessionId, nodeId, execute_agent_name):
            '''
                react 节点中 对于一个 agent_x (电脑agent)， 构建memory的函数
            '''
            nodeType = 'opsgptkg_task' #假设一定是task节点
            tool_ancestor = self.get_tool_ancestor(sessionId, nodeId, nodeType)

            if nodeId not in [nodeinancestor['nodeId'] for nodeinancestor in tool_ancestor]:
                tool_ancestor = tool_ancestor +  [{'nodeId': nodeId, 'nodeType':nodeType}]

            #需要将自己也加上，方便在下一步memory检索的时候把本节点的历史也得到，由于在生成str的时候，第一时间就save本届点的memory，所以这样做是可以的
            #需要注意的是，给agent和给主持人看到的输入是不一样的。 主持人看到的是 memory + node_text + currentnodehistory, currentnodehistory 是文本，因为主持人需要维持一个 结构化的输出。
            #agent看到的是  memory，agent只需要说出一句话即可
            get_messages_res_sorted = self.get_memory_from_ancestor(tool_ancestor, sessionId, execute_agent_name) #此时是调用外部agent，所以需要加tag
            assembled_memory = self.assemble_memory_for_reactagent(nodeId, nodeType, get_messages_res_sorted)
            return assembled_memory
    def get_cur_node_memory(self, sessionId, nodeId):
            """
                获取当前节点的游戏记录，不包含祖先节点。
            """ 
            nodeType = 'opsgptkg_task' #假设一定是task节点
            tool_ancestor = [{'nodeId':nodeId, 'nodeType':nodeType}]
            logging.info(f'tool_ancestor:{tool_ancestor}')
            get_messages_res_sorted = self.get_memory_from_ancestor(tool_ancestor, sessionId, role_tags = None) #此时是主持人，所以需要看到所有的memory，无需加tag。 对于在我这一侧需要运行的llm，一定是看到所有信息，因为我就是主持人
            logging.info(f'get_messages_res_sorted:{get_messages_res_sorted}')
            assembled_memory = self.assemble_memory_for_reactagent(nodeId, nodeType, get_messages_res_sorted)
            return assembled_memory

    def react_get_question_plan(self, sessionId:str, nodeId:str, execute_agent_names : Union[str, List[str]]):
        '''
            如果react模块 react_flag==waiting_other_agent， 则需要返回 question_plan
            可能需要区分人来回答还是大模型来回答
        '''
        logging.info(f"nodeId is {nodeId} , execute_agent_names is {execute_agent_names}")
        toolPlan = []
        if type(execute_agent_names) == str:
            #如果只输入一个agent_name
            execute_agent_names = [execute_agent_names]
            
            
        for execute_agent_name in execute_agent_names:
            if '人类' in execute_agent_name: #需要提交给人
                '''
                example: {'toolDescription': '请用户回答',
                'currentNodeId': 'INT_3',
                'memory': None,
                'type': 'userProblem',
                'questionDescription': {'questionType': 'essayQuestion',
                'questionContent': {'question': '请输入',
                'candidate': None }}}
    
                一定是一个问答题， 无需提问，这里question变成一个固定值了。 最重要的是把memory 也是空， 因为历史信息在对话里已经显示了。
                '''
                tool_one_step= ToolPlanOneStep(
                    **{'toolDescription': '请用户回答',
                    'currentNodeId': nodeId + '%%@@#' + execute_agent_name,
                    'currentNodeInfo':execute_agent_name,
                    'memory': None,
                    'type': 'userProblem',
                    'questionDescription': {'questionType': 'essayQuestion',
                    'questionContent': {'question': '请玩家根据当前情况发言',
                    'candidate': None }}}
                    )
                
                toolPlan.append( tool_one_step.dict())
    
            else: #需要执行agent
                '''
                example :[{
                "toolDescription": "toolDescriptionA",
                "currentNodeId": "INT_1",
                "memory": JsonStr,
                "type":"onlyTool",
                    }]
                '''
    
                
                assembled_memory = self.get_memory_for_computer_agent(sessionId, nodeId, execute_agent_name)
                react_memory = assembled_memory
                if type(react_memory)!= str:
                    react_memory = json.dumps(react_memory, ensure_ascii=False)
    
                # logging.info(f'react_memory is {react_memory}')
                tool_one_step= ToolPlanOneStep(**{
                "toolDescription": execute_agent_name,
                'currentNodeInfo':execute_agent_name,
                "currentNodeId": nodeId + '%%@@#' + execute_agent_name,
                "memory": react_memory,
                "type":"reactExecution",
                    })
            
                
                # toolPlan = [{
                # "toolDescription": execute_agent_name,
                # "currentNodeId": nodeId,
                # "memory": react_memory,
                # "type":"reactExecution",
                #     }]
                
                toolPlan.append(tool_one_step.dict())
            
            
        return toolPlan 



    def get_tool_ancestor(self, sessionId, start_nodeid = '为什么余额宝没收到收益_complaint', start_nodetype = 'opsgptkg_task'):

        #1 对每个nodeid，得到其memory， 首先需要遍历其所有的祖先task节点，将相关信息记录下来
        tool_ancestor = []
        nodeid_in_search = [{'nodeId':start_nodeid, 'nodeType':start_nodetype}]
        nodeid_in_search_all = [{'nodeId':start_nodeid, 'nodeType':start_nodetype}]

        while len(nodeid_in_search)!= 0:
            nodedict_now = nodeid_in_search.pop()
            nodeid_now      = nodedict_now['nodeId']
            nodetype_now    = nodedict_now['nodeType']

            
            #查祖先节点 reverse=True
            neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes={"id": nodeid_now,}, node_type=nodetype_now, reverse=True)
            print(nodeid_now, nodetype_now, neighborNodes, '=========')


            for i in range(len(neighborNodes) ):
                # if  res['resultSet']['rows'][i]['columns'][0] == {}:
                #     continue
            
                # else:
                    nodeid_new = neighborNodes[i].id
                    nodetype_new = neighborNodes[i].type
                    if nodeid_new in [kk['nodeId'] for kk in nodeid_in_search]:  #已经探索过了，不再探索
                        continue

                    elif nodetype_new == 'opsgptkg_task':  #如果是task节点，则加入到tool_plan中，同时继续往前延展。

                        #查询该任务节点有没有收到过response，直接查询count，不用在意count的个数
                        message_res = self.memory_handler.nodecount_get( sessionId, nodeid_new)  #查看这个节点的count计数

                        if len(message_res) == 0:  #这个task节点没有memory 或者没有收到response，则不再往前延展，减少geabase查询个数
                            print(f'#这个task节点{nodeid_new}没有memory 或者没有收到response，则不再往前延展，减少geabase查询个数')
                            continue
                        else:
                            print('#如果是task节点，则加入到tool_plan中，同时继续往前延展。 get_tool_ancestor')
                            tool_ancestor.insert(0, {'nodeId':nodeid_new, 'nodeType':nodetype_new}) # 倒叙插入到图谱中    
                            if  {'nodeId':nodeid_new, 'nodeType':nodetype_new} not in nodeid_in_search_all :
                                nodeid_in_search_all.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                                nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})




                    elif nodetype_now != 'opsgptkg_intent' and nodetype_new == 'opsgptkg_intent':
                        #第一次出现意图节点，需要尝试
                        #print('#第一次出现意图节点，需要尝试')
                        tool_ancestor.insert(0, {'nodeId':nodeid_new, 'nodeType':nodetype_new}) # 倒叙插入到图谱中    
                        if  {'nodeId':nodeid_new, 'nodeType':nodetype_new} not in nodeid_in_search_all :
                                nodeid_in_search_all.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                                nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                        # nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                    elif nodetype_now == 'opsgptkg_intent' and nodetype_new == 'opsgptkg_intent':
                        #从意图节点再次碰到意图节点，终止
                        #print('#从意图节点再次碰到意图节点，终止')
                        pass
                    elif nodetype_new == 'opsgptkg_phenomenon':
                        #如果是事实节点，则继续
                        tool_ancestor.insert(0, {'nodeId':nodeid_new, 'nodeType':nodetype_new}) # 倒叙插入到图谱中   
                        if  {'nodeId':nodeid_new, 'nodeType':nodetype_new} not in nodeid_in_search_all :
                                nodeid_in_search_all.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                                nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})  
                        # nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})

                    else:##如果是不是task节点，也不是意图节点，不加入到tool_plan中，继续延展
                        #print('#如果是不是task节点，也不是意图节点，不加入到tool_plan中，继续延展')
                        if  {'nodeId':nodeid_new, 'nodeType':nodetype_new} not in nodeid_in_search_all :
                                nodeid_in_search_all.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                                nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                        # nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
        
        tool_ancestor_new = []
        for i  in range(len(tool_ancestor)):
            item_i = tool_ancestor[i]
            if item_i not in tool_ancestor_new:
                tool_ancestor_new.append(item_i)
        logging.info(f'geabase_getmemory  tool_ancestor_new  的个数为{len(tool_ancestor_new)}')
        logging.info(f'geabase_getmemory  tool_ancestor  的个数为{len(tool_ancestor)}')
        #print('tool_ancestor_new',  tool_ancestor_new)
        tool_ancestor = tool_ancestor_new
        return tool_ancestor

    def get_memory_from_ancestor(self, tool_ancestor, sessionId, role_tags = None): 
        '''
            给定了一堆祖先节点 + 当前节点，从中提取出memory
            祖先节点
                对于祖先tool 而言，提取出 nodedescription、tool responds
                对于祖先react 而言，提取出 nodedescription（name）， 每一条message
                将这个list 按照时间顺序排好
            当前节点
                对于tool 而言，没有当前节点的memory
                对于react节点而言， 有运行到中间状态的memory
            将这个list 按照时间顺序排好
            按照固定格式输出 memory_list_output

            role_tags  是一系列list,  如果指定为空，则没有约束

        '''
        if role_tags == None:
            role_tags = None
        else:
            role_tags = ['all'] + [role_tags]
        # print(role_tags)
        message_res_list = []
        for i in range(len(tool_ancestor)):
            logging.info(f'geabase_getmemory  查询第{i}个祖先节点')
            # logging.info(tool_ancestor[i])
            nodeId   =  tool_ancestor[i]['nodeId']
            nodeType =  tool_ancestor[i]['nodeType']
            logging.info(f'【查询】memory message_index {nodeId}; sessionId {sessionId} ')
            # if self.gb_handler.geabase_is_react_node(nodeId, nodeType) == False:
            #当前节点为tool or react 节点，一次性获得该节点所有的 chapter的memory数据
            if nodeType == 'opsgptkg_task':
                memory_res = self.memory_manager.get_memory_pool_by_all({ 
                    # "message_index": hash_id(nodeId, sessionId), #nodeId.replace(":", "_").replace("-", "_"), 
                    'user_name':  hash_id(nodeId),
                    "chat_index": sessionId,
                    "role_tags": role_tags,
                    }
                    )
                logging.info(f'memory_res为:{memory_res}')
                message_res = memory_res.get_messages()
                message_res_list = message_res_list + message_res



            elif nodeType == 'opsgptkg_intent':
                #如果祖先节点是意图节点,  意图节点的memory 暂时不分 tag
                memory_res = self.memory_manager.get_memory_pool_by_all({ 
                        "message_index": hash_id(nodeId, sessionId), #nodeId.replace(":", "_").replace("-", "_"), 
                        "chat_index": sessionId, 
                        "role_type": "user"})

                message_res = memory_res.get_messages()
                message_res_list = message_res_list + message_res

        #根据时间排序
        # message_res_list = message_res_list[::-1]  #倒转message， 因为发现tbase存数据是类似堆栈的格式存的。 后来者在上; 似乎不对
        get_messages_res_sorted = self.sort_messages_by_time(message_res_list)
        return get_messages_res_sorted


    def assemble_memory_for_reactagent(self, nodeId, nodeType, get_messages_res_sorted):
        '''
            假设 祖先节点已经选择好了，而且 节点中相关的message也选择好了， 也经过时间排序了
            react 节点中 对于一个 agent_x (电脑agent)， 组装memory的函数
        '''

        if self.gb_handler.geabase_is_react_node(nodeId, nodeType) == False:
            raise ValueError(f'当前应该不是 single 节点才对 ')
        else: #react 节点
            memory_list = []
            for i in range(len( get_messages_res_sorted  ) ):
                if get_messages_res_sorted[i].role_name in ['firstUserInput', 'function_caller', 'user' ]:
                    # # 第一次输入， tool返回， tool描述，
                    # memory_list.append({
                    #         'role_type': get_messages_res_sorted[i].role_type,
                    #         'role_name': get_messages_res_sorted[i].role_name,
                    #         'role_content': get_messages_res_sorted[i].role_content}
                    # )#此处存疑，需要实验后才知道效果如何，注释后，相当于主持人和agent只能看到tool的标题和执行结果，且以list的形式呈现
                    memory_list.append(get_messages_res_sorted[i].role_content)
                elif get_messages_res_sorted[i].role_type in ['react_memory_save']:
                    # react 模块各个角色说的话， 
                    memory_list.append(get_messages_res_sorted[i].role_content)
        return memory_list

    def assemble_memory_for_tool(self, nodeId, nodeType, get_messages_res_sorted):
        if self.gb_handler.geabase_is_react_node(nodeId, nodeType) == False:
            '''            
            '''
            memory_list = []
            for i in range(len( get_messages_res_sorted  ) ):
                if get_messages_res_sorted[i].role_name == 'firstUserInput':
                    memory_list.append({
                            'role_type': 'user',
                            'role_name': 'firstUserInput',
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
                if get_messages_res_sorted[i].role_name == 'user':
                    memory_list.append({
                            'role_type': 'user',
                            'role_name': 'None',
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
                if get_messages_res_sorted[i].role_name == 'function_caller':
                    memory_list.append({
                            'role_type': 'observation',
                            'role_name': 'function_caller',
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
                if get_messages_res_sorted[i].role_type in ['react_memory_save']:
                    # react 模块各个角色说的话， 
                    memory_list.append({
                            'role_type': get_messages_res_sorted[i].role_type,
                            'role_name': get_messages_res_sorted[i].role_name,
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
        else: #react 节点
            raise ValueError(f'当前应该是 tool task 节点才对 ')
            
        return memory_list

    def assemble_memory(self, nodeId, nodeType, get_messages_res_sorted):
        '''
            组装memory
            get_messages_res_sorted 已经根据时间排序好了。 但是对于tool 和  react模块的memory拼装做法有所不同
        '''
        if self.gb_handler.geabase_is_react_node(nodeId, nodeType) == False:
            '''            

            '''
            memory_list = []
            for i in range(len( get_messages_res_sorted  ) ):
                if get_messages_res_sorted[i].role_name == 'firstUserInput':
                    memory_list.append({
                            'role_type': 'user',
                            'role_name': 'firstUserInput',
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
                if get_messages_res_sorted[i].role_name == 'user':
                    memory_list.append({
                            'role_type': 'user',
                            'role_name': 'None',
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
                if get_messages_res_sorted[i].role_name == 'function_caller':
                    memory_list.append({
                            'role_type': 'observation',
                            'role_name': 'function_caller',
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
                if get_messages_res_sorted[i].role_type in ['react_memory_save']:
                    # react 模块各个角色说的话， 
                    memory_list.append({
                            'role_type': get_messages_res_sorted[i].role_type,
                            'role_name': get_messages_res_sorted[i].role_name,
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
        else: #react 节点
            memory_list = []
            for i in range(len( get_messages_res_sorted  ) ):
                if get_messages_res_sorted[i].role_name in ['firstUserInput', 'function_caller', 'user' ]:
                    # 第一次输入， tool返回， tool描述，
                    memory_list.append({
                            'role_type': get_messages_res_sorted[i].role_type,
                            'role_name': get_messages_res_sorted[i].role_name,
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
                elif get_messages_res_sorted[i].role_type in ['react_memory_save']:
                    # react 模块各个角色说的话， 
                    memory_list.append({
                            'role_type': get_messages_res_sorted[i].role_type,
                            'role_name': get_messages_res_sorted[i].role_name,
                            'role_content': get_messages_res_sorted[i].role_content}
                    )
        return memory_list


    
if __name__ == "__main__":


    pass

    #