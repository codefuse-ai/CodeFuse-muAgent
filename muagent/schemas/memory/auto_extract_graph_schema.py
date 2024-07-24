from pydantic import BaseModel
from typing import List, Dict
from enum import Enum



class Attribute(BaseModel):
    name: str
    description: str


class GNodeAbs(BaseModel):
    # node type for extract
    type: str
    attributes: List[Attribute]


class GRelationAbs(BaseModel):
    # todo: 废弃
    # relation type for extract
    type: str
    attributes: List[Attribute]


class GEdgeAbs(BaseModel):
    # relation type for extract
    type: str
    attributes: List[Attribute]


class GNode(BaseModel):
    id: str
    attributes: Dict


class GEdge(BaseModel):
    start_id: str
    end_id: str
    attributes: Dict


class GRelation(BaseModel):
    # todo: 废弃
    start_id: str
    end_id: str
    attributes: Dict


class ThemeEnums(Enum):
    '''
    the memory themes
    '''
    Person: str = "person"
    Event: str = "event"

