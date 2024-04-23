import os
from loguru import logger

try:
    import os, sys
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
    
    try:
        from test_config import BgeBaseChineseEmbeddings
        embeddings = BgeBaseChineseEmbeddings()
    except:
        embeddings = None
except Exception as e:
    # set your config
    api_key = ""
    api_base_url= ""
    model_name = ""
    embed_model = ""
    embed_model_path = ""
    embeddings = None
    logger.error(f"{e}")


from muagent.base_configs.env_config import JUPYTER_WORK_PATH
from muagent.tools import toLangchainTools, TOOL_DICT, TOOL_SETS
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.connector.phase import BasePhase
from muagent.connector.schema import Message

#
tools = toLangchainTools([TOOL_DICT[i] for i in TOOL_SETS if i in TOOL_DICT])


# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"

# embedding and llm config
llm_config = LLMConfig(
    model_name=model_name, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)

if embeddings:
    embed_config = EmbedConfig(
        embed_model="default",
        langchain_embeddings=embeddings
    )
else:
    embed_config = EmbedConfig(
        embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
    )

# 
phase_name = "baseGroupPhase"
phase = BasePhase(
    phase_name, embed_config=embed_config, llm_config=llm_config
)


# if you want to analyze a data.csv, please put the csv file into a jupyter_work_path (or your defined path)
import shutil
source_file = 'D://project/gitlab/llm/external/ant_code/Codefuse-chatbot/jupyter_work/employee_data.csv'
shutil.copy(source_file, JUPYTER_WORK_PATH)


# round-1
query_content = "确认本地是否存在employee_data.csv，并查看它有哪些列和数据类型;然后画柱状图"
query = Message(
    role_name="human", role_type="user", tools=tools, input_query=query_content,
)
# phase.pre_print(query)
output_message, output_memory = phase.step(query)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))

# # round-2
# query_content = "帮我确认下127.0.0.1这个服务器的在10点是否存在异常，请帮我判断一下"
# query = Message(
#     role_name="human", role_type="user", tools=tools, input_query=query_content,
# )
# # phase.pre_print(query)
# output_message, output_memory = phase.step(query)
# print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))