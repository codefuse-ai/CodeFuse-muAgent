from abc import ABCMeta, abstractmethod
from typing import (
    Any,
    Union,
    Optional,
    Type,
    Literal,
    Dict,
    List,
    Tuple,
    Sequence,
    Mapping
)
from pydantic import BaseModel
from loguru import logger
import os
import uuid
import copy

from .base import *
from .util import edges_to_graph_with_cycle_detection
from ..sandbox import NBClientBox
from ..tools import get_tool
from ..schemas import Memory, Message, PromptConfig
from ..schemas.common import ActionStatus, LogVerboseEnum

from muagent.base_configs.env_config import KB_ROOT_PATH


class _PromptManagerWrapperMeta(ABCMeta):
    """A meta call to replace the prompt manager wrapper's __call__ function with
    wrapper about error handling."""

    def __new__(mcs, name: Any, bases: Any, attrs: Any) -> Any:
        if "__call__" in attrs:
            attrs["__call__"] = attrs["__call__"]
        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name: Any, bases: Any, attrs: Any) -> None:
        if not hasattr(cls, "_registry"):
            cls._registry = {}
            cls._type_registry = {}
        else:
            cls._registry[name] = cls
            if hasattr(cls, "pm_type"):
                cls._type_registry[cls.pm_type] = cls
        super().__init__(name, bases, attrs)


