from abc import abstractmethod, ABC
from typing import List, Dict
import os, sys, copy, json, uuid, random
from jieba.analyse import extract_tags
from collections import Counter
from loguru import logger
import numpy as np

from langchain_community.docstore.document import Document


from .base_memory_manager import BaseMemoryManager

from ..schemas import Memory, Message
from ..schemas.models import ModelConfig
from ..schemas.db import DBConfig, GBConfig, VBConfig, TBConfig

from ..models import get_model

from muagent.connector.configs.generate_prompt import *
from muagent.db_handler import *
from muagent.llm_models import getChatModelFromConfig
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.utils.common_utils import *
from muagent.base_configs.env_config import KB_ROOT_PATH


class LocalMemoryManager(BaseMemoryManager):
    """This class represents a LocalMemoryManager that inherits from BaseMemoryManager.
    It provides functionalities to handle local memory storage and retrieval of messages.
    """
    memory_manager_type: str = "local_memory_manager"
    """The type of memory manager"""

    def __init__(
            self,
            embed_config: Union[ModelConfig, EmbedConfig],
            llm_config: Union[LLMConfig, ModelConfig],
            vb_config: Optional[VBConfig] = None,
            db_config: Optional[DBConfig] = None,
            gb_config: Optional[GBConfig] = None,
            tb_config: Optional[TBConfig] = None,
            do_init: bool = False,
            kb_root_path: str = KB_ROOT_PATH,
        ):
        """Initialize the LocalMemoryManager with configurations.

        Args:
            embed_config (Union[ModelConfig, EmbedConfig]): Configuration for embedding.
            llm_config (Union[LLMConfig, ModelConfig]): Configuration for LLM.
            vb_config (Optional[VBConfig], optional): Vector database configuration.
            db_config (Optional[DBConfig], optional): Database configuration.
            gb_config (Optional[GBConfig], optional): Graph database configuration.
            tb_config (Optional[TBConfig], optional): Tbase configuration.
            do_init (bool, optional): Flag indicating if initialization is required.
            kb_root_path (str, optional): Path for storing knowledge base files (default is KB_ROOT_PATH).
        """
        super().__init__(
            vb_config or VBConfig(vb_type="LocalFaissHandler"), 
            db_config, gb_config, tb_config,
            embed_config
        )
        
        self.do_init = do_init
        self.kb_root_path = kb_root_path
        self.embed_config: Union[ModelConfig, EmbedConfig] = embed_config
        self.llm_config: Union[LLMConfig, ModelConfig] = llm_config

        # default
        self.session_index: str = "default"
        self.kb_name = f"{self.session_index}"
        self.uuid_file = os.path.join(
            self.kb_root_path, f"{self.session_index}/conversation.jsonl")

        self.recall_memory_dict: Dict[str, Memory] = {}
        self.memory_uuids = set()
        self.save_message_keys = [
            'session_index', 'message_index', 'role_name', 'role_type', 'content',
            'input_text', 'role_tags', 'content', 'step_content', 
            'parsed_content', 'spec_parsed_contents', 'global_kwargs', 
            'start_datetime', 'end_datetime', 
            "keyword", "vector"
        ]
        # init from config
        if isinstance(self.llm_config, LLMConfig):
            self.model = getChatModelFromConfig(self.llm_config)
        else:
            self.model = get_model(self.llm_config)
        self.init_handler()
        self.load(do_init)

    def clear_local(self, re_init: bool = False, handler_type: str = None):
        """Clear local memory and reinitialize if specified.

        Args:
            re_init (bool, optional): Whether to reinitialize after clearing.
            handler_type (str, optional): Type of handler to use (currently unused).
        """
        if self.vb: # 存到了本地需要清理
            self.vb.clear_vs_local()
            self.load(re_init)

    def append(self, message: Message, role_tag: str=None) -> None:
        """Append a message to the local memory and update vector store if necessary.

        Args:
            message (Message): The message to append.
            role_tag (str, optional): An optional role tag for the message.
        """
        # update the newest uuid_name
        self.check_uuid_name(message)
        datetimes = self.recall_memory_dict[self.session_index].get_datetimes()
        contents = self.recall_memory_dict[self.session_index].get_contents()
        message_indexes = self.recall_memory_dict[
            self.session_index].get_memory_values("message_index")
        # if message not in chat history, no need to update
        if message.message_index in message_indexes:
            self.update2vb(message, role_tag)
        elif ((message.end_datetime not in datetimes) or
            ((message.input_text not in contents) and (message.content not in contents))
        ):
            self.append2vb(message, role_tag)

    def append2vb(self, message: Message, role_tag: str=None) -> None:
        """Append a message and its embeddings to the vector store (VB).

        Args:
            message (Message): The message to append to the vector store.
            role_tag (str, optional): Optional role tag for the message.
        """
        if role_tag:
            if isinstance(message.role_tags, list):
                message.role_tags = list(set(message.role_tags + [role_tag]))
            else:
                message.role_tags += f", {role_tag}"
        self.recall_memory_dict[self.session_index].append(message)
        memory = self.recall_memory_dict[self.session_index]
        # 
        docs, json_messages = self.message_process([message])
        if self.embed_config:
            self.vb.add_docs(docs, kb_name=self.kb_name)
        # 
        if True: # resave the local
            _, json_messages = self.message_process(memory.messages)
            save_to_json_file(json_messages, self.uuid_file)


    def update2vb(self, message: Message, role_tag: str=None) -> None:
        """Update an existing message in the vector store.

        Args:
            message (Message): The message to update.
            role_tag (str, optional): Optional role tag for the message.
        """
        memory = self.recall_memory_dict[self.session_index]
        memory.update(message, role_tag)

        # 
        docs, json_messages = self.message_process([message])
        # if self.embed_config:
        #     # search
        #     # delete
        #     # add
        #     self.vb.add_docs(docs, kb_name=self.kb_name)
        # 
        if True: # resave the local
            _, json_messages = self.message_process(memory.messages)
            save_to_json_file(json_messages, self.uuid_file)


    def extend(self, memory: Memory, role_tag: str=None):
        """Append multiple messages from a Memory object to local memory.

        Args:
            memory (Memory): The Memory object containing messages to append.
            role_tag (str, optional): An optional role tag for messages.
        """
        for message in memory.messages:
            self.append(message, role_tag)

    def message_process(self, messages: List[Message]):
        """Convert message objects to vector store/local data format.

        Args:
            messages (List[Message]): List of messages to process.

        Returns:
            Tuple[List[Document], dict]: Tuple containing documents for vector storage and a JSON representation of messages.
        """
        messages = [{
                k: v for k, v in m.dict().items() 
                if k in self.save_message_keys
            }
            for m in messages
        ]
        docs = [{
            "page_content": m["step_content"] or m["content"] or m["input_text"], 
            "metadata": m} 
            for m in messages
        ]
        docs = [Document(**doc) for doc in docs]
        # convert messages to local data-format
        memory_messages = self.recall_memory_dict[self.session_index].dict()
        json_messages = {
            k: [
                {kkk: vvv for kkk, vvv in vv.items() 
                 if kkk in self.save_message_keys}
                for vv in v 
            ] 
            for k, v in memory_messages.items()
        }

        return docs, json_messages

    def load(self, re_init=False) -> Memory:
        """Load memory from files in the specified database root path.

        Args:
            re_init (bool, optional): Flag indicating if reinitialization of memory should occur.

        Returns:
            Memory: Loaded messages in memory format.
        """
        if not re_init:
            for root, dirs, files in os.walk(self.kb_root_path):
                for file in files:
                    if file != 'conversation.jsonl': continue
                    file_path = os.path.join(root, file)
                    # get uuid_name
                    relative_path = os.path.relpath(root, self.kb_root_path)
                    path_parts = relative_path.split(os.sep)
                    uuid_name = "_".join(path_parts)
                    # load to local cache
                    recall_memory = Memory(**read_json_file(file_path))
                    self.recall_memory_dict[uuid_name] = recall_memory
        else:
            self.recall_memory_dict = {}

    def get_memory_pool(self, session_index: str = "") -> Memory:
        """Retrieve the memory pool for a specific session index.

        Args:
            session_index (str, optional): Session index (default is empty string).

        Returns:
            Memory: Retrieved messages in memory format.
        """
        return self.recall_memory_dict.get(session_index, Memory(messages=[]))

    def embedding_retrieval(
            self, 
            text: str,
            top_k=1, 
            score_threshold=0.7, 
            session_index: str = "default", 
            **kwargs
        ) -> List[Message]:
        """Retrieve messages based on text embedding.

        Args:
            text (str): The input text for embedding retrieval.
            top_k (int, optional): The number of top results to retrieve (default is 1).
            score_threshold (float, optional): Minimum score for message retrieval (default is 0.7).
            session_index (str, optional): Session identifier (default is "default").

        Returns:
            Memory: Retrieved messages in memory format.
        """
        if text is None: return Memory(messages=[])

        # kb_name = self.get_vbname_from_sessionindex(session_index)
        kb_name = session_index
        docs = self.vb.search(
            text, 
            top_k=top_k, 
            score_threshold=score_threshold, 
            kb_name=kb_name
        )
        return Memory(messages=[Message(**doc.metadata) for doc, score in docs])
    
    def text_retrieval(
            self, 
            text: str, 
            session_index: str = "default", 
            **kwargs
        )  -> Memory:
        """Retrieve messages based on text content.

        Args:
            text (str): The text to match against messages.
            session_index (str, optional): Session identifier (default is "default").

        Returns:
            Memory: Messages matching the text content.
        """
        if text is None: return Memory(messages=[])

        # uuid_name = self.get_uuid_from_sessionindex(session_index)
        messages = self.recall_memory_dict.get(
            session_index, Memory(messages=[])).messages
        return self._text_retrieval_from_cache(
            messages, text, score_threshold=0.3, topK=5, **kwargs
        )

    def datetime_retrieval(
            self, 
            session_index: str, 
            datetime: str,
            text: str = None, 
            n: int = 5, 
            key: str = "start_datetime", 
            **kwargs
        ) -> Memory:
        """Retrieve messages based on date and time criteria.

        Args:
            session_index (str): The session index to filter messages.
            datetime (str): The datetime string reference for filtering.
            text (str, optional): Optional text to match with messages.
            n (int, optional): Number of minutes to define the range (default is 5).
            key (str, optional): The key for datetime filtering (default is "start_datetime").

        Returns:
            Memory: Retrieved messages in memory format.
        """
        if datetime is None: return Memory(messages=[])

        # uuid_name = self.get_uuid_from_sessionindex(session_index)
        messages = self.recall_memory_dict.get(
            session_index, Memory(messages=[])).messages
        return self._datetime_retrieval_from_cache(
            messages, datetime, text, n, **kwargs
        )
    
    def _text_retrieval_from_cache(
            self,
            messages: List[Message], 
            text: str = None, 
            score_threshold=0.3, 
            topK=5, 
            tag_topK=5, 
            **kwargs
        ) -> Memory:
        keywords = extract_tags(text, topK=tag_topK)

        matched_messages = []
        for message in messages:
            content = message.step_content or message.input_text or message.content
            message_keywords = extract_tags(content, topK=tag_topK)
            # calculate jaccard similarity
            intersection = Counter(keywords) & Counter(message_keywords)
            union = Counter(keywords) | Counter(message_keywords)
            similarity = sum(intersection.values()) / sum(union.values())
            if similarity >= score_threshold:
                matched_messages.append((message, similarity))
        matched_messages = sorted(matched_messages, key=lambda x:x[1])
        # return [m for m, s in matched_messages][:topK]  
        return Memory(messages=[m for m, s in matched_messages][:topK]  ) 
     
    def _datetime_retrieval_from_cache(
            self, 
            messages: List[Message], 
            datetime: str, 
            text: str = None, 
            n: int = 5, **kwargs
        ) -> Memory:
        # select message by datetime
        datetime_before, datetime_after = addMinutesToTimestamp(datetime, n)
        select_messages = [
            message for message in messages 
            if datetime_before<=dateformatToTimestamp(message.end_datetime, 1, message.datetime_format)<=datetime_after
        ]
        return self._text_retrieval_from_cache(select_messages, text)
    
    def recursive_summary(
            self, 
            messages: List[Message], 
            split_n: int = 20, 
            session_index: str=""
        ) -> Memory:
        """Generate a recursive summary of the provided messages.

        Args:
            messages (List[Message]): List of messages to summarize.
            split_n (int, optional): Number of messages to include in each summary pass (default is 20).
            session_index (str, optional): Session identifier for the summary.

        Returns:
            Memory: Updated messages including the summary.
        """
        if len(messages) == 0:
            return Memory(messages=[])
        
        newest_messages = messages[-split_n:]
        summary_messages = messages[:max(0, len(messages)-split_n)]
        
        while (len(newest_messages) != 0) and (newest_messages[0].role_type != "user"):
            message = newest_messages.pop(0)
            summary_messages.append(message)
        
        # summary
        summary_content = '\n\n'.join([
            m.role_type + "\n" + "\n".join(([f"*{k}* {v}" for parsed_output in m.spec_parsed_contents for k, v in parsed_output.items() if k not in ['Action Status']]))
            for m in summary_messages if m.role_type not in  ["summary"]
        ])
        
        summary_prompt = createSummaryPrompt(conversation=summary_content)
        content = self.model.predict(summary_prompt)
        summary_message = Message(
            session_index=session_index,
            role_name="summaryer",
            role_type="summary",
            content=content,
            step_content=content,
            spec_parsed_contents=[],
            global_kwargs={}
        )
        summary_message.spec_parsed_contents.append({"summary": content})
        newest_messages.insert(0, summary_message)
        
        return Memory(messages=newest_messages)

    def check_uuid_name(self, message: Message = None):
        if message.session_index != self.session_index:
            self.session_index = message.session_index
            # self.init_vb()

        self.kb_name = self.session_index
        self.uuid_file = os.path.join(self.kb_root_path, f"{self.session_index}/conversation.jsonl")

        self.memory_uuids.add(self.session_index)
        if self.session_index not in self.recall_memory_dict:
            self.recall_memory_dict[self.session_index] = Memory(messages=[])

    def modified_message(self, message: Message, update_rule_text: str) -> Message:
        # 创建提示语，在更新规则文本中包含当前消息的内容
        prompt = f"结合以下更新内容修改当前消息内容:\n更新内容: {update_rule_text}\n\n当前消息内容:\n{message.role_content}\n\n请生成新的消息内容:"

        new_content = self.model.predict(prompt)

        message.content = new_content

        return message