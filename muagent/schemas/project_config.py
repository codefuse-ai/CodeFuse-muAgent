
from pydantic import BaseModel, Field
from typing import (
    List, 
    Dict, 
    Optional, 
    Union, 
    Literal,
    Any
)

from .models import ModelConfig, LLMConfig
from .agent_config import AgentConfig, PromptConfig
from .db import GBConfig, TBConfig



class ProjectConfig(BaseModel):
    """The dataclass of project config"""

    agent_configs: Optional[Dict[str, AgentConfig]]
    """"""

    prompt_configs: Optional[Dict[str, PromptConfig]]
    """"""

    model_configs: Optional[Dict[str, Any]]
    """"""

    graph: Any = None
    """"""

    def extend_agent_configs(
            self, 
            agent_configs: Union[AgentConfig, List[AgentConfig], Dict[str, AgentConfig]]
        ):

        if isinstance(agent_configs, AgentConfig):
            self.agent_configs.update({agent_configs.config_name: agent_configs})

        if isinstance(agent_configs, List):
            self.agent_configs.update({
                i.config_name: agent_configs for i in agent_configs 
                if isinstance(agent_configs, AgentConfig)
            })                      
        elif isinstance(agent_configs,  Dict):
            self.agent_configs.update(agent_configs)
    
    def extend_prompt_configs(
            self, 
            prompt_configs: Union[PromptConfig, List[PromptConfig], Dict[str, PromptConfig]]
        ):
        if isinstance(prompt_configs, PromptConfig):
            self.prompt_configs.update({prompt_configs.config_name: prompt_configs})

        if isinstance(prompt_configs, List):
            self.prompt_configs.update({
                i.config_name: prompt_configs for i in prompt_configs 
                if isinstance(prompt_configs, PromptConfig)
            })                      
        elif isinstance(prompt_configs,  Dict):
            self.prompt_configs.update(prompt_configs)

    def extend_model_configs(
            self, 
            model_configs: Union[ModelConfig, List[ModelConfig], Dict[str, ModelConfig]]
        ):
        if isinstance(model_configs, ModelConfig):
            self.model_configs.update({model_configs.config_name: model_configs})

        if isinstance(model_configs, List):
            self.model_configs.update({
                i.config_name: model_configs for i in model_configs 
                if isinstance(model_configs, ModelConfig)
            })                      
        elif isinstance(model_configs,  Dict):
            self.model_configs.update(model_configs)

    def extend_graph(self, graph):
        """wait"""
        pass

    def __add__(self, other: 'ProjectConfig') -> 'ProjectConfig':
        if isinstance(other, ProjectConfig):
            self.extend_agent_configs(other.agent_configs)
            self.extend_prompt_configs(other.model_configs)
            self.extend_prompt_configs(other.prompt_configs)
            self.extend_graph(other.graph)
            return self
        else:
            raise ValueError(f"cant add unspecified type like as {type(other)}")
        


class EKGProjectConfig(BaseModel):
    """The dataclass of project config"""
    
    config_name: str = "default"
    """The config name of EKG Project"""

    model_configs: Optional[Dict[str, Union[ModelConfig, Any]]]
    """"""

    embed_configs: Optional[Dict[str, ModelConfig]]
    """"""

    agent_configs: Optional[Dict[str, AgentConfig]]
    """"""
    
    prompt_configs: Optional[Dict[str, PromptConfig]]
    """"""

    db_configs: Optional[Dict[str, Union[GBConfig, TBConfig]]]
    """"""