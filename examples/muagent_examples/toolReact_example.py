import os, sys, json
from loguru import logger

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


from muagent.tools import toLangchainTools, TOOL_DICT, TOOL_SETS
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.connector.phase import BasePhase
from muagent.connector.schema import Message


# 
llm_config = LLMConfig(
    model_name=model_name, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)


# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"

phase_name = "toolReactPhase"
phase = BasePhase(
    phase_name, embed_config=embed_config, llm_config=llm_config
)


# round-1
tools = toLangchainTools([TOOL_DICT[i] for i in TOOL_SETS if i in TOOL_DICT])
query_content = "帮我确认下127.0.0.1这个服务器的在10点是否存在异常，请帮我判断一下"
query = Message(
    role_name="human", role_type="user", tools=tools, input_query=query_content,
    )

# phase.pre_print(query)
output_message, output_memory = phase.step(query)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))