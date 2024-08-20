agent_prompt_en = '''
Please ensure your selection is one of the listed roles. Available roles for selection:
{agents}
Please ensure select the Role from agent names, such as {agent_names}'''

agent_prompt_zh = '''
Please ensure your selection is one of the listed roles. Available roles for selection:
{agents}
Please ensure select the Role from agent names, such as {agent_names}'''


summary_prompt_zh = '''
Your job is to summarize a history of previous messages in a conversation between an AI persona and a human.
The conversation you are given is a fixed context window and may not be complete.
Messages sent by the AI are marked with the 'assistant' role.
The AI 'assistant' can also make calls to functions, whose outputs can be seen in messages with the 'function' role.
Things the AI says in the message content are considered inner monologue and are not seen by the user.
The only AI messages seen by the user are from when the AI uses 'send_message'.
Messages the user sends are in the 'user' role.
The 'user' role is also used for important system events, such as login events and heartbeat events (heartbeats run the AI's program without user action, allowing the AI to act without prompting from the user sending them a message).
Summarize what happened in the conversation from the perspective of the AI (use the first person).
Keep your summary less than 100 words, do NOT exceed this word limit.
Only output the summary, do NOT include anything else in your output.

--- conversation
{conversation}
---
'''


summary_prompt_en = '''
Your job is to summarize a history of previous messages in a conversation between an AI persona and a human.
The conversation you are given is a fixed context window and may not be complete.
Messages sent by the AI are marked with the 'assistant' role.
The AI 'assistant' can also make calls to functions, whose outputs can be seen in messages with the 'function' role.
Things the AI says in the message content are considered inner monologue and are not seen by the user.
The only AI messages seen by the user are from when the AI uses 'send_message'.
Messages the user sends are in the 'user' role.
The 'user' role is also used for important system events, such as login events and heartbeat events (heartbeats run the AI's program without user action, allowing the AI to act without prompting from the user sending them a message).
Summarize what happened in the conversation from the perspective of the AI (use the first person).
Keep your summary less than 100 words, do NOT exceed this word limit.
Only output the summary, do NOT include anything else in your output.

--- conversation
{conversation}
---
'''


memory_extract_prompt_en = '''## 角色
你是一个结构化信息抽取的专家，你需要根据定义的节点、边类型，从输入的长对话文本中抽取节点和边关系。

## 节点和边的数据结构
{schemas}

## 要求
1、根据 节点和边的数据结构 完成信息抽取
2、edges中出现的start_id和end_id节点一定要在node中出现过

## 输出结构
{
    'nodes': [
        {'type': '{节点类型}', 'name': '{节点名称}', 'attributes': {'attribute1': '{属性值1}', ..., 'attributeN': '{属性值N}'},
         ...,
         {'type': '{节点类型}', 'name': '{节点名称}', 'attributes': {'attribute1': '{属性值1}', ..., 'attributeN': '{属性值N}'},
    ],
    'edges': [
        {'type': '{边类型}', 'start_id': '{实体名称}', 'end_id': '{实体名称}', 'name': '{边名称}', 'attributes': {'attribute1': '{属性值1}', ..., 'attributeN': '{属性值N}'},
         ...,
         {'type': '{边类型}', 'start_id': '{实体名称}', 'end_id': '{实体名称}', 'name': '{边名称}', 'attributes': {'attribute1': '{属性值1}', ..., 'attributeN': '{属性值N}'},
    ],
}

## 输入
{conversation}

## 输出
'''



memory_extract_prompt_zh = '''## 角色
你是一个结构化信息抽取的专家，你需要根据定义的节点、边类型，从输入的长对话文本中抽取节点和边关系。

## 节点和边的数据结构
{schemas}

## 要求
1、根据 节点和边的数据结构 完成信息抽取
2、edges中出现的start_id和end_id节点一定要在node中出现过

## 输出结构
{
    'nodes': [
        {'type': '{节点类型}', 'name': '{节点名称}', 'attributes': {'attribute1': '{属性值1}', ..., 'attributeN': '{属性值N}'},
         ...,
         {'type': '{节点类型}', 'name': '{节点名称}', 'attributes': {'attribute1': '{属性值1}', ..., 'attributeN': '{属性值N}'},
    ],
    'edges': [
        {'type': '{边类型}', 'start_id': '{实体名称}', 'end_id': '{实体名称}', 'attributes': {'name': '{边名称}', 'attribute1': '{属性值1}', ..., 'attributeN': '{属性值N}'},
         ...,
         {'type': '{边类型}', 'start_id': '{实体名称}', 'end_id': '{实体名称}', 'attributes': {'name': '{边名称}', 'attribute1': '{属性值1}', ..., 'attributeN': '{属性值N}'},
    ],
}

## 输入
{conversation}

## 输出
'''


