from abc import ABCMeta
from pydantic import BaseModel
import os
from typing import (
    List, 
    Union, 
    Generator, 
    Any, 
    Type,
    Optional,
    Literal
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
from ..schemas.models import ModelConfig
from ..schemas.models import LLMConfig as TempLLMConfig
from ..memory_manager import BaseMemoryManager
from ..prompt_manager import BasePromptManager
from ..models import ModelWrapperBase, get_model

from .agent_util import MessageUtil
from muagent.connector.schema import LogVerboseEnum
from muagent.llm_models import getChatModelFromConfig


class _AgentWapperBase(ABCMeta):
    """A meta class to replace the tool wrapper's run function with
    a wrapper that handles errors gracefully.
    """

    def __new__(mcs, name: Any, bases: Any, attrs: Any) -> Any:
        if "__call__" in attrs:
            attrs["__call__"] = attrs["__call__"]
        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name: Any, bases: Any, attrs: Any) -> None:
        # Initialize class-level registries for storing agent classes
        if not hasattr(cls, "_registry"):
            cls._registry = {}  # Registry of agent class names
            cls._type_registry = {}  # Registry of agent class type names
        else:
            # Register the current class in the registry
            cls._registry[name] = cls
            cls._type_registry[cls.agent_type] = cls
        super().__init__(name, bases, attrs)


