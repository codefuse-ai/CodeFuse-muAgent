from typing import Union, Optional, Sequence
from dataclasses import dataclass


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


GENERAL_INTENTION_PROMPT = """## 背景
作为智能助手，您需要根据用户询问判断其主要意图，以确定接下来的行动。

## 任务
找出最相关的意图，包括以下{num}种：
{intention}

## 输出格式
最相关意图对应的数字（第一个意图对应数字1）{extra}。
{example}
## 用户询问
"""


@dataclass
class IntentionInfo:
    description: str
    name: Optional[str] = None
    tag: Optional[str] = None

    def __post_init__(self):
        marks = '.。,，;；:：?？\t\n '
        self.description = self.description.replace('{', '{{').replace('}', '}}').strip(marks)
        
        if self.name:
            self.name = self.name.replace('{', '{{').replace('}', '}}').strip(marks)

    def __str__(self):
        if self.name:
            return f'{self.name}：{self.description}'
        return self.description


def get_intention_prompt(
    intentions: Sequence[IntentionInfo],
    examples: Optional[dict[str, Union[IntentionInfo, Sequence[IntentionInfo]]]]=None,
    allow_multiple_choice=False
) -> str:
    nums_zh = ('一', '两', '三', '四', '五', '六', '七', '八', '九', '十')

    intention_num = len(intentions)
    intention_num_zh = nums_zh[intention_num - 1] if intention_num <= len(nums_zh) else intention_num

    intentions_str, intention2idx = '', dict()
    for i, intention_info in enumerate(intentions):
        end_mark = '。' if i == intention_num - 1 else '；'
        intentions_str += '{}. {}{}\n'.format(i + 1, intention_info, end_mark)
        intention2idx[str(intention_info)] = i + 1
    
    extra = '，若存在多个意图都是最相关的，请用","分开' if allow_multiple_choice else ''

    example_str = ''
    if examples:
        example_str += '\n## 示例\n'
        for query, label in examples.items():
            if isinstance(label, IntentionInfo):
                label = [label]
            label = ','.join([str(intention2idx[str(x)]) for x in label])
            example_str += f'问题：{query}\n回答：{label}\n'
    
    prompt = GENERAL_INTENTION_PROMPT.format(
        num=intention_num_zh,
        intention=intentions_str[:-1],
        extra=extra,
        example=example_str
    )

    prompt += '问题：{query}\n回答：'
    return prompt


INTENTION_ALLPLAN = IntentionInfo(
    description='用户想要获取某个问题的答案，或某个解决方案的完整流程（步骤）。',
    name='整体计划查询', tag='allPlan'
)
INTENTION_NEXTSTEP = IntentionInfo(
    description='用户询问某个问题或方案中某一个特定步骤。通常会提及“下一步”、“具体操作”等。',
    name='某一步任务查询', tag='nextStep'
)
INTENTION_SEVERALSTEPS = IntentionInfo(
    description='用户询问某个问题或方案中其中某几个步骤。',
    name='某几步任务查询', tag='severalSteps'
)
INTENTION_BACKGROUND = IntentionInfo(
    description='用户询问某个问题或方案的背景知识，规则以及流程介绍等。',
    name='背景查询', tag='background'
)
INTENTION_CHAT = IntentionInfo(
    description='用户询问的内容与当前的技术问题或解决方案无关，更多是出于兴趣或社交性质的交流。',
    name='闲聊', tag='justChat'
)
INTENTION_EXECUTE = IntentionInfo(
    description='用户在使用某平台、服务、产品或功能时遇到了问题，或者要求完成某一需要执行的任务，或者明确声明要执行某一流程或游戏',
    name='执行'
)
INTENTION_QUERY = IntentionInfo(
    description='用户的主要目的是获取信息而非执行任务（比如：怎么向银行申请贷款），或只是简单闲聊。',
    name='询问'
)
INTENTION_NOMATCH = IntentionInfo(
    description='与上述意图都不匹配，属于其他类型的询问意图。'
)

INTENTIONS_WHETHER_EXEC = (INTENTION_EXECUTE, INTENTION_QUERY)
WHETHER_EXECUTE_PROMPT = get_intention_prompt(
    intentions=INTENTIONS_WHETHER_EXEC,
    examples={
        '为什么我的优惠券使用失败？': INTENTION_EXECUTE,
        '如何向银行贷款？': INTENTION_QUERY,
        '开始玩游戏。': INTENTION_EXECUTE,
        '帮我看一下今天的天气怎么样': INTENTION_EXECUTE
    }
)

INTENTIONS_CONSULT_WHICH = (INTENTION_ALLPLAN, INTENTION_NEXTSTEP, INTENTION_SEVERALSTEPS, INTENTION_BACKGROUND, INTENTION_CHAT)
CONSULT_WHICH_PROMPT = get_intention_prompt(
    intentions=INTENTIONS_CONSULT_WHICH,
    examples={
        '如何组织一次活动？': INTENTION_ALLPLAN,
        '系统升级的整个流程是怎样的？': INTENTION_ALLPLAN,
        '为什么我没有收到红包？请告诉我方案': INTENTION_ALLPLAN,
        '如果我想学习一门新语言，第一步我需要先做些什么？': INTENTION_NEXTSTEP,
        '项目开发中代码开发完成后需要经过哪几步测试才能发布到生产呢？': INTENTION_SEVERALSTEPS,
        '请问下狼人杀游戏中猎人的主要职责是什么？': INTENTION_BACKGROUND,
        '听说你们采用了新工具，能讲讲它的特点吗？': INTENTION_CHAT
    }
)
