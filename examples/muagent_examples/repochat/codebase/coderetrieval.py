import os
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.codechat.codebase_handler.codebase_handler import CodeBaseHandler

from dotenv import load_dotenv

from utils.tools import check_java_project
class CodeRetrieval:
    def __init__(self,code_path,use_nh) -> None:
        load_dotenv()
        api_key = os.environ["OPENAI_API_KEY"]
        api_base_url= os.environ["API_BASE_URL"]
        model_name = os.environ["model_name"]
        embed_model = os.environ["embed_model"]
        model_engine = os.environ["model_engine"]
        self.llm_config = LLMConfig(
            model_name=model_name, model_engine=model_engine, api_key=api_key,  api_base_url=api_base_url, temperature=0.3
        )
        self.embed_config = EmbedConfig(
            embed_engine=model_engine, embed_model=embed_model,  api_key=api_key,  api_base_url=api_base_url)
        if use_nh:
            os.environ['nb_host'] = 'graphd'
            os.environ['nb_port'] = '9669'
            os.environ['nb_username'] = 'root'
            os.environ['nb_password'] = 'nebula'
            os.environ['nb_space'] = "client"
        # 开始检查codepath是否存在
        if not os.path.exists(code_path):
            raise Exception(f"code_path {code_path} not exists")
        # 开始检查code_path这个是否是java项目 TODO:后面加其它语言
        check_java_project(code_path)
        self.code_path = code_path
        self.lang = "java" 
        self.use_nh = use_nh
        self.CB_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repobase")
        
    def init_codebase(self, codebase_name: str):
        self.cbh = CodeBaseHandler(codebase_name, self.code_path, crawl_type='dir', use_nh=self.use_nh, local_graph_path=self.CB_ROOT_PATH,
                      llm_config=self.llm_config, embed_config=self.embed_config,language=self.lang)
        self.cbh.import_code(do_interpret=False)
    def search_code(self, query,search_type="cypher",limit=10):
        return self.cbh.search_code(query,search_type,limit=limit)