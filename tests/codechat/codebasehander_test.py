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

# local debug
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.codechat.codebase_handler.codebase_handler import CodeBaseHandler
from muagent.base_configs.env_config import CB_ROOT_PATH


llm_config = LLMConfig(
    model_name=model_name, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)


# delete codebase
codebase_name = 'client_local'
code_path = "D://chromeDownloads/devopschat-bot/client_v2/client"
use_nh = True # if you dont have nebula graph, it will use local version
do_interpret = True

cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.delete_codebase(codebase_name=codebase_name)


# initialize codebase
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.import_code(do_interpret=do_interpret)


# require class code node
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
vertexes = cbh.search_vertices(vertex_type="class") # method/class


# search_type = [tag, cypher, description] if you have llm and nebula-api
code_text, related_vertex = cbh.search_code(query="remove函数做什么", search_type="tag", limit = 3)
print(code_text)