import os
import sys
from loguru import logger

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if src_dir not in sys.path:
    sys.path.append(src_dir)

from muagent.service.ekg_inference import IntentionRouter
from muagent.schemas.db import GBConfig, TBConfig
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.schemas.ekg.ekg_graph import NodeTypesEnum
from muagent.schemas.common import GNode, GEdge
from langchain.llms.base import LLM


try:
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
    api_key = os.environ["OPENAI_API_KEY"]
    api_base_url= os.environ["API_BASE_URL"]
    model_name = os.environ["model_name"]
    model_engine = os.environ["model_engine"]
    embed_model = os.environ["embed_model"]
    embed_model_path = os.environ["embed_model_path"]
except Exception as e:
    # set your config
    api_key = ""
    api_base_url= ""
    model_name = ""
    model_engine = os.environ["model_engine"]
    model_engine = ""
    embed_model = ""
    embed_model_path = ""
    logger.error(f"{e}")


# 初始化 TbaseHandler 实例
tb_config = TBConfig(
    tb_type="TbaseHandler",
    index_name="muagent_test",
    host=os.environ['host'],
    port=os.environ['port'],
    username=os.environ['username'],
    password=os.environ['password'],
    extra_kwargs={
        'host': os.environ['host'],
        'port': os.environ['port'],
        'username': os.environ['username'] ,
        'password': os.environ['password'],
        'definition_value': os.environ['definition_value']
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
        "space": os.environ['nb_space'],
        'definition_value': os.environ['nb_definition_value']

    }
)

# llm config
llm_config = LLMConfig(
    model_name=model_name,
    model_engine=model_engine,
    api_key=api_key,
    api_base_url=api_base_url,
    temperature=0.3,
)

# embed config
embed_config = None

ekg_construct_service = EKGConstructService(
    embed_config=embed_config,
    llm_config=llm_config,
    tb_config=tb_config,
    gb_config=gb_config,
)

intention_router = IntentionRouter(
    ekg_construct_service.model,
    ekg_construct_service.gb,
    ekg_construct_service.tb,
    embed_config
)


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


descriptions_flow = {
    '节假日安排': {
        '当前时间在上午9:00~12:00之间': {'心情不错': None, '心情很一般': None, '心情很糟糕': None},
        '当前时间在下午14:00~18:00之间': {'很有活力': None, '无精打采': None},
        '当前时间在晚上8点~11点之间': {'今天是周六': None, '今天不是周六': None},
        '现在已经晚上23点过了': {'该睡觉了': None}
    }
}
query = '现在是周六晚上9点'
intention_nodes, intention_edges = generate_intention_flow(descriptions_flow)
print('Nodes...')
for v in intention_nodes.values():
    print(v)
print('Edges')
for edge in intention_edges:
    print(edge)

# 添加节点和边
ekg_construct_service.add_nodes(list(intention_nodes.values()), teamid='intention_test')
ekg_construct_service.add_edges(intention_edges, teamid='intention_test')

# nlp 路由
out = intention_router.get_intention_by_node_info_nlp(
    root_node_id=intention_nodes[next(iter(descriptions_flow))].id,
    query=query,
    start_from_root=True
)
print(out)


# 路由匹配
# rule = """import re
# def func(node: GNode, query: str):
#     nums = re.findall('[1-9]+', getattr(node, 'description', ''))
#     if not nums:
#         return -float('inf')
#     query_time = re.findall('[1-9]+', query)[0]
#     return int(query_time > nums[0])
# """
# out = intention_router.get_intention_by_node_info_match(
#     root_node_id=intention_nodes[next(iter(descriptions_flow))].id,
#     rule=rule,
#     query=query
# )
# print(out)
