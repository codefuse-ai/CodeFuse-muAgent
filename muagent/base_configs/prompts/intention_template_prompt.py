from typing import Union, Optional


RECOGNIZE_INTENTION_PROMPT = """你是一个任务决策助手，能够将理解用户意图并决策采取最合适的行动，尽可能地以有帮助和准确的方式回应人类，
使用 JSON Blob 来指定一个返回的内容，提供一个 action（行动）。
有效的 'action' 值为：'planning'(需要先进行拆解计划) or 'only_answer' （不需要拆解问题即可直接回答问题）or "tool_using" (使用工具来回答问题) or 'coding'(生成可执行的代码)。
在每个 $JSON_BLOB 中仅提供一个 action，如下所示：
```
{{'action': $ACTION}}
```
按照以下格式进行回应：
问题：输入问题以回答
行动：$ACTION
```
$JSON_BLOB
```
"""



'''## AGENT PROFILE
### Role
{role_prompt}

### Task
{task_prompt}

### TOOL INFORMATION Format
### AGENT INFORMATION FORMAT 


### requirement
The Action Status field ensures that the tools or code mentioned in the Action can be parsed smoothly. Please make sure not to omit the Action Status field when replying.



### INFORMATION Format
#### DOC

### Context Format
#### SESSION RECORDS
对话流生成策略

### Input Format
**{Key}:** key description

### RESPONSE OUTPUT FORMAT
**{Key}:** key description



## BEGIN!!!

### DOCUMENT INFORMATION

### Context
#### SESSION RECORDS


### Input
**{Key}:** key description

### Ouput Response
'''


def get_intention_prompt(
    background: str, intentions: Union[list, tuple], examples: Optional[dict]=None
) -> str:
    nums_zh = ('一', '两', '三', '四', '五', '六', '七', '八', '九', '十')

    intention_num = len(intentions)
    num_zh = nums_zh[intention_num - 1] if intention_num <= 10 else intention_num
    prompt = f'##背景##\n{background}\n\n##任务##\n辨别用户的询问意图，包括以下{num_zh}类：\n'

    for i, val in enumerate(intentions):
        if isinstance(val, (list, tuple)):
            k, v = val
            cur_intention = f'{i + 1}. {k}：{v}\n'
        else:
            cur_intention = f'{i + 1}. {val}\n'
        prompt += cur_intention
    
    prompt += '\n##注意事项##\n'
    num_range_str = '、'.join(map(str, range(1, intention_num + 1)))
    prompt += f'回答：数字{num_range_str}中的一个来表示用户的询问意图，对应上述{num_zh}种分类。避免提供额外解释或其他信息。\n\n'

    if examples:
        prompt += '##示例##\n'
        intention_idx_map = {k[0]: idx + 1 for idx, k in enumerate(intentions)}
        for query, ans in examples.items():
            ans = intention_idx_map[ans]
            prompt += f'询问：{query}\n回答：{ans}\n\n'
    
    prompt += '##用户询问##\n询问：{query}\n回答：'
    return prompt


INTENTIONS_CONSULT_WHICH = [
    ('整体计划查询', '用户询问关于某个解决方案的完整流程或步骤，包含但不限于“整个流程”、“步骤”、“流程图”等词汇或概念。'),
    ('下一步任务查询', '用户询问在某个解决方案的特定步骤中应如何操作或处理，通常会提及“下一步”、“具体操作”、“如何做”等，且明确指向解决方案中的某个特定环节。'),
    ('闲聊', '用户询问的内容与当前的技术问题或解决方案无关，更多是出于兴趣或社交性质的交流。')
]
CONSULT_WHICH_PROMPT = get_intention_prompt(
    '作为运维领域的客服，您的职责是根据用户询问的内容，精准判断其背后的意图，以便提供最恰当的服务和支持。',
    INTENTIONS_CONSULT_WHICH,
    {
        '系统升级的整个流程是怎样的？': '整体计划查询',
        '听说你们采用了新工具，能讲讲它的特点吗？': '闲聊'
    }
)

INTENTIONS_WHETHER_EXEC = [
    ('执行', '当用户声明自己在使用某平台、服务、产品或功能时遇到具体问题，且明确表示不知道如何解决时，其意图应被分类为“执行”。'),
    ('询问', '当用户明确询问某些解决方案的背景、流程、方式方法等信息，或只是出于好奇想要了解更多信息，或只是简单闲聊时，其意图应被分类为“询问”。')
]
WHETHER_EXECUTE_PROMPT = get_intention_prompt(
    '作为运维领域的客服，您需要根据用户询问判断其主要意图，以确定接下来的运维流程。',
    INTENTIONS_WHETHER_EXEC,
    {
        '为什么我的优惠券使用失败？': '执行',
        '我想知道如何才能更好地优化我的服务器性能，你们有什么建议吗？': '询问'
    }
)

DIRECT_CHAT_PROMPT = """##背景##
作为运维领域的客服，您的职责是根据自身专业知识回答用户询问，以便提供最恰当的服务和支持。

##任务##
基于您所掌握的领域知识，对用户的提问进行回答。

##注意事项##
请尽量从客观的角度来回答问题，内容符合事实、有理有据。

##用户询问##
询问：{query}
回答：
"""
