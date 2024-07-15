from loguru import logger


from muagent.schemas.ekg import *
from muagent.schemas.db import *
from muagent.db_handler import *
from muagent.orm import table_init

from muagent.llm_models.llm_config import EmbedConfig, LLMConfig

from muagent.base_configs.env_config import KB_ROOT_PATH



class EKGConstructService:

    def __init__(
            self, 
            embed_config: EmbedConfig,
            llm_config: LLMConfig,
            db_config: DBConfig = None,
            vb_config: VBConfig = None,
            gb_config: GBConfig = None,
            tb_config: TBConfig = None,
            sls_config: SLSConfig = None,
            do_init: bool = False,
            kb_root_path: str = KB_ROOT_PATH,
        ):

        self.db_config = db_config
        self.vb_config = vb_config
        self.gb_config = gb_config
        self.tb_config = tb_config
        self.sls_config = sls_config
        self.do_init = do_init
        self.kb_root_path = kb_root_path
        self.embed_config: EmbedConfig = embed_config
        self.llm_config: LLMConfig = llm_config

    def init_handler(self, ):
        """Initializes Database VectorBase GraphDB TbaseDB"""
        self.init_vb()
        # self.init_db()
        # self.init_tb()
        # self.init_gb()

    def reinit_handler(self, do_init: bool=False):
        self.init_vb()
        # self.init_db()
        # self.init_tb()
        # self.init_gb()

    def init_tb(self, do_init: bool=None):
        tb_dict = {"TbaseHandler": TbaseHandler}
        tb_class =  tb_dict.get(self.tb_config.tb_type, TbaseHandler)
        tbase_args = {
            "host": self.tb_config.host,
            "port": self.tb_config.port,
            "username": self.tb_config.username,
            "password": self.tb_config.password,
        }
        self.vb = tb_class(tbase_args, self.tb_config.index_name)

    def init_gb(self, do_init: bool=None):
        pass
        gb_dict = {"NebulaHandler": NebulaHandler, "NetworkxHandler": NetworkxHandler}
        gb_class =  gb_dict.get(self.gb_config.gb_type, NetworkxHandler)
        self.gb = gb_class(self.db_config)

    def init_db(self, do_init: bool=None):
        pass
        db_dict = {"LocalFaissHandler": LocalFaissHandler}
        db_class =  db_dict.get(self.db_config.db_type)
        self.db = db_class(self.db_config)

    def init_vb(self, do_init: bool=None):
        table_init()
        vb_dict = {"LocalFaissHandler": LocalFaissHandler}
        vb_class =  vb_dict.get(self.vb_config.vb_type, LocalFaissHandler)
        self.vb: LocalFaissHandler = vb_class(self.embed_config, vb_config=self.vb_config)

    def init_sls(self, do_init: bool=None):
        sls_dict = {"AliYunSLSHandler": AliYunSLSHandler}
        sls_class =  sls_dict.get(self.sls_config.sls_type, AliYunSLSHandler)
        self.vb: AliYunSLSHandler = sls_class(self.embed_config, vb_config=self.vb_config)

    def create_ekg(self, ):
        ekg_router = {}

    def text2graph(self, ):
        # graph_id, alarms, steps

        # alarms, steps ==|llm|==> node_dict, edge_list, abnormal_dict

        # dsl ==|code2graph|==> node_dict, edge_list, abnormal_dict

        # dsl2graph => write2kg
        
        pass

    def dsl2graph(self, ):
        # dsl, write2kg, intent_node, graph_id

        # dsl ==|code2graph|==> node_dict, edge_list, abnormal_dict

        # dsl2graph => write2kg
        pass

    def yuque2graph(self, **kwargs):
        # yuque_url, write2kg, intent_node

        # get_graph(yuque_url)
        # graph_id from md(yuque_content)

        # yuque_dsl ==|code2graph|==> node_dict, edge_list, abnormal_dict

        # dsl2graph => write2kg
        pass

    def write2kg(self, graph_id: str, ekg_sls_data: EKGSlsData, ekg_tbase_data: EKGTbaseData):
        # dsl2graph => write2kg
        ## delete tbase/graph by graph_id
        ### diff the tabse within newest by graph_id
        ### diff the graph within newest by graph_id
        ## update tbase/graph by graph_id
        pass

    def get_intent(self, content: dict, ) -> EKGIntentResp:
        '''according content search intent'''
        pass

    def get_intents(self, contents: list[dict], ) -> EKGIntentResp:
        '''according contents search intents'''
        pass
    
    def get_node_edge_dict(self, cotents: list[dict], ) -> EKGSlsData:
        '''according contents generate ekg's raw datas'''
        # code2graph
        pass

    # def transform2sls(self, ekg_sls_data: EKGSlsData) -> list[EKGGraphSlsSchema]:
    #     pass

    def transform2tbase(self, ekg_sls_data: EKGSlsData) -> EKGTbaseData:
        pass

    def transform2dsl(self, ekg_sls_data: EKGSlsData):
        '''define your personal dsl format and code'''
        pass

