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
from muagent.prompt_manager import CommonPromptManager


from typing import (
    List, 
    Any,
    Union,
    Optional,
    Dict,
    Literal
)
from pydantic import BaseModel

class NewPromptManager(CommonPromptManager):

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
        # update new titles
        extra_registry_titles: Dict = {
            "EXAMPLE": {
                "description": "这里是一些实例以供参考。",
                "function": "",
                "display_type": "title"
            },
            "INPUT EXAMPLE": {
                "description": "this input example",
                "prompt": "",
                "function": "",
                "display_type": "description"
            },
            "OUTPUT EXAMPLE": {
                "description": "this output example",
                "prompt": "",
                "function": "handle_empty_key",
                "display_type": "description"
            },
        }
        # 
        extra_register_edges: List = [
            ("EXAMPLE", "INPUT EXAMPLE"),
            ("EXAMPLE", "OUTPUT EXAMPLE"),
        ]

        #
        new_dfsindex_to_str_format: Dict = {
            0: "#### {}\n{}",
            1: "### {}\n{}",
            2: "## {}\n{}",
            3: "# {}\n{}",
        }
        """use {title name} {description/function_value}"""
        
        super().__init__(
            system_prompt=system_prompt,
            input_template=input_template,
            output_template=output_template,
            prompt=prompt,
            language=language,
            extra_registry_titles=extra_registry_titles,
            extra_register_edges=extra_register_edges,
            new_dfsindex_to_str_format=new_dfsindex_to_str_format,
            monitored_agents=monitored_agents,
            monitored_fields=monitored_fields,
            **kwargs
        )


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
    language="en",
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

# prompt = bpm.pre_print(
#     query=query, memory=memory, tools=tools, 
#     agent_names=agent_names, agent_descs=agent_descs
# )
# print(prompt)

prompt = bpm.generate_prompt(
    query=query, memory=memory, tools=tools,
    agent_names=agent_names, agent_descs=agent_descs
)
print(prompt)