memory_auto_schema_prompt_en = """## 角色
你是一个知识图谱专家，擅长从对话文本中抽象出实体和边的数据结构定义

## 目的
从对话中总结出节点和边的抽象定义，包括节点类型及相关属性、边类型及相关属性

## 节点要求
1、利用本体论帮助定义一致和标准化的节点类型。实体节点的类型可按照实体的自然属性（如人、地点等）、社会属性（如组织、事件等）或功能属性（如产品、服务等）等进行分类。
2、也可以参考现有的分类体系，如图书馆分类法、行业标准等，可以为定义节点类型提供参考
3、同时需要定义节点类型之间的关系，例如继承、关联等。以便于构建复杂的知识结构。
4、同时采用层次化的方法来组织节点类型，例如“人”可以进一步细分为“政治家”、“艺术家”、“科学家”等。
5、定义通用属性和特定属性，每个节点类型可能具有多维度的属性，例如“地点”可以有“经纬度”、“海拔”、“人口”等属性。


## 边要求
1、利用本体论可以帮助定义一致和标准化的边类型。边代表实体间的关系，例如“出生在”、“属于”等。
2、参考现有的分类体系和关系定义，如RDF Schema、OWL等，可以为定义边类型提供参考。
3、将关系进行分类，例如将所有表示位置的关系归为一类，所有表示组织的归属关系归为另一类。
4、除了基本的关系，如“出生在”、“属于”，还应考虑更复杂或特定领域的关系。
5、某些关系可能需要附加的属性来提供更多信息，例如“开始时间”、“结束时间”等。


## 分析要求
1、节点和边的定义应该遵循一定的语义规则，以确保知识图谱的一致性和可理解性。
2、从长文本对话的多层次结构进行分析


## 输出结构
{
    'nodes': [
        {'type': "{节点类型}", 'attributes': [{'name': '{属性名称}', 'description': '{属性描述}'}, ...,  {'name': '{属性名称}', 'description': '{属性描述}'}]},
        ...,
        {'type': "{节点类型}", 'attributes': [{'name': '{属性名称}', 'description': '{属性描述}'}, ...,  {'name': '{属性名称}', 'description': '{属性描述}'}]},
    ],
    'edge': [
        {'type': "{边类型}", 'attributes': [{'name': '{属性名称}', 'description': '{属性描述}'}, ...,  {'name': '{属性名称}', 'description': '{属性描述}'}]},
        ...,
        {'type': "{边类型}", 'attributes': [{'name': '{属性名称}', 'description': '{属性描述}'}, ...,  {'name': '{属性名称}', 'description': '{属性描述}'}]},
    ],
}

## 输入
{conversation}

## 输出
"""


memory_auto_schema_prompt_zh = """## 角色
你是一个知识图谱专家，擅长从对话文本中抽象出实体和边的数据结构定义

## 目的
从对话中总结出节点和边的抽象定义，包括节点类型及相关属性、边类型及相关属性

## 节点要求
1、利用本体论帮助定义一致和标准化的节点类型。实体节点的类型可按照实体的自然属性（如人、地点等）、社会属性（如组织、事件等）或功能属性（如产品、服务等）等进行分类。
2、也可以参考现有的分类体系，如图书馆分类法、行业标准等，可以为定义节点类型提供参考
3、同时需要定义节点类型之间的关系，例如继承、关联等。以便于构建复杂的知识结构。
4、同时采用层次化的方法来组织节点类型，例如“人”可以进一步细分为“政治家”、“艺术家”、“科学家”等。
5、定义通用属性和特定属性，每个节点类型可能具有多维度的属性，例如“地点”可以有“经纬度”、“海拔”、“人口”等属性。


## 边要求
1、利用本体论可以帮助定义一致和标准化的边类型。边代表实体间的关系，例如“出生在”、“属于”等。
2、参考现有的分类体系和关系定义，如RDF Schema、OWL等，可以为定义边类型提供参考。
3、将关系进行分类，例如将所有表示位置的关系归为一类，所有表示组织的归属关系归为另一类。
4、除了基本的关系，如“出生在”、“属于”，还应考虑更复杂或特定领域的关系。
5、某些关系可能需要附加的属性来提供更多信息，例如“开始时间”、“结束时间”等。


## 分析要求
1、节点和边的定义应该遵循一定的语义规则，以确保知识图谱的一致性和可理解性。
2、从长文本对话的多层次结构进行分析


## 输出结构
{
    'nodes': [
        {'type': "{节点类型}", 'attributes': [{'name': '{属性名称}', 'description': '{属性描述}'}, ...,  {'name': '{属性名称}', 'description': '{属性描述}'}]},
        ...,
        {'type': "{节点类型}", 'attributes': [{'name': '{属性名称}', 'description': '{属性描述}'}, ...,  {'name': '{属性名称}', 'description': '{属性描述}'}]},
    ],
    'edge': [
        {'type': "{边类型}", 'attributes': [{'name': '{属性名称}', 'description': '{属性描述}'}, ...,  {'name': '{属性名称}', 'description': '{属性描述}'}]},
        ...,
        {'type': "{边类型}", 'attributes': [{'name': '{属性名称}', 'description': '{属性描述}'}, ...,  {'name': '{属性名称}', 'description': '{属性描述}'}]},
    ],
}

## 输入
{conversation}

## 输出
"""



