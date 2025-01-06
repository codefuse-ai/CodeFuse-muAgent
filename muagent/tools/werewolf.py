import os
from typing import (
    List, 
    Dict
)
from loguru import logger
from pydantic import BaseModel, Field
import random


from .base_tool import BaseToolModel
from ..models import get_model, ModelConfig



class RoleAssignmentTool(BaseToolModel):
    name = "狼人杀-角色分配工具"
    description = "狼人杀的角色分配工具，可以为每一位玩家分配一个单词和人物角色。"

    class ToolInputArgs(BaseModel):
        pass

    class ToolOutputArgs(BaseModel):
        roles: list

    @classmethod
    def run(cls, **kwargs) -> ToolOutputArgs:
        """Execute your tool!"""

        players = [
            ["朱丽", "agent_朱丽"],
            ["周杰", "agent_周杰"],
            ["沈强", "agent_沈强"],
            ["韩刚", "agent_韩刚"],
            ["梁军", "agent_梁军"],
            ["周欣怡", "agent_周欣怡"],
            ["贺子轩", "agent_贺子轩"],
            ["人类玩家", "agent_人类玩家"]
        ]
        random.shuffle(players)
        roles = ["平民_1", "平民_2", "平民_3", "狼人_1", "狼人_2", "狼人_3", "女巫", "预言家"]
        random.shuffle(roles)

        assigned_roles = []
        for i in range(len(players)):
            assigned_roles.append({
                "player_name": players[i][0],
                "agent_name": players[i][1],
                "agent_description": roles[i]
            })
        return assigned_roles



class PlayerSeatingTool(BaseToolModel):
    name: str = "狼人杀-座位分配"
    description: str = "狼人杀的座位分配工具，可以将玩家顺序打乱随机分配座位"

    class ToolInputArgs(BaseModel):
        pass

    class ToolOutputArgs(BaseModel):
        seating_chart: str

    @classmethod
    def run(cls, **kwargs) -> ToolOutputArgs:
        """Execute your tool!"""

        players = [
            ["朱丽", "agent_朱丽"],
            ["周杰", "agent_周杰"],
            ["沈强", "agent_沈强"],
            ["韩刚", "agent_韩刚"],
            ["梁军", "agent_梁军"],
            ["周欣怡", "agent_周欣怡"],
            ["贺子轩", "agent_贺子轩"],
            ["人类玩家", "agent_人类玩家"]
        ]
        n = len(players)
        random.shuffle(players)

        seating_chart = "\n\n| 座位 | 玩家 |\n|---|---|\n"
        seating_chart += "\n".join(f"| {i} | **{players[i-1][0]}** |" for i in range(1, n + 1))
        
        return seating_chart
    

class WerewolfGameInstructionTool(BaseToolModel):
    name = "狼人杀-游戏指令"
    description = "狼人杀的游戏指令工具，需要根据记忆的上下文信息，当前任务、以及你拿到的身份信息来进行回应。"

    class ToolInputArgs(BaseModel):
        pass

    class ToolOutputArgs(BaseModel):
        instruction: str

    @classmethod
    def run(cls, **kwargs) -> ToolOutputArgs:
        """Execute your tool!"""
        template = (
            '##狼人杀游戏说明##\n'
            '这个游戏基于文字交流, 以下是游戏规则：\n'
            '角色:\n'
            '主持人也是游戏的组织者，你需要正确回答他的指示。游戏中有五种角色：狼人、平民、预言家、女巫和猎人，三个狼人，一个预言家，一个女巫，一个猎人，两个平民。\n'
            '好人阵营: 村民、预言家、猎人和女巫。\n'
            '游戏阶段：游戏分为两个交替的阶段：白天和黑夜。\n'
            '黑夜：\n'
            '在黑夜阶段，你与主持人的交流内容是保密的。你无需担心其他玩家和主持人知道你说了什么或做了什么。\n'
            '- 如果你是狼人，你需要和队友一起选择袭击杀死一个玩家\n'
            '- 如果你是女巫，你有一瓶解药，可以拯救被狼人袭击的玩家，以及一瓶毒药，可以在黑夜后毒死一个玩家。解药和毒药只能使用一次。\n'
            '- 如果你是预言家，你可以在每个晚上检查一个玩家是否是狼人，这非常重要。\n'
            '- 如果你是猎人，当你在黑夜被狼人杀死时可以选择开枪杀死任意一名玩家。\n'
            '- 如果你是村民，你在夜晚无法做任何事情。\n'
            '白天：\n'
            '你与存活所有玩家（包括敌人）讨论。讨论结束后，玩家投票来淘汰一个自己怀疑是狼人的玩家。获得最多票数的玩家将被淘汰。主持人将告诉谁被杀，否则将没有人被杀。\n'
            '如果你是猎人，当你在白天被投票杀死之后可以选择开枪杀死任意一名玩家。\n'
            '游戏目标:\n'
            '狼人的目标是杀死所有的好人阵营中的玩家，并且不被好人阵营的玩家识别出狼人身份；\n'
            '好人阵营的玩家，需要找出并杀死所有的狼人玩家。\n'
            '##注意##\n'
            '你正在参与狼人杀这个游戏，你应该感知自己的名字、座位号和角色。\n'
            '1. 若你的角色为狼人，白天的发言应该尽可能隐藏身份。\n'
            '2. 若你的角色属于好人阵营，白天的发言应该根据游戏进展尽可能分析出谁是狼人。\n'
            '##以下为目前游戏进展##\n'
            '{memory}\n'
            '##发言格式##\n'
            '你的回答中需要包含你的想法并给出简洁的理由，注意请有理有据，白天的发言尽量不要与别人的发言内容重复。发言的格式应该为Python可直接解析的jsonstr，格式如下：\n'
            '{{\"thought\": 以“我是【座位号】号玩家【名字】【角色】”开头，根据主持人的通知感知自己的【名字】、【座位号】、【角色】，根据游戏进展和自己游戏角色的当前任务分析如何发言，字数不超过150字, \"output\": 您的发言应该符合目前游戏进展和自己角色的逻辑，白天投票环节不能投票给自己。}}\n'
            '##开始发言##\n'
        )
        model_config = None
        try:
            model_config = ModelConfig(
                config_name="codefuse_default",
                model_type=os.environ.get("DEFAULT_MODEL_TYPE"),
                model_name=os.environ.get("DEFAULT_MODEL_NAME"),
                api_key=os.environ.get("DEFAULT_API_KEY"),
                api_url=os.environ.get("DEFAULT_API_URL"),
            )
            memory = kwargs.get("memory") or ""
            model = get_model(model_config)
            content = model.predict(template.format(memory=memory))
        except Exception as e:
            content = f"无法正确调用模型: {e}, {model_config}"
        return content


