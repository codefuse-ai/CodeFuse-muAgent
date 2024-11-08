from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Literal
from enum import Enum
import copy
import json


SHAPE2TYPE = {
    'rect': 'task',
    'parallelogram': 'analysis',
    'diamond': 'phenomenon',
    'circle': 'schedule',
    'process': 'task',
    'data': 'analysis',
    'decision': 'phenomenon',
    'start-end': 'schedule'
}

#####################################################################
############################ Base Schema #############################
#####################################################################
class NodeSchema(BaseModel):
    type: str
    ID: Optional[int] = None # depend on id-str
    id: str
    # depend on user's difine
    name: str
    # depend on user's difine
    description: str
    gdb_timestamp: Optional[int] = None
    # 
    extra: Union[str, Dict] = '{}'

    def attributes(self, ):
        attrs = copy.deepcopy(vars(self))
        # for k in ["ID", "type", "id"]:
        for k in ["type", "id"]:
            attrs.pop(k)
        attrs.update(json.loads(attrs.pop("extra", '{}') or '{}'))
        return attrs


class EdgeSchema(BaseModel):
    type: str
    # entity_id, ekg_node:{graph_id}:{node_type}:{content_md5}
    SRCID: Optional[int] = None
    original_src_id1__: str
    # entity_id, ekg_node:{graph_id}:{node_type}:{content_md5}
    DSTID: Optional[int] = None
    original_dst_id2__: str
    # 
    timestamp: Optional[int] = None
    gdb_timestamp: Optional[int] = None

    def attributes(self, ):
        attrs = copy.deepcopy(vars(self))
        # for k in ["SRCID", "DSTID", "type", "timestamp", "original_src_id1__", "original_dst_id2__"]:
        for k in ["type", "original_src_id1__", "original_dst_id2__"]:
            attrs.pop(k)
        attrs.update(json.loads(attrs.pop("extra", '{}') or '{}'))
        return attrs
#####################################################################
############################ EKG Schema #############################
#####################################################################

class NodeTypesEnum(Enum):
    TASK = 'opsgptkg_task'
    ANALYSIS = 'opsgptkg_analysis'
    PHENOMENON = 'opsgptkg_phenomenon'
    SCHEDULE = 'opsgptkg_schedule'
    INTENT = 'opsgptkg_intent'
    AGENT = 'opsgptkg_agent'
    TOOL = 'opsgptkg_tool'
    TOOL_TYPE = 'opsgptkg_tooltype'
    TEAM = 'opsgptkg_team'
    OWNER = 'opsgptkg_owner'
    EDGE = 'edge'

# EKG Node and Edge Schemas
class EKGNodeSchema(NodeSchema):
    teamids: str = ''
    # version:str # yyyy-mm-dd HH:MM:SS
    extra: str = '{}'


class EKGEdgeSchema(EdgeSchema):
    # teamids: str
    # version:str # yyyy-mm-dd HH:MM:SS
    extra: str = '{}'


class EKGIntentNodeSchema(EKGNodeSchema):
    pass


class EKGScheduleNodeSchema(EKGNodeSchema):
    # do action or not
    enable: bool = False
    envdescription: str = Field("",
        description=f"Initialization text, used to generate the initial environment, "
        f"if none is provided, it will be empty string"
    )


class EKGTaskNodeSchema(EKGNodeSchema):
    # when to access
    accesscriteria: str = '{}'
    executetype: str = ''

    # communication: str = Field(
    #     "", 
    #     description=f"Communication for advancing interaction with users"
    #     f" (only effective in precise consulting cases), targeting scenarios or risk operations."
    # )
    
    organization: str = Field("", description="the name of organization")

    owner: str = Field("", description="the name of owner")

    isolation: Literal["public", "private", "semi-public"] = Field(
        "public",
        description="Method of Message Isolation"
    )
    
    historyenable: Literal["yes", "no"] = Field(
        "no", description='Reference to historical memory'
    )
    
    action: Literal["parallel", "react", "plan", "single"] = Field(
        "single", description='Execution method of the task node'
    )
    
    dostop: Literal["yes", "no"] = Field(
        "no", description='Whether to perform termination checks during execution.'
    )
    
    dodisplay: Literal["yes", "no","True","False"] = Field(
        "no", description='Whether to display the result.'
    )

    updaterule: str = Field(
        "", description='Update rules for environment variables.'
    )
    
    keytext: str = Field(
        "",
        description=f'Key information (distinct from description, which may be too lengthy) '
        f'for retrieving historical session content.'
    )
    

