from pydantic import BaseModel
from typing import List, Dict
from enum import Enum
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
    ID: int = None # depend on id-str
    id: str
    # depend on user's difine
    name: str
    # depend on user's difine
    description: str
    gdb_timestamp: int



class EdgeSchema(BaseModel):
    # entity_id, ekg_node:{graph_id}:{node_type}:{content_md5}
    SRCID: int = None
    original_src_id1__: str
    # entity_id, ekg_node:{graph_id}:{node_type}:{content_md5}
    DSTID: int = None
    original_dst_id2__: str
    # 
    timestamp: int
    gdb_timestamp: int


#####################################################################
############################ EKG Schema #############################
#####################################################################

class NodeTypesEnum(Enum):
    TASK = 'opsgptkg_task'
    ANALYSIS = 'opsgptkg_analysis'
    PHENOMENON = 'opsgptkg_phenomenon'
    SCHEDULE = 'opsgptkg_schedule'
    INTENT = 'opsgptkg_intent'
    TOOL = 'opsgptkg_tool'
    TOOL_INSTANCE = 'opsgptkg_tool_instance'
    TEAM = 'opsgptkg_team'
    OWNER = 'opsgptkg_owner'
    EDGE = 'edge'

# EKG Node and Edge Schemas
class EKGNodeSchema(NodeSchema):
    teamids: str
    # version:str # yyyy-mm-dd HH:MM:SS
    extra: str = ''



class EKGEdgeSchema(EdgeSchema):
    # teamids: str
    # version:str # yyyy-mm-dd HH:MM:SS
    extra: str = ''

    def attrbutes(self, ):
        extra_attr = json.loads(self.extra)
        return extra_attr


class EKGIntentNodeSchema(EKGNodeSchema):
    # path: str = ''

    def attrbutes(self, ):
        extra_attr = json.loads(self.extra)
        return {
            **{
                "name": self.name,
                "description": self.description,
                "teamids": self.teamids,
                "path": self.path
            }, 
            **extra_attr
        }

class EKGScheduleNodeSchema(EKGNodeSchema):
    # do action or not
    enable: bool

    def attrbutes(self, ):
        extra_attr = json.loads(self.extra)
        return {
            **{
                "name": self.name,
                "description": self.description,
                "teamids": self.teamids,
                "enable": self.enable
            }, 
            **extra_attr
        }

class EKGTaskNodeSchema(EKGNodeSchema):
    # tool: str
    # needcheck: bool
    # when to access
    accesscriteria: str
    executetype: str
    # 
    # owner: str

    def attrbutes(self, ):
        extra_attr = json.loads(self.extra)
        return {
            **{
                "name": self.name,
                "description": self.description,
                "teamids": self.teamids,
                "accesscriteria": self.accesscriteria,
                "executetype": self.executetype,
                # "tool": self.tool
            }, 
            **extra_attr
        }
    

class EKGAnalysisNodeSchema(EKGNodeSchema):
    # when to access
    accesscriteria: str
    # do summary or not
    summaryswtich: bool
    # summary template
    dsltemplate: str

    def attrbutes(self, ):
        extra_attr = json.loads(self.extra)
        return {
            **{
                "name": self.name,
                "description": self.description,
                "teamids": self.teamids,
                "accesscriteria": self.accesscriteria,
                "summaryswtich": self.summaryswtich,
                "dsltemplate": self.dsltemplate 
            }, 
            **extra_attr
        }
    

class EKGPhenomenonNodeSchema(EKGNodeSchema):

    def attrbutes(self, ):
        extra_attr = json.loads(self.extra)
        return {
            **{
                "name": self.name,
                "description": self.description,
                "teamids": self.teamids,
            }, 
            **extra_attr
        }
    

# Ekg Tool Schemas
class ToolSchema(NodeSchema):
    # version:str # yyyy-mm-dd HH:MM:SS
    extra: str = ''


class EKGPToolTypeSchema(ToolSchema):
    toolprotocol: str
    status: bool


class EKGPToolSchema(EKGPToolTypeSchema):
    input: str # jsonstr
    output: str # jsonstr



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
    tool: str = ''
    access_criteria: str = ''
    teamids: str = ''
    extra: str = ''
    enable: bool = False
    dslTemplate: str = ''


class EKGNodeTbaseSchema(BaseModel):
    node_id: str
    node_type: str
    # node_str = 'graph_id={graph_id}'/teamids, use for searching by graph_id/teamids
    node_str: str
    name_keyword: str
    desc_keyword: str
    name_vector: List
    desc_vector: List


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
    NodeTypesEnum.TOOL.value: EKGPToolTypeSchema,
    NodeTypesEnum.TOOL_INSTANCE.value: EKGPToolSchema,
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