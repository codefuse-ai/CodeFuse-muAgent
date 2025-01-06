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


class SeatAssignerTool(BaseToolModel):
    """
    This tool assigns seat positions to players and formats them in a markdown table.
    Example Output: 
    ```
    | 座位 | 玩家 |
    |---|---|
    | 1 | **张伟** |
    | 2 | **李静** |
    | 3 | **王鹏** |
    | 4 | **人类玩家** |
    ```
    """
    name: str = "谁是卧底-座位分配"
    description: str = "谁是卧底的座位分配工具，可以将玩家顺序打乱随机分配座位"
    
    class ToolInputArgs(BaseModel):
        """Input for SeatAssigner."""
        pass  # No specific parameters required for this tool

    class ToolOutputArgs(BaseModel):
        """Output for SeatAssigner."""
        table: str = Field(..., description="Markdown table of seating arrangement")

    @classmethod
    def run(cls, **kwargs) -> str:
        """Execute the seat assignment tool."""
        players = [["张伟", "agent_张伟"], ["李静", "agent_李静"], ["王鹏", "agent_王鹏"], ["人类玩家", "agent_人类玩家"]]
        # Shuffle players to assign them to random seats
        random.shuffle(players)
        # Create the markdown table
        markdown_table = "\n\n| 座位 | 玩家 |\n|---|---|\n" + "\n".join(
            f"| {i+1} | **{players[i][0]}** |" for i in range(len(players))
        )
        return markdown_table


class RoleAssignerTool(BaseToolModel):
    """
    This class assigns roles and words to players in a game.
    The output will include player names, agent names, agent descriptions, and secret words based on their role type.
    """
    name: str = "谁是卧底-角色分配"
    description: str = "谁是卧底的角色分配工具，可以为每一位玩家分配一个单词和人物角色。"
    
    class ToolInputArgs(BaseModel):
        """Input for assigning roles."""
        pass
    
    class ToolOutputArgs(BaseModel):
        """Output for assigned roles."""
        roles: List[Dict[str, str]] = Field(..., description="List of roles assigned to players")

    @classmethod
    def run(cls, **kwargs) -> List[Dict[str, str]]:
        words = [
            ["苹果", "梨"],
            ["猫", "狗"],
            ["摩托车", "自行车"],
            ["太阳", "月亮"],
            ["红色", "粉色"],
            ["大象", "长颈鹿"],
            ["铅笔", "钢笔"],
            ["牛奶", "豆浆"],
            ["河", "湖"],
            ["面包", "蛋糕"],
            ["饺子", "包子"],
            ["冬天", "夏天"],
            ["电视", "电脑"],
            ["铅笔", "橡皮"],
            ["跑步", "游泳"],
            ["手机", "平板"],
            ["鱼", "虾"],
            ["空调", "风扇"],
            ["马", "驴"],
            ["书", "杂志"],
            ["草", "树"],
            ["杯子", "碗"],
            ["米饭", "面条"],
            ["饼干", "蛋糕"],
            ["雨伞", "雨衣"],
            ["猪", "牛"],
            ["白菜", "生菜"],
            ["吉他", "钢琴"],
            ["飞机", "火车"],
            ["镜子", "眼镜"]
        ]

        player_names = ["张伟", "李静", "王鹏", "人类玩家"]
        roles = ["平民_1", "平民_2", "平民_3", "卧底_1"]
        random.shuffle(player_names)
        random.shuffle(roles)
        
        word_idx = random.randint(0, len(words) - 1)
        under_cover_word_idx = random.randint(0, 1)

        result = []
        for i in range(len(player_names)):
            r = {
                "player_name": player_names[i],
                "agent_name": f"agent_{player_names[i]}",
                "agent_description": roles[i],
                "单词": words[word_idx][1 - under_cover_word_idx] if roles[i].startswith("平民") else words[word_idx][under_cover_word_idx]
            }
            result.append(r)

        return result


