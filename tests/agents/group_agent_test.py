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

from muagent.tools import TOOL_SETS
from muagent.schemas import Message
from muagent.agents import BaseAgent
from muagent.project_manager import get_project_config_from_env


tools = list(TOOL_SETS)
tools = ["KSigmaDetector", "MetricsQuery"]
role_prompt = "you are a helpful assistant!"

AGENT_CONFIGS = {
    "grouper": {
        "agent_type": "GroupAgent",
        "agent_name": "grouper",
        "agents": ["codefuse_reacter_1", "codefuse_reacter_2"]
    },
    "codefuse_reacter_1": {
        "agent_type": "ReactAgent",
        "agent_name": "codefuse_reacter_1",
        "tools": tools,
    },
    "codefuse_reacter_2": {
        "agent_type": "ReactAgent",
        "agent_name": "codefuse_reacter_2",
        "tools": tools,
    }
}
os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)

# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"

# 
project_config = get_project_config_from_env()
agent = BaseAgent.init_from_project_config(
    "grouper", project_config
)

query_content = "帮我确认下127.0.0.1这个服务器的在10点是否存在异常，请帮我判断一下"
query = Message(
    role_name="human", 
    role_type="user", 
    content=query_content,
)
# agent.pre_print(query)
output_message = agent.step(query)
print("input:", output_message.input_text)
print("content:", output_message.content)
print("step_content:", output_message.step_content)