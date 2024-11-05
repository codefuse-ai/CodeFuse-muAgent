import os
import sys
import shutil
from loguru import logger

grandparent_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(grandparent_dir)

parent_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(parent_dir)
sys.path.append(grandparent_dir + 'examples/ekg_examples')
print(grandparent_dir + 'examples/')

print(grandparent_dir,parent_dir)

try:
    import test_config
    api_key = os.environ["OPENAI_API_KEY"]
    api_base_url= os.environ["API_BASE_URL"]
    model_name = os.environ["model_name"]
    model_engine = os.environ["model_engine"]
    embed_model = os.environ["embed_model"]
    embed_model_path = os.environ["embed_model_path"]
except Exception as e:
    # set your config
    logger.error(f"{e}")
    logger.error(f"please set your test_config")

    if not os.path.exists(os.path.join(parent_dir, "test_config.py")):
        shutil.copy(
            os.path.join(parent_dir, "test_config.py.example"), 
            os.path.join(parent_dir, "test_config.py")
        )
    import test_config
    # set your config
    api_key = ""
    api_base_url= ""
    model_name = ""
    model_engine = ""
    embed_model = ""
    embed_model_path = ""
    logger.error(f"{e}")


from muagent.service.ekg_inference import IntentionRouter
from muagent.schemas.db import GBConfig, TBConfig
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.schemas.ekg.ekg_graph import NodeTypesEnum
from muagent.schemas.common import GNode, GEdge
from langchain.llms.base import LLM

# 初始化 TbaseHandler 实例
tb_config = TBConfig(
    tb_type="TbaseHandler",
    index_name="opsgptkg_node",
    host=os.environ['tb_host'],
    port=os.environ['tb_port'],
    username=os.environ['tb_username'],
    password=os.environ['tb_password'],
    extra_kwargs={
        'host': os.environ['tb_host'],
        'port': os.environ['tb_port'],
        'username': os.environ['tb_username'] ,
        'password': os.environ['tb_password'],
        'definition_value': os.environ['tb_definition_value']
    }
)

# 初始化 NebulaHandler 实例
gb_config = GBConfig(
    gb_type="NebulaHandler",
    extra_kwargs={
        'host': os.environ['nb_host'],
        'port': os.environ['nb_port'],
        'username': os.environ['nb_username'] ,
        'password': os.environ['nb_password'],
        "space": os.environ['nb_space']
    }
)

# llm config
llm_config = LLMConfig(
    model_name=model_name,
    model_engine=model_engine,
    api_key=api_key,
    api_base_url=api_base_url,
    temperaTrue=0.3,
)

# embed config
embed_config = None

ekg_construct_service = EKGConstructService(
    embed_config=embed_config,
    llm_config=llm_config,
    tb_config=tb_config,
    gb_config=gb_config,
    initialize_space=False
)

intention_router = IntentionRouter(
    ekg_construct_service.model,
    ekg_construct_service.gb,
    ekg_construct_service.tb,
    embed_config
)

# query = '北京烤鸭好吃么？'
# ans = ekg_construct_service.model.predict(query).strip()
# print(ans)
# exit()


# 生成节点和意图树
def generate_intention_node(id: str, attrs: dict):
    assert 'description' in attrs
    return GNode(**{
        'id': id,
        'type': NodeTypesEnum.INTENT.value,
        'attributes': attrs
    })


def generate_edge(node1: GNode, node2: GNode):
    type_connect = "extend" if node1.type == "opsgptkg_intent" and node2.type == "opsgptkg_intent" else "route"
    return GEdge(**{
        "start_id": node1.id, 
        "end_id": node2.id, 
        "type": f"{node1.type}_{type_connect}_{node2.type}",
        "attributes": {
            "lat": "hello",
            "attr": "hello"
        }
    })

