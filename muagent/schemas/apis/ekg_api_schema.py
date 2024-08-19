from pydantic import BaseModel
from typing import List, Dict
from enum import Enum

from muagent.schemas.common import GNode, GEdge




class EKGResponse(BaseModel):
    successCode: int
    errorMessage: str


# text2graph
class EKGT2GRequest(BaseModel):
    text: str
    intentText: str = ""
    intentNodeids: List[str] = []
    intentPath: List[str] = []
    teamid: str
    write2kg: bool = False

class EKGGraphResponse(EKGResponse):
    nodes: List[GNode]
    edges: List[GEdge]



# update graph by compare
class UpdateGraphRequest(BaseModel):
    originNodes: List[GNode]
    originEdges: List[GEdge]
    nodes: List[GNode]
    edges: List[GEdge]
    teamid: str



# get node by nodeid and nodetype
class GetNodeRequest(BaseModel):
    nodeid: str
    nodeType: str

class GetNodeResponse(EKGResponse):
    node: GNode



# get graph by nodeid\nodetpye\hop
class GetGraphRequest(BaseModel):
    nodeid: str
    nodeType: str
    hop: int = 10
    layer: str



# get node by nodeid and nodetype
class SearchNodesRequest(BaseModel):
    text: str
    nodeType: str
    teamid: str
    topK: int = 5

class GetNodesResponse(EKGResponse):
    nodes: List[GNode]



# get node by nodeid and nodetype
class SearchAncestorRequest(BaseModel):
    nodeid: str
    nodeType: str
    rootid: str
    hop: int = 10


class LLMParamsResponse(BaseModel):
    url: str
    model_name: str
    model_type: str
    api_key: str
    stop: str
    temperature: float
    top_k: int
    top_p: float

class EmbeddingsParamsResponse(BaseModel):
    # ollama embeddings
    url: str
    embedding_type: str
    model_name: str
    api_key: str
