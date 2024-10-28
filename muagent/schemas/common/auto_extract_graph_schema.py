from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
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



###############################
##### tbase & gbase status #####
###############################

class TbaseExecStatus(BaseModel):
    errorMessage: Optional[str] = None
    statusCode: Optional[int] = None
    # 
    total: Optional[int] = None
    docs: Optional[List[dict]] = None


class GbaseExecStatus(BaseModel):
    # 
    errorMessage: Optional[str] = Field(
        "", title="errorMessage", 
        description="gql execution message",
    )
    # 
    errorCode: int = Field(
        0, title="errorCode", 
        description=f"gql exec status, if errorCode is 0"
        f"the gql execution is succeed",
    )
    # 
    results: Optional[Union[List, Dict]] = None
