import time, sys
import os
import yaml
import requests 
from typing import List
from loguru import logger
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)

try:
    import os, sys
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
except Exception as e:
    # set your config
    logger.error(f"{e}")

from muagent.schemas.db import *
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.service.ekg_construct.ekg_construct_base import EKGConstructService

from pydantic import BaseModel

# llm config
class CustomLLM(LLM, BaseModel):
    url: str = "http://localhost:11434/api/generate"
    model_name: str = "qwen2:1b"
    model_type: str = "ollama"
    api_key: str = ""
    stop: str = None
    temperature: float = 0.3
    top_k: int = 50
    top_p: float = 0.95

    def params(self):
        keys = ["url", "model_name", "model_type", "api_key", "stop", "temperature", "top_k", "top_p"]
        return {
            k:v
            for k,v in self.__dict__.items() 
            if k in keys}
    
    def update_params(self, **kwargs):
        # 更新属性
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _llm_type(self, *args):
        return ""

    def predict(self, prompt: str, stop = None) -> str:
        return self._call(prompt, stop)

    def _call(self, prompt: str,
              stop = None) -> str:
        """_call
        """
        return_str = ""
        stop = stop or self.stop

        if self.model_type == "ollama":
            data = {
                "model": self.model_name,
                "prompt": prompt
            }
            r = requests.post(self.url, json=data, )
            return r.json()
        elif self.model_type == "openai":
            from muagent.llm_models.openai_model import getChatModelFromConfig
            llm_config = LLMConfig(
                model_name=self.model_name,
                model_engine="openai",
                api_key=self.api_key,
                api_base_url=self.url,
                temperature=self.temperature,
                stop=self.stop
            )
            model = getChatModelFromConfig(llm_config)
            return model.predict(prompt, stop=self.stop)
        elif self.model_type == "lingyiwangwu":
            from muagent.llm_models.openai_model import getChatModelFromConfig
            llm_config = LLMConfig(
                model_name=self.model_name,
                model_engine="lingyiwangwu",
                api_key=self.api_key,
                api_base_url=self.url,
                temperature=self.temperature,
                stop=self.stop
            )
            model = getChatModelFromConfig(llm_config)
            return model.predict(prompt, stop=self.stop)
        else:
            pass

        return return_str


class CustomEmbeddings(Embeddings):
    # ollama embeddings
    url = "http://localhost:11434/api/embeddings"
    # 
    embedding_type = "ollama"
    model_name = ""
    api_key = ""

    def params(self):
        return {
            "url": self.url, "model_name": self.model_name, 
            "embedding_type": self.embedding_type, "api_key": self.api_key
        }

    def update_params(self, **kwargs):
        # 更新属性
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _get_sentence_emb(self, sentence: str) -> dict:
        """
        调用句子向量提取服务
        """
        if self.embedding_type == "ollama":
            data = {
                "model": self.model_name,
                "prompt": sentence
            }
            r = requests.post(self.url, json=data, )
            return r.json()
        elif self.embedding_type == "openai":
            from muagent.llm_models.get_embedding import get_embedding
            os.environ["OPENAI_API_KEY"] = self.api_key
            os.environ["API_BASE_URL"] = self.url
            embed_config = EmbedConfig(
                embed_engine="openai",
                api_key=self.api_key,
                api_base_url=self.url,
            )
            text2vector_dict = get_embedding("openai", [sentence], embed_config=embed_config)
            return text2vector_dict[sentence]
        else:
            pass

        return []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []

        def process_text(text):
            # print("分句：" + str(text) + "\n")
            emb_str = self._get_sentence_emb(text)
            # print("向量：" + str(emb_str) + "\n")
            return emb_str

        with ThreadPoolExecutor() as executor:
            results = list(tqdm(executor.map(process_text, texts), total=len(texts), desc="Embedding documents"))

        embeddings.extend(results)
        print("向量个数" + str(len(embeddings)))
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Compute query embeddings using a HuggingFace transformer model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        logger.info("提问query: " + str(text))
        embedding = self._get_sentence_emb(text)
        logger.info("提问向量:" + str(embedding))
        return embedding
    


cur_dir = os.path.dirname(__file__)
print(cur_dir)

# 要打开的YAML文件路径
file_path = 'ekg.yaml'

# 使用 'with' 语句确保文件正确关闭
with open(os.path.join(cur_dir, file_path), 'r') as file:
    # 加载YAML文件内容
    config_data = yaml.safe_load(file)



# gb_config = GBConfig(
#     gb_type="GeaBaseHandler", 
#     extra_kwargs={
#         'metaserver_address': config_data["gbase_config"]['metaserver_address'],
#         'project': config_data["gbase_config"]['project'],
#         'city': config_data["gbase_config"]['city'],
#         'lib_path': config_data["gbase_config"]['lib_path'],
#     }
# )


# gb_config = GBConfig(
#     gb_type="NebulaHandler", 
#     extra_kwargs={}
# )

# 初始化 NebulaHandler 实例
gb_config = GBConfig(
    gb_type="NebulaHandler", 
    extra_kwargs={
        'host': config_data["nebula_config"]['host'],
        'port': config_data["nebula_config"]['port'],
        'username': config_data["nebula_config"]['username'] ,
        'password': config_data["nebula_config"]['password'],
        "space": config_data["nebula_config"]['space_name'],    
    }
)

# 初始化 TbaseHandler 实例
tb_config = TBConfig(
    tb_type="TbaseHandler",
    index_name="muagent_test",
    host=config_data["tbase_config"]["host"],
    port=config_data["tbase_config"]['port'],
    username=config_data["tbase_config"]['username'],
    password=config_data["tbase_config"]['password'],
    extra_kwargs={
        'host': config_data["tbase_config"]['host'],
        'port': config_data["tbase_config"]['port'],
        'username': config_data["tbase_config"]['username'] ,
        'password': config_data["tbase_config"]['password'],
        'definition_value': config_data["tbase_config"]['definition_value']
    }
)

llm = CustomLLM()
llm_config = LLMConfig(
    llm=llm
)


embeddings = CustomEmbeddings()
# embed_config = EmbedConfig(
#     embed_model="default",
#     langchain_embeddings=embeddings
# )
embed_config = None


ekg_construct_service = EKGConstructService(
    embed_config=embed_config,
    llm_config=llm_config,
    tb_config=tb_config,
    gb_config=gb_config,
)

from muagent.httpapis.ekg_construct import create_api
create_api(llm, embeddings, ekg_construct_service)