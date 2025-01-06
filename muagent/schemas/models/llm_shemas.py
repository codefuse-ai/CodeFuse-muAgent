from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from enum import Enum



class ChatMessage(BaseModel):
    role: str
    content: str


class FunctionCallData(BaseModel):
    name: str
    arguments: Union[str, dict]


class ToolCall(BaseModel):
    id: Optional[Union[str, int]] = None
    type: str = "function"
    function: FunctionCallData


class LLMOuputMessage(BaseModel):
    content: Optional[str] = None
    role: str
    tool_calls: List[ToolCall] = []


class Choice(BaseModel):
    finish_reason: str
    index: int = 0
    message: LLMOuputMessage


class UsageData(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_token: int


class LLMResponse(BaseModel):
    choices: List[Choice]
    created: int = 0
    id: str
    model: str
    object: str
    usage: Optional[UsageData] = None



