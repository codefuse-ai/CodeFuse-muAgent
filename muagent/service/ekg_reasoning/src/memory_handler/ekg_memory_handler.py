import uuid
import json
import os
import sys
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


from muagent.connector.schema import Message
from src.utils.call_llm import call_llm,extract_final_result
import logging
logging.basicConfig(level=logging.INFO)

# from loguru import logger as logging
from src.geabase_handler.geabase_handlerplus import GB_handler
from src.utils.normalize import hash_id

#muagent 依赖包
from muagent.connector.schema import Message
from muagent.schemas.db import TBConfig
from muagent.db_handler import *
from muagent.connector.memory_manager import TbaseMemoryManager
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.schemas.db import GBConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.service.ekg_inference import IntentionRouter


class memory_handler_ekg():
    '''
        在图谱推理过程中使用到的 和memory相关的tool
        只包含纯用memory的函数
    '''
    def __init__(self,  memory_manager, geabase_handler):
        self.geabase_handler = geabase_handler
        self.memory_manager  = memory_manager
        self.gb_handler = GB_handler(self.geabase_handler) #gb_handler 以  geabase_handler 为基础，封装了一些处理逻辑

        


    def is_nodetask_completed(self, sessionId, nodeId, nodeType,):
        '''
            判断节点对于的任务当前是否完成了
                查询count即可
            {'chapter': 2,  'section': 10 , 'allsection': '20', 'nodestage': 'running' #end # notStart}
        '''
        if nodeType != 'opsgptkg_task': #如果不是任务节点，一定执行完了. 只有任务节点才能执行多次？
            return True
        memory_manager_res= self.memory_manager.get_memory_pool_by_all({ 
                                                        #    "chat_index": sessionId, 
                                                           "message_index" : hash_id( nodeId, sessionId, '_count'),
                                                          })
        get_messages_res = memory_manager_res.get_messages()
        if get_messages_res == []: #没有查询到count数据
            return False
        if json.loads(get_messages_res[0].role_content)['nodestage'] == 'end':
            return True
        else:
            return False

    
    def append_tools(self, tool_information, chat_index, nodeid, user_name):
        #tool_information: dict, chat_index: str, nodeid: str, user_name: str)
        '''
            对于observation式的结果，一次录入四个到 memory里， 需要自己写代码
        '''
        pass

    def intention_first_input_save(self, sessionId, currentNodeId, role_content,  
            hashpostfix = '_firstIntentRecognitionCall' , 
            user_name = "None", 
            role_name = "firstIntentRecognitionCall",
            role_type = "intentRecognition"):
            '''
                第一次意图识别输入存入到memory里
            '''
            message = Message(
                chat_index= sessionId,  #self.sessionId
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix),  
                user_name = user_name,
                role_name = role_name, # agent 名字，
                role_type = role_type, 
                role_content = role_content, # 第一次意图识别的输入
            )
            self.memory_manager.append(message)

    def intention_problem_save(self, sessionId, currentNodeId, role_content,  
            hashpostfix = '_IntentRecognitionProblem' , 
            user_name = "None", 
            role_name = "intentRecognitionProblem",
            role_type = "intentRecognition"):
            #存问题
            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix),  
                user_name = user_name,
                role_name = role_name, 
                role_type = role_type, 
                role_content = role_content, 
            )
            self.memory_manager.append(message)

    def intention_idinfo_save(self, sessionId, currentNodeId, role_content,  
            hashpostfix = '_IntentRecognitionCanditateId' , 
            user_name = "None", 
            role_name = "intentRecognitionCanditateId",
            role_type = "intentRecognition"):
            #存选项id
            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix),  
                user_name = user_name,
                role_name = role_name, 
                role_type = role_type, 
                role_content = role_content, 
            )
            self.memory_manager.append(message)

    def intention_save_return_answer(self, sessionId, currentNodeId, role_content,  
            hashpostfix = '_IntentRecognitionUserAnswer' , 
            user_name = "None", 
            role_name = "intentRecognitionUserAnswer",
            role_type = "intentRecognition"):
            '''
                保存从用户侧得来的回答
            '''
            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix),  
                user_name = user_name,
                role_name = role_name, 
                role_type = role_type, 
                role_content = role_content, 
            )
            self.memory_manager.append(message)
    def intention_get_all(self, sessionId  ):
        '''
            获取所有 role_type == 'intentRecognition'  的memory，并整合成一个list, 再将这个list转换为str
        '''
        memory_manager_res= self.memory_manager.get_memory_pool_by_all({ 
                                                                "chat_index": sessionId, 
                                                                })
        get_messages_res = memory_manager_res.get_messages()
        intention_refere_memory = []
        for i in range(len(get_messages_res)):
            if get_messages_res[i].role_type == 'intentRecognition':
                intention_refere_memory.append( get_messages_res[i].json())
        intention_refere_memory_str  =  json.dumps(intention_refere_memory, ensure_ascii=False)
        return intention_refere_memory_str
    

    def first_query_save(self, sessionId, currentNodeId, role_content,  
            hashpostfix = '-firstUserInput' , 
            user_name = "None", 
            role_name = "firstUserInput",
            role_type = "user"):
            '''
                第一次query input save， 记录在意图节点上
            '''
            
            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix),  
                user_name = user_name,
                role_name = role_name, 
                role_type = role_type, 
                role_content = role_content, 
            )
            self.memory_manager.append(message)

    def get_nodeobservation_current(self, sessionId, currentNodeId  , start_nodetype  ):
        '''
            得到该tool节点的输入值。当且仅当节点类型为tool时能得到返回值
        '''
        pass
        if start_nodetype != 'opsgptkg_task':
            raise ValueError("只有task节点能取得执行的返回值")

        chapter = self.nodecount_get_key( sessionId, currentNodeId, key = 'chapter')
        if chapter == None:
                chapter = 1
        



        aaa = self.memory_manager.get_memory_pool_by_all({ 
            # "message_index": hash_id(currentNodeId, sessionId, f'_chapter{chapter}-toolResponse'), #加上了toolResponse检索不到，可能时超长度了
            "message_index": hash_id(currentNodeId, sessionId, f'_chapter{chapter}'), #
            "chat_index": sessionId, 
            "role_name": "function_caller", 
            "role_type": "observation"})

        bbb = aaa.get_messages()
        if len(bbb) == 0:
            return None
        observation_current = bbb[-1].role_content
        return observation_current

    def nodeid_in_subtree_get(self, currentNodeId, sessionId):
        hashpostfix = '-nodeid_in_subtree' 
        memory_manager_res= self.memory_manager.get_memory_pool_by_all({ 
                                                           "chat_index": sessionId, 
                                                        #    "message_index" : hash_id( currentNodeId, sessionId, hashpostfix),
                                                        #    "role_type": "nodeid_in_subtree",
                                                          })
        get_messages_res = memory_manager_res.get_messages()
        return get_messages_res
    def nodeid_in_subtree_save(self, sessionId, currentNodeId, role_content,  
            hashpostfix = '-nodeid_in_subtree' , 
            user_name = "None", 
            role_name = "nodeid_in_subtree",
            role_type = "nodeid_in_subtree"):
            '''
                -nodeid_in_subtree save, 记录在意图节点上
            '''
            if type(role_content)!= str:
                role_content = json.dumps(role_content, ensure_ascii=False)

            # logging.info(f'nodeid_in_subtree_save start, currentNodeId is {currentNodeId} , sessionId is {sessionId},hashpostfix is {hashpostfix}')
            # logging.info(f'user_name is {user_name} , role_name is {role_name}, role_type is {role_type}, role_content is {role_content}')
            # logging.info(f'type(role_content) is  {type(role_content)}')
            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix),  
                user_name = user_name,
                role_name = role_name, 
                role_type = role_type, 
                role_content = role_content, 
            )
            
            self.memory_manager.append(message)
            logging.info('nodeid_in_subtree_save end')


    def init_react_count(self, sessionId, currentNodeId):
        '''
            当react的状态是 end 或者为空的时候调用此函数，进行初始化 或者 chapter + 1

            #{'chapter': 2,  'section': 10 , 'allsection': '20', 'nodestage': 'running' #end # notStart}
        '''
        count_info = self.nodecount_get(sessionId, currentNodeId)
        if count_info == []:
            #所有都设置为1，状态是running
            role_content={'chapter': 1,  'section': 0 , 'allsection': 0, 'nodestage': 'running' }
        else:
            role_content = count_info[0].role_content
            role_content = json.loads(role_content)
            role_content['chapter'] = role_content['chapter']  + 1
        
        if role_content['chapter'] >=8:
            raise ValueError("单个节点chapter超过了8次，退出")
        
        self.nodecount_set(sessionId, currentNodeId, role_content)


        memory_manager_res= self.memory_manager.get_memory_pool_by_all({ 
                                                        #    "chat_index": sessionId, 
                                                           "message_index" : hash_id( currentNodeId, sessionId, '_count'),

                                                          })
        get_messages_res = memory_manager_res.get_messages()
        return get_messages_res
        
    def nodecount_get(self, sessionId, currentNodeId):
        '''
            得到当前node的 count数据
            #{'chapter': 2,  'section': 10 , 'allsection': '20', 'nodestage': 'running' #end # notStart}
        '''
        memory_manager_res= self.memory_manager.get_memory_pool_by_all({ 
                                                        #    "chat_index": sessionId, 
                                                           "message_index" : hash_id( currentNodeId, sessionId, '_count'),

                                                          })
        get_messages_res = memory_manager_res.get_messages()
        return get_messages_res

    def nodecount_get_key(self, sessionId, currentNodeId,key = 'chapter'):
        '''
            得到当前node的 count数据
            #{'chapter': 2,  'section': 10 , 'allsection': '20', 'nodestage': 'running' #end # notStart}
        '''
        memory_manager_res= self.memory_manager.get_memory_pool_by_all({ 
                                                        #    "chat_index": sessionId, 
                                                           "message_index" : hash_id( currentNodeId, sessionId, '_count'),
                                                          })
        get_messages_res = memory_manager_res.get_messages()
        if get_messages_res == []:
            return None
        else:
            role_content = get_messages_res[0].role_content
            role_content = json.loads(role_content)
            return role_content[key]

    def nodecount_set_key(self, sessionId, currentNodeId, key='nodestage', value='running'):
        '''
            对nodecount的某一个key进行修改
        '''
        get_messages_res = self.nodecount_get( sessionId, currentNodeId)
        node_count_info  = get_messages_res[0].role_content
        node_count_info  = json.loads(node_count_info)
        node_count_info[key] = value

        self.nodecount_set( sessionId, currentNodeId, node_count_info)

    def nodecount_set(self, sessionId, currentNodeId, 
        role_content={'chapter': 2,  'section': 10 , 'allsection': '20', 'nodestage': 'running' }):

            if type(role_content) != str:
                role_content = json.dumps(role_content, ensure_ascii=False)
            hashpostfix_all = '_count'
            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix_all),  
                user_name =  hash_id(currentNodeId),
                role_name = 'count', 
                role_type = 'None', 
                role_content = role_content, 
            )
            self.memory_manager.append(message)
    
    def tool_nodecount_add_chapter(self, sessionId, currentNodeId):
        count_res =  self.nodecount_get(sessionId, currentNodeId) 
        if count_res == []:
            count_info = {'chapter': 1,  'section': 1 , 'allsection': '1', 'nodestage': 'end' }
            logging.info(f'节点{sessionId} 的 count_info现在是{count_info}')
            self.nodecount_set( sessionId, currentNodeId,count_info)  #重写count数据，
        else:
            count_info = count_res[0].role_content #{'chapter': 2,  'section': 10 , 'allsection': '20', 'nodestage': 'running' )
            count_info = json.loads(count_info)
            count_info['chapter'] = count_info['chapter'] + 1

            logging.info(f'节点{sessionId} 的 count_info现在是{count_info}')
            self.nodecount_set( sessionId, currentNodeId,count_info)  #重写count数据，

    def tool_nodedescription_save(self, sessionId, currentNodeId, role_content, user_input_memory_tag=None): 
            '''
                将 tool 的 description 存入到memory中, 分成 chapter
                后缀是 _chapter1-userinput

                将user_name 设置为 currentNodeId
                user_name = currentNodeId

                # 如果节点上有tag，则需要强制将tag写入到节点memory中
                # 对于tool的问题和回答，强制放入到 all 中
                # tool的可见范围也是 all
            '''
            if self.gb_handler.get_extra_tag(  currentNodeId,  'opsgptkg_task',  'ignorememory') == 'True':
                return 0

            hashpostfix = '-userinput' 
            user_name = currentNodeId
            role_name = 'user'
            role_type = "userinput"

            node_count_res = self.nodecount_get( sessionId, currentNodeId)
            if node_count_res == []:
                chapter = 1
            else:
                role_content_withchapter = node_count_res[0].role_content
                role_content_withchapter = json.loads(role_content_withchapter)
                chapter = role_content_withchapter['chapter']

            if user_input_memory_tag == None:
                role_tags_ = 'all'
            else:
                role_tags_ = user_input_memory_tag
            hashpostfix_all = f'_chapter{chapter}' + hashpostfix
            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix_all),  
                user_name =  hash_id(user_name),
                role_name = role_name, 
                role_type = role_type, 
                role_content = role_content, 
                role_tags= role_tags_
            )
            
            self.memory_manager.append(message)




    def react_nodedescription_save(self, sessionId, currentNodeId, role_content): 
            '''
                将 react 的 name 存入到memory中, 分成 chapter。由于react模式的description都太长了，所以目前只保留name
                由于react模式的description都太长了，所以目前只保留name。此处可以修改 pass
                后缀是 _chapter1-userinput
                

                将user_name 设置为 currentNodeId
                user_name = currentNodeId

                # 如果节点上有tag，则需要强制将tag写入到节点memory中
                对于react的name，强制放入到 tag all 中
            '''

            hashpostfix = '-userinput' 
            user_name = currentNodeId
            role_name = 'user'
            role_type = "userinput"

            node_count_res = self.nodecount_get( sessionId, currentNodeId)
            if node_count_res == []:
                chapter = 1
            else:
                chapter = json.loads(node_count_res[0].role_content)['chapter']  
            
            hashpostfix_all = f'_chapter{chapter}' + hashpostfix
            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix_all),  
                user_name = hash_id(user_name),
                role_name = role_name, 
                role_type = role_type, 
                role_content = role_content, 
                role_tags=", ".join([ "all"])
            )
            
            self.memory_manager.append(message)


    def react_memory_save(self, sessionId, currentNodeId, llm_res):
        '''
            将一个node中  llm的返回值 解析成json，存储在memory里。 每次覆盖式存储。 存主持人说的话、其他agent说的话； 同时修改count中的计数
        
        llm_str = llm_result_truncation + '":[]}]'
        llm_result_truncation = '[\n    {"action": {"agent_name": "主持人"}, "Dungeon_Master": [{"content": "狼人时刻开始，以下玩家是狼人：player_1（狼人-1），李四（人类玩家）（狼人-2）。", "memory_tag":["agent_1", "人类agent"]}]},\n    {"action": {"agent_name": "agent_1", "player_name":"player_1"}, "observation'
        '''

        #1. 解析 llm的输出
        if type(llm_res) == str:
            llm_res_json = json.loads(llm_res)
        else:
            llm_res_json = llm_res
        logging.info(f' llm_res是{llm_res}')
        # logging.info(f' llm_res_json是{llm_res_json}')
        section = 0
        memory_save_info_list = []
        for i in range(len(llm_res_json)):
            if llm_res_json[i]['action'] == 'taskend':
                #任务执行完毕
                break
            agent_name = llm_res_json[i]['action']['agent_name']
            if agent_name == '主持人':
                player_name = '主持人'
                for j in range(len(llm_res_json[i]['Dungeon_Master'])):
                    content  = llm_res_json[i]['Dungeon_Master'][j]['content']
                    memory_tag  = llm_res_json[i]['Dungeon_Master'][j]['memory_tag']
                    section += 1
                    memory_save_info_list.append([player_name, agent_name, content, memory_tag, section])
            else:
                logging.info(f' llm_res_json[i]是{llm_res_json[i]}')
                if  llm_res_json[i]['observation'] == []:
                    continue
                player_name = llm_res_json[i]['action']['player_name']
                for j in range(len(llm_res_json[i]['observation'])):
                    content  = llm_res_json[i]['observation'][j]['content']
                    memory_tag  = llm_res_json[i]['observation'][j]['memory_tag']
                    section += 1
                    memory_save_info_list.append([player_name, agent_name, content,  memory_tag, section])
        

        if 'taskend' not in  json.dumps(llm_res,  ensure_ascii=False)   and  memory_save_info_list[-1][1] != '主持人': 
            #现在还没有run到最后。那么            #最后一个observation，这个是幻觉，主持人替其他玩家说的话， 不能存入到memory里
            #如果run到最后了， 那么最后一个observation是本次填充的
            memory_save_info_list = memory_save_info_list[0:-1]

        logging.info(f'memory_save_info_list is {memory_save_info_list}')
        
        #2. 将llm的输出存入到memory中，更新，已经写入的就不更新了
        hashpostfix = '_reactmemory' 
        user_name = currentNodeId
        # role_name = 'userinput'
        role_type = "react_memory_save"

        node_count_res = self.nodecount_get( sessionId, currentNodeId)
        if node_count_res == []:
            chapter = 1
        else:
            chapter = json.loads(node_count_res[0].role_content)['chapter']  
        
        
        for i in range(len(memory_save_info_list)):
            player_name, agent_name, content,  memory_tag, section = memory_save_info_list[i]
            hashpostfix_all = f'_chapter{chapter}_section{section}' + hashpostfix

            
            memory_manager_res= self.memory_manager.get_memory_pool_by_all({ 
                                                # "chat_index": sessionId, 
                                                "message_index" : hash_id(currentNodeId, sessionId, hashpostfix_all),

                                                })
            get_messages_res = memory_manager_res.get_messages()
            if get_messages_res != []:
                #这一条数据已经有了，不用重复写入，只更新没有写入的
                continue

            user_input_memory_tag = self.gb_handler.user_input_memory_tag(currentNodeId, 'opsgptkg_task')
            if user_input_memory_tag == None:
                memory_tag= memory_tag
            else:
                memory_tag = [user_input_memory_tag]

            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix_all),  
                user_name = hash_id(user_name),#currentNodeId
                role_name = agent_name, 
                role_type = 'react_memory_save', 
                role_content = f'{player_name} : {content}',    # 这里能看到的 谁说了什么话
                role_tags=", ".join(memory_tag)
            )
            
            self.memory_manager.append(message)
        
        #3. 更新section,覆盖式更新
        node_count_res = self.nodecount_get( sessionId, currentNodeId)
        role_content_nodeinfo = json.loads(node_count_res[0].role_content)
        role_content_nodeinfo['section'] = len(memory_save_info_list)  
        self.nodecount_set( sessionId, currentNodeId, role_content_nodeinfo)

    def react_current_history_save(self, sessionId, currentNodeId, role_content):
            hashpostfix = '_his'
            user_name = currentNodeId
            role_name = 'history'
            role_type = "DM"

            node_count_res = self.nodecount_get( sessionId, currentNodeId)
            if node_count_res == []:
                chapter = 1
            else:
                chapter = json.loads(node_count_res[0].role_content)['chapter']  
            
            hashpostfix_all = f'_chapter{chapter}' + hashpostfix
            message = Message(
                chat_index= sessionId,  
                message_index=  hash_id(currentNodeId, sessionId, hashpostfix_all),  
                user_name = hash_id(user_name),
                role_name = role_name, 
                role_type = role_type, 
                role_content = role_content, 
                
            )
            
            self.memory_manager.append(message)

    def react_current_history_get(self, sessionId, currentNodeId): 
            '''
                得到当前的current_history
            '''
            node_count_res = self.nodecount_get( sessionId, currentNodeId)
            if node_count_res == []:
                chapter = 1
            else:
                chapter = json.loads(node_count_res[0].role_content)['chapter'] 
            
            hashpostfix = '_his'
            hashpostfix_all = f'_chapter{chapter}' + hashpostfix
            print(currentNodeId, sessionId, hashpostfix_all)
            memory_manager_res= self.memory_manager.get_memory_pool_by_all({ 
                                                        #    "chat_index": sessionId, 
                                                           "message_index" : hash_id(currentNodeId, sessionId, hashpostfix_all),
                                                           "role_name" : 'history',
                                                           "role_type" : "DM"
                                                          })
            get_messages_res = memory_manager_res.get_messages()
            return get_messages_res[0].role_content


    def tool_observation_save(self, sessionId, currentNodeId, tool_information, user_input_memory_tag = None): 
            '''
                将 tool 的 observation 存入到memory中, 分成 chapter
                后缀是 _chapter1-userinput
                user_name = currentNodeId
            '''
            user_name = currentNodeId
            if self.gb_handler.get_extra_tag(  currentNodeId,  'opsgptkg_task',  'ignorememory') == 'True':
                return 0

            chapter = self.nodecount_get_key( sessionId, currentNodeId,key = 'chapter')
            if chapter == None:
                chapter = 1

            tool_map = {
                # "toolKey": {"role_name": "tool_selector", "role_type": "assistant", "customed_keys": ["toolDef"], "role_tags": ""}, 
                # "toolParam": {"role_name": "tool_filler", "role_type": "assistant", "role_tags": ''}, 
                "toolResponse": {"role_name": "function_caller", "role_type": "observation","role_tags": "all"}, 
                # "toolSummary": {"role_name": "function_summary", "role_type": "Summary", "role_tags": ''}, 
            }

            for k, v in tool_map.items():
                try:
                    if user_input_memory_tag == None:
                        role_tags_ = v["role_tags"]
                    else:
                        role_tags_ = user_input_memory_tag



                    message = Message(
                        chat_index=sessionId,
                        #message_index= f"{nodeid}-{uuid.uuid4()}",
                        # message_index= f"{nodeid}-{k}", #hash_id(currentNodeId, sessionId, f'-{k}'),
                        message_index= hash_id(currentNodeId, sessionId, f'_chapter{chapter}-{k}'),
                        user_name = hash_id(user_name),
                        role_name = v["role_name"], # agent 名字，
                        role_type = v["role_type"], # agent 类型，默认assistant，可选observation
                        ## llm output
                        role_content    = tool_information[k], # 输入
                        role_tags       = role_tags_,
                        customed_kargs = {
                            **{kk: vv for kk, vv in tool_information.items() 
                                if kk in v.get("customed_keys", [])}
                        } # 存储docs、tool等信息
                    )

                    self.memory_manager.append(message)
                except:
                    pass
    

            #logging.info(f'sessionId {sessionId} start_nodeid {start_nodeid} 的 memory 是 {memory}')

    def get_output(self,sessionId, start_datetime, end_datetime):
        memory_manager_res= self.memory_manager.get_memory_pool_by_all({ 
                                                            "chat_index": sessionId, 
                                                            'role_tags': ['all', '人类'],
                                                            "start_datetime":[start_datetime, end_datetime],
                                                          })
        get_messages_res = memory_manager_res.get_messages()
        if get_messages_res == []:
            logging.info('本阶段没有能给用户看的信息')
            return None
        outputinfo = []
        for i in range(len(get_messages_res)):
            outputinfo.append( get_messages_res[i].role_content   )
        logging.info(f'outputinfo is {outputinfo}')

        # outputinfo_str = json.dumps(outputinfo, ensure_ascii=False)
        outputinfo_str = to_markdown(outputinfo)
        return outputinfo_str

def to_markdown(lst):
    '''
        将list【str， str】 转换为markdown模式
         ["主持人:  好的，接下来4号位的player_2发言", "李四(人类玩家) :  我的也是一种小动物，毛茸茸的"]
         '**主持人:**  <br>好的，接下来4号位的player_2发言<br><br>**李四(人类玩家):**  <br>我的也是一种小动物，毛茸茸的'

    '''
    markdown_lst = []
    for line in lst:
        # 分割字符串，以':'为分隔符，但确保只分割第一次出现的冒号
        if ':' not in line:
            markdown_lst.append(line)
            continue
        name, content = line.split(':', 1)
        # 去除前后空白并添加Markdown格式
        name = name.strip()
        content = content.strip()
        markdown_line = f"**{name}:**  <br>{content}"
        markdown_lst.append(markdown_line)
    res = '<br><br>'.join(markdown_lst)
    return res


if __name__ == "__main__":

    pass