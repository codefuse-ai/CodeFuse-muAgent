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
    model_engine = os.environ["model_engine"]
    
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
    model_engine = ""
    embed_model = ""
    embed_model_path = ""
    embeddings = None
    logger.error(f"{e}")


# # test local code
# src_dir = os.path.join(
#     os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# )
# sys.path.append(src_dir)
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.connector.phase import BasePhase
from muagent.connector.schema import Message
from muagent.base_configs.env_config import JUPYTER_WORK_PATH

# log-level，print prompt or llm predict
os.environ["log_verbose"] = "0"

llm_config = LLMConfig(
    model_name=model_name, model_engine=model_engine, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)


# if you want to analyze a data.csv, please put the csv file into a jupyter_work_path (or your defined path)
import shutil
source_file = 'D://project/gitlab/llm/external/ant_code/Codefuse-chatbot/jupyter_work/employee_data.csv'
shutil.copy(source_file, JUPYTER_WORK_PATH)

# 
phase_name = "baseTaskPhase"
phase = BasePhase(
    phase_name, embed_config=embed_config, llm_config=llm_config, 
)
# round-1
query_content = "确认本地是否存在employee_data.csv，并查看它有哪些列和数据类型;然后画柱状图"
query = Message(
    role_name="human", role_type="user", input_query=query_content,
)

output_message, output_memory = phase.step(query)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))