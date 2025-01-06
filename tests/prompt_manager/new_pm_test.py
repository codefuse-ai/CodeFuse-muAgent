import os, sys
from loguru import logger
import json

os.environ["do_create_dir"] = "1"

try:
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
except Exception as e:
    # set your config
    logger.error(f"{e}")


# test local code
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)


from muagent.schemas import Memory, Message, PromptConfig
from muagent.prompt_manager import BasePromptManager
from muagent.agents import BaseAgent


from typing import (
    List, 
    Any,
    Union,
    Optional,
    Dict,
    Literal
)
from pydantic import BaseModel

class NewPromptManager(BasePromptManager):

    pm_type: str = "NewPromptManager"
    """The type of prompt manager."""

    def __init__(
            self, 
            system_prompt: str = "you are a helpful assistant!\n",
            input_template: Union[str, BaseModel] = "",
            output_template: Union[str, BaseModel] = "",
            prompt: Optional[str] = None,
            language: Literal["en", "zh"] = "en",
            *,
            monitored_agents=[], 
            monitored_fields=[],
            **kwargs
        ):
        super().__init__(
            system_prompt=system_prompt,
            input_template=input_template,
            output_template=output_template,
            prompt=prompt,
            language=language,
            monitored_agents=monitored_agents,
            monitored_fields=monitored_fields,
            **kwargs
        )
        # update new titles
        self.extra_registry_titles: Dict = {
            "AGENT PROFILE": {
                "description": "",
                "function": "handle_agent_profile",
                "display_type": "title"
            },
            "TOOL INFORMATION": {
                "description": "",
                "prompt": (
                    'Below is a list of tools that are available for your use:{formatted_tools}'
                    '\nvalid "tool_name" value is:\n{tool_names}'
                    ),
                "function": "handle_tool_data",
                "display_type": "description",
                "str_template": "**{}\n{}"
            },
            "AGENT INFORMATION": {
                "description": "",
                "prompt": (
                    'Please ensure your selection is one of the listed roles. Available roles for selection:\n{agents}'
                    'Please ensure select the Role from agent names, such as {agent_names}'
                    ),
                "function": "handle_agent_data",
                "display_type": "description"
            },
        }
        # 
        self.extra_register_edges: List = [
            ("AGENT PROFILE", "AGENT INFORMATION"),
            ("AGENT PROFILE", "TOOL INFORMATION"),
        ]

        #
        
        self.new_dfsindex_to_str_format: Dict = {
            0: "#### {}\n{}",
            1: "### {}\n{}",
            2: "## {}\n{}",
            3: "# {}\n{}",
        }
        """use {title name} {description/function_value}"""
        # 
        self.register_graph({}, [], {}, {})

    def register_prompt(self):
        """register input/output/prompt into titles and edges"""
        pass

    def handle_agent_profile(self, **kwargs) -> str:
        return self.system_prompt

    def handle_tool_data(self, **kwargs):
        import random
        from textwrap import dedent
        from muagent.tools import get_tool, BaseToolModel

        if 'tools' not in kwargs: return ""

        tools: List = kwargs.get('tools')
        prompt: str = kwargs.get('prompt')
        tools: List[BaseToolModel] = [get_tool(tool) for tool in tools if isinstance(tool, str)]
        
        if len(tools) == 0: return ""

        tool_strings = []
        for tool in tools:
            args_str = f'args: {str(tool.intput_to_json_schema())}' if tool.ToolInputArgs else ""
            tool_strings.append(f"{tool.name}: {tool.description}, {args_str}")
        formatted_tools = "\n".join(tool_strings)
        
        tool_names = ", ".join([tool.name for tool in tools])
        
        tool_prompt = dedent(prompt.format(formatted_tools=formatted_tools, tool_names=tool_names))
        while "\n " in tool_prompt:
            tool_prompt = tool_prompt.replace("\n ", "\n")
                        
        return tool_prompt

    def handle_agent_data(self, **kwargs):
        """"""
        import random
        from textwrap import dedent
        if 'agent_names' not in kwargs or "agent_descs" not in kwargs: 
            return ""
        
        agent_names: List = kwargs.get('agent_names')
        agent_descs: List = kwargs.get('agent_descs')
        prompt: str = kwargs.get('prompt')

        if len(agent_names) == 0: return ""

        random.shuffle(agent_names)
        agent_descriptions = []
        for agent_name, desc in zip(agent_names, agent_descs):
            while "\n\n" in desc:
                desc = desc.replace("\n\n", "\n")
            desc = desc.replace("\n", ",")
            agent_descriptions.append(
                f'"role name: {agent_name}\nrole description: {desc}"'
            )

        agent_description =  "\n".join(agent_descriptions)
        agent_prompt = dedent(
            prompt.format(agents=agent_description, agent_names=agent_names)
        )

        while "\n " in agent_prompt:
            agent_prompt = agent_prompt.replace("\n ", "\n")

        return agent_prompt
    
system_prompt = "you are a helpful assistant!\n"
intput_template = ""
output_template = ""
prompt = ""

agent_names = ["agent1", "agent2"]
agent_descs = [f"hello {agent}" for agent in agent_names]
tools = ["Multiplier", "WeatherInfo"]


bpm = NewPromptManager(
    # system_prompt=system_prompt,
    # input_template=intput_template,
    # output_template=output_template,
    # prompt=prompt,
    language="zh",
)

# 
message1 = Message(
    role_name="test",
    role_type="user",
    content="hello"
)
message2 = Message(
    role_name="test",
    role_type="assistant",
    content="hi! can i help you!"
)
query = Message(
    role_name="test",
    role_type="user",
    input_text="i want to know the weather of beijing",
    content="i want to know the weather of beijing",
    spec_parsed_content={
        "Retrieval Code Snippets": "hi"
    },
    global_kwargs={
        "Code Snippet": "hello",
        "Test Code": "nice to meet you."
    }
)
memory = Memory(messages=[message1, message2])

prompt = bpm.pre_print(
    query=query, memory=memory, tools=tools, 
    agent_names=agent_names, agent_descs=agent_descs
)
print(prompt)

prompt = bpm.generate_prompt(
    query=query, memory=memory, tools=tools,
    agent_names=agent_names, agent_descs=agent_descs
)
print(prompt)