class EKGAnalysisNodeSchema(EKGNodeSchema):
    # when to access
    accesscriteria: str = '{}'
    # do summary or not
    summaryswitch: bool = False
    # summary template
    dsltemplate: str = ''

    keytext: str = Field(
        "",
        description=f'Key information (distinct from description, which may be too lengthy) '
        f'for retrieving historical session content.'
    )

class EKGPhenomenonNodeSchema(EKGNodeSchema):
    pass
    

# Ekg Tool Schemas
class EKGToolTypeSchema(NodeSchema):
    toolprotocol: str
    status: bool


class EKGToolSchema(NodeSchema):
    filltype: Literal["auto", "manual", "var"] = Field(
        "auto",
        description='parameters fill type'
    )
    input: str = Field("", description='jsonstr')
    output: str = Field("", description='jsonstr')


class EKGAgentSchema(NodeSchema):
    modelname: str = Field("", description='llm model name')

# SLS / Tbase 
class EKGGraphSlsSchema(BaseModel):
    # node_{NodeTypesEnum}
    type: str = ''
    id: str = ''
    name: str = ''
    description: str = ''
    start_id: str = ''
    end_id: str = ''
    # ADD/DELETE
    operation_type: str = ''
    # {tool_id},{tool_id},{tool_id}
    executetype: str = ''
    accesscriteria: str = ''
    teamids: str = ''
    extra: str = ''
    enable: bool = False
    dsltemplate: str = ''
    summaryswitch: bool = False

    gdb_timestamp: int
    original_src_id1__: str = ""
    original_dst_id2__: str = ""

class EKGNodeTbaseSchema(BaseModel):
    node_id: str
    node_type: str
    # node_str = 'graph_id={graph_id}'/teamids, use for searching by graph_id/teamids
    node_str: str
    name_keyword: str
    description_keyword: str
    name_vector: List
    description_vector: List


class EKGEdgeTbaseSchema(BaseModel):
    # {start_id}:{end_id}
    edge_id: str
    edge_type: str
    # start_id
    edge_source: str
    # end_id
    edge_target: str
    # edge_str = 'graph_id={graph_id}'/teamids, use for searching by graph_id/teamids
    edge_str: str


class EKGTbaseData(BaseModel):
    nodes: list[EKGNodeTbaseSchema]
    edges: list[EKGEdgeTbaseSchema]


class EKGSlsData(BaseModel):
    nodes: list[EKGGraphSlsSchema]
    edges: list[EKGGraphSlsSchema]


TYPE2SCHEMA = {
    NodeTypesEnum.ANALYSIS.value: EKGAnalysisNodeSchema,
    NodeTypesEnum.TASK.value: EKGTaskNodeSchema,
    NodeTypesEnum.INTENT.value: EKGIntentNodeSchema,
    NodeTypesEnum.PHENOMENON.value: EKGPhenomenonNodeSchema,
    NodeTypesEnum.SCHEDULE.value: EKGScheduleNodeSchema,
    NodeTypesEnum.TOOL_TYPE.value: EKGToolTypeSchema,
    NodeTypesEnum.TOOL.value: EKGToolSchema,
    NodeTypesEnum.AGENT.value: EKGAgentSchema,
    NodeTypesEnum.EDGE.value: EKGEdgeSchema
}


#####################
##### yuque dsl #####
#####################

class YuqueDslNodeData(BaseModel):
    id: str
    label: str
    type: str

class YuqueDslEdgeData(BaseModel):
    id: str
    source: str
    target: str
    label: str


class YuqueDslDatas(BaseModel):
    nodes: List[YuqueDslNodeData]
    edges: List[YuqueDslEdgeData]