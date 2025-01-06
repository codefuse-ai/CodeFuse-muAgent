import json
import hashlib
from loguru import logger
from typing import List, Tuple, Dict

from muagent.schemas.common import GNode, GEdge
from muagent.schemas.ekg import NodeSchema, TYPE2SCHEMA_BIZ



def decode_biznodes(
        nodes: List[GNode]
    ) -> Tuple[List[GNode], List[GEdge]]:
    '''
    compatible biz data : 
        - node's attributes "extra"
        - task node with tools and agents
    '''
    new_nodes = []
    new_edges = []
    for node in nodes:
        schema = TYPE2SCHEMA_BIZ.get(node.type,)
        extra = node.attributes.pop("extra", {})
        if extra and isinstance(extra, str):
            extra = json.loads(extra)
        elif extra and isinstance(extra, dict):
            pass
        else:
            extra = {}

        node.attributes.update(extra)
        node_data = schema(
            **{**{"id": node.id, "type": node.type}, **node.attributes}
        )

        # if node.type == "opsgptkg_task":
        #     logger.debug(f"schema:{ schema}")
        #     logger.debug(f"node_data:{ type(node_data)}")
        #     logger.debug(f"node_data:{ node_data}")
            
        node_data = {
            k:v
            for k, v in node_data.dict().items()
            if k not in ["type", "ID", "id", "extra"]
        }

        # if node.type == "opsgptkg_task":
        #     logger.debug(f"node_data:{ node_data}")

        # update agent/tool nodes and edges
        agents = node_data.pop("agents", [])
        tools = node_data.pop("tools", [])

        for agent_or_tool in agents + tools:

            if agent_or_tool["type"] not in ["opsgptkg_agent", "opsgptkg_tool"]:
                continue
            schema = TYPE2SCHEMA_BIZ.get(agent_or_tool["type"])
            agent_or_tool: NodeSchema = schema(**agent_or_tool)
            new_nodes.append(GNode(**{
                "id": agent_or_tool.id, 
                "type": agent_or_tool.type,
                "attributes": agent_or_tool.attributes()
            }))
            # may lost edge attributes
            new_edges.append(GEdge(
                start_id=node.id,
                end_id=agent_or_tool.id,
                type='_route_'.join(['opsgptkg_task', agent_or_tool.type]),
                attributes={}
            ))

        # if node.type == "opsgptkg_task":
        #     logger.debug(f"node_data:{ node_data}")
        #     logger.debug(f"node.attributes:{ node.attributes}")

        new_nodes.append(GNode(**{
            "id": node.id, 
            "type": node.type,
            "attributes": {**node_data, **node.attributes}
        }))
    return new_nodes, new_edges



def encode_biznodes(
        nodes: List[GNode], 
        edges: List[GEdge]
    ) -> Tuple[List[GNode], List[GEdge]]:
    '''
    compatible biz data: 
        - node's attributes "extra"
        - task node with tools and agents
    '''
    task_nodes_by_id: Dict[str, GNode] = {
        n.id: n for n in nodes if n.type=="opsgptkg_task"
    }
    agent_nodes_by_id: Dict[str, GNode] = {
        n.id: n for n in nodes if n.type in ["opsgptkg_tool"]
    }
    tool_nodes_by_id: Dict[str, GNode] = {
        n.id: n for n in nodes if n.type in ["opsgptkg_agent"]
    }

    new_edges = []
    for edge in edges:
        if edge.start_id in task_nodes_by_id:
            task_nodes_by_id[edge.start_id].attributes.setdefault("agents", [])
            task_nodes_by_id[edge.start_id].attributes.setdefault("tools", [])

            if edge.end_id in agent_nodes_by_id:
                task_nodes_by_id[edge.end_id].attributes["agents"].append(
                    agent_nodes_by_id[edge.end_id].dict()
                )
                continue

            if edge.end_id in tool_nodes_by_id:
                task_nodes_by_id[edge.end_id].attributes["tools"].append(
                    tool_nodes_by_id[edge.end_id].dict()
                )
                continue
        new_edges.append(edge)

    
    return nodes, new_edges