text2EKG_prompt_en = '''# 上下文 #
给定一个关于某个描述流程或者步骤的输入文本，我需要根据给定的输入文本，得到输入文本中流程或者操作步骤的结构化表示，之后可以用来在其它程序中绘制流程图。
你是一个结构化信息抽取和总结的专家，你可以根据输入的流程相关描述文本，抽取其中的关键节点及节点间的连接顺序，生成流程或者步骤的结构化json表示。
#############
# 目标 #
我希望你根据输入文本，提供一个输入文本中流程、操作的结构化json表示。可以参考以下步骤思考，但是不要输出每个步骤中间结果，只输出最后的流程图json：
1. 确定流程图节点: 根据输入文本内容，确定流程图的各个节点。节点可以用如下结构表示：
{
  "nodes": {
    "节点序号": {
      "type": "节点类型",
      "content": "节点内容"
    },
  }
}
其中 nodes 用来存放抽取的节点，每个 node 的 key 通过从0开始对递增序列表示，value 是一个字典，包含 type 和 content 两个属性， type 对应下面定义的四种节点类型，content 为抽取的节点内容。
节点类型定义如下:
Schedule:
  表示输入文本中流程和操作要完成的事情和任务，是对输入文本的意图的总结；
  第一个节点永远是Schedule节点。
Task: 
  表示该节点需要执行的任务。
Phenomenon:
  表示依据Task节点的执行结果，得到的事实结论。
  Phenomenon节点只能连接在Task节点之后。
Analysis:
  表示依据Phenomenon节点的事实进行推断的过程；
  Analysis节点只能连接在Phenomenon节点之后。

2. 连接流程图节点: 根据输入文本内容，确定流程图的各个节点的连接关系。节点之间的连接关系可以用如下结构表示：
{
  "edges": [
    {
      "start": "起始节点序号",
      "end": "终止节点序号"
    }
  ]
}
edges 用来存放节点间的连接顺序，它是一个列表，每个元素是一个字典，包含 start 和 end 两个属性， start 为起始 node 的 节点序号, end 为结束 node 的 节点序号。

3. 生成表示流程图的完整json: 将上面[确定流程图节点]和[连接流程图节点]步骤中的结果放到一个json，检查生成的流程图是否符合给定输入文本的内容，优化流程图的结构，合并相邻同类型节点，返回最终的json。
#############
# 风格 #
流程图节点数尽可能少，保持流程图结构简洁，相邻同类型节点可以合并。流程图节点中的节点内容content要准确、详细、充分。
#############
# 语气 #
专业，技术性
#############
# 受众 #
面向提供流程文本的人员，让他们确信你生成的流程图准确表示了文本中的流程步骤。
#############
# 响应 #
返回json结构定义如下:
{
  "nodes": {
    "节点序号": {
      "type": "节点类型",
      "content": "节点内容"
    }
  },
  "edges": [
    {
      "start": "起始节点序号",
      "end": "终止节点序号"
    }
  ]
}
#############
# 例子 #
以下是几个例子：

# 例子1 #
输入文本:路径：排查网络问题
1. 通过观察sofagw网关监控发现，BOLT失败数突增
2. 且失败曲线与退保成功率曲线相关性较高，判定是网络问题。

输出:{
  "nodes": {
    "0": {
      "type": "Schedule",
      "content": "排查网络问题"
    },
    "1": {
      "type": "Task",
      "content": "查询sofagw网关监控BOLT失败数"
    },
    "2": {
      "type": "Task",
      "content": "查询sofagw网关监控退保成功率"
    },
    "3": {
      "type": "Task",
      "content": "判断两条时序相关性"
    },
    "4": {
      "type": "Phenomenon",
      "content": "相关性较高"
    },
    "5": {
      "type": "Analysis",
      "content": "网络问题"
    }
  },
  "edges": [
    {
      "start": "0",
      "end": "1"
    },
    {
      "start": "1",
      "end": "2"
    },
    {
      "start": "2",
      "end": "3"
    },
    {
      "start": "3",
      "end": "4"
    },
    {
      "start": "4",
      "end": "5"
    }
  ]
}

# 例子2 #
输入文本:二、使用模版创建选品集
STEP1：创建选品集
注：因为只能选择同类型模版，必须先选择数据类型，才能选择模版创建
STEP2：按需选择模版后，点击确认

- 我的收藏：个人选择收藏的模版
- 我的创建：个人创建的模版
- 模版广场：公开的模版，可以通过名称/创建人搜索到需要的模版并选择使用 

STEP3：按需调整指标模版内的值，完成选品集创建

输出:{
  "nodes": {
    "0": {
      "type": "Schedule",
      "content": "使用模版创建选品集"
    },
    "1": {
      "type": "Task",
      "content": "创建选品集\n\n注：因为只能选择同类型模版，必须先选择数据类型，才能选择模版创建"
    },
    "2": {
      "type": "Task",
      "content": "按需选择模版后，点击确认\n\n - 我的收藏：个人选择收藏的模版 \n\n - 我的创建：个人创建的模版 \n\n - 模版广场：公开的模版，可以通过名称/创建人搜索到需要的模版并选择使用"
    },
    "3": {
      "type": "Task",
      "content": "按需调整指标模版内的值，完成选品集创建"
    }
  },
  "edges": [
    {
      "start": "0",
      "end": "1"
    },
    {
      "start": "1",
      "end": "2"
    },
    {
      "start": "2",
      "end": "3"
    }
  ]
}

# 例子3 #
输入文本:Step1

- 点击右侧的左右切换箭头，找到自己所在的站点或业务模块;
Step2

- 查询对应一级场景，若没有所需一级场景则联系 [@小明][@小红]添加：具体操作如下：
- 邮件模板
| 项目背景：<br />场景名称：<br />场景描述：<br />数据类型：商家/商品/营销商家/营销商品/权益商家/权益选品（必要的才选）<br />业务管理员：（花名） |
| --- |

- 发送邮件[@小明][@小红]抄送 [@小白]
Step3

- 查询对应二级场景，若没有所需二级场景则联系一级场景管理员添加，支持通过搜索二级场景名称和ID快速查询二级场景；
- 一级管理员为下图蓝色框①所在位置查看
Step4

- 申请二级场景数据权限，由对应二级场景管理员审批。若二级场景管理员为@小花@小映，按一级场景走申请流程。
- 二级管理员为下图蓝色框②所在位置查看

输出:{
  "nodes": {
    "0": {
      "type": "Schedule",
      "content": "场景权限申请"
    },
    "1": {
      "type": "Task",
      "content": "点击右侧的左右切换箭头，找到自己所在的站点或业务模块"
    },
    "2": {
      "type": "Task",
      "content": "查询对应一级场景，若没有所需一级场景则联系 [@小明][@小红]添加：具体操作如下：\n 发送邮件给小明和小红，抄送小白，邮件内容包括项目背景，场景名称，场景描述，数据类型和业务管理员"
    },
    "3": {
      "type": "Task",
      "content": "查询对应二级场景，若没有所需二级场景则联系一级场景管理员添加，支持通过搜索二级场景名称和ID快速查询二级场景"
    },
    "4": {
      "type": "Task",
      "content": "申请二级场景数据权限，由对应二级场景管理员审批。若二级场景管理员为@小花@小映，按一级场景走申请流程"
    }
  },
  "edges": [
    {
      "start": "0",
      "end": "1"
    },
    {
      "start": "1",
      "end": "2"
    },
    {
      "start": "2",
      "end": "3"
    },
    {
      "start": "3",
      "end": "4"
    }
  ]
}
#############
# 开始抽取 #
请根据上述说明和例子来对以下的输入文本抽取结构化流程json:

输入文本:{text}

输出:'''

text2EKG_prompt_zh = text2EKG_prompt_en