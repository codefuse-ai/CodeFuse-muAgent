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



OPENAI_MAX_LENGTH = {
    "update": 20231212,
    # gpt-4
    "gpt-4o-mini": 8192,
    "gpt-4-1106-preview": 128000,
    "gpt-4-vision-preview": 128000,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-32k-0613": 32768,
    "gpt-4-0314": 8192,  # legacy
    "gpt-4-32k-0314": 32768,  # legacy
    # gpt-3.5
    "gpt-3.5-turbo-1106": 16385,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16385,
    "gpt-3.5-turbo-instruct": 4096,
    "gpt-3.5-turbo-0613": 4096,  # legacy
    "gpt-3.5-turbo-16k-0613": 16385,  # deprecated on June 13th 2024
    "gpt-3.5-turbo-0301": 4096,  # deprecated on June 13th 2024
    "text-davinci-003": 4096,  # deprecated on Jan 4th 2024
    "text-davinci-002": 4096,  # deprecated on Jan 4th 2024
    "code-davinci-002": 4096,  # deprecated on Jan 4th 2024
    # gpt-3 legacy
    "text-curie-001": 2049,
    "text-babbage-001": 2049,
    "text-ada-001": 2049,
    "davinci": 2049,
    "curie": 2049,
    "babbage": 2049,
    "ada": 2049,
    # 
    "text-embedding-3-small": 8191,
    "text-embedding-3-large": 8191,
    "text-embedding-ada-002": 8191,
}


def get_openai_max_length(model_name: str) -> int:
    """Get the max length of the OpenAi models."""
    try:
        return OPENAI_MAX_LENGTH[model_name]
    except KeyError as exc:
        raise KeyError(
            f"Model [{model_name}] not found in OPENAI_MAX_LENGTH. "
            f"The last updated date is {OPENAI_MAX_LENGTH['update']}",
        ) from exc
    


