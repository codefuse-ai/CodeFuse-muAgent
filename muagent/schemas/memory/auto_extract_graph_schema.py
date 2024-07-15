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
    # relation type for extract
    type: str
    attributes: List[Attribute]


class GNode(BaseModel):
    id: str
    attributes: Dict[str, str]


class GRelation(BaseModel):
    id: str
    start_id: str
    end_id: str
    attributes: Dict[str, str]


class ThemeEnums(Enum):
    '''
    the memory themes
    '''
    Person: str = "person"
    Event: str = "event"

