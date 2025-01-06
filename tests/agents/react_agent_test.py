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
from muagent import get_project_config_from_env

# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"

tools = list(TOOL_SETS)
tools = ["KSigmaDetector", "MetricsQuery"]
role_prompt = "you are a helpful assistant!"

AGENT_CONFIGS = {
    "reacter": {
        "system_prompt": role_prompt,
        "agent_type": "ReactAgent",
        "agent_name": "reacter",
        "tools": tools,
        "llm_config_name": "qwen_chat"
    }
}
os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)

# 
project_config = get_project_config_from_env()
agent = BaseAgent.init_from_project_config(
    "reacter", project_config
)

query_content = "帮我确认下127.0.0.1这个服务器的在10点是否存在异常，请帮我判断一下"
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