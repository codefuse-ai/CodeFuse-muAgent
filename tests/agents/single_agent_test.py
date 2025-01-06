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
from muagent.agents import SingleAgent, BaseAgent
from muagent import get_project_config_from_env



# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"

role_prompt = "you are a helpful assistant!"
role_prompt = """#### AGENT PROFILE
you are a helpful assistant!

#### RESPONSE OUTPUT FORMAT
**Action Status:** Set to 'stopped' or 'code_executing'. 
If it's 'stopped', the action is to provide the final answer to the session records and executed steps. 
If it's 'code_executing', the action is to write the code.

**Action:** 
```python
# Write your code here
...
```
"""

role_prompt = """#### AGENT PROFILE
you are a helpful assistant!

#### RESPONSE OUTPUT FORMAT
**Action Status:** Set to either 'stopped' or 'tool_using'. If 'stopped', provide the final response to the original question. If 'tool_using', proceed with using the specified tool.

**Action:** Use the tools by formatting the tool action in JSON. The format should be:

```json
{
  "tool_name": "$TOOL_NAME",
  "tool_params": "$INPUT"
}
```
"""

tools = list(TOOL_SETS)
tools = ["KSigmaDetector", "MetricsQuery"]


AGENT_CONFIGS = {
    "codefuse_simpler": {
        "agent_type": "SingleAgent",
        "agent_name": "codefuse_simpler",
        "tools": tools,
        "llm_config_name": "qwen_chat"
    }
}
os.environ["AGENT_CONFIGS"] = json.dumps(AGENT_CONFIGS)


project_config = get_project_config_from_env()
agent = BaseAgent.init_from_project_config(
    "codefuse_simpler", project_config
)
# base_agent = SingleAgent(
#     system_prompt=role_prompt,
#     project_config=project_config,
#     tools=tools
# )


question = "用python画一个爱心"
query = Message(
    session_index="agent_test", 
    role_type="user", 
    role_name="user", 
    content=question,
)

# base_agent.pre_print(query)
# output_message = base_agent.step(query)
# print(output_message.input_text)
# print(output_message.content)




query_content = "帮我确认下127.0.0.1这个服务器的在10点是否存在异常，请帮我判断一下"
query = Message(
    role_name="human", 
    role_type="user", 
    input_text=query_content,
)
# base_agent.pre_print(query)
output_message = agent.step(query)
print("### intput ###\n", output_message.input_text)
print("### content ###\n", output_message.content)
print("### step content ###\n", output_message.step_content)