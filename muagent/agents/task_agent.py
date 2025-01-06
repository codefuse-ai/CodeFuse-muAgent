from abc import ABCMeta
from pydantic import BaseModel
import os
from typing import (
    List, 
    Union, 
    Generator, 
    Optional,
    Tuple,
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
from ..memory_manager import BaseMemoryManager
from ..base_configs.prompts import PLAN_EXECUTOR_PROMPT

from muagent.connector.schema import LogVerboseEnum




executor_output_template = '''#### RESPONSE OUTPUT FORMAT
**Thoughts:** Considering the session records and task records, decide whether the current step requires the use of a tool or code_executing. 
Solve the problem  only displaying the thought process necessary for the current step of solving the problem. 

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
```'''


class TaskAgent(BaseAgent):
    """TaskAgent class that extends the BaseAgent class for delegaing query into multi task.
    
    TaskAgent Examples:
    .. code-block:: python 
        
        from muagent.schemas import Message
        from muagent.agents import BaseAgent
        from muagent import get_project_config_from_env
        
        tools = list(TOOL_SETS)
        tools = ["KSigmaDetector", "MetricsQuery"]
        role_prompt = "you are a helpful assistant!"

        AGENT_CONFIGS = {
            "tasker": {
                "system_prompt": role_prompt,
                "agent_type": "TaskAgent",
                "agent_name": "tasker",
                "tools": tools,
                "llm_config_name": "qwen_chat"
            }
        }
        os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)

        # 
        project_config = get_project_config_from_env()
        agent = BaseAgent.init_from_project_config(
            "tasker", project_config
        )

        query_content = "先帮我获取下127.0.0.1这个服务器在10点的数，然后在帮我判断下数据是否存在异常"
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

    agent_type: str = "TaskAgent"
    """The type of the agent, which is defined as 'TaskAgent'."""

    agent_id: str
    """Unique identifier for the agent."""

    def __init__(
            self, 
            agent_name: str = "codefuse_tasker",
            system_prompt: str = "you are a helpful assistant!\n",
            input_template: Union[str, BaseModel] = "",
            output_template: Union[str, BaseModel] = executor_output_template,
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
            do_all_task: bool = True,
            log_verbose: str = "0",
        ):
        super().__init__(
            agent_name=agent_name,
            system_prompt=system_prompt,
            input_template=input_template,
            output_template=output_template or executor_output_template,
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
        self.do_all_task = do_all_task
    
    def step_stream(
            self, 
            query: Message, 
            memory_manager: Optional[BaseMemoryManager]=None, 
            session_index: str = "default"
        ) -> Generator[Message, None, None]:
        '''Stream the agent's responses based on an input multi-message query.'''
        
        session_index = query.session_index or session_index

        # insert query into memory
        self.append_history(query)
        self.update_memory_manager(query, memory_manager)

        # transform query into output_message.input_text
        output_message = self.inherit_extrainfo(query)
        output_message = self.start_action_step(output_message)

        # get memory from self or memory_manager
        memory = self.get_memory(session_index)

        # generate prompt by prompt manager
        input_text = query.content or output_message.input_text
        prompt = PLAN_EXECUTOR_PROMPT.format(
            **{"content": input_text.replace("*", "")}
        )
        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"{self.agent_name} prompt: {prompt}")

        model = self._get_model()
        content = model.predict(prompt)

        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"{self.agent_name} content: {content}")

        plan_message = Message(
            session_index=session_index,
            role_name="plan_extracter",
            role_type="assistant",
            content=content,
            global_kwargs=query.global_kwargs
        )
        plan_message = self.prompt_manager.parser(plan_message)
        # process input_quert to plans and plan_step
        plan_step = int(plan_message.parsed_content.get("PLAN_STEP", 0))
        plans = plan_message.parsed_content.get("PLAN", [input_text])

        if self.do_all_task:
            # run all tasks step by step
            for idx, task_content in enumerate(plans[plan_step:]):
                for output_message in self._execute_line(
                    task_content, output_message, plan_step+idx, session_index
                ):
                    yield output_message
        else:
            task_content = plans[plan_step]
            for output_message in self._execute_line(
                    task_content, output_message, plan_step+idx, session_index
                ):
                pass

        # end
        output_message = self.end_action_step(output_message)

        # update self_memory and memory pool
        self.append_history(output_message)
        self.update_memory_manager(output_message, memory_manager)
        yield output_message

    def _execute_line(
            self, 
            task_content: str, 
            output_message: Message,
            plan_step, 
            session_index
        ) -> Generator[Tuple[Message, Memory], None, None]:
        '''task execute line'''
        query = copy.deepcopy(output_message)
        query.parsed_content = {"CURRENT_STEP": task_content}
        query = self.start_action_step(query)

        # get memory from self or memory_manager
        memory = self.get_memory(session_index)

        for output_message in self._run_stream(
            query, output_message, memory, session_index
        ):
            yield output_message
        output_message.update_spec_parsed_content(
            {**output_message.spec_parsed_content, **{"PLAN_STEP": plan_step}}
        )
        yield output_message

    def _run_stream(
            self,
            query: Message,
            output_message: Message,
            memory: Memory, 
            session_index: str
        ) -> Generator[Tuple[Message, Memory], None, None]:
        '''execute the llm predict by created prompt'''
        prompt = self.prompt_manager.generate_prompt(
            query=query, 
            memory=memory,
            tools=self.tools,
        )

        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"{self.agent_name} prompt: {prompt}")

        model = self._get_model()
        content = model.predict(prompt)

        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"{self.agent_name} content: {content}")

        output_message.update_content(content)
        output_message = self.prompt_manager.parser(output_message)
        # according the output to choose one action for code_content or tool_content
        output_message, observation_message = self.message_util.step_router(
            output_message, session_index=session_index,
            tools=self.tools
        )
        react_message = copy.deepcopy(output_message)
        self.append_history(react_message)
        # task_memory.append(react_message)
        if observation_message:
            # task_memory.append(observation_message)
            self.append_history(observation_message)
            output_message.update_parsed_content(observation_message.parsed_content)
            output_message.update_spec_parsed_content(observation_message.parsed_content)
        yield output_message
        
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