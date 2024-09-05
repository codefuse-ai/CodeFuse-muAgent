from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import time

from aliyun.log import *
from muagent.schemas.common import *
from muagent.schemas.db import SLSConfig

    
    
class AliYunSLSHandler:
    '''can ADD/DELETE within graph'''
    def __init__(
            self,
            sls_config: SLSConfig = SLSConfig(sls_type="aliyunSls")
    ):
        self.project = sls_config.extra_kwargs.get("project")
        self.logstore = sls_config.extra_kwargs.get("logstore")
        self.endpoint = sls_config.extra_kwargs.get("endpoint")
        self.accessKeyId = sls_config.extra_kwargs.get("accessKeyId")
        self.accessKey = sls_config.extra_kwargs.get("accessKey")
        
        self.client = LogClient(self.endpoint, self.accessKeyId, self.accessKey)

    def add_data(self, data: List[Tuple[str, str]]) -> str:
        # 将数据写入到 sls 中
        # > data_list: list of list of tuple [ [ ('k1', 'v1'), ('k2', 'v2')] ]
        log_item_list = [
            LogItem(timestamp=int(time.time()), contents=data)
        ]
        response = self.put_logs(self.logstore, log_item_list, )
        return response.log_print()
        
    def add_datas(self, data_list: List[List[Tuple[str, str]]]) -> str:
        # 将数据写入到 sls 中
        # > data_list: list of list of tuple [ [ ('k1', 'v1'), ('k2', 'v2')] ]
        log_item_list = [
            LogItem(timestamp=int(time.time()), contents=data)
            for data in data_list
        ]
        response = self.put_logs(self.logstore, log_item_list, )
        return response.log_print()

    def create_project(self, project, project_description=''):
        """创建项目"""
        return self.client.create_project(project, project_description)

    def create_logstore(self, logstore=None, ttl=30, shard_count=2):
        """创建日志库"""
        logstore = logstore or self.logstore
        return self.client.create_logstore(self.project, logstore, ttl, shard_count)

    def delete_logstore(self, logstore):
        """删除日志库"""
        return self.client.delete_logstore(self.project, logstore)

    def create_index(self, logstore, index_detail):
        """创建日志索引"""
        return self.client.create_index(self.project, logstore, index_detail)
        
    def list_logstores(self, project: str = None) -> List[str]:
        """获取项目中所有日志库名称"""
        request = ListLogstoresRequest(project or self.project)
        r = self.client.list_logstores(request)
        return r.logstores

    def list_shards(self, project: str = None, logstore: str = None) -> List[int]:
        response = self.client.list_shards(project or self.project, logstore or self.logstore)
        shards = response.get_shards_info()
        return  [i["shardID"] for i in shards]

    def put_logs(self, logstore, logitems: List[LogItem], topic=None, source=None):
        """写入日志"""
        req = PutLogsRequest(self.project, logstore, topic, source, logitems, compress=False)
        return self.client.put_logs(req)

    def get_logs(self, logstore, query, from_time, to_time, topic=None):
        """查询日志"""
        req = GetLogsRequest(self.project, logstore, from_time, to_time, topic, query)
        return self.client.get_logs(req)

    def pull_logs(self, logstore=None, count=10) -> List:
        """拉取日志"""
        logstore = logstore or self.logstore
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=3)
        
        shards = self.list_shards(logstore=logstore)
        shard_id = shards[0]
        
        # 获得开始cursor，传入 Shard ID 和开始时间
        start_cursor = self.client.get_cursor(self.project, logstore, shard_id, start_time.timestamp()).get_cursor()
        # 获得结束cursor，这使用"end"表示当前最新的cursor
        end_cursor = self.client.get_cursor(self.project, logstore, shard_id, "end").get_cursor()
        
        r = self.client.pull_logs(self.project, logstore, shard_id, start_cursor, count, end_cursor)
        return r.get_loggroup_list()

    def add_node(self, node: GNode):
        insert_nodes = self.node_process([node], "ADD")
        self.add_datas(insert_nodes)

    def add_nodes(self, nodes: List[GNode]):
        insert_nodes = self.node_process(nodes, "ADD")
        self.add_datas(insert_nodes)

    def add_edge(self, edge: GRelation):
        insert_relations = self.relation_process([edge], "ADD")
        self.add_datas(insert_relations)

    def add_edges(self, edges: List[GRelation]):
        insert_relations = self.relation_process(edges, "ADD")
        self.add_datas(insert_relations)

    def delete_node(self, node: GNode):
        insert_nodes = self.node_process([node], "DELETE")
        self.add_datas(insert_nodes)

    def delete_nodes(self, nodes: List[GNode]):
        insert_nodes = self.node_process(nodes, "DELETE")
        self.add_datas(insert_nodes)

    def delete_edge(self, edge: GRelation):
        insert_relations = self.relation_process([edge], "DELETE")
        self.add_datas(insert_relations)
        
    def delete_edges(self, edges: List[Tuple]):
        insert_relations = self.relation_process(edges, "DELETE")
        self.add_datas(insert_relations)

    def node_process(self, nodes: List[GNode], crud_type) -> List[List[Tuple]]:
        node_list = [
            [('id', node.id)] + \
            [(k, v) if k!="operation_type" else (k, crud_type) for k,v in node.attributes.items()]
            for node in nodes
        ]
        return node_list

    def relation_process(self, relations: List[GRelation], crud_type) -> List[List[Tuple]]:
        relation_list = [
            [('start_id', relation.start_id), ('end_id', relation.start_id)] +\
                [(k, v) if k!="operation_type" else (k, crud_type) for k,v in relation.attributes.items()]
            for relation in relations
        ]
        return relation_list