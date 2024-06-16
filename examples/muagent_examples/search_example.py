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
from muagent.tools import toLangchainTools, TOOL_DICT, TOOL_SETS
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig

from muagent.connector.phase import BasePhase
from muagent.connector.schema import Message, Memory



# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"

# 
llm_config = LLMConfig(
    model_name=model_name, model_engine=model_engine, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)

# 当duckduckgo连接不通的时候可以配置这个
os.environ["DUCKDUCKGO_PROXY"] = os.environ.get("DUCKDUCKGO_PROXY") or "socks5h://127.0.0.1:13659"

phase_name = "searchChatPhase"
phase = BasePhase(
    phase_name, embed_config=embed_config, llm_config=llm_config
)

# round-1
query_content1 = "美国当前总统是谁？"
query = Message(
    chat_index="search_test",role_name="human", role_type="user", input_query=query_content1,
    search_engine_name="duckduckgo", score_threshold=1.0, top_k=3
    )

output_message, output_memory = phase.step(query)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))

# round-2
query_content2 = "美国上一任总统是谁，两个人有什么关系没？"
query = Message(
    chat_index="search_test", role_name="human", role_type="user", input_query=query_content2,
    search_engine_name="duckduckgo", score_threshold=1.0, top_k=3
    )
output_message, output_memory = phase.step(query)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))