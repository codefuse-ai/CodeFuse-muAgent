

## 如何注册个性化的retrieval模块

基础模型配置

```
import os, sys, json
from loguru import logger

# set your config
api_key = ""
api_base_url= ""
model_name = ""
embed_model = ""
embed_model_path = ""
```


<br>注册语言模型和向量模型
```
from muagent.base_configs.env_config import KB_ROOT_PATH
from muagent.tools import toLangchainTools, TOOL_DICT, TOOL_SETS
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.connector.phase import BasePhase
from muagent.connector.schema import Message, Memory
from muagent.retrieval.base_retrieval import IMRertrieval

# 
llm_config = LLMConfig(
    model_name=model_name, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)

```


<br>注册个性化的知识库检索器
```
# retrieval your customized register demo
from muagent.tools import DocRetrieval
class BaseDocRetrieval(IMRertrieval):

    def __init__(self, knowledge_base_name: str, search_top=5, score_threshold=1.0, embed_config: EmbedConfig=EmbedConfig(), kb_root_path: str=KB_ROOT_PATH):
        self.knowledge_base_name = knowledge_base_name
        self.search_top = search_top
        self.score_threshold = score_threshold
        self.embed_config = embed_config
        self.kb_root_path = kb_root_path

    def run(self, query: str, search_top=None, score_threshold=None, ):
        docs = DocRetrieval.run(
            query=query, knowledge_base_name=self.knowledge_base_name,
            search_top=search_top or self.search_top,
            score_threshold=score_threshold or self.score_threshold,
            embed_config=self.embed_config,
            kb_root_path=self.kb_root_path
        )
        return docs


doc_retrieval = BaseDocRetrieval(knowledge_base_name=kb_name, score_threshold=1.0, search_top=3, embed_config=embed_config)
```

<br>进行场景实例构建和知识库问答
```
# set chat phase
phase_name = "docChatPhase"
phase = BasePhase(
    phase_name, embed_config=embed_config, llm_config=llm_config, kb_root_path=KB_ROOT_PATH,
    doc_retrieval=doc_retrieval
)

# round-1
query_content = "langchain有哪些模块"
query = Message(
    role_name="human", role_type="user", input_query=query_content,
)
output_message, output_memory = phase.step(query)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))

# round-2
query_content = "提示（prompts）有什么用？"
query = Message(
    role_name="human", role_type="user", input_query=query_content,
)
output_message, output_memory = phase.step(query)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))
```