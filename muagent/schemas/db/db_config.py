from pydantic import BaseModel
from typing import List, Dict



class DBConfig(BaseModel):
    db_type: str
    extra_kwargs: Dict = {}


class GBConfig(BaseModel):
    gb_type: str
    extra_kwargs: Dict = {}


class TBConfig(BaseModel):
    tb_type: str
    index_name: str            
    host: str
    port: str
    username: str
    password: str
    extra_kwargs: Dict = {}


class VBConfig(BaseModel):
    vb_type: str
    kb_root_path: str = None
    extra_kwargs: Dict = {}