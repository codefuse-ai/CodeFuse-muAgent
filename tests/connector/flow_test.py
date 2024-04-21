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


from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.codechat.codebase_handler.codebase_handler import CodeBaseHandler
from muagent.base_configs.env_config import CB_ROOT_PATH

llm_config = LLMConfig(
    model_name=model_name, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)
# define your customized llm
# llm_config = LLMConfig(llm=ReadingModel())

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)
# define your customized embeddings
# embeddings = BgeBaseChineseEmbeddings()
# embed_config = EmbedConfig(langchain_embeddings=embeddings)


# delete codebase
codebase_name = 'client_local'
code_path = "D://chromeDownloads/devopschat-bot/client_v2/client"
use_nh = True
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.delete_codebase(codebase_name=codebase_name)


# initialize codebase
codebase_name = 'client_local'
code_path = "D://chromeDownloads/devopschat-bot/client_v2/client"
use_nh = True
do_interpret = True
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.import_code(do_interpret=do_interpret)


from muagent.connector.antflow import AgentFlow, ChainFlow, PhaseFlow
from muagent.connector.configs.prompts import QA_TEMPLATE_PROMPT
from muagent.connector.configs import BASE_PROMPT_CONFIGS
from muagent.retrieval.base_retrieval import BaseCodeRetrieval
import os

agent_flow1 = AgentFlow(
    agent_type="BaseAgent", 
    agent_index=0,
    chat_turn=1,
    role_type = "assistant",
    role_name = "qaer",
    role_prompt = QA_TEMPLATE_PROMPT,
    prompt_config = BASE_PROMPT_CONFIGS,
    focus_agents = [],
    focus_messages = [],
    embed_config= embed_config,
    llm_config = llm_config,
    )

chain_flow1 = ChainFlow(
    chain_name="qaer",
    chain_index=0,
    agent_flows=[agent_flow1],
    chat_turn = 1,
    do_checker = False,
    embed_config= embed_config,
    llm_config = llm_config,
    )

codebase_name = 'client_local'
retrieval = BaseCodeRetrieval(
    codebase_name, embed_config=embed_config, llm_config=llm_config, 
    search_type = 'tag', code_limit = 1, local_graph_path=CB_ROOT_PATH)


# log-level，print prompt和llm predict
os.environ["log_verbose"] = "1"


phase_name = "code_qa_chain"
phase_flow = PhaseFlow(
    phase_name=phase_name, chain_flows=[chain_flow1,],
    embed_config= embed_config,
    llm_config = llm_config,
    code_retrieval=retrieval,
)

query_content = "remove 这个函数是做什么的"
query_content = {"query": "remove 这个函数是做什么的", "search_type": "tag"}
phase_flow(query_content)