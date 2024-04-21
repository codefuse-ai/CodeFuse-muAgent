import os, sys
from loguru import logger


os.environ["do_create_dir"] = "1"

try:
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
    api_key = os.environ["OPENAI_API_KEY"]
    api_base_url= os.environ["API_BASE_URL"]
    model_name = os.environ["model_name"]
    embed_model = os.environ["embed_model"]
    embed_model_path = os.environ["embed_model_path"]
except Exception as e:
    # set your config
    api_key = ""
    api_base_url= ""
    model_name = ""
    embed_model = ""
    embed_model_path = ""
    logger.error(f"{e}")

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

sys.path.append(src_dir)

from muagent.base_configs.env_config import JUPYTER_WORK_PATH
from muagent.connector.agents import BaseAgent, ReactAgent, ExecutorAgent, SelectorAgent
from muagent.connector.chains import BaseChain
from muagent.connector.phase import BasePhase
from muagent.connector.schema import Role, Message, ChainConfig
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.tools import toLangchainTools, TOOL_DICT, TOOL_SETS


llm_config = LLMConfig(
    model_name=model_name, api_key=api_key,  api_base_url=api_base_url, temperature=0.3,
    stop="**Observation:**"
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)

# log-level，print prompt和llm predict
os.environ["log_verbose"] = "2"

tools = toLangchainTools([TOOL_DICT[i] for i in TOOL_SETS if i in TOOL_DICT])[:3]


prompt = """#### Agent Profile

Your goal is to response according the Context Data's information with the role that will best facilitate a solution, taking into account all relevant context (Context) provided.

When you need to select the appropriate role for handling a user's query, carefully read the provided role names, role descriptions and tool list.

ATTENTION: response carefully referenced "Response Output Format" in format.

#### Response Output Format

**Thoughts:** think the reason step by step about why you selecte one role

**Role:** Select the role from agent names.
"""
from muagent.connector.configs.prompts import REACT_CODE_PROMPT, REACT_TOOL_PROMPT

tool_role = Role(role_type="assistant", role_name="tool_reacter", prompt=REACT_TOOL_PROMPT)
tool_react_agent = ReactAgent(
    role=tool_role,
    task="",
    chat_turn=3,
    focus_agents=[],
    focus_message_keys=[],
    llm_config=llm_config, embed_config=embed_config,
)


code_role = Role(role_type="assistant", role_name="code_reacter", prompt=REACT_CODE_PROMPT)
code_react_agent = ReactAgent(
    role=code_role,
    task="",
    chat_turn=3,
    focus_agents=[],
    focus_message_keys=[],
    llm_config=llm_config, embed_config=embed_config,
)


role = Role(role_type="assistant", role_name="qaer", prompt=prompt)
base_agent = SelectorAgent(
    role=role,
    task="",
    chat_turn=3,
    focus_agents=[],
    focus_message_keys=[],
    llm_config=llm_config, embed_config=embed_config,
    group_agents=[tool_react_agent, code_react_agent]
)

chain_config = ChainConfig(chain_name="group_chain", agents=[base_agent.role.role_name], chat_turn=1)
base_chain = BaseChain(
    chainConfig=chain_config, agents=[base_agent], 
    llm_config=llm_config, embed_config=embed_config,
)

base_phase = BasePhase(
    phase_name="group_phase", chains=[base_chain],
    embed_config=embed_config, llm_config=llm_config
)
# if you want to analyze a data.csv, please put the csv file into a jupyter_work_path (or your defined path)
import shutil
source_file = 'D://project/gitlab/llm/external/ant_code/Codefuse-chatbot/jupyter_work/employee_data.csv'
shutil.copy(source_file, JUPYTER_WORK_PATH)

question = "确认本地是否存在employee_data.csv，并查看它有哪些列和数据类型;然后画柱状图"
query = Message(
    user_name="test", role_type="user", role_name="user", input_query=question,
    tools=tools,
)

# base_phase.pre_print(query)
output_message, output_memory = base_phase.step(query)
print(output_message.input_query)
print(output_message.role_content)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))