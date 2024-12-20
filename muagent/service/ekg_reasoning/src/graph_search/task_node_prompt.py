# -*- coding: utf-8 -*-

PARALLEL_RUNNING_PROMPT= \
'''
##输出##
请以dict的形式，给出参与者的所有行动计划。行动计划表示为JSON，格式为
 {"thought": str, "action_plan": [{"player_name":str, "agent_name":str}, {"player_name":str, "agent_name":str}], "Dungeon_Master": [{"memory_tag":str,"content":str}] }


关键词含义如下：
_ thought (str): 主持人的一些思考,包括分析玩家的存活状态，对历史对话信息的理解，对当前任务情况的判断等。 
_ player_name (str): 玩家的 player_name
_ agent_name (str):  玩家的 agent_name;
_ content (str):     为主持人的告知信息, 
_ memory_tag (List[str]): memory_tag 固定为本条信息的可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]

##example##
{"thought": "str", "action_plan": [{"player_name":str, "agent_name":str}, {"player_name":str, "agent_name":str}, ... ], "Dungeon_Master": [{ "memory_tag":["agent_name_a","agent_name_b"], "content": "str",}]}

##注意事项##
1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。
2. 整个dict是一个jsonstr，请输出jsonstr，不用输出markdown格式
3. 结合已有的步骤，只输出一个 dict，不要包含其他信息
'''



PLANNING_RUNNING_PROMPT= \
'''
##输出##
请以dict的形式，给出参与者的所有行动计划。行动计划表示为JSON，格式为
 {"thought": str, "action_plan": [{"player_name":str, "agent_name":str, "task_description":str}, {"player_name":str, "agent_name":str,"task_description":str}], "Dungeon_Master": [{"memory_tag":str}] }


关键词含义如下：
_ thought (str): 主持人的一些思考,包括分析玩家的存活状态，对历史对话信息的理解，对当前任务情况的判断等。 
_ player_name (str): 行动方的 player_name, 若行动方为玩家，否则为玩家的 player_name;如果行动方是主持人，为 "主持人"，
_ agent_name (str):  行动方的 agent_name, 若行动方为玩家，否则为玩家的 agent_name;如果行动方是主持人，为 "主持人"，
_ task_description (str):     为行动方本轮的任务. 只要写要做什么事儿即可，因为现在还处于任务规划阶段，事情还没有开始做。比如行动方本轮的目的是讨论，写出讨论的话题、目的等即可，不要把讨论的内容也写出来，因为现在还没有开始讨论，只是在规划行动计划。
_ memory_tag (List[str]): memory_tag 固定为本条信息的可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]

##example##
{"thought": "str", "action_plan": [{"player_name":str, "agent_name":str, "task_description":str}, {"player_name":str, "agent_name":str, "task_description":str}, ... ], "Dungeon_Master": [{ "memory_tag":["agent_name_a","agent_name_b"], "content": "str",}]}

##注意事项##
1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。
2. 整个dict是一个jsonstr，请输出jsonstr，不用输出markdown格式
3. 结合已有的步骤，只输出一个 dict，不要包含其他信息
'''


PLANNING_RUNNING_PROMPT_DM_SPEECH= \
'''
##输出##
本阶段行动计划已经给出了，根据行动计划，此时轮到主持人发言。主持人的发言表示为JSON，格式为
{"thought": str,  "content":str}]}
 
主持人请尽量不要重复上一轮的发言
 
关键词含义如下：
_ thought (str): 主持人的一些思考,包括分析玩家的存活状态，对历史对话信息的理解，对当前任务情况的判断等。 
_ content (str):     为主持人的具体发言信息, 




##注意事项##
1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。
2. 整个dict是一个jsonstr，请输出jsonstr，不用输出markdown格式
3. 结合已有的步骤，只输出一个 dict，不要包含其他信息
'''


PLANNING_RUNNING_AGENT_REPLY_TEMPLATE= \
{"thought": "None", "action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, 
 "observation": [{ "memory_tag":["agent_name_a"],"content": "str"}]}

PLANNING_RUNNING_PROMPT_SUFFIX_1 = \
'\n##已有步骤##\n无' 



PLANNING_RUNNING_PROMPT_SUFFIX_2 = \
'\n##请输出下一个步骤,切记只输出一个步骤，它应该只是一个dict ##\n'

REACT_RUNNING_PROMPT = \
"""
##输出##
请以列表的形式，给出参与者的所有行动。每个行动表示为JSON，格式为
[{"thought": str, "action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}, ...]

关键词含义如下：
_ thought (str): 主持人执行行动的一些思考,包括分析玩家的存活状态，对历史对话信息的理解，对当前任务情况的判断。 
_ action (dict): 行动发起方的信息。
_ player_name (str): 行动发起方的 player_name，若行动发起方为主持人，为空，否则为玩家的 player_name；
_ agent_name (str): 行动发起方的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。
_ content (str): 行动发起方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。
_ memory_tag (List[str]): 无论行动发起方是主持人还是玩家，memory_tag 固定为所有信息可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]


##example##
如果是玩家发言，则用 {"thought": "str", "action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{ "memory_tag":["agent_name_a","agent_name_b"],"content": "str"}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description
如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"thought": "str", "action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["agent_name_a","agent_name_b"], "content": "str",}]}

##注意事项##
1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。
2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。
3. 输出列表的最后一个元素一定是{"action": "taskend"}。
4. 整个list是一个jsonstr，请输出jsonstr，不用输出markdown格式
5. 结合已有的步骤，每次只输出下一个步骤，即一个 {"thought":  str, "action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}
6. 如果是人类玩家发言， 一定要选择类似 人类agent 这样的agent_name
"""


