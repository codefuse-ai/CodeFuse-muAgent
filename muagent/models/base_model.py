"""
The implementation of this _ModelWrapperMeta are borrowed from
https://github.com/modelscope/agentscope/blob/main/src/agentscope/models/model.py
"""


from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import (
    Any, 
    Optional, 
    Type, 
    Union, 
    Sequence, 
    List, 
    Generator, 
    Literal,
    Mapping
)
from loguru import logger
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from muagent.schemas import Message, Memory
from muagent.schemas.models import (
    ModelConfig, 
)
from muagent.utils.common_utils import _convert_to_str


class _ModelWrapperMeta(ABCMeta):
    """A meta call to replace the model wrapper's __call__ function with
    wrapper about error handling."""

    def __new__(mcs, name: Any, bases: Any, attrs: Any) -> Any:
        if "__call__" in attrs:
            attrs["__call__"] = attrs["__call__"]
        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name: Any, bases: Any, attrs: Any) -> None:
        if not hasattr(cls, "_registry"):
            cls._registry = {}
            cls._type_registry = {}
            cls._deprecated_type_registry = {}
        else:
            cls._registry[name] = cls
            if hasattr(cls, "model_type"):
                cls._type_registry[cls.model_type] = cls
                if hasattr(cls, "deprecated_model_type"):
                    cls._deprecated_type_registry[
                        cls.deprecated_model_type
                    ] = cls
        super().__init__(name, bases, attrs)


