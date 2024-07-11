from loguru import logger

import numpy as np

import redis
from redis.commands.search.indexDefinition import (
    IndexDefinition,
)

from redis.commands.json.path import Path
from redis.commands.search.query import Query
from redis.commands.search.field import (
    TextField,
    NumericField,
    VectorField,
    TagField
)

from muagent.schemas.db import TBConfig



class TbaseHandler:
    def __init__(
            self, 
            tbase_args, 
            index_name="test", 
            definition_value="message",
            tb_config: TBConfig = None
        ):
        self.client = redis.Redis(
            host=tbase_args['host'],
            port=tbase_args['port'],
            username=tbase_args['username'],
            password=tbase_args['password']
        )
        self.index_name = index_name
        self.definition_value = definition_value
        self.tb_config = tb_config

    def create_index(self, index_name=None, schema=None, definition: list =None):
        '''
        create index
        :param index_name:
        :param schema:
        :param definition:
        :return:
        '''
        index_name = index_name or self.index_name
        if schema is None:
            raise ValueError("Schema can't be None")

        definition = definition if definition else \
                IndexDefinition(prefix=[f"{self.definition_value}:"])
        res = self.client.ft(index_name).create_index(
            fields=schema,
            definition=definition,
        )
        # logger.debug(self.client.ft(index_name).info())
        return True

    def insert_data_hash(self, data_list, key="message_index", expire_time=86400):
        '''
        insert data into hash index
        :param index_name:
        :param data_list:
        :return:
        '''
        data_list = [data_list] if isinstance(data_list, dict) else data_list
        if not isinstance(data_list, list):
            raise ValueError(f"data_list'type is {type(data_list)}, it must be List, ")
        
        # logger.debug(f"{data_list}")
        for data in data_list:
            key_value = f"{self.definition_value}:" + data.get(key, "")
            r = self.client.hset(key_value, mapping=data)
            rr = self.client.expire(key_value, expire_time)
        return len(data_list)

    def search(self, query, index_name: str = None, query_params: dict = {}):
        '''
        search
        :param index_name:
        :param query:
        :param query_params
        :return:
        '''
        index_name = index_name or self.index_name
        index = self.client.ft(index_name)

        if type(query) == str:
            query = Query(query)

        res = index.search(query, query_params=query_params)
        return res

    def vector_search(self, base_query: str, index_name: str = None, query_params: dict={}):
        '''
        vector_search
        :param base_query:
        :param index_name:
        :param query_params
        :return:
        '''
        query = (
            Query(base_query)
                .sort_by('distance')
                .dialect(2)
        )
        r = self.search(query, index_name, query_params)
        return r

    def delete(self, content):
        '''
        delete
        :param id:
        :return:
        '''
        id = f"{self.definition_value}:{content}"
        res = self.client.delete(id)
        return res

    def get(self, content):
        id = f"{self.definition_value}:{content}"
        logger.debug(f"{id}")
        res = self.client.hgetall(id)
        return res

    def fuzzy_delete(self, collection_name, delete_str, index_name="test"):
        '''
        delete by metaid
        :param index_name:
        :param delete_str:
        :return:
        '''

        # search_first
        query = '(@document_keyword:{collection_name})'.replace('collection_name', collection_name) + f'''(@document_meta_id:"{delete_str}")'''
        logger.info(f'query={query}')
        res = self.search(index_name, query)
        logger.info(f'search result number={res.total}')

        for data in res.docs:
            # logger.info(data)
            document_id = data['document_id']
            self.delete(document_id)
        msg = f'delete success, num of delete entities={res.total}'
        return msg

    def is_index_exists(self, index_name: str = None):
        '''
        check if is already exist
        :param index_name:
        :return:
        '''
        index_name = index_name or self.index_name

        try:
            res = self.client.ft(index_name).info()
            return True
        except Exception as e:
            if str(e) == 'Unknown index name':
                return False

        return False

    def drop_index(self, index_name: str):
        '''
        drop index
        :return:
        '''
        try:
            res = self.client.ft(index_name).dropindex(delete_documents=True)
        except Exception as e:
            logger.info(f'error occured during drop_index, error message={e}')
            return False
        return True
    


