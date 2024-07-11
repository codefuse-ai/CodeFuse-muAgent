from pydantic import BaseModel
from typing import List, Dict
from enum import Enum



class Attribute(BaseModel):
    name: str
    description: str


class GNodeAbs(BaseModel):
    type: str
    attributes: List[Attribute]


class GRelationAbs(BaseModel):
    type: str
    attributes: List[Attribute]


class GNode(BaseModel):
    id: str = None
    type: str
    attributes: Dict[str, str]


class GRelation(BaseModel):
    id: str = None
    type: str
    left: GNode
    right: GNode
    attributes: Dict[str, str]


class ThemeEnums(Enum):
    '''
    the memory themes
    '''
    Person: str = "person"
    Event: str = "event"

