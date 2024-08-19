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
    type: str
    attributes: Dict

    def __getattr__(self, name: str):
        return self.attributes.get(name)


class GEdge(BaseModel):
    start_id: str
    end_id: str
    type: str
    attributes: Dict


class Graph(BaseModel):
    nodes: List[GNode]
    edges: List[GEdge]
    paths: List[List[str]] = []


class GNodeRequest(BaseModel):
    id: str
    type: str
    attributes: Dict
    operationType: str


class GEdgeRequst(BaseModel):
    start_id: str
    end_id: str
    type: str
    attributes: Dict
    operationType: str

    
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

