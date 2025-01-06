# -*- coding: utf-8 -*-
"""Model wrapper for Ollama models."""
import os
from abc import ABC
from typing import (
    Sequence, 
    Any, 
    Optional, 
    List, 
    Union, 
    Generator,
    Literal,
    Mapping
)

from .base_model import ModelWrapperBase
from ..schemas import Message


class OllamaWrapperBase(ModelWrapperBase, ABC):
    """The base class for Ollama model wrappers.

    To use Ollama API, please
    1. First install ollama server from https://ollama.com/download and
    start the server
    2. Pull the model by `ollama pull {model_name}` in terminal
    After that, you can use the ollama API.
    """

    model_type: str
    """The type of the model wrapper, which is to identify the model wrapper
    class in model configuration."""

    model_name: str
    """The model name used in ollama API."""

    options: dict
    """A dict contains the options for ollama generation API,
    e.g. {"temperature": 0, "seed": 123}"""

    keep_alive: str
    """Controls how long the model will stay loaded into memory following
    the request."""

    def __init__(
        self,
        config_name: str,
        model_name: str,
        api_key: str = '',
        options: dict = None,
        keep_alive: str = "5m",
        api_url: Optional[Union[str, None]] = "http://127.0.0.1:11434",
        **kwargs: Any,
    ) -> None:
        """Initialize the model wrapper for Ollama API.

        Args:
            model_name (`str`):
                The model name used in ollama API.
            options (`dict`, default `None`):
                The extra keyword arguments used in Ollama api generation,
                e.g. `{"temperature": 0., "seed": 123}`.
            keep_alive (`str`, default `5m`):
                Controls how long the model will stay loaded into memory
                following the request.
            host (`str`, default `None`):
                The host port of the ollama server.
                Defaults to `None`, which is 127.0.0.1:11434.
        """

        super().__init__(config_name=config_name, model_name=model_name)

        self.options = options
        self.keep_alive = keep_alive
        self.api_url = api_url or "http://127.0.0.1:11434"

        try:
            import ollama
        except ImportError as e:
            raise ImportError(
                "The package ollama is not found. Please install it by "
                'running command `pip install "ollama>=0.1.7"`',
            ) from e

        self.client = ollama.Client(host=self.api_url)


