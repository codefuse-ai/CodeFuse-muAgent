EN_TITLE_EDGES = [
    ("AGENT PROFILE", "ROLE"),
    ("AGENT PROFILE", "AGENT INFORMATION"),
    ("AGENT PROFILE", "TOOL INFORMATION"),
    ("CONTEXT FORMAT", "SESSION RECORDS"),
    ("CONTEXT FORMAT", "CURRENT QUERY"),
]

EN_TITLE_CONFIGS = {
    "AGENT PROFILE": {
        "description": "",
        "function": "handle_empty_key",
        "display_type": "title"
    },
    "CONTEXT FORMAT": {
        "description": "Use the content provided in the context.",
        "function": "handle_empty_key",
        "display_type": "values"
    },
    "INPUT FORMAT": {
        "description": "",
        "function": "handle_empty_key",
        "display_type": "values"
    },
    "RESPONSE OUTPUT FORMAT": {
        "description": "",
        "function": "handle_react_memory",
        "display_type": "must_value"
    },
    "ROLE": {
        "description": "",
        "prompt": "",
        "function": "handle_agent_profile",
        "display_type": "description"
    },
    "TOOL INFORMATION": {
        "description": "",
        "prompt": """Below is a list of tools that are available for your use:{formatted_tools}\nvalid "tool_name" value is:\n{tool_names}""",
        "function": "handle_tool_data",
        "display_type": "description"
    },
    "AGENT INFORMATION": {
        "description": "",
        "prompt": '''Please ensure your selection is one of the listed roles. Available roles for selection:\n{agents}Please ensure select the Role from agent names, such as {agent_names}''',
        "function": "handle_agent_data",
        "display_type": "description"
    },
    "SESSION RECORDS": {
        "description": "In this part, we will supply with the context about this question.",
        "function": "handle_session_records",
        "display_type": "value"
    },
    "CURRENT QUERY": {
        "description": "In this part, we will supply with current question to do.",
        "function": "handle_current_query",
        "display_type": "value"
    },
}




EN_TITLE_FORMAT = {
    0: "#### {}\n{}",
    1: "### {}\n{}",
    2: "## {}\n{}",
    3: "# {}\n{}",
}


EN_ZERO_TITLES = {
    "agent": "AGENT PROFILE", 
    "context": "CONTEXT FORMAT",
    "input": "INPUT FORMAT",
    "output": "RESPONSE OUTPUT FORMAT"
}


EN_TITLES = {
    "title_prefix": [EN_ZERO_TITLES["agent"], EN_ZERO_TITLES["context"]],
    "title_suffix": [EN_ZERO_TITLES["input"], EN_ZERO_TITLES["output"]],
    "title_middle": [],
}


EN_COMMON_TEXT = {
    "transition_text": "BEGIN!!!",
    "reponse_text": "Please response:"
}
