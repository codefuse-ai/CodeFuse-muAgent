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

print(grandparent_dir,parent_dir
      )

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
    temperaTrue=0.3,
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


new_nodes_1 = []
new_edges_1 = []


new_nodes_2 = \
[GNode(id='剧本杀/谁是卧底', type='opsgptkg_intent', attributes={'ID': -5201231166222141228, 'teamids': '', 'gdb_timestamp': '1725088421109', 'description': '谁是卧底', 'name': '谁是卧底', 'extra': ''}),
  GNode(id='剧本杀/狼人杀', type='opsgptkg_intent', attributes={'ID': 5476827419397129797, 'description': '狼人杀', 'name': '狼人杀', 'extra': '', 'teamids': '', 'gdb_timestamp': '1724815561170'}),
  GNode(id='剧本杀/谁是卧底/智能交互', type='opsgptkg_schedule', attributes={'ID': 603563742932974030, 'extra': '', 'teamids': '', 'gdb_timestamp': '1725088469126', 'description': '智能交互', 'name': '智能交互', 'enable': ''}),
  GNode(id='剧本杀/狼人杀/智能交互', type='opsgptkg_schedule', attributes={'ID': -5931163481230280444, 'extra': '', 'teamids': '', 'gdb_timestamp': '1724815624907', 'description': '智能交互', 'name': '智能交互', 'enable': ''}),
  GNode(id='剧本杀/谁是卧底/智能交互/分配座位', type='opsgptkg_task', attributes={'ID': 2011080219630105469, 'extra': '{"dodisplay":"True"}', 'teamids': '', 'gdb_timestamp': '1728912109030', 'executetype': '', 'description': '分配座位', 'name': '分配座位', 'accesscriteria': ''}),
  GNode(id='剧本杀/狼人杀/智能交互/位置选择', type='opsgptkg_task', attributes={'ID': 2541178858602010284, 'description': '位置选择', 'name': '位置选择', 'accesscriteria': '', 'extra': '{"memory_tag": "all"}', 'teamids': '', 'gdb_timestamp': '1724849735167', 'executetype': ''}),
  GNode(id='剧本杀/谁是卧底/智能交互/角色分配和单词分配', type='opsgptkg_task', attributes={'ID': -1817533533893637377, 'accesscriteria': '', 'extra': '{"memory_tag": "None","dodisplay":"True"}', 'teamids': '', 'gdb_timestamp': '1728912123682', 'executetype': '', 'description': '角色分配和单词分配', 'name': '角色分配和单词分配'}),
  GNode(id='剧本杀/狼人杀/智能交互/角色选择', type='opsgptkg_task', attributes={'ID': -8695604495489305484, 'description': '角色选择', 'name': '角色选择', 'accesscriteria': '', 'extra': '{"memory_tag": "None"}', 'teamids': '', 'gdb_timestamp': '1724849085296', 'executetype': ''}),
  GNode(id='剧本杀/谁是卧底/智能交互/通知身份', type='opsgptkg_task', attributes={'ID': 8901447933395410622, 'extra': '{"pattern": "react","dodisplay":"True"}', 'teamids': '', 'gdb_timestamp': '1728912141060', 'executetype': '', 'description': '##角色##\n你正在参与“谁是卧底”这个游戏，你的角色是[主持人]。你熟悉“谁是卧底”游戏的完整流程，你需要完成[任务]，保证游戏的顺利进行。\n目前已经完成 1)位置分配; 2)角色分配和单词分配。\n##任务##\n向所有玩家通知信息他们的 座位信息和单词信息。\n发送格式是： 【身份通知】你是{player_name}, 你的位置是{位置号}号， 你分配的单词是{单词}\n##详细步骤##\nstep1.依次向所有玩家通知信息他们的 座位信息和单词信息。发送格式是： 你是{player_name}, 你的位置是{位置号}号， 你分配的单词是{单词}\nstpe2.所有玩家信息都发送后，结束\n\n##注意##\n1. 每条信息只能发送给对应的玩家，其他人无法看到。\n2. 不要告诉玩家的角色信息，即不要高斯他是平民还是卧底角色\n3. 在将每个人的信息通知到后，本阶段任务结束\n##输出##\n请以列表的形式，给出参与者的所有行动。每个行动表示为JSON，格式为\n[{"action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}, ...]\n\n关键词含义如下：\n_ player_name (str): 行动方的 player_name，若行动方为主持人，为空，否则为玩家的 player_name；\n_ agent_name (str): 行动方的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。\n_ content (str): 行动方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。\n_ memory_tag (List[str]): 无论行动方是主持人还是玩家，memory_tag 固定为**所有**信息可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]\n\n#example#\n如果是玩家发言，则用 {"action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{ "memory_tag":["agent_name_a","agent_name_b"],"content": "str"}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description\n\n如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["agent_name_a","agent_name_b"], "content": "str",}]}\n\n##注意事项##\n1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。\n2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。\n3. 输出列表的最后一个元素一定是{"action": "taskend"}。\n4. 整个list是一个jsonstr，请输出jsonstr，不用输出markdown格式\n5. 结合已有的步骤，每次只输出下一个步骤，即一个 {"action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}', 'name': '通知身份', 'accesscriteria': ''}),
  GNode(id='剧本杀/狼人杀/智能交互/向玩家通知消息', type='opsgptkg_task', attributes={'ID': -4014299322597660132, 'extra': '{"pattern": "react"}', 'teamids': '', 'gdb_timestamp': '1725092109310', 'executetype': '', 'description': '##角色##\n你正在参与狼人杀这个游戏，你的角色是[主持人]。你熟悉狼人杀游戏的完整流程，你需要完成[任务]，保证狼人杀游戏的顺利进行。\n目前已经完成位置分配和角色分配。\n##任务##\n向所有玩家通知信息他们的座位信息和角色信息。\n发送格式是： 你是{player_name}, 你的位置是{位置号}号，你的身份是{角色名}\n##注意##\n1. 每条信息只能发送给对应的玩家，其他人无法看到。\n##输出##\n请以列表的形式，给出参与者的所有行动。每个行动表示为Python可解析的JSON，格式为\n\n[{"action": {player_name, agent_name}, "observation" or "Dungeon_Master": [{content, memory_tag}, ...]}]\n\n关键词含义如下：\n_ player_name (str): 行动方的 player_name，若行动方为主持人，为空，否则为玩家的 player_name；\n_ agent_name (str): 行动方的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。\n_ content (str): 行动方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。\n_ memory_tag (List[str]): 无论行动方是主持人还是玩家，memory_tag 固定为**所有**信息可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]\n\n##example##\n如果是玩家发言，则用 {"action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{"content": "str", "memory_tag":["agent_name_a","agent_name_b"]}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description\n\n如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{"content": "str", memory_tag:["agent_name_a","agent_name_b"]}]}\n\n##注意事项##\n1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。\n2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。\n3. 输出列表的最后一个元素一定是{"action": "taskend"}。\n4. 整个list是一个jsonstr，请直接输出jsonstr，不用输出markdown格式\n\n##结果##', 'name': '向玩家通知消息', 'accesscriteria': ''}),
  GNode(id='剧本杀/谁是卧底/智能交互/关键信息_1', type='opsgptkg_task', attributes={'ID': 3196717310525578616, 'gdb_timestamp': '1728913619628', 'executetype': '', 'description': '关键信息', 'name': '关键信息', 'accesscriteria': '', 'extra': '{"ignorememory":"True","dodisplay":"True"}', 'teamids': ''}),
  GNode(id='剧本杀/狼人杀/智能交互/狼人时刻', type='opsgptkg_task', attributes={'ID': 8926130661368382825, 'accesscriteria': 'OR', 'extra': '{"pattern": "react"}', 'teamids': '', 'gdb_timestamp': '1725092131051', 'executetype': '', 'description': '##背景##\n在狼人杀游戏中，主持人通知当前存活的狼人玩家指认一位击杀对象，所有狼人玩家给出击杀目标，主持人确定最终结果。\n\n##任务##\n整个流程分为6个步骤：\n1. 存活狼人通知：主持人向所有的狼人玩家广播，告知他们当前存活的狼人玩家有哪些。\n2. 第一轮讨论：主持人告知所有存活的狼人玩家投票，从当前存活的非狼人玩家中，挑选一个想要击杀的玩家。\n3. 第一轮投票：按照座位顺序，每一位存活的狼人为自己想要击杀的玩家投票。\n4. 第一轮结果反馈：主持人统计所有狼人的票数分布，确定他们是否达成一致。若达成一致，告知所有狼人最终被击杀的玩家的player_name，流程结束；否则，告知他们票数的分布情况，并让所有狼人重新投票指定击杀目标，主持人需要提醒他们，若该轮还不能达成一致，则取票数最大的目标为最终击杀对象。\n5. 第二轮投票：按照座位顺序，每一位存活的狼人为自己想要击杀的玩家投票。\n6. 第二轮结果反馈：主持人统计第二轮投票中所有狼人的票数分布，取票数最大的玩家为最终击杀对象，如果存在至少两个对象的票数最大且相同，取座位号最大的作为最终击杀对象。主持人告知所有狼人玩家最终被击杀的玩家的player_name。\n\n该任务的参与者只有狼人玩家和主持人，信息可见对象是所有狼人玩家。\n\n##输出##\n请以列表的形式，给出参与者的所有行动。每个行动表示为Python可解析的JSON，格式为\n\n[{"action": {player_name, agent_name}, "observation" or "Dungeon_Master": [{content, memory_tag}, ...]}]\n\n关键词含义如下：\n_ player_name (str): 行动方的 player_name，若行动方为主持人，为空，否则为玩家的 player_name；\n_ agent_name (str): 行动方的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。\n_ content (str): 行动方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。\n_ memory_tag (List[str]): 无论行动方是主持人还是玩家，memory_tag 固定为**所有**信息可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]\n\n##example##\n如果是玩家发言，则用 {"action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{"content": "str", "memory_tag":["agent_name_a","agent_name_b"]}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description\n\n如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{"content": "str", memory_tag:["agent_name_a","agent_name_b"]}]}\n\n##注意事项##\n1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。\n2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。\n3. 输出列表的最后一个元素一定是{"action": "taskend"}。\n4. 整个list是一个jsonstr，请直接输出jsonstr，不用输出markdown格式\n\n##结果##', 'name': '狼人时刻'}),
  GNode(id='剧本杀/谁是卧底/智能交互/开始新一轮的讨论', type='opsgptkg_task', attributes={'ID': -6077057339616293423, 'accesscriteria': 'OR', 'extra': '{"pattern": "react", "endcheck": "True",\n"memory_tag":"all",\n"dodisplay":"True"}', 'teamids': '', 'gdb_timestamp': '1728913634866', 'executetype': '', 'description': '###以上为本局游戏记录###\n\n\n##背景##\n你正在参与“谁是卧底”这个游戏，你的角色是[主持人]。你熟悉“谁是卧底”游戏的完整流程，你需要完成[任务]，保证游戏的顺利进行。\n\n##任务##\n以结构化的语句来模拟进行 谁是卧底的讨论环节。 在这一个环节里，所有主持人先宣布目前存活的玩家，然后每位玩家按照座位顺序发言\n\n\n##详细步骤##\nstep1. 主持人根据本局游戏历史记录，感知最开始所有的玩家 以及 在前面轮数中已经被票选死亡的玩家。注意死亡的玩家不能参与本轮游戏。得到当前存活的玩家个数以及其player_name。 并告知所有玩家当前存活的玩家个数以及其player_name。\nstep2. 主持人确定发言规则并告知所有玩家，发言规则步骤如下: 存活的玩家按照座位顺序由小到大进行发言\n（一个例子：假设总共有5个玩家，如果3号位置处玩家死亡，则发言顺序为：1_>2_>4_>5）\nstep3.  存活的的玩家按照顺序依次发言\nstpe4.  在每一位存活的玩家都发言后，结束\n\n                                      \n                                      \n##注意##\n1.之前的游戏轮数可能已经投票选中了某位/某些玩家，被票选中的玩家会立即死亡，不再视为存活玩家,死亡的玩家不能参与本轮游戏     \n2.你要让所有存活玩家都参与发言，不能遗漏任何存活玩家。在本轮所有玩家只发言一次\n3.该任务的参与者为主持人和所有存活的玩家，信息可见对象为所有玩家。\n4.不仅要模拟主持人的发言，还需要模拟玩家的发言\n5.每一位存活的玩家均发完言后，本阶段结束\n\n\n\n##输出##\n请以列表的形式，给出参与者的所有行动。每个行动表示为JSON，格式为\n[ {"thought": str, "action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}] }, ...]\n\n\n\n\n关键词含义如下：\n_ thought (str): 主持人执行行动的一些思考,包括分析玩家的存活状态，对历史对话信息的理解，对当前任务情况的判断等。 \n_ player_name (str): 行动方的 player_name，若行动方为主持人，为空 ;否则为玩家的 player_name；\n_ agent_name (str): 行动方的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。\n_ content (str): 行动方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。\n_ memory_tag (List[str]): 无论行动方是主持人还是玩家，memory_tag 固定为本条信息的可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]\n\n##example##\n如果是玩家发言，则用 {"thought": "str", "action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{ "memory_tag":["agent_name_a","agent_name_b"],"content": "str"}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description\n\n如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"thought": "str", "action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["agent_name_a","agent_name_b"], "content": "str",}]}\n\n##注意事项##\n1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。\n2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。\n3. 输出列表的最后一个元素一定是{"action": "taskend"}。\n4. 整个list是一个jsonstr，请输出jsonstr，不用输出markdown格式\n5. 结合已有的步骤，每次只输出下一个步骤，即一个 {"thought":  str, "action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}\n6. 如果是人类玩家发言， 一定要选择类似 agent_人类玩家 这样的agent_name', 'name': '开始新一轮的讨论'}),
  GNode(id='剧本杀/狼人杀/智能交互/天亮讨论', type='opsgptkg_task', attributes={'ID': 274796810216558717, 'gdb_timestamp': '1725106348469', 'executetype': '', 'description': '##角色##\n你正在参与狼人杀这个游戏，你的角色是[主持人]。你熟悉狼人杀游戏的完整流程，你需要完成[任务]，保证狼人杀游戏的顺利进行。\n##任务##\n你的任务如下: \n1. 告诉玩家昨晚发生的情况: 首先告诉玩家天亮了，然后你需要根据过往信息，告诉所有玩家，昨晚是否有玩家死亡。如果有，则向所有人宣布死亡玩家的名字，你只能宣布死亡玩家是谁如："昨晚xx玩家死了"，不要透露任何其他信息。如果没有，则宣布昨晚是平安夜。\n2. 确定发言规则并告诉所有玩家:\n确定发言规则步骤如下: \n第一步：确定第一个发言玩家，第一个发言的玩家为死者的座位号加1位置处的玩家(注意：最后一个位置+1的位置号为1号座位），如无人死亡，则从1号玩家开始。\n第二步：告诉所有玩家从第一个发言玩家开始发言，除了死亡玩家，每个人都需要按座位号依次讨论，只讨论一轮，所有人发言完毕后结束。注意不能遗忘指挥任何存活玩家发言！\n以下是一个例子：\n```\n总共有5个玩家，如果3号位置处玩家死亡，则第一个发言玩家为4号位置处玩家，因此从他开始发言，发言顺序为：4_>5_>1_>2\n```\n3. 依次指定存活玩家依次发言\n4. 被指定的玩家依次发言\n##注意##\n1. 你必须根据规则确定第一个发言玩家是谁，然后根据第一个发言玩家的座位号，确定所有人的发言顺序并将具体发言顺序并告知所有玩家，不要做任何多余解释\n2. 你要让所有存活玩家都参与发言，不能遗漏任何存活玩家\n##输出##\n请以列表的形式，给出参与者的所有行动。每个行动表示为Python可解析的JSON，格式为\n\n[{"action": {player_name, agent_name}, "observation" or "Dungeon_Master": [{content, memory_tag}, ...]}]\n\n关键词含义如下：\n_ player_name (str): 行动方的 player_name，若行动方为主持人，为空，否则为玩家的 player_name；\n_ agent_name (str): 行动方的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。\n_ content (str): 行动方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。\n_ memory_tag (List[str]): 无论行动方是主持人还是玩家，memory_tag 固定为**所有**信息可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]\n\n##example##\n如果是玩家发言，则用 {"action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{"content": "str", "memory_tag":["agent_name_a","agent_name_b"]}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description\n\n如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{"content": "str", memory_tag:["agent_name_a","agent_name_b"]}]}\n\n##注意事项##\n1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。\n2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。\n3. 输出列表的最后一个元素一定是{"action": "taskend"}。\n4. 整个list是一个jsonstr，请直接输出jsonstr，不用输出markdown格式\n\n##结果（请直接在后面输出，如果后面已经有部分结果，请续写。一定要保持续写后的内容结合前者能构成一个合法的 jsonstr）##', 'name': '天亮讨论', 'accesscriteria': '', 'extra': '{"pattern": "react"}', 'teamids': ''}),
  GNode(id='剧本杀/谁是卧底/智能交互/关键信息_2', type='opsgptkg_task', attributes={'ID': -8309123437761850283, 'description': '关键信息', 'name': '关键信息', 'accesscriteria': '', 'extra': '{"ignorememory":"True","dodisplay":"True"}', 'teamids': '', 'gdb_timestamp': '1728913648645', 'executetype': ''}),
  GNode(id='剧本杀/狼人杀/智能交互/票选凶手', type='opsgptkg_task', attributes={'ID': 1492108834523573937, 'accesscriteria': '', 'extra': '{"pattern": "react"}', 'teamids': '', 'gdb_timestamp': '1725106389716', 'executetype': '', 'description': '##角色##\n你正在参与“谁是卧底”这个游戏，你的角色是[主持人]。你熟悉“谁是卧底”游戏的完整流程，你需要完成[任务]，保证游戏的顺利进行。\n\n##任务##\n你的任务如下:\n1. 告诉玩家投票规则，规则步骤如下: \nstep1: 确定讨论阶段第一个发言的玩家A\nstep2: 从A玩家开始，按座位号依次投票，每个玩家只能对一个玩家进行投票，投票这个玩家表示认为该玩家是“卧底”。每个玩家只能投一次票。\nstep3: 将完整投票规则告诉所有玩家\n2. 指挥存活玩家依次投票。\n3. 被指定的玩家进行投票\n4. 主持人统计投票结果，并告知所有玩家，投出的角色是谁。\n\n该任务的参与者为主持人和所有存活的玩家，信息可见对象是所有玩家。\n\n##输出##\n请以列表的形式，给出参与者的所有行动。每个行动表示为Python可解析的JSON，格式为\n```\n{"action": {player_name, agent_name}, "observation" or "Dungeon_Master": [{content, memory_tag}, ...]}\n```\n关键词含义如下：\n_ player_name (str): 行动方的 player_name，若行动方为主持人，为空，否则为玩家的 player_name；\n_ agent_name (str): 行动方的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。\n_ content (str): 行动方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。\n_ memory_tag (List[str]): 无论行动方是主持人还是玩家，memory_tag 固定为**所有**信息可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]\n\n##example##\n如果是玩家发言，则用 {"action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{"content": "str", "memory_tag":["agent_name_a","agent_name_b"]}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description\n\n如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{"content": "str", memory_tag:["agent_name_a","agent_name_b"]}]}\n\n##注意事项##\n1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。\n2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。\n3. 输出列表的最后一个元素一定是{"action": "taskend"}。\n4. 整个list是一个jsonstr，请直接输出jsonstr，不用输出markdown格式\n\n##结果##\n', 'name': '票选凶手'}),
  GNode(id='剧本杀/谁是卧底/智能交互/票选卧底_1', type='opsgptkg_task', attributes={'ID': 267468674566989196, 'teamids': '', 'gdb_timestamp': '1728913670477', 'executetype': '', 'description': '##以上为本局游戏历史记录##\n##角色##\n你是一个统计票数大师，你正在参与“谁是卧底”这个游戏，你的角色是[主持人]。你熟悉“谁是卧底”游戏的完整流程，你需要完成[任务]，保证游戏的顺利进行。 现在是投票阶段。\n\n##任务##\n以结构化的语句来模拟进行 谁是卧底的投票环节， 也仅仅只模拟投票环节，投票环节结束后就本阶段就停止了，由后续的阶段继续进行游戏。 在这一个环节里，由主持人先告知大家投票规则，然后组织每位存活玩家按照座位顺序发言投票, 所有人投票后，本阶段结束。 \n##详细步骤##\n你的任务如下:\nstep1. 向所有玩家通知现在进入了票选环节，在这个环节，每个人都一定要投票指定某一个玩家为卧底\nstep2. 主持人确定投票顺序并告知所有玩家。 投票顺序基于如下规则: 1: 存活的玩家按照座位顺序由小到大进行投票（一个例子：假设总共有5个玩家，如果3号位置处玩家死亡，则投票顺序为：1_>2_>4_>5）2: 按座位号依次投票，每个玩家只能对一个玩家进行投票。每个玩家只能投一次票。3：票数最多的玩家会立即死亡\n\nstep3. 存活的的玩家按照顺序进行投票\nstep4. 所有存活玩家发言完毕,主持人宣布投票环节结束\n该任务的参与者为主持人和所有存活的玩家，信息可见对象是所有玩家。\n##注意##\n\n1.之前的游戏轮数可能已经投票选中了某位/某些玩家，被票选中的玩家会立即死亡，不再视为存活玩家      \n2.你要让所有存活玩家都参与投票，不能遗漏任何存活玩家。在本轮每一位玩家只投票一个人\n3.该任务的参与者为主持人和所有存活的玩家，信息可见对象为所有玩家。\n4.不仅要模拟主持人的发言，还需要模拟玩家的发言\n5.不允许玩家自己投自己，如果出现了这种情况，主持人会提醒玩家重新投票。\n\n\n\n##输出##\n请以列表的形式，给出参与者的所有行动。每个行动表示为JSON，格式为\n["thought": str, {"action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}, ...]\n关键词含义如下：\n_ thought (str): 主持人执行行动的一些思考,包括分析玩家的存活状态，对历史对话信息的理解，对当前任务情况的判断。 \n_ player_name (str): ***的 player_name，若行动方为主持人，为空，否则为玩家的 player_name；\n_ agent_name (str): ***的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。\n_ content (str): 行动方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。\n_ memory_tag (List[str]): 无论行动方是主持人还是玩家，memory_tag 固定为**所有**信息可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]\n##example##\n如果是玩家发言，则用 {"thought": "str", "action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{ "memory_tag":["agent_name_a","agent_name_b"],"content": "str"}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description\n如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"thought": "str", "action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["agent_name_a","agent_name_b"], "content": "str",}]}\n##注意事项##\n1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。\n2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。\n3. 输出列表的最后一个元素一定是{"action": "taskend"}。\n4. 整个list是一个jsonstr，请输出jsonstr，不用输出markdown格式\n5. 结合已有的步骤，每次只输出下一个步骤，即一个 {"thought":  str, "action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}\n6. 如果是人类玩家发言， 一定要选择类似 人类agent 这样的agent_name', 'name': '票选卧底', 'accesscriteria': '', 'extra': '{"pattern": "react", "endcheck": "True", "memory_tag":"all","dodisplay":"True"}'}),
  GNode(id='剧本杀/谁是卧底/智能交互/关键信息_4', type='opsgptkg_task', attributes={'ID': -4669093152651945828, 'extra': '{"ignorememory":"True","dodisplay":"True"}', 'teamids': '', 'gdb_timestamp': '1728913685959', 'executetype': '', 'description': '关键信息_4', 'name': '关键信息_4', 'accesscriteria': ''}),
  GNode(id='剧本杀/谁是卧底/智能交互/统计票数', type='opsgptkg_task', attributes={'ID': -6836070348442528830, 'teamids': '', 'gdb_timestamp': '1728913701092', 'executetype': '', 'description': '##以上为本局游戏历史记录##\n##角色##\n你是一个统计票数大师，你非常擅长计数以及统计信息。你正在参与“谁是卧底”这个游戏，你的角色是[主持人]。你熟悉“谁是卧底”游戏的完整流程，你需要完成[任务]，保证游戏的顺利进行。 现在是票数统计阶段\n\n##任务##\n以结构化的语句来模拟进行 谁是卧底的票数统计阶段， 也仅仅只票数统计阶段环节，票数统计阶段结束后就本阶段就停止了，由后续的阶段继续进行游戏。 在这一个环节里，由主持人根据上一轮存活的玩家投票结果统计票数。 \n##详细步骤##\n你的任务如下:\nstep1. 主持人感知上一轮投票环节每位玩家的发言, 统计投票结果，格式为[{"player_name":票数}]. \nstep2  然后，主持人宣布死亡的玩家，以最大票数为本轮被投票的目标，如果票数相同，则取座位号高的角色死亡。并告知所有玩家本轮被投票玩家的player_name。（格式为【重要通知】本轮死亡的玩家为XXX）同时向所有玩家宣布，被投票中的角色会视为立即死亡（即不再视为存活角色）\nstep3. 在宣布死亡玩家后，本阶段流程结束，由后续阶段继续推进游戏\n该任务的参与者为主持人和所有存活的玩家，信息可见对象是所有玩家。\n##注意##\n1.如果有2个或者两个以上的被玩家被投的票数相同，则取座位号高的玩家死亡。并告知大家原因：票数相同，取座位号高的玩家死亡\n2.在统计票数时，首先确认存活玩家的数量，再先仔细回忆，谁被投了。 最后统计每位玩家被投的次数。 由于每位玩家只有一票，所以被投次数的总和等于存活玩家的数量 \n3.通知完死亡玩家是谁后，本阶段才结束，由后续阶段继续推进游戏。输出 {"action": "taskend"}即可\n4.主持人只有当通知本轮死亡的玩家时，才使用【重要通知】的前缀，其他情况下不要使用【重要通知】前缀\n5.只统计上一轮投票环节的情况\n##example##\n{"thought": "在上一轮中, 存活玩家有 小北,李光,赵鹤,张良 四个人。 其中 小北投了李光, 赵鹤投了小北, 张良投了李光, 李光投了张良。总结被投票数为： 李光:2票; 小北:1票,张良:1票. Check一下，一共有四个人投票了，被投的票是2（李光）+1（小北）+1（张良）=4，总结被投票数没有问题。 因此李光的票最多", "action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["all"], "content": "李光:2票; 小北:1票,张良:1票 .因此李光的票最多.【重要通知】本轮死亡玩家是李光",}]}\n\n##example##\n{"thought": "在上一轮中, 存活玩家有 小北,人类玩家,赵鹤,张良 四个人。 其中 小北投了人类玩家, 赵鹤投了小北, 张良投了小北, 人类玩家投了张良。总结被投票数为：小北:2票,人类玩家:1票,张良:0票 .Check一下，一共有四个人投票了，被投的票是2（小北）+1（人类玩家）+张良（0）=3，总结被投票数有问题。 更正总结被投票数为：小北:2票,人类玩家:1票,张良:1票。因此小北的票最多", "action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["all"], "content": "小北:2票,人类玩家:1票,张良:1票 .因此小北的票最多.【重要通知】本轮死亡玩家是小北",}]}\n\n\n##输出##\n请以列表的形式，给出参与者的所有行动。每个行动表示为JSON，格式为\n["thought": str, {"action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}, ...]\n关键词含义如下：\n_ thought (str): 主持人执行行动的一些思考,包括分析玩家的存活状态，对历史对话信息的理解，对当前任务情况的判断。 \n_ player_name (str): ***的 player_name，若行动方为主持人，为空，否则为玩家的 player_name；\n_ agent_name (str): ***的 agent_name，若为主持人，则 agent_name 为 "主持人"，否则为玩家的 agent_name。\n_ content (str): 行动方的具体行为，若为主持人，content 为告知信息；否则，content 为玩家的具体行动。\n_ memory_tag (List[str]): 无论行动方是主持人还是玩家，memory_tag 固定为**所有**信息可见对象的agent_name, 如果信息可见对象为所有玩家，固定为 ["all"]\n##example##\n如果是玩家发言，则用 {"thought": "str", "action": {"agent_name": "agent_name_c", "player_name":"player_name_d"}, "observation": [{ "memory_tag":["agent_name_a","agent_name_b"],"content": "str"}]} 格式表示。content是玩家发出的信息；memory_tag是这条信息可见的对象，需要填写agent名。不要填写 agent_description\n如果agent_name是主持人，则无需输入player_name， 且observation变为 Dungeon_Master。即{"thought": "str", "action": {"agent_name": "主持人", "player_name":""}, "Dungeon_Master": [{ "memory_tag":["agent_name_a","agent_name_b"], "content": "str",}]}\n##注意事项##\n1. 所有玩家的座位、身份、agent_name、存活状态等信息在开头部分已给出。\n2. "observation" or "Dungeon_Master"如何选择？若 agent_name 为"主持人"，则为"Dungeon_Master"，否则为 "observation"。\n3. 输出列表的最后一个元素一定是{"action": "taskend"}。\n4. 整个list是一个jsonstr，请输出jsonstr，不用输出markdown格式\n5. 结合已有的步骤，每次只输出下一个步骤，即一个 {"thought":  str, "action": {"player_name":str, "agent_name":str}, "observation" or "Dungeon_Master": [{"memory_tag":str,"content":str}]}\n6. 如果是人类玩家发言， 一定要选择类似 人类agent 这样的agent_name', 'name': '统计票数', 'accesscriteria': '', 'extra': '{"pattern": "react", "endcheck": "True", "memory_tag":"all","model_name":"gpt_4","dodisplay":"True"}'}),
  GNode(id='剧本杀/谁是卧底/智能交互/关键信息_3', type='opsgptkg_task', attributes={'ID': -4800215480474522940, 'accesscriteria': '', 'extra': '{"ignorememory":"True","dodisplay":"True"}', 'teamids': '', 'gdb_timestamp': '1728913715255', 'executetype': '', 'description': '关键信息', 'name': '关键信息'}),
  GNode(id='剧本杀/谁是卧底/智能交互/判断游戏是否结束', type='opsgptkg_task', attributes={'ID': -5959590132883379159, 'description': '判断游戏是否结束', 'name': '判断游戏是否结束', 'accesscriteria': '', 'extra': '{"memory_tag": "None","dodisplay":"True"}', 'teamids': '', 'gdb_timestamp': '1728913728308', 'executetype': ''}),
  GNode(id='剧本杀/谁是卧底/智能交互/事实_1', type='opsgptkg_phenomenon', attributes={'ID': -525629912140732688, 'description': '是', 'name': '是', 'extra': '', 'teamids': '', 'gdb_timestamp': '1725089138724'}),
  GNode(id='剧本杀/谁是卧底/智能交互/事实_2', type='opsgptkg_phenomenon', attributes={'ID': 4216433814773851843, 'teamids': '', 'gdb_timestamp': '1725089593085', 'description': '否', 'name': '否', 'extra': ''}),
  GNode(id='剧本杀/谁是卧底/智能交互/给出每个人的单词以及最终胜利者', type='opsgptkg_task', attributes={'ID': 8878899410716129093, 'extra': '{"dodisplay":"True"}', 'teamids': '', 'gdb_timestamp': '1728913745186', 'executetype': '', 'description': '给出每个人的单词以及最终胜利者', 'name': '给出每个人的单词以及最终胜利者', 'accesscriteria': ''}),
  GNode(id='剧本杀/狼人杀/智能交互/判断游戏是否结束', type='opsgptkg_task', attributes={'ID': -2316854558435035646, 'description': '判断游戏是否结束 ', 'name': '判断游戏是否结束 ', 'accesscriteria': '', 'extra': '{"memory_tag": "None"}', 'teamids': '', 'gdb_timestamp': '1725092210244', 'executetype': ''}),
  GNode(id='剧本杀/狼人杀/智能交互/事实_2', type='opsgptkg_phenomenon', attributes={'ID': -6298561983042120406, 'extra': '', 'teamids': '', 'gdb_timestamp': '1724816562165', 'description': '否', 'name': '否'}),
  GNode(id='剧本杀/狼人杀/智能交互/事实_1', type='opsgptkg_phenomenon', attributes={'ID': 6987562967613654408, 'gdb_timestamp': '1724816495297', 'description': '是', 'name': '是', 'extra': '', 'teamids': ''}),
  GNode(id='剧本杀/l狼人杀/智能交互/宣布游戏胜利者', type='opsgptkg_task', attributes={'ID': -758955621725402723, 'extra': '', 'teamids': '', 'gdb_timestamp': '1725097362872', 'executetype': '', 'description': '判断游戏是否结束', 'name': '判断游戏是否结束', 'accesscriteria': ''}),
  GNode(id='剧本杀', type='opsgptkg_intent', attributes={'ID': -3388526698926684245, 'description': '剧本杀', 'name': '剧本杀', 'extra': '', 'teamids': '', 'gdb_timestamp': '1724815537102'})]



