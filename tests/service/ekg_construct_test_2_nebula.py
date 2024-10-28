import time
import sys, os
from loguru import logger
import copy

import pdb

# 在需要设置断点的地方
# pdb.set_trace()


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

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)

import os, sys
from loguru import logger

sys.path.append("/ossfs/workspace/muagent")
from muagent.schemas.common import GNode, GEdge
from muagent.schemas.db import GBConfig, TBConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig



# 初始化 GeaBaseHandler 实例
# gb_config = GBConfig(
#     gb_type="GeaBaseHandler", 
#     extra_kwargs={
#         'metaserver_address': os.environ['metaserver_address'],
#         'project': os.environ['project'],
#         'city': os.environ['city'],
#         'lib_path': os.environ['lib_path'],
#     }
# )


# 初始化 TbaseHandler 实例
tb_config = TBConfig(
    tb_type="TbaseHandler",
    index_name="muagent_test",
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
    model_name=model_name, model_engine=model_engine, api_key=api_key, api_base_url=api_base_url, temperature=0.3,
)


# emebdding config
# embed_config = EmbedConfig(
#     embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
# )

# embed_config = EmbedConfig(
#     embed_model="default",
#     langchain_embeddings=embeddings
# )
embed_config = None

ekg_construct_service = EKGConstructService(
    embed_config=embed_config,
    llm_config=llm_config,
    tb_config=tb_config,
    gb_config=gb_config,
    initialize_space=False
)



# test return dic
# node1 = [GNode(
#                 id = "ekg_team_3400004",
#                 type = "opsgptkg_intent",
#                 attributes = {
#                     "name": "开始",
#                     "description": "团队起始节点",
#                     "ID": 5945714343936,
#                     "teamids": "3400004",
#                     "gdb_timestamp": 1725537224
#                 }
#             )
# ]

# result = ekg_construct_service.add_nodes(node1,"yunjiu_test")
# print(result)




def generate_node(id, type):
    extra_attr = {"tmp": "hello"}
    if type == "opsgptkg_schedule":
        extra_attr["enable"] = False
        
    if type == "opsgptkg_task":
        extra_attr["accesscriteria"] = "hello"
        extra_attr["executetype"] = "hello"
        
    if type == "opsgptkg_analysis":
        extra_attr["accesscriteria"] = "hello"
        extra_attr["summaryswtich"] = False
        extra_attr['dsltemplate'] = "hello"             
        
    return GNode(**{
        "id": id, 
        "type": type,
        "attributes": {**{
            "path": id,
            "name": id,
            "description": id, 
        }, **extra_attr}
    })


def generate_edge(node1, node2):
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


# nodetypes = [
#     'opsgptkg_intent', 'opsgptkg_schedule', 'opsgptkg_task',
#     'opsgptkg_phenomenon', 'opsgptkg_analysis'
# ]

# nodes_dict = {}
# for nodetype in nodetypes:
#     for i in range(8):
#         # print(f"shanshi_{nodetype}_{i}")
#         nodes_dict[f"shanshi_{nodetype}_{i}"] = generate_node(f"shanshi_{nodetype}_{i}", nodetype)

# edge_ids = [
#     ["shanshi_opsgptkg_intent_0", "shanshi_opsgptkg_intent_1"],
#     ["shanshi_opsgptkg_intent_1", "shanshi_opsgptkg_intent_2"],
#     ["shanshi_opsgptkg_intent_2", "shanshi_opsgptkg_schedule_0"],
#     ["shanshi_opsgptkg_intent_2", "shanshi_opsgptkg_schedule_1"],
#     ["shanshi_opsgptkg_schedule_1", "shanshi_opsgptkg_analysis_3"],
#     ["shanshi_opsgptkg_schedule_0", "shanshi_opsgptkg_task_0"],
#     ["shanshi_opsgptkg_task_0", "shanshi_opsgptkg_task_1"],
#     ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_analysis_0"],
#     ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_phenomenon_0"],
#     ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_phenomenon_1"],
#     ["shanshi_opsgptkg_phenomenon_0", "shanshi_opsgptkg_task_2"],
#     ["shanshi_opsgptkg_phenomenon_1", "shanshi_opsgptkg_task_3"],
#     ["shanshi_opsgptkg_task_2", "shanshi_opsgptkg_analysis_1"],
#     ["shanshi_opsgptkg_task_3", "shanshi_opsgptkg_analysis_2"],
# ]

