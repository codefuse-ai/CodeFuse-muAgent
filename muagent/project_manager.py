from typing import (
    Dict,
    Optional,
    Union
)
import os, sys, json, random
from loguru import logger


from .schemas.models import ModelConfig, LLMConfig
from .schemas import ProjectConfig, PromptConfig, AgentConfig


def get_project_config_from_env(
    agent_configs: Optional[Dict[str, AgentConfig]] = None,
    model_configs: Optional[Dict[str, Union[ModelConfig, LLMConfig]]] = None,
    prompt_configs: Optional[Dict[str, PromptConfig]] = PromptConfig(),
) -> ProjectConfig:
    """"""
    init_dict = {
        "model_configs": [model_configs, ModelConfig],
        "agent_configs": [agent_configs, AgentConfig],
        "prompt_configs": [prompt_configs, PromptConfig],
    }
    project_configs = {
        "model_configs": None,
        "agent_configs": None,
        "prompt_configs": None,
    }
    for k, (v, _type) in init_dict.items():
        if v:
            pass
        elif k.upper() in os.environ:
            v = json.loads(os.environ[k.upper()])
            vc = {}
            for kk, vv in v.items():
                try:
                    vc[kk] = _type(**vv)
                except:
                    vc[kk] = LLMConfig(**vv)
            v = vc
            if v:
                chat_list = [_type for _type in v.keys() if "chat" in _type]
                embedding_list = [_type for _type in v.keys() if "embedding" in _type]
                if chat_list:
                    v["default_chat"] = v[random.choice(chat_list)]
                    model_type = random.choice(chat_list)
                    default_model_config = v[model_type]
                    os.environ["DEFAULT_MODEL_TYPE"] = model_type
                    os.environ["DEFAULT_MODEL_NAME"] = default_model_config.model_name
                    os.environ["DEFAULT_API_KEY"] = default_model_config.api_key or ""
                    os.environ["DEFAULT_API_URL"] = default_model_config.api_url or ""
                if embedding_list:
                    v["default_embed"] = v[random.choice(embedding_list)]
                    model_type = random.choice(chat_list)
                    default_model_config = v[model_type]
                    os.environ["DEFAULT_EMBED_MODEL_TYPE"] = model_type
                    os.environ["DEFAULT_EMBED_MODEL_NAME"] = default_model_config.model_name
                    os.environ["DEFAULT_EMBED_API_KEY"] = default_model_config.api_key or ""
                    os.environ["DEFAULT_EMBED_API_URL"] = default_model_config.api_url or ""
                project_configs[k] = v
            else:
                logger.warning(
                f"Cant't init any {k} in this env."
            )
        else:
            logger.warning(
                f"Cant't init any {k} in this env."
            ) 
    return ProjectConfig(**project_configs)