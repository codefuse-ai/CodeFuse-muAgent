from pydantic import BaseModel
from typing import List, Union, Dict, Optional, Literal
from loguru import logger

from .message import Message


class Memory(BaseModel):
    '''The base dataclass of Memory'''

    messages: List[Message] = []
    _limit: Optional[int] = None
    
    def set_limit(self, limit: Optional[int] = None):
        self._limit = limit

    def _limit_messages(self, ):
        if self._limit:
            self.messages = self.messages[-self._limit:]

    def append(self, message: Message):
        self.messages.append(message)
        self._limit_messages()

    def extend(self, memory: 'Memory'):
        self.messages.extend(memory.messages)
        self._limit_messages()

    def update(self, message: Message, role_tag: str = None):
        if role_tag is None:
            return 
        message_index = message.message_index
        idx = None
        for idx, msg in enumerate(self.messages):
            if msg.session_index == message_index: break
        if idx is not None:
            if (self.messages[idx].role_tags, list):
                self.messages[idx].role_tags = list(set(self.messages[idx].role_tags + [role_tag]))    
            else:
                self.messages[idx].role_tags += f", {role_tag}"

    def sort_by_key(self, key: str):
        self.messages = sorted(self.messages, key=lambda x: getattr(x, key, f"No this {key}"))

    def clear(self, k: int = None):
        '''save the messages by k limit'''
        if k is None:
            self.messages = []
        else:
            self.messages = self.messages[-k:]

    def get_messages(self, k=0) -> List[Message]:
        """Return the most recent k memories, return all when k=0"""
        return self.messages[-k:]

    def get_datetimes(self) -> List[any]:
        """get datetime values values. default: end_datetime"""
        return self.get_memory_values("end_datetime")

    def get_contents(self) -> List[any]:
        """get content values"""
        return self.get_memory_values("content")

    def get_memory_values(self, key: str) -> List[any]:
        return [message.get_value(key) for message in self.messages]
    
    def split_by_role_type(self) -> List[Dict[str, 'Memory']]:
        """
        Split messages into rounds of conversation based on role_type.
        Each round consists of consecutive messages of the same role_type.
        User messages form a single round, while assistant and function messages are combined into a single round.
        Each round is represented by a dict with 'role' and 'memory' keys, with assistant and function messages
        labeled as 'assistant'.
        """
        rounds = []
        current_memory = Memory()
        current_role = None

        for msg in self.messages:
            # Determine the message's role, considering 'function' as 'assistant'
            message_role = 'assistant' if msg.role_type in ['assistant', 'function'] else 'user'
            
            # If the current memory is empty or the current message is of the same role_type as current_role, add to current memory
            if not current_memory.messages or current_role == message_role:
                current_memory.append(msg)
            else:
                # Finish the current memory and start a new one
                rounds.append({'role': current_role, 'memory': current_memory})
                current_memory = Memory()
                current_memory.append(msg)
            
            # Update the current_role, considering 'function' as 'assistant'
            current_role = message_role

        # Don't forget to add the last memory if it exists
        if current_memory.messages:
            rounds.append({'role': current_role, 'memory': current_memory})
            
        return rounds

    def format_rounds_to_html(self) -> str:
        formatted_html_str = ""
        rounds = self.split_by_role_type()

        for round in rounds:
            role = round['role']
            memory = round['memory']
            
            # 转换当前round的Memory为字符串
            messages_str = memory.to_str_messages()

            # 根据角色类型添加相应的HTML标签
            if role == 'user':
                formatted_html_str += f"<user-message>\n{messages_str}\n</user-message>\n"
            else:  # 对于'assistant'和'function'角色，我们将其视为'assistant'
                formatted_html_str += f"<assistant-message>\n{messages_str}\n</assistant-message>\n"

        return formatted_html_str

    def to_format_messages(
            self, 
            attributes: dict[str, Union[any, List[any]]] = {},
            filter_type: Optional[Literal['select', 'filter']] = None,
            *,
            return_all: bool = True, 
            content_key: str = "content", 
            with_tag: bool = False,
            format_type: Literal['raw', 'tuple', 'dict', 'str']='raw',
            logic: Literal['or', 'and'] = 'and'
        ) -> List[Message]:
        '''Filter messages by attributes'''
        def _logic_check(values: List[bool], logic):
            # default: not filter any message 
            if values == []: return True
            return any(values) if logic == "or" else all(values)

        def _select(message, attrs, select_type="filter"):
            if select_type == "filter":
                return [message.get(key) not in value if isinstance(value, list) else
                    message.get(key) != value
                    for key, value in attrs.items()
                ]
            else:
                return [message.get(key) in value if isinstance(value, list) else
                    message.get(key) == value
                    for key, value in attrs.items()
                ]
        # 
        messages = [ 
            message for message in self.messages
            if _logic_check(_select(message, attributes, filter_type), logic)
        ]

        # 
        if format_type == "tuple":
            return [
                message.to_tuple_message(return_all, content_key)
                for message in messages
            ]
        elif format_type == "dict":
            return [
                message.to_dict_message()
                for message in messages
            ]
        elif format_type == "str":
            return "\n\n".join([
                message.to_str_content(content_key, with_tag=with_tag) 
                for message in messages 
            ])

        return messages
    
    @classmethod
    def from_memory_list(cls, memorys: List['Memory']) -> 'Memory':
        return cls(messages=[message for memory in memorys for message in memory.get_messages()])
    
    def __len__(self, ):
        return len(self.messages)

    def __str__(self) -> str:
        return self.to_format_messages(format_type="str")
        return "\n".join([": ".join(i) for i in self.to_format_messages(format_type="tuple")])
    
    def __add__(self, other: Union[Message, 'Memory']) -> 'Memory':
        if isinstance(other, Message):
            return Memory(messages=self.messages + [other])
        elif isinstance(other, Memory):
            return Memory(messages=self.messages + other.messages)
        else:
            raise ValueError(f"cant add unspecified type like as {type(other)}")
        
    
    