from typing import (
    List,
    Union,
    Optional,
)
import numpy as np
from jieba.analyse import extract_tags
import random
from collections import Counter
from loguru import logger
import json

from .base_memory_manager import BaseMemoryManager

from ..schemas import Memory, Message
from ..schemas.models import ModelConfig
from ..schemas.db import DBConfig, GBConfig, VBConfig, TBConfig

from ..db_handler import *
from ..models import get_model


from muagent.llm_models import getChatModelFromConfig
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.connector.configs.generate_prompt import *
from muagent.utils.common_utils import *

from muagent.llm_models.get_embedding import get_embedding
from redis.commands.search.field import (
    TextField,
    NumericField,
    VectorField,
    TagField
)

DIM = 768
MESSAGE_SCHEMA = [
    TextField("session_index", ),
    TextField("message_index", ),
    TextField("node_index"),
    TextField("role_name",),
    TextField("role_type", ),
    TextField('input_text'),
    TextField("content", ),
    TextField("role_tags"),
    TextField("parsed_output"),
    TextField("global_kwargs",),
    NumericField("start_datetime",) ,   
    NumericField("end_datetime",),
    VectorField("vector",
                'FLAT',
                {
                    "TYPE": "FLOAT32",
                    "DIM": DIM,
                    "DISTANCE_METRIC": "COSINE"
                }),
    TagField(name='keyword', separator='|')
]



