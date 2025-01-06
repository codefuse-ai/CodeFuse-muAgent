# -*- coding: utf-8 -*-
"""Model wrapper for DashScope models"""
import os
from abc import ABC
from http import HTTPStatus
from typing import (
    Any,
    Union,
    List,
    Sequence,
    Optional,
    Generator,
    Literal
)

import openai
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from loguru import logger

try:
    import dashscope

    dashscope_version = dashscope.version.__version__
    if dashscope_version < "1.19.0":
        logger.warning(
            f"You are using 'dashscope' version {dashscope_version}, "
            "which is below the recommended version 1.19.0. "
            "Please consider upgrading to maintain compatibility.",
        )
    from dashscope.api_entities.dashscope_response import GenerationResponse
except ImportError:
    dashscope = None
    GenerationResponse = None


from ..schemas import Message
from .base_model import ModelWrapperBase
from ..utils.common_utils import _convert_to_str



class QwenWrapperBase(ModelWrapperBase, ABC):
    """The model wrapper for DashScope API."""

    def __init__(
        self,
        config_name: str,
        model_name: str = None,
        api_key: str = None,
        generate_args: dict = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the DashScope wrapper.

        Args:
            config_name (`str`):
                The name of the model config.
            model_name (`str`, default `None`):
                The name of the model to use in DashScope API.
            api_key (`str`, default `None`):
                The API key for DashScope API.
            generate_args (`dict`, default `None`):
                The extra keyword arguments used in DashScope api generation,
                e.g. `temperature`, `seed`.
        """
        if model_name is None:
            model_name = config_name
            logger.warning("model_name is not set, use config_name instead.")

        super().__init__(config_name=config_name, model_name=model_name)

        self.generate_args = generate_args or {}

        self.api_key = api_key
        self.max_length = None

    def format(
        self,
        *args: Union[Message, Sequence[Message]],
    ) -> Union[List[dict], str]:
        raise RuntimeError(
            f"Model Wrapper [{type(self).__name__}] doesn't "
            f"need to format the input. Please try to use the "
            f"model wrapper directly.",
        )


class QwenChatWrapper(QwenWrapperBase):
    """The model wrapper for DashScope's chat API, refer to
    https://help.aliyun.com/zh/dashscope/developer-reference/api-details

    Response:
        - Refer to
        https://help.aliyun.com/zh/dashscope/developer-reference/quick-start?spm=a2c4g.11186623.0.0.7e346eb5RvirBw

        ```json
        {
            "status_code": 200,
            "request_id": "a75a1b22-e512-957d-891b-37db858ae738",
            "code": "",
            "message": "",
            "output": {
                "text": null,
                "finish_reason": null,
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": "xxx"
                        }
                    }
                ]
            },
            "usage": {
                "input_tokens": 25,
                "output_tokens": 77,
                "total_tokens": 102
            }
        }
        ```
    """

    model_type: str = "qwen_chat"

    def __init__(
        self,
        config_name: str,
        model_name: str = None,
        api_key: str = None,
        api_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        stream: bool = False,
        generate_args: dict = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the DashScope wrapper.

        Args:
            config_name (`str`):
                The name of the model config.
            model_name (`str`, default `None`):
                The name of the model to use in DashScope API.
            api_key (`str`, default `None`):
                The API key for DashScope API.
            stream (`bool`, default `False`):
                If True, the response will be a generator in the `stream`
                field of the returned `ModelResponse` object.
            generate_args (`dict`, default `None`):
                The extra keyword arguments used in DashScope api generation,
                e.g. `temperature`, `seed`.
        """

        super().__init__(
            config_name=config_name,
            model_name=model_name,
            api_key=api_key,
            generate_args=generate_args,
            **kwargs,
        )
        self.api_url = api_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.stream = stream
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.api_url)

    def __call__(
        self,
        prompt: str = None,
        messages: Sequence[dict] = [],
        tools: Sequence[object] = [],
        *,
        tool_choice: Optional[Literal['auto', 'required']] = None,
        parallel_tool_calls: Optional[bool] = None,
        stream: Optional[bool] = None,
        stop: Optional[str] = '',
        format_type: Literal['str', 'raw', 'dict'] = 'raw',
        **kwargs
    ) -> Generator[Union[ChatCompletionChunk, ChatCompletion], None, None]:
        """Invoke the Yi Chat API by sending a list of messages."""
        
        messages = [{"role": "user", "content": prompt}] if prompt else messages
        # Checking messages
        if not isinstance(messages, list):
            raise ValueError(
                f"Yi `messages` field expected type `list`, "
                f"got `{type(messages)}` instead.",
            )

        if not all("role" in Message and "content" in Message for Message in messages):
            raise ValueError(
                "Each message in the 'messages' list must contain a 'role' "
                "and 'content' key for Yi API.",
            )
        # 

        stream = stream or self.stream
        model_name = self.model_name
        # 
        # step1: prepare keyword arguments
        kwargs = {**self.generate_args, **kwargs}
        kwargs.update(
            {
                "model": model_name,
                "messages": messages,
                "stream": stream,
                "stop": stop
                # "tools": tools,
                # "tool_choice": tool_choice,
                # "parallel_tool_calls": parallel_tool_calls,
            },
        )
        if tools:
            kwargs["tools"] = tools

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
        """A common format strategy for chat models, which will format the
        input messages into a user message.

        Note this strategy maybe not suitable for all scenarios,
        and developers are encouraged to implement their own prompt
        engineering strategies.

        The following is an example:

        .. code-block:: python

            prompt1 = model.format(
                Message("system", "You're a helpful assistant", role="system"),
                Message("Bob", "Hi, how can I help you?", role="assistant"),
                Message("user", "What's the date today?", role="user")
            )

            prompt2 = model.format(
                Message("Bob", "Hi, how can I help you?", role="assistant"),
                Message("user", "What's the date today?", role="user")
            )

        The prompt will be as follows:

        .. code-block:: python

            # prompt1
            [
                {
                    "role": "system",
                    "content": "You're a helpful assistant"
                },
                {
                    "role": "user",
                    "content": (
                        "## Conversation History\\n"
                        "Bob: Hi, how can I help you?\\n"
                        "user: What's the date today?"
                    )
                }
            ]

            # prompt2
            [
                {
                    "role": "user",
                    "content": (
                        "## Conversation History\\n"
                        "Bob: Hi, how can I help you?\\n"
                        "user: What's the date today?"
                    )
                }
            ]


        Args:
            args (`Union[Msg, Sequence[Msg]]`):
                The input arguments to be formatted, where each argument
                should be a `Msg` object, or a list of `Msg` objects.
                In distribution, placeholder is also allowed.

        Returns:
            `List[dict]`:
                The formatted messages.
        """

        return ModelWrapperBase.format_for_common_chat_models(*args)


    def format_prompt(self, *args: Union[Message, Sequence[Message]]) -> str:
        """Forward the input to the model.

        Args:
            args (`Union[Msg, Sequence[Msg]]`):
                The input arguments to be formatted, where each argument
                should be a `Msg` object, or a list of `Msg` objects.
                In distribution, placeholder is also allowed.

        Returns:
            `str`:
                The formatted string prompt.
        """
        input_msgs: List[Message] = []
        for _ in args:
            if _ is None:
                continue
            if isinstance(_, Message):
                input_msgs.append(_)
            elif isinstance(_, list) and all(isinstance(__, Message) for __ in _):
                input_msgs.extend(_)
            else:
                raise TypeError(
                    f"The input should be a Msg object or a list "
                    f"of Msg objects, got {type(_)}.",
                )

        sys_prompt = None
        dialogue = []
        for i, unit in enumerate(input_msgs):
            if i == 0 and unit.role_type == "system":
                # system prompt
                sys_prompt = unit.content
            else:
                # Merge all messages into a conversation history prompt
                dialogue.append(
                    f"{unit.role_name}: {unit.content}",
                )

        dialogue_history = "\n".join(dialogue)

        if sys_prompt is None:
            prompt_template = "## Conversation History\n{dialogue_history}"
        else:
            prompt_template = (
                "{system_prompt}\n"
                "\n"
                "## Conversation History\n"
                "{dialogue_history}"
            )

        return prompt_template.format(
            system_prompt=sys_prompt,
            dialogue_history=dialogue_history,
        )