def generate_intention_flow(descs_dict: dict):
    def _generate_intention_flow(desc_dict, out_node: dict, out_edge: list, start_idx=0):
        for k, v in desc_dict.items():
            out_node[k] = generate_intention_node(
                id=f'intention_test_{start_idx}',
                attrs={'description': k, 'name': ''}
            )
            start_idx += 1
            if v is not None:
                start_idx = _generate_intention_flow(v, out_node, out_edge, start_idx)
                for k_1 in v:
                    out_edge.append(generate_edge(out_node[k], out_node[k_1]))
        return start_idx
    
    nodes, edges = dict(), []
    _generate_intention_flow(descs_dict, nodes, edges, 0)
    return nodes, edges




#%%
#测试单个节点的录入


one_node = GNode(**{
    "id": "6a9NGyq6Oyqoe57SrFU14JWsguo79I8v",
    "type": "opsgptkg_intent",
    "attributes": {
        "name": "答疑",
        "description": "答疑",
        "ID": 3545543925760,
        "teamids": "2700003, graph_id=2700003",
        "gdb_timestamp": 1725020465
    }
})
print(one_node)
print('type of one_node is ',type(one_node))
ekg_construct_service.gb.add_node(one_node)


logger.info('尝试查找')
start_nodeid = '6a9NGyq6Oyqoe57SrFU14JWsguo79I8v' 
start_nodetype    =' opsgptkg_intent'

one_node_ = ekg_construct_service.gb.get_current_node(attributes={"id": start_nodeid,}, 
                                  node_type=start_nodetype)
print(one_node_)


import math
import hashlib

def normalize(lis):
    s = sum([i * i for i in lis])
    if s == 0:
        raise ValueError('Sum of lis is 0')

    s_sqrt = math.sqrt(s)
    res = [i / s_sqrt for i in lis]
    return res
def md5_hash(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()
def hash_id(nodeId, sessionId='', otherstr = None):
    test_res = ''
    test_all = nodeId + sessionId 
    test_res = test_res + (md5_hash(test_all))
    if otherstr == None:
        return test_res
    else:
        test_res = test_res + otherstr
        return test_res


# %%
# query_list = [
#     "如何选择合适的医院和医生？",
#     "在线医疗咨询如何进行？",
#     "医保报销流程是什么？",
#     "如何预防常见疾病？",
#     "在家如何自我监测健康状况？",
#     "贷款利率是如何计算的？",
#     "个人信用评分对贷款申请有何影响？",
#     "如何提高贷款审批通过率？",
#     "贷款违约的后果是什么？",
#     "贷款提前还款需要注意什么？",
#     "狼人杀中\"预言家\"、\"女巫\"等角色的特殊能力是什么？",
#     "谁是卧底中如何有效推理和猜测？",
#     "狼人杀游戏的胜利条件是什么？",
#     "如何组织一场趣味性十足的线上游戏之夜？",
#     "蚂蚁森林的游戏规则和玩法是什么？",
#     "如何设计有效的团队建设活动？",
#     "团建活动中如何增强团队凝聚力？",
#     "如何评估团建活动的效果？",
#     "年终总结会议的策划要点有哪些？",
#     "公司文化塑造的关键因素是什么？",
#     "如何规划和执行公司年度庆典？",
#     "公司活动预算的合理分配策略是什么？",
#     "如何激励员工参与公司活动？",
#     "在线支付平台的安全防护措施有哪些？",
#     "如何处理在线预约后的取消或修改？",
#     "医疗保险报销的具体步骤是什么？",
#     "如何合理安排个人体检计划？"
# ]
start_nodeid = 'ekg_team_default'
query_list = ['如何使用花呗申请贷款']
# query = '在线医疗咨询如何进行？'
for i, query in enumerate(query_list):
    print(f'问题{i}')
    whether_execute = intention_router.get_intention_whether_execute(query)
    print(f'是否执行：{whether_execute}')
    consult_which = intention_router.get_intention_consult_which(query)
    print(f'咨询：{consult_which}')
    ret = intention_router.get_intention_by_node_info(
        query=query,
        root_node_id=start_nodeid,
        rule='nlp',
        start_from_root=False
    )
    intention_node = intention_router.gb_handler.get_current_node(
        {'id': ret['node_id']}, intention_router._node_type
    )
    print(f'意图识别\nquery: {query}\nresults: {ret}')
    print('GNode(id={}) 信息：{}'.format(ret['node_id'], intention_node))