

import uuid
import json
import os
import sys

#muagent 依赖包
from muagent.connector.schema import Message
from muagent.schemas.db import TBConfig
from muagent.db_handler import *
from muagent.connector.memory_manager import TbaseMemoryManager
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.schemas.db import GBConfig


from muagent.connector.schema import Message
from src.utils.call_llm import call_llm, extract_final_result, robust_call_llm

import logging
logging.basicConfig(level=logging.INFO)

from src.geabase_handler.geabase_handlerplus import GB_handler
from src.utils.normalize import hash_id





from muagent.db_handler import GeaBaseHandler
from muagent.schemas.common import GNode, GEdge
from muagent.schemas.db import GBConfig




class qa_class():
    def __init__(
            self, 
            memory_manager, 
            geabase_handler,  
            uesr_query = '',
            start_nodeid = '为什么', 
            start_nodetype = 'opsgptkg_intent',
            llm_config=None
        ):
        # self.option = option
        self.memory_manager = memory_manager
        self.uesr_query = uesr_query
        self.start_nodeid = start_nodeid
        self.start_nodetype = start_nodetype
        self.geabase_handler = geabase_handler
        

        # self.gb_handler = GB_handler(self.option, self.GeaBaseClient)
        self.gb_handler = GB_handler(geabase_handler)
        self.llm_config = llm_config


    def full_link_summary(self):
        '''
            用户询问整条链路在做什么
        '''
        resstr_llm_summary = None
        resstr = self.geabase_nodediffusion_qa()
        print(resstr)
        print(f'full_link_summary prompt的长度为 {len(resstr)}')
        resstr_llm_summary = call_llm(input_content = resstr, llm_model = None,llm_config=self.llm_config)

        visualization_url = self.get_visualization_url()


        return resstr_llm_summary

    def next_step_summary(self):
        '''
            用户询问下一步应该做什么
            根据  self.uesr_query, self.start_nodeid
        '''
        #获取整个流程
        full_graph_info = self.geabase_handler.get_hop_infos(attributes={"id": self.start_nodeid,}, node_type="opsgptkg_intent", hop = 15 )
        full_graph_info_str = str(full_graph_info.nodes) + '\n' + str(full_graph_info.edges) + '\n'
        prompt = \
        f'''
        你是一个数据内容查询专家，目前的任务是根据full_graph_info信息，回答用户的问题
        ##注意##
        full_graph_info 是一个具体的流程信息，包含了节点和边的信息
        用户的问题都是问这个流程的问题， 比如用户问XXX的第一步是什么， 其实等价于问这个流程的第一步是什么

        full_graph_info:{full_graph_info_str}

        用户的query : {self.uesr_query}

        请回答用户的问题
        '''
        print(prompt)
        print(f'prompt的长度为 {len(prompt)}')

        res = call_llm(input_content = prompt, llm_model = None, llm_config=self.llm_config)
        
        return res


    def get_referred_node(self):
        '''
            根据用户query， 以及整个链路的节点描述，得到用户指代的节点
                使用 self.uesr_query, self.start_nodeid
        '''

        #获取整个流程
        full_graph_info = self.geabase_handler.get_hop_infos(attributes={"id": self.start_nodeid,}, node_type="opsgptkg_intent", hop = 15 )
        node_info_str = str(full_graph_info.nodes)
        prompt = \
        f'''
        你是一个数据内容查询专家，目前的任务是根据 node 信息和用户query，给出和用户query最相近的一个node

        node信息:{node_info_str}

        用户的query : {self.uesr_query}

        返回和用户query相关的一个节点的id
        '''
        print(prompt)
        print(f'prompt的长度为 {len(prompt)}')
        res = call_llm(input_content = prompt, llm_model = None,llm_config=self.llm_config)
        # res = robust_call_llm(prompt)
        return res


    def get_visualization_url(self):
        #根据当前意图节点，返回查询图结构的url
        prefix = '___'
        intermediate_separator = '##__##'

        
        return f'{os.environ["sre_agent_flow_url"]}{prefix}{self.start_nodeid}{intermediate_separator}{self.start_nodetype}' #三个___为保留字符

    def geabase_nodediffusion_qa(self):
        '''
            遍历整个计划，返回相应的结构描述
        '''


        #resstr = '你是一个计划总结大师，可以用比较通俗易懂的语言总结一个计划。 以下计划由一个知识图谱表示。请将其总结为自然语言的方式 \n'


        # #1.假设当前节点已经运行完，得到后面的tool. 如果为事实节点，则需要采用大模型进行判断
        # tool_plan = []
        # nodeid_in_search = [{'nodeId':self.start_nodeid, 'nodeType':self.start_nodetype}]

        # while len(nodeid_in_search)!= 0:
        #     nodedict_now = nodeid_in_search.pop()
        #     nodeid_now      = nodedict_now['nodeId']
        #     nodetype_now    = nodedict_now['nodeType']

        #     if nodetype_now == 'opsgptkg_analysis':
        #         if self.gb_handler.geabaseGetOnlyOneNodeInfoWithKey( rootNodeId = nodeid_now, rootNodeType = nodetype_now, key = 'accesscriteria') == 'or':
        #             #当链接到node_result_1节点的node_phenomena都满足时，才激活node_result_1
        #             resstr += f'当链接到{nodeid_now}节点的node_phenomena只要满足一个时，就能激活{nodeid_now}'
        #         else:
        #             resstr += f'当链接到{nodeid_now}节点的node_phenomena都满足时，才能激活{nodeid_now}'

        #         #nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
        #     if nodetype_now == 'opsgptkg_phenomenon':
        #         '''
        #             node_phenomena_1 与 结论 node_result_1 相连，node_result_1的内容为  热点账户问题，无需应急。
        #             node_phenomena_1 与 结论 node_result_4 相连，node_result_4的内容为  请排查其他原因
        #         '''
        #         neighbor_node_id_list       = self.gb_handler.get_children_id( nodeid_now, nodetype_now)   #get_nodeid_from_res(res)
        #         next_node_description_list  = self.gb_handler.get_children_description( nodeid_now, nodetype_now)  #get_nodedescription_from_res(res)
        #         for  i in range(len(neighbor_node_id_list)):
        #             resstr += f'{nodeid_now}节点 与 {neighbor_node_id_list[i]} 相连，节点{neighbor_node_id_list[i]}的内容为： {next_node_description_list[i]}'
        #     # print('==================')
        #     # print(f'nodeid_in_search is {nodeid_in_search}')
        #     # print('=================')



            
        #     if self.gb_handler.all_nodetype_check(nodeid_now, nodetype_now, 'opsgptkg_task') == True:
        #         # 后续节点都是task节点，
        #         neighbor_node_id_list       = self.gb_handler.get_children_id( nodeid_now, nodetype_now)   #get_nodeid_from_res(res)
        #         next_node_description_list  = self.gb_handler.get_children_description( nodeid_now, nodetype_now)  #get_nodedescription_from_res(res)

        #         if nodetype_now == 'opsgptkg_schedule': #操作计划节点后第一次出现任务节点
        #             if len(neighbor_node_id_list) >= 2:
        #                 resstr += f'并行执行{len(neighbor_node_id_list)}个任务：\n'
        #             else:
        #                 resstr += f'执行{len(neighbor_node_id_list)}个任务：\n '
        #             for i in range(len(neighbor_node_id_list)):
        #                 resstr += f' {neighbor_node_id_list[i]} 的内容是 : {next_node_description_list[i]}  \n'
        #         else:
        #             if len(neighbor_node_id_list) >= 2:
        #                 resstr += f'{nodeid_now}后面是并行执行{len(neighbor_node_id_list)}个任务：\n'
        #             else:
        #                 resstr += f'{nodeid_now}后面是执行{len(neighbor_node_id_list)}个任务：\n '
                    
        #             for i in range(len(neighbor_node_id_list)):
        #                 resstr += f'{nodeid_now}后面是{neighbor_node_id_list[i]}, {neighbor_node_id_list[i]}的内容是:{next_node_description_list[i]} \n'

        #         for i in range(len(neighbor_node_id_list)): #往后扩展
        #             nodeid_in_search.append({'nodeId':neighbor_node_id_list[i], 'nodeType':'opsgptkg_task'})

        #     elif self.gb_handler.all_nodetype_check(nodeid_now, nodetype_now, 'opsgptkg_phenomenon') == True: 
        #         #后续所有节点都是判断节点, 则进行大模型判断，选中其中一个 phenomenon 进入后续，同时在phenomenons节点上记录memory
        #         neighbor_node_id_list       = self.gb_handler.get_children_id( nodeid_now, nodetype_now)   #get_nodeid_from_res(res)
        #         next_node_description_list  = self.gb_handler.get_children_description( nodeid_now, nodetype_now)  #get_nodedescription_from_res(res)


        #         resstr += f'{nodeid_now}后面有{len(neighbor_node_id_list)}种可能 '
        #         for i in range(len(neighbor_node_id_list)): #往后扩展
        #             resstr += f'{neighbor_node_id_list[i]}:{next_node_description_list[i]}; '
        #             resstr += '\n'

        #         for i in range(len(neighbor_node_id_list)): #往后扩展
        #             nodeid_in_search.append({'nodeId':neighbor_node_id_list[i], 'nodeType':'opsgptkg_phenomenon'})




        #     elif self.gb_handler.all_nodetype_check(nodeid_now, nodetype_now, 'opsgptkg_schedule') == True:
        #         #后面都是操作计划节点，假设只有一个操作计划节点
        #         neighbor_node_id_list       = self.gb_handler.get_children_id( nodeid_now, nodetype_now)   #get_nodeid_from_res(res)
        #         next_node_description_list  = self.gb_handler.get_children_description( nodeid_now, nodetype_now)  #get_nodedescription_from_res(res)
        #         # neighbor_node_id_list       = get_nodeid_from_res(res)
        #         # next_node_description_list  = get_nodedescription_from_res(res)
        #         for i in range(len(neighbor_node_id_list)):
        #             resstr = resstr + '操作计划名：' + self.gb_handler.geabase_getDescription(neighbor_node_id_list[i], 'opsgptkg_schedule') + '\n' + '最开始，'
        #             nodeid_in_search.append({'nodeId':neighbor_node_id_list[i], 'nodeType':'opsgptkg_schedule'})


        #     elif self.gb_handler.all_nodetype_check(nodeid_now, nodetype_now, 'opstpgkg_analysis') == True:
        #         neighbor_node_id_list       = self.gb_handler.get_children_id( nodeid_now, nodetype_now)   #get_nodeid_from_res(res)
        #         next_node_description_list  = self.gb_handler.get_children_description( nodeid_now, nodetype_now)  #get_nodedescription_from_res(res)

        #         # neighbor_node_id_list       = get_nodeid_from_res(res)
        #         # next_node_description_list  = get_nodedescription_from_res(res)
        #         for i in range(len(neighbor_node_id_list)):

        #             resstr += f'{nodeid_now} 与 {neighbor_node_id_list[i]} 相连，{neighbor_node_id_list[i]}的内容为 {next_node_description_list[i]} '
        #             nodeid_in_search.append({'nodeId':neighbor_node_id_list[i], 'nodeType':'opsgptkg_schedule'})

        #     else:
        #         neighbor_node_id_list       = self.gb_handler.get_children_id( nodeid_now, nodetype_now)   #get_nodeid_from_res(res)
        #         neighbor_node_type_list  = self.gb_handler.get_children_type( nodeid_now, nodetype_now)  #get_nodedescription_from_res(res)

        #         for i in range(len(neighbor_node_id_list) ):

        #                 nodeid_new = neighbor_node_id_list[i]
        #                 nodetype_new = neighbor_node_type_list[i]
                        
        #                 #只要后续有节点就继续扩展
        #                 nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})

            
        
        full_graph_info = self.geabase_handler.get_hop_infos(attributes={"id": self.start_nodeid,}, node_type="opsgptkg_intent", hop = 15 )
        full_graph_info_str = str(full_graph_info.nodes) + '\n' + str(full_graph_info.edges) + '\n'
        resstr = \
        f'''
        你是一个计划总结大师，可以用比较通俗易懂的语言总结一个计划。  
        计划由知识图谱的形式表示，即full_graph_info。 
        
        
        ##注意##
        full_graph_info 是一个具体的流程信息，包含了节点和边的信息
        

        full_graph_info:{full_graph_info_str}


        '''

        resstr += ' \n \n 请总结上述排查计划，注意有些情况下可以概况总结处理.注意,请直接输出总结结果，不要输出其他的话:' 
        return  resstr


if __name__ == "__main__":


    pass