def _to_openai_image_url(url: str) -> str:
    """Convert an image url to openai format. If the given url is a local
    file, it will be converted to base64 format. Otherwise, it will be
    returned directly.

    Args:
        url (`str`):
            The local or public url of the image.
    """
    # See https://platform.openai.com/docs/guides/vision for details of
    # support image extensions.
    support_image_extensions = (
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
    )

    parsed_url = urlparse(url)

    lower_url = url.lower()

    # Web url
    if parsed_url.scheme != "":
        if any(lower_url.endswith(_) for _ in support_image_extensions):
            return url

    # Check if it is a local file
    elif os.path.exists(url) and os.path.isfile(url):
        if any(lower_url.endswith(_) for _ in support_image_extensions):
            with open(url, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode(
                    "utf-8",
                )
            extension = parsed_url.path.lower().split(".")[-1]
            mime_type = f"image/{extension}"
            return f"data:{mime_type};base64,{base64_image}"

    raise TypeError(f"{url} should be end with {support_image_extensions}.")



class OpenAIWrapperBase(ModelWrapperBase, ABC):
    """The model wrapper for OpenAI API.

    Response:
        - From https://platform.openai.com/docs/api-reference/chat/create

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
        api_url: str = "https://api.openai.com/v1",
        organization: str = None,
        client_args: dict = None,
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

        try:
            from zdatafront import ZDataFrontClient
            from zdatafront.openai import SyncProxyHttpClient
            VISIT_DOMAIN = os.environ.get("visit_domain")
            VISIT_BIZ = os.environ.get("visit_biz")
            VISIT_BIZ_LINE = os.environ.get("visit_biz_line")
            aes_secret_key = os.environ.get("aes_secret_key")
            zdatafront_client = ZDataFrontClient(
                visit_domain=VISIT_DOMAIN, 
                visit_biz=VISIT_BIZ, 
                visit_biz_line=VISIT_BIZ_LINE, 
                aes_secret_key=aes_secret_key
            )
            http_client = SyncProxyHttpClient(zdatafront_client=zdatafront_client, prefer_async=True)
        except Exception as e:
            logger.warning("There is no zdatafront, act as openai")
            http_client = None

        if http_client:
            self.client = openai.OpenAI(
                api_key=api_key,
                http_client=http_client,
                organization=organization,
                **(client_args or {}),
                timeout=120,
            )
        else:
            self.client = openai.OpenAI(
                api_key=api_key,
                organization=organization,
                **(client_args or {}),
            )
        # Set the max length of OpenAI model
        try:
            self.max_length = get_openai_max_length(self.model_name)
        except Exception as e:
            logger.warning(
                f"fail to get max_length for {self.model_name}: " f"{e}",
            )
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


class OpenAIChatWrapper(OpenAIWrapperBase):
    """The model wrapper for OpenAI's chat API."""

    model_type: str = "openai_chat"

    substrings_in_vision_models_names = ["gpt-4-turbo", "vision", "gpt-4o"]
    """The substrings in the model names of vision models."""

    def __init__(
        self,
        config_name: str,
        model_name: str = None,
        api_key: str = None,
        api_url: str = "https://api.openai.com/v1",
        organization: str = None,
        client_args: dict = None,
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
        stream: bool = None,
        stop: Optional[str] = '',
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
                "OpenAI `messages` field expected type `list`, "
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
                "stop": stop,
            },
        )

        if stream:
            kwargs["stream_options"] = {"include_usage": True}

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

    @staticmethod
    def _format_Message_with_url(
        message: Message,
        model_name: str,
    ) -> Dict:
        """Format a message with image urls into openai chat format.
        This format method is used for gpt-4o, gpt-4-turbo, gpt-4-vision and
        other vision models.
        """
        # Check if the model is a vision model
        if not any(
            _ in model_name
            for _ in OpenAIChatWrapper.substrings_in_vision_models_names
        ):
            logger.warning(
                f"The model {model_name} is not a vision model. "
                f"Skip the url in the message.",
            )
            return {
                "role": message.role_type,
                "name": message.role_name,
                "content": message.content,
            }

        # Put all urls into a list
        urls = message.image_urls if isinstance(message.image_urls, list) else [message.image_urls]

        # Check if the url refers to an image
        checked_urls = []
        for url in urls:
            try:
                checked_urls.append(_to_openai_image_url(url))
            except TypeError:
                logger.warning(
                    f"The url {url} is not a valid image url for "
                    f"OpenAI Chat API, skipped.",
                )

        if len(checked_urls) == 0:
            # If no valid image url is provided, return the normal message dict
            return {
                "role": message.role_type,
                "name": message.role_name,
                "content": message.content,
            }
        else:
            # otherwise, use the vision format message
            returned_Message = {
                "role": message.role_type,
                "name": message.role_name,
                "content": [
                    {
                        "type": "text",
                        "text": message.content,
                    },
                ],
            }

            image_dicts = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": _,
                    },
                }
                for _ in checked_urls
            ]

            returned_Message["content"].extend(image_dicts)

            return returned_Message

    @staticmethod
    def static_format(
        *args: Union[Message, Sequence[Message]],
        model_name: str,
    ) -> List[dict]:
        """A static version of the format method, which can be used without
        initializing the OpenAIChatWrapper object.

        Args:
            args (`Union[Message, Sequence[Message]]`):
                The input arguments to be formatted, where each argument
                should be a `Message` object, or a list of `Message` objects.
                In distribution, placeholder is also allowed.
            model_name (`str`):
                The name of the model to use in OpenAI API.

        Returns:
            `List[dict]`:
                The formatted messages in the format that OpenAI Chat API
                required.
        """
        messages = []
        for arg in args:
            if arg is None:
                continue
            if isinstance(arg, Message):
                if arg.image_urls is not None and arg.image_urls:
                    # Format the message according to the model type
                    # (vision/non-vision)
                    formatted_Message = OpenAIChatWrapper._format_Message_with_url(
                        arg,
                        model_name,
                    )
                    messages.append(formatted_Message)
                else:
                    messages.append(
                        {
                            "role": arg.role_type,
                            "name": arg.role_name,
                            "content": arg.content,
                        },
                    )

            elif isinstance(arg, list):
                messages.extend(
                    OpenAIChatWrapper.static_format(
                        *arg,
                        model_name=model_name,
                    ),
                )
            else:
                raise TypeError(
                    f"The input should be a Message object or a list "
                    f"of Message objects, got {type(arg)}.",
                )

        return messages

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

        # Format messages according to the model name
        if self.model_name.startswith("gpt-"):
            return OpenAIChatWrapper.static_format(
                *args,
                model_name=self.model_name,
            )
        else:
            # The OpenAI library maybe re-used to support other models
            return ModelWrapperBase.format_for_common_chat_models(*args)


class OpenAIEmbeddingWrapper(OpenAIWrapperBase):
    """The model wrapper for OpenAI embedding API.

    Response:
        - Refer to
        https://platform.openai.com/docs/api-reference/embeddings/create

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

    model_type: str = "openai_embedding"

    def __call__(
        self,
        texts: Union[list[str], str],
        dimension=768,
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
        # step1: prepare keyword arguments
        kwargs = {**self.generate_args, **kwargs}

        # step2: forward to generate response
        response = self.client.embeddings.create(
            input=texts,
            model=self.model_name,
            **kwargs,
        )
        # step5: return response
        response_json = response.model_dump()
        return response_json

    def embed_query(self, text: str) -> List[float]:
        response = self([text])
        output = response["data"]
        return output[0]["embedding"]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self(texts)
        output = response["data"]
        return [emb["embedding"] for emb in output]
    