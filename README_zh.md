<p align="left">
    <a>中文</a>&nbsp ｜ &nbsp<a href="README.md">English&nbsp </a>
</p>

# <p align="center">muAgent: An Innovative Agent Framework Driven by KG Engine</p>

<p align="center">
    <a href="README_zh.md"><img src="https://img.shields.io/badge/文档-中文版-yellow.svg" alt="ZH doc"></a>
    <a href="README.md"><img src="https://img.shields.io/badge/document-English-yellow.svg" alt="EN doc"></a>
    <a href="LICENSE.md"><img src="https://img.shields.io/badge/license-Apache%202.0-yellow" alt="License">
    <a href="https://github.com/codefuse-ai/CodeFuse-muAgent/issues">
      <img alt="Open Issues" src="https://img.shields.io/github/issues-raw/codefuse-ai/CodeFuse-muAgent" />
    </a>
    <br><br>
</p>



## 🔔 更新
- [2024.04.01] muAgent正式开源，聚焦多agent编排，协同FunctionCall、RAG、CodeInterpreter等技术
- [2024.09.05] 发布 muAgent v2.0 - EKG：一款由知识图谱引擎驱动的创新Agent产品框架
- [2024.10.28] 发布 muAgent v2.1，提供 一键式部署能力，包括基于KG的Agent编排、基于java的工具/Agent注册和管理、可拖拉拽编辑的前端产品UI

## 📜 目录
- [🤝 介绍](#-介绍)
- [🚀 快速使用](#-快速使用)
- [🧭 关键技术](#-关键技术)
- [🤗 贡献指南](#-贡献指南)
- [🗂 其他](#-其他)
  - [📱 联系我们](#-联系我们)


## 🤝 介绍
<p align="justify">
全新体验的Agent框架，将KG从知识获取来源直接升级为Agent编排引擎！基于LLM+ EKG（Eventic Knowledge Graph 行业知识承载）驱动，协同MultiAgent、FunctionCall、CodeInterpreter等技术，通过画布式拖拽、轻文字编写，让大模型在人的经验指导下帮助你实现各类复杂 SOP 流程。兼容现有市面各类Agent框架，同时可实现复杂推理、在线协同、人工交互、知识即用四大核心差异技术功能。这套框架目前在蚂蚁集团内多个复杂DevOps场景落地验证，同时来体验下我们快速搭建的谁是卧底游戏吧。
</p>
<div align="center">
  <img src="docs/resources/ekg-arch-zh.webp" alt="muAgent Architecture" width="770">
</div>


## 🚀 快速使用
完整文档见：[CodeFuse-muAgent](https://codefuse.ai/zh-CN/docs/api-docs/MuAgent/overview/multi-agent)
更多[demo](https://codefuse.ai/zh-CN/docs/api-docs/MuAgent/connector/customed_examples)

### EKG服务

```bash
# 使用我们的EKG服务只需要三步！（beta版本，需要将本地代码打包到容器中）

# 第一步. 加载代码
git clone https://github.com/codefuse-ai/CodeFuse-muAgent.git

# 第二步.
cd CodeFuse-muAgent

# 第三步. 启动所有容器服务，EKG基础镜像构建需要花费点时间
docker-compose up -d
```

<div align="center">
  <img src="docs/resources/ekg_demo.png" alt="EKG DEMO" width="770">
</div>


现在仍为beta版本，待v1.0版本完善后，会放出v1.0+的镜像以供下载。

敬请期待!

### SKD版本
1. 安装
```
pip install codefuse-muagent
```

2. 代码问答和相关配置，可以看 [docs](https://codefuse.ai/docs/api-docs/MuAgent/connector/customed_examples) 和代码示例 [examples](https://github.com/codefuse-ai/CodeFuse-muAgent/tree/main/examples)


## 🧭 关键技术

- **图谱构建**：通过虚拟团队构建、场景意图划分，让你体验在线文档VS本地文档的差别；同时，文本语义输入的节点使用方式，让你感受有注释代码VS无注释代码的差别，充分体现在线协同的优势；面向海量存量文档（通用文本、流程画板等），支持文本智能解析、一键导入，以及经验拆分泛化
- **图谱资产**：通过场景意图、事件流程、统一工具、组织人物四部分的统一图谱设计，满足各类SOP场景所需知识承载；工具在图谱的纳入进一步提升工具选择、参数填充的准确性，人物/智能体在图谱的纳入，让人可加入流程的推进，可灵活应用于多人文本游戏
- **图谱推理**：相比其他Agent框架纯模型推理、纯人工编排的推理模式，让大模型在人的经验/设计指导下做事，灵活、可控，同时面向未知局面，可自由探索，同时将成功探索经验总结、图谱沉淀，面向相似问题，少走弯路；整体流程唤起支持平台对接（规则配置）、语言触发，满足各类诉求
- **调试运行**：图谱编辑完成后，可视调试，快速发现流程错误、修改优化，同时面向调试成功路径，关联配置自动沉淀，减少模型交互、模型开销，加速推理流程；此外，在线运行中，我们提供全链路可视化监控
- **记忆管理**：统一消息池设计，支持各类场景所需分门别类消息投递、订阅，隔离且互通，便于多Agent场景消息管理使用；同时面向超长上下文，支持消息检索、排序、蒸馏，提升整体问答质量
- **操作空间**：遵循Swagger协议，提供工具注册、权限管理、统一分类，方便LLM在工具调用中接入使用；提供安全可信代码执行环境，同时确保代码精准生成，满足可视绘图、数值计算、图表编辑等各类场景诉求

## 🤗 贡献指南
感谢您对muAgent项目的关注！我们欢迎您的任何建议、意见（包括批评）和贡献。

为了更好促进项目的发展，我们鼓励您通过GitHub的Issues提交您对项目的各种建议、意见和评论。

参与Codefuse项目并为其作出贡献的方法有很多：代码实现、测试编写、文档完善等等。任何贡献我们都会非常欢迎，并将您加入贡献者列表，详见[Contribution Guide](https://codefuse-ai.github.io/contribution/contribution)。

## 🗂 其他
### 📱 联系我们
<div align=center>
  <img src="docs/resources/wechat.png" alt="图片", width="180">
</div>