# nodeid_set = set()
# origin_edges = []
# origin_nodes = []
# for src_id, dst_id in edge_ids:
#     origin_edges.append(generate_edge(nodes_dict[src_id], nodes_dict[dst_id]))
#     if src_id not in nodeid_set:
#         nodeid_set.add(src_id)
#         origin_nodes.append(nodes_dict[src_id])
#     if dst_id not in nodeid_set:
#         nodeid_set.add(dst_id)
#         origin_nodes.append(nodes_dict[dst_id])




# new_edge_ids = [
#     ["shanshi_opsgptkg_intent_0", "shanshi_opsgptkg_intent_1"],
#     ["shanshi_opsgptkg_intent_1", "shanshi_opsgptkg_intent_2"],
#     ["shanshi_opsgptkg_intent_2", "shanshi_opsgptkg_schedule_0"],
#     # 新增
#     ["shanshi_opsgptkg_intent_2", "shanshi_opsgptkg_schedule_2"],
#     ["shanshi_opsgptkg_schedule_2", "shanshi_opsgptkg_analysis_4"],
#     # 
#     ["shanshi_opsgptkg_schedule_0", "shanshi_opsgptkg_task_0"],
#     ["shanshi_opsgptkg_task_0", "shanshi_opsgptkg_task_1"],
#     ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_analysis_0"],
#     ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_phenomenon_0"],
#     ["shanshi_opsgptkg_task_1", "shanshi_opsgptkg_phenomenon_1"],
#     ["shanshi_opsgptkg_phenomenon_0", "shanshi_opsgptkg_task_2"],
#     ["shanshi_opsgptkg_phenomenon_1", "shanshi_opsgptkg_task_3"],
#     ["shanshi_opsgptkg_task_2", "shanshi_opsgptkg_analysis_1"],
#     ["shanshi_opsgptkg_task_3", "shanshi_opsgptkg_analysis_2"],
# ]

# nodeid_set = set()
# edges = []
# nodes = []
# for src_id, dst_id in new_edge_ids:
#     edges.append(generate_edge(nodes_dict[src_id], nodes_dict[dst_id]))
#     if src_id not in nodeid_set:
#         nodeid_set.add(src_id)
#         nodes.append(nodes_dict[src_id])
#     if dst_id not in nodeid_set:
#         nodeid_set.add(dst_id)
#         nodes.append(nodes_dict[dst_id])

# for node in nodes:
#     if node.type == "opsgptkg_task":
#         node.attributes["name"] += "_update"
#         node.attributes["tmp"] += "_update"
#         node.attributes["description"] += "_update"

# for edge in edges:
#     if edge.type == "opsgptkg_task_route_opsgptkg_task":
#         edge.attributes["lat"] += "_update"
        

# 
teamid = "shanshi_test"

# logger.info(origin_nodes[0])

# origin_nodes = [GNode(**n) for n in origin_nodes]
# origin_edges = [GEdge(**e) for e in origin_edges]

# logger.info(origin_edges[0])

# ekg_construct_service.add_nodes(origin_nodes, teamid)
# ekg_construct_service.add_edges(origin_edges, teamid)

#print(len(origin_edges))

#print(origin_edges)

# done
teamid = "shanshi_test_2"
rootid="shanshi_opsgptkg_intent_0"
# ekg_construct_service.update_graph(origin_nodes, origin_edges, nodes, edges, teamid, rootid)
# ekg_construct_service.update_graph(origin_nodes, origin_edges, nodes, edges, teamid)



# do search
# node = ekg_construct_service.get_node_by_id(nodeid="shanshi_opsgptkg_task_3", node_type="opsgptkg_task")
# print(node)
# graph = ekg_construct_service.get_graph_by_nodeid(nodeid="shanshi_opsgptkg_intent_0", node_type="opsgptkg_intent")
# print(len(graph.nodes), len(graph.edges), len(graph.paths))
# logger.info(graph.paths[1])