class GameActionTool(BaseToolModel):
    name = "谁是卧底-游戏行动"
    description = "谁是卧底的游戏行动工具，需要根据记忆的上下文信息，当前任务、以及你拿到的单词信息来进行回答响应。"

    class ToolInputArgs(BaseModel):
        pass

    class ToolOutputArgs(BaseModel):
        content: str

    @classmethod
    def run(cls, **kwargs) -> str:
        """Execute your tool!"""
        
        template = (
            '##背景##\n'
            '您正在参加“谁是卧底”这款游戏，您的目标是：想办法击杀与自己身份不同的所有玩家，获得胜利。\n'
            '\n'
            '##游戏介绍##\n'
            '在“谁是卧底”游戏中，每位玩家会被分配一个[单词]（玩家可见）和一个身份（玩家不可见，包括[平民]和[卧底]两种身份），卧底的[单词]跟[平民]不同，但有许多共同的特征。\n'
            '\n'
            '##任务##\n'
            '1. 根据**游戏进展中主持人的最新通知**，感知当前的任务：讨论 or 票选卧底，准备发言。\n'
            '2. 如果任务是讨论，感知分配给您的[单词]，描述它的某一特征（**描述内容可真可假，禁止描述已经提到过的特征**），您的目标是：让其他玩家相信该特征与他们的[单词]是相符的；否则，投票给某个当前存活玩家，并说明理由，您的目标是：让其他玩家相信，该玩家给出的特征与大家的[单词]都不符。\n'
            '\n'
            '##发言示例##\n'
            '（任务是讨论）一种植物，可食用。\n'
            '（任务是票选卧底）我投票给李静，因为对比所有人的发言，他的描述和其他的有明显区别。\n'
            '\n'
            '##游戏进展##\n'
            '{memory}\n'
            '\n'
            '##注意##\n'
            '- 无论您的任务是什么，**禁止泄露自己的[单词]，发言内容尽可能简洁！！！**。\n'
            '- 如果您的任务是讨论，**描述的特征可真可假，但要避免已经提到过的特征**；如果是票选卧底，**一定要明确表示投票给哪一位玩家（禁止给自己或已经死亡的玩家投票）**。\n'
            '- 禁止描述任何没有发生过的事情。\n'
            '\n'
            '##游戏经验##\n'
            '如果任务是讨论，以下是描述[单词]特征时的一些经验：\n'
            '1. 保持模糊性：特征不宜过于明显（尤其当您是首位发言的玩家时），这样很容易别人推测出自己的[单词]。\n'
            '2. 逐渐清晰：与其他玩家给出的特征相比，您的特征应该更清晰，否则很容易被其他玩家怀疑。\n'
            '3. 定位身份：如果您发现多个玩家的特征跟您的[单词]都不符，那么自己的身份很可能是[卧底]，应该推测他们的[单词]是什么，**编造**跟他们[单词]相符的特征。\n'
            '\n'
            '##输出##\n'
            'Python可直接解析的jsonstr，格式如下：\n'
            '{{\"thought\": 感知自己的名字、位置（根据主持人的【身份通知】!!!注意您不是人类玩家）、[单词]、当前任务、哪些特征已经被提出来、推测其他玩家的[单词]是什么、自己是否是[卧底]、如何保护自己，分析内容不超过120字, \"output\": 您的发言（避免泄露[单词]，避免投票给自己，避免重复特征，直接说出符合您的身份的话，不要输出其他信息）}}\n'
            '以{{开头，任何其他内容都是不允许的！\n'
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
    

class AgentZhangweiTool(GameActionTool):
    name = "谁是卧底-张伟"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与谁是卧底这场游戏，在游戏中你的名字是李静"
    )

class AgentLijingTool(GameActionTool):
    name = "谁是卧底-李静"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与谁是卧底这场游戏，在游戏中你的名字是李静"
    )


class AgentWangpengTool(GameActionTool):
    name = "谁是卧底-王鹏"
    description = (
        f"你是一个智能体(Agent)，你正在模拟玩家参与谁是卧底这场游戏，在游戏中你的名字是李静"
    )


