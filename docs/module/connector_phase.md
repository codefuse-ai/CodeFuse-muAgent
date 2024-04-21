---
title: Connector Phase
slug: Connector Phase ZH
url: "muagent/connector-phase-zh"
aliases:
- "/muagent/connector-phase-zh"
---



## 快速构建一个 agent phase
- 首先增加openai配置，也可以是其它类似于openai接口的模型（通过fastchat启动）
```
# 设置openai的api-key
import os, sys
import openai
import importlib
#
OPENAI_API_BASE = "https://api.openai.com/v1"
os.environ["API_BASE_URL"] = OPENAI_API_BASE
os.environ["OPENAI_API_KEY"] = "sk-xxx"
openai.api_key = "sk-xxx"
os.environ["model_name"] = "gpt-3.5-turbo"

# 
os.environ["embed_model"] = "{{embed_model_name}}"
os.environ["embed_model_path"] = "{{embed_model_path}}"

#
os.environ["DUCKDUCKGO_PROXY"] = os.environ.get("DUCKDUCKGO_PROXY") or "socks5://127.0.0.1:13659"
```

- 配置相关 LLM 和 Embedding Model
```
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig

# LLM 和 Embedding Model 配置
llm_config = LLMConfig(
    model_name=os.environ["model_name"], api_key=os.environ["OPENAI_API_KEY"], 
    api_base_url=os.environ["API_BASE_URL"], temperature=0.3
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=os.environ["embed_model"], 
    embed_model_path=os.environ["embed_model_path"]
)
```


- 这里从已有的 phase 配置中选一个 phase 来做示例
```
from muagent.base_configs.env_config import JUPYTER_WORK_PATH, KB_ROOT_PATH
from muagent.connector.configs import AGETN_CONFIGS
from muagent.connector.phase import BasePhase
from muagent.connector.schema import Message, load_role_configs

# log-level，print prompt和llm predict
os.environ["log_verbose"] = "2"

phase_name = "searchChatPhase"
phase = BasePhase(
    phase_name, embed_config=embed_config, llm_config=llm_config, 
)

# round-1
query_content1 = "美国当前总统是谁？"
query = Message(
    role_name="human", role_type="user", 
    role_content=query_content1, input_query=query_content1, origin_query=query_content1,
    search_engine_name="duckduckgo", score_threshold=1.0, top_k=3
    )

output_message, output_memory = phase.step(query)

print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))

# round-2
query_content2 = "美国上一任总统是谁，两个人有什么关系没？"
query = Message(
    role_name="human", role_type="user", 
    role_content=query_content2, input_query=query_content2, origin_query=query_content2,
    search_engine_name="duckduckgo", score_threshold=1.0, top_k=3
    )
output_message, output_memory = phase.step(query)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))
```



## Phase 参数配置
|Config Key Name	|Type	|Description|
| ------------------ | ---------- | ---------- |
|phase_name|	String|	场景名称|
|phase_config|CompletePhaseConfig| 默认为None，可直接指定完整的phaseconfig， 暂未实现|
|llm_config	|LLMConfig	|大语言模型配置|
|embed_config	|EmbedConfig	|向量模型配置|
|sandbox_server	|Dict	|沙盒环境即notebook启动配置|
|jupyter_work_path	|str	|沙盒环境的工作目录|
|kb_root_path	|str	|memory的存储路径|
|log_verbose	|str	|agent prompt&predict的日志打印级别|
| base_phase_config | Union[dict, str] | 默认配置：PHASE_CONFIGS，可通过实现对这个变量新增来实现自定义配置 |
| base_chain_config | Union[dict, str] | 默认配置：CHAIN_CONFIGS，可通过实现对这个变量新增来实现自定义配置 |
| base_role_config  | Union[dict, str] | 默认配置：AGETN_CONFIGS，可通过实现对这个变量新增来实现自定义配置 |
