from pydantic import BaseModel
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



group_output_template = """#### RESPONSE OUTPUT FORMAT
**Thoughts:** think the reason step by step about why you selecte one role

**Role:** Select one role from agent names. No other information.
"""

group_output_template_zh = """#### 响应输出格式
**思考:** 一步一步思考你选择一个角色的原因

**角色:** 从代理名称中选择一个角色。不要包含其他信息。
"""

class GroupAgent(BaseAgent):
    """GroupAgent class that extends the BaseAgent class for 
    managing the agent team to complete task.

    GroupAgent Examples:
    .. code-block:: python 
        from muagent.tools import TOOL_SETS
        from muagent.schemas import Message
        from muagent.agents import BaseAgent
        from muagent.project_manager import get_project_config_from_env


        tools = list(TOOL_SETS)
        tools = ["KSigmaDetector", "MetricsQuery"]
        role_prompt = "you are a helpful assistant!"

        AGENT_CONFIGS = {
            "grouper": {
                "agent_type": "GroupAgent",
                "agent_name": "grouper",
                "agents": ["codefuse_reacter_1", "codefuse_reacter_2"]
            },
            "codefuse_reacter_1": {
                "agent_type": "ReactAgent",
                "agent_name": "codefuse_reacter_1",
                "tools": tools,
            },
            "codefuse_reacter_2": {
                "agent_type": "ReactAgent",
                "agent_name": "codefuse_reacter_2",
                "tools": tools,
            }
        }
        os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)

        # log-level，print prompt和llm predict
        os.environ["log_verbose"] = "0"

        # 
        project_config = get_project_config_from_env()
        agent = BaseAgent.init_from_project_config(
            "grouper", project_config
        )

        query_content = "帮我确认下127.0.0.1这个服务器的在10点是否存在异常，请帮我判断一下"
        query = Message(
            role_name="human", 
            role_type="user", 
            content=query_content,
        )
        # agent.pre_print(query)
        output_message = agent.step(query)
        print("input:", output_message.input_text)
        print("content:", output_message.content)
        print("step_content:", output_message.step_content)
    """

    agent_type: str = "GroupAgent"
    """The type of the agent, which is defined as 'GroupAgent'."""

    agent_id: str
    """Unique identifier for the agent."""

    def __init__(
            self, 
            agent_name: str = "codefuse_grouper",
            system_prompt: str = "you are a helpful assistant!\n",
            input_template: Union[str, BaseModel] = "",
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
            **kwargs,
        ):

        super().__init__(
            agent_name=agent_name,
            system_prompt=system_prompt,
            input_template=input_template,
            output_template=group_output_template,
            prompt="",
            agents=agents,
            tools=tools,
            agent_desc=agent_desc,
            agent_config=agent_config,
            model_config=model_config,
            prompt_config=prompt_config,
            project_config = project_config,
            log_verbose=log_verbose,
            **kwargs,
        )
    
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
        select_message = self.inherit_extrainfo(query)
        select_message = self.start_action_step(select_message)

        # get memory from self or memory_manager
        memory = self.get_memory(session_index)

        # generate prompt by prompt manager
        agents = [self.get_agent_by_name(agent_name) for agent_name in self.agents]
        agent_descs = [agent.agent_desc or agent.system_prompt for agent in agents]
        prompt = self.prompt_manager.generate_prompt(
            query=select_message, memory=memory, 
            tools=self.tools, agent_names=self.agents, agent_descs=agent_descs,
        )

        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"{self.agent_name} prompt: {prompt}")

        # predict 
        model = self._get_model()
        content = model.predict(prompt)

        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"{self.agent_name} content: {content}")

        # update infomation
        select_message.update_content(content)
        # common parse llm' content to message
        select_message = self.prompt_manager.parser(select_message)

        output_message = None
        if select_message.parsed_content.get("Role", "") in self.agents:
            agent_name = select_message.parsed_content.get("Role", "")
            agent = self.get_agent_by_name(agent_name)

            # update self_memory
            self.append_history(select_message)
            self.update_memory_manager(select_message, memory_manager)

            # 把除了role以外的信息传给下一个agent
            logger.debug(f"{select_message.parsed_content}")
            select_message.parsed_content.update(
                {k:v for k,v in select_message.parsed_content.items() if k!="Role"}
            )
            logger.debug(f"{select_message.parsed_content}")

            # only query to next agent
            query_bak = self.inherit_extrainfo(query)
            for output_message in agent.step_stream(query_bak, memory_manager, session_index):
                yield output_message or select_message
            
            #
            output_message = self.end_action_step(output_message)

            select_message.update_content(output_message.step_content)
            select_message.update_parsed_content(output_message.parsed_content)
            select_message.update_spec_parsed_content(output_message.spec_parsed_content)

            # update memory pool
            self.append_history(output_message)
            self.update_memory_manager(select_message, memory_manager)
        yield select_message

    def get_agent_by_name(self, agent_name: str) -> BaseAgent:
        """new a agent by agent name and project config"""
        return self.init_from_project_config(agent_name, self.project_config)

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