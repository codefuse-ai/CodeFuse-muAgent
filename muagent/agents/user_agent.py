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


class UserAgent(BaseAgent):
    """UserAgent class that extends the BaseAgent class for simulating user' response."""

    agent_type: str = "UserAgent"
    """The type of the agent, which is defined as 'UserAgent'."""

    agent_id: str
    """Unique identifier for the agent."""

    def __init__(
            self,
            agent_name: str = "codefuse_user",
            system_prompt: str = "",
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

        # insert query into memory
        self.append_history(query)
        self.update_memory_manager(query, memory_manager)

        # transform query into output_message.input_text
        output_message = self.inherit_extrainfo(query)
        output_message = self.start_action_step(output_message)

        # get memory from self or memory_manager
        memory = self.get_memory(session_index)
        
        # generate prompt by prompt manager
        prompt = self.prompt_manager.generate_prompt(
            query=output_message, memory=memory, tools=self.tools
        )
        
        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"{self.agent_name} prompt: {prompt}")

        # predict 
        content = input("please answer: \n")

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
        title = f"<<<<{self.agent_name}'s prompt>>>>"
        print("#"*len(title) + f"\n{title}\n"+ "#"*len(title)+ f"\n\n{query.content}\n\n")