class AgentZhuliTool(WerewolfGameInstructionTool):
    name = "狼人杀-agent_朱丽"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与狼人杀这场游戏，在游戏中你的名字是朱丽"
    )


class AgentZhoujieTool(WerewolfGameInstructionTool):
    name = "狼人杀-agent_周杰"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与狼人杀这场游戏，在游戏中你的名字是周杰"
    )


class AgentShenqiangTool(WerewolfGameInstructionTool):
    name = "狼人杀-agent_沈强"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与狼人杀这场游戏，在游戏中你的名字是沈强"
    )

class AgentHangangTool(WerewolfGameInstructionTool):
    name = "狼人杀-agent_韩刚"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与狼人杀这场游戏，在游戏中你的名字是韩刚"
    )


class AgentLiangjunTool(WerewolfGameInstructionTool):
    name = "狼人杀-agent_梁军"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与狼人杀这场游戏，在游戏中你的名字是梁军"
    )

class AgentZhouxinyiTool(WerewolfGameInstructionTool):
    name = "狼人杀-agent_周欣怡"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与狼人杀这场游戏，在游戏中你的名字是周欣怡"
    )


class AgentHezixuanTool(WerewolfGameInstructionTool):
    name = "狼人杀-agent_贺子轩"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与狼人杀这场游戏，在游戏中你的名字是贺子轩"
    )