# # search nodes by text
text = 'shanshi_test'
teamid = "shanshi_test"
# nodes = ekg_construct_service.search_nodes_by_text(text, teamid=teamid)
# print(len(nodes))

# # search path by node and rootid
# graph = ekg_construct_service.search_rootpath_by_nodeid(nodeid="shanshi_opsgptkg_analysis_2", node_type="opsgptkg_analysis", rootid="shanshi_opsgptkg_intent_0")
# graph = ekg_construct_service.search_rootpath_by_nodeid(nodeid="shanshi_opsgptkg_analysis_2", node_type="opsgptkg_analysis", rootid="shanshi_opsgptkg_analysis_2")

# print(len(graph.nodes), len(graph.edges))
# print(len(graph.paths))
# print(graph.paths)
# print(graph)


# create_ekg
# params = {
#         "text": '测试文本',
#         "teamid": "shanshi_test_2",
#         "intentNodeids": ["shanshi_opsgptkg_intent_1"],
#         "rootid": "shanshi_opsgptkg_intent_0",
#         "intent_text": None,
#         "all_intent_list": [],
#         "do_save": False
# }
# result = ekg_construct_service.create_ekg(
#                 text=params["text"], teamid=params["teamid"],rootid=params["rootid"],
#                 service_name="text2graph"
#             )
# print(result)




# intent_subgraph_new_edges = intent_subgraph['newGraph']['edges']

# logger.info('尝试查插入边')
# for one_edge  in intent_subgraph_new_edges:
#     one_edge['type'] = 'opsgptkg_intent_extend_opsgptkg_intent'     #先假设都是这种类型的边
#     one_edge['start_id'] = one_edge['startId']
#     one_edge['end_id'] = one_edge['endId']
#     one_edge = GEdge(**one_edge)    
#     ekg_construct_service.gb.add_edge(one_edge)


#### 测试添加节点 #####
teamid = "yunjiu_test"

node1 = GNode(**{
    "id": f"ekg_team_{teamid}", 
    "type": "opsgptkg_intent",
    "attributes": {
        "name": "开始",
        "description": "团队起始节点",
        "ID": 1945714343936,
        "teamids": "3400004",
        "gdb_timestamp": 1725537224,
        "extra":"{\"status\": \"active\"}"
    }
    })


node2 = copy.deepcopy(node1)
node2.id = "yunjiu_2"
node2.attributes['name'] = "一阶相邻"
node2.attributes['ID'] = 2945714343937

node3 = copy.deepcopy(node1)
node3.id = "yunjiu_3"
node3.attributes['name'] = "结束"
node3.attributes['ID'] = 3945714343937


edge1 = GEdge(**{
    "start_id": f"ekg_team_{teamid}", 
    "end_id": "yunjiu_2", 
    "type": "opsgptkg_intent_route_opsgptkg_schedule",
    "attributes": {
        "DSTID": 2545543925760,
        "SRCID": 1213242748928,
        "gdb_timestamp": 1725960671
    }
    })

edge2 = copy.deepcopy(edge1)
edge2.start_id = "yunjiu_2"
edge2.end_id = "yunjiu_3"
edge2.attributes['SRCID'] = 2545543925760
edge2.attributes['DSTID'] = 3545543925760

teamid = "yunjiu_test"

# res = ekg_construct_service.add_nodes([node1,node2,node3], teamid)
# logger.info(res)

# ekg_construct_service.add_edges([edge1,edge2], teamid)

### 删除边 delete_edges ###
# res = ekg_construct_service.delete_edges([edge2], teamid)
# logger.info(res)

### 删除节点 delete_nodes ###
# res = ekg_construct_service.delete_nodes([node1,node2,node3], teamid)
# logger.info(res)

### 更新节点 update_nodes ###
# new_node2 = copy.deepcopy(node2)
# new_node2.attributes['name'] = "一阶相邻(更新)"
# res = ekg_construct_service.update_nodes([new_node2], teamid)
# logger.info(res)

### 更新边 update_edges ###
# new_edge1 = copy.deepcopy(edge1)
# new_edge1.attributes['extra'] = "dfdsfsre"
# res = ekg_construct_service.update_edges([new_edge1], teamid)
# logger.info(res)

