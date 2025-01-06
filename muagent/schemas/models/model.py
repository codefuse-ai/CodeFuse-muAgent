

from pydantic import BaseModel, root_validator
from typing import List, Dict, Optional, Union, Literal



class ModelConfig(BaseModel):
    """The dataclass for model config."""

    config_name: Optional[str] = None
    """The name of the model configuration. It equals to model_name or model_type."""

    model_type: str
    """The type of the model wrapper, which is to identify the model wrapper
    class in model configuration."""

    model_name: str
    """The name of the model, which is used in model api calling."""
    
    api_key: Optional[str] = None
    """The api key of the model, which is used in model api calling."""

    api_url: Optional[str] = None
    """The api url of the model, which is used in model api calling."""

    max_tokens: Optional[int] = None
    """The max_tokens of the model, which is used in model api calling."""

    top_p: float = 0.9
    """The top_p of the model, which is used in model api calling."""

    temperature: float = 0.3
    """The temperature of the model, which is used in model api calling."""

    stream: bool = False
    """The stream mode of the model, which is used in model api calling."""

    @root_validator(pre=True)
    def set_default_config_name(cls, values):
        """Set config_name to model_name if config_name is not provided."""
        if 'config_name' not in values or values['config_name'] is None:
            values['config_name'] = values.get('model_name')
        return values
    


class LLMConfig(BaseModel):
    """temp config will delete"""
    model_name: str = "gpt-3.5-turbo"
    model_engine: str = "openai"
    temperature: float = 0.3    
    stop: Union[List[str], str] = None
    api_key: str = ""
    api_base_url: str = ""
    llm: Optional[str] = ""