class WerewolfGameEndCheckerTool(BaseToolModel):
    name = "狼人杀-胜利条件判断"
    description = "狼人杀的胜利条件判断工具，判断当前狼人杀游戏是否结束。"

    class ToolInputArgs(BaseModel):
        pass

    class ToolOutputArgs(BaseModel):
        thought: str
        players: dict
        isEnd: str

    @classmethod
    def run(cls, **kwargs) -> ToolOutputArgs:
        """Execute your tool!"""
        template = (
            '##本局游戏历史记录##\n'
            '{memory}\n'
            '\n'
            '##背景##\n'
            '你是一个逻辑判断大师，你正在参与“狼人杀”这个游戏，你的角色是[主持人]。你熟悉“狼人杀”游戏的完整流程，现在需要判断当前游戏是否结束。\n'
            '\n'
            '##任务##\n'
            '你的任务是判断当前游戏是否结束，规则如下：\n'
            '根据【重要信息】感知每一轮被投票死亡、被狼人杀死、被女巫毒死、被猎人带走的玩家。 统计目前存活的[好人]玩家数量、[狼人]玩家数量。格式{{\"存活的好人\":[player_name], \"存活的狼人\":[player_name]}}，判断以下条件中的一个是否满足：\n'
            '1. 存活的“狼人”玩家数量为0。\n'
            '2. “狼人”数量超过了“好人”数量。\n'
            '3. “狼人”数量等于“好人”数量，“女巫”已死亡或者她的毒药已经使用。\n'
            '若某个条件满足，游戏结束；否则游戏没有结束。\n'
            '\n'
            '##输出##\n'
            '返回JSON格式，格式为：{{\"thought\": str, \"存活的玩家信息\": {{\"存活的好人\":[player_name], \"存活的狼人\":[player_name]}}, \"isEnd\": \"是\" or \"否\"}}\n'
            '-thought **根据本局游戏历史记录** 分析 游戏最开始有哪些玩家, 他们的身份是什么, 投票导致死亡的玩家有哪些? 被狼人杀死的玩家有哪些? 被女巫毒死的玩家是谁? 被猎人带走的玩家是谁？分析当前存活的玩家有哪些? 是否触发了游戏结束条件? 等等。\n'
            '\n'
            '##example##\n'
            '{{\"thought\": \"**游戏开始时** 有 小杭、小北、小赵、小钱、小孙、小李、小夏、小张 八位玩家, 其中 小杭、小北、小赵是[狼人], 小钱、小孙是[平民], 小李是[预言家]，小夏是[女巫]，小张是[猎人]，小张在第一轮被狼人杀死了，猎人没有开枪，[狼人]数量大于[好人]数量，因此游戏未结束。\", \"存活的玩家信息\": {{\"存活的狼人\":[\"小杭\", \"小北\", \"小赵\"]}}, {{\"存活的好人\":[\"小钱\", \"小孙\", \"小李\", \"小夏\"]}}, \"isEnd\": \"否\" }}\n'
            '##注意事项##\n'
            '1. 所有玩家的座位、身份、agent_name、存活状态、游戏进展等信息在开头部分已给出。\n'
            '2. \"是\" or \"否\" 如何选择？若游戏结束，则为\"是\"，否则为\"否\"。\n'
            '3. 请直接输出jsonstr，不用输出markdown格式。\n'
            '4. 游戏可能进行了不只一轮，可能有1个或者2个玩家已经死亡，请注意感知。\n'
        )
        model_config = None
        try:
            model_config = ModelConfig(
                config_name="codefuse_default",
                model_type=os.environ.get("DEFAULT_MODEL_TYPE"),
                model_name=os.environ.get("DEFAULT_MODEL_NAME"),
                api_key=os.environ.get("DEFAULT_API_KEY"),
                api_url=os.environ.get("DEFAULT_API_URL"),
            )
            memory = kwargs.get("memory") or ""
            model = get_model(model_config)
            content = model.predict(template.format(memory=memory))
        except Exception as e:
            content = f"无法正确调用模型: {e}, {model_config}"
        return content
    


class WerewolfGameOutcomeTool(BaseToolModel):
    name = "狼人杀-结果输出"
    description = "狼人杀的结果输出工具，判断狼人杀游戏中最终的胜利方是谁。"

    class ToolInputArgs(BaseModel):
        pass

    class ToolOutputArgs(BaseModel):
        reason: str
        角色分配结果为: str
        获胜方为: str

    @classmethod
    def run(cls, **kwargs) -> ToolOutputArgs:
        """Execute your tool!"""
        template = (
            '##本局游戏历史记录##\n'
            '{memory}\n'
            '\n'
            '##背景##\n'
            '您正在参与“狼人杀”这个游戏，角色是[主持人]。现在游戏已经结束，您需要判断胜利的一方是谁。\n'
            '\n'
            '##任务##\n'
            '统计目前存活的[好人]玩家数量、[狼人]玩家数量。判断以下条件中的哪一个满足：\n'
            '1. 存活的“狼人”玩家数量为0。\n'
            '2. “狼人”数量超过了“好人”数量。\n'
            '3. “狼人”数量等于“好人”数量，“女巫”已死亡或者她的毒药已经使用。\n'
            '如果条件1满足，则[好人]胜利；如果条件2或者条件3满足，则[狼人]胜利。\n'
            '\n'
            '##输出##\n'
            'Python可直接解析的jsonstr，格式如下：\n'
            '{{\"原因是\": 获胜者为[好人]或[狼人]的原因, \"角色分配结果为\": 所有玩家的角色(根据本局游戏历史记录), \"获胜方为\": \"好人\" or \"狼人\"}}\n'
            '以{{开头，任何其他内容都是不允许的！\n'
            '\n'
            '##输出示例##\n'
            '{{\"原因是\": \"狼人数量为0\", \"角色分配结果为\": \"沈强：身份为狼人_1；周欣怡：身份为狼人_2；梁军：身份为狼人_3；贺子轩：身份为平民_1；人类玩家：身份为平民_2；朱丽：身份为预言家；韩刚：身份为女巫；周杰：身份为猎人。\", \"获胜方为\": \"好人\"}}\n'
            '\n'
            '##注意##\n'
            '请输出所有玩家的角色分配结果，不要遗漏信息。\n'
            '\n'
            '##结果##\n'
            '\n'
        )
        
        model_config = None
        try:
            model_config = ModelConfig(
                config_name="codefuse_default",
                model_type=os.environ.get("DEFAULT_MODEL_TYPE"),
                model_name=os.environ.get("DEFAULT_MODEL_NAME"),
                api_key=os.environ.get("DEFAULT_API_KEY"),
                api_url=os.environ.get("DEFAULT_API_URL"),
            )
            memory = kwargs.get("memory") or ""
            model = get_model(model_config)
            content = model.predict(template.format(memory=memory))
        except Exception as e:
            content = f"无法正确调用模型: {e}, {model_config}"
        return content