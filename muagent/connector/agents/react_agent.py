from typing import List, Union
import traceback
import copy
import uuid
from loguru import logger

from langchain.schema import BaseRetriever

from muagent.connector.schema import (
    Memory, Task, Env, Role, Message, ActionStatus, PromptField, LogVerboseEnum
)
from muagent.connector.memory_manager import BaseMemoryManager
from muagent.llm_models import LLMConfig, EmbedConfig
from muagent.db_handler.vector_db_handler.tbase_handler import TbaseHandler

from .base_agent import BaseAgent
from muagent.base_configs.env_config import JUPYTER_WORK_PATH, KB_ROOT_PATH

react_output_template = '''#### RESPONSE OUTPUT FORMAT
**Thoughts:** According the previous observations, plan the approach for using the tool effectively.

**Action Status:** Set to either 'stopped' or 'tool_using'. If 'stopped', provide the final response to the original question. If 'tool_using', proceed with using the specified tool.

**Action:** Use the tools by formatting the tool action in JSON. The format should be:

```json
{
  "tool_name": "$TOOL_NAME",
  "tool_params": "$INPUT"
}
```

**Observation:** Evaluate the outcome of the tool's usage.

... (Repeat this Thoughts/Action Status/Action/Observation cycle as needed)

**Thoughts:** Determine the final response based on the results.

**Action Status:** Set to 'stopped'

**Action:** Conclude with the final response to the original question in this format:

```json
{
  "tool_params": "Final response to be provided to the user",
  "tool_name": "notool",
}
```
'''

class ReactAgent(BaseAgent):
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
            tbase_handler: TbaseHandler = None
            ):
        
        role.react_context_level = 1
        role.output_template = react_output_template
        # role.session_context_level = 0
        super().__init__(role, prompt_config, prompt_manager_type, task, memory, chat_turn, 
                         focus_agents, focus_message_keys, llm_config, embed_config, sandbox_server,
                         jupyter_work_path, kb_root_path, doc_retrieval, code_retrieval, search_retrieval,
                         log_verbose, tbase_handler
                         )

    def step(self, query: Message, history: Memory = None, background: Memory = None, memory_manager: BaseMemoryManager = None, chat_index: str = "") -> Message:
        '''agent reponse from multi-message'''
        chat_index = query.chat_index or chat_index or str(uuid.uuid4())
        for message in self.astep(query, history, background, memory_manager, chat_index=chat_index):
            pass
        return message

    def astep(self, query: Message, history: Memory = None, background: Memory = None, memory_manager: BaseMemoryManager = None, chat_index: str = "") -> Message:
        '''agent reponse from multi-message'''
        chat_index = query.chat_index or chat_index or str(uuid.uuid4())
        step_nums = copy.deepcopy(self.chat_turn)
        react_memory = Memory(messages=[])
        # insert query
        output_message = Message(
                chat_index=chat_index,
                user_name=query.user_name,
                role_name=self.role.role_name,
                role_type="assistant", #self.role.role_type,
                role_content=query.input_query,
                step_content="",
                input_query=query.input_query,
                tools=query.tools,
                # parsed_output_list=[query.parsed_output],
                customed_kargs=query.customed_kargs
                )
        query_c = copy.deepcopy(query)
        query_c = self.start_action_step(query_c)

        memory_manager = self.init_memory_manager(memory_manager)
        memory_manager.append(query)
        memory_pool = memory_manager.get_memory_pool(chat_index)
        
        idx = 0
        # start to react
        while step_nums > 0:
            output_message.role_content = output_message.step_content
            prompt = self.prompt_manager.generate_full_prompt(
                previous_agent_message=query_c, agent_long_term_memory=self.memory, ui_history=history, chain_summary_messages=background, react_memory=react_memory, 
                memory_pool=memory_pool)
            try:
                content = self.llm.predict(prompt)
            except Exception as e:
                logger.error(f"error prompt: {prompt}")
                raise Exception(traceback.format_exc())
            
            output_message.role_content = "\n"+content
            output_message.step_content += "\n"+output_message.role_content
            yield output_message

            if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
                logger.debug(f"{self.role.role_name}, {idx} iteration prompt: {prompt}")

            if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
                logger.info(f"{self.role.role_name}, {idx} iteration step_run: {output_message.role_content}")

            output_message = self.message_utils.parser(output_message)
            # when get finished signal can stop early
            if output_message.action_status == ActionStatus.FINISHED or output_message.action_status == ActionStatus.STOPPED: 
                output_message.parsed_output_list.append(output_message.parsed_output)
                break
            # according the output to choose one action for code_content or tool_content
            output_message, observation_message = self.message_utils.step_router(output_message, chat_index=chat_index)
            output_message.parsed_output_list.append(output_message.parsed_output)
            
            react_message = copy.deepcopy(output_message)
            react_memory.append(react_message)
            if observation_message:
                react_memory.append(observation_message)
                output_message.parsed_output_list.append(observation_message.parsed_output)
                # logger.debug(f"{observation_message.role_name} content: {observation_message.role_content}")
            idx += 1
            step_nums -= 1
            yield output_message
        # react' self_memory saved at last
        self.append_history(output_message)
        output_message.input_query = query.input_query
        # end_action_step, BUG:it may cause slack some information
        output_message = self.end_action_step(output_message)
        # update memory pool
        memory_manager.append(output_message)
        yield output_message
        
    def pre_print(self, query: Message, history: Memory = None, background: Memory = None, memory_manager: BaseMemoryManager=None, chat_index: str=""):
        react_memory = Memory(messages=[])
        memory_pool = memory_manager.get_memory_pool(chat_index)
        prompt = self.prompt_manager.pre_print(
                previous_agent_message=query, agent_long_term_memory=self.memory, ui_history=history, chain_summary_messages=background, react_memory=react_memory, 
                memory_pool=memory_pool)
        title = f"<<<<{self.role.role_name}'s prompt>>>>"
        print("#"*len(title) + f"\n{title}\n"+ "#"*len(title)+ f"\n\n{prompt}\n\n")

    