class QwenTextEmbeddingWrapper(QwenWrapperBase):
    """The model wrapper for DashScope Text Embedding API.

    Response:
        - Refer to
        https://help.aliyun.com/zh/dashscope/developer-reference/text-embedding-api-details?spm=a2c4g.11186623.0.i3

        ```json
        {
            "status_code": 200, // 200 indicate success otherwise failed.
            "request_id": "fd564688-43f7-9595-b986", // The request id.
            "code": "", // If failed, the error code.
            "message": "", // If failed, the error message.
            "output": {
                "embeddings": [ // embeddings
                    {
                        "embedding": [ // one embedding output
                            -3.8450357913970947, ...,
                        ],
                        "text_index": 0 // the input index.
                    }
                ]
            },
            "usage": {
                "total_tokens": 3 // the request tokens.
            }
        }
        ```
    """

    model_type: str = "qwen_text_embedding"

    def __call__(
        self,
        texts: Union[list[str], str],
        dimension: Literal[512, 768, 1024, 1536] = 768,
        **kwargs: Any,
    ):
        """Embed the messages with DashScope Text Embedding API.

        Args:
            texts (`list[str]` or `str`):
                The messages used to embed.
            **kwargs (`Any`):
                The keyword arguments to DashScope Text Embedding API,
                e.g. `text_type`. Please refer to
                https://help.aliyun.com/zh/dashscope/developer-reference/api-details-15
                for more detailed arguments.

        Returns:
            `ModelResponse`:
                A list of embeddings in embedding field and the raw
                response in raw field.

        Note:
            `parse_func`, `fault_handler` and `max_retries` are reserved
            for `_response_parse_decorator` to parse and check the response
            generated by model wrapper. Their usages are listed as follows:
                - `parse_func` is a callable function used to parse and
                check the response generated by the model, which takes the
                response as input.
                - `max_retries` is the maximum number of retries when the
                `parse_func` raise an exception.
                - `fault_handler` is a callable function which is called
                when the response generated by the model is invalid after
                `max_retries` retries.
        """
        # client = openai.OpenAI(api_key=self.api_key, base_url=self.api_url)
        # step1: prepare keyword arguments
        kwargs = {**self.generate_args, **kwargs}

        # step2: forward to generate response
        response = dashscope.TextEmbedding.call(
            input=texts,
            model=self.model_name,
            api_key=self.api_key,
            dimension=dimension,
            **kwargs,
        )

        if response.status_code != HTTPStatus.OK:
            error_msg = (
                f" Request id: {response.request_id},"
                f" Status code: {response.status_code},"
                f" error code: {response.code},"
                f" error message: {response.message}."
            )
            raise RuntimeError(error_msg)

        # step5: return response
        return response

    def embed_query(self, text: str) -> List[float]:
        response = self([text])
        output = response["output"]
        embeddings = output["embeddings"]
        return embeddings[0]["embedding"]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self(texts)
        output = response["output"]
        embeddings = output["embeddings"]
        return [emb["embedding"] for emb in embeddings]
    