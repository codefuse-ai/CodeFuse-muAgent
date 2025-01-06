import os, sys
from loguru import logger
import json

os.environ["do_create_dir"] = "1"

try:
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
except Exception as e:
    # set your config
    logger.error(f"{e}")

# test local code
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)


from muagent.schemas import Message, Memory
from muagent.agents import FunctioncallAgent
from muagent import get_agent, get_project_config_from_env


# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"

AGENT_CONFIGS = {
    "codefuse_function_caller": {
        "config_name": "codefuse_function_caller",
        "agent_type": "FunctioncallAgent",
        "agent_name": "codefuse_function_caller",
        "llm_config_name": "qwener"
    }
}
os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)
project_config = get_project_config_from_env()
tools = ["KSigmaDetector", "MetricsQuery"]
tools = [
    "谁是卧底-座位分配", "谁是卧底-角色分配", "谁是卧底-结果输出", "谁是卧底-胜利条件判断",
    "谁是卧底-张伟", "谁是卧底-李静", "谁是卧底-王鹏",
]

# tools = [
#     "狼人杀-角色分配工具", "狼人杀-座位分配", "狼人杀-胜利条件判断", "狼人杀-结果输出",
#     '狼人杀-agent_朱丽', '狼人杀-agent_周杰', '狼人杀-agent_沈强', '狼人杀-agent_韩刚', 
#     '狼人杀-agent_梁军', '狼人杀-agent_周欣怡', '狼人杀-agent_贺子轩'
# ]

agent = FunctioncallAgent(
    agent_name="codefuse_function_caller",
    project_config=project_config,
    tools=tools
)


memory_content = "[0.857, 2.345, 1.234, 4.567, 3.456, 9.876, 5.678, 7.89, 6.789, 8.901, 10.987, 12.345, 11.234, 14.567, 13.456, 19.876, 15.678, 17.89, 16.789, 18.901, 20.987, 22.345, 21.234, 24.567, 23.456, 29.876, 25.678, 27.89, 26.789, 28.901]"
memory = Memory(
    messages=[Message(
        role_type="observation",
        content=memory_content
    )]
)
query_content = "帮我查询下127.0.0.1这个服务器的在10点的数据"
query_content = "帮我判断这个数据是否异常"
query_content = "开始分配座位"
query_content = "开始分配身份"
query_content = "游戏是否结束"
query_content = "游戏的胜利玩家是谁"

memory_content = "3号玩家说今天天气很好"
memory = Memory(
    messages=[Message(
        role_type="observation",
        content=memory_content
    )]
)
query_content = "我要使用工具，工具描述为agent_张伟"
# query_content = "我要使用工具，工具描述为'agent_周杰'"


query = Message(
    role_name="human", 
    role_type="user", 
    content=query_content,
)
# agent.pre_print(query)
# output_message = agent.step(query, memory=memory)
output_message = agent.step(query, extra_params={"memory": memory_content})
print("### intput ###\n", output_message.input_text)
print("### content ###\n", output_message.content)
print("### observation ###\n", output_message.parsed_contents[-1]["Observation"])
print("### step content ###\n", output_message.step_content)