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


class SingleAgent(BaseAgent):
    """SingleAgent class that extends the BaseAgent class for simple single-agent tasks.
    
    FunctioncallAgent Examples:
    .. code-block:: python 
        from muagent.schemas import Message, Memory
        from muagent.agents import BaseAgent
        from muagent import get_project_config_from_env

        tools = list(TOOL_SETS)
        tools = ["KSigmaDetector", "MetricsQuery"]
        AGENT_CONFIGS = {
            "codefuse_simpler": {
                "agent_type": "SingleAgent",
                "agent_name": "codefuse_simpler",
                "tools": tools,
                "llm_config_name": "qwen_chat"
            }
        }
        os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)

        project_config = get_project_config_from_env()
        agent = BaseAgent.init_from_project_config(
            "codefuse_simpler", project_config
        )

        query_content = "帮我确认下127.0.0.1这个服务器的在10点是否存在异常，请帮我判断一下"
        query = Message(
            role_name="human", 
            role_type="user", 
            input_text=query_content,
        )
        # base_agent.pre_print(query)
        output_message = agent.step(query)
        print("### intput ###", output_message.input_text)
        print("### content ###", output_message.content)
        print("### step content ###", output_message.step_content)
    """

    agent_type: str = "SingleAgent"
    """The type of the agent, which is defined as 'SingleAgent'."""

    agent_id: str
    """Unique identifier for the agent."""

    def __init__(
            self,
            agent_name: str = "codefuse_simpler",
            system_prompt: str = "you are a helpful assistant!\n",
            input_template: Union[str, BaseModel] = "",
            output_template: Union[str, BaseModel] = "",
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
            output_template=output_template,
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
            session_index: str = "default"
        ) -> Generator[Message, None, None]:
        '''Stream the agent's responses based on an input multi-message query.'''
        
        session_index = query.session_index or session_index

        # Insert the received query into memory
        self.append_history(query)
        self.update_memory_manager(query, memory_manager)

        # Create an output message containing inherited information from the input query
        output_message = self.inherit_extrainfo(query)
        output_message = self.start_action_step(output_message)

        # Retrieve memory for the current session, either from self or the memory manager
        memory = self.get_memory(session_index)
        
        # Generate a prompt using the prompt manager
        prompt = self.prompt_manager.generate_prompt(
            query=output_message, memory=memory, tools=self.tools
        )
        
        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"{self.agent_name} prompt: {prompt}")

        # Predict the content using the agent's model
        model = self._get_model()
        content = model.predict(prompt)

        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"{self.agent_name} content: {content}")

        # Update the output message with the predicted content
        output_message.update_content(content)
        
        # Parse the output content into a structured message format
        output_message = self.prompt_manager.parser(output_message)

        # Process any actions or observations required based on the output message
        output_message, observation_message = self.message_util.step_router(
            output_message, 
            session_index=session_index,
            tools=self.tools,
        )

        # Wrap up any action steps
        output_message = self.end_action_step(output_message)

        # Update memory with the output message and any observations
        self.append_history(output_message)
        self.update_memory_manager(output_message, memory_manager)
        if observation_message:
            self.append_history(observation_message)
            self.update_memory_manager(observation_message, memory_manager)

        yield output_message  # Yield the constructed output message
    
    def pre_print(
            self, 
            query: Message, 
            memory_manager: BaseMemoryManager=None, 
            tools: List[str] = [],
            session_index: str = "default"
        ) -> None:
        """Prepare and print the prompt format for this agent based on the input query."""
        session_index = query.session_index or session_index
        # Prepare an output message with inherited information
        output_message = self.inherit_extrainfo(query)
        output_message = self.start_action_step(output_message)

        # Insert query into memory for later reference
        self.append_history(query)
        self.update_memory_manager(query, memory_manager)
        
        # Get the current memory for the session
        memory = self.get_memory(session_index)

        # Generate and format the prompt
        prompt = self.prompt_manager.pre_print(query=query, memory=memory, tools=tools or self.tools)

        # Display the prompt for this agent
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