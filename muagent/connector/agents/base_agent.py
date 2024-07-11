from typing import List, Union
import importlib
import re, os
import copy
import uuid
from loguru import logger

from langchain.schema import BaseRetriever

from muagent.connector.schema import (
    Memory, Task, Role, Message, PromptField, LogVerboseEnum
)
from muagent.connector.message_process import MessageUtils
from muagent.llm_models import getExtraModel, LLMConfig, getChatModelFromConfig, EmbedConfig
from muagent.connector.prompt_manager.prompt_manager import PromptManager
from muagent.connector.memory_manager import BaseMemoryManager, LocalMemoryManager, TbaseMemoryManager
from muagent.base_configs.env_config import JUPYTER_WORK_PATH, KB_ROOT_PATH
from muagent.db_handler.vector_db_handler.tbase_handler import TbaseHandler

class BaseAgent:

    def __init__(
            self, 
            role: Role,
            prompt_config: List[PromptField] = None,
            prompt_manager_type: str = "PromptManager",
            task: Task = None,
            memory: Memory = None,
            chat_turn: int = 1,
            focus_agents: List[str] = [],
            focus_message_keys: List[str] = [],
            #
            llm_config: LLMConfig = None,
            embed_config: EmbedConfig = None,
            sandbox_server: dict = {},
            jupyter_work_path: str = JUPYTER_WORK_PATH,
            kb_root_path: str = KB_ROOT_PATH,
            doc_retrieval: Union[BaseRetriever] = None,
            code_retrieval = None,
            search_retrieval = None,
            log_verbose: str = "0",
            tbase_handler: TbaseHandler = None,
            ):
        
        self.task = task
        self.role = role
        self.sandbox_server = sandbox_server
        self.jupyter_work_path = jupyter_work_path
        self.kb_root_path = kb_root_path
        self.message_utils = MessageUtils(role, sandbox_server, jupyter_work_path, embed_config, llm_config, kb_root_path, doc_retrieval, code_retrieval, search_retrieval, log_verbose)
        self.memory = self.init_history(memory)
        self.llm_config: LLMConfig = llm_config
        self.embed_config: EmbedConfig = embed_config
        self.llm = self.create_llm_engine(llm_config=self.llm_config)
        self.chat_turn = chat_turn
        # 
        self.focus_agents = focus_agents
        self.focus_message_keys = focus_message_keys
        # 
        prompt_manager_module = importlib.import_module("muagent.connector.prompt_manager")
        prompt_manager = getattr(prompt_manager_module, prompt_manager_type)
        self.prompt_manager: PromptManager = prompt_manager(role=role, role_prompt=role.role_prompt, prompt_config=prompt_config)
        self.log_verbose = max(os.environ.get("log_verbose", "0"), log_verbose)
        self.tbase_handler = tbase_handler

    def step(self, query: Message, history: Memory = None, background: Memory = None, memory_manager: BaseMemoryManager=None, chat_index: str = "") -> Message:
        '''agent reponse from multi-message'''
        chat_index = query.chat_index or chat_index or str(uuid.uuid4())
        message = None
        for message in self.astep(query, history, background, memory_manager, chat_index=chat_index):
            pass
        return message
    
    def astep(self, query: Message, history: Memory = None, background: Memory = None, memory_manager: BaseMemoryManager=None, chat_index: str = "") -> Message:
        '''agent reponse from multi-message'''
        # insert query into memory
        chat_index = query.chat_index or chat_index or str(uuid.uuid4())
        query_c = copy.deepcopy(query)
        query_c = self.start_action_step(query_c)

        memory_manager = self.init_memory_manager(memory_manager)
        memory_manager.append(query)
        memory_pool = memory_manager.get_memory_pool(chat_index)

        prompt = self.prompt_manager.generate_full_prompt(
            previous_agent_message=query_c, agent_long_term_memory=self.memory, ui_history=history, chain_summary_messages=background, memory_pool=memory_pool)
        content = self.llm.predict(prompt)

        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"{self.role.role_name} prompt: {prompt}")

        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"{self.role.role_name} content: {content}")

        output_message = Message(
            chat_index=chat_index,
            user_name=query.user_name,
            role_name=self.role.role_name,
            role_type="assistant", #self.role.role_type,
            role_content=content,
            step_content=content,
            input_query=query_c.input_query,
            tools=query_c.tools,
            # parsed_output_list=[query.parsed_output],
            customed_kargs=query_c.customed_kargs
            )
        
        # common parse llm' content to message
        output_message = self.message_utils.parser(output_message)

        # action step
        output_message, observation_message = self.message_utils.step_router(output_message, history, background, memory_manager=memory_manager, chat_index=chat_index)
        output_message.parsed_output_list.append(output_message.parsed_output)
        if observation_message:
            output_message.parsed_output_list.append(observation_message.parsed_output)

        # update self_memory
        self.append_history(query_c)
        self.append_history(output_message)

        # output_message.input_query = output_message.role_content
        # end
        output_message = self.message_utils.inherit_extrainfo(query, output_message)
        output_message = self.end_action_step(output_message)

        # update memory pool
        memory_manager.append(output_message)
        yield output_message
    
    def pre_print(self, query: Message, history: Memory = None, background: Memory = None, memory_manager: BaseMemoryManager=None, chat_index: str = ""):
        chat_index = query.chat_index or chat_index or str(uuid.uuid4())

        memory_manager = self.init_memory_manager(memory_manager)
        memory_manager.append(query)
        memory_pool = memory_manager.get_memory_pool(chat_index)

        prompt = self.prompt_manager.pre_print(
            previous_agent_message=query, agent_long_term_memory=self.memory, ui_history=history, chain_summary_messages=background, memory_pool=memory_pool)
        title = f"<<<<{self.role.role_name}'s prompt>>>>"
        print("#"*len(title) + f"\n{title}\n"+ "#"*len(title)+ f"\n\n{prompt}\n\n")

    def init_history(self, memory: Memory = None) -> Memory:
        return Memory(messages=[])
    
    def update_history(self, message: Message):
        self.memory.append(message)

    def append_history(self, message: Message):
        self.memory.append(message)
        
    def clear_history(self, ):
        self.memory.clear()
        self.memory = self.init_history()
    
    def init_memory_manager(self, memory_manager):
        if memory_manager is None:
            if self.tbase_handler:
                memory_manager = TbaseMemoryManager(
                unique_name=self.role.role_name, use_vector=True, 
                tbase_handler=self.tbase_handler, 
                embed_config=self.embed_config, llm_config=self.llm_config,
                )
            else:
                memory_manager = LocalMemoryManager(
                    unique_name=self.role.role_name, 
                    do_init=True, 
                    kb_root_path = self.kb_root_path, 
                    embed_config=self.embed_config, 
                    llm_config=self.llm_config
                )
        return memory_manager

    def create_llm_engine(self, llm_config: LLMConfig = None, temperature=0.2, stop=None):
        return getChatModelFromConfig(llm_config=llm_config)
    
    def registry_actions(self, actions):
        '''registry llm's actions'''
        self.action_list = actions

    def start_action_step(self, message: Message) -> Message:
        '''do action before agent predict '''
        # action_json = self.start_action()
        # message["customed_kargs"]["xx"] = action_json
        return message

    def end_action_step(self, message: Message) -> Message:
        '''do action after agent predict '''
        # action_json = self.end_action()
        # message["customed_kargs"]["xx"] = action_json
        return message
    
    def token_usage(self, ):
        '''calculate the usage of token'''
        pass
    
    def get_memory(self, content_key="role_content"):
        return self.memory.to_tuple_messages(content_key="step_content")
    
    def get_memory_str(self, content_key="role_content"):
        return "\n".join([": ".join(i) for i in self.memory.to_tuple_messages(content_key="step_content")])
