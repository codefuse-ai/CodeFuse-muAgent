from .base_agent import BaseAgent
from .single_agent import SingleAgent
from .react_agent import ReactAgent
from .task_agent import TaskAgent
from .group_agent import GroupAgent
from .user_agent import UserAgent
from .functioncall_agent import FunctioncallAgent
from ..schemas import AgentConfig

__all__ = [
    "BaseAgent",
    "SingleAgent",
    "ReactAgent",
    "TaskAgent",
    "GroupAgent",
    "UserAgent",
    "FunctioncallAgent"
]


def get_agent(agent_config: AgentConfig) -> BaseAgent:
    """Get the agent by agent config

    Args:
        agent_config (`AgentConfig`): The agent config

    Returns:
        `BaseAgent`: The specific agent
    """
    return BaseAgent.init_from_project_config(agent_config)