class GameEndCheckerTool(BaseToolModel):
    name = "谁是卧底-胜利条件判断"
    description = "谁是卧底的胜利条件判断工具，判断当前谁是卧底游戏是否结束。"

    class ToolInputArgs(BaseModel):
        pass

    class ToolOutputArgs(BaseModel):
        content: str

    @classmethod
    def run(cls, **kwargs) -> str:
        """Execute your tool!"""

        template = (
            '##本局游戏历史记录##\n'
            '{memory}\n\n'
            '##背景##\n'
            '你是一个逻辑判断大师，你正在参与“谁是卧底”这个游戏，你的角色是[主持人]。你熟悉“谁是卧底”游戏的完整流程，现在需要判断当前游戏是否结束。\n\n'
            '##任务##\n'
            '你的任务是判断当前游戏是否结束，规则如下：\n'
            '根据【重要信息】感知每一轮被投票死亡的玩家。 统计目前存活的[平民]玩家数量、[卧底]玩家数量。格式{{\"存活的卧底\":[player_name], \"存活的平民\":[player_name]}},判断以下条件中的一个是否满足：\n'
            '1. \t卧底玩家全部已经死亡（即 存活[卧底]数量为0）。\n'
            '2.  存活的[平民]数量与存活的[卧底]数量相等。\n'
            '如果其中一个条件满足，则游戏结束；否则，游戏需要继续。\n\n'
            '##输出##\n'
            '返回jsonstr 格式。{{\"thought\": str, \"存活的玩家信息\": {{\"存活的卧底\":[player_name], \"存活的平民\":[player_name]}}, \"isEnd\": \"是\" or \"否\"}}\n'
            '-thought **根据本局游戏历史记录** 分析 游戏最开始有哪些玩家, 他们的身份是什么, 投票导致死亡的玩家有哪些? 分析当前存活的玩家有哪些 ? 是否触发了游戏结束条件? 等等\n\n'
            '##注意事项##\n'
            '1. 所有玩家的座位、身份、agent_name、存活状态、游戏进展等信息在开头部分已给出。\n'
            '2. \"是\" or \"否\" 如何选择？若游戏结束，则为\"是\"，否则为\"否\"。\n'
            '3. 请直接输出jsonstr，不用输出markdown格式。\n\n'
            '4. 游戏可能进行了不只一轮，可能有1个或者2个玩家已经死亡，请注意感知\n'
            '##结果##\n\n'
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

class GameOutcomeCheckerTool(BaseToolModel):
    name = "谁是卧底-结果输出"
    description = "谁是卧底的结果输出工具，判断谁是卧底游戏中最终的胜利方是谁，并输出角色分配情况"

    class ToolInputArgs(BaseModel):
        pass

    class ToolOutputArgs(BaseModel):
        content: str

    @classmethod
    def run(cls, **kwargs) -> str:
        """Execute your tool!"""

        template = (
            '##本局游戏历史记录##\n'
            '{memory}\n'
            '\n'
            '##背景##\n'
            '您正在参与“谁是卧底”这个游戏，角色是[主持人]。现在游戏已经结束，您需要判断胜利的一方是谁。\n'
            '\n'
            '##任务##\n'
            '统计目前存活的[平民]玩家数量、[卧底]玩家数量。判断以下条件中的哪一个满足：\n'
            '1.[卧底]数量为0。\n'
            '2.[平民]数量与[卧底]数量相等。\n'
            '如果条件1满足，则[平民]胜利；如果条件2满足，则[卧底]胜利。\n'
            '\n'
            '##输出##\n'
            'Python可直接解析的jsonstr，格式如下：\n'
            '{{\"原因是\": 获胜者为[平民]或[卧底]的原因, \"角色分配结果为\": 所有玩家的身份和单词(根据本局游戏历史记录), \"获胜方为\": \"平民\" or \"卧底\"}}\n'
            '以{{开头，任何其他内容都是不允许的！\n'
            '\n'
            '##输出示例##\n'
            '{{\"原因是\": \"卧底数量为0\", \"角色分配结果为\": \"李静：身份为卧底，单词为香蕉；人类玩家:身份为平民, 单词为梨子; 张伟:身份为平民, 单词为梨子; 王鹏：身份为平民, 单词为梨子。\", \"获胜方为\": \"平民\"}}\n'
            '\n'
            '##注意##\n'
            '请输出所有玩家的角色分配结果，不要遗漏信息\n'
            '\n'
            '##结果##\n\n'
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