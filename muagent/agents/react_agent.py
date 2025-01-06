from abc import ABCMeta
from pydantic import BaseModel
from typing import (
    List, 
    Union, 
    Generator,
    Optional,
)
import copy
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
from ..schemas.common import ActionStatus
from ..memory_manager import BaseMemoryManager

from muagent.connector.schema import LogVerboseEnum



react_output_template = '''#### RESPONSE OUTPUT FORMAT
**Thoughts:** According the previous observations, plan the approach for using the tool effectively.

**Action Status:** stoped, tool_using or code_executing
Use 'stopped' when the task has been completed, and no further use of tools or execution of code is necessary. 
Use 'tool_using' when the current step in the process involves utilizing a tool to proceed. 
Use 'code_executing' when the current step requires writing and executing code.

**Action:** 

If Action Status is 'tool_using', format the tool action in JSON from Question and Observation, enclosed in a code block, like this:
```json
{
  "tool_name": "$TOOL_NAME",
  "tool_params": "$INPUT"
}
```

If Action Status is 'code_executing', write the necessary code to solve the issue, enclosed in a code block, like this:
```python
Write your running code here
```

If Action Status is 'stopped', provide the final response or instructions in written form, enclosed in a code block, like this:
```text
The final response or instructions to the user question.
```

**Observation:** Check the results and effects of the executed action.

... (Repeat this Thoughts/Action Status/Action/Observation cycle as needed)

**Thoughts:** Conclude the final response to the user question.

**Action Status:** stoped

**Action:** The final answer or guidance to the user question.
'''


class ReactAgent(BaseAgent):
    """ReactAgent class that extends the BaseAgent class for completing task by reacting.
    
    ReactAgent Examples:
    .. code-block:: python 
        from muagent.tools import TOOL_SETS
        from muagent.schemas import Message
        from muagent.agents import BaseAgent
        from muagent import get_project_config_from_env

        # log-level，print prompt和llm predict
        os.environ["log_verbose"] = "0"

        tools = list(TOOL_SETS)
        tools = ["KSigmaDetector", "MetricsQuery"]
        role_prompt = "you are a helpful assistant!"

        AGENT_CONFIGS = {
            "reacter": {
                "system_prompt": role_prompt,
                "agent_type": "ReactAgent",
                "agent_name": "reacter",
                "tools": tools,
                "llm_config_name": "qwen_chat"
            }
        }
        os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)

        # 
        project_config = get_project_config_from_env()
        agent = BaseAgent.init_from_project_config(
            "reacter", project_config
        )

        query_content = "帮我确认下127.0.0.1这个服务器的在10点是否存在异常，请帮我判断一下"
        query = Message(
            role_name="human", 
            role_type="user", 
            content=query_content,
        )
        # agent.pre_print(query)
        output_message = agent.step(query)
        print("### intput ### ", output_message.input_text)
        print("### content ### ", output_message.content)
        print("### step content ### ", output_message.step_content)
    """

    agent_type: str = "ReactAgent"
    """The type of the agent, which is defined as 'ReactAgent'."""

    agent_id: str
    """Unique identifier for the agent."""

    def __init__(
            self, 
            agent_name: str = "codefuse_reacter",
            system_prompt: str = "you are a helpful assistant!\n",
            input_template: Union[str, BaseModel] = "",
            output_template: Union[str, BaseModel] = react_output_template,
            prompt: Optional[str] = None,
            stop: str = '**Observation:**',
            agents: List[str] = [],
            tools: List[str] = [],
            agent_desc: str = "",
            *,
            agent_config: Optional[AgentConfig] = None,
            model_config: Optional[ModelConfig] = None,
            prompt_config: Optional[PromptConfig] = PromptConfig(),
            project_config: Optional[ProjectConfig] = None,
            # 
            chat_turn: int = 3,
            log_verbose: str = "0",
        ):
        super().__init__(
            agent_name=agent_name,
            system_prompt=system_prompt,
            input_template=input_template,
            output_template=output_template or react_output_template,
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
        # 
        self.stop = stop
        self.chat_turn = chat_turn
    
    def step_stream(
            self, 
            query: Message, 
            memory_manager: Optional[BaseMemoryManager]=None, 
            session_index: str = "default"
        ) -> Generator[Message, None, None]:
        '''Stream the agent's responses based on an input multi-message query.'''
        
        session_index = query.session_index or session_index
        step_nums = copy.deepcopy(self.chat_turn)
        react_memory = Memory(messages=[])

        # insert query into memory
        self.append_history(query)
        self.update_memory_manager(query, memory_manager)

        # transform query into output_message.input_text
        output_message = self.inherit_extrainfo(query)
        output_message = self.start_action_step(output_message)

        # get memory from self or memory_manager
        memory = self.get_memory(session_index)

        idx = 0
        while step_nums > 0:
            output_message.content = output_message.step_content
            prompt = self.prompt_manager.generate_prompt(
                query=output_message, 
                memory=memory, 
                react_memory=react_memory, 
                tools=self.tools
            )
            
            try:
                model = self._get_model()
                content = model.predict(prompt, self.stop)
            except Exception as e:
                logger.error(f"error : {e}, prompt: {prompt}")
                raise RuntimeError(f"error : {e}, prompt: {prompt}")

            output_message.content = content
            output_message.step_content += f"\n{content}"
            yield output_message

            if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
                logger.debug(f"{self.agent_name}, {idx} iteration prompt: {prompt}")

            if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
                logger.info(f"{self.agent_name}, {idx} iteration step_run: {content}")

            output_message = self.prompt_manager.parser(output_message)
            # when get finished signal can stop early
            if (output_message.action_status == ActionStatus.FINISHED or 
                output_message.action_status == ActionStatus.STOPPED): 
                output_message.spec_parsed_contents.append(output_message.spec_parsed_content)
                break
            # according the output to choose one action for code_content or tool_content
            output_message, observation_message = self.message_util.step_router(
                output_message, 
                session_index=session_index,
                tools=self.tools,
            )
            
            # only record content
            react_message = copy.deepcopy(output_message)
            react_memory.append(react_message)
            if observation_message:
                react_memory.append(observation_message)
                output_message.update_parsed_content(observation_message.parsed_content)
                output_message.update_spec_parsed_content(observation_message.parsed_content)
            idx += 1
            step_nums -= 1
            yield output_message

        # end
        output_message = self.end_action_step(output_message)

        # update self_memory and memory pool
        self.append_history(output_message)
        self.update_memory_manager(output_message, memory_manager)
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
        react_memory = Memory(messages=[])
        # 
        output_message = self.inherit_extrainfo(query)
        output_message = self.start_action_step(output_message)

        # insert query into memory
        self.append_history(query)
        self.update_memory_manager(query, memory_manager)
        
        # get memory from self or memory_manager
        memory = self.get_memory(session_index)

        prompt = self.prompt_manager.pre_print(
            query=query, 
            memory=memory,
            tools=tools or self.tools,
            react_memory=react_memory
        )

        title = f"<<<<{self.agent_name}'s prompt>>>>"
        print("#"*len(title) + f"\n{title}\n"+ "#"*len(title)+ f"\n\n{prompt}\n\n")
    
    def start_action_step(self, message: Message) -> Message:
        '''Perform any required actions before predicting the response of the agent.'''
        # action_json = self.start_action()
        # message["customed_kargs"]["xx"] = action_json
        return message

    def end_action_step(self, message: Message) -> Message:
        '''Perform any required actions after the agent has predicted the response.'''
        # action_json = self.end_action()
        # message["customed_kargs"]["xx"] = action_json
        return message