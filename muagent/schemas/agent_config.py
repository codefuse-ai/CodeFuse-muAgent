
from pydantic import BaseModel, root_validator
from typing import List, Dict, Optional, Union, Literal


class PromptConfig(BaseModel):
    """The dataclass for prompt config."""

    config_name: str = "codefuse"
    """The config name of prompt."""

    prompt_manager_type: str = "CommonPromptManager"
    """The type of prompt manager."""

    language: Literal['en', 'zh'] = 'en'
    """The language of prompt manager."""


class AgentConfig(BaseModel):
    """The dataclass for agent config"""

    config_name: str
    """The name of the agent configuration. It equals to agent name"""

    agent_type: str
    """The type of the agent wrapper, which is to identify the agent wrapper
    class in model configuration."""

    agent_name: str
    """The name of the agent, which is used in agent api calling. It will eqaul to role name"""

    agent_desc: str = ""
    """The role description of this role."""

    system_prompt: str = ""
    """The system prompt of this role."""

    input_template: Union[str, BaseModel] = ""
    """The input template for role."""

    output_template: Union[str, BaseModel] = ""
    """The output template for role."""

    prompt: str = ""
    """The full prompt of this role. it will override system prompt + input prompt + output prompt"""

    tools: List[str] = []
    """The tools' name of this role. it will use these tools to complete task"""

    agents: List[str] = []
    """This role can manage some agents. It will ask one agent to complete task"""

    # 
    llm_config_name: Optional[str]
    """The name of the llm model configuration."""

    em_config_name: Optional[str]
    """The name of the embedding model configuration."""

    prompt_config_name: Optional[str]
    """"""

    @root_validator(pre=True)
    def set_default_config_name(cls, values):
        """Set config_name to model_name if config_name is not provided."""
        if 'config_name' not in values or values['config_name'] is None:
            values['config_name'] = values.get('agent_name')
        return values