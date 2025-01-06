from pydantic import BaseModel
from typing import List, Dict, Optional, Literal, Union
from enum import Enum

from muagent.schemas.common import GNode, GEdge
from muagent.schemas.models import ChatMessage, Choice



class EKGResponse(BaseModel):
    successCode: int
    errorMessage: str

class EKGALResponse(BaseModel):
    algorithmResult: str
    predictedScore: float = 0.0

class EKGAIResponse(BaseModel):
    resultMap: EKGALResponse
    debugMessage: str = ""
    errorMessage: str
    serverIp: str = ""
    success: bool

class EKGQueryRequest(BaseModel):
    query: dict

class EKGFeaturesRequest(BaseModel):
    features: EKGQueryRequest


# embeddings
class EmbeddingsResponse(EKGResponse):
    successCode: int
    errorMessage: str
    embeddings: List[List[float]]

class EmbeddingsRequest(BaseModel):
    texts: List[str]

class LLMRequest(BaseModel):
    text: str
    stop: Optional[str]


class LLMFCRequest(BaseModel):
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None
    tools: List[Union[str, object]] = []
    tool_choice: Optional[Literal["auto", "required"]] = "auto"
    parallel_tool_calls: bool = False
    stop: Optional[str]


class LLMFCResponse(EKGResponse):
    choices: List[Choice]


class LLMResponse(EKGResponse):
    successCode: int
    errorMessage: str
    answer: str

# text2graph
class EKGT2GRequest(BaseModel):
    text: str
    intentText: str = ""
    intentNodeids: List[str] = []
    intentPath: List[str] = []
    teamid: str
    rootid: str
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
    rootNodeId: str

class UpdateGraphResponse(BaseModel):
    successCode: int
    errorMessage: str
    nodes: List
    edges: List




# get node by nodeid and nodetype
class GetNodeRequest(BaseModel):
    nodeid: str
    nodeType: Optional[str] = None
    serviceType: Literal["gbase", "tbase"] = "gbase"

class GetNodeResponse(EKGResponse):
    node: GNode = None



# get graph by nodeid\nodetpye\hop
class GetGraphRequest(BaseModel):
    nodeid: str
    nodeType: str
    hop: int = 10
    layer: str = "first" # first\second



# get node by nodeid and nodetype
class SearchNodesRequest(BaseModel):
    text: str
    nodeType: str = ""
    teamid: Optional[str] = None
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
    url: Optional[str] = None
    model_name: str
    model_type: str = "ollama"
    api_key: str = ""
    stop: Optional[str] = None
    temperature: float = 0.3
    top_k: int = 50
    top_p: float = 0.95

class LLMParamsRequest(LLMParamsResponse):
    pass


class EmbeddingsParamsResponse(BaseModel):
    # ollama embeddings
    url: Optional[str] = None
    embedding_type: str = "ollama"
    model_name: str = "qwen2.5:0.5b"
    api_key: str = ""


class EmbeddingsParamsRequest(EmbeddingsParamsResponse):
    pass


class LLMOllamaPullRequest(BaseModel):
    model_name: str
    
class EKGMigrationSeasoningResponse(BaseModel):
    resultCode: int
    errorMessage:str
    resultMap:dict
    



