# -*- coding: utf-8 -*-
"""Model wrapper for OpenAI models
The implementation of this _ModelWrapperMeta are borrowed from
https://github.com/modelscope/agentscope/blob/main/src/agentscope/models/openai_model.py
"""


from abc import ABC
from typing import (
    Union,
    Any,
    List,
    Sequence,
    Dict,
    Optional,
    Generator,
    Literal
)
from urllib.parse import urlparse
import os
import base64
from loguru import logger
try:
    import openai
except ImportError as e:
    raise ImportError(
        "Cannot find openai package, please install it by "
        "`pip install openai`",
    ) from e

from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types import CreateEmbeddingResponse
from .base_model import ModelWrapperBase
from ..schemas import Message



class KimiWrapperBase(ModelWrapperBase, ABC):
    """The model wrapper for OpenAI API.

    Response:
        - From https://platform.moonshot.cn/docs/intro

        ```json
        {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4o-mini",
            "system_fingerprint": "fp_44709d6fcb",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello there, how may I assist you today?",
                    },
                    "logprobs": null,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 9,
                "completion_tokens": 12,
                "total_tokens": 21
            }
        }
        ```
    """

    def __init__(
        self,
        config_name: str,
        model_name: str = None,
        api_key: str = None,
        api_url: str = "https://api.moonshot.cn/v1",
        generate_args: dict = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the openai client.

        Args:
            config_name (`str`):
                The name of the model config.
            model_name (`str`, default `None`):
                The name of the model to use in OpenAI API.
            api_key (`str`, default `None`):
                The API key for OpenAI API. If not specified, it will
                be read from the environment variable `OPENAI_API_KEY`.
            organization (`str`, default `None`):
                The organization ID for OpenAI API. If not specified, it will
                be read from the environment variable `OPENAI_ORGANIZATION`.
            client_args (`dict`, default `None`):
                The extra keyword arguments to initialize the OpenAI client.
            generate_args (`dict`, default `None`):
                The extra keyword arguments used in openai api generation,
                e.g. `temperature`, `seed`.
        """

        if model_name is None:
            model_name = config_name
            logger.warning("model_name is not set, use config_name instead.")

        init_params = locals()
        init_params.pop("self")
        init_params["model_type"] = self.model_type
        super().__init__(**init_params)
        # super().__init__(config_name=config_name, model_name=model_name)

        self.generate_args = generate_args or {}
        self.api_url = api_url or "https://api.moonshot.cn/v1"
        self.client = openai.OpenAI(api_key=api_key, base_url=self.api_url,)

    def format(
        self,
        *args: Union[Message, Sequence[Message]],
    ) -> Union[List[dict], str]:
        raise RuntimeError(
            f"Model Wrapper [{type(self).__name__}] doesn't "
            f"need to format the input. Please try to use the "
            f"model wrapper directly.",
        )


class KimiChatWrapper(KimiWrapperBase):
    """The model wrapper for OpenAI's chat API."""

    model_type: str = "moonshot_chat"

    substrings_in_vision_models_names = ["gpt-4-turbo", "vision", "gpt-4o"]
    """The substrings in the model names of vision models."""

    def __init__(
        self,
        config_name: str,
        model_name: str = None,
        api_key: str = None,
        api_url: str = "https://api.moonshot.cn/v1",
        stream: bool = False,
        generate_args: dict = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the openai client.

        Args:
            config_name (`str`):
                The name of the model config.
            model_name (`str`, default `None`):
                The name of the model to use in OpenAI API.
            api_key (`str`, default `None`):
                The API key for OpenAI API. If not specified, it will
                be read from the environment variable `OPENAI_API_KEY`.
            organization (`str`, default `None`):
                The organization ID for OpenAI API. If not specified, it will
                be read from the environment variable `OPENAI_ORGANIZATION`.
            client_args (`dict`, default `None`):
                The extra keyword arguments to initialize the OpenAI client.
            stream (`bool`, default `False`):
                Whether to enable stream mode.
            generate_args (`dict`, default `None`):
                The extra keyword arguments used in openai api generation,
                e.g. `temperature`, `seed`.
        """

        init_params = locals()
        init_params.pop("self")
        init_params["model_type"] = self.model_type
        self.generate_args = generate_args
        super().__init__(**init_params)
        self.stream = stream

    def __call__(
        self,
        prompt: str = None,
        messages: Sequence[dict] = [],
        tools: Sequence[object] = [],
        *,
        tool_choice: Optional[Literal['auto', 'required']] = None,
        parallel_tool_calls: Optional[bool] = None,
        stop: Optional[str] = '',
        stream: bool = None,
        format_type: Literal['str', 'raw', 'dict'] = 'raw',
        **kwargs: Any,
    ) -> Generator[Union[ChatCompletionChunk, ChatCompletion], None, None]:
        """Processes a list of messages to construct a payload for the OpenAI
        API call. It then makes a request to the OpenAI API and returns the
        response. This method also updates monitoring metrics based on the
        API response.

        Each message in the 'messages' list can contain text content and
        optionally an 'image_urls' key. If 'image_urls' is provided,
        it is expected to be a list of strings representing URLs to images.
        These URLs will be transformed to a suitable format for the OpenAI
        API, which might involve converting local file paths to data URIs.

        Args:
            messages (`list`):
                A list of messages to process.
            stream (`Optional[bool]`, defaults to `None`)
                Whether to enable stream mode, which will override the
                `stream` argument in the constructor if provided.
            **kwargs (`Any`):
                The keyword arguments to OpenAI chat completions API,
                e.g. `temperature`, `max_tokens`, `top_p`, etc. Please refer to
                https://platform.openai.com/docs/api-reference/chat/create
                for more detailed arguments.

        Returns:
            `ModelResponse`:
                The response text in text field, and the raw response in
                raw field.

        Note:
            `parse_func`, `fault_handler` and `max_retries` are reserved for
            `_response_parse_decorator` to parse and check the response
            generated by model wrapper. Their usages are listed as follows:
                - `parse_func` is a callable function used to parse and check
                the response generated by the model, which takes the response
                as input.
                - `max_retries` is the maximum number of retries when the
                `parse_func` raise an exception.
                - `fault_handler` is a callable function which is called
                when the response generated by the model is invalid after
                `max_retries` retries.
        """

        messages = [{"role": "user", "content": prompt}] if prompt else messages

        # step1: prepare keyword arguments
        kwargs = {**self.generate_args, **kwargs}

        # step2: checking messages
        if not isinstance(messages, list):
            raise ValueError(
                "Kimi `messages` field expected type `list`, "
                f"got `{type(messages)}` instead.",
            )
        if not all("role" in Message and "content" in Message for Message in messages):
            raise ValueError(
                "Each message in the 'messages' list must contain a 'role' "
                "and 'content' key for OpenAI API.",
            )

        # step3: forward to generate response
        if stream is None:
            stream = self.stream

        kwargs.update(
            {
                "model": self.model_name,
                "messages": messages,
                "stream": stream,
                "tools": tools,
                "tool_choice": tool_choice,
                "parallel_tool_calls": parallel_tool_calls,
                "stop": stop
            },
        )
        
        response = self.client.chat.completions.create(**kwargs)

        if format_type == "str":
            content = ""
            if stream:
                for chunk in response:
                    content += chunk.choices[0].delta.content or ''
                    yield content
            else:
                yield response.choices[0].message.content
        else:
            if stream:
                for chunk in response:
                    yield chunk
            else:
                yield response

    def format(
        self,
        *args: Union[Message, Sequence[Message]],
    ) -> List[dict]:
        """Format the input string and dictionary into the format that
        OpenAI Chat API required. If you're using a OpenAI-compatible model
        without a prefix "gpt-" in its name, the format method will
        automatically format the input messages into the required format.

        Args:
            args (`Union[Message, Sequence[Message]]`):
                The input arguments to be formatted, where each argument
                should be a `Message` object, or a list of `Message` objects.
                In distribution, placeholder is also allowed.

        Returns:
            `List[dict]`:
                The formatted messages in the format that OpenAI Chat API
                required.
        """

        return ModelWrapperBase.format_for_common_chat_models(*args)


class KimiEmbeddingWrapper(KimiWrapperBase):
    """The model wrapper for OpenAI embedding API.

    Response:
        - Refer to
        https://xx

        ```json
        {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [
                        0.0023064255,
                        -0.009327292,
                        .... (1536 floats total for ada-002)
                        -0.0028842222,
                    ],
                    "index": 0
                }
            ],
            "model": "text-embedding-ada-002",
            "usage": {
                "prompt_tokens": 8,
                "total_tokens": 8
            }
        }
        ```
    """

    model_type: str = "kimi_embedding"

    def __call__(
        self,
        texts: Union[list[str], str],
        **kwargs: Any,
    ) -> CreateEmbeddingResponse:
        """Embed the messages with OpenAI embedding API.

        Args:
            texts (`list[str]` or `str`):
                The messages used to embed.
            **kwargs (`Any`):
                The keyword arguments to OpenAI embedding API,
                e.g. `encoding_format`, `user`. Please refer to
                https://platform.openai.com/docs/api-reference/embeddings
                for more detailed arguments.

        Returns:
            `ModelResponse`:
                A list of embeddings in embedding field and the
                raw response in raw field.

        Note:
            `parse_func`, `fault_handler` and `max_retries` are reserved for
            `_response_parse_decorator` to parse and check the response
            generated by model wrapper. Their usages are listed as follows:
                - `parse_func` is a callable function used to parse and check
                the response generated by the model, which takes the response
                as input.
                - `max_retries` is the maximum number of retries when the
                `parse_func` raise an exception.
                - `fault_handler` is a callable function which is called
                when the response generated by the model is invalid after
                `max_retries` retries.
        """
        raise NotImplementedError(
            f"Model Wrapper [{type(self).__name__}]"
            f" is missing the required `__call__` method",
        )