new_edges_2 = \
[GEdge(start_id='剧本杀', end_id='剧本杀/谁是卧底', type='opsgptkg_intent_route_opsgptkg_intent', attributes={'SRCID': -3388526698926684245, 'DSTID': -5201231166222141228, 'gdb_timestamp': '1725088433347', 'extra': ''}),
  GEdge(start_id='剧本杀', end_id='剧本杀/狼人杀', type='opsgptkg_intent_route_opsgptkg_intent', attributes={'SRCID': -3388526698926684245, 'DSTID': 5476827419397129797, 'gdb_timestamp': '1724815572710', 'extra': ''}),
  GEdge(start_id='剧本杀/谁是卧底', end_id='剧本杀/谁是卧底/智能交互', type='opsgptkg_intent_route_opsgptkg_schedule', attributes={'SRCID': -5201231166222141228, 'DSTID': 603563742932974030, 'gdb_timestamp': '1725088478251', 'extra': ''}),
  GEdge(start_id='剧本杀/狼人杀', end_id='剧本杀/狼人杀/智能交互', type='opsgptkg_intent_route_opsgptkg_schedule', attributes={'SRCID': 5476827419397129797, 'DSTID': -5931163481230280444, 'gdb_timestamp': '1724815633494', 'extra': ''}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互', end_id='剧本杀/谁是卧底/智能交互/分配座位', type='opsgptkg_schedule_route_opsgptkg_task', attributes={'SRCID': 603563742932974030, 'DSTID': 2011080219630105469, 'gdb_timestamp': '1725088659469', 'extra': ''}),
  GEdge(start_id='剧本杀/狼人杀/智能交互', end_id='剧本杀/狼人杀/智能交互/位置选择', type='opsgptkg_schedule_route_opsgptkg_task', attributes={'SRCID': -5931163481230280444, 'DSTID': 2541178858602010284, 'gdb_timestamp': '1724815720186', 'extra': ''}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/分配座位', end_id='剧本杀/谁是卧底/智能交互/角色分配和单词分配', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': 2011080219630105469, 'DSTID': -1817533533893637377, 'gdb_timestamp': '1725088761379', 'extra': ''}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/位置选择', end_id='剧本杀/狼人杀/智能交互/角色选择', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': 2541178858602010284, 'DSTID': -8695604495489305484, 'extra': '', 'gdb_timestamp': '1724815828424'}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/角色分配和单词分配', end_id='剧本杀/谁是卧底/智能交互/通知身份', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': -1817533533893637377, 'DSTID': 8901447933395410622, 'gdb_timestamp': '1725088813780', 'extra': ''}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/角色选择', end_id='剧本杀/狼人杀/智能交互/向玩家通知消息', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': -8695604495489305484, 'DSTID': -4014299322597660132, 'gdb_timestamp': '1724815943792', 'extra': ''}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/通知身份', end_id='剧本杀/谁是卧底/智能交互/关键信息_1', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': 8901447933395410622, 'DSTID': 3196717310525578616, 'extra': '', 'gdb_timestamp': '1725364881808'}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/向玩家通知消息', end_id='剧本杀/狼人杀/智能交互/狼人时刻', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': -4014299322597660132, 'DSTID': 8926130661368382825, 'gdb_timestamp': '1724815952503', 'extra': ''}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/关键信息_1', end_id='剧本杀/谁是卧底/智能交互/开始新一轮的讨论', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': 3196717310525578616, 'DSTID': -6077057339616293423, 'extra': '', 'gdb_timestamp': '1725364891197'}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/狼人时刻', end_id='剧本杀/狼人杀/智能交互/天亮讨论', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': 8926130661368382825, 'DSTID': 274796810216558717, 'gdb_timestamp': '1724911515908', 'extra': ''}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/开始新一轮的讨论', end_id='剧本杀/谁是卧底/智能交互/关键信息_2', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': -6077057339616293423, 'DSTID': -8309123437761850283, 'extra': '', 'gdb_timestamp': '1725364966817'}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/天亮讨论', end_id='剧本杀/狼人杀/智能交互/票选凶手', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': 274796810216558717, 'DSTID': 1492108834523573937, 'extra': '', 'gdb_timestamp': '1724816423574'}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/关键信息_2', end_id='剧本杀/谁是卧底/智能交互/票选卧底_1', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': -8309123437761850283, 'DSTID': 267468674566989196, 'gdb_timestamp': '1725507894066', 'extra': ''}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/票选卧底_1', end_id='剧本杀/谁是卧底/智能交互/关键信息_4', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': 267468674566989196, 'DSTID': -4669093152651945828, 'gdb_timestamp': '1725507901109', 'extra': ''}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/关键信息_4', end_id='剧本杀/谁是卧底/智能交互/统计票数', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': -4669093152651945828, 'DSTID': -6836070348442528830, 'extra': '', 'gdb_timestamp': '1725507907343'}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/统计票数', end_id='剧本杀/谁是卧底/智能交互/关键信息_3', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': -6836070348442528830, 'DSTID': -4800215480474522940, 'extra': '', 'gdb_timestamp': '1725507917664'}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/关键信息_3', end_id='剧本杀/谁是卧底/智能交互/判断游戏是否结束', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': -4800215480474522940, 'DSTID': -5959590132883379159, 'extra': '', 'gdb_timestamp': '1725365051574'}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/判断游戏是否结束', end_id='剧本杀/谁是卧底/智能交互/事实_1', type='opsgptkg_task_route_opsgptkg_phenomenon', attributes={'SRCID': -5959590132883379159, 'DSTID': -525629912140732688, 'extra': '', 'gdb_timestamp': '1725089153218'}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/判断游戏是否结束', end_id='剧本杀/谁是卧底/智能交互/事实_2', type='opsgptkg_task_route_opsgptkg_phenomenon', attributes={'SRCID': -5959590132883379159, 'DSTID': 4216433814773851843, 'extra': '', 'gdb_timestamp': '1725089603500'}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/事实_1', end_id='剧本杀/谁是卧底/智能交互/给出每个人的单词以及最终胜利者', type='opsgptkg_phenomenon_route_opsgptkg_task', attributes={'SRCID': -525629912140732688, 'DSTID': 8878899410716129093, 'gdb_timestamp': '1725089654391', 'extra': ''}),
  GEdge(start_id='剧本杀/谁是卧底/智能交互/事实_2', end_id='剧本杀/谁是卧底/智能交互/开始新一轮的讨论', type='opsgptkg_phenomenon_route_opsgptkg_task', attributes={'SRCID': 4216433814773851843, 'DSTID': -6077057339616293423, 'extra': '', 'gdb_timestamp': '1725089612866'}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/票选凶手', end_id='剧本杀/狼人杀/智能交互/判断游戏是否结束', type='opsgptkg_task_route_opsgptkg_task', attributes={'SRCID': 1492108834523573937, 'DSTID': -2316854558435035646, 'extra': '', 'gdb_timestamp': '1724816464917'}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/判断游戏是否结束', end_id='剧本杀/狼人杀/智能交互/事实_2', type='opsgptkg_task_route_opsgptkg_phenomenon', attributes={'SRCID': -2316854558435035646, 'DSTID': -6298561983042120406, 'gdb_timestamp': '1724816570641', 'extra': ''}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/判断游戏是否结束', end_id='剧本杀/狼人杀/智能交互/事实_1', type='opsgptkg_task_route_opsgptkg_phenomenon', attributes={'SRCID': -2316854558435035646, 'DSTID': 6987562967613654408, 'gdb_timestamp': '1724816506031', 'extra': ''}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/事实_2', end_id='剧本杀/狼人杀/智能交互/狼人时刻', type='opsgptkg_phenomenon_route_opsgptkg_task', attributes={'SRCID': -6298561983042120406, 'DSTID': 8926130661368382825, 'extra': '', 'gdb_timestamp': '1724816585403'}),
  GEdge(start_id='剧本杀/狼人杀/智能交互/事实_1', end_id='剧本杀/l狼人杀/智能交互/宣布游戏胜利者', type='opsgptkg_phenomenon_route_opsgptkg_task', attributes={'SRCID': 6987562967613654408, 'DSTID': -758955621725402723, 'gdb_timestamp': '1724911404270', 'extra': ''})]

