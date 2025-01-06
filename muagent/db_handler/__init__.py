# encoding: utf-8
'''
@author: 温进
@file: __init__.py.py
@time: 2023/11/16 下午3:15
@desc:
'''

from .graph_db_handler import NebulaHandler, NetworkxHandler, AliYunSLSHandler, GeaBaseHandler, GBHandler
from .vector_db_handler import LocalFaissHandler, TbaseHandler, ChromaHandler
from .db import _engine, Base

__all__ = [
    "GBHandler", "NebulaHandler", "NetworkxHandler", "GeaBaseHandler", 
    "ChromaHandler", "TbaseHandler", "LocalFaissHandler", 
    "AliYunSLSHandler"
]


def create_tables():
    Base.metadata.create_all(bind=_engine)

def reset_tables():
    Base.metadata.drop_all(bind=_engine)
    create_tables()


def check_tables_exist(table_name) -> bool:
    table_exist = _engine.dialect.has_table(_engine.connect(), table_name, schema=None)
    return table_exist

def table_init():
    if (not check_tables_exist("knowledge_base")) or (not check_tables_exist ("knowledge_file")) or \
            (not check_tables_exist ("code_base")):
        create_tables()
