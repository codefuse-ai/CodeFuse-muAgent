from loguru import logger
from typing import List
from functools import lru_cache
import os, shutil

from langchain.embeddings.base import Embeddings
from langchain_community.docstore.document import Document

from muagent.utils.server_utils import torch_gc
from muagent.retrieval.base_service import SupportedVSType
from muagent.retrieval.faiss_m import FAISS
from muagent.llm_models.llm_config import EmbedConfig
from muagent.schemas.db import VBConfig
from muagent.retrieval.utils import load_embeddings_from_path

from muagent.base_configs.env_config import (
    KB_ROOT_PATH, FAISS_NORMALIZE_L2, SCORE_THRESHOLD
)



class LocalFaissHandler:

    def __init__(
            self,
            embed_config: EmbedConfig,
            vb_config: VBConfig = None
        ):

        self.vb_config = vb_config
        self.embed_config = embed_config
        self.embeddings = load_embeddings_from_path(
            self.embed_config.embed_model_path, 
            self.embed_config.model_device, 
            self.embed_config.langchain_embeddings
        )
        
        # INIT
        self.search_index: FAISS = None
        self.kb_name = "default"
        self.kb_root_path = vb_config.kb_root_path or KB_ROOT_PATH
        self.kb_path = "default"
        self.vs_path = "default"
        # DEFAULT
        self.distance_strategy = "EUCLIDEAN_DISTANCE"
        # init search_index
        self.create_vs()

    @lru_cache(1)
    def create_vs(self, kb_name: str = None):
        kb_name = kb_name or self.kb_name
        self.mkdir_vspath(kb_name, self.kb_root_path)
        if "index.faiss" in os.listdir(self.vs_path):
            self.load_vs_from_localdir(self.vs_path)
        else:
            self.create_empty_vs()

    def add_docs(
        self,
        docs: List[Document],
        kb_name: str = None,
        **kwargs,
    ):
        if kb_name:
            self.create_vs(kb_name)
        # 可能需要临时修改处理
        self.search_index.embedding_function = self.embeddings.embed_documents
        # logger.info("loaded docs, docs' lens is {}".format(len(docs)))
        self.search_index.add_documents(docs)
        torch_gc()
        self.search_index.save_local(self.vs_path)

    def clear_vs(self):
        if os.path.exists(self.kb_path):
            shutil.rmtree(self.kb_path)
        os.makedirs(self.kb_path)

    def clear_vs_local(self, kb_name: str = None):
        def _del(_path):
            if os.path.exists(_path):
                shutil.rmtree(_path)
            os.makedirs(_path)
            return True
        
        if kb_name:
            kb_path = LocalFaissHandler.get_kb_path(kb_name, self.kb_root_path)
            return _del(kb_path)
        
        for dir in os.listdir(self.kb_root_path):
            dir_path = os.path.join(self.kb_root_path, dir)
            if not os.path.isdir(dir_path): continue
            _del(dir_path)
        return True

    def search(
        self,
        query: str,
        top_k: int,
        score_threshold: float = SCORE_THRESHOLD,
        kb_name: str = None,
    ) -> List[Document]:
        
        if kb_name:
            self.create_vs(kb_name)
        
        docs = self.search_index.similarity_search_with_score(query, k=top_k, score_threshold=score_threshold)
        return docs
    
    def get_all_documents(self, kb_name: str = None):
        if kb_name:
            self.create_vs()
        return self.search_index.get_all_documents()
    
    # method for initing vs
    def create_empty_vs(self, ):
        doc = Document(page_content="init", metadata={})
        self.search_index = FAISS.from_documents([doc], self.embeddings, normalize_L2=FAISS_NORMALIZE_L2, distance_strategy=self.distance_strategy)
        ids = [k for k, v in self.search_index.docstore._dict.items()]
        self.search_index.delete(ids)

    def load_vs_from_localdir(self, vs_path):
        if "index.faiss" in os.listdir(vs_path):
            self.search_index = FAISS.load_local(vs_path, self.embeddings, normalize_L2=FAISS_NORMALIZE_L2, distance_strategy=self.distance_strategy)
        else:
            self.create_empty_vs()

    def mkdir_vspath(self, kb_name, kb_root_path):
        self.vs_path = LocalFaissHandler.get_vs_path(kb_name, kb_root_path)
        self.kb_path = LocalFaissHandler.get_kb_path(kb_name, kb_root_path)
        if not os.path.exists(self.vs_path):
            os.makedirs(self.vs_path)

    def vs_type(self) -> str:
        return SupportedVSType.FAISS

    @staticmethod
    def get_vs_path(kb_name: str, kb_root_path: str):
        return os.path.join(LocalFaissHandler.get_kb_path(kb_name, kb_root_path), "vector_store")

    @staticmethod
    def get_kb_path(kb_name: str, kb_root_path: str):
        return os.path.join(kb_root_path, kb_name)