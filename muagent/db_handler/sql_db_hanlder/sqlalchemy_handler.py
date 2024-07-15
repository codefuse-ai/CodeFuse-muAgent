from contextlib import contextmanager
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from muagent.schemas.kb.base_schema import KnowledgeBaseSchema
from muagent.base_configs.env_config import SQLALCHEMY_DATABASE_URI

# connect the sql databse
_engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base = declarative_base()

session_factory = sessionmaker(bind=_engine)



# def init_session():
#     session = session_factory()

#     try:
#         yield session
#     finally:
#         try:
#             session.commit()
#         except Exception as e:
#             session.rollback()
#             raise e
#         finally:
#             session.close()



# def with_session(func):
#     def wrapper(*args, **kwargs):
#         session = session_factory()
#         try:
#             return func(session, *args, **kwargs)
#         finally:
#             try:
#                 session.commit()
#             except Exception as e:
#                 session.rollback()
#                 raise e
#             finally:
#                 session.close()
#     return wrapper


# @contextmanager
# def session_scope():
#     """上下文管理器用于自动获取 Session, 避免错误"""
#     session = session_factory(autoflush=True)
#     try:
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         raise e
#     finally:
#         session.close()


def db_session_commit_rollback_close(func):
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)  # 执行函数逻辑
            self.session.commit()  # 提交事务
            return result
        except Exception as e:
            self.session.rollback()  # 事务回滚
            print(f"An error occurred: {e}")  # 这里可以替换为日志记录或者返回错误信息
            raise
        finally:
            self.session.close()  # 关闭会话
            self.session = session_factory() # 重新创建会话以便复用handler
    return wrapper


from sqlalchemy import create_engine, Column, Integer, String
# 定义模型
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)

    def __repr__(self):
        return f"<User(name={self.name}, fullname={self.fullname})>"

t = User()



class SqlalchemyHandler():

    def __init__(self, ):
        # 创建 Session 实例
        self.session = session_factory()

    @db_session_commit_rollback_close
    def add(self, schema, kwargs):
        # 创建新用户对象
        data = schema(**kwargs)
        # 将对象添加到会话并提交保存到数据库
        self.session.add(data)
        return True

    @db_session_commit_rollback_close
    def query(self, schema, kwargs: dict, query_type="first"):
        if query_type == "first":
            # 查询单个对象
            data = self.session.query(schema).filter_by(**kwargs).first()
            datas = [data]
        else:
            # 查询所有对象
            datas = self.session.query(schema).all()

        for data in datas:
            print(data)
        return datas

    @db_session_commit_rollback_close
    def update(self, schema, kwargs: dict):
        # 查询后更新对象
        data = self.session.query(schema).filter_by(**kwargs).first()
        if data:
            for key, value in kwargs.items():
                # 只有在字段内时，才更新该属性
                if hasattr(data, key):
                    setattr(data, key, value)
        return True
    
    @db_session_commit_rollback_close
    def delete(self, schema, kwargs: dict, filter_keys: list = [],):
        filter_kwargs = {k:v for k,v in kwargs.items() if k in filter_keys}
        # 查询后删除对象
        data = self.session.query(schema).filter_by(**filter_kwargs).first()
        if data:
            self.session.delete(data)
            return True
        return False

    @db_session_commit_rollback_close
    def add_kb_to_db(self, schema, kwargs: dict, filter_keys: list = [],):
        filter_kwargs = {k:v for k,v in kwargs.items() if k in filter_keys}
        # 创建知识库实例
        data = self.session.query(schema).filter_by(**filter_kwargs).first()
        if not data:
            data = schema(**kwargs)
            self.session.add(data)
        else: # update kb with new vs_type and embed_model
            for key, value in kwargs.items():
                # 只有在字段内时，才更新该属性
                if hasattr(data, key):
                    setattr(data, key, value)
        return True
    
    @with_session
    def add_kb_to_db(session, kb_name, vs_type, embed_model):
        # 创建知识库实例
        kb = session.query(KnowledgeBaseSchema).filter_by(kb_name=kb_name).first()
        if not kb:
            kb = KnowledgeBaseSchema(kb_name=kb_name, vs_type=vs_type, embed_model=embed_model)
            session.add(kb)
        else: # update kb with new vs_type and embed_model
            kb.vs_type = vs_type
            kb.embed_model = embed_model
        return True


    @with_session
    def list_kbs_from_db(session, min_file_count: int = -1):
        kbs = session.query(KnowledgeBaseSchema.kb_name).filter(KnowledgeBaseSchema.file_count > min_file_count).all()
        kbs = [kb[0] for kb in kbs]
        return kbs


    @with_session
    def kb_exists(session, kb_name):
        kb = session.query(KnowledgeBaseSchema).filter_by(kb_name=kb_name).first()
        status = True if kb else False
        return status


    @with_session
    def load_kb_from_db(session, kb_name):
        kb = session.query(KnowledgeBaseSchema).filter_by(kb_name=kb_name).first()
        if kb:
            kb_name, vs_type, embed_model = kb.kb_name, kb.vs_type, kb.embed_model
        else:
            kb_name, vs_type, embed_model = None, None, None
        return kb_name, vs_type, embed_model


    @with_session
    def delete_kb_from_db(session, kb_name):
        kb = session.query(KnowledgeBaseSchema).filter_by(kb_name=kb_name).first()
        if kb:
            session.delete(kb)
        return True


    @with_session
    def get_kb_detail(session, kb_name: str) -> dict:
        kb: KnowledgeBaseSchema = session.query(KnowledgeBaseSchema).filter_by(kb_name=kb_name).first()
        if kb:
            return {
                "kb_name": kb.kb_name,
                "vs_type": kb.vs_type,
                "embed_model": kb.embed_model,
                "file_count": kb.file_count,
                "create_time": kb.create_time,
            }
        else:
            return {}

    @classmethod
    def create_tables(cls):
        Base.metadata.create_all(bind=_engine)

    @classmethod
    def reset_tables(cls, ):
        Base.metadata.drop_all(bind=_engine)
        SqlalchemyHandler.create_tables()

    @classmethod
    def table_init(cls, ):
        if (not SqlalchemyHandler.check_tables_exist("knowledge_base")) or (not SqlalchemyHandler.check_tables_exist ("knowledge_file")) or \
                (not SqlalchemyHandler.check_tables_exist ("code_base")):
            SqlalchemyHandler.create_tables()

    @classmethod
    def check_tables_exist(cls, table_name) -> bool:
        table_exist = _engine.dialect.has_table(_engine.connect(), table_name, schema=None)
        return table_exist
