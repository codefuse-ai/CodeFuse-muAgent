from pydantic import BaseModel, root_validator
from loguru import logger
import uuid
from muagent.utils.common_utils import getCurrentDatetime
from .general_schema import *


class Message(BaseModel):
    chat_index: str = "" # 会话ID，某一轮会话
    message_index: str = "" # 会话消息ID，某轮会话里第几个会话记录
    user_name: str = "default"
    role_name: str
    role_type: str
    role_prompt: str = ""
    input_query: str = ""
    start_datetime: str = None
    end_datetime: str = None
    role_tags: str = ""

    # llm output
    role_content: str = ""
    step_content: str = ""

    # llm parsed information
    # code_content: str = None
    # tool_params: str = None
    # tool_name: str = None
    parsed_output: dict = {}
    spec_parsed_output: dict = {}
    parsed_output_list: List[Dict] = []

    # llm\tool\code executre information
    action_status: str = "default"
    # code_answer: str = None
    # tool_answer: str = None
    # observation: str = None
    figures: Dict[str, str] = {}

    # prompt support information
    task: Task = None
    db_docs: List['Doc'] = []
    code_docs: List['CodeDoc'] = []
    search_docs: List['Doc'] = []
    # user's customed kargs for init or end action
    customed_kargs: dict = {}

    # phase input
    agents: List = []
    tools: List = []
    phase_name: str = None
    chain_name: str = None
    do_search: bool = False
    doc_engine_name: str = None
    code_engine_name: str = None
    cb_search_type: str = None
    search_engine_name: str = None 
    top_k: int = 3
    use_nh: bool = True
    local_graph_path: str = ''
    score_threshold: float = 1.0
    do_doc_retrieval: bool = False
    do_code_retrieval: bool = False
    do_tool_retrieval: bool = False
    history_node_list: List[str] = []


    @root_validator(pre=True)
    def check_card_number_omitted(cls, values):
        input_query = values.get("input_query")
        role_content = values.get("role_content")
        if input_query is None:
            values["input_query"] = role_content
        if role_content is None:
            values["role_content"] = input_query
        return values
    
    @root_validator(pre=True)
    def check_datetime(cls, values):
        start_datetime = values.get("start_datetime")
        end_datetime = values.get("end_datetime")
        if start_datetime is None:
            values["start_datetime"] = getCurrentDatetime("%Y-%m-%d %H:%M:%S.%f")
        if end_datetime is None:
            values["end_datetime"] = getCurrentDatetime("%Y-%m-%d %H:%M:%S.%f")
        return values

    @root_validator(pre=True)
    def check_message_index(cls, values):
        message_index = values.get("message_index")
        chat_index = values.get("chat_index")
        if message_index is None or message_index == "":
            values["message_index"] = str(uuid.uuid4()).replace("-", "_")

        if chat_index is None or chat_index == "":
            values["chat_index"] = str(uuid.uuid4()).replace("-", "_")
        return values
    

    def update_attribute(self, key: str, value):
        if hasattr(self, key):
            setattr(self, key, value)
            self.end_datetime = getCurrentDatetime("%Y-%m-%d %H:%M:%S.%f")
        else:
            raise AttributeError(f"{key} is not a valid property of {self.__class__.__name__}")

    def get_attribute_type(self, key):
        return type(getattr(self, key, None))

    # @root_validator(pre=True)
    # def check_card_number_omitted(cls, values):
    #     input_query = values.get("input_query")
    #     origin_query = values.get("origin_query")
    #     role_content = values.get("role_content")
    #     if input_query is None:
    #         values["input_query"] = origin_query or role_content
    #     if role_content is None:
    #         values["role_content"] = origin_query
    #     return values
    
    # pydantic>=2.0
    # @model_validator(mode='after')
    # def check_passwords_match(self) -> 'Message':
    #     if self.input_query is None:
    #         self.input_query = self.origin_query or self.role_content
    #     if self.role_content is None:
    #         self.role_content = self.origin_query
    #     return self
    
    def to_tuple_message(self, return_all: bool = True, content_key="role_content"):
        role_content = self.to_str_content(False, content_key)
        if return_all:
            return (self.role_name, role_content)
        else:
            return (role_content)
    
    def to_dict_message(self, ):
        return vars(self)
        
    def to_str_content(self, return_all: bool = True, content_key="role_content", with_tag=False):
        # TODO while role_type is USER  return input_query, else return role_content
        if content_key == "role_content":
            role_content = self.role_content or self.input_query
        elif content_key == "step_content":
            role_content  = self.step_content or self.role_content or self.input_query
        elif content_key == "parsed_output":
            role_content = "\n".join([f"**{k}:** {v}" for k, v in self.parsed_output.items()]) or self.input_query
        elif content_key == "parsed_output_list":
            role_content = "\n".join([f"**{k}:** {v}" for po in self.parsed_output_list for k,v in po.items()]) or self.input_query
        else:
            role_content = self.role_content or self.input_query

        if with_tag:
            start_tag = f"<{self.role_type}-{self.role_name}-message>"
            end_tag = f"</{self.role_type}-{self.role_name}-message>"
            return f"{start_tag}\n{role_content}\n{end_tag}"
        else:
            return role_content
    
    def __str__(self) -> str:
        # key_str = '\n'.join([k for k, v in vars(self).items()])
        # logger.debug(f"{key_str}")
        return "\n".join([": ".join([k, str(v)]) for k, v in vars(self).items()])
    