from abc import ABCMeta
from pydantic import BaseModel
import os
from typing import (
    List, 
    Union, 
    Generator,
    Optional,
)

from loguru import logger

from ..schemas import (
    Message,
    Memory,
    PromptConfig,
    AgentConfig,
    ProjectConfig
)
from .base_agent import BaseAgent
from ..schemas.models import ModelConfig
from ..memory_manager import BaseMemoryManager

from muagent.connector.schema import LogVerboseEnum



funtioncall_output_template = '''#### RESPONSE OUTPUT FORMAT
**Thoughts:** According the previous context, plan the approach for using the tool effectively.

**Action Status:** stoped, tool_using or code_executing
Use 'stopped' when the task has been completed, and no further use of tools or execution of code is necessary. 
Use 'tool_using' when the current step in the process involves utilizing a tool to proceed.

**Action:** 

If Action Status is 'tool_using', format the tool action in JSON from Question and Observation, enclosed in a code block, like this:
```json
{
  "tool_name": "$TOOL_NAME",
  "tool_params": $args
}
```

If Action Status is 'stopped', provide the final response or instructions in written form, enclosed in a code block, like this:
```text
The final response or instructions to the user question.
```
'''


class FunctioncallAgent(BaseAgent):
    """FunctioncallAgent class that extends the BaseAgent class for 
    function calling.
    
    FunctioncallAgent Examples:
    .. code-block:: python 
        from muagent.schemas import Message, Memory
        from muagent.agents import FunctioncallAgent
        from muagent import get_project_config_from_env


        # log-level，print prompt和llm predict
        os.environ["log_verbose"] = "0"

        AGENT_CONFIGS = {
            "codefuse_function_caller": {
                "config_name": "codefuse_function_caller",
                "agent_type": "FunctioncallAgent",
                "agent_name": "codefuse_function_caller",
                "llm_config_name": "qwener"
            }
        }
        os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)

        project_config = get_project_config_from_env()
        tools = ["KSigmaDetector", "MetricsQuery"]
        agent = FunctioncallAgent(
            agent_name="codefuse_function_caller",
            project_config=project_config,
            tools=tools
        )

        query_content = "帮我查询下127.0.0.1这个服务器的在10点的数据"
        query = Message(
            role_name="human", 
            role_type="user", 
            content=query_content,
        )
        # agent.pre_print(query)
        output_message = agent.step(query)
        print("### intput ###\n", output_message.input_text)
        print("### content ###\n", output_message.content)
        print("### step content ###\n", output_message.step_content)
    """

    agent_type: str = "FunctioncallAgent"
    """The type of the agent, which is defined as 'FunctioncallAgent'."""

    agent_id: str
    """Unique identifier for the agent."""

    def __init__(
            self,
            agent_name: str = "codefuse_function_caller",
            system_prompt: str = "you are a helpful assistant!\n",
            input_template: Union[str, BaseModel] = "",
            output_template: Union[str, BaseModel] = funtioncall_output_template,
            prompt: Optional[str] = None,
            agents: List[str] = [],
            tools: List[str] = [],
            agent_desc: str = "",
            *,
            agent_config: Optional[AgentConfig] = None,
            model_config: Optional[ModelConfig] = None,
            prompt_config: Optional[PromptConfig] = PromptConfig(), 
            project_config: Optional[ProjectConfig] = None,
            # 
            log_verbose: str = "0",
        ):

        super().__init__(
            agent_name=agent_name,
            system_prompt=system_prompt,
            input_template=input_template,
            output_template=output_template or funtioncall_output_template,
            prompt=prompt,
            agents=agents,
            tools=tools,
            agent_desc=agent_desc,
            agent_config=agent_config,
            model_config=model_config,
            prompt_config=prompt_config,
            project_config=project_config,
            log_verbose=log_verbose
        )

    def step_stream(
            self, 
            query: Message, 
            memory_manager: Optional[BaseMemoryManager]=None,
            session_index: str = "default",
            memory: Optional[Memory] = None,
            **kwargs
        ) -> Generator[Message, None, None]:
        '''agent response from multi-message'''
        
        session_index = query.session_index or session_index

        # insert query into memory
        self.append_history(query)
        self.update_memory_manager(query, memory_manager)

        # transform query into output_message.input_text
        output_message = self.inherit_extrainfo(query)
        output_message = self.start_action_step(output_message)

        # get memory from self or memory_manager
        memory = memory or self.get_memory(session_index)
        
        # generate prompt by prompt manager
        prompt = self.prompt_manager.generate_prompt(
            query=output_message, memory=memory, tools=self.tools
        )
        
        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"{self.agent_name} prompt: {prompt}")

        # predict 
        model = self._get_model()
        content = model.predict(prompt)

        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"{self.agent_name} content: {content}")

        # update infomation
        output_message.update_content(content)
        
        # common parse llm' content to message
        output_message = self.prompt_manager.parser(output_message)

        # todo: action step
        output_message, observation_message = self.message_util.step_router(
            output_message, 
            session_index=session_index,
            tools=self.tools,
            **kwargs
        )
        # end
        output_message = self.end_action_step(output_message)

        # update self_memory and memory pool
        self.append_history(output_message)
        self.update_memory_manager(output_message, memory_manager)
        if observation_message:
            self.append_history(observation_message)
            self.update_memory_manager(observation_message, memory_manager)

        yield output_message
    
    def pre_print(
            self, 
            query: Message, 
            memory_manager: BaseMemoryManager=None, 
            tools: List[str] = [],
            session_index: str = "default"
            
        ) -> None:
        """pre print this agent prompt format"""
        session_index = query.session_index or session_index
        # 
        output_message = self.inherit_extrainfo(query)
        output_message = self.start_action_step(output_message)

        # insert query into memory
        self.append_history(query)
        self.update_memory_manager(query, memory_manager)
        
        # get memory from self or memory_manager
        memory = self.get_memory(session_index)

        prompt = self.prompt_manager.pre_print(query=query, memory=memory, tools=tools or self.tools)

        title = f"<<<<{self.agent_name}'s prompt>>>>"
        print("#"*len(title) + f"\n{title}\n"+ "#"*len(title)+ f"\n\n{prompt}\n\n")

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