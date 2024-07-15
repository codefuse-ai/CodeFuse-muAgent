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