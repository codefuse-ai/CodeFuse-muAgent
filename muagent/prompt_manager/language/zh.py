ZH_TITLE_EDGES = [
    ("智能体配置", "角色"),
    ("智能体配置", "智能体信息"),
    ("智能体配置", "工具信息"),
    ("上下文", "会话记录"),
    ("上下文", "当前问题"),
]

ZH_TITLE_CONFIGS = {
    "智能体配置": {
        "description": "",
        "function": "handle_empty_key",
        "display_type": "title"
    },
    "上下文": {
        "description": "使用下面内容作为上下文的信息。",
        "function": "handle_empty_key",
        "display_type": "values"
    },
    "输入": {
        "description": "",
        "function": "handle_empty_key",
        "display_type": "values"
    },
    "输出": {
        "description": "",
        "function": "handle_react_memory",
        "display_type": "must_value"
    },
    "角色": {
        "description": "",
        "prompt": "",
        "function": "handle_agent_profile",
        "display_type": "description"
    },
    "工具信息": {
        "description": "",
        "prompt": """以下是您可以使用的工具列表：{formatted_tools}\n有效的 "tool_name" 值是：\n{tool_names}""",
        "function": "handle_tool_data",
        "display_type": "description"
    },
    "智能体信息": {
        "description": "",
        "prompt": '''请确保您的选择是列出的角色之一。可供选择的角色有：\n{agents}请确保从代理名称中选择角色，例如 {agent_names}''',
        "function": "handle_agent_data",
        "display_type": "description"
    },
    "会话记录": {
        "description": "在这个部分，我们将提供有关这个问题的上下文。",
        "function": "handle_session_records",
        "display_type": "value"
    },
    "当前问题": {
        "description": "在这个部分，我们将提供当前需要处理的问题。",
        "function": "handle_current_query",
        "display_type": "value"
    },
}




ZH_TITLE_FORMAT = {
    0: "#### {}\n{}",
    1: "### {}\n{}",
    2: "## {}\n{}",
    3: "# {}\n{}",
}

ZH_ZERO_TITLES = {
    "agent": "智能体配置", 
    "context": "上下文",
    "input": "输入",
    "output": "输出"
}

ZH_TITLES = {
    "title_prefix": [ZH_ZERO_TITLES["agent"], ZH_ZERO_TITLES["context"]],
    "title_suffix": [ZH_ZERO_TITLES["input"], ZH_ZERO_TITLES["output"]],
    "title_middle": [],
}


ZH_COMMON_TEXT = {
    "transition_text": "开始",
    "reponse_text": "请回答："
}
