

## flow 编排
下面从代码层面介绍，用muagent来进行flow编排

### 自定义LLM&Embedding组件
```
from langchain.llms.base import BaseLLM, LLM
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.schema import Document
from langchain.embeddings.base import Embeddings

class BgeBaseChineseEmbeddings(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute query embeddings using a HuggingFace transformer model.

        Args:
            text: The texts to embed.

        Returns:
            Embeddings for the texts.
        """
        pass

    def embed_query(self, text: str) -> List[float]:
        """Compute query embeddings using a HuggingFace transformer model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        pass



# 自定义LLM模块，复用 langchain 类
class ReadingModel(LLM):
        repetition_penalty = 1.1
        temperature = 0.2
        top_k = 40
        top_p = 0.9

        @property
        def _llm_type(self) -> str:
            return "ReadingModel"

        def predict(self, prompt: str, stop: Optional[List[str]] = None) -> str:
            return self._call(prompt, stop)

        # def batch(self, prompts: str, stop: Optional[List[str]] = None) -> List[str]:
        #     return [self._call(prompt, stop) for prompt in prompts]

        def _call(self, prompt: str,
                  stop: Optional[List[str]] = None) -> str:
            """_call
            将prompt 经过 llm 得到 文本输出
            """
            pass

```


### LLM Embedding Config
配置llm和embedding
```
import os, sys
from loguru import logger

# set your config
api_key = ""
api_base_url= ""
model_name = ""
embed_model = ""
embed_model_path = ""
logger.error(f"{e}")


from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.codechat.codebase_handler.codebase_handler import CodeBaseHandler
from muagent.base_configs.env_config import CB_ROOT_PATH

llm_config = LLMConfig(
    model_name=model_name, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)
# define your customized llm
# llm_config = LLMConfig(llm=ReadingModel())

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)
# define your customized embeddings
# embeddings = BgeBaseChineseEmbeddings()
# embed_config = EmbedConfig(langchain_embeddings=embeddings)
```


### 代码库注册
如何利用muagent组建构建代码库
```
# delete codebase
codebase_name = 'client_local'
code_path = "D://chromeDownloads/devopschat-bot/client_v2/client"
use_nh = True
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.delete_codebase(codebase_name=codebase_name)


# initialize codebase
codebase_name = 'client_local'
code_path = "D://chromeDownloads/devopschat-bot/client_v2/client"
use_nh = True
do_interpret = True
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.import_code(do_interpret=do_interpret)
```

### flow 编排
```
from muagent.connector.antflow import AgentFlow, ChainFlow, PhaseFlow
from muagent.connector.configs.prompts import QA_TEMPLATE_PROMPT
from muagent.connector.configs import BASE_PROMPT_CONFIGS
from muagent.retrieval.base_retrieval import BaseCodeRetrieval
import os

agent_flow1 = AgentFlow(
    agent_type="BaseAgent", 
    agent_index=0,
    chat_turn=1,
    role_type = "assistant",
    role_name = "qaer",
    role_prompt = QA_TEMPLATE_PROMPT,
    prompt_config = BASE_PROMPT_CONFIGS,
    focus_agents = [],
    focus_messages = [],
    embed_config= embed_config,
    llm_config = llm_config,
    )

chain_flow1 = ChainFlow(
    chain_name="qaer",
    chain_index=0,
    agent_flows=[agent_flow1],
    chat_turn = 1,
    do_checker = False,
    embed_config= embed_config,
    llm_config = llm_config,
    )


# 注册 代码库 retrieval
codebase_name = 'client_local'
retrieval = BaseCodeRetrieval(
    codebase_name, embed_config=embed_config, llm_config=llm_config, 
    search_type = 'tag', code_limit = 1, local_graph_path=CB_ROOT_PATH)


# log-level，print prompt和llm predict
os.environ["log_verbose"] = "1"


phase_name = "code_qa_chain"
phase_flow = PhaseFlow(
    phase_name=phase_name, chain_flows=[chain_flow1,],
    embed_config= embed_config,
    llm_config = llm_config,
    code_retrieval=retrieval,
)
```


### 开始代码库问答

```
query_content = "remove 这个函数是做什么的"
query_content = {"query": "remove 这个函数是做什么的", "search_type": "tag"}
phase_flow(query_content)
```