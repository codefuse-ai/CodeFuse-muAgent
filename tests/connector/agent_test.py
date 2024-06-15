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
from muagent.connector.agents import BaseAgent, ReactAgent, ExecutorAgent, SelectorAgent
from muagent.connector.schema import Role, Message
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
os.environ["log_verbose"] = "0"

tools = toLangchainTools([TOOL_DICT[i] for i in TOOL_SETS if i in TOOL_DICT])[:3]

# role_prompt = "you are a helpful assistant!"
# prompt = """#### AGENT PROFILE
# you are a helpful assistant!

# #### RESPONSE OUTPUT FORMAT
# **Action Status:** finished or continued
# If it's 'finished', the context can answer the origin query.
# If it's 'continued', the context cant answer the origin query.

# **response:** Incorporate the context of the SESSION RECORDS, answer question concisely and professionally.
# """
# role = Role(role_type="assistant", role_name="qaer", role_prompt=role_prompt, prompt=prompt)
# base_agent = BaseAgent(
#     role=role,
#     task="",
#     focus_agents=[],
#     focus_message_keys=[],
#     llm_config=llm_config, embed_config=embed_config,
# )

# query = Message(
#     chat_index="test1", user_name="test", role_type="user", role_name="user", input_query="hello!",
#     tools=tools,
# )
# # base_agent.pre_print(query)
# output_message = base_agent.step(query)
# print(output_message.input_query)
# print(output_message.role_content)



# role_prompt = """When interacting with users, your role is to respond in a helpful and accurate manner using the tools available. Follow the steps below to ensure efficient and effective use of the tools.

# Please note that all the tools you can use are listed below. You can only choose from these tools for use. 

# If there are no suitable tools, please do not invent any tools. Just let the user know that you do not have suitable tools to use.

# ATTENTION: The Action Status field ensures that the tools or code mentioned in the Action can be parsed smoothly. Please make sure not to omit the Action Status field when replying."""

# role = Role(role_type="assistant", role_name="qaer", role_prompt=role_prompt)
# base_agent = ReactAgent(
#     role=role,
#     task="",
#     chat_turn=3,
#     focus_agents=[],
#     focus_message_keys=[],
#     llm_config=llm_config, embed_config=embed_config,
# )

# question = "帮我确认下127.0.0.1这个服务器的在10点是否存在异常，请帮我判断一下"
# query = Message(
#     chat_index="test2", user_name="test", role_type="user", role_name="user", input_query=question,
#     tools=tools,
# )
# # base_agent.pre_print(query)
# output_message = base_agent.step(query)
# print(output_message.input_query)
# print(output_message.role_content)



# role_prompt = """When users need help with coding or using tools, your role is to provide precise and effective guidance. 
# Use the tools provided if they can solve the problem, otherwise, write the code step by step, showing only the part necessary to solve the current problem. 
# Each reply should contain only the guidance required for the current step either by tool usage or code. 
# ATTENTION: The Action Status field ensures that the tools or code mentioned in the Action can be parsed smoothly. Please make sure not to omit the Action Status field when replying."""

# role = Role(role_type="assistant", role_name="qaer", role_prompt=role_prompt)
# base_agent = ExecutorAgent(
#     role=role,
#     task="",
#     chat_turn=3,
#     focus_agents=[],
#     focus_message_keys=[],
#     llm_config=llm_config, embed_config=embed_config,
# )

# question = "[导入pandas、numpy、matplotlib，生成正弦函数的值，画出正弦函数]"
# query = Message(
#     chat_index="test3", user_name="test", role_type="user", role_name="user", input_query=question,
#     tools=tools,
# )
# # base_agent.pre_print(query)
# output_message = base_agent.step(query)
# print(output_message.input_query)
# print(output_message.role_content)



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
    chat_turn=3,
    focus_agents=[],
    focus_message_keys=[],
    llm_config=llm_config, embed_config=embed_config,
)


code_role = Role(role_type="assistant", role_name="code_reacter", prompt=REACT_CODE_PROMPT)
code_react_agent = ReactAgent(
    role=code_role,
    chat_turn=3,
    focus_agents=[],
    focus_message_keys=[],
    llm_config=llm_config, embed_config=embed_config,
)


role = Role(role_type="assistant", role_name="qaer", prompt=prompt)
base_agent = SelectorAgent(
    role=role,
    chat_turn=3,
    focus_agents=[],
    focus_message_keys=[],
    llm_config=llm_config, embed_config=embed_config,
    group_agents=[tool_react_agent, code_react_agent]
)

question = "确认本地是否存在employee_data.csv，并查看它有哪些列和数据类型;然后画柱状图"
query = Message(
    chat_index="agent_test", user_name="test", role_type="user", role_name="user", input_query=question,
    tools=tools,
)
# base_agent.pre_print(query)
output_message = base_agent.step(query)
print(output_message.input_query)
print(output_message.parsed_output_list)
