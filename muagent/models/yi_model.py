# -*- coding: utf-8 -*-
"""Model wrapper for Yi models
The implementation of this _ModelWrapperMeta are borrowed from
https://github.com/modelscope/agentscope/blob/main/src/agentscope/models/yi_model.py
"""


import json
from typing import (
    List,
    Union,
    Sequence,
    Optional,
    Generator,
    Literal
)

import openai
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from .base_model import ModelWrapperBase
from ..schemas import Message


class YiChatWrapper(ModelWrapperBase):
    """The model wrapper for Yi Chat API.

    Response:
        - From https://platform.lingyiwanwu.com/docs

        ```json
        {
            "id": "cmpl-ea89ae83",
            "object": "chat.completion",
            "created": 5785971,
            "model": "yi-large-rag",
            "usage": {
                "completion_tokens": 113,
                "prompt_tokens": 896,
                "total_tokens": 1009
            },
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Today in Los Angeles, the weather ...",
                    },
                    "finish_reason": "stop"
                }
            ]
        }
        ```
    """

    model_type: str =  "yi_chat"

    def __init__(
        self,
        config_name: str,
        model_name: str,
        api_key: str,
        api_url: str="https://api.lingyiwanwu.com/v1",
        max_tokens: Optional[int] = None,
        top_p: float = 0.9,
        temperature: float = 0.3,
        stream: bool = False,
        **kwargs,
    ) -> None:
        """Initialize the Yi chat model wrapper.

        Args:
            config_name (`str`):
                The name of the configuration to use.
            model_name (`str`):
                The name of the model to use, e.g. yi-large, yi-medium, etc.
            api_key (`str`):
                The API key for the Yi API.
            max_tokens (`Optional[int]`, defaults to `None`):
                The maximum number of tokens to generate, defaults to `None`.
            top_p (`float`, defaults to `0.9`):
                The randomness parameters in the range [0, 1].
            temperature (`float`, defaults to `0.3`):
                The temperature parameter in the range [0, 2].
            stream (`bool`, defaults to `False`):
                Whether to stream the response or not.
        """

        init_params = locals()
        init_params.pop("self")
        init_params["model_type"] = self.model_type
        super().__init__(**init_params)

        if top_p > 1 or top_p < 0:
            raise ValueError(
                f"The `top_p` parameter must be in the range [0, 1], but got "
                f"{top_p} instead.",
            )

        if temperature < 0 or temperature > 2:
            raise ValueError(
                f"The `temperature` parameter must be in the range [0, 2], "
                f"but got {temperature} instead.",
            )
        self.api_url = api_url or "https://api.lingyiwanwu.com/v1"
        self.client = openai.OpenAI(api_key=self.api_key,base_url=self.api_url)
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.temperature = temperature
        self.stream = stream

    def __call__(
        self,
        prompt: str = None,
        messages: Sequence[dict] = [],
        tools: Sequence[object] = [],
        *,
        tool_choice: Literal['auto', 'required'] = 'auto',
        parallel_tool_calls: Optional[bool] = None,
        stream: Optional[bool] = None,
        stop: Optional[str] = '',
        format_type: Literal['str', 'raw', 'dict'] = 'raw',
        **kwargs
    ) -> Generator[Union[ChatCompletionChunk, ChatCompletion, str], None, None]:
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
        model_name = "yi-large-fc" if tools else self.model_name
        # model_name = self.model_name
        # 
        kwargs.update(
            {
                "model": model_name,
                "messages": messages,
                "stream": stream,
                "tools": tools,
                "tool_choice": tool_choice,
                "parallel_tool_calls": parallel_tool_calls,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": self.top_p,
                "stop": [stop]
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

    def function_call(
        self,
        messages: Optional[Sequence[dict]] = None,
        tools: Sequence[object] = [],
        *,
        prompt: Optional[str] = None,
        tool_choice: Literal['auto', 'required'] = 'auto',
        parallel_tool_calls: Optional[bool] = None,
        stream: Optional[bool] = False,
    ) -> ChatCompletion:
        """Call a function to process messages with optional tools.

        Args:
            messages (Optional[Sequence[dict]], optional): A sequence of messages for context.
            tools (Sequence[object], optional): Tools available for use.
            prompt (Optional[str], optional): An optional prompt.
            tool_choice (Optional[Literal['auto', 'required']], optional): How to select tools.
            parallel_tool_calls (Optional[bool], optional): If true, allows parallel tool calls.
            stream (Optional[bool], optional): If true, streams the output instead of returning it all at once.

        Returns:
            Union[ChatCompletion, Mapping]: The result of the function call processed by the model.
        """
        kwargs = locals()
        kwargs.pop("self")
        kwargs.pop("__class__")
        return super().function_call(**kwargs)

    def function_call_stream(
        self,
        messages: Optional[Sequence[dict]] = None,
        tools: Sequence[object] = [],
        *,
        prompt: Optional[str] = None,
        tool_choice: Literal['auto', 'required'] = 'auto',
        parallel_tool_calls: Optional[bool] = None,
        stream: Optional[bool] = True,
    ) -> Generator[ChatCompletionChunk, None, None]:
        """Stream function call outputs.

        Args:
            messages (Optional[Sequence[dict]], optional): A sequence of messages for context.
            tools (Sequence[object], optional): Tools available for use.
            prompt (Optional[str], optional): An optional prompt.
            tool_choice (Optional[Literal['auto', 'required']], optional): How to select tools.
            parallel_tool_calls (Optional[bool], optional): If true, allows parallel tool calls.
            stream (Optional[bool], optional): If true, streams the output instead of returning it all at once.

        Yields:
            Generator[Union[ChatCompletionChunk, Mapping], None, None]: A generator yielding parts of the function output.
        """
        kwargs = locals()
        kwargs.pop("self")
        kwargs.pop("__class__")
        for i in super().function_call_stream(**kwargs): yield i

    def format(
        self,
        *args: Union[Message, Sequence[Message]],
    ) -> List[dict]:
        """Format the messages into the required format of Yi Chat API.

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

        Args:
            args (`Union[Message, Sequence[Message]]`):
                The input arguments to be formatted, where each argument
                should be a `Message` object, or a list of `Message` objects.
                In distribution, placeholder is also allowed.

        Returns:
            `List[dict]`:
                The formatted messages.
        """

        # TODO: Support Vision model
        if self.model_name == "yi-vision":
            raise NotImplementedError(
                "Yi Vision model is not supported in the current version, "
                "please format the messages manually.",
            )

        return ModelWrapperBase.format_for_common_chat_models(*args)