class BasePromptManager(metaclass=_PromptManagerWrapperMeta):
    
    pm_type: str = "BasePromptManager"
    """The type of prompt manager."""

    def __init__(
            self, 
            system_prompt: str = "you are a helpful assistant!\n",
            input_template: Union[str, BaseModel] = "",
            output_template: Union[str, BaseModel] = "",
            prompt: Optional[str] = "",
            language: Literal["en", "zh"] = "en",
            *,
            monitored_agents=[], 
            monitored_fields=[],
            log_verbose: str = "0",
            workdir_path: str =  KB_ROOT_PATH,
            **kwargs
        ):
        # 
        self.system_prompt = system_prompt
        self.input_template = input_template
        self.output_template = output_template
        self.prompt = prompt
        self.language = language
        # decrapted
        self.monitored_agents = monitored_agents
        self.monitored_fields = monitored_fields
        # 
        self.extra_registry_titles: Dict = {}
        self.extra_register_edges: Sequence = []
        self.new_dfsindex_to_str_format: Dict = {}
        """use {title name} {description/function_value}"""

        # 
        self.codebox = NBClientBox(do_code_exe=True)  # Initialize code execution box
        self.workdir_path = workdir_path  # Set the working directory path
        self.log_verbose = os.environ.get("log_verbose", "0") or log_verbose  # Configure logging verbosity
    
    @classmethod
    def from_config(self, prompt_config: PromptConfig, **kwargs) -> 'BasePromptManager':
        """Get the prompt manager from PromptConfig"""
        init_kwargs = {**kwargs, **prompt_config.dict()}
        return self.get_wrapper(prompt_config.prompt_manager_type)(**init_kwargs)
    
    @classmethod
    def get_wrapper(cls, prompt_manager_type: str) -> Type['BasePromptManager']:
        """Get the specific PromptManager wrapper"""
        if prompt_manager_type in cls._type_registry:
            return cls._type_registry[prompt_manager_type]  # type: ignore[return-value]
        elif prompt_manager_type in cls._registry:
            return cls._registry[prompt_manager_type]  # type: ignore[return-value]
        else:
            raise KeyError(
                f"Unsupported prompt_manager_type [{prompt_manager_type}]"
            )

    def register_graph(
            self, 
            title_configs: Mapping[str, Mapping] = {}, 
            title_edges: Sequence[Sequence[str]] = {}, 
            title_format: Mapping[int, str] = {}, 
            titles: Mapping[str, Sequence[str]] = {},
            zero_titles: Mapping = {},
            common_texts: Mapping[str, str] = {}
        ):
        """transform title and edge into title graph to execute"""
        # custom define
        self.register_env(
            title_configs, title_edges, title_format, titles, 
            zero_titles=zero_titles, 
            common_texts=common_texts
        )
        self.register_prompt()

        # prepare title graph
        start_nodes, self.title_graph = edges_to_graph_with_cycle_detection(self._registry_edges)
        for title in start_nodes:
            if title not in self._title_prefix + self._title_suffix:
                self._title_middle.append(title)

        if LogVerboseEnum.le(LogVerboseEnum.Log3Level, os.environ.get("log_verbose", "0")):
            logger.debug(f"{self._registry_titles}, {self._registry_edges}, {self.title_graph}")

    def register_env(
            self, 
            title_configs: Mapping[str, Mapping] = {}, 
            title_edges: Sequence[Sequence[str]] = {}, 
            title_format: Mapping[int, str] = {}, 
            titles: Mapping[str, Sequence[str]] = {},
            *,
            zero_titles: Mapping = {},
            common_texts: Mapping[str, str] = {}
        ):
        self._registry_titles = copy.deepcopy(title_configs)
        self._registry_titles.update(self.extra_registry_titles)
        self._registry_edges = copy.deepcopy(title_edges)
        self._registry_edges.extend(self.extra_register_edges)

        self._dfsindex_to_str_format = copy.deepcopy(title_format)
        self._dfsindex_to_str_format.update(self.new_dfsindex_to_str_format)
    
        self._title_prefix = titles.get("title_prefix", [])
        self._title_suffix = titles.get("title_suffix", [])
        self._title_middle = titles.get("title_middle", [])

        self._zero_titles = copy.deepcopy(zero_titles) # or ZERO_TITLES_LANGUAGE.get(self.language)
        self._common_texts = copy.deepcopy(common_texts) or COMMON_TEXT_LANGUAGE.get(self.language)

    @abstractmethod
    def register_prompt(self, ):
        """register input/output/prompt into titles and edges"""
        raise NotImplementedError(
            f"Prompt Manager Wrapper [{type(self).__name__}]"
            f" is missing the required `register_prompt`"
            f" method.",
        )

    def pre_print(self, **kwargs) -> str:
        kwargs.update({"is_pre_print": True})
        prompt = self.generate_prompt(**kwargs)
        return prompt
    
    def generate_prompt(self, **kwargs) -> str:
        '''force to print all prompt format whatever it has value'''
        if self.prompt:
            return self.prompt.format(**self.handler_prompt_values(**kwargs))
        
        is_pre_print = kwargs.get("is_pre_print", False)
        # update title's description and function_value
        title_values = {}
        for title, title_config in self._registry_titles.items():
            if hasattr(self, title_config["function"]):

                handler = getattr(self, title_config["function"])
                function_value = handler(
                    prompt=title_config.get("prompt", ""), title_key=title, **kwargs
                ) if handler else None
            else:
                function_value = title_config["description"]
                
            title_values[title] = {
                "description": title_config["description"],
                "function_value": function_value,
                "display_type": title_config["display_type"],
                "str_template": title_config.get("str_template", ""),
                "prompt": title_config.get("prompt", ""),
            }

        # transform title values into 'markdown' prompt by title graph
        prompt_values: List[str] = []
        prompt_values = self._process_title_values(
            title_values, 
            title_type="description", 
            prompt_values=prompt_values,
            is_pre_print=is_pre_print
        )

        transition_text = self._common_texts["transition_text"]
        prompt_values.append(self._dfsindex_to_str_format[0].format(transition_text, ""))

        prompt_values = self._process_title_values(
            title_values, 
            title_type="value", 
            prompt_values=prompt_values,
            is_pre_print=is_pre_print
        )

        # logger.info(prompt_values)
        reponse_text = self._common_texts["reponse_text"]
        if not any("RESPONSE OUTPUT" in i for i in prompt_values):
            prompt_values.append(reponse_text)
        elif not any(["RESPONSE OUTPUT\n" in i for i in prompt_values]):
            prompt_values.append(self._dfsindex_to_str_format[0].format("RESPONSE OUTPUT", ""))
        # return prompt except '\n' in end
        prompt_values = [pv.rstrip('\n') for pv in prompt_values]
        return '\n\n'.join(prompt_values)

    def _process_title_values(
            self, 
            title_values: Mapping[str, Mapping[str, Any]], 
            title_type: Literal["description", "value"],
            prompt_values: Sequence[str] = [],
            is_pre_print=False
        ):
        '''process title values to prompt'''

        def append_prompt_dfs(titles: Sequence[str], prompt_values: Sequence=[], dfs_index=0):
            ''''''
            if titles == [] or titles is None: return prompt_values
            for title in titles:
                title_value = title_values.get(title)
                ctitles = self.title_graph.get(title, [])
                ctitle_values = [
                    ctitle
                    for ctitle in ctitles
                    if title_values.get(ctitle, {}).get('function_value') 
                ]

                str_template = title_value.get(
                    "str_template", self._dfsindex_to_str_format[dfs_index]
                ) or self._dfsindex_to_str_format[dfs_index]
                description = title_value["description"]
                function_value = title_value["function_value"]
                display_type = title_value["display_type"]
                prompt = title_value["prompt"]

                # logger.info(
                #     f"title={title}, description={description}, function_value={function_value} \n"
                #     f"display_type={display_type}, str_template={str_template} \n"
                #     f"ctitles= {ctitles}, ctitle_values={ctitle_values}"
                # )

                # todo display_type==only_value
                if title_type=="description":
                    if display_type == "title":
                        prompt_values.append(str_template.format(title, description or function_value))
                    elif display_type=="description" and function_value:
                        prompt_values.append(str_template.format(title, function_value or description or prompt))
                    elif display_type == "value" and (function_value or len(ctitle_values)>0):
                        prompt_values.append(str_template.format(title, description or function_value))
                    elif display_type == "values" and len(ctitle_values)>0:
                        prompt_values.append(str_template.format(title, description or function_value))
                    elif display_type == "must_value" and (description or function_value or len(ctitle_values)>0):
                        prompt_values.append(str_template.format(title, description or function_value))
                    elif is_pre_print:
                        prompt_values.append(str_template.format(title, description or function_value))
                elif title_type=="value":
                    if display_type == "values" and len(ctitle_values)>0:
                        prompt_values.append(str_template.format(title.replace(' FORMAT', ''), ""))
                    # must value
                    elif display_type == "must_value" and (function_value and len(ctitle_values)>0):
                        prompt_values.append(str_template.format(title.replace(' FORMAT', ''), function_value))
                        continue
                    elif display_type == "must_value" and function_value:
                        prompt_values.append(str_template.format(title.replace(' FORMAT', ''), function_value))
                    elif display_type == "must_value" and len(ctitle_values)>0:
                        prompt_values.append(str_template.format(title.replace(' FORMAT', ''), ""))
                    # value
                    elif display_type == "value" and (function_value and len(ctitle_values)>0):
                        prompt_values.append(str_template.format(title.replace(' FORMAT', ''), function_value))
                    elif display_type == "value" and function_value:
                        prompt_values.append(str_template.format(title.replace(' FORMAT', ''), function_value))
                    elif display_type == "value" and len(ctitle_values)>0:
                        prompt_values.append(str_template.format(title.replace(' FORMAT', ''), ""))
                    elif is_pre_print and display_type not in ["title", "description"]:
                        prompt_values.append(str_template.format(title.replace(' FORMAT', ''), function_value))

                prompt_values = append_prompt_dfs(ctitles, prompt_values, dfs_index+1)

            return prompt_values

        start_titles = self._title_prefix + self._title_middle + self._title_suffix
        return append_prompt_dfs(start_titles, prompt_values)

    def parser(self, message: Message) -> Message:
        '''parse llm output into dict'''
        return message

    def step_router(
            self, 
            msg: Message, 
            session_index: str = "",
            **kwargs
        ) -> Tuple[Message, ...]:
        """Route a message to the appropriate step for processing based on its action status.

        Args:
            msg (Message): The input message that needs processing.
            session_index (str): The session identifier for managing the conversation.
            **kwargs: Additional parameters for processing.

        Returns:
            Tuple[Message, ...]: The processed message and any observation message.
        """
        session_index = msg.session_index or session_index or str(uuid.uuid4())
        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"message.action_status: {msg.action_status}")
            
        observation_msg = None
        # Determine the action to take based on the message's action status
        if msg.action_status == ActionStatus.CODE_EXECUTING:
            msg, observation_msg = self.code_step(msg, session_index)
        elif msg.action_status == ActionStatus.TOOL_USING:
            msg, observation_msg = self.tool_step(msg, session_index, **kwargs)
        elif msg.action_status == ActionStatus.CODING2FILE:
            self.save_code2file(msg, self.workdir_path)
        # Handle other action statuses as needed (currently no operations for these)
        elif msg.action_status == ActionStatus.CODE_RETRIEVAL:
            pass
        elif msg.action_status == ActionStatus.CODING:
            pass

        return msg, observation_msg

    def code_step(self, msg: Message, session_index: str) -> Message:
        """Execute code contained in the message.

        Args:
            msg (Message): The message containing code to be executed.
            session_index (str): The session identifier for managing the conversation.

        Returns:
            Tuple[Message, Message]: The processed message and an observation message regarding code execution.
        """
        # Execute the code using the codebox and capture the result
        code_key = "code_content"
        code_content = msg.spec_parsed_content.get(code_key, "")
        code_answer = self.codebox.chat(
            '```python\n{}```'.format(code_content)
        )

        # Prepare a response message based on code execution result
        observation_title = {
            "error": "The return error after executing the above code is {code_answer}，need to recover.\n",
            "accurate": "The return information after executing the above code is {code_answer}.\n",
            "figure": "The return figure name is {uid} after executing the above code.\n"
        }
        code_prompt = (
            observation_title["error"].format(code_answer=code_answer.code_exe_response)
            if code_answer.code_exe_type == "error" else 
            observation_title["accurate"].format(code_answer=code_answer.code_exe_response)
        )
        
        # Create an observation message for logging code execution outcome
        observation_msg = Message(
            session_index=session_index,
            role_name="function",
            role_type="observation",
            input_text=code_content,
        )

        uid = str(uuid.uuid1())  # Generate a unique identifier for related content
        if code_answer.code_exe_type == "image/png":
            # If the code execution produces an image, log the result and update the message
            msg.global_kwargs[uid] = code_answer.code_exe_response
            msg.step_content += "\n**Observation:**: " + observation_title["figure"].format(uid=uid)
            msg.parsed_contents.append({"Observation": observation_title["figure"].format(uid=uid)})
            observation_msg.update_content("\n**Observation:**: " + observation_title["figure"].format(uid=uid))
            observation_msg.update_parsed_content({"Observation": observation_title["figure"].format(uid=uid)})
        else:
            # Log the standard execution result
            msg.step_content += f"\n**Observation:**: {code_prompt}\n"
            observation_msg.update_content(code_prompt)
            observation_msg.update_parsed_content({"Observation": f"{code_prompt}\n"})
        
        # Log the observations at the defined verbosity level
        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"Code Observation: {msg.action_status}, {observation_msg.content}")
        
        return msg, observation_msg

    def tool_step(
            self, 
            msg: Message, 
            session_index: str,
            **kwargs
        ) -> Message:
        """Execute a tool based on parameters in the message.

        Args:
            msg (Message): The message that specifies the tool to be executed.
            session_index (str): The session identifier for managing the conversation.
            **kwargs: Additional parameters for processing, including available tools.

        Returns:
            Tuple[Message, ...]: 
                The processed message and an observation message regarding the tool execution.
        """
        observation_title = {
            "error": "there is no tool can execute.\n",
            "accurate": "",
            "figure": "The return figure name is {uid} after executing the above code.\n"
        }
        no_tool_msg = "\n**Observation:** there is no tool can execute.\n"  # Message for missing tool
        tool_names = kwargs.get("tools")  # Retrieve available tool names
        extra_params = kwargs.get("extra_params", {})
        tool_param = msg.spec_parsed_content.get("tool_param", {})  # Parameters for the tool execution
        tool_param.update(extra_params)
        tool_name = msg.spec_parsed_content.get("tool_name", "")  # Name of the tool to execute

        # Create a message to log the tool execution result
        observation_msg = Message(
            session_index=session_index,
            role_name="function",
            role_type="observation",
            input_text=str(tool_param),
        )
        if LogVerboseEnum.ge(LogVerboseEnum.Log2Level, self.log_verbose):
            logger.debug(f"message: {msg.action_status}, {tool_param}")

        if tool_name not in tool_names:
            msg.step_content += f"\n{no_tool_msg}"
            observation_msg.update_content(no_tool_msg)
            observation_msg.update_parsed_content({"Observation": no_tool_msg})
        else:
            # Execute the specified tool and capture the result
            tool = get_tool(tool_name)
            tool_res = tool.run(**tool_param)
            msg.step_content += f"\n**Observation:** {tool_res}.\n"
            msg.parsed_contents.append({"Observation": f"{tool_res}.\n"})
            observation_msg.update_content(f"**Observation:** {tool_res}.\n")
            observation_msg.update_parsed_content({"Observation": f"{tool_res}.\n"})

        # Log the observations at the defined verbosity level
        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"**Observation:** {msg.action_status}, {observation_msg.content}")
        
        return msg, observation_msg

    def save_code2file(self, msg: Message, project_dir="./"):
        """Save the code from the message to a specified file.

        Args:
            msg (Message): The message containing the code to be saved.
            project_dir (str): Directory path where the code file will be saved.
        """
        filename = msg.parsed_content.get("SaveFileName")  # Retrieve filename from message content
        code = msg.spec_parsed_content.get("code")  # Extract code content from the message

        # Replace HTML entities in the code
        for k, v in {"&gt;": ">", "&ge;": ">=", "&lt;": "<", "&le;": "<="}.items():
            code = code.replace(k, v)

        project_dir_path = os.path.join(self.workdir_path, project_dir)  # Construct project directory path
        file_path = os.path.join(project_dir_path, filename)  # Full path for the output code file

        # Create directories if they don't exist
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write the code to the file
        with open(file_path, "w") as f:
            f.write(code)

    def handler_prompt_values(self, **kwargs) -> Mapping[str, str]:
        """Handling prompt values from memory, message' global or content
        or step content or spec parsed content
        """
        raise NotImplementedError(
            f"Prompt Manager Wrapper [{type(self).__name__}]"
            f" is missing the required `handler_prompt_values`"
            f" method.",
        )

    def handle_empty_key(self, **kwargs) -> str:
        '''return "" ''' 
        return ""
    
    def handler_input_key(self, **kwargs) -> str:
        '''return {input_template}''' 
        return self.input_template

    def handler_output_key(self, **kwargs) -> str:
        '''return {output_template}''' 
        return self.output_template
    