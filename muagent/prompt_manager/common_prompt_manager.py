from typing import (
    List, 
    Any,
    Union,
    Optional,
    Literal
)
import copy
from pydantic import BaseModel
import random
from textwrap import dedent
from loguru import logger
import json

from .base import *
from .base_prompt_manager import BasePromptManager
from ..schemas import Memory, Message, PromptConfig
from ..tools import get_tool, BaseToolModel

from muagent.connector.utils import *


class CommonPromptManager(BasePromptManager):
    """Prompt Manager of MarkDown style"""
    
    pm_type: str = "CommonPromptManager"
    """The type of prompt manager."""

    def __init__(
            self, 
            system_prompt: str = "you are a helpful assistant!\n",
            input_template: Union[str, BaseModel] = "",
            output_template: Union[str, BaseModel] = "",
            prompt: Optional[str] = "",
            language: Literal["en", "zh"] = "en",
            *,
            extra_registry_titles: Dict = {},
            extra_register_edges: List = [],
            new_dfsindex_to_str_format: Dict = {},
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
        self.extra_registry_titles: Dict = extra_registry_titles
        self.extra_register_edges: List = extra_register_edges
        self.new_dfsindex_to_str_format: Dict = new_dfsindex_to_str_format

        # 
        self.register_graph(
            TITLE_CONFIGS_LANGUAGE[self.language], 
            TITLE_EDGES_LANGUAGE[self.language], 
            TITLE_FORMAT_LANGUAGE[self.language], 
            titles=TITLE_LANGUAGE[self.language],
            zero_titles=ZERO_TITLES_LANGUAGE[self.language],
            common_texts=COMMON_TEXT_LANGUAGE[self.language],
        )

    def register_prompt(self, ):
        """register input/output/prompt into titles and edges"""
        input_str, output_str = "", ""
        input_values, output_values = {}, {}

        if self.system_prompt:
            input_str = extract_section(
                self.system_prompt, 
                self._zero_titles["input"]
            )
            output_str = extract_section(
                self.system_prompt, 
                self._zero_titles["output"]
            )

            input_values = parse_section_to_dict(
                self.system_prompt, 
                self._zero_titles["input"]
            )
            output_values = parse_section_to_dict(
                self.system_prompt, 
                self._zero_titles["output"]
            )
            self.system_prompt = extract_section(
                self.system_prompt, 
                self._zero_titles["agent"]
            ) or self.system_prompt

        if self.input_template:
            input_values = parse_section_to_dict(
                self.input_template, 
                self._zero_titles["input"]
            ) or input_values

            self.input_template = extract_section(
                self.input_template, 
                self._zero_titles["input"]
            ) or input_str

        if self.output_template:
            output_values = parse_section_to_dict(
                self.output_template, 
                self._zero_titles["output"]
            ) or output_values
            self.output_template = extract_section(
                self.output_template, 
                self._zero_titles["output"]
            ) or output_str
        # 
        self._registry_titles[self._zero_titles["input"]].update({
            "description": self.input_template or input_str, 
        })
        
        self._registry_titles[self._zero_titles["output"]].update({
            "description": self.output_template or output_str, 
        })
        self._registry_titles.update(
            {k: {
                "description": v, 
                "function": "handle_custom_data", 
                "display_type": "value",
                "str_template": "**{}:** {}",
                } 
            for k,v in (input_values|output_values).items()}
        )
        self._registry_edges.extend(
            [(self._zero_titles["output"], k) for k in input_values.keys()]
        )
        self._registry_edges.extend(
            [(self._zero_titles["output"], k) for k in output_values.keys()]
        )

    def pre_print(self, **kwargs):
        kwargs.update({"is_pre_print": True})
        prompt = self.generate_prompt(**kwargs)

        input_keys = parse_section(self.system_prompt, self._zero_titles["output"])
        llm_predict = "\n".join([f"**{k}:**" for k in input_keys])
        return_prompt = (
            f"{prompt}\n\n"
            f"{'#'*19}"
            "\n<<<<LLM PREDICT>>>>\n"
            f"{'#'*19}"
            f"\n\n{llm_predict}\n"
        )
        return return_prompt

    def parser(self, message: Message) -> Message:
        '''parse llm output into dict'''
        content = message.content
        # parse start
        parsed_dict = parse_text_to_dict(content)
        spec_parsed_dict = parse_dict_to_dict(parsed_dict)
        # select parse value
        action_value = parsed_dict.get('Action Status')
        if action_value:
            action_value = action_value.lower()

        code_content_value = spec_parsed_dict.get('python') or \
                            spec_parsed_dict.get('java')
        if action_value == 'tool_using':
            tool_params_value = spec_parsed_dict.get('json')
        else:
            tool_params_value = {}

        # add parse value to message
        message.action_status = action_value or "default"
        spec_parsed_dict["code_content"] = code_content_value
        spec_parsed_dict["tool_param"] = tool_params_value.get("tool_params")
        spec_parsed_dict["tool_name"] = tool_params_value.get("tool_name")
        # 
        message.update_parsed_content(parsed_dict)
        message.update_spec_parsed_content(spec_parsed_dict)
        return message
    
    def handler_prompt_values(self, **kwargs) -> Dict[str, str]:
        memory: Memory = kwargs.get("memory", None)
        query: Message = kwargs.get("query", None)
        result = {
            "query": query.content or query.input_text if query else "",
            "memory": memory.to_format_messages(format_type="str")
        }
        return result
    
    def handle_custom_data(self, **kwargs):
        '''get key-value from parsed_output_list or global_kargs'''
        key: str = kwargs.get("title_key", "")
        query: Message = kwargs.get('query')

        keys = [
            "_".join([i.title() for i in key.split(" ")]),
            " ".join([i.title() for i in key.split("_")]), 
            key
        ]
        keys = list(set(keys))

        content = ""
        for key in keys:
            if key in query.spec_parsed_content:
                content = query.spec_parsed_content.get(key)
                content = "\n".join(content) if isinstance(content, list) else content
                break
            if key in query.global_kwargs:
                content = query.global_kwargs.get(key)
                content = "\n".join(content) if isinstance(content, list) else content
                break

        return content
    
    def handle_tool_data(self, **kwargs):
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

    def handle_current_query(self, **kwargs) -> str:
        """"""
        query: Message = kwargs.get('query')
        if query:
            return query.input_text
        return ""
    
    def handle_session_records(self, **kwargs) -> str:

        memory: Memory = kwargs.get('memory', Memory(messages=[]))
        return memory.to_format_messages(
            content_key='parsed_contents', 
            format_type='str',
            with_tag=True
        )
    
    def handle_agent_profile(self, **kwargs) -> str:
        return extract_section(self.system_prompt, 'AGENT PROFILE') or self.system_prompt
    
    def handle_output_format(self, **kwargs) -> str:
        return extract_section(self.system_prompt, self._zero_titles["output"])

    def handle_react_memory(self, **kwargs) -> str:
        react_memory: Memory = kwargs.get('react_memory')

        if react_memory:
            return react_memory.to_format_messages(format_type="str")
        return ""

    def handle_task_memory(self, **kwargs) -> str:
        if 'task_memory' not in kwargs:
            return ""

        task_memory: Memory = kwargs.get('task_memory', Memory(messages=[]))
        if task_memory is None:
            return ""
        
        return "\n".join([
            "\n".join([f"**{k}:**\n{v}" for k,v in _dict.items() if k not in ["CURRENT_STEP"]])
            for _dict in task_memory.get_memory_values("parsed_content")
        ])

    def handle_current_plan(self, **kwargs) -> str:
        if 'query' not in kwargs:
            return ""
        query: Message = kwargs['query']
        return query.global_kwargs.get("CURRENT_STEP", "")
    