class OllamaChatWrapper(OllamaWrapperBase):
    """The model wrapper for Ollama chat API.

    Response:
        - Refer to
        https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion

        ```json
        {
            "model": "registry.ollama.ai/library/llama3:latest",
            "created_at": "2023-12-12T14:13:43.416799Z",
            "message": {
                "role": "assistant",
                "content": "Hello! How are you today?"
            },
            "done": true,
            "total_duration": 5191566416,
            "load_duration": 2154458,
            "prompt_eval_count": 26,
            "prompt_eval_duration": 383809000,
            "eval_count": 298,
            "eval_duration": 4799921000
        }
        ```
    """

    model_type: str = 'ollama_chat'

    def __init__(
        self,
        config_name: str,
        model_name: str,
        stream: bool = False,
        options: dict = None,
        keep_alive: str = "5m",
        api_url: Optional[Union[str, None]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the model wrapper for Ollama API.

        Args:
            model_name (`str`):
                The model name used in ollama API.
            stream (`bool`, default `False`):
                Whether to enable stream mode.
            options (`dict`, default `None`):
                The extra keyword arguments used in Ollama api generation,
                e.g. `{"temperature": 0., "seed": 123}`.
            keep_alive (`str`, default `5m`):
                Controls how long the model will stay loaded into memory
                following the request.
            api_url (`str`, default `None`):
                The host port of the ollama server.
                Defaults to `None`, which is 127.0.0.1:11434.
        """

        super().__init__(
            config_name=config_name,
            model_name=model_name,
            options=options,
            keep_alive=keep_alive,
            api_url=api_url,
            **kwargs,
        )

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
        stream: Optional[bool] = None,
        options: Optional[dict] = None,
        keep_alive: Optional[str] = None,
        format_type: Literal['str', 'raw', 'dict'] = 'raw',
        **kwargs: Any,
    ):
        """Generate response from the given messages.

        Args:
            messages (`Sequence[dict]`):
                A list of messages, each message is a dict contains the `role`
                and `content` of the message.
            stream (`bool`, default `None`):
                Whether to enable stream mode, which will override the `stream`
                input in the constructor.
            options (`dict`, default `None`):
                The extra arguments used in ollama chat API, which takes
                effect only on this call, and will be merged with the
                `options` input in the constructor,
                e.g. `{"temperature": 0., "seed": 123}`.
            keep_alive (`str`, default `None`):
                How long the model will stay loaded into memory following
                the request, which takes effect only on this call, and will
                override the `keep_alive` input in the constructor.

        Returns:
            `ModelResponse`:
                The response text in `text` field, and the raw response in
                `raw` field.
        """

        messages = [{"role": "user", "content": prompt}] if prompt else messages
        # step1: prepare parameters accordingly
        if options is None:
            options = self.options or {"stop": [stop] if stop else []}
        else:
            options = {**self.options, **options}

        keep_alive = keep_alive or self.keep_alive

        # step2: forward to generate response
        stream = self.stream if stream is None else stream

        kwargs.update(
            {
                "model": self.model_name,
                "messages": messages,
                "tools": tools,
                "stream": stream,
                "options": options,
                "keep_alive": keep_alive,
            },
        )

        response = self.client.chat(**kwargs)
        if format_type == "str":
            content = ""
            if stream:
                for chunk in response:
                    content += chunk["message"]["content"] or ''
                    yield content
            else:
                yield response["message"]["content"]
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
        """Format the messages for ollama Chat API.

        All messages will be formatted into a single system message with
        system prompt and conversation history.

        Note:
        1. This strategy maybe not suitable for all scenarios,
        and developers are encouraged to implement their own prompt
        engineering strategies.
        2. For ollama chat api, the content field shouldn't be empty string.

        Example:

        .. code-block:: python

            prompt = model.format(
                Message("system", "You're a helpful assistant", role="system"),
                Message("Bob", "Hi, how can I help you?", role="assistant"),
                Message("user", "What's the date today?", role="user")
            )

        The prompt will be as follows:

        .. code-block:: python

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

        # Parse all information into a list of messages
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
                    f"The input should be a Message object or a list "
                    f"of Message objects, got {type(_)}.",
                )

        # record dialog history as a list of strings
        system_prompt = None
        history_content_template = []
        dialogue = []
        # TODO: here we default the url links to images
        images = []
        for i, unit in enumerate(input_msgs):
            if i == 0 and unit.role_type == "system":
                # system prompt
                system_prompt = unit.content
            else:
                # Merge all messages into a conversation history prompt
                dialogue.append(
                    f"{unit.role_name}: {unit.content}",
                )

            if unit.image_urls is not None:
                images.extend(unit.image_urls)

        if len(dialogue) != 0:
            dialogue_history = "\n".join(dialogue)

            history_content_template.extend(
                ["## Conversation History", dialogue_history],
            )

        history_content = "\n".join(history_content_template)

        # The conversation history message
        history_message = {
            "role": "user",
            "content": history_content,
        }

        if len(images) != 0:
            history_message["images"] = images

        if system_prompt is None:
            return [history_message]

        return [
            {"role": "system", "content": system_prompt},
            history_message,
        ]

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


class OllamaEmbeddingWrapper(OllamaWrapperBase):
    """The model wrapper for Ollama embedding API.

    Response:
        - Refer to
        https://github.com/ollama/ollama/blob/main/docs/api.md#generate-embeddings

        ```json
        {
            "model": "all-minilm",
            "embeddings": [[
                0.010071029, -0.0017594862, 0.05007221, 0.04692972,
                0.008599704, 0.105441414, -0.025878139, 0.12958129,
            ]]
        }
        ```
    """

    model_type: str = "ollama_embedding"

    def __call__(
        self,
        texts: str,
        options: Optional[dict] = None,
        keep_alive: Optional[str] = None,
        **kwargs: Any,
    ) -> Mapping[str, Sequence[float]]:
        """Generate embedding from the given prompt.

        Args:
            prompt (`str`):
                The prompt to generate response.
            options (`dict`, default `None`):
                The extra arguments used in ollama embedding API, which takes
                effect only on this call, and will be merged with the
                `options` input in the constructor,
                e.g. `{"temperature": 0., "seed": 123}`.
            keep_alive (`str`, default `None`):
                How long the model will stay loaded into memory following
                the request, which takes effect only on this call, and will
                override the `keep_alive` input in the constructor.

        Returns:
            `ModelResponse`:
                The response embedding in `embedding` field, and the raw
                response in `raw` field.
        """
        # step1: prepare parameters accordingly
        if options is None:
            options = self.options
        else:
            options = {**self.options, **options}

        keep_alive = keep_alive or self.keep_alive

        # step2: forward to generate response
        response = self.client.embed(
            model=self.model_name,
            input=texts,
            options=options,
            keep_alive=keep_alive,
            **kwargs,
        )
        # step5: return response
        return response

    def embed_query(self, text: str) -> List[float]:
        response = self([text])
        embeddings = response["embeddings"]
        return embeddings[0]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self(texts)
        embeddings = response["embeddings"]
        return embeddings
    
    def format(
        self,
        *args: Union[Message, Sequence[Message]],
    ) -> Union[List[dict], str]:
        raise RuntimeError(
            f"Model Wrapper [{type(self).__name__}] doesn't "
            f"need to format the input. Please try to use the "
            f"model wrapper directly.",
        )