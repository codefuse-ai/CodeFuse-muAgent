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

from muagent.tools import toLangchainTools, TOOL_DICT, TOOL_SETS

from muagent.schemas import Message
from muagent.models import ModelConfig
from muagent.agents import BaseAgent
from muagent import get_project_config_from_env


# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"


tools = list(TOOL_SETS)
tools = ["KSigmaDetector", "MetricsQuery"]
role_prompt = "you are a helpful assistant!"

AGENT_CONFIGS = {
    "tasker": {
        "system_prompt": role_prompt,
        "agent_type": "TaskAgent",
        "agent_name": "tasker",
        "tools": tools,
        "llm_config_name": "qwen_chat"
    }
}
os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)

# 
project_config = get_project_config_from_env()
agent = BaseAgent.init_from_project_config(
    "tasker", project_config
)

query_content = "先帮我获取下127.0.0.1这个服务器在10点的数，然后在帮我判断下数据是否存在异常"
query = Message(
    role_name="human", 
    role_type="user", 
    content=query_content,
)
# agent.pre_print(query)
output_message = agent.step(query)
print("### intput ###\n", output_message.input_text)
print("### content ###\n", output_message.content)
print("### step content ###\n", output_message.step_content)