new_nodes = new_nodes_1 + new_nodes_2
new_edges = new_edges_1 + new_edges_2

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
    
    




logger.info('尝试查插入节点')




for one_node  in new_nodes:   
    one_node.attributes['description']  = one_node.attributes['description']
    
    one_node.attributes['gdb_timestamp'] = int(one_node.attributes['gdb_timestamp'] )
    one_node.id = hash_id(one_node.id )
    
    if one_node.type == 'opsgptkg_analysis':
        
        one_node.attributes['summaryswitch'] = False
        
    if one_node.type == 'opsgptkg_schedule':
        one_node.attributes['enable'] = True
    
    print(one_node)
    ekg_construct_service.gb.add_node(one_node)
    




logger.info('尝试查插入边')
for one_edge  in new_edges:
    one_edge.attributes['gdb_timestamp'] = int(one_edge.attributes['gdb_timestamp'] )
    one_edge.start_id = hash_id(one_edge.start_id )
    one_edge.end_id = hash_id(one_edge.end_id )
    one_edge.attributes['type'] = 'opsgptkg_intent_extend_opsgptkg_intent' 
    print(one_edge)
    
    if one_edge.type == 'opsgptkg_phenomenon_conclude_opsgptkg_analysis':
        one_edge.type = 'opsgptkg_phenomenon_route_opsgptkg_analysis'
    ekg_construct_service.gb.add_edge(one_edge)
    






logger.info('尝试查找一阶近邻')
#start_nodeid = hash_id('剧本杀' )
#start_nodeid = hash_id('剧本杀' )
start_nodetype    =' opsgptkg_intent'

neighbor_nodes = ekg_construct_service.gb.get_neighbor_nodes(attributes={"id": start_nodeid,}, 
                                  node_type=start_nodetype)

current_nodes = ekg_construct_service.gb.get_current_nodes(attributes={"id": start_nodeid,}, 
                                  node_type=start_nodetype)

print(neighbor_nodes)
print(current_nodes)