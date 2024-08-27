import re, traceback, uuid, copy, json, os
from typing import Union, Tuple
from loguru import logger

from langchain.schema import BaseRetriever

from muagent.connector.schema import (
    Memory, Role, Message, ActionStatus, CodeDoc, Doc, LogVerboseEnum
)
from muagent.retrieval.base_retrieval import IMRertrieval
from muagent.connector.memory_manager import BaseMemoryManager
from muagent.tools import DDGSTool, DocRetrieval, CodeRetrieval
from muagent.sandbox import PyCodeBox, CodeBoxResponse
from muagent.llm_models.llm_config import LLMConfig, EmbedConfig
from muagent.base_configs.env_config import JUPYTER_WORK_PATH

from .utils import parse_dict_to_dict, parse_text_to_dict


class MessageUtils:
    def __init__(
            self, 
            role: Role = None,
            sandbox_server: dict = {},
            jupyter_work_path: str = JUPYTER_WORK_PATH,
            embed_config: EmbedConfig = None,
            llm_config: LLMConfig = None,
            kb_root_path: str = "",
            doc_retrieval: Union[BaseRetriever, IMRertrieval] = None,
            code_retrieval: IMRertrieval = None,
            search_retrieval: IMRertrieval = None,
            log_verbose: str = "0"
        ) -> None:
        self.role = role
        self.sandbox_server = sandbox_server
        self.jupyter_work_path = jupyter_work_path
        self.embed_config = embed_config
        self.llm_config = llm_config
        self.kb_root_path = kb_root_path
        self.doc_retrieval = doc_retrieval
        self.code_retrieval = code_retrieval
        self.search_retrieval = search_retrieval
        self.codebox = PyCodeBox(
                    remote_url=self.sandbox_server.get("url", "http://127.0.0.1:5050"),
                    remote_ip=self.sandbox_server.get("host", "http://127.0.0.1"),
                    remote_port=self.sandbox_server.get("port", "5050"),
                    jupyter_work_path=jupyter_work_path,
                    token="mytoken",
                    do_code_exe=True,
                    do_remote=self.sandbox_server.get("do_remote", False),
                    do_check_net=False
                    )
        self.log_verbose = os.environ.get("log_verbose", "0") or log_verbose
    
    def inherit_extrainfo(self, input_message: Message, output_message: Message):
        output_message.user_name = input_message.user_name
        output_message.db_docs = input_message.db_docs
        output_message.search_docs = input_message.search_docs
        output_message.code_docs = input_message.code_docs
        output_message.figures.update(input_message.figures)
        output_message.code_engine_name = input_message.code_engine_name

        output_message.doc_engine_name = input_message.doc_engine_name
        output_message.search_engine_name = input_message.search_engine_name
        output_message.top_k = input_message.top_k
        output_message.score_threshold = input_message.score_threshold
        output_message.cb_search_type = input_message.cb_search_type
        output_message.do_doc_retrieval = input_message.do_doc_retrieval
        output_message.do_code_retrieval = input_message.do_code_retrieval
        output_message.do_tool_retrieval = input_message.do_tool_retrieval
        # 
        output_message.tools = input_message.tools
        output_message.agents = input_message.agents

        # update customed_kargs, if exist, keep; else add
        customed_kargs = copy.deepcopy(input_message.customed_kargs)
        customed_kargs.update(output_message.customed_kargs)
        output_message.customed_kargs = customed_kargs
        return output_message
    
    def inherit_baseparam(self, input_message: Message, output_message: Message):
        # 只更新参数
        output_message.doc_engine_name = input_message.doc_engine_name
        output_message.search_engine_name = input_message.search_engine_name
        output_message.top_k = input_message.top_k
        output_message.score_threshold = input_message.score_threshold
        output_message.cb_search_type = input_message.cb_search_type
        output_message.do_doc_retrieval = input_message.do_doc_retrieval
        output_message.do_code_retrieval = input_message.do_code_retrieval
        output_message.do_tool_retrieval = input_message.do_tool_retrieval
        # 
        output_message.tools = input_message.tools
        output_message.agents = input_message.agents
        # 存在bug导致相同key被覆盖
        output_message.customed_kargs.update(input_message.customed_kargs)
        return output_message

    def get_extrainfo_step(self, message: Message, do_search, do_doc_retrieval, do_code_retrieval, do_tool_retrieval) -> Message:
        ''''''
        if do_search:
            message = self.get_search_retrieval(message)
        
        if do_doc_retrieval:
            message = self.get_doc_retrieval(message)

        if do_code_retrieval:
            message = self.get_code_retrieval(message)

        if do_tool_retrieval:
            message = self.get_tool_retrieval(message)
        
        return message 
    
    def get_search_retrieval(self, message: Message,) -> Message:
        SEARCH_ENGINES = {"duckduckgo": DDGSTool}
        search_docs = []
        for idx, doc in enumerate(SEARCH_ENGINES["duckduckgo"].run(message.role_content, 3)):
            doc.update({"index": idx})
            search_docs.append(Doc(**doc))
        message.search_docs = search_docs
        return message
    
    def get_doc_retrieval(self, message: Message) -> Message:
        query = message.role_content
        knowledge_basename = message.doc_engine_name
        top_k = message.top_k
        score_threshold = message.score_threshold
        if self.doc_retrieval:
            if isinstance(self.doc_retrieval, BaseRetriever):
                # langchain format
                docs = self.doc_retrieval.get_relevant_documents(query)
                docs = [
                    {"index": idx, "snippet": doc.page_content, "title": doc.metadata.get("title_prefix", ""), "link": doc.metadata.get("url", "")}
                    for idx, doc in enumerate(docs)
                ]
            else:
                # docs = self.doc_retrieval.run(query, search_top=message.top_k, score_threshold=message.score_threshold,)
                docs = self.doc_retrieval.run(query)
            message.db_docs = [Doc(**doc) for doc in docs]
        else:
            if knowledge_basename:
                docs = DocRetrieval.run(query, knowledge_basename, top_k, score_threshold, self.embed_config, self.kb_root_path)
                message.db_docs = [Doc(**doc) for doc in docs]
        return message
    
    def get_code_retrieval(self, message: Message) -> Message:
        query = message.role_content
        code_engine_name = message.code_engine_name
        history_node_list = message.history_node_list

        use_nh = message.use_nh
        local_graph_path = message.local_graph_path

        if self.code_retrieval:
            code_docs = self.code_retrieval.run(
                query, history_node_list=history_node_list, search_type=message.cb_search_type,
                code_limit=1
            )
        else:
            code_docs = CodeRetrieval.run(code_engine_name, query, code_limit=message.top_k, history_node_list=history_node_list, search_type=message.cb_search_type,
                                      llm_config=self.llm_config, embed_config=self.embed_config,
                                      use_nh=use_nh, local_graph_path=local_graph_path)
        
        message.code_docs = [CodeDoc(**doc) for doc in code_docs] 
        return message
    
    def get_tool_retrieval(self, message: Message) -> Message:
        return message
    
    def step_router(self, message: Message, history: Memory = None, background: Memory = None, memory_manager: BaseMemoryManager=None, chat_index: str = "") -> Tuple[Message, ...]:
        ''''''
        chat_index = message.chat_index or chat_index or str(uuid.uuid4())
        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"message.action_status: {message.action_status}")
            
        observation_message = None
        if message.action_status == ActionStatus.CODE_EXECUTING:
            message, observation_message = self.code_step(message, chat_index)
        elif message.action_status == ActionStatus.TOOL_USING:
            message, observation_message = self.tool_step(message, chat_index)
        elif message.action_status == ActionStatus.CODING2FILE:
            self.save_code2file(message, self.jupyter_work_path)
        elif message.action_status == ActionStatus.CODE_RETRIEVAL:
            pass
        elif message.action_status == ActionStatus.CODING:
            pass
        
        return message, observation_message

    def code_step(self, message: Message, chat_index: str) -> Message:
        '''execute code'''
        # code_answer = self.codebox.chat('```python\n{}```'.format(message.code_content))
        code_answer = self.codebox.chat('```python\n{}```'.format(message.customed_kargs.get("code_content", "")))
        code_prompt = f"The return error after executing the above code is {code_answer.code_exe_response}，need to recover.\n" \
                    if code_answer.code_exe_type == "error" else f"The return information after executing the above code is {code_answer.code_exe_response}.\n"
        
        observation_message = Message(
                chat_index=chat_index,
                user_name=message.user_name,
                role_name="observation",
                role_type="function", #self.role.role_type,
                role_content="",
                step_content="",
                # input_query=message.code_content,
                input_query=message.customed_kargs.get("code_content", ""),
                )
        uid = str(uuid.uuid1())
        if code_answer.code_exe_type == "image/png":
            message.figures[uid] = code_answer.code_exe_response
            message.step_content += f"\n**Observation:**: The return figure name is {uid} after executing the above code.\n"
            observation_message.role_content = f"\n**Observation:**: The return figure name is {uid} after executing the above code.\n"
            observation_message.parsed_output = {"Observation": f"The return figure name is {uid} after executing the above code.\n"}
        else:
            message.step_content += f"\n**Observation:**: {code_prompt}\n"
            observation_message.role_content = f"\n**Observation:**: {code_prompt}\n"
            observation_message.parsed_output = {"Observation": f"{code_prompt}\n"}
        
        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"**Observation:** {message.action_status}, {observation_message.role_content}")
        return message, observation_message

    def tool_step(self, message: Message, chat_index: str) -> Message:
        '''execute tool'''
        observation_message = Message(
                chat_index=chat_index,
                user_name=message.user_name,
                role_name="observation",
                role_type="function", #self.role.role_type,
                role_content="\n**Observation:** there is no tool can execute\n",
                step_content="",
                input_query=str(message.customed_kargs.get("tool_params", {})),
                tools=message.tools,
                )
        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"message: {message.action_status}, {message.customed_kargs.get('tool_params', '')}")

        tool_names = [tool.name for tool in message.tools]
        if message.customed_kargs.get("tool_name", "") not in tool_names:
            message.step_content += f"\n**Observation:** there is no tool can execute.\n"
            observation_message.role_content = f"\n**Observation:** there is no tool can execute.\n"
            observation_message.parsed_output = {"Observation": "there is no tool can execute.\n"}
        
        # logger.debug(message.tool_params)
        for tool in message.tools:
            if tool.name == message.customed_kargs.get("tool_params", {}).get("tool_name", ""):
                tool_res = tool.func(**message.customed_kargs.get("tool_params", {}).get("tool_params", {}))
                message.step_content += f"\n**Observation:** {tool_res}.\n"
                observation_message.role_content = f"\n**Observation:** {tool_res}.\n"
                observation_message.parsed_output = {"Observation": f"{tool_res}.\n"}
                break

        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"**Observation:** {message.action_status}, {observation_message.role_content}")
        return message, observation_message

    # TODO outlines
    def parser(self, message: Message) -> Message:
        '''parse llm output into dict'''
        content = message.role_content
        # parse start
        parsed_dict = parse_text_to_dict(content)
        spec_parsed_dict = parse_dict_to_dict(parsed_dict)
        # select parse value
        action_value = parsed_dict.get('Action Status')
        if action_value:
            action_value = action_value.lower()

        code_content_value = spec_parsed_dict.get('code')
        if action_value == 'tool_using':
            tool_params_value = spec_parsed_dict.get('json')
        else:
            tool_params_value = {}

        # add parse value to message
        message.action_status = action_value or "default"
        message.customed_kargs["code_content"] = code_content_value
        message.customed_kargs["tool_params"] = tool_params_value
        message.parsed_output = parsed_dict
        message.spec_parsed_output = spec_parsed_dict
        return message

    def save_code2file(self, message: Message, project_dir="./"):
        filename = message.parsed_output.get("SaveFileName")
        code = message.spec_parsed_output.get("code")

        for k, v in {"&gt;": ">", "&ge;": ">=", "&lt;": "<", "&le;": "<="}.items():
            code = code.replace(k, v)

        file_path = os.path.join(project_dir, filename)

        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            f.write(code)
        