## 根据nodeid 查询图信息
# logger.info('根据nodeid 查询图信息')
# res = ekg_construct_service.get_graph_by_nodeid("ekg_team_test",'opsgptkg_intent',hop=12, block_attributes={"type": "opsgptkg_task"})
# logger.info(res)

# print(ekg_construct_service.get_node_by_id(f"ekg_team_{teamid}")) #可以查询到

# res = ekg_construct_service.search_rootpath_by_nodeid('yunjiu_3','opsgptkg_intent','ekg_team_yunjiu_test')
# logger.info(res.nodes)

# res = ekg_construct_service.search_nodes_by_text(text = '一阶',teamid = 'yunjiu_test')
# logger.info(res)




######## test update_graph add
# new_node2 = copy.deepcopy(node2)
# new_node2.attributes['name'] = "一阶相邻修改"

node1 = GNode(**{
    "id": f"ekg_team_{teamid}", 
    "type": "opsgptkg_intent",
    "attributes": {
        "name": "开始",
        "description": "团队起始节点",
        "ID": 1945714343936,
        "teamids": "3400004",
        "gdb_timestamp": 1725537224,
        "extra":"{\"status\": \"active\"}"
    }
    })

# res = ekg_construct_service.update_graph(origin_nodes=[],
#                                          origin_edges=[],
#                                          new_nodes=[node1,node2],
#                                          new_edges=[edge1],
#                                          teamid=teamid,
#                                          rootid=f"ekg_team_{teamid}"
#                                          )
# logger.info(res)

# res = ekg_construct_service.get_graph_by_nodeid(node1.id,node1.type)
# logger.info(res)
# logger.info(len(res.nodes))
# logger.info(len(res.edges))

# logger.info("========= 删除边node1 edge1 ===========")
# res = ekg_construct_service.update_graph(origin_nodes=[node1,node2],
#                                          origin_edges=[edge1],
#                                          new_nodes=[node1],
#                                          new_edges=[],
#                                          teamid=teamid,
#                                          rootid=f"ekg_team_{teamid}"
#                                          )
# logger.info(res)

# logger.info("========= 删除边edge2 ===========")
# res = ekg_construct_service.update_graph(origin_nodes=[node1,node2,node3],
#                                          origin_edges=[edge1,edge2],
#                                          new_nodes=[node1,node2,node3],
#                                          new_edges=[edge1],
#                                          teamid=teamid,
#                                          rootid=f"ekg_team_{teamid}"
#                                          )
# logger.info(res)


# res = ekg_construct_service.get_graph_by_nodeid(node1.id,node1.type)
# logger.info(res)


# logger.info("========= 删除节点node3 ===========")
# res = ekg_construct_service.update_graph(origin_nodes=[node1,node2],
#                                          origin_edges=[edge1],
#                                          new_nodes=[node1],
#                                          new_edges=[],
#                                          teamid=teamid,
#                                          rootid=f"ekg_team_{teamid}"
#                                          )
# logger.info(res)

# res = ekg_construct_service.get_graph_by_nodeid(node1.id,node1.type)
# logger.info(res)
# logger.info(len(res.nodes))
# logger.info(len(res.edges))

############################ 测试graph #####################################

node1 = GNode(**{
    "id": "ekg_team_yunjiu_test",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "开始",
                        "description": "团队起始节点",
                        "ID": 4.617441492992E12,
                        "isTeamRoot": True,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 1729587508
                    }
    })

node2 = GNode(**{
    "id": "DyI9sEWjEQ1Cr0AdXi2GhDic8lqxHGR8",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "场景意图",
                        "description": "场景意图",
                        "ID": 6.617441492992E12,
                        "isTeamRoot": False,
                        "teamids": "yunjiu_test",
                        "gdb_timestamp": 2729587508
                    }
    })


edge1 = GEdge(**{
    "start_id": "ekg_team_yunjiu_test",
                    "end_id": "DyI9sEWjEQ1Cr0AdXi2GhDic8lqxHGR8",
                    "type": "opsgptkg_intent_route_opsgptkg_intent",
                    "attributes": {
                        "sourceHandle": "0",
                        "targetHandle": "2"
                    }
    })

