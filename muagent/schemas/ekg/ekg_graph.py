from pydantic import BaseModel
from typing import List, Dict
from enum import Enum


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


class NodeTypesEnum(Enum):
    TASK = 'task'
    ANALYSIS = 'analysis'
    PHENOMENON = 'phenomenon'
    SCHEDULE = 'schedule'
    INTENT = 'intent'
    TOOL = 'tool'
    TOOL_INSTANCE = 'tool_instance'
    TEAM = 'team'
    OWNER = 'owner'


class EKGNodeSchema(BaseModel):
    # entity_id, ekg_node:{graph_id}:{node_type}:{content_md5}
    id: str
    # depend on user's difine
    name: str
    # depend on user's difine
    description: str


class EKGEdgeSchema(EKGNodeSchema):
    # ekg_edge:{graph_id}:{start_id}:{end_id}
    id: str
    # entity_id, ekg_node:{graph_id}:{node_type}:{content_md5}
    star_id: str
    # entity_id, ekg_node:{graph_id}:{node_type}:{content_md5}
    end_id: str


class EKGIntentNodeSchema(EKGNodeSchema):
    pass


class EKGScheduleNodeSchema(EKGNodeSchema):
    pass


class EKGTaskNodSchema(EKGNodeSchema):
    tool: str
    needCheck: bool
    accessCriteira: str


class EKGAnalysisNodeSchema(EKGNodeSchema):
    accessCriteira: str


class EKGPhenomenonNodeSchema(EKGNodeSchema):
    pass


class EKGGraphSlsSchema(BaseModel):
    # node_{NodeTypesEnum}
    type: str
    name: str
    id: str
    description: str
    start_id: str = ''
    end_id: str = ''
    # ADD/DELETE
    operation_type: str = ''
    # {tool_id},{tool_id},{tool_id}
    tool: str = ''
    access_criteria: str = ''


class EKGNodeTbaseSchema(BaseModel):
    node_id: str
    node_type: str
    # node_str = 'graph_id={graph_id}', use for searching by graph_id
    node_str: str
    node_vector: List


class EKGEdgeTbaseSchema(BaseModel):
    edge_id: str
    edge_type: str
    edge_source: str
    edge_target: str
    # edge_str = 'graph_id={graph_id}', use for searching by graph_id
    edge_str: str


class EKGTbaseData(BaseModel):
    nodes: list[EKGNodeTbaseSchema]
    edges: list[EKGEdgeTbaseSchema]


class EKGSlsData(BaseModel):
    nodes: list[EKGGraphSlsSchema]
    edges: list[EKGGraphSlsSchema]