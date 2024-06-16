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
from muagent.base_configs.env_config import CB_ROOT_PATH
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.connector.phase import BasePhase
from muagent.connector.schema import Message, Memory
from muagent.codechat.codebase_handler.codebase_handler import CodeBaseHandler


# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"


llm_config = LLMConfig(
    model_name=model_name, model_engine=model_engine, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)


# delete codebase
codebase_name = 'client_local'
code_path = "D://chromeDownloads/devopschat-bot/client_v2/client"
# initialize codebase
use_nh = True
do_interpret = True
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.delete_codebase(codebase_name=codebase_name)


# initialize codebase
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.import_code(do_interpret=do_interpret)


# 
phase_name = "codeChatPhase"
phase = BasePhase(
    phase_name, embed_config=embed_config, llm_config=llm_config,
)


# # round-1
# query_content = "代码一共有多少类"
# query = Message(
#     chat_index="codechat_test", role_name="human", role_type="user", input_query=query_content,
#     code_engine_name=codebase_name, score_threshold=1.0, top_k=3, cb_search_type="cypher",
#     local_graph_path=CB_ROOT_PATH, use_nh=use_nh
#     )

# output_message1, output_memory1 = phase.step(query)
# print(output_memory1.to_str_messages(return_all=True, content_key="parsed_output_list"))

# # round-2
# query_content = "代码库里有哪些函数，返回5个就行"
# query = Message(
#     chat_index="codechat_test", role_name="human", role_type="user", input_query=query_content,
#     code_engine_name=codebase_name, score_threshold=1.0, top_k=3, cb_search_type="cypher",
#     local_graph_path=CB_ROOT_PATH, use_nh=use_nh
#     )
# output_message2, output_memory2 = phase.step(query)
# print(output_memory2.to_str_messages(return_all=True, content_key="parsed_output_list"))


# # round-3
query_content = "remove 这个函数是做什么的"
query = Message(
    chat_index="codechat_test", role_name="user", role_type="human", input_query=query_content,
    code_engine_name=codebase_name, score_threshold=1.0, top_k=3, cb_search_type="tag",
    local_graph_path=CB_ROOT_PATH, use_nh=use_nh
    )
output_message3, output_memory3 = phase.step(query)
# print(output_message3)
print(output_memory3.to_str_messages(return_all=True, content_key="parsed_output_list"))

# round-4
query_content = "有没有函数已经实现了从字符串删除指定字符串的功能，使用的话可以怎么使用，写个java代码"
query = Message(
    chat_index="codechat_test", role_name="human", role_type="user", input_query=query_content,
    code_engine_name=codebase_name, score_threshold=1.0, top_k=3, cb_search_type="description",
    local_graph_path=CB_ROOT_PATH, use_nh=use_nh
    )
output_message4, output_memory4 = phase.step(query)
# print(output_message4)
print(output_memory4.to_str_messages(return_all=True, content_key="parsed_output_list"))

# round-5
query_content = "有根据我以下的需求用 java 开发一个方法：输入为字符串，将输入中的 .java 字符串给删除掉，然后返回新的字符串"
query = Message(
    chat_index="codechat_test", role_name="human", role_type="user", input_query=query_content,
    code_engine_name=codebase_name, score_threshold=1.0, top_k=3, cb_search_type="description",
    local_graph_path=CB_ROOT_PATH, use_nh=use_nh
    )
output_message5, output_memory5 = phase.step(query)
# print(output_message5)
print(output_memory5.to_str_messages(return_all=True, content_key="parsed_output_list"))