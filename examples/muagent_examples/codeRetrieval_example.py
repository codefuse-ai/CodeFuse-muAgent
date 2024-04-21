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


from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.connector.agents import BaseAgent, ReactAgent, ExecutorAgent, SelectorAgent
from muagent.connector.chains import BaseChain
from muagent.connector.phase import BasePhase
from muagent.connector.schema import (
    Message, Role, ActionStatus, ChainConfig
    )
from muagent.connector.prompt_manager.prompt_manager import PromptManager
from muagent.codechat.codebase_handler.codebase_handler import CodeBaseHandler
from muagent.base_configs.env_config import CB_ROOT_PATH

from loguru import logger



# update new agent configs
codeRetrievalJudger_PROMPT = """#### Agent Profile

Given the user's question and respective code, you need to decide whether the provided codes are enough to answer the question.

#### Input Format

**Retrieval Codes:** the Retrieval Codes from the code base

#### Response Output Format
**Action Status:** Set to 'finished' or 'continued'. 
If it's 'finished', the provided codes can answer the origin query.
If it's 'continued', the origin query cannot be answered well from the provided code.

**REASON:** Justify the decision of choosing 'finished' and 'continued' by evaluating the progress step by step.
"""

codeRetrievalDivergent_PROMPT = """#### Agent Profile

You are a assistant that helps to determine which code package is needed to answer the question.

Given the user's question, Retrieval code, and the code Packages related to Retrieval code. you need to decide which code package we need to read to better answer the question.

#### Input Format

**Retrieval Codes:** the Retrieval Codes from the code base

**Code Packages:** the code packages related to Retrieval code

#### Response Output Format

**Code Package:** Identify another Code Package from the Code Packages that can most help to provide a better answer to the Origin Query, only put one name of the code package here.

**REASON:** Justify the decision of choosing 'finished' and 'continued' by evaluating the progress step by step.
"""


from muagent.tools import CodeRetrievalSingle, RelatedVerticesRetrival, Vertex2Code

# 定义一个新的类
class CodeRetrievalJudger(BaseAgent):

    def start_action_step(self, message: Message) -> Message:
        '''do action before agent predict '''
        if 'Retrieval_Codes' in message.customed_kargs:
            # already retrive the code
            pass
        else:
            action_json = CodeRetrievalSingle.run(message.code_engine_name, message.input_query, llm_config=self.llm_config, embed_config=self.embed_config, 
                                                  search_type="tag", local_graph_path=message.local_graph_path, use_nh=message.use_nh)
            message.customed_kargs["CodeRetrievalSingleRes"] = action_json
            message.customed_kargs['Current_Vertex'] = action_json['vertex']
            message.customed_kargs.setdefault("Retrieval Codes", [])
            message.customed_kargs["Retrieval Codes"].append(action_json["code"])
        return message


# 定义一个新的类
class CodeRetrievalDivergent(BaseAgent):
    # prepare your key-value align to prompt-input-keys
    def start_action_step(self, message: Message) -> Message:
        '''do action before agent predict '''
        action_json = RelatedVerticesRetrival.run(message.code_engine_name, message.customed_kargs['Current_Vertex'])
        if not action_json['vertices']:
            message.action_status = ActionStatus.FINISHED
        message.customed_kargs["Code Packages"] = [str(i) for i in action_json.get("vertices", [])]
        return message

    # prepare your key-value align to prompt-input-keys
    def end_action_step(self, message: Message) -> Message:
        '''do action before agent predict '''
        # logger.error(f"message: {message}")
        action_json = Vertex2Code.run(message.code_engine_name, message.parsed_output["Code Package"])
        # logger.debug(f'action_json={action_json}')
        if not action_json['code']:
            message.action_status = ActionStatus.FINISHED
            return message

        message.customed_kargs["Vertex2Code"] = action_json
        message.customed_kargs['Current_Vertex'] = message.parsed_output["Code Package"]
        message.customed_kargs.setdefault("Retrieval Codes", [])

        if action_json['code'] in message.customed_kargs["Retrieval Codes"]:
            message.action_status = ActionStatus.FINISHED
            return message

        message.customed_kargs["Retrieval Codes"].append(action_json['code'])

        return message

# log-level，print prompt和llm predict
os.environ["log_verbose"] = "0"

# 
llm_config = LLMConfig(
    model_name=model_name, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
)

embed_config = EmbedConfig(
    embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
)


# delete codebase
codebase_name = 'client_local'
code_path = '/Users/bingxu/Desktop/工作/大模型/chatbot/test_code_repo/client'
code_path = "D://chromeDownloads/devopschat-bot/client_v2/client"
use_nh = True
do_interpret = False
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.delete_codebase(codebase_name=codebase_name)

# initialize codebase
cbh = CodeBaseHandler(codebase_name, code_path, crawl_type='dir', use_nh=use_nh, local_graph_path=CB_ROOT_PATH,
                      llm_config=llm_config, embed_config=embed_config)
cbh.import_code(do_interpret=do_interpret)

# it need nebula for using cypher function, if you dont have nebula-api,it can't work

tool_role = Role(role_type="assistant", role_name="codeRetrievalJudger", prompt=codeRetrievalJudger_PROMPT)
codeRetrievalJudger = CodeRetrievalJudger(
    role=tool_role,
    task="",
    chat_turn=3,
    focus_agents=[],
    focus_message_keys=[],
    llm_config=llm_config, embed_config=embed_config,
)


code_role = Role(role_type="assistant", role_name="CodeRetrievalDivergent", prompt=codeRetrievalDivergent_PROMPT)
codeRetrievalDivergent = CodeRetrievalDivergent(
    role=code_role,
    task="",
    chat_turn=1,
    focus_agents=[],
    focus_message_keys=[],
    llm_config=llm_config, embed_config=embed_config,
)


chain_config = ChainConfig(
    chain_name="retrieval_chain", agents=[codeRetrievalJudger.role.role_name, codeRetrievalDivergent.role.role_name], 
    chat_turn=1)

chain = BaseChain(
    chainConfig=chain_config, agents=[codeRetrievalJudger, codeRetrievalDivergent], 
    llm_config=llm_config, embed_config=embed_config,
)

phase = BasePhase(
    phase_name="retrieval_phase", chains=[chain],
    embed_config=embed_config, llm_config=llm_config
)


# round-1
query_content = "UtilsTest 这个类中测试了哪些函数,测试的函数代码是什么"
query = Message(
    role_name="human", role_type="user", input_query=query_content,
    code_engine_name=codebase_name, score_threshold=1.0, top_k=3, cb_search_type="tag",
    local_graph_path=CB_ROOT_PATH, use_nh=use_nh
    )

# phase.pre_print(query)
output_message, output_memory = phase.step(query)
print(output_memory.to_str_messages(return_all=True, content_key="parsed_output_list"))