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
    background: str, intentions: Union[list, tuple], examples: Optional[dict]=None,
    allow_multiple_choice=False
) -> str:
    nums_zh = ('一', '两', '三', '四', '五', '六', '七', '八', '九', '十')
    marks = '.。,，;；:：?？\t\n'

    intention_num = len(intentions)
    num_zh = nums_zh[intention_num - 1] if intention_num <= 10 else intention_num
    prompt = f'##背景##\n{background}\n\n##任务##\n找出最相关的意图，包括以下{num_zh}种：\n'

    for i, val in enumerate(intentions):
        if isinstance(val, (list, tuple)):
            k, v = val
            cur_intention = '{}. {}：{}；\n'.format(i + 1, k, v.strip(marks))
        else:
            cur_intention = '{}. {}；\n'.format(i + 1, val.strip(marks))
        prompt += cur_intention
    
    temp = '，若存在多个意图都是最相关的，请用","分开' if allow_multiple_choice else ''
    prompt += f'\n##输出格式##\n最相关意图对应的数字（第一个意图对应数字1）{temp}。\n\n'

    if examples:
        prompt += '##示例##\n'
        intention_idx_map = {k[0]: idx + 1 for idx, k in enumerate(intentions)}
        for query, ans in examples.items():
            if not isinstance(ans, (list, tuple)):
                ans = [ans]
            ans = ','.join([str(intention_idx_map[x]) for x in ans])
            prompt += f'问题：{query}\n回答：{ans}\n\n'
    
    prompt += '##用户询问##\n问题：{query}\n回答：'
    return prompt


INTENTIONS_CONSULT_WHICH = [
    ('整体计划查询', '用户想要获取某个问题的答案，或某个解决方案的完整流程（步骤）。'),
    ('下一步任务查询', '用户询问某个问题或方案的特定步骤，通常会提及“下一步”、“具体操作”等'),
    ('闲聊', '用户询问的内容与当前的技术问题或解决方案无关，更多是出于兴趣或社交性质的交流。')
]
INTENTIONS_CONSULT_WHICH_CODE = {
    '整体计划查询': 'allPlan',
    '下一步任务查询': 'nextStep',
    '闲聊': 'justChat'
}
CONSULT_WHICH_PROMPT = get_intention_prompt(
    '作为智能助手，您的职责是根据用户询问的内容，精准判断其背后的意图，以便提供最恰当的服务和支持。',
    INTENTIONS_CONSULT_WHICH,
    {
        '如何组织一次活动？': '整体计划查询',
        '系统升级的整个流程是怎样的？': '整体计划查询',
        '为什么我没有收到红包？请告诉我方案': '整体计划查询',
        '听说你们采用了新工具，能讲讲它的特点吗？': '闲聊'
    }
)

INTENTIONS_WHETHER_EXEC = [
    ('执行', '用户在使用某平台、服务、产品或功能时遇到了问题，或者明确声明要执行某一流程或游戏。'),
    ('询问', '用户的主要目的是获取信息，或只是简单闲聊。')
]
WHETHER_EXECUTE_PROMPT = get_intention_prompt(
    '作为智能助手，您需要根据用户询问判断其主要意图，以便提供最恰当的服务和支持。',
    INTENTIONS_WHETHER_EXEC,
    {
        '为什么我的优惠券使用失败？': '执行',
        '公司团建怎么申请？': '询问',
        '开始玩游戏。': '执行'
    }
)

DIRECT_CHAT_PROMPT = """##背景##
作为智能助手，您的职责是根据自身专业知识回答用户询问，以便提供最恰当的服务和支持。

##任务##
基于您所掌握的领域知识，对用户的提问进行回答。

##注意事项##
1. 请尽量从客观的角度来回答问题，内容符合事实、有理有据。
2. 内容尽量简洁。

##用户询问##
询问：{query}
回答：
"""
