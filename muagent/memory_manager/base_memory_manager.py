from abc import abstractmethod, ABC
from typing import (
    List, 
    Dict,
    Optional
)
from loguru import logger

from ..schemas import Memory, Message
from ..schemas.db import DBConfig, GBConfig, VBConfig, TBConfig
from ..schemas.models import ModelConfig
from ..db_handler import *

# from muagent.orm import table_init
from muagent.db_handler import table_init


class BaseMemoryManager(ABC):
    """
    This class represents a local memory manager that inherits from BaseMemoryManager.

    Attributes:
    - memory_type: A string representing the memory type. Default is "recall".
    - do_init: A boolean indicating whether to initialize. Default is False.
    - recall_memory: An instance of Memory class representing the recall memory.
    - save_message_keys: A list of strings representing the keys for saving messages.

    Methods:
    - __init__: Initializes the LocalMemoryManager with the given user_name, unique_name, memory_type, and do_init.
    - init_vb: Initializes the vb.
    - append: Appends a message to the recall memory, current memory, and summary memory.
    - extend: Extends the recall memory, current memory, and summary memory.
    - load: Loads the memory from the specified directory and returns a Memory instance.
    - router_retrieval: Routes the retrieval based on the retrieval type.
    - embedding_retrieval: Retrieves messages based on embedding.
    - text_retrieval: Retrieves messages based on text.
    - datetime_retrieval: Retrieves messages based on datetime.
    - recursive_summary: Performs recursive summarization of messages.
    """

    memory_manager_type: str = "base_memory_manager"
    """The type of memory manager"""

    def __init__(
            self,
            vb_config: Optional[VBConfig] = None,
            db_config: Optional[DBConfig] = None,
            gb_config: Optional[GBConfig] = None,
            tb_config: Optional[TBConfig] = None,
            embed_config: Optional[ModelConfig] = None,
            do_init: bool = False,
        ):
        """
        Initializes the LocalMemoryManager with the given parameters.

        Args:
        - embed_config: EmbedConfig, the embedding model config
        - llm_config: LLMConfig, the LLM model config
        - db_config: DBConfig, the Database config
        - vb_config: VBConfig, the vector base config
        - gb_config: GBConfig, the graph base config
        - do_init: A boolean indicating whether to initialize. Default is False.
        """
        self.db_config = db_config
        self.vb_config = vb_config
        self.gb_config = gb_config
        self.tb_config = tb_config
        self.embed_config = embed_config
        self.do_init = do_init
        self.recall_memory_dict: Dict[str, Memory] = {}
        self.save_message_keys = [
            'session_index', 'role_name', 'role_type', 'role_prompt', 'input_query',
            'datetime', 'role_content', 'step_content', 'parsed_output', 'spec_parsed_output', 'parsed_output_list', 
            'task', 'db_docs', 'code_docs', 'search_docs', 'phase_name', 'chain_name', 'customed_kargs']

    def init_handler(self, ):
        """Initializes Database VectorBase GraphDB TbaseDB"""
        self.init_vb()
        self.init_tb()
        self.init_db()
        self.init_gb()

    def reinit_handler(self, do_init: bool=False):
        self.init_vb()
        self.init_tb()
        self.init_db()
        self.init_gb()

    def init_vb(self, do_init: bool=None):
        """
        Initializes the vb.
        """
        if self.vb_config:
            table_init()
            vb_dict = {"LocalFaissHandler": LocalFaissHandler}
            vb_class =  vb_dict.get(self.vb_config.vb_type, LocalFaissHandler)
            self.vb: LocalFaissHandler = vb_class(self.embed_config, vb_config=self.vb_config)

    def init_db(self, ):
        """Initializes Database VectorBase GraphDB TbaseDB"""
        if self.db_config:
            db_dict = {"LocalFaissHandler": LocalFaissHandler}
            db_class =  db_dict.get(self.db_config.db_type)
            self.db = db_class(self.db_config)

    def init_tb(self, do_init: bool=None):
        """
        Initializes the tb.
        """
        if self.tb_config:
            tb_dict = {"TbaseHandler": TbaseHandler}
            tb_class =  tb_dict.get(self.tb_config.tb_type, TbaseHandler)
            self.tb = tb_class(self.tb_config, self.tb_config.index_name)

    def init_gb(self, do_init: bool=None):
        """
        Initializes the gb.
        """
        if self.gb_config:
            gb_dict = {"NebulaHandler": NebulaHandler}
            gb_class =  gb_dict.get(self.gb_config.gb_type, NebulaHandler)
            self.gb = gb_class(self.gb_config)

    def append(self, message: Message, role_tag: str):
        """
        Appends a message to the recall memory, current memory, and summary memory.

        Args:
        - message: An instance of Message class representing the message to be appended.
        """
        pass

    def extend(self, memory: Memory,  role_tag: str):
        """
        Extends the recall memory, current memory, and summary memory.

        Args:
        - memory: An instance of Memory class representing the memory to be extended.
        """
        pass

    def load(self, load_dir: str = "") -> Memory:
        """
        Loads the memory from the specified directory and returns a Memory instance.

        Args:
        - load_dir: A string representing the directory to load the memory from. Default is KB_ROOT_PATH.

        Returns:
        - An instance of Memory class representing the loaded memory.
        """
        pass

    def get_memory_pool(self, session_index: str) -> Memory:
        """
        return memory_pool
        """
        pass
    
    def search_messages(self, text: str=None, n=5, **kwargs) -> List[Message]:
        """
        return the search messages

        Args:
        - text: A string representing the text for retrieval. Default is None.
        - n: An integer representing the number of messages. Default is 5.
        """
    
    def router_retrieval(self, 
        session_index: str = "default", text: str=None, datetime: str = None, 
        n=5, top_k=5, retrieval_type: str = "embedding", **kwargs
    ) -> Memory:
        """
        Routes the retrieval based on the retrieval type.

        Args:
        - text: A string representing the text for retrieval. Default is None.
        - datetime: A string representing the datetime for retrieval. Default is None.
        - n: An integer representing the number of messages. Default is 5.
        - top_k: An integer representing the top k messages. Default is 5.
        - retrieval_type: A string representing the retrieval type. Default is "embedding".
        - **kwargs: Additional keyword arguments for retrieval.

        Returns:
        - A list of Message instances representing the retrieved messages.
        """
        retrieval_func_dict = {
            "embedding": self.embedding_retrieval, 
            "text": self.text_retrieval, 
            "datetime": self.datetime_retrieval
        }
        
        # 确保提供了合法的检索类型
        if retrieval_type not in retrieval_func_dict:
            raise ValueError(
                f"Invalid retrieval_type: '{retrieval_type}'. "
                f"Available types: {list(retrieval_func_dict.keys())}"
            )

        retrieval_func = retrieval_func_dict[retrieval_type]
        # 
        params = locals()
        params.pop("self")
        params.pop("retrieval_type")
        params.update(params.pop('kwargs', {}))
        # 
        return retrieval_func(**params)

    def embedding_retrieval(self, text: str, embed_model="", top_k=1, score_threshold=1.0, **kwargs) -> Memory:
        """
        Retrieves messages based on embedding.

        Args:
        - text: A string representing the text for retrieval.
        - embed_model: A string representing the embedding model. Default is EMBEDDING_MODEL.
        - top_k: An integer representing the top k messages. Default is 1.
        - score_threshold: A float representing the score threshold. Default is SCORE_THRESHOLD.
        - **kwargs: Additional keyword arguments for retrieval.

        Returns:
        - A list of Message instances representing the retrieved messages.
        """
        pass

    def text_retrieval(self, text: str, **kwargs) -> Memory:
        """
        Retrieves messages based on text.

        Args:
        - text: A string representing the text for retrieval.
        - **kwargs: Additional keyword arguments for retrieval.

        Returns:
        - A list of Message instances representing the retrieved messages.
        """
        pass

    def datetime_retrieval(self, datetime: str, text: str = None, n: int = 5, **kwargs)  -> Memory:
        """
        Retrieves messages based on datetime.

        Args:
        - datetime: A string representing the datetime for retrieval.
        - text: A string representing the text for retrieval. Default is None.
        - n: An integer representing the number of messages. Default is 5.
        - **kwargs: Additional keyword arguments for retrieval.

        Returns:
        - A list of Message instances representing the retrieved messages.
        """
        pass

    def recursive_summary(self, messages: List[Message], split_n: int = 20)  -> Memory:
        """
        Performs recursive summarization of messages.

        Args:
        - messages: A list of Message instances representing the messages to be summarized.
        - split_n: An integer representing the split n. Default is 20.

        Returns:
        - A list of Message instances representing the summarized messages.
        """
        pass

    def reranker(self, ):
        """
        rerank the retrieval message from memory
        """
        pass

