# encoding: utf-8
'''
@author: 云玖
@file: nebula_test.py
@time: 2024/8/9 下午14:56
@desc:
'''
import time

from tqdm import tqdm
from loguru import logger

from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

import sys, os

import copy

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
print(src_dir)
sys.path.append(src_dir)

from muagent.schemas.common import GNode, GEdge
from muagent.db_handler.graph_db_handler.nebula_handler import NebulaHandler


if __name__ == '__main__':
    host = '127.0.0.1'
    port = '9669'
    username = 'root'
    password = 'nebula'
    space_name = 'client'

    nebula = NebulaHandler()

    #创建图空间
    #vid_type = 'FIXED_STRING(32)'
    #space_creation_result = nebula.create_space(space_name, vid_type)

    # 展示空间
    #res = nebula.show_space()
    #print(res)

    # 删除图空间
    #res = nebula.drop_space(space_name)
    #print(res)

    # 添加标签
    tag_name = 'player'
    prop_dict = {
        "name": "string",
        "age": "int"
        }
    
    #res = nebula.create_tag(tag_name, prop_dict)
    #print(res)

    # 展示标签
    #res = nebula.show_tags()
    #print(res)
    teamid = 'yunjiu_test'
    node1 = GNode(**{
    "id": "yunjiu_1", 
    "type": "opsgptkg_intent",
    "attributes": {
        "name": "开始",
        "description": "团队起始节点",
        "ID": 5945714343936,
        "teamids": "3400004",
        "gdb_timestamp": 1725537224,
        "extra":"dfsf"
    }
    })

    # res = nebula.is_nodeid_exist(node1)
    # logger.info(res)

    # print(type(node1.attributes.get('extra')))
    # res = nebula.add_node(node1)
    # logger.info(res)
    

    node2 = copy.deepcopy(node1)
    node2.id = "yunjiu_2"
    node2.attributes['ID'] = 2945714343936

    node3 = copy.deepcopy(node1)
    node3.id = "yunjiu_3"
    node3.attributes['ID'] = 3945714343936

    # res = nebula.add_node(node1)
    # logger.info(res)

    # res = nebula.add_node(node2)
    # logger.info(res)

    # res = nebula.add_node(node3)
    # logger.info(res)

    ##### 批量添加node #####
    # res = nebula.add_nodes([node1,node2,node3])
    # logger.info(res)


    ##### 更新node #####
    # print({"id":node3.id}, node3.attributes, node3.type, node3.id)
    # print(node3.attributes["name"])
    # node3.attributes["name"] = "结束"
    # res = nebula.update_node({"id":node3.id}, node3.attributes, node3.type, node3.id)
    # logger.info(res)

    ##### 删除node #####
    # res = nebula.delete_node({"id": node1.id},node1.type)
    # logger.info(res)

    # res = nebula.delete_nodes(node_type=node1.type, IDs=[node3.attributes["ID"],node2.attributes["ID"]])
    # logger.info(res)

    # ##### 查询节点 #####
    # res = nebula.get_current_nodes({"id": node3.id},node3.type)
    # logger.info(res)

    # res = nebula.get_current_nodes({"id": node2.id},node2.type)
    # logger.info(res)
    

    ##### Edge边 #######
    
    
    teamid = 'yunjiu_test'
    edge1 = GEdge(**{
    "start_id": "yunjiu_1", 
    "end_id": "yunjiu_2", 
    "type": "opsgptkg_intent_route_opsgptkg_intent",
    "attributes": {
        "DSTID": 2213242748928,
        "SRCID": 1545543925760,
        "gdb_timestamp": 1725960671
    }
    })

    edge2 = copy.deepcopy(edge1)
    edge2.start_id = "yunjiu_2"
    edge2.end_id = "yunjiu_3"
    edge2.attributes['SRCID'] = 2213242748928
    edge2.attributes['DSTID'] = 3213242748928
    
    ##### 添加Edge ##### 
    res = nebula.add_edge(edge1)
    logger.info(res)

    ##### 批量添加Edges ##### 
    # res = nebula.add_edges([edge2,edge1])
    # logger.info(res)

    ##### 更新Edge ##### 
    # new_edge1 = copy.deepcopy(edge1)
    # new_edge1.attributes["gdb_timestamp"] = 123456789

    # res = nebula.update_edge(edge1.start_id, edge1.end_id, new_edge1.attributes, edge1.type)
    # logger.info(res)

    ##### 删除Edge str##### 
    # res = nebula.delete_edge(edge1.start_id, edge1.end_id, edge1.type)
    # logger.info(res)

    ##### 删除Edge int##### 
    # res = nebula.delete_edge(edge1.attributes['SRCID'], edge1.attributes['DSTID'], edge1.type)
    # logger.info(res)

    # res = nebula.update_edge(edge1.start_id, edge1.end_id, new_edge1.attributes, edge1.type)
    # logger.info(res)

    ##### 批量删除Edges ##### 
    # 暂未用到
    # res = nebula.delete_edges(edge1.start_id, edge1.end_id, edge1.type)
    # logger.info(res)

    #### 根据int 边id SRCID 和 DSTID 来查询 #####
    # res = nebula.get_current_edgeID(edge1.attributes['SRCID'], edge1.attributes['DSTID'], edge1.type)
    # logger.info(res)




    ##### 查询Edge ##### 
    # res = nebula.get_current_edge(edge1.start_id, edge1.end_id, edge1.type)
    # logger.info(res)
    # res = nebula.get_current_edge(edge2.start_id, edge2.end_id, edge2.type)
    # logger.info(res)
    








    #创建edge标签
    #res = nebula.create_edge_type(edge1)

    #查看edge tag
    #res = nebula.show_edge_type()
    #print(res)

    #删除edge tag
    #res = nebula.drop_edge_type("friend")
    #print(res)

    #插入edge
    # res = nebula.add_edge(edge1)
    # logger.info(res)
    
    #批量插入edges
    #res = nebula.add_edges([edge2,edge3])
    
    #删除edge
    #res = nebula.delete_edge("yunjiu_3","yunjiu_2","friend")
    #print(res)


    #修改edge
    src_id = "yunjiu_2"
    dst_id = "yunjiu_3"
    set_attributes = {"since": 2025}
    edge_type = "friend"
    #res = nebula.update_edge(src_id, dst_id, set_attributes, edge_type)
    #print(res)
    


    #查询edges
    # res = nebula.get_current_edge("dfd","yunjiu_2")
    # logger.info(type(res))
    # logger.info(res)

    
    #查询edges id
    # res = nebula.get_current_edgeID("yunjiu_1","yunjiu_2","friend")
    # print(res)

    

    #根据attributes查询节点
    attributes = {
        "name": "yunjiu_test"
    }
    #res = nebula.get_current_nodes(attributes=attributes, node_type="player")
    #print(res)

    # res = nebula.get_current_node(attributes=attributes, node_type="player")
    # print(res)

    # res = nebula.get_current_nodeID(attributes=attributes, node_type="player")
    # print(res)

    #根据node id list查询nodes
    #res = nebula.get_nodes_by_ids(["yunjiu_2","yunjiu_1"])
    #print('Search result: \n', res)
    #print('Result lenth:', len(res))

    #get_neighbor_nodes
    # res = nebula.get_neighbor_nodes(attributes=attributes, node_type="player")
    # print('Search result: \n', res)
    # print('Result lenth:', len(res))

    #get_neighbor_edges
    # res = nebula.get_neighbor_edges(attributes=attributes, node_type="player")
    # print('Search result: \n', res)
    # print('Result lenth:', len(res))

    # res = nebula.check_neighbor_exist(attributes=attributes, node_type="player")
    # print(res)

    # block_attributes = {}
    # select_attributes = {}

    # res = nebula.get_hop_infos(attributes=attributes, node_type="player", 
    #                            hop = 2,block_attributes = block_attributes, 
    #                            select_attributes = select_attributes)
    # print(res)














    











    #result = res.add_node(node1)
    #print(result)