### 删除节点 delete_nodes ###
# res = ekg_construct_service.delete_nodes([node1,node2], "yunjiu_test")
# logger.info(res)

## 添加节点
res = ekg_construct_service.update_graph(origin_nodes=[],
                                         origin_edges=[],
                                         new_nodes=[node1,node2],
                                         new_edges=[edge1],
                                         teamid="yunjiu_test",
                                         rootid="ekg_team_yunjiu_test"
                                         )
logger.info('#### update_graph返回信息 #####')
logger.info(res)

# ### 删除node2和边edge1 ###
# res = ekg_construct_service.update_graph(origin_nodes=[node1,node2],
#                                          origin_edges=[edge1],
#                                          new_nodes=[node1],
#                                          new_edges=[],
#                                          teamid="yunjiu_test",
#                                          rootid="ekg_team_yunjiu_test"
#                                          )
# logger.info('#### update_graph返回信息 #####')
# logger.info(res)

logger.info('#### get_graph_by_nodeid #####')
res = ekg_construct_service.get_graph_by_nodeid(node1.id,node1.type)
logger.info(res)
logger.info(len(res.nodes))
logger.info(len(res.edges))

### 删除节点 delete_nodes ###
# res = ekg_construct_service.delete_nodes([node1,node2], "yunjiu_test")
# logger.info(res)


####################################################################################

node_test_1 = GNode(**{
     "id": "ekg_team_hhh",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "ID": 9522373689344,
                        "name": "开始",
                        "description": "团队起始节点",
                        "gdb_timestamp": 1729676623,
                        "teamids": "hhh",
                        "isTeamRoot": True
                    }
    })

node_test_2 = GNode(**{
     "id": "X3wm9oNqxvlSAg5WD667ouI",
                    "type": "opsgptkg_intent",
                    "attributes": {
                        "name": "场景意图",
                        "description": ""
                    }
    })


# edge_test_1 = GEdge(**{
#      "start_id": "ekg_team_hhh",
#                     "end_id": "X3wm9oNqxvlSAg5WD667ouI",
#                     "attributes": {
#                         "sourceHandle": "2",
#                         "targetHandle": "1"
#                     }
#     })

# edge3 = GEdge(**{
#     "start_id": "ekg_team_default",
#                     "end_id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
#                     "type": "opsgptkg_intent_route_opsgptkg_schedule",
#                     "attributes": {
#                         "timestamp": 1,
#                         "gdb_timestamp": 1729652633,
#                         "sourceHandle": "0",
#                         "targetHandle": "2"
#                     }
#     })

# edge4 = GEdge(**{
#     "start_id": "MS4U9s5koTw5RaKYRG5QnD8LQCiYYeP9",
#                     "end_id": "vCPMMrxprW9D6zcHofYAs2JP2YGyBXRk",
#                     "type": "opsgptkg_intent_route_opsgptkg_schedule",
#                     "attributes": {
#                         "timestamp": 1,
#                         "gdb_timestamp": 1729653290,
#                         "sourceHandle": "0",
#                         "targetHandle": "2"
#                     }
#     })


###########################################################
# res = ekg_construct_service.update_graph(origin_nodes=[],
#                                          origin_edges=[],
#                                          new_nodes=[node_test_1],
#                                          new_edges=[],
#                                          teamid="hhh",
#                                          rootid="ekg_team_hhh"
#                                          )
# logger.info('#### update_graph返回信息 #####')
# logger.info(res)

### 删除node2和边edge1 ###
# res = ekg_construct_service.update_graph(origin_nodes=[node1,node2],
#                                          origin_edges=[edge1],
#                                          new_nodes=[node1],
#                                          new_edges=[],
#                                          teamid="yunjiu_test",
#                                          rootid="ekg_team_yunjiu_test"
#                                          )
# logger.info('#### update_graph返回信息 #####')
# logger.info(res)

# logger.info('#### get_graph_by_nodeid #####')
# res = ekg_construct_service.get_graph_by_nodeid(node1.id,node1.type)
# logger.info(res)
# logger.info(len(res.nodes))
# logger.info(len(res.edges))

