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
                ouput_result = robust_call_llm(input_query, 'gpt_4')
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
                ouput_result = robust_call_llm(input_query, 'gpt_4',temperature = 0.1)
                logging.info(f'修正后的输出为{ouput_result}')
                llm_result_json = json.loads(ouput_result)
    return llm_result_json

def agent_respond_extract_output(input_str):
    if 'output' not in input_str:
        return input_str
    input_str = input_str.split('output')[-1]  #取output后面的值
    input_str = input_str.replace('"', '').replace(':', '').replace('}', '').replace('{', '') #去除掉可能的符号
    return input_str
    


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
    
 
    def robust_call_llm_with_llmname(self, input_query, rootNodeId, stop = None, temperature = 0, presence_penalty=0):

        #logging.info('using a gpt_4')
        res = call_llm(input_content = input_query, llm_model = 'gpt_4',  stop = stop,temperature=temperature, presence_penalty=presence_penalty,
                       llm_config=self.llm_config)
        return res


        model_name = self.gb_handler.get_extra_tag(  rootNodeId = rootNodeId, rootNodeType = 'opsgptkg_task', key = 'model_name')
        logging.info(f'model_name is {model_name}')
        if model_name == None:
            model_name = 'gpt_4'
        if model_name == 'gpt_4':
            try:
                logging.info('using a gpt_4')
                res = call_llm(input_content = input_query, llm_model = 'gpt_4',  stop = stop,temperature=temperature, presence_penalty=presence_penalty)
            except:
                logging.info('using Qwen2_72B_Instruct_OpsGPT')
                res = call_llm(input_content = input_query, llm_model = 'Qwen2_72B_Instruct_OpsGPT',stop = stop, temperature=temperature,presence_penalty=presence_penalty)
            return res
        else:
            try:
                logging.info('using Qwen2_72B_Instruct_OpsGPT')
                res = call_llm(input_content = input_query, llm_model = 'Qwen2_72B_Instruct_OpsGPT',stop = stop, temperature=temperature,presence_penalty=presence_penalty)
            except:
                logging.info('using a gpt_4')
                res = call_llm(input_content = input_query, llm_model = 'gpt_4',  stop = stop,temperature=temperature, presence_penalty=presence_penalty)
            return res

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
        

    def react_running(self, sessionId, nodeId, nodeType, agent_respond = ''):
        '''
            react 模块 运行

        '''
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

    def react_get_question_plan(self, sessionId, nodeId, execute_agent_name):
        '''
            如果react模块 react_flag==waiting_other_agent， 则需要返回 question_plan
            可能需要区分人来回答还是大模型来回答
        '''
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
            toolPlan = [ {'toolDescription': '请用户回答',
            'currentNodeId': nodeId,
            'memory': None,
            'type': 'userProblem',
            'questionDescription': {'questionType': 'essayQuestion',
            'questionContent': {'question': '请玩家根据当前情况发言',
            'candidate': None }}} ]

            return toolPlan
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
            toolPlan = [{
            "toolDescription": execute_agent_name,
            "currentNodeId": nodeId,
            "memory": react_memory,
            "type":"reactExecution",
                }]
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
            #print(nodeid_now, nodetype_now, neighborNodes, '=========')


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
            raise ValueError(f'当前应该是 react 节点才对 ')
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
        response = call_llm(input_content = prompt_temp, llm_model = 'Qwen2_72B_Instruct_OpsGPT',llm_config=self.llm_config)# qwen_chat_14b #Qwen_72B_Chat_vLLM
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
            start_nodeid = '为什么余额宝没收到收益_complaint', start_nodetype = 'opsgptkg_intent', agent_respond = None):
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
            logging.info(f'react节点{start_nodeid}没有执行完，需要继续执行')
            runningFlag, reactPlan = self.react_running( sessionId, start_nodeid, start_nodetype, agent_respond )

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
                                runningFlag, reactPlan = self.react_running( sessionId, nodeid_new, nodetype_new, None )#这种时候是react节点第一次运行，一定是主持人，一定要看到全局信息

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
                memory = self.get_memory_for_tool(sessionId, nodeId)
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