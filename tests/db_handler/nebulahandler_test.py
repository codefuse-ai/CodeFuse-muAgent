# encoding: utf-8
'''
@author: 温进
@file: nebula_test.py
@time: 2023/11/16 下午2:48
@desc:
'''
import time

from tqdm import tqdm
from loguru import logger

import sys, os

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
print(src_dir)
sys.path.append(src_dir)
from muagent.db_handler.graph_db_handler.nebula_handler import NebulaHandler


if __name__ == '__main__':
    host = '127.0.0.1'
    port = '9669'
    username = 'root'
    password = ''
    space_name = 'client'

    nh = NebulaHandler(host, port, username, password, space_name=space_name)

    # add host
    # res = nh.add_host(host=host, port='9779')
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())


    # test create space
    # res = nh.create_space(space_name=space_name, vid_type='FIXED_STRING(30)')
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # test show space
    # res = nh.show_space()
    # logger.debug(res)

    # test drop space
    # res = nh.drop_space('testing')
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # show hosts
    # res = nh.execute_cypher('SHOW HOSTS', use_space_name=False)
    # logger.debug(res)

    # test create tags
    # tag_name = 'student'
    # prop_dict = {
    #     'age': 'int',
    #     'name': 'string'
    # }
    # nh.set_space_name('test')
    # res = nh.create_tag(tag_name, prop_dict)
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # test show tags:
    # res = nh.show_tags()
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # test insert vertex
    # st = time.time()
    # single_rt_list = []
    # properties_name = ['name', 'age']
    # value_dict = {
    #     'properties_name': ['name', 'age'],
    #     'values': {
    #         'aaa': ['a', 20]
    #     }
    # }
    # for _ in tqdm(range(1)):
    #     for idx in range(10):
    #         value_dict['values'][f'a{idx}'] = [f'a{idx}', 100]
    #     single_st = time.time()
    #     res = nh.insert_vertex(tag_name='student', value_dict=value_dict)
    #     single_rt = time.time() - single_st
    #     single_rt_list.append(single_rt)
    # total_rt = time.time() - st
    # logger.info('total_rt={}'.format(total_rt))
    # logger.info(f'mean of single rt={sum(single_rt_list) / len(single_rt_list)}')
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # test create edge_type
    # edge_type_name = 'friend'
    # prop_dict = {
    #     'dur': 'int'
    # }
    # res = nh.create_edge_type(edge_type_name, prop_dict)
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # test show edge
    # res = nh.show_edge_type()
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # test drop edge_type
    # res = nh.drop_edge_type('follow')
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # test insert edge
    # edge_type_name = 'friend'
    # value_dict = {
    #     'properties_name': ['dur'],
    #     'values': {
    #         ('a1', 'a2'): [100]
    #     }
    # }
    # res = nh.insert_edge(edge_type_name, value_dict)
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # test match
#     cypher = '''
# USE client;MATCH (v1:package)-[e:contain]->(v2) WHERE id(v2) == 'com.theokanning.openai.client.Utils' RETURN id(v1) as id;
#     '''
#
#     res = nh.execute_cypher(cypher, space_name=nh.space_name, format_res=True)
#     logger.debug(res)
#     logger.debug(res['id'][0])
#     logger.debug(type(res['id'][0]))
#     logger.debug(dir(res['id'][0]))


    # test get number of node
    # cypher = 'SUBMIT JOB STATS;'
    # res = nh.execute_cypher(cypher, space_name)
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # cypher = 'SHOW STATS'
    # res = nh.execute_cypher(cypher, space_name)
    # logger.debug(res)
    # logger.debug(res.is_succeeded())
    # logger.debug(res.error_msg())

    # res = nh.get_stat()
    # logger.debug(res)

    # test get vertices
    # res = nh.get_vertices()
    # logger.debug(res['v'][0].as_node().get_id())

#     cypher = '''MATCH (p:`package`)-[:contain]->(c:`class`)
# RETURN COUNT(c) AS class_count;'''
#     res = nh.execute_cypher(cypher, space_name)
#     logger.debug(res)
#     logger.debug(res.error_msg())
#     logger.debug(res.as_dict())
