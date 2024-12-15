# encoding: utf-8
'''
@author: 云玖
@file: nebula_handler.py
@time: 2024/8/9 下午14:56
@desc:
'''
import time
from loguru import logger
from typing import List, Dict, Any
import json
import requests

from muagent.schemas.common import GNode, GEdge, Graph
from muagent.schemas.db import GBConfig
from .base_gb_handler import GBHandler
from muagent.schemas.common import *
from muagent.utils.common_utils import double_hashing


from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from nebula3.data.DataObject import ValueWrapper
from nebula3.common.ttypes import *

from nebula3.data.ResultSet import ResultSet

class CustomResultSet(ResultSet):

    def __init__(self, resp, all_latency, decode_type='utf-8', timezone_offset=0):
        super().__init__(resp, all_latency, decode_type, timezone_offset)

    def error_msg(self):

        if self._resp.error_msg is None:
            return ''
        try:
            # 使用 UTF-8 解码，并在遇到解码错误时进行替换处理
            return self._resp.error_msg.decode(self._decode_type, errors='replace')
        except UnicodeDecodeError as e:
            # 记录错误日志并返回默认错误信息
            logger.error(f"Unicode decode error: {e}")
            return "Failed to decode error message."


class NebulaHandler:
    def __init__(self,gb_config : GBConfig = None):
        '''
        init nebula connection_pool
        @param host: host
        @param port: port
        @param username: username
        @param password: password
        '''
        config = Config()

        self.connection_pool = ConnectionPool()

        if gb_config == None:
            
            self.connection_pool.init([('graphd', '9669')], config)
            self.username = '' or 'root'
            self.nb_pw = '' or 'nebula'
            self.space_name = "client"
        else:
            logger.info('NebulaGraph容器启动中，请等待')
            
            if self.nebula_started(gb_config):
                self.connection_pool.init([(gb_config.extra_kwargs.get("host"), gb_config.extra_kwargs.get("port"))], config)
        
            self.username = gb_config.extra_kwargs.get("username")
            self.nb_pw = gb_config.extra_kwargs.get("password")
            self.space_name = gb_config.extra_kwargs.get("space")

    def nebula_started(self, gb_config: GBConfig):
        '''
        Continuously ping the nebula server until it has started
        If it does not start within 40 seconds, raise an exception
        '''
        # 80 attempts at 0.5 seconds each = 40 seconds
        max_attempts = 80 

        host = gb_config.extra_kwargs.get('host')
        port = gb_config.extra_kwargs.get('port')

        for attempt in range(max_attempts):
            if self.connection_pool.ping([host, port]):
                logger.info(f"nebula server is ok, total waiting time: {attempt * 0.5}s")
                return True
            
            logger.info(f"ping nebula server.. waiting time: {attempt * 0.5}s")
            time.sleep(0.5)

        raise Exception('The nebula server did not start within 40 seconds.')

    def execute_cypher(self, cypher: str, space_name: str = '',ignore_log: bool = False, format_res: str = 'as_primitive', use_space_name: bool = True):
        '''
        @param space_name: space_name, if provided, will execute use space_name first
        @param cypher:
        @return:
        '''
        with self.connection_pool.session_context(self.username, self.nb_pw) as session:
            if use_space_name:
                if space_name:
                    cypher = f'USE {space_name};{cypher}'
                elif self.space_name:
                    cypher = f'USE {self.space_name};{cypher}'

            # logger.debug(cypher)
            resp = session.execute(cypher)

            # 使用自定义 ResultSet 类处理响应
            resp = CustomResultSet(resp._resp, resp._all_latency)
            
            if ignore_log == False:
                if resp.is_succeeded():
                    #logger.info(f"Successfully executed Cypher query: {cypher}")
                    
                    pass
                    
                else:
                    logger.error(f"Failed to execute Cypher query: {cypher}")
                    print(resp.error_msg())
                

            if format_res == 'as_primitive':
                resp = resp.as_primitive()
            elif format_res == 'dict_for_vis':
                resp = resp.dict_for_vis()
        return resp
    
    def execute_cypher_return_status(self, cypher: str, space_name: str = '', format_res: str = 'as_primitive', use_space_name: bool = True):
        '''
        @param space_name: space_name, if provided, will execute use space_name first
        @param cypher:
        @return:
        '''
        with self.connection_pool.session_context(self.username, self.nb_pw) as session:
            if use_space_name:
                if space_name:
                    cypher = f'USE {space_name};{cypher}'
                elif self.space_name:
                    cypher = f'USE {self.space_name};{cypher}'

            # logger.debug(cypher)
            resp = session.execute(cypher)

            # 使用自定义 ResultSet 类处理响应
            resp = CustomResultSet(resp._resp, resp._all_latency)

            if resp.is_succeeded():
                logger.info(f"Successfully executed Cypher query: {cypher}")
                # 添加成功
                return GbaseExecStatus(
                errorMessage="GDB_SUCCEED", 
                errorCode=0, 
                )
                
            else:
                logger.error(f"Failed to execute Cypher query: {cypher}")
                print(resp.error_msg())
                return GbaseExecStatus(
                errorMessage=resp.error_msg(), 
                errorCode=resp.error_code(), 
                )
            

    def add_hosts(self, hostname, port):
            with self.connection_pool.session_context(self.username, self.nb_pw) as session:
                cypher = f'ADD HOSTS "{hostname}":{port}'
                resp = session.execute(cypher)
            return resp

    def close_connection(self):
        self.connection_pool.close()

    def create_space(self, space_name: str, vid_type: str = 'FIXED_STRING(32)', comment: str = ''):
        '''
        create space
        @param space_name: cannot startwith number
        @return:
        '''
        cypher = f'CREATE SPACE IF NOT EXISTS {space_name} (vid_type={vid_type}) comment="{comment}";'
        cypher = f'CREATE SPACE IF NOT EXISTS {space_name} (vid_type={vid_type}, partition_num=10, replica_factor=1);'
        # logger.debug(f"{cypher}")
        resp = self.execute_cypher(cypher, use_space_name=False)

        return resp

    def show_space(self):
        cypher = 'SHOW SPACES'
        resp = self.execute_cypher(cypher)
        return resp

    def drop_space(self, space_name):
        cypher = f'DROP SPACE {space_name}'
        return self.execute_cypher(cypher)
    
    def show_hosts(self):
        cypher = 'SHOW HOSTS'
        resp = self.execute_cypher(cypher, use_space_name=False)
        return resp

    def create_tag(self, tag_name: str, prop_dict: dict = {}):
        '''
        创建 tag
        @param tag_name: tag 名称
        @param prop_dict: 属性字典 {'prop 名字': 'prop 类型'}
        @return:
        '''
        cypher = f'CREATE TAG IF NOT EXISTS {tag_name}'
        cypher += '('
        for k, v in prop_dict.items():
            # id属性不能为空值
            if k == 'id':
                cypher += f'{k} {v} NOT NULL,'
            else:
                cypher += f'{k} {v} ,'
        cypher = cypher.rstrip(',')
        cypher += ')'
        cypher += ';'

        res = self.execute_cypher(cypher, self.space_name,True)
        return res

    def show_tags(self):
        '''
        查看 tag
        @return:
        '''
        cypher = 'SHOW TAGS'
        resp = self.execute_cypher(cypher, self.space_name)
        return resp

    def create_edge_type(self, edge_type_name: str, prop_dict: dict = {}):
        '''
        创建边标签
        @param edge_info: 边的信息字典，包括标签名称和属性字典
        @return: 执行结果
        '''

        # 构建 Cypher 查询
        cypher = f'CREATE EDGE IF NOT EXISTS {edge_type_name}'

        if prop_dict:
            cypher += '('
            for k, v in prop_dict.items():
                # 数据库系统命名字段，需要加``
                if k.upper() == 'TIMESTAMP': 
                    k = f'`{k}`'
                # 需根据输入类型进一步补充
                # if isinstance(v, int):
                #     prop_type = 'INT'
                # elif isinstance(v, float):
                #     prop_type = 'FLOAT'
                # elif isinstance(v, str):
                #     prop_type = 'STRING'
                # else:
                #     prop_type = 'UNKNOWN'
                cypher += f'{k} {v},'
            cypher = cypher.rstrip(',')
            cypher += ')'
        cypher += ';'

        # 执行查询
        res = self.execute_cypher(cypher, self.space_name,True)
        return res

    def show_edge_type(self):
        '''
        查看 tag
        @return:
        '''
        cypher = 'SHOW EDGES'
        resp = self.execute_cypher(cypher, self.space_name)
        return resp

    def delete_edge_type(self, edge_type_name: str):
        cypher = f'DROP EDGE {edge_type_name}'
        return self.execute_cypher(cypher, self.space_name)
    
    def add_node(self, node: GNode) -> GbaseExecStatus:
        '''
        Insert vertex into the graph.
        
        @param node: Dictionary containing node information
        @return: Result of Cypher query execution
        '''

        # 查询节点提前error判断
        check_res = self.check_node_before_execute(node.id,"add")
        if check_res != None:
            return check_res

        # 从GNode实例中提取信息
        vid = node.id
        tag_name = node.type  # 使用type作为tag名称
        # attributes = node.attributes

        # 初始化节点属性字典，并将节点的ID属性添加进去
        node_attributes = {"id": node.id, "type": node.type}
        node_attributes["ID"] = node.attributes.pop("ID", "") or double_hashing(node.id)
        node_attributes.update(node.attributes)
        
        # 构建 Cypher 查询
        properties_name = list(node_attributes.keys())
        
        # 构建查询字符串
        cypher = f'INSERT VERTEX {tag_name} ('
        cypher += ','.join(properties_name)
        cypher += ') VALUES '
        
        cypher += f'"{vid}":('
        for prop_name in properties_name:
            value = node_attributes.get(prop_name)
            if isinstance(value, str):
                if prop_name in {'extra', 'description', 'envdescription','updaterule'}:
                    # 转义换行符和双引号
                    value = value.replace("\n", "\\n").replace("\"", "\\\"")
                    cypher += f'"{value}",'
                elif prop_name == 'description':
                    value = value.replace("\n", "\\n").replace("\"", "\\\"")
                    cypher += f'"{value}",'
                elif prop_name == 'envdescription':
                    value = value.replace("\n", "\\n").replace("\"", "\\\"")
                    cypher += f'"{value}",'
                else:
                    cypher += f'"{value}",'
                #cypher += f'"{value}",'
            else:
                cypher += f'{value},'
        cypher = cypher.rstrip(',')
        cypher += ');'
        
        # 执行 Cypher 查询
        res = self.execute_cypher_return_status(cypher, self.space_name)
        return res
    
    def add_nodes(self, nodes: List[GNode]) -> GbaseExecStatus:
        for node in nodes:
            self.add_node(node)


    def add_edge(self, edge: GEdge) -> GbaseExecStatus:
        '''
        插入边
        @param edge: 边的信息字典，包括标签名称、起始节点 ID、结束节点 ID 和属性字典
        @return: 执行结果
        '''
        # if edge.start_id or edge.end_id == "":
        #     return GbaseExecStatus(
        #     errorMessage="GDB_ENGINE_PROP_INVALID", 
        #     errorCode=2, 
        #     )
        
        # if len(self.get_current_edge(edge.start_id, edge.end_id)) > 0:
        #     return GbaseExecStatus(
        #     errorMessage='GDB_ENGINE_PRIMARY_KEY_DUPLICATE', 
        #     errorCode=1, 
        #     )
        edge_exits = self.check_edge_before_execute(edge.start_id, edge.end_id,'add')
        if edge_exits != None:
            return edge_exits
        
        edge_type_name = edge.type
        src_vid = edge.start_id
        dst_vid = edge.end_id
        attributes = edge.attributes

        attributes["type"] = edge_type_name

        # 如果SRCID 和DSTID不存在，使用哈希赋值
        edge_attributes = {
            "SRCID": edge.attributes.pop("SRCID", 0) or double_hashing(edge.start_id),
            "DSTID": edge.attributes.pop("DSTID", 0) or double_hashing(edge.end_id),
        }
        attributes.update(edge_attributes)

        # 构建 Cypher 查询
        cypher = f'INSERT EDGE {edge_type_name} ('

        # 获取属性名称
        properties_name = list(attributes.keys())
        for property_name in properties_name:
            # 处理 @timestamp 字段
            if property_name == '@timestamp':
                cypher += f'`timestamp`,'
            else:
                cypher += f'{property_name},'
            #cypher += f'{property_name},'
        cypher = cypher.rstrip(',')

        cypher += ') VALUES '
        cypher += f'"{src_vid}"->"{dst_vid}":('

        # 添加属性值
        for attr_name in properties_name:
            attr_value = attributes[attr_name]
            if isinstance(attr_value, str):
                if attr_name == 'extra':
                    # 处理 extra 字段中的 JSON 字符串，转义双引号
                    attr_value = attr_value.replace('"', '\\"')
                    cypher += f'"{attr_value}",'
                else:
                    cypher += f'"{attr_value}",'
            else:
                cypher += f'{attr_value},'
        cypher = cypher.rstrip(',')
        cypher += ');'

        # 执行查询
        res = self.execute_cypher_return_status(cypher, self.space_name)
        return res
    
    def add_edges(self, edges: List[GEdge]) -> GbaseExecStatus:
        for edge in edges:
            self.add_edge(edge)

    def update_node(self, attributes: dict, set_attributes: dict, node_type: str = None, ID: int = None) -> GbaseExecStatus:
        # 添加引号并构造 SET 子句
        # set_clause = ', '.join([f'{k} = "{v}"' if isinstance(v, str) else f'{k} = {v}' for k, v in set_attributes.items()])
        
        node_id = attributes.get('id')
        
        # 查询节点提前error判断
        check_res = self.check_node_before_execute(node_id)
        if check_res != None:
            return check_res

        set_clause_parts = []
        for k, v in set_attributes.items():
            # todo: 需要对更多特殊字符进行转义
            if k == 'extra' and isinstance(v, str):
                # 转义 extra 字段中的 JSON 字符串中的双引号
                v = v.replace('"', '\\"')
                set_clause_parts.append(f'{k} = "{v}"')
            elif isinstance(v, str):
                set_clause_parts.append(f'{k} = "{v}"')
            else:
                set_clause_parts.append(f'{k} = {v}')

        set_clause = ', '.join(set_clause_parts)
        # if attributes == {}:
        #     attributes = {'ID': ID}
        # id = self.get_current_nodeID(attributes, node_type)
        #ngql里字段str需要用""括起来, 语句最好采用拼接的方式
        # cypher = f'UPDATE VERTEX ON {node_type} "{id}" '
        cypher = f'UPDATE VERTEX ON {node_type} "{node_id}" '
                
        cypher += f'SET {set_clause} '
                
        cypher += f'YIELD {", ".join(set_attributes.keys())};'

        # 执行查询
        res = self.execute_cypher_return_status(cypher, self.space_name)
        return res

    def update_edge(self, src_id, dst_id, set_attributes: dict, edge_type: str = None) -> GbaseExecStatus:
        # set_clause = ', '.join([f'{k} = "{v}"' if isinstance(v, str) else f'{k} = {v}' for k, v in set_attributes.items()])
        
        src_id, dst_id = self.get_current_edgeID(src_id, dst_id)

        edge_exits = self.check_edge_before_execute(src_id, dst_id)
        if edge_exits != None:
            return edge_exits
        
        # if self.check_edge_before_execute(src_id, dst_id) != None:
        #     return self.check_edge_before_execute(src_id, dst_id)

        set_clause_parts = []
        for k, v in set_attributes.items():
            if k == 'extra' and isinstance(v, str):
                # 转义 extra 字段中的 JSON 字符串中的双引号
                v = v.replace('"', '\\"')
                set_clause_parts.append(f'{k} = "{v}"')
            elif isinstance(v, str):
                set_clause_parts.append(f'{k} = "{v}"')
            else:
                set_clause_parts.append(f'{k} = {v}')

        set_clause = ', '.join(set_clause_parts)

        cypher = f'UPDATE EDGE ON {edge_type} "{src_id}" -> "{dst_id}" '
                
        cypher += f'SET {set_clause} '

        # 执行查询
        res = self.execute_cypher_return_status(cypher, self.space_name)
        return res
    
    def delete_node(self, attributes: dict, node_type: str = None, ID: int = None) -> GbaseExecStatus:
        node_id = attributes.get('id')
        # 查询节点提前error判断
        check_res = self.check_node_before_execute(node_id)
        logger.info(check_res)
        if check_res != None:
            return check_res
        
        cypher = f'DELETE VERTEX "{node_id}" WITH EDGE;'

        # 执行查询
        res = self.execute_cypher_return_status(cypher, self.space_name)
        return res

    def delete_nodes(self, attributes: dict = {}, node_type: str = None, IDs: List[int] = []) -> GbaseExecStatus:
        # todo: 如果IDs为空，需要使用atributes来查找，attributes需要是一个[dict]形式

        # 使用ID来查找nodeid再调用delete_node进行删除
        for Id in IDs:
            attributes_ID = {'ID': Id}
            node_id = self.get_current_nodeID(attributes_ID, node_type)
            self.delete_node(attributes={'id':node_id})

    def delete_edge(self, src_id, dst_id, edge_type: str = None) -> GbaseExecStatus:
        '''
        parameters
        src_id: str or int
        dst_id: str or int
        '''
        #首先需要判断是str类型的还是属性中int类型的,需要获取str id
        src_id, dst_id = self.get_current_edgeID(src_id, dst_id)

        if self.check_edge_before_execute(src_id, dst_id) != None:
            return self.check_edge_before_execute(src_id, dst_id)
        
        cypher = f'DELETE EDGE {edge_type} "{src_id}" -> "{dst_id}"@0;'

        # 执行查询
        res = self.execute_cypher_return_status(cypher, self.space_name)
        return res

    def delete_edges(self, id_pairs: List, edge_type: str = None):
        #该函数暂未用到

        # 构建DELETE EDGE语句
        edge_deletions = []
        for src_id, dst_id in id_pairs:
            edge_deletions.append(f'"{src_id}" -> "{dst_id}"')

        # 将所有边的删除语句拼接成一条完整的Cypher查询
        cypher = f'DELETE EDGE {edge_type} {", ".join(edge_deletions)};'

        # 执行查询
        res = self.execute_cypher(cypher, self.space_name)
        return res
        
    def get_nodeIDs(self, attributes: dict, node_type: str) -> List[int]:
        result = self.get_current_nodes(attributes, node_type)
        return [i.attributes.get("ID") for i in result]

    # 输出待确认，是自带id还是属性里的ID
    def get_current_nodeID(self, attributes: dict, node_type: str) -> int:
        result = self.get_current_node(attributes, node_type)
        
        return result.id
        #return result.attributes.get("ID")

    # 输出待确认
    def get_current_edgeID(self, src_id, dst_id, edge_type:str = None):
        # 如果是str类型id（start_id），直接返回
        if not isinstance(src_id, int) or not isinstance(dst_id, int):
            return src_id, dst_id
        else:
            # 如果不是str类型id（start_id）是int类型的，需要根据它查找（start_id）
            # 生成MATCH子句
            match_clause = f'MATCH (n0)-[e]->(n1) WITH e, properties(e) as props, keys(properties(e)) as kk'

            where_clause = f'props["SRCID"] == {src_id} AND props["DSTID"] == {dst_id}'

            where_clause = f'WHERE [i IN kk WHERE {where_clause}]'

            return_clause = 'RETURN e'

            cypher = f'{match_clause} {where_clause} {return_clause}'

            # cypher = f'''
            # MATCH (n0)-[e]->(n1) \
            # WITH e, properties(e) as props, keys(properties(e)) as kk \
            # WHERE [i in kk where props[""] == 90]  \
            # RETURN e;
            # '''

            # 执行查询
            resp = self.execute_cypher(cypher, self.space_name)

            decode_resp = self.decode_result(resp,['e'])

            resp = [item.get('e') for item in decode_resp if 'e' in item]

            try:
                # logger.info(resp[0])
                # str
                src_id = resp[0].start_id
                dst_id = resp[0].end_id

                return src_id, dst_id
            except IndexError:
                logger.info(f"未查询到{src_id}->{dst_id}Edge")
                return None, None

            

        

    def get_current_node(self, attributes: dict, node_type: str = None, return_keys: list = []) -> GNode:
        try:
            return self.get_current_nodes(attributes, node_type, return_keys)[0]
        except IndexError:
            logger.info("未查询到Node")
            return None

    def get_nodes_by_ids(self, ids: List[int] = []) -> List[GNode]:
        # 生成MATCH子句
        match_clause = 'MATCH (n0) WITH n0, properties(n0) as props, keys(properties(n0)) as kk '

        list_clause = ', '.join(f'{id}' for id in ids)
        # 生成WHERE子句
        where_clause = f'WHERE props["ID"] IN [{list_clause}]'

        # 生成RETURN子句
        return_clause = 'RETURN n0'

        # 拼接最终的Cypher查询语句
        cypher = f'{match_clause} {where_clause} {return_clause}'

        # 执行查询
        res = self.execute_cypher(cypher, self.space_name)

        logger.info(res)

        decode_resp = self.decode_result(res,'n0')

        return [item.get('n0') for item in decode_resp if 'n0' in item]
    
    def get_current_nodes(self, attributes: dict, node_type: str = None, return_keys: list = []) -> List[GNode]:
        
        # 生成MATCH子句
        match_clause = f'MATCH (n0{":" + node_type if node_type else ""}) WITH n0, properties(n0) as props, keys(properties(n0)) as kk '

        # 生成WHERE子句
        where_clause = ' AND '.join(
            f'props["{key}"] == "{value}"' if isinstance(value, str) else f'props["{key}"] == {value}'
            for key, value in attributes.items()
        )

        # 将WHERE子句包装成正确的格式
        where_clause = f'WHERE [i IN kk WHERE {where_clause}]'

        # 生成RETURN子句
        return_clause = 'RETURN n0' if not return_keys else f'RETURN n0, {", ".join(return_keys)}'

        # 拼接最终的Cypher查询语句
        cypher = f'{match_clause} {where_clause} {return_clause}'

        # 执行查询
        resp = self.execute_cypher(cypher, self.space_name)

        decode_resp = self.decode_result(resp,['n0'])

        # print('====================get_current_nodes==============')
        # print([item.get('n0') for item in decode_resp if 'n0' in item])
        # test_node = [item.get('n0') for item in decode_resp if 'n0' in item]
        # print(type(test_node[0].id))
        # print(type(test_node[0].id))


        return [item.get('n0') for item in decode_resp if 'n0' in item]

    def get_current_edge(self, src_id, dst_id, edge_type:str = None, return_keys: list = [], limits: int = 100) -> GEdge:
        if edge_type:
            cypher = f'''
            MATCH (n0)-[e:{edge_type}]->(n1) \
            WHERE id(n0) == "{src_id}" AND id(n1) == "{dst_id}"  \
            RETURN e \
            LIMIT {limits};
            '''
        else:
            cypher = f'''
            MATCH (n0)-[e]->(n1) \
            WHERE id(n0) == "{src_id}" AND id(n1) == "{dst_id}"  \
            RETURN e \
            LIMIT {limits};
            '''
        
        # 执行查询
        resp = self.execute_cypher(cypher, self.space_name)

        decode_resp = self.decode_result(resp,['e'])

        resp = [item.get('e') for item in decode_resp if 'e' in item]
        try:
            return resp[0]
        except IndexError:
            logger.info(f"未查询到{src_id}->{dst_id}Edge")
            return None

    
    # 结果待去重
    def get_neighbor_nodes(self, attributes: dict, node_type: str = None, return_keys: list = [],reverse: bool = False) -> List[GNode]:
        # 先通过get_current_nodes搜索到节点
        # 如果属性字典里直接没有包含id，先根据其他属性查询node id
        if not attributes['id']:
            result = self.get_current_nodes(attributes, node_type)
            id_list = [item.id for item in result]
        else:
            id_list = [attributes['id']]

        #print(result)
        
        #print(id_list) # ['yunjiu_3', 'yunjiu_4', 'yunjiu_2']
        id_list_str = '", "'.join(id_list)

        # 再根据搜索到的节点id查找附近的nodes
        if reverse:
            cypher = f'''MATCH (n0)<--(n1) \
            WHERE id(n0) in ["{id_list_str}"] \
            RETURN n1'''
        else:
            cypher = f'''MATCH (n0)-->(n1) \
            WHERE id(n0) in ["{id_list_str}"] \
            RETURN n1'''

        # 执行查询
        resp = self.execute_cypher(cypher, self.space_name)

        decode_resp = self.decode_result(resp,['n1'])

        return [item.get('n1') for item in decode_resp if 'n1' in item]

    # 结果待去重
    def get_neighbor_edges(self, attributes: dict, node_type: str = None, return_keys: list = []) -> List[GEdge]:
        # 先通过get_current_nodes搜索到节点
        result = self.get_current_nodes(attributes, node_type)

        edges_id_list = [item.id for item in result]

        edges_id_list_str = '", "'.join(edges_id_list)

        # 再根据搜索到的节点id查找附近的edges，示例：
        cypher = f'''MATCH (n0)-[e]-(n1) \
        WHERE id(n0) in ["{edges_id_list_str}"] \
        RETURN e'''

        # 执行查询
        resp = self.execute_cypher(cypher, self.space_name)

        decode_resp = self.decode_result(resp,['e'])

        return [item.get('e') for item in decode_resp if 'e' in item]

    def check_neighbor_exist(self, attributes: dict, node_type: str = None, check_attributes: dict = {}) -> bool:
        # 判断是否有邻居nodes
        result = self.get_neighbor_nodes(attributes, node_type)
        return len(result) > 0

    # 结果待去重
    def get_hop_infos(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: List[dict] = {}, select_attributes: dict = {}, reverse=False) -> Graph:
        '''
        hop >= 2， 表面需要至少两跳
        '''
        hop_max = 10

        hop_num = max(min(hop, hop_max), 2) # 2 <= hop_num <= 10

        result = self.get_current_nodes(attributes=attributes, node_type=node_type)

        nodes_id_list = [item.id for item in result]

        nodes_id_list_str = '", "'.join(nodes_id_list)

        if reverse:
            cypher = f'''MATCH p=(n0)<-[es*1..{hop_num}]-(n1) \
            WHERE id(n0) in ["{nodes_id_list_str}"] \
            RETURN n0, es, n1, p'''
        else:
            cypher = f'''MATCH p=(n0)-[es*1..{hop_num}]->(n1) \
            WHERE id(n0) in ["{nodes_id_list_str}"] \
            RETURN n0, es, n1, p'''

        # 执行查询
        resp = self.execute_cypher(cypher, self.space_name)

        decode_resp = self.decode_result(resp,['n0','es','n1','p'])

        # logger.info(decode_resp)

        #print(decode_resp)

        # 筛选
        decode_resp = self.deduplicate_paths(decode_resp, block_attributes, select_attributes)

        # logger.info(decode_resp) # 如果输出：[]
        if not decode_resp:
            return Graph(nodes=[], edges=[], paths=[])
        
        nodes = [decode_resp[0]['n0']] + [item.get('n1') for item in decode_resp if 'n1' in item]

        edges = [item.get('es') for item in decode_resp if 'es' in item]
        edges = [item for sublist in edges for item in sublist]

        # logger.info(edges)
        # # Edges去重
        edges = list({(edge.start_id, edge.end_id, edge.type): edge for edge in edges}.values())  # 根据起点、终点和类型去重

        # Nodes去重
        nodes = list({(node.id): node for node in nodes}.values()) # 根据node id去重
        
        # logger.info(edges)
        
        path = [item.get('p') for item in decode_resp if 'p' in item]

        # 如果 reverse == True，反转路径中的每个子路径
        if reverse:
            path = [p[::-1] for p in path]

        return Graph(nodes=nodes, edges=edges, paths=path)

    def get_hop_nodes(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: dict = []) -> List[GNode]:
        result = self.get_hop_infos(attributes, node_type, hop, block_attributes)
        return result.nodes

    def get_hop_edges(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: dict = []) -> List[GEdge]:
        result = self.get_hop_infos(attributes, node_type, hop, block_attributes)
        return result.edges

    def get_hop_paths(self, attributes: dict, node_type: str = None, hop: int = 2, block_attributes: dict = []) -> List[str]:
        # 
        result = self.get_hop_infos(attributes, node_type, hop, block_attributes)
        return result.paths

    def deduplicate_paths(self, result, block_attributes: dict = {}, select_attributes: dict = {}):
        
        if not block_attributes and not select_attributes:
            return result

        # 筛选1 - 根据block_attributes查找的nodeid列表: 如果path中的node出现在block列表里，删除
        if block_attributes:
            # block_result = self.get_current_nodes(block_attributes)
            # block_nodes_id_list = [item.id for item in block_result]
            # block_filtered_result = [
            #     path for path in result
            #     if not any(node in block_nodes_id_list for node in path.get('p', {}))
            # ]   
            block_nodes_id_list = []
            # 遍历每个block_attribute的条件并获取节点
            for block_attribute in block_attributes:
                block_result = self.get_current_nodes(block_attribute)
                block_nodes_id_list.extend([item.id for item in block_result])
            
            # 过滤结果，如果path中的节点出现在block列表里则删除
            block_filtered_result = [
                path for path in result
                if not any(node in block_nodes_id_list for node in path.get('p', {}))
            ]

            result = block_filtered_result

        # 筛选2 - 根据select_attributes筛选:如果path中有node没有出现在select列表里，删除
        # （注意如果select列表为空，不执行该筛选条件）
        if select_attributes:
            select_result = self.get_current_nodes(select_attributes)
            select_nodes_id_list = [item.id for item in select_result]
            select_filtered_result = [
                path for path in result
                if all(node in select_nodes_id_list for node in path.get('p', {}))
            ]
            result = select_filtered_result


        return result

    def decode_result(self, data: List[Dict[str, Any]], return_keys: List[str]) -> List[Dict[str, Any]]:
        #return_keys = [var.strip() for var in cypher.split("RETURN")[-1].split(',') if var.strip()]

        #print(return_keys)

        extracted_info = []

        for item in data:

            info = {}

            if 'n0' in return_keys:
                n0 = item.get('n0', {})
                info['n0'] = self.decode_node(n0)
            
            if 'e' in return_keys:
                e = item.get('e', {})
                info['e'] = self.decode_edge(e)

            if 'es' in return_keys:
                es = item.get('es', {})
                info['es'] = self.decode_edges(es)
            
            if 'n1' in return_keys:
                n1 = item.get('n1', {})
                info['n1'] = self.decode_node(n1)
            
            if 'p' in return_keys:
                p = item.get('p', {})
                info['p'] = self.decode_path(p)
            
            # 将字典添加到结果列表中
            extracted_info.append(info) 
        
        return extracted_info  # format: [{n0/n1/e/p:,},{},{}......]

    def decode_node(self, node_data: Dict[str, Any]) -> GNode:
        #nodes = []
    
        vid = node_data.get('vid', '')
        tags = node_data.get('tags', {})
        
        # 只处理第一个 tag
        for type_name, attributes in tags.items():
            # 使用 convert_value 处理 attributes 中的每一个值
            processed_attributes = {k: self.convert_value(v) for k, v in attributes.items()}
        
            node_instance = GNode(
                id=vid,
                type=type_name,
                # attributes=attributes
                attributes=processed_attributes
            )
            return node_instance
        
            #nodes.append(node_instance)
        
        return None

    def decode_edge(self, edge_data: List[Dict[str, Any]]) -> GEdge:
        if not edge_data:
            raise ValueError("The edge_data list is empty")
        
        #print(edge_data)

        #edge = edge_data[0]  # Since input data only contains one edge

        start_id = edge_data.get('src', '')
        end_id = edge_data.get('dst', '')
        edge_type = edge_data.get('type', '')
        attributes = edge_data.get('props', {})

        # 使用 convert_value 处理 attributes 中的每一个值
        processed_attributes = {k: self.convert_value(v) for k, v in attributes.items()}
        
        return GEdge(
            start_id=start_id,
            end_id=end_id,
            type=edge_type,
            # attributes=attributes
            attributes=processed_attributes
        )
    
    def decode_edges(self, edge_data: List[Dict[str, Any]]) -> List[GEdge]:
        if not edge_data:
            raise ValueError("The edge_data list is empty")
        
        edges = []

        for edge in edge_data:
            start_id = edge.get('src', '')
            end_id = edge.get('dst', '')
            edge_type = edge.get('type', '')
            attributes = edge.get('props', {})

            # 使用 convert_value 处理 attributes 中的每一个值
            processed_attributes = {k: self.convert_value(v) for k, v in attributes.items()}
            
            edges.append(GEdge(
                start_id=start_id,
                end_id=end_id,
                type=edge_type,
                attributes=processed_attributes
            ))
        
        return edges
    
    def decode_path(self, data: Dict[str, Any]) -> List[str]:
        nodes = data.get("nodes", [])
        path = [node.get("vid") for node in nodes if "vid" in node]
        return path
    
    # nebula对于加了/符号的str类型会转换成ValueWrapper类型输出，需要进行格式转换
    def convert_value(self, value_wrapper):
        if isinstance(value_wrapper, ValueWrapper):

            value_type = value_wrapper._get_type_name()
            if value_type == 'string':
                return value_wrapper.as_string()
            elif value_type == 'int':
                return value_wrapper.as_int()
            elif value_type == 'double':
                return value_wrapper.as_double()
            elif value_type == 'bool':
                return value_wrapper.as_bool()
            elif value_type == 'list':
                return value_wrapper.as_list()
            elif value_type == 'map':
                return value_wrapper.as_map()
            else:
                return None  # 未知类型处理
        return value_wrapper

    def is_nodeid_exist(self, nodeid: str) -> bool:
        cypher = f'MATCH (n0) WHERE id(n0) == "{nodeid}" RETURN n0'
        resp = self.execute_cypher(cypher, self.space_name)
        if resp == []:
            return False
        else:
            return True

    def check_edge_exist(self, src_id: str, dst_id: str) -> bool:
        try:
            if self.get_current_edge(src_id, dst_id):
                print('Edge already exists!')
                return True
        except Exception as e:
            print('Edge not exists!')
            return False
        

    def check_node_before_execute(self, nodeid: str, action: str = ""):
        '''
            action: operation methods(add/update/delete)
        '''

        # 当nodeid为空时
        if nodeid == "":
            return GbaseExecStatus(
            errorMessage="GDB_ENGINE_PROP_INVALID", 
            errorCode=2, 
            )
        # 节点是否存在: 1.删除时节点存在不报错 2.添加时节点存在报错 3.update时节点存在不报错
        if self.is_nodeid_exist(nodeid) and action == "add":
            logger.info('Node already exits!')
            return GbaseExecStatus(
            errorMessage='GDB_ENGINE_PRIMARY_KEY_DUPLICATE', 
            errorCode=1, 
            )
        
        return None

    def check_edge_before_execute(self, src_id, dst_id, action:str = '', timestamp = "need_add"):
        # timestamp、src_id、dst_id是否为空
        if timestamp == "" or src_id == "" or dst_id == "":
            return GbaseExecStatus(
            errorMessage="GDB_ENGINE_PROP_INVALID", 
            errorCode=2, 
            )
        # src_id&dst_id是否重复
        edge_exist = self.check_edge_exist(src_id, dst_id)
        if edge_exist == True and action == 'add':
            return GbaseExecStatus(
            errorMessage='GDB_ENGINE_PRIMARY_KEY_DUPLICATE', 
            errorCode=1, 
            )

        return None











