from pydantic import BaseModel, root_validator
from typing import List, Dict, Optional, Literal, Union, Sequence, Tuple
from loguru import logger
import uuid
from muagent.utils.common_utils import getCurrentDatetime



class Message(BaseModel):
    '''The base dataclass of Message

    The following is an example:

    .. code-block:: python

        from muagent.schemas.message import Message
        msg = Message(
            role_name="system",
            role_type="system",
            content="You're a helpful assistant",
        )
    '''
    
    # 
    role_name: str = "muagent"
    '''The role name of agent to generate this message.'''

    role_type: Literal[
        'system', 
        'user', 
        'assistant', 
        'observation', 
        'tool_call',
        'function',
        'codefuse',
        'summary'
    ] = "codefuse"
    '''The role type of agent to generate this message. such as system/user/assistant/observation/tool_call'''
    # 
    role_tags: Union[Sequence[str], str] = ''
    '''The tags of this message.'''

    embedding: Optional[Sequence] = None
    '''The embedding from LLM of this message.'''

    image_urls: Optional[Sequence[str]] = None
    '''The image_urls from LLM of this message.'''

    action_status: str = "default"
    '''llm\tool\code executre information'''

    content: Optional[str] = ""
    '''The last response from LLM of this message.'''

    step_content: Optional[str] = ''
    '''The multi content from LLM of this message, connected by \n'''

    parsed_content: Dict = {}
    '''The structed content from LLM parsing of this message'''

    parsed_contents: List[Dict] = []
    '''The multi structed content from LLM parsing of this message'''

    spec_parsed_content: Dict = {}
    '''The special structed content from LLM parsing of this message'''

    spec_parsed_contents: List[Dict] = []
    '''The multi special structed content from LLM parsing of this message'''

    global_kwargs: Dict = {}
    '''user's customed kargs for init or end action'''

    # input from last message
    input_text: Optional[str] = ""
    '''The input text from last message.'''

    parsed_input: Dict = {}
    '''The structed input from LLM parsing from last message'''

    parsed_inputs: List[Dict] = []
    '''The multi structed input from LLM parsing from last message'''

    spec_parsed_input: Dict = {}
    '''The special structed content from LLM parsing of this message'''

    spec_parsed_inputs: List[Dict] = []
    '''The multi special structed content from LLM parsing of this message'''

    # 
    session_index: Optional[str] = None
    '''The session index of this message.'''

    message_index: Optional[str] = None
    '''The message index of this message.'''

    node_index: Optional[str] = "default"
    '''The node index of this message.'''

    # 
    start_datetime: str = None
    '''The first record time of this message.'''

    end_datetime: str = None
    '''The last update time of this message.'''

    datetime_format: str = "%Y-%m-%d %H:%M:%S.%f"

    @root_validator(pre=True)
    def check_card_number_omitted(cls, values):
        input_text = values.get("input_text")
        content = values.get("content")
        if content is None:
            values["content"] = content or input_text
        return values
    
    @root_validator(pre=True)
    def check_datetime(cls, values):
        start_datetime = values.get("start_datetime")
        end_datetime = values.get("end_datetime")
        datetime_format = values.get("datetime_format", "%Y-%m-%d %H:%M:%S.%f")
        if start_datetime is None:
            values["start_datetime"] = getCurrentDatetime(datetime_format)
        if end_datetime is None:
            values["end_datetime"] = getCurrentDatetime(datetime_format)
        return values

    @root_validator(pre=True)
    def check_message_index(cls, values):
        message_index = values.get("message_index")
        session_index = values.get("session_index")
        if message_index is None or message_index == "":
            values["message_index"] = str(uuid.uuid4()).replace("-", "_")

        if session_index is None or session_index == "":
            values["session_index"] = str(uuid.uuid4()).replace("-", "_")
        return values

    def update_input(self, input: Union[str, 'Message'], parsed_input: Dict = {}):
        if isinstance(input, str):
            self.update_attributes({"input_text": input})
        else:
            self.update_attributes({"input_text": input.content})

    def update_parsed_input(self, parsed_input: Dict):
        self.update_attributes({"parsed_input": parsed_input})
        self.update_attributes({"parsed_inputs": self.parsed_inputs + [parsed_input]})

    def update_spec_parsed_input(self, spec_parsed_input: Dict):
        self.update_attributes({"spec_parsed_input": spec_parsed_input})
        self.update_attributes({"spec_parsed_inputs": self.spec_parsed_inputs + [spec_parsed_input]})

    def update_content(self, content: Union[str, 'Message'], parsed_content: Dict = {}):
        if isinstance(content, str):
            self.update_attributes({"content": content})
            self.update_attributes({"step_content": self.step_content + f"\n{content}"})
        else:
            self.update_attributes({"content": content.content})
            self.update_attributes({"step_content": self.step_content + f"\n{content.content}"})

    def update_parsed_content(self, parsed_content: Dict = {}):
        self.update_attributes({"parsed_content": parsed_content})
        self.update_attributes({"parsed_contents": self.parsed_contents + [parsed_content]})

    def update_spec_parsed_content(self, spec_parsed_content: Dict = {}):
        self.update_attributes({"spec_parsed_content": spec_parsed_content})
        self.update_attributes({"spec_parsed_contents": self.spec_parsed_contents + [spec_parsed_content]})

    def update_attributes(self, attributes: dict):
        '''update message attributes'''
        for k, v in attributes.items():
            self.update_attribute(k, v)

    def update_attribute(self, key: str, value):
        if hasattr(self, key):
            setattr(self, key, value)
            self.end_datetime = getCurrentDatetime(self.datetime_format)
        else:
            raise AttributeError(f"{key} is not a valid property of {self.__class__.__name__}")

    def to_dict_message(self, ) -> Dict:
        return vars(self)

    def to_tuple_message(
            self, 
            return_all: bool = True, 
            content_key: Literal[
                'input_text',
                'content',
                'step_conetent',
                'parsed_content',
                'spec_parsed_contents',
            ] = "content", 
        ) -> Union[str, Tuple[str, str]]:
        content = self.to_str_content(False, content_key)
        if return_all:
            return (self.role_name, content)
        else:
            return (content)
    
    def to_str_content(
            self, 
            content_key: Literal[
                'input_text',
                'content',
                'step_conetent',
                'parsed_content',
                'parsed_contents',
                'spec_parsed_content',
                'spec_parsed_contents',
            ] = "content", 
            with_tag=False
        ) -> str:
        # TODO while role_type is USER  return input_query, else return role_content
        response = self.content or self.input_text
        if content_key == "content":
            content = response
        elif content_key == "input_text":
            content = self.input_text
        elif content_key == "step_content":
            content  = self.step_content or response
        elif content_key == "parsed_content":
            content = "\n".join([v for k, v in self.parsed_content.items()]) or response
            # content = "\n".join([f"**{k}:** {v}" for k, v in self.parsed_content.items()]) or response
        elif content_key == "spec_parsed_content":
            content = "\n".join([f"**{k}:** {v}" for k, v in self.spec_parsed_content.items()]) or response
        elif content_key == "parsed_contents":
            content = "\n".join([v for po in self.parsed_contents for k,v in po.items()]) or response
        elif content_key == "spec_parsed_contents":
            content = "\n".join([f"**{k}:** {v}" for po in self.spec_parsed_contents for k,v in po.items()]) or response
        else:
            content = response

        if with_tag:
            start_tag = f"<{self.role_type}-{self.role_name}-message>"
            end_tag = f"</{self.role_type}-{self.role_name}-message>"
            return f"{start_tag}\n{content}\n{end_tag}"
        else:
            return content
    
    def get_value(self, key: str) -> any:
        """
        Get the value of the given key from the message.

        :param key: The key of the attribute to retrieve.
        :return: The value associated with the key.
        """
        if hasattr(self, key):
            return getattr(self, key, None)
        raise AttributeError(f"Message don't have attribute {key}")
    
    def get_attribute_type(self, key):
        return type(getattr(self, key, None))
    
    def __str__(self) -> str:
        # key_str = '\n'.join([k for k, v in vars(self).items()])
        # logger.debug(f"{key_str}")
        return "\n".join([": ".join([k, str(v)]) for k, v in vars(self).items()])
    