class BaseAgent(metaclass=_AgentWapperBase):
    """Base class for agents, providing initialization and interaction methods.

    You can define your custom agent for your agent work, such as
    .. code-block:: python

        from muagent.schemas.message import BaseAgent

        class SingleAgent(BaseAgent):
            """"""
            agent_type: str = "SingleAgent"
            """"""
            agent_id: str
            """"""
            def __init__(
                    self,
                    agent_name: str = "codefuse_simpler",
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
                '''agent response from multi-message'''
                session_index = query.session_index or session_index
                # insert query into memory
                ...
                # transform query into output_message.input_text
                ...
                # get memory from self or memory_manager
                ...
                # generate prompt by prompt manager
                ...
                # predict
                ...
                # update infomation
                ...
                # common parse llm' content to message
                ...
                # todo: action step
                ...
                # end
                ...
                # update self_memory and memory pool
                ...
                def pre_print(
                        self, 
                        query: Message, 
                        memory_manager: BaseMemoryManager=None, 
                        tools: List[str] = [],
                        session_index: str = "default"
                        
                    ) -> None:
                    pass
    """

    agent_type: str = "BaseAgent"
    """Defines the type of the agent (default is BaseAgent)."""

    agent_id: str
    """Unique identifier for the agent."""

    def __init__(
            self,
            agent_name: str = "codefuse_baser",
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
        # Configure logging verbosity
        self.log_verbose = max(os.environ.get("log_verbose", "0"), log_verbose)

        # Initialize agent properties
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.input_template = input_template
        self.output_template = output_template
        self.prompt = prompt
        self.agent_desc = agent_desc
        self.agents = agents
        self.tools = tools
        self.agent_config = agent_config
        self.prompt_config = prompt_config
        self.model_config = model_config
        self.project_config = project_config
        #
        self.memory: Memory = Memory()
        self.message_util = MessageUtil()

        # Initialize agent from configuration data
        self._init_from_configs()

    def _init_from_configs(self):
        '''Initialize agent's configuration from provided parameters.'''
        if not self.agent_name:
            raise ValueError(
                f"Init a agent must have a agent name."
            )
        # Load configurations
        self._init_agent_config()
        self._init_model_config()
        self._init_prompt_config()

    def _init_agent_config(self):
        '''Initialize agent configuration (AgentConfig).'''
        # Load agent configuration based on the agent name and project config
        if self.agent_name and self.project_config and self.project_config.agent_configs:
            tmp_agent_config = self.project_config.agent_configs.get(self.agent_name)
            self.agent_config = self.agent_config or tmp_agent_config
            
        if self.agent_config and isinstance(self.agent_config, AgentConfig):
            # Set agent properties from the configuration
            self.agent_name = self.agent_config.agent_name
            self.system_prompt = self.system_prompt or self.agent_config.system_prompt
            self.input_template = self.input_template or self.agent_config.input_template
            self.output_template = self.output_template or self.agent_config.output_template
            self.prompt = self.prompt or self.agent_config.prompt
            self.agent_desc = self.agent_desc or self.agent_config.agent_desc
            self.tools = self.tools or self.agent_config.tools or self.tools
            self.agents = self.agents or self.agent_config.agents
            self._llm_config_name = self.agent_config.llm_config_name
            self._em_config_name = self.agent_config.em_config_name
            self._prompt_config_name = self.agent_config.prompt_config_name
        
    def _init_model_config(self):
        '''Initialize model configuration (ModelConfig).'''
        # Check if model_config was provided
        if self.model_config:
            pass
        # Load model configuration from project config if not provided
        elif self.agent_name and self.project_config and self.project_config.model_configs:
            if self._llm_config_name in self.project_config.model_configs:
                self.model_config = self.project_config.model_configs[self._llm_config_name]
            elif "default_chat" in self.project_config.model_configs:
                self.model_config = self.project_config.model_configs["default_chat"]
            else:
                raise ValueError(
                    f"While init a model, project_config must have model configs. "
                    f"However, there is something wrong in agent_name: {self.agent_name} "
                    f"agent_config: {self.project_config.model_configs} "
                )
        else:
            raise ValueError(
                f"While init a model, it must have model config. "
                f"However, there is something wrong in agent_name: {self.agent_name} "
                f"agent_config: {self.project_config} "
            )

    def _init_prompt_config(self):
        '''Initialize prompt configuration (PromptConfig).'''
        # Load prompt configuration based on the agent's name and project config
        if self.agent_name and self.project_config and self.project_config.prompt_configs:
            self.prompt_config = self.project_config.prompt_configs.get(
                self.agent_name, PromptConfig()
            )
            self._init_prompt_manager()
        else:
            self.prompt_config = PromptConfig()  # Fallback to default prompt config
            self._init_prompt_manager()

    def _init_prompt_manager(self):
        '''Initialize prompt manager from prompt configurations.'''
        self.prompt_manager = BasePromptManager.from_config(
            system_prompt=self.system_prompt,
            input_template=self.input_template,
            output_template=self.output_template,
            prompt=self.prompt,
            prompt_config=self.prompt_config,
        )

    def copy_config(self) -> ProjectConfig:
        '''Create a copy of the current agent's configuration for use in a project.'''
        return ProjectConfig(
            agent_configs={self.agent_config.config_name: self.agent_config} if self.agent_config  else {}, 
            prompt_configs={self.prompt_config.config_name: self.prompt_config} if self.prompt_config  else {}, 
            model_configs={self.model_config.config_name: self.model_config} if self.model_config  else {}, 
        )

    @classmethod
    def init_from_project_config(cls, agent_name: str, project_config: ProjectConfig) -> 'BaseAgent':
        '''Create a new instance of the agent from project configuration.'''
        agent_config = project_config.agent_configs[agent_name]
        agent_type = agent_config.agent_type
        model_config = (
            project_config.model_configs[agent_config.llm_config_name]
            if agent_config.llm_config_name 
            else project_config.model_configs["default_chat"]
        )
        prompt_config = (
            project_config.prompt_configs[agent_config.prompt_config_name]
            if agent_config.prompt_config_name
            else PromptConfig()
        )
        return cls.get_wrapper(agent_type)(
            agent_config=agent_config, 
            model_config=model_config,
            prompt_config=prompt_config,
            project_config=project_config
        )

    @classmethod
    def get_wrapper(cls, agent_type: str) -> Type['BaseAgent']:
        '''Retrieve the appropriate agent class wrapper based on the agent type.

        Args:
            agent_type (str): 
                A string that specifies the type of agent for which a wrapper 
                class is requested. This string is used to look up the 
                appropriate agent class from the registered agent type registry.

        Returns:
            Type['BaseAgent']: 
                The method returns the appropriate subclass of BaseAgent based on 
                the provided agent_type. If the agent_type is found in the 
                class's _type_registry or _registry, it returns the corresponding 
                class. If not found, it raises a KeyError.
        '''
        if agent_type in cls._type_registry:
            return cls._type_registry[agent_type]
        elif agent_type in cls._registry:
            return cls._registry[agent_type]
        else:
            raise KeyError(
                f"Agent Library is missing "
                f"{agent_type}, please check your agent type"
            )

    def step(
            self, 
            query: Message, 
            memory_manager: Optional[BaseMemoryManager]=None, 
            session_index: str = "default",
            **kwargs
        ) -> Optional[Message]:
        '''Process a query and return the agent's response.

        Args:
            query (Message): 
                An instance of the Message class containing the 
                input query for the agent.
            memory_manager (Optional[BaseMemoryManager]): 
                An optional memory manager instance for managing message history.
            session_index (str, default="default"): 
                A string representing the session index for message tracking and management.
            kwargs: Additional keyword arguments for extended functionality.

        Returns:
            Optional[Message]: 
                The final response from the agent as an instance of the Message class, 
                or None if no response is available.
        '''
        session_index = query.session_index or session_index
        message = None
        # Retrieve the final message from the step_stream generator
        for message in self.step_stream(
            query, memory_manager, session_index, **kwargs
        ):
            pass
        return message

    def step_stream(
            self, 
            query: Message, 
            memory_manager: Optional[BaseMemoryManager]=None, 
            session_index: str = "default"
        ) -> Generator[Message, None, None]:
        '''Stream the agent's responses over multiple messages.

        Args:
            query (Message): 
                An instance of the Message class containing the 
                input query for the agent.
            memory_manager (Optional[BaseMemoryManager]): 
                An optional memory manager instance for managing message history.
            session_index (str, default="default"): 
                A string representing the session index for message tracking and management.

        Returns:
            Generator[Message, None, None]: 
                A generator that yields multiple Message instances as responses to the input query.
        '''
        raise NotImplementedError(
            f"Agent Wrapper [{type(self).__name__}]"
            f" is missing the required `step_stream`"
            f" method.",
        )
    
    def pre_print(
            self, 
            query: Message, 
            memory_manager: BaseMemoryManager=None,
            session_index: str = "default",
            **kwargs
        ) -> None:
        """Pre-print this agent's prompt format.

        Args:
            query (Message): 
                An instance of the Message class containing the 
                input query for the agent.
            memory_manager (Optional[BaseMemoryManager]): 
                An optional memory manager instance for managing message history.
            session_index (str, default="default"): 
                A string representing the session index for message tracking and management.
        """
        session_index = query.session_index or session_index
        # Generate the output message before proceeding with the agent action
        output_message = self.inherit_extrainfo(query)
        output_message = self.start_action_step(output_message)

        # Insert query into history memory
        self.append_history(query)
        self.update_memory_manager(query, memory_manager)
        
        # Retrieve memory for the current session
        memory = self.get_memory(session_index)
        prompt = self.prompt_manager.pre_print(query=query, memory=memory, **kwargs)

        # Displaying the formatted prompt for the agent
        title = f"<<<<{self.agent_name}'s prompt>>>>"
        print("#"*len(title) + f"\n{title}\n" + "#"*len(title) + f"\n\n{prompt}\n\n")

    def inherit_extrainfo(self, input: Message):
        """Incorporate additional information from the last message into the new message."""
        output_message = Message(
            role_name=self.agent_name,
            role_type="assistant",
            session_index=input.session_index,
        )
        output_message.update_input(input)
        output_message.global_kwargs = copy.deepcopy(input.global_kwargs)  # Preserve global args
        return output_message
    
    def registry_actions(self, actions):
        '''Register actions related to the LLM model.'''
        self.action_list = actions

    def start_action_step(self, message: Message) -> Message:
        '''Perform actions before predicting the response from the agent.'''
        # (To be implemented) Additional actions can be done here
        return message

    def end_action_step(self, message: Message) -> Message:
        '''Perform actions after the agent has predicted a response.'''
        # (To be implemented) Additional actions can be done here
        return message
    
    def update_memory_manager(
            self, 
            message: Message,
            memory_manager: Optional[BaseMemoryManager] = None, 
        ):
        """Update the memory manager with the latest message."""
        if memory_manager:
            memory_manager.append(message, self.agent_name)

    def init_history(self, memory: Memory = None) -> Memory:
        """Initialize message history."""
        return Memory(messages=[])
    
    def update_history(self, message: Message):
        """Update the agent's internal history with a new message."""
        self.memory.append(message)

    def append_history(self, message: Message):
        """Append a new message to the agent's history."""
        self.memory.append(message)
        
    def clear_history(self):
        """Clear the agent's memory history."""
        self.memory.clear()
        self.memory = self.init_history()

    def get_memory(
            self, 
            session_index: str,
            memory_manager: Optional[BaseMemoryManager] = None, 
        ) -> Memory:
        """Retrieve the agent's memory for a given session index."""
        if memory_manager:
            return memory_manager.get_memory_pool(session_index=session_index)
        return self.memory
    
    def memory_to_format_messages(
            self,
            attributes: dict[str, Union[any, List[any]]] = {},
            filter_type: Optional[Literal['select', 'filter']] = None,
            *,
            return_all: bool = True, 
            content_key: str = "response", 
            with_tag: bool = False,
            format_type: Literal['raw', 'tuple', 'dict', 'str']='raw',
            logic: Literal['or', 'and'] = 'and'
        ) -> List:
        """Format the stored memory into specific message formats based on parameters."""
        kwargs = locals()
        kwargs.pop("self")
        kwargs.pop("class")
        return self.memory.to_format_messages(**kwargs)

    def _get_model(self) -> ModelWrapperBase:
        """Retrieve the model wrapper based on the model configuration."""
        if isinstance(self.model_config, ModelConfig):
            return get_model(self.model_config)
        elif isinstance(self.model_config, TempLLMConfig):
            return getChatModelFromConfig(self.model_config)