class TbaseMemoryManager(BaseMemoryManager):
    """
    This class represents a TbaseMemoryManager that inherits from BaseMemoryManager.
    """

    memory_manager_typy = "tbase_memory_manager"
    """The type of memory manager for identification purposes."""

    def __init__(
            self,
            embed_config: Union[ModelConfig, EmbedConfig],
            llm_config: Union[LLMConfig, ModelConfig],
            tbase_handler: TbaseHandler = None,
            use_vector: bool = False,
            vb_config: Optional[VBConfig] = None,
            db_config: Optional[DBConfig] = None,
            gb_config: Optional[GBConfig] = None,
            tb_config: Optional[TBConfig] = None,
            do_init: bool = False,
        ):
        """Initialize the TbaseMemoryManager with specified configurations.

        Args:
            embed_config (Union[ModelConfig, EmbedConfig]): Configuration for embedding.
            llm_config (Union[LLMConfig, ModelConfig]): Configuration for the LLM.
            tbase_handler (TbaseHandler, optional): Handler for Tbase database access.
            use_vector (bool, optional): Flag to specify whether to use vector embeddings.
            vb_config (Optional[VBConfig], optional): Configuration for the vector database.
            db_config (Optional[DBConfig], optional): Configuration for the main database.
            gb_config (Optional[GBConfig], optional): Configuration for graph database.
            tb_config (Optional[TBConfig], optional): Configuration for Tbase.
            do_init (bool, optional): Flag to indicate if initialization is required.
        """
        
        super().__init__(vb_config, db_config, gb_config, tb_config)
        self.do_init = do_init
        self.embed_config: Union[ModelConfig, EmbedConfig] = embed_config
        self.llm_config: Union[LLMConfig, ModelConfig] = llm_config
        self.tb: TbaseHandler = tbase_handler
        self.save_message_keys = [
            'session_index', 'message_index', 'node_index', 'role_name', 'role_type', 'content',
            'input_text', 'role_tags', 'content', 'step_content', 
            'parsed_content', 'spec_parsed_contents', 'global_kwargs', 
            'start_datetime', 'end_datetime', 
            "keyword", "vector"
        ]
        self.use_vector = use_vector
        self.init_handler()
        self.init_tb_index()

    def init_tb_index(self, do_init: bool=None):
        """Initialize the Tbase index if it does not already exist.

        Args:
            do_init (bool, optional): Optional flag for initialization (unused here).
        """
        # Create index if it does not exist
        if not self.tb.is_index_exists():
            res = self.tb.create_index(schema=MESSAGE_SCHEMA)
            logger.info(res)

    def append(self, message: Message, role_tag: str=None) -> None:
        """Append a message to the Tbase memory.

        Args:
            message (Message): The message to be appended.
            role_tag (str, optional): Optional role tag for the message.
        """
        tbase_message = self.localMessage2TbaseMessage(message, role_tag)  # Convert local message to Tbase format
        self.tb.insert_data_hash(tbase_message)  # Insert into Tbase

    def extend(self, memory: Memory, role_tag: str=None) -> None:
        """Append multiple messages from memory to Tbase.

        Args:
            memory (Memory): The memory containing messages to append.
            role_tag (str, optional): Optional role tag for all messages.
        """
        for message in memory.messages:
            self.append(message, role_tag)  # Append each message

    def append_tools(self, tool_information: dict, session_index: str, nodeid: str, node_index: str="default") -> None:
        """Append tool-related information to Tbase as messages.

        Args:
            tool_information (dict): Dictionary containing tool information.
            session_index (str): Session identifier.
            nodeid (str): Graph node ID.
            node_index (str, optional): Node index for differentiating nodes.
        """
        tool_map = {
             "toolKey": {"role_name": "tool_selector", "role_type": "assistant", 
                         "customed_keys": ["toolDef"]
                         }, 
             "toolParam": {"role_name": "tool_filler", "role_type": "assistant"}, 
             "toolResponse": {"role_name": "function_caller", "role_type": "observation"}, 
             "toolSummary": {"role_name": "function_summary", "role_type": "Summary"}, 
        }

        for k, v in tool_map.items():
            try:
                message = Message(
                    session_index=session_index,
                    message_index= f"{nodeid}_{k}",
                    node_index=node_index,
                    role_name = v["role_name"],  # Assign role name
                    role_type = v["role_type"],  # Assign role type
                    content = tool_information[k],  # Assign tool information content
                    global_kwargs = {
                        **{kk: vv for kk, vv in tool_information.items() 
                            if kk in v.get("customed_keys", [])}
                    }  # Store additional tool information
                )
            except:
                pass
            self.append(message)  # Append the message to Tbase


    def get_memory_by_sessionindex_tags(self, session_index: str, tags: List[str], limit: int = 10) -> Memory:
        """Retrieve memory messages by session index and tags.

        Args:
            session_index (str): The session index to search for.
            tags (List[str]): List of tags to match against messages.
            limit (int, optional): The maximum number of messages to retrieve (default is 10).

        Returns:
            Memory: Retrieved messages in memory format.
        """
        tags_str = '|'.join([f"*{tag}*" for tag in tags])  # Create a tags search string
        querys = [
            f"@session_index:{session_index}",  # Query for session index
            f"@role_tags:{tags_str}",  # Query for role tags
        ]
        query = f"({')('.join(querys)})" if len(querys) >=2 else "".join(querys)  # Combine queries
        r = self.tb.search(query, limit=limit)  # Search Tbase
        return self.tbasedoc2Memory(r)  # Convert results to Memory format
    
    def get_memory_by_chatindex_tags(self, chat_index: str, tags: List[str], limit: int = 10) -> Memory:
        """Retrieve memory messages by chat index and tags.

        Args:
            chat_index (str): The chat index to search for.
            tags (List[str]): List of tags to match against messages.
            limit (int, optional): The maximum number of messages to retrieve (default is 10).

        Returns:
            Memory: Retrieved messages in memory format.
        """
        tags_str = '|'.join([f"*{tag}*" for tag in tags])  # Create a tags search string
        querys = [
            f"@session_index:{chat_index}",  # Query for session index
            f"@role_tags:{tags_str}",  # Query for role tags
        ]
        query = f"({')('.join(querys)})" if len(querys) >=2 else "".join(querys)  # Combine queries
        logger.debug(f"{query}")
        r = self.tb.search(query, limit=limit)  # Search Tbase
        return self.tbasedoc2Memory(r)  # Convert results to Memory format

    def get_memory_pool(self, session_index: str = "") -> Memory:
        """Get the memory pool for a specific session index.

        Args:
            session_index (str, optional): Session index (default is empty string).

        Returns:
            Memory: Retrieved messages in memory format.
        """
        return self.get_memory_pool_by_all({"session_index": session_index})  # Retrieve all memory for session

    def get_memory_pool_by_content(self, content: str) -> Memory:
        """Get memory pool based on content search.

        Args:
            content (str): Content to search for in messages.

        Returns:
            Memory: Retrieved messages in memory format.
        """
        r = self.tb.search(content)  # Search Tbase
        return self.tbasedoc2Memory(r)  # Convert results to Memory format

    def get_memory_pool_by_key_content(self, key: str, content: str) -> Memory:
        """Get memory pool based on key and content search.

        Args:
            key (str): Key to search for in messages.
            content (str): Content to search for in messages.

        Returns:
            Memory: Retrieved messages in memory format.
        """
        if key == "keyword":
            query = f"@{key}:{{{content}}}"  # Special handling for keywords
        else:
            query = f"@{key}:{content}"  # General query
        r = self.tb.search(query)  # Search Tbase
        return self.tbasedoc2Memory(r)  # Convert results to Memory format

    def get_memory_pool_by_all(self, search_key_contents: dict, limit: int =10) -> Memory:
        """Get memory pool based on multiple search criteria.

        Args:
            search_key_contents (dict): Dictionary containing key-value pairs for searching messages.
            limit (int, optional): The maximum number of messages to retrieve (default is 10).

        Returns:
            Memory: Retrieved messages in memory format.
        """
        querys = []
        for k, v in search_key_contents.items():
            if not v: continue
            if k == "keyword":
                querys.append(f"@{k}:{{{v}}}")
            elif k == "role_tags":
                tags_str = '|'.join([f"*{tag}*" for tag in v]) if isinstance(v, list) else f"{v}"
                querys.append(f"@role_tags:{tags_str}")
            elif k == "start_datetime":
                query = f"(@start_datetime:[{v[0]} {v[1]}])"
                querys.append(query)
            elif k == "end_datetime":
                query = f"(@end_datetime:[{v[0]} {v[1]}])"
                querys.append(query)
            else:
                querys.append(f"@{k}:{v}")
        
        query = f"({')('.join(querys)})" if len(querys) >=2 else "".join(querys)
        r = self.tb.search(query, limit=limit)
        return self.tbasedoc2Memory(r)
        
    def embedding_retrieval(self, text: str, top_k=1, score_threshold=1.0, session_index: str = "default", **kwargs) -> Memory:
        """Retrieve memory using vector embeddings based on input text.

        Args:
            text (str): The input text for which embeddings are generated.
            top_k (int, optional): Number of top results to retrieve (default is 1).
            score_threshold (float, optional): Minimum score for fetching results (default is 1.0).
            session_index (str, optional): Session identifier (default is "default").

        Returns:
            Memory: Retrieved messages in memory format.
        """
        if text is None: return Memory(messages=[])
        if not self.use_vector and self.embed_config:
            logger.error(f"can't use vector search, because the use_vector is {self.use_vector}")
            return Memory(messages=[])
        
        if self.use_vector and self.embed_config:
            query_embedding = self._get_embedding_array(text)
        
        base_query = f'(@session_index:{session_index})=>[KNN {top_k} @vector $vector AS distance]'
        query_params = {"vector": query_embedding}
        r = self.tb.vector_search(base_query, query_params=query_params)
        return self.tbasedoc2Memory(r)
    
    def text_retrieval(self, text: str, session_index: str = "default", **kwargs)  -> Memory:
        """Retrieve messages based on text content and session index.

        Args:
            text (str): The text to search for.
            session_index (str, optional): Session identifier (default is "default").

        Returns:
            Memory: Retrieved messages in memory format.
        """
        keywords = extract_tags(text, topK=-1)
        if len(keywords) > 0:
            keyword = "|".join(keywords)
            query = f"(@session_index:{session_index})(@keyword:{{{keyword}}})"
        else:
            query = f"@session_index:{session_index}"
        # logger.debug(f"text_retrieval query: {query}")
        r = self.tb.search(query)
        memory = self.tbasedoc2Memory(r)
        return self._text_retrieval_from_cache(memory.messages, text)

    def datetime_retrieval(
            self, 
            session_index: str, 
            datetime: str, 
            text: str = None, 
            n: int = 5, 
            key: str = "start_datetime", 
            **kwargs
        ) -> Memory:
        """Retrieve messages based on datetime range and session index.

        Args:
            session_index (str): The session index to filter messages.
            datetime (str): The timestamp used for filtering messages.
            text (str, optional): Optional text to retrieve alongside datetime.
            n (int, optional): Number of minutes to define the range (default is 5).
            key (str, optional): The key for datetime filtering (default is "start_datetime").

        Returns:
            Memory: Retrieved messages in memory format.
        """

        intput_timestamp = None
        for datetime_format in ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]:
            try:
                intput_timestamp = dateformatToTimestamp(datetime, 1000, datetime_format)
                break
            except:
                pass
        if intput_timestamp is None: 
            raise ValueError(f"can't transform datetime into [%Y-%m-%d %H:%M:%S.%f, %Y-%m-%d %H:%M:%S]")

        query = f"(@session_index:{session_index})(@{key}:[{intput_timestamp-n*60*1000} {intput_timestamp+n*60*1000}])"
        # logger.debug(f"datetime_retrieval query: {query}")
        r = self.tb.search(query)
        memory = self.tbasedoc2Memory(r)
        return self._text_retrieval_from_cache(memory.messages, text)
        
    def _text_retrieval_from_cache(
            self, 
            messages: List[Message], 
            text: str = None, 
            score_threshold=0.3, 
            topK=5, 
            tag_topK=5, 
            **kwargs
        ) -> Memory:
        """Retrieve messages based on text similarity from cached messages."""

        if text is None:
            return Memory(messages=messages[:topK])

        if len(messages) < topK:
            return Memory(messages=messages)
        
        keywords = extract_tags(text, topK=tag_topK)

        matched_messages = []
        for message in messages:
            message_keywords = extract_tags(
                message.step_content or message.content or message.input_text, 
                topK=tag_topK
            )
            # calculate jaccard similarity
            intersection = Counter(keywords) & Counter(message_keywords)
            union = Counter(keywords) | Counter(message_keywords)
            similarity = sum(intersection.values()) / sum(union.values())
            if similarity >= score_threshold:
                matched_messages.append((message, similarity))
        matched_messages = sorted(matched_messages, key=lambda x:x[1])
        return Memory(messages=[m for m, s in matched_messages][:topK])
    
    def recursive_summary(
            self, 
            messages: List[Message], 
            session_index: str, 
            split_n: int = 20
        ) -> Memory:
        """Generate a recursive summary of the provided messages.

        Args:
            messages (List[Message]): List of messages to summarize.
            session_index (str): Session identifier for the summary.
            split_n (int, optional): Number of messages to include in each summary pass (default is 20).

        Returns:
            Memory: Updated messages including the summary.
        """

        if len(messages) == 0:
            return Memory(messages=messages)
        
        newest_messages = messages[-split_n:]
        summary_messages = messages[:len(messages)-split_n]
        
        while (len(newest_messages) != 0) and (newest_messages[0].role_type != "user"):
            message = newest_messages.pop(0)
            summary_messages.append(message)
        
        # summary
        model = self._get_model()
        summary_content = '\n\n'.join([
            m.role_type + "\n" + "\n".join(([f"*{k}* {v}" for parsed_output in m.spec_parsed_contents for k, v in parsed_output.items() if k not in ['Action Status']]))
            for m in summary_messages if m.role_type not in  ["summary"]
        ])
        # summary_prompt = CONV_SUMMARY_PROMPT_SPEC.format(conversation=summary_content)
        summary_prompt = createSummaryPrompt(conversation=summary_content)
        logger.debug(f"{summary_prompt}")
        content = model.predict(summary_prompt)
        summary_message = Message(
            session_index=session_index,
            role_name="summaryer",
            role_type="summary",
            content=content,
            step_content=content,
            parsed_output_list=[],
            global_kwargs={}
        )
        summary_message.spec_parsed_contents.append({"summary": content})
        newest_messages.insert(0, summary_message)
        return Memory(messages=newest_messages)

    def localMessage2TbaseMessage(self, message: Message, role_tag: str= None):
        """Convert a local Message object to a format suitable for Tbase storage."""

        r = self.tb.search(f"@message_index: {message.message_index}")
        history_role_tags = json.loads(r.docs[0].role_tags) if r.total == 1 else []

        tbase_message = {}
        for k, v in message.dict().items():
            v = list(set(history_role_tags+[role_tag])) if k=="role_tags" and role_tag else v
            if isinstance(v, dict) or isinstance(v, list):
                v = json.dumps(v, ensure_ascii=False)
            tbase_message[k] = v

        tbase_message["start_datetime"] = dateformatToTimestamp(message.start_datetime, 1000, "%Y-%m-%d %H:%M:%S.%f")
        tbase_message["end_datetime"] = dateformatToTimestamp(message.end_datetime, 1000, "%Y-%m-%d %H:%M:%S.%f")

        if self.use_vector and self.embed_config:
            tbase_message["vector"] = self._get_embedding_array(message.content)
        tbase_message["keyword"] = " | ".join(extract_tags(message.content, topK=-1) 
                                                + [tbase_message["message_index"].split("-")[0]])

        tbase_message = {
            k: v for k, v in tbase_message.items()
            if k in self.save_message_keys
        }
        return tbase_message

    def tbasedoc2Memory(self, r_docs) -> Memory:
        """Convert Tbase documents back into Memory objects."""

        memory = Memory()
        for doc in r_docs.docs:
            tbase_message = {}
            for k, v in doc.__dict__.items():
                if k in ["content", "input_text"]:
                    tbase_message[k] = v
                    continue
                try:
                    v = json.loads(v)
                except:
                    pass

                tbase_message[k] = v

            message = Message(**tbase_message)
            memory.append(message)

        for message in memory.messages:
            message.start_datetime = timestampToDateformat(int(message.start_datetime), 1000, "%Y-%m-%d %H:%M:%S.%f")
            message.end_datetime = timestampToDateformat(int(message.end_datetime), 1000, "%Y-%m-%d %H:%M:%S.%f")

        memory.sort_by_key("end_datetime")
        return memory
    

    def init_global_msg(self, session_index: str, role_name: str, content: str, role_type: str = "global_value") -> bool:
        """Initialize a global message and append it to the memory.

        Args:
            session_index (str): The session index to which the message belongs.
            role_name (str): The role name for the message.
            content (str): The content of the message.
            role_type (str, optional): The role type of the message (default is "global_value").

        Returns:
            bool: True if the message was initialized successfully; otherwise, False.
        """

        msg = Message(session_index=session_index, message_index = role_name ,role_name=role_name, role_type=role_type, content=content)
        try:
            self.append(msg)
            return True  
        except Exception as e:
            logger.error(f"Failed to initialize global message: {e}")
            return False
    
    def get_msg_by_role_name(self, session_index: str, role_name: str) -> Optional[Message]:
        """Retrieve a message by its role name within a session.

        Args:
            session_index (str): The session index to search within.
            role_name (str): The role name of the desired message.

        Returns:
            Optional[Message]: The found message, or None if not found.
        """

        memory = self.get_memory_pool_by_all({"session_index": session_index, "role_name": role_name})
        # memory = self.get_memory_pool(session_index)
        for msg in memory.messages:
            if msg.role_name == role_name:
                return msg
        return None
    
    def get_msg_content_by_role_name(self, session_index: str, role_name: str) -> Optional[str]:
        """Retrieve the content of a message by its role name.

        Args:
            session_index (str): The session index to search within.
            role_name (str): The role name of the desired message.

        Returns:
            Optional[str]: The content of the found message, or None if not found.
        """

        message = self.get_msg_by_role_name(session_index, role_name)
        if message == None:
            return None
        else:
            return message.content
        
    def update_msg_content_by_rule(self, session_index: str, role_name: str, new_content: str,update_rule: str) -> bool:
        """Update the content of a message based on an update rule.

        Args:
            session_index (str): The session index to search within.
            role_name (str): The role name of the message to update.
            new_content (str): The new content to apply.
            update_rule (str): The rule to apply for the update.

        Returns:
            bool: True if the message was successfully updated; otherwise, False.
        """

        message = self.get_msg_by_role_name(session_index, role_name)
        
        if message == None:
            return False 

        prompt = f"{new_content}\n{role_name}:{message.content}\n{update_rule}"
        model = self._get_model()

        new_content = model.predict(prompt)

        if new_content is not None:
            message.content = new_content  
            self.append(message)
            return True
        else:
            return False
        
    def _get_embedding(self, text) -> Dict[str, List[float]]:
        text_vector = {}
        if self.embed_config and text:
            if isinstance(self.embed_config, ModelConfig):
                self.emebd_model = get_model(self.embed_config)
                vector = self.emebd_model.embed_query(text)
                text_vector = {text: vector}
            else:
                text_vector = get_embedding(
                    self.embed_config.embed_engine, [text],
                    self.embed_config.embed_model_path, self.embed_config.model_device,
                    self.embed_config
                )
        else:
            text_vector = {text: [random.random() for _ in range(768)]}
        return text_vector

    def _get_embedding_array(self, text) -> Dict[str, List[bytes]]:
        text_vector = self._get_embedding(text)
        return np.array(text_vector[text]).\
                    astype(dtype=np.float32).tobytes()
    
    def _get_model(self, ):
        if isinstance(self.llm_config, LLMConfig):
            model = getChatModelFromConfig(self.llm_config)
        else:
            model = get_model(self.llm_config)
        return model