class ModelWrapperBase(metaclass=_ModelWrapperMeta):
    """The base class for model wrapper."""

    model_type: str
    """The type of the model wrapper, which is to identify the model wrapper
    class in model configuration."""

    config_name: str
    """The name of the model configuration."""

    model_name: str
    """The name of the model, which is used in model api calling."""
    
    api_key: Optional[str] = None
    """The api key of the model, which is used in model api calling."""
    
    api_url: Optional[str] = None
    """The api url of the model, which is used in model api calling."""

    def __init__(
        self,  # pylint: disable=W0613
        config_name: str,
        model_name: str,
        model_type: str = "codefuse",
        api_key: Optional[str] = "model_base_xxx",
        api_url: Optional[str]="https://codefuse.ai",
        **kwargs: Any,
    ) -> None:
        """Base class for model wrapper.

        All model wrappers should inherit this class and implement the
        `__call__` function.

        Args:
            config_name (`str`):
                The id of the model, which is used to extract configuration
                from the config file.
            model_name (`str`):
                The name of the model.
            api_key (`str`):
                The api key of the model.
            api_url (`str`):
                The api url of the model.
            model_type (`str`):
                The type of the model wrapper.
        """
        self.config_name = config_name
        self.model_name = model_name
        self.api_key = api_key
        self.api_url = api_url
        self.model_type = model_type
        # logger.info(f"Initialize model by configuration [{config_name}]")

    @classmethod
    def from_config(self, model_config: ModelConfig) -> 'ModelWrapperBase':
        model_config_dict = model_config.dict()
        model_type = model_config_dict.pop("model_type")
        return self.get_wrapper(model_type)(**model_config_dict)
    
    @classmethod
    def get_wrapper(cls, model_type: str) -> Type[ModelWrapperBase]:
        """Get the specific model wrapper"""
        if model_type in cls._type_registry:
            return cls._type_registry[model_type]  # type: ignore[return-value]
        elif model_type in cls._registry:
            return cls._registry[model_type]  # type: ignore[return-value]
        elif model_type in cls._deprecated_type_registry:
            deprecated_cls = cls._deprecated_type_registry[model_type]
            logger.warning(
                f"Model type [{model_type}] will be deprecated in future "
                f"releases, please use [{deprecated_cls.model_type}] instead.",
            )
            return deprecated_cls  # type: ignore[return-value]
        else:
            raise KeyError(
                f"Unsupported model_type [{model_type}],"
                "use PostApiModelWrapper instead.",
            )

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
        format_type: Literal["str", "dict", "raw"] = "str",
        **kwargs: Any,
    ) -> Generator[Union[ChatCompletion, ChatCompletionChunk, str, Mapping], None, None]:
        """Process input with the model.

        Args:
            prompt (str, optional): The prompt string to provide to the model.
            messages (Sequence[dict], optional): A sequence of messages for conversation context.
            tools (Sequence[object], optional): Tools that can be utilized in the processing.
            tool_choice (Optional[Literal['auto', 'required']], optional): Determining how to select tools.
            parallel_tool_calls (Optional[bool], optional): If true, allows parallel calls to tools.
            stream (bool, optional): If true, the output is streamed rather than returned all at once.
            stop (Optional[str], optional): Token to signify stopping generation.
            format_type (Literal["str", "dict", "raw"], optional): The format of the output.
            **kwargs: Additional keyword arguments for extensibility.

        Returns:
            Generator[Union[ChatCompletion, ChatCompletionChunk, str, Mapping], None, None]: 
            A generator yielding completion responses from the model.
        """
        raise NotImplementedError(
            f"Model Wrapper [{type(self).__name__}]"
            f" is missing the required `__call__`"
            f" method.",
        )

    def predict(
        self,
        prompt: str,
        stop: Optional[str] = '',
    ) -> Union[ChatCompletion, str]:
        """Generate a prediction based on the provided prompt.

        Args:
            prompt (str): The input prompt for prediction.
            stop (Optional[str], optional): Token to signify stopping generation.

        Returns:
            Union[ChatCompletion, str]: The model's prediction in the specified format.
        """
        return self.generate(prompt, stop, "str")
    
    def generate(
        self,
        prompt: str,
        stop: Optional[str] = '',
        format_type: Literal["str", "raw"] = "raw",
    ) -> Union[ChatCompletion, str]:
        """Generate a response by calling the model.

        Args:
            prompt (str): The input prompt.
            stop (Optional[str], optional): Token to signify stopping generation.
            format_type (Literal["str", "raw"], optional): The format of the output.

        Returns:
            Union[ChatCompletion, str]: The generated response from the model.
        """
        for i in self.__call__(prompt, stop=stop, stream=False, format_type=format_type): 
            pass
        return i
    
    def generate_stream(self,
        prompt: str,
        stop: Optional[str] = '',
        format_type: Literal["str", "raw"] = "raw",
    ) -> Generator[Union[ChatCompletionChunk, str], None, None]:
        """Stream the generated response from the model.

        Args:
            prompt (str): The input prompt.
            stop (Optional[str], optional): Token to signify stopping generation.
            format_type (Literal["str", "raw"], optional): The format of the output.

        Yields:
            Generator[Union[ChatCompletionChunk, str], None, None]: A generator yielding parts of the response.
        """
        for i in self.__call__(prompt, stop=stop, stream=True, format_type=format_type): 
            yield i

    def chat(self,
        messages: Optional[Sequence[dict]],
        stop: Optional[str] = '',
        format_type: Literal["str", "raw"] = "raw",
    ) -> Union[ChatCompletion, str]:
        """Process a chat message input and return the model's response.

        Args:
            messages (Optional[Sequence[dict]]): A sequence of messages for conversation context.
            stop (Optional[str], optional): Token to signify stopping generation.
            format_type (Literal["str", "raw"], optional): The format of the output.

        Returns:
            Union[ChatCompletion, str]: The model's chat response in the specified format.
        """
        for i in self.__call__(None, messages, stop=stop, stream=False, format_type=format_type): 
            return i

    def chat_stream(self,
        messages: Optional[Sequence[dict]],
        stop: Optional[str] = '',
        format_type: Literal["str", "raw"] = "raw",
    ) -> Generator[Union[ChatCompletionChunk, str], None, None]:
        """Stream chat responses from the model.

        Args:
            messages (Optional[Sequence[dict]]): A sequence of messages for conversation context.
            stop (Optional[str], optional): Token to signify stopping generation.
            format_type (Literal["str", "raw"], optional): The format of the output.

        Yields:
            Generator[Union[ChatCompletionChunk, str], None, None]: A generator yielding parts of the chat response.
        """
        for i in self.__call__(None, messages, stop=stop, stream=True, format_type=format_type): 
            yield i

    def function_call(
        self,
        messages: Optional[Sequence[dict]] = None,
        tools: Sequence[object] = [],
        *,
        prompt: Optional[str] = None,
        tool_choice: Optional[Literal['auto', 'required']] = None,
        parallel_tool_calls: Optional[bool] = None,
        stream: Optional[bool] = False,
        stop: Optional[str] = '',
        format_type: Literal["raw"] = "raw",
    ) -> Union[ChatCompletion, Mapping]:
        """Call a function to process messages with optional tools.

        Args:
            messages (Optional[Sequence[dict]], optional): A sequence of messages for context.
            tools (Sequence[object], optional): Tools available for use.
            prompt (Optional[str], optional): An optional prompt.
            tool_choice (Optional[Literal['auto', 'required']], optional): How to select tools.
            parallel_tool_calls (Optional[bool], optional): If true, allows parallel tool calls.
            stream (Optional[bool], optional): If true, streams the output instead of returning it all at once.
            stop (Optional[str], optional): Token to signify stopping generation.
            format_type (Literal["raw"], optional): Specifies to return the output in raw format.

        Returns:
            Union[ChatCompletion, Mapping]: The result of the function call processed by the model.
        """
        kwargs = locals()
        kwargs.pop("self")
        for i in self.__call__(**kwargs): 
            pass
        return i

    def function_call_stream(
        self,
        messages: Optional[Sequence[dict]] = None,
        tools: Sequence[object] = [],
        *,
        prompt: Optional[str] = None,
        tool_choice: Optional[Literal['auto', 'required']] = 'auto',
        parallel_tool_calls: Optional[bool] = None,
        stream: Optional[bool] = True,
        stop: Optional[str] = '',
        format_type: Literal["raw"] = "raw",
    ) -> Generator[Union[ChatCompletionChunk, Mapping], None, None]:
        """Stream function call outputs.

        Args:
            messages (Optional[Sequence[dict]], optional): A sequence of messages for context.
            tools (Sequence[object], optional): Tools available for use.
            prompt (Optional[str], optional): An optional prompt.
            tool_choice (Optional[Literal['auto', 'required']], optional): How to select tools.
            parallel_tool_calls (Optional[bool], optional): If true, allows parallel tool calls.
            stream (Optional[bool], optional): If true, streams the output.
            stop (Optional[str], optional): Token to signify stopping generation.
            format_type (Literal["raw"], optional): Specifies to return output in raw format.

        Yields:
            Generator[Union[ChatCompletionChunk, Mapping], None, None]: A generator yielding parts of the function output.
        """
        kwargs = locals()
        kwargs.pop("self")
        for i in self.__call__(**kwargs): 
            yield i

    def batch(self, *args: Any, **kwargs: Any) -> List[ChatCompletion]:
        """Process batch inputs with the model.

        This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError(
            f"Model Wrapper [{type(self).__name__}]"
            f" is missing the required `batch`"
            f" method.",
        )

    def embed_query(self, text: str) -> List[float]:
        """Embed a query into a vector representation.

        This method should be implemented by subclasses.

        Args:
            text (str): The text to embed.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError(
            f"Model Wrapper [{type(self).__name__}]"
            f" is missing the required `embed_query`"
            f" method.",
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents into vector representations.

        This method should be implemented by subclasses.

        Args:
            texts (List[str]): The list of texts to embed.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError(
            f"Model Wrapper [{type(self).__name__}]"
            f" is missing the required `embed_documents`"
            f" method.",
        )
    
    def format(
        self,
        *args: Union[Message, Sequence[Message]],
    ) -> Union[List[dict], str]:
        """Format the input messages into the format that the model
        API required."""
        raise NotImplementedError(
            f"Model Wrapper [{type(self).__name__}]"
            f" is missing the required `format` method",
        )

    @staticmethod
    def format_for_common_chat_models(
        *args: Union[Message, Sequence[Message]],
    ) -> List[dict]:
        """A common format strategy for chat models, which will format the
        input messages into a system message (if provided) and a user message.

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
            args (`Union[Message, Sequence[Message]]`):
                The input arguments to be formatted, where each argument
                should be a `Message` object, or a list of `Message` objects.
                In distribution, placeholder is also allowed.

        Returns:
            `List[dict]`:
                The formatted messages.
        """
        if len(args) == 0:
            raise ValueError(
                "At least one message should be provided. An empty message "
                "list is not allowed.",
            )

        # Parse all information into a list of messages
        input_Messages = []
        for _ in args:
            if _ is None:
                continue
            if isinstance(_, Message):
                input_Messages.append(_)
            elif isinstance(_, list) and all(isinstance(__, Message) for __ in _):
                input_Messages.extend(_)
            else:
                raise TypeError(
                    f"The input should be a Message object or a list "
                    f"of Message objects, got {type(_)}.",
                )

        # record dialog history as a list of strings
        dialogue = []
        sys_prompt = None
        for i, unit in enumerate(input_Messages):
            if i == 0 and unit.role == "system":
                # if system prompt is available, place it at the beginning
                sys_prompt = _convert_to_str(unit.content)
            else:
                # Merge all messages into a conversation history prompt
                dialogue.append(
                    f"{unit.name}: {_convert_to_str(unit.content)}",
                )

        content_components = []

        # The conversation history is added to the user message if not empty
        if len(dialogue) > 0:
            content_components.extend(["## Conversation History"] + dialogue)

        messages = [
            {
                "role": "user",
                "content": "\n".join(content_components),
            },
        ]

        # Add system prompt at the beginning if provided
        if sys_prompt is not None:
            messages = [{"role": "system", "content": sys_prompt}] + messages

        return messages