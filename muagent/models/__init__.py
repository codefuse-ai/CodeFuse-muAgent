# -*- coding: utf-8 -*-
""" Import modules in models package."""
from typing import Type
from loguru import logger

from ..schemas.models import ModelConfig
from .base_model import ModelWrapperBase
from .openai_model import (
    OpenAIWrapperBase,
    OpenAIChatWrapper,
    # OpenAIDALLEWrapper,
    OpenAIEmbeddingWrapper,
)
from .dashscope_model import (
    DashScopeChatWrapper,
    # DashScopeImageSynthesisWrapper,
    DashScopeTextEmbeddingWrapper,
    # DashScopeMultiModalWrapper,
)
from .ollama_model import (
    OllamaChatWrapper,
    OllamaEmbeddingWrapper,
    # OllamaGenerationWrapper,
)
from .qwen_model import (
    QwenChatWrapper,
    QwenTextEmbeddingWrapper
)
from .kimi_model import (
    KimiChatWrapper,
    KimiEmbeddingWrapper
)
# from .gemini_model import (
#     GeminiChatWrapper,
#     GeminiEmbeddingWrapper,
# )
# from .zhipu_model import (
#     ZhipuAIChatWrapper,
#     ZhipuAIEmbeddingWrapper,
# )
# from .litellm_model import (
#     LiteLLMChatWrapper,
# )
from .yi_model import (
    YiChatWrapper,
)

__all__ = [
    "ModelWrapperBase",
    "ModelResponse",
    "PostAPIModelWrapperBase",
    "PostAPIChatWrapper",
    "OpenAIWrapperBase",
    "OpenAIChatWrapper",
    "OpenAIDALLEWrapper",
    "OpenAIEmbeddingWrapper",
    "DashScopeChatWrapper",
    "DashScopeImageSynthesisWrapper",
    "DashScopeTextEmbeddingWrapper",
    "DashScopeMultiModalWrapper",
    "OllamaChatWrapper",
    "OllamaEmbeddingWrapper",
    "OllamaGenerationWrapper",
    "GeminiChatWrapper",
    "GeminiEmbeddingWrapper",
    "ZhipuAIChatWrapper",
    "ZhipuAIEmbeddingWrapper",
    "LiteLLMChatWrapper",
    "YiChatWrapper",
    "QwenChatWrapper",
    "QwenTextEmbeddingWrapper",
    "KimiChatWrapper",
    "KimiEmbeddingWrapper"
]


def _get_model_wrapper(model_type: str) -> Type[ModelWrapperBase]:
    """Get the specific type of model wrapper

    Args:
        model_type (`str`): The model type name.

    Returns:
        `Type[ModelWrapperBase]`: The corresponding model wrapper class.
    """
    wrapper = ModelWrapperBase.get_wrapper(model_type=model_type)
    if wrapper is None:
        raise KeyError(
            f"Unsupported model_type [{model_type}],"
            "use PostApiModelWrapper instead.",
        )
    return wrapper


def get_model(model_config: ModelConfig) -> ModelWrapperBase:
    """Get the model by model config

    Args:
        model_config (`ModelConfig`): The model config

    Returns:
        `ModelWrapperBase`: The specific model
    """
    return ModelWrapperBase.from_config(model_config)