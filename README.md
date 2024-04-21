<p align="left">
    <a href="README_zh.md">中文</a>&nbsp ｜ &nbsp<a>English&nbsp </a>
</p>

# <p align="center">MuAgent: A Multi-Agent FrameWork For Faster Build Agents</p>

<p align="center">
    <a href="README.md"><img src="https://img.shields.io/badge/文档-中文版-yellow.svg" alt="ZH doc"></a>
    <a href="README_en.md"><img src="https://img.shields.io/badge/document-English-yellow.svg" alt="EN doc"></a>
    <img src="https://img.shields.io/github/license/codefuse-ai/muagent" alt="License">
    <a href="https://github.com/codefuse-ai/muagent/issues">
      <img alt="Open Issues" src="https://img.shields.io/github/issues-raw/codefuse-ai/muagent" />
    </a>
    <br><br>
</p>



## 🔔 News
- [2024.04.01] muagent is now open source, featuring functionalities such as knowledge base, code library, tool usage, code interpreter, and more

## 📜 Contents
- [🤝 Introduction](#-Introduction)
- [🚀 QuickStart](#-QuickStart)
- [🧭 Key Technologies](#-Key-Technologies)
- [🗂 Miscellaneous](#-Miscellaneous)
  - [📱 Contact Us](#-Contact-Us)


## 🤝 Introduction
Developed by the Ant CodeFuse Team, muagent is a Multi-Agent framework whose primary goal is to streamline the Standard Operating Procedure (SOP) orchestration for agents. muagent integrates a rich collection of toolkits, code libraries, knowledge bases, and sandbox environments, enabling users to rapidly construct complex Multi-Agent interactive applications in any field. This framework allows for the efficient execution and handling of multi-layered and multi-dimensional complex tasks.

![](docs/resources/agent_runtime.png)

## 🚀 快速使用
For complete documentation, see: [muagent](docs/overview/o1.muagent.md)
For more [demos](docs/overview/o3.quick-start.md)

1. Installation
```
pip install muagent
```

2. Code answer Prepare related llm and embedding model configurations
```
import os

# set your config
api_key = ""
api_base_url= ""
model_name = ""
embed_model = ""
embed_model_path = ""

from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.connector.phase import BasePhase
from muagent.connector.schema import Message, Memory
from muagent.codechat.codebase_handler.codebase_handler import CodeBaseHandler

llm_config = LLMConfig(
    model_name=model_name, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)
```

<br>

Initialize the codebase
```
codebase_name = 'client_local'
code_path = "D://chromeDownloads/devopschat-bot/client_v2/client"

cbh = CodeBaseHandler(
    codebase_name, code_path, crawl_type='dir', use_nh=use_nh,local_graph_path=CB_ROOT_PATH,
    llm_config=llm_config, embed_config=embed_config
)
cbh.import_code(do_interpret=do_interpret)
```

<br>

Start codebase Q&A
```
# 
phase_name = "codeChatPhase"
phase = BasePhase(
    phase_name, embed_config=embed_config, llm_config=llm_config,
)
```

## Key Technologies

● Agent Base：Four fundamental Agent types are constructed – BaseAgent, ReactAgent, ExecutorAgent, SelectorAgent, supporting basic activities across various scenarios 
● Communication: Information transmission between Agents is accomplished through Message and Parse Message entities, interacting with Memory Manager and managing memories in the Memory Pool 
● Prompt Manager: Customized Agent Prompts are automatically assembled with the aid of Role Handler, Doc/Tool Handler, Session Handler, and Customized Handler 
● Memory Manager: Facilitates the management of chat history storage, information compression, and memory retrieval, culminating in storage within databases, local systems, and vector databases via the Memory Pool 
● Component: Auxiliary ecosystem components to construct Agents, including Retrieval, Tool, Action, Sandbox, etc. 
● Customized Model: Supports the integration of private LLM and Embedding models

##  Contribution
We are deeply grateful for your interest in the Codefuse project and warmly welcome any suggestions, opinions (including criticism), comments, and contributions. 

Feel free to raise your suggestions, opinions, and comments directly through GitHub Issues. There are numerous ways to participate in and contribute to the Codefuse project: code implementation, writing tests, process tool improvements, documentation enhancements, etc. 

We welcome any contribution and will add you to the list of contributors. See [Contribution Guide...](docs/contribution/contribute_guide.md)


## 🗂 Miscellaneous
### 📱 Contact Us
<div align=center>
  <img src="docs/resources/wechat.png" alt="图片", width="360">
</div>
