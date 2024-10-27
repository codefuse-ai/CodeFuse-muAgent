from typing import List, Union, Dict
import os
import json

from langchain_openai import ChatOpenAI
from langchain.llms.base import LLM
from langchain_community.docstore.document import Document


from muagent.connector.configs.generate_prompt import *
from muagent.connector.schema import Memory, Message
from muagent.schemas.db import DBConfig, GBConfig, VBConfig, TBConfig
from muagent.schemas.common import *
from muagent.db_handler import *
from muagent.connector.memory_manager import BaseMemoryManager
from muagent.llm_models import *
from muagent.base_configs.env_config import KB_ROOT_PATH
from muagent.orm import table_init

from muagent.utils.common_utils import *


class HierarchicalMemoryManager(BaseMemoryManager):
    def __init__(
            self,
            embed_config: EmbedConfig,
            llm_config: LLMConfig,
            db_config: DBConfig = None,
            vb_config: VBConfig = None,
            gb_config: GBConfig = None,
            tb_config: TBConfig = None,
            do_init: bool = False,
            kb_root_path: str = KB_ROOT_PATH,
        ):
        self.db_config = db_config
        self.vb_config = vb_config
        self.gb_config = gb_config
        self.tb_config = tb_config
        self.do_init = do_init
        self.kb_root_path = kb_root_path
        self.embed_config: EmbedConfig = embed_config
        self.llm_config: LLMConfig = llm_config

        # default
        self.chat_index: str = "default"
        self.user_name = "default"
        self.uuid_name = "_".join([self.chat_index, self.user_name])
        self.kb_name = f"{self.chat_index}/{self.user_name}"
        self.uuid_file = os.path.join(self.kb_root_path, f"{self.chat_index}/{self.user_name}/conversation.jsonl")
        self.recall_memory_dict: Dict[str, Memory] = {} # overall turn conversation
        self.gb_memory_dict: Dict[str, Memory] = {} # lastet 10 turn conversation
        self.memory_uuids = set()
        self.save_message_keys = [
            'chat_index', 'message_index', 'user_name', 'role_name', 'role_type', 'input_query', 'role_content', 'step_content', 
            'parsed_output', 'parsed_output_list', 'customed_kargs', "db_docs", "code_docs", "search_docs", 'start_datetime', 'end_datetime', 
            "keyword", "vector",
        ]
        # init from config
        self.model = getChatModelFromConfig(self.llm_config)
        self.init_handler()
        self.load(do_init)

    def init_handler(self, ):
        """Initializes Database VectorBase GraphDB TbaseDB"""
        self.init_vb()
        # self.init_db()
        # self.init_tb()
        self.init_gb()

    def reinit_handler(self, do_init: bool=False):
        self.init_vb()
        # self.init_db()
        # self.init_tb()
        self.init_gb()

    def clear_local(self, re_init: bool = False, handler_type: str = None):
        if self.vb: # 存到了本地需要清理
            self.vb.clear_vs_local()
            self.load(re_init)

    def init_tb(self, do_init: bool=None):
        tb_dict = {"TbaseHandler": TbaseHandler}
        tb_class =  tb_dict.get(self.tb_config.tb_type, TbaseHandler)
        tbase_args = {
            "host": self.tb_config.host,
            "port": self.tb_config.port,
            "username": self.tb_config.username,
            "password": self.tb_config.password,
        }
        self.vb = tb_class(tbase_args, self.tb_config.index_name, tb_config=self.tb_config)

    def init_gb(self, do_init: bool=None):
        gb_dict = {"NebulaHandler": NebulaHandler, "NetworkxHandler": NetworkxHandler}
        gb_class =  gb_dict.get(self.gb_config.gb_type, NetworkxHandler)
        self.gb: NetworkxHandler = gb_class(kb_root_path=KB_ROOT_PATH, gb_config=self.gb_config)

    def init_db(self, do_init: bool=None):
        self.db = None
        # db_dict = {"LocalFaissHandler": LocalFaissHandler}
        # db_class =  db_dict.get(self.db_config.db_type)
        # self.db = db_class(self.db_config)

    def init_vb(self, do_init: bool=None):
        table_init()
        vb_dict = {"LocalFaissHandler": LocalFaissHandler}
        vb_class =  vb_dict.get(self.vb_config.vb_type, LocalFaissHandler)
        self.vb: LocalFaissHandler = vb_class(self.embed_config, vb_config=self.vb_config)

    def append(self, message: Message):
        """
        Appends a message to the recall memory, current memory, and summary memory.

        Args:
        - message: An instance of Message class representing the message to be appended.
        """
        # update the newest uuid_name
        self.check_uuid_name(message)
        datetimes = self.recall_memory_dict[self.uuid_name].get_datetimes()
        contents = self.recall_memory_dict[self.uuid_name].get_contents()
        # if message not in chat history, no need to update
        if (message.end_datetime not in datetimes) or \
            ((message.input_query not in contents) and (message.role_content not in contents)):
            self.append2gb(message)
            self.append2vb(message)
        # 5、offline：summary node
        # 6、offline：node cluster
        # 7、offline: summary node/relation cluster

    def append2gb(self, message: Message):
        message_limit = 9
        # 0、check the sustain the requirement
        self.gb_memory_dict[self.uuid_name].append_with_limit(message, limit=message_limit)
        # 1、acquire the conversation
        messages = self.gb_memory_dict[self.uuid_name].get_messages(max(int(message_limit*2/3), 1))
        ## The number of messages must meet a certain size
        if len(messages) >= 6:
            # TODO add user-name as sep
            conversation = "\n".join([m.to_str_content(content_key="step_content") for m in messages])
            # 2、offline: get schema from content by llm, merge schema from origin shcemas
            self.node_schmeas, self.edge_schemas = self._get_schema_by_llm(conversation)
            # 3、offline: get graph node and graph relation from content by llm
            nodes, edges = self._get_ner_by_llm(conversation, self.node_schmeas, self.edge_schemas)
            # 4、insert graph node and graph into graph db
            self.gb.add_nodes(nodes)
            self.gb.add_edges(edges)
            # 
            if True: # resave the local
                self.gb.save(self.kb_name)

            self.gb_memory_dict[self.uuid_name].clear(3)

    def append2vb(self, message: Message) -> None:
        self.recall_memory_dict[self.uuid_name].append(message)
        # 
        docs, json_messages = self.message_process([message])
        # 
        if True: # resave the local
            save_to_json_file(json_messages, self.uuid_file)

        if self.embed_config:
            self.vb.add_docs(docs, kb_name=self.kb_name)

    def extend(self, memory: Memory):
        """
        Extends the recall memory, current memory, and summary memory.

        Args:
        - memory: An instance of Memory class representing the memory to be extended.
        """
        for message in memory.messages:
            self.append(message)

    def get_memory_pool(self, chat_index: str):
        """
        return memory_pool
        """
        pass

    def _get_schema_by_llm(
            self, conversation: str, node_schemas: List[GNodeAbs], edge_schemas: List[GRelationAbs]
        ) -> tuple[List[GNodeAbs], List[GRelationAbs]]:
        """
        """
        # acquire the prompt
        prompt = createMKGSchemaPrompt(conversation=conversation)
        # 
        content = self.model.predict(prompt)
        # convert schema
        raw_schema = json.loads(content)
        nodes = raw_schema["nodes"]
        edges = raw_schema["edges"]
        # merge schemas
        self._merge_node_schems([GNodeAbs(**node) for node in nodes], node_schemas)
        self._merge_node_schems([GRelationAbs(**edge) for edge in edges], edge_schemas)
        return node_schemas, edge_schemas

    def _merge_node_schems(self, new_schemas: List[GNodeAbs], old_schemas: List[GNodeAbs]):
        old_schemas.extend(new_schemas)
        return old_schemas

    def _merge_edge_schems(self, new_schemas: List[GRelationAbs], old_schemas: List[GRelationAbs]):
        old_schemas.extend(new_schemas)
        return old_schemas
    
    def _get_ner_by_llm(
            self, conversation, node_schemas: List[GNodeAbs], edge_schemas: List[GRelationAbs]
        ) -> tuple[list[GNode], list[GRelation]]:
        """
        """
        # 
        schemas = {
            "nodes": [s.dict() for s in node_schemas], 
            "edges": [s.dict() for s in edge_schemas]
        }
        schemas_json = json.dumps(schemas, indent=2, ensure_ascii=False)
        prompt = createMKGPrompt(conversation=conversation, schemas=schemas_json)
        # 
        content = self.model.predict(prompt)
        # convert content to node or relation
        raw_schema = json.loads(content)
        nodes = raw_schema["nodes"]
        nodes_dict = {node["name"]: node for node in nodes}
        edges = raw_schema["edges"]

        nodes = [GNode(**node) for node in nodes]
        edges = [
            GRelation(**{**edge, **{'start_id': nodes_dict.get(edge['start_id'], {}), 'end_id': nodes_dict.get(edge['end_id'], {})}}) 
            for edge in edges
        ]
        return nodes, edges

    def message_process(self, messages: List[Message]):
        '''convert messages to vb/local data-format'''
        messages = [
                    {k: v for k, v in m.dict().items() if k in self.save_message_keys}
                    for m in messages
                ] 
        docs = [{"page_content": m["step_content"] or m["role_content"] or m["input_query"], "metadata": m} for m in messages]
        docs = [Document(**doc) for doc in docs]
        # convert messages to local data-format
        memory_messages = self.recall_memory_dict[self.uuid_name].dict()
        json_messages = {
            k: [
                {kkk: vvv for kkk, vvv in vv.items() if kkk in self.save_message_keys}
                for vv in v 
            ] 
            for k, v in memory_messages.items()
        }

        return docs, json_messages

    def check_uuid_name(self, message: Message = None):
        if message.chat_index != self.chat_index:
            self.chat_index = message.chat_index
            self.user_name = message.user_name
            # self.init_vb()

        self.uuid_name = "_".join([self.chat_index, self.user_name])
        self.kb_name = f"{self.chat_index}/{self.user_name}"
        self.uuid_file = os.path.join(self.kb_root_path, f"{self.chat_index}/{self.user_name}/conversation.jsonl")

        self.memory_uuids.add(self.uuid_name)
        if self.uuid_name not in self.recall_memory_dict:
            self.recall_memory_dict[self.uuid_name] = Memory(messages=[])
        if self.uuid_name not in self.gb_memory_dict:
            self.gb_memory_dict[self.uuid_name] = Memory(messages=[])

    def get_uuid_from_chatindex(self, chat_index: str) -> str:
        for i in self.recall_memory_dict:
            if chat_index in i:
                return i
        return ""

    def get_kbname_from_chatindex(self, chat_index: str) -> str:
        return self.get_uuid_from_chatindex(chat_index).replace("_", "/")