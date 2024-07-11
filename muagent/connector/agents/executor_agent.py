from typing import List, Union
import copy
import uuid
from loguru import logger

from langchain.schema import BaseRetriever

from muagent.connector.schema import (
    Memory, Task, Env, Role, Message, ActionStatus, PromptField, LogVerboseEnum
)
from muagent.connector.memory_manager import BaseMemoryManager
from muagent.llm_models import LLMConfig, EmbedConfig
from muagent.base_configs.prompts import PLAN_EXECUTOR_PROMPT
from muagent.base_configs.env_config import JUPYTER_WORK_PATH, KB_ROOT_PATH
from muagent.db_handler.vector_db_handler.tbase_handler import TbaseHandler

from .base_agent import BaseAgent

executor_output_template = '''#### RESPONSE OUTPUT FORMAT
**Thoughts:** Considering the session records and task records, decide whether the current step requires the use of a tool or code_executing. 
Solve the problem  only displaying the thought process necessary for the current step of solving the problem. 

**Action Status:** Set to 'stopped' or 'code_executing'. If it's 'stopped', the action is to provide the final answer to the original question. If it's 'code_executing', the next step is to write the code.

**Action:** Code according to your thoughts. Use this format for code:

```python
# Write your code here
```'''

class ExecutorAgent(BaseAgent):
    def __init__(
            self, 
            role: Role,
            prompt_config: List[PromptField] = None,
            prompt_manager_type: str= "PromptManager",
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
            tbase_handler: TbaseHandler = None
            ):
        role.task_context_level = 1
        role.output_template = executor_output_template

        super().__init__(role, prompt_config, prompt_manager_type, task, memory, chat_turn,
                         focus_agents, focus_message_keys, llm_config, embed_config, sandbox_server,
                         jupyter_work_path, kb_root_path, doc_retrieval, code_retrieval, search_retrieval, 
                         log_verbose, tbase_handler
                         )
        self.do_all_task = True # run all tasks

    def astep(self, query: Message, history: Memory = None, background: Memory = None, memory_manager: BaseMemoryManager=None, chat_index: str = "") -> Message:
        '''agent reponse from multi-message'''
        chat_index = query.chat_index or chat_index or str(uuid.uuid4())
        # insert query into memory
        task_executor_memory = Memory(messages=[])
        # insert query
        output_message = Message(
                chat_index=chat_index,
                user_name=query.user_name,
                role_name=self.role.role_name,
                role_type="assistant", #self.role.role_type,
                role_content="",
                step_content="",
                input_query=query.input_query,
                tools=query.tools,
                # parsed_output_list=[query.parsed_output],
                customed_kargs=query.customed_kargs
            )
        
        memory_manager = self.init_memory_manager(memory_manager)
        memory_manager.append(query)
        memory_pool = memory_manager.get_memory_pool(chat_index)
        # acquire the input_query
        input_query = query.role_content or query.input_query
        prompt = PLAN_EXECUTOR_PROMPT.format(**{"content": input_query.replace("*", "")})
        content = self.llm.predict(prompt)
        # logger.debug(f"prompt={prompt}")
        # logger.debug(f"content={content}")
        plan_message = Message(
                chat_index=chat_index,
                user_name=query.user_name,
                role_name="plan_extracter",
                role_type="assistant", #self.role.role_type,
                role_content=content,
                customed_kargs=query.customed_kargs
            )

        plan_message = self.message_utils.parser(plan_message)
        # process input_quert to plans and plan_step
        plan_step = int(plan_message.parsed_output.get("PLAN_STEP", 0))
        plans = plan_message.parsed_output.get("PLAN", [input_query])
        # logger.debug(f"plans={plans}, plan_step={plan_step}")

        def _execute_line(task_content, output_message, task_executor_memory, plan_step, chat_index):
            '''task execute line'''
            query_c = copy.deepcopy(query)
            query_c.parsed_output = {"CURRENT_STEP": task_content}
            query_c = self.start_action_step(query_c)
            task_executor_memory.append(query_c)
            for output_message, task_executor_memory in self._arun_step(
                        output_message, query_c, self.memory, history, background, memory_pool, task_executor_memory, chat_index):
                pass
            output_message.parsed_output.update({"PLAN_STEP": plan_step})

        if self.do_all_task:
            # run all tasks step by step
            for idx, task_content in enumerate(plans[plan_step:]):
                # create your llm prompt
                _execute_line(task_content, output_message, task_executor_memory, plan_step+idx, chat_index)
                yield output_message
        else:
            task_content = plans[plan_step]
            _execute_line(task_content, output_message, task_executor_memory, plan_step, chat_index)

        # update self_memory
        self.append_history(query)
        self.append_history(output_message)
        # output_message.input_query = output_message.role_content

        # end_action_step
        output_message = self.end_action_step(output_message)
        # update memory pool
        memory_manager.append(output_message)
        yield output_message

    def _arun_step(self, output_message: Message, query: Message, self_memory: Memory, 
            history: Memory, background: Memory, memory_pool: BaseMemoryManager, 
            task_memory: Memory, chat_index: str) -> Union[Message, Memory]:
        '''execute the llm predict by created prompt'''
        prompt = self.prompt_manager.generate_full_prompt(
            previous_agent_message=query, agent_long_term_memory=self_memory, ui_history=history, chain_summary_messages=background, memory_pool=memory_pool,
            task_memory=task_memory)
        content = self.llm.predict(prompt)

        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"{self.role.role_name} prompt: {prompt}")

        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"{self.role.role_name} content: {content}")

        output_message.role_content = content
        output_message.step_content += "\n"+output_message.role_content
        output_message = self.message_utils.parser(output_message)
        # according the output to choose one action for code_content or tool_content
        output_message, observation_message = self.message_utils.step_router(output_message, chat_index=chat_index)
        # update parserd_output_list
        output_message.parsed_output_list.append(output_message.parsed_output)

        react_message = copy.deepcopy(output_message)
        task_memory.append(react_message)
        if observation_message:
            task_memory.append(observation_message)
            output_message.parsed_output_list.append(observation_message.parsed_output)
            # logger.debug(f"{observation_message.role_name} content: {observation_message.role_content}")
        yield output_message, task_memory

    def pre_print(self, query: Message, history: Memory = None, background: Memory = None, memory_manager: BaseMemoryManager = None, chat_index: str = ""):
        task_memory = Memory(messages=[])
        memory_pool = memory_manager.get_memory_pool(chat_index)
        prompt = self.prompt_manager.pre_print(
                previous_agent_message=query, agent_long_term_memory=self.memory, ui_history=history, chain_summary_messages=background, react_memory=None, 
                memory_pool=memory_pool, task_memory=task_memory)
        title = f"<<<<{self.role.role_name}'s prompt>>>>"
        print("#"*len(title) + f"\n{title}\n"+ "#"*len(title)+ f"\n\n{prompt}\n\n")
