import sys
sys.path.append('D:/CodeFuse-muAgent-main')
import random
from textwrap import dedent
import copy
from loguru import logger

from langchain.agents.tools import Tool

from muagent.connector.schema import Memory, Message, Role
from muagent.connector.utils import extract_section, parse_section, parse_section_to_dict


FORTH_TITLES = {
    "AGENT PROFILE": {
        "description": "",
        "function": "handle_empty_key",
    },
    "INFORMATION FORMAT": {
        "description": "this is information format",
        "function": "handle_empty_key",
    },
    "CONTEXT FORMAT": {
        "description": "Use the content provided in the context.",
        "function": "handle_empty_key",
    },
    "INPUT FORMAT": {
        "description": "",
        "function": "handle_empty_key",
    },
    "RESPONSE OUTPUT FORMAT": {
        "description": "",
        "function": "handle_empty_key",
    },
}

AGENT_TITLES = {
    "AGENT PROFILE": {
        "ROLE": {
            "description": "",
            "function": "handle_agent_profile",
        },
        # "TASK": {
        #     "description": "",
        #     "function": "handle_task_data",
        # },
        "TOOL INFORMATION": {
            "description": "",
            "function": "handle_tool_data",
        },
        "AGENT INFORMATION": {
            "description": "",
            "function": "handle_agent_data",
        },
        # attention 
    },
}
INFORMATION_TITLES = {
    "INFORMATION FORMAT": {
        "DOCUMENT INFORMATION": {
            "description": "this is DOCUMENT INFORMATION",
            "function": "handle_doc_info"
        },
        "CODE INFORMATION": {
            "description": "this is CODE INFORMATION",
            "function": "handle_code_info"
        },
        "SEARCH INFORMATION": {
            "description": "this is SEARCH INFORMATION",
            "function": "handle_search_info"
        },
    },
}

CONTEXT_TITLES = {
    "CONTEXT FORMAT": {
        "SESSION RECORDS": {
            "description": "this is SESSION RECORDS",
            "function": "handle_session_records"
        },
    }
}

# can update
ACTION_TITLES = {}




class PromptManager:
    
    def __init__(self, role: Role, role_prompt="", prompt_config=None, monitored_agents=[], monitored_fields=[]):
        self.role: Role = role
        self.role_prompt = role_prompt
        self.monitored_agents = monitored_agents
        self.monitored_fields = monitored_fields
        self.field_handlers = {}
        self.context_handlers = {}
        self.field_order = []  # 用于普通字段的顺序
        self.context_order = []  # 单独维护上下文字段的顺序
        self.field_descriptions = {}
        self.omit_if_empty_flags = {}
        self.context_title = "### Context Data\n\n"  
        
        self.prompt_config = prompt_config
        if self.prompt_config:
            self.register_fields_from_config()

        self.register_prompt_config()
    
    def register_prompt_config(self, ):
        '''
        '''
        # base titles
        self.agent_titles = AGENT_TITLES
        self.forth_titles = FORTH_TITLES
        self.information_titles = INFORMATION_TITLES
        self.context_titles = CONTEXT_TITLES
        # 
        self.title_levels = {
            "TASK RECORDS": self.role.task_context_level,
            "REACT RECORDS": self.role.react_context_level,
            "SESSION RECORDS": self.role.session_context_level,
            "CONTEXT FORMAT": max(self.role.task_context_level, self.role.react_context_level, self.role.session_context_level),
            "DOCUMENT INFORMATION": self.role.doc_doc_level,
            "CODE INFORMATION": self.role.code_doc_level,
            "SEARCH INFORMATION": self.role.search_doc_level,
            "INFORMATION FORMAT": max(self.role.doc_doc_level, self.role.code_doc_level, self.role.search_doc_level),
            "AGENT INFORMATION": self.role.agent_level,
            "TOOL INFORMATION": self.role.tool_level,
            "INPUT FORMAT": 1,
            "RESPONSE OUTPUT FORMAT": 1,
        }

        # according input and output to update
        self.star_output_titles = {}
        self.star_input_titles = {}

        input_values = {}
        output_str = extract_section(
            self.role.output_template.replace("Response Output Format", 'RESPONSE OUTPUT FORMAT'), 
            'RESPONSE OUTPUT FORMAT')
        
        if self.role.prompt:
            output_str = extract_section(
                self.role.prompt.replace("Response Output Format", 'RESPONSE OUTPUT FORMAT'), 
                'RESPONSE OUTPUT FORMAT')
            input_values = parse_section_to_dict(
                self.role.prompt.replace("Input Format", 'INPUT FORMAT'), 'INPUT FORMAT')
            self.role_prompt = extract_section(
                self.role.prompt.replace("Agent Profile", 'AGENT PROFILE'), 'AGENT PROFILE')

        if output_str:
            self.star_output_titles.update({
                "RESPONSE OUTPUT FORMAT": {
                    "": {"description": output_str, "function": "handle_response"} 
                }
            })
        if input_values:
            self.star_input_titles.update({
                "INPUT FORMAT": {
                    k: {"description": v, "function": "handle_custom_data"} 
                    for k,v in input_values.items()
                }
            })

    def register_field(self, field_name, function=None, title=None, description=None, is_context=True, omit_if_empty=True):
        """
        注册一个新的字段及其处理函数。
        Args:
            field_name (str): 字段名称。
            function (callable): 处理字段数据的函数。
            title (str, optional): 字段的自定义标题（可选）。
            description (str, optional): 字段的描述（可选，可以是几句话）。
            is_context (bool, optional): 指示该字段是否为上下文字段。
            omit_if_empty (bool, optional): 如果数据为空，是否省略该字段。
        """
        if not function:
            function = self.handle_custom_data
        
        # Register the handler function based on context flag
        if is_context:
            self.context_handlers[field_name] = function
        else:
            self.field_handlers[field_name] = function
        
        # Store the custom title if provided and adjust the title prefix based on context
        title_prefix = "####" if is_context else "###"
        if title is not None:
            self.field_descriptions[field_name] = f"{title_prefix} {title}\n\n"
        elif description is not None:
            # If title is not provided but description is, use description as title
            self.field_descriptions[field_name] = f"{title_prefix} {field_name.replace('_', ' ').title()}\n\n{description}\n\n"
        else:
            # If neither title nor description is provided, use the field name as title
            self.field_descriptions[field_name] = f"{title_prefix} {field_name.replace('_', ' ').title()}\n\n"
            
        # Store the omit_if_empty flag for this field
        self.omit_if_empty_flags[field_name] = omit_if_empty
        
        if is_context and field_name != 'context_placeholder':
            self.context_handlers[field_name] = function
            self.context_order.append(field_name)
        else:
            self.field_handlers[field_name] = function
            self.field_order.append(field_name)
    
    def generate_full_prompt(self, **kwargs):
        full_prompt = []
        context_prompts = []  # 用于收集上下文内容
        is_pre_print = kwargs.get("is_pre_print", False) # 用于强制打印所有prompt 字段信息，不管有没有空

        # update all title's description and function_value
        title_values = {}
        for forth_title, forth_value in self.forth_titles.items():
            handler = getattr(self, forth_value["function"])
            kwargs.update({"title_key": forth_title})
            function_value = handler(**kwargs)
            title_values[forth_title] = {
                "description": forth_value["description"],
                "function_value": function_value,
                "agent_values": [],
                "context_values": [],
                "info_values": [],
                "star_output_values": [],
                "star_input_values": []
            }
            # 
            key_titles = {
                 "agent_values": self.agent_titles,
                 "info_values": self.information_titles,
                 "context_values": self.context_titles,
                 "star_output_values": self.star_output_titles,
                 "star_input_values": self.star_input_titles,
            }
            for key, titles in key_titles.items():
                # logger.debug(f"{forth_title}, {titles.get(forth_title)}")
                for title, value in titles.get(forth_title, {}).items():
                    handler = getattr(self, value["function"])
                    kwargs.update({"title_key": title})
                    function_value = handler(**kwargs)
                    title_values[forth_title][key].append({
                        "description": value['description'],
                        "function_value": function_value,
                        "title": title
                        })

        # logger.debug(f"{title_values}")
        prompt_values = []
        prompt_values = self._process_title_values(title_values, prompt_values, 
                                                   title_type="description", is_pre_print=is_pre_print)
        prompt_values.append("## BEGIN!!!")
        prompt_values = self._process_title_values(title_values, prompt_values, 
                                                   title_type="function_value", is_pre_print=is_pre_print)

        # logger.debug(prompt_values)
        if not any([i=="#### RESPONSE OUTPUT" for i in prompt_values]):
            prompt_values.append("#### RESPONSE OUTPUT")
        # 返回完整的提示，移除尾部的空行
        return '\n'.join(prompt_values).rstrip('\n')

    def _process_title_values(self, title_values, prompt_values, title_type="description", is_pre_print=False):
        '''process title values to prompt'''
        response_omit_flag = False
        key_placeholder = {}
        for forth_title in title_values.keys():
            forth_title_value = title_values[forth_title]
            func_values = {k: [i["function_value"] for i in forth_title_value[k]] 
                           for k in ['agent_values', 'info_values', 'context_values', 'star_output_values', 'star_input_values'] }
            
            star_values = {k: forth_title_value[k] for k in ['star_output_values', 'star_input_values'] }
            
            if forth_title in ["RESPONSE OUTPUT FORMAT", "INPUT FORMAT"] and title_type == "description" and any([len(v) for _, v in star_values.items()]):
                pass
            elif not (forth_title_value['function_value'] or any([any(v) for _, v in func_values.items()]) ):
                if forth_title == "RESPONSE OUTPUT FORMAT" and title_type=="description":
                    response_omit_flag = True
                    prompt_values.append("RESPONSE_placeholder")
                continue
            
            if title_type == "function_value" and forth_title in ["AGENT PROFILE"]:
                continue
            # #### title
            if title_type == "description":
                prompt_values.append(f"#### {forth_title}\n{forth_title_value['description'] or forth_title_value['function_value'] }")
            elif title_type == "function_value" and forth_title not in ["AGENT PROFILE", "AGENT INFORMATION", "TOOL INFORMATION"]:
                prompt_values.append(f"#### {forth_title.replace(' FORMAT', '')}\n{ forth_title_value['function_value'] }")

            # ### title
            for key in ['agent_values', 'info_values', 'context_values', 'star_output_values', 'star_input_values']:
                values = forth_title_value[key]
                str_template = '### {}\n{}' if key not in ['star_output_values', 'star_input_values'] else "**{}:** {}"

                for value in values:
                    title = value["title"]
                    
                    title_level = self.title_levels.get(title, 1)
                    if title_level == 0: continue # level==0, don't output this title
                    
                    if (value['function_value'] and title_type == "description") or (title_level==2 or is_pre_print):
                        prompt_values.append(str_template.format(title, value['description'] or value['function_value']).replace("**:**", ""))
                        key_placeholder.setdefault(key, []).append(title)
                    elif (forth_title in ["RESPONSE OUTPUT FORMAT", "INPUT FORMAT"] and title_type == "description") or (title_level==2 or is_pre_print):
                        prompt_values.append(str_template.format(title, value['description']).replace("**:**", ""))
                    elif (value['function_value'] and title_type == "function_value") or (title_level==2 or is_pre_print):
                        prompt_values.append(str_template.format(title.replace(" FORMAT", ""), value['function_value']).replace("**:**", ""))
                
            if title_type == "description":
                prompt_values.append(f"{forth_title}_placeholder")

        # logger.debug(f"{prompt_values}")
        # customized
        for key in title_values.keys():
            key_extra_prompt = ""
            if key == "AGENT PROFILE":
                key_extra_prompt = self._create_attention_prompt(key_placeholder)
            
            prompt_values = [
                pv.replace(f"{key}_placeholder", key_extra_prompt)
                for pv in prompt_values
            ]

        if response_omit_flag:
            key_extra_prompt = self._create_attention_prompt(key_placeholder)
            prompt_values = [
                pv.replace("RESPONSE_placeholder", "### RESPONSE OUTPUT FORMAT\n**response:** {}".format(key_extra_prompt.split("\n")[1]))
                for pv in prompt_values
            ]

        return prompt_values

    def _create_attention_prompt(self, key_placeholder):
        key_extra_prompt = ""
        agent_titles = key_placeholder.get("agent_values", [])
        info_titles = key_placeholder.get("info_values", [])
        context_titles = key_placeholder.get("context_values", [])

        if info_titles and context_titles:
            key_extra_prompt += f"Refer to {'&'.join(info_titles)} and incorporate the context of the {'&'.join(context_titles)}, "
        elif info_titles:
            key_extra_prompt += f"Refer to {'&'.join(info_titles)}, "
        elif context_titles:
            key_extra_prompt += f"Incorporate the context of the {'&'.join(context_titles)}, "
        
        if "TASK" in agent_titles:
            key_extra_prompt += "complete the task specified above efficiently.\n"
        else:
            key_extra_prompt += "answer question concisely and professionally.\n"
        
        key_extra_prompt += "response carefully referenced in 'Response Output Format'.\n"
        key_extra_prompt = "### ATTENTION\n" + key_extra_prompt
        return key_extra_prompt


    def pre_print(self, **kwargs):
        kwargs.update({"is_pre_print": True})
        prompt = self.generate_full_prompt(**kwargs)

        input_keys = parse_section(self.role_prompt, 'Response Output Format')
        llm_predict = "\n".join([f"**{k}:**" for k in input_keys])
        return prompt + "\n\n" + "#"*19 + "\n<<<<LLM PREDICT>>>>\n" + "#"*19  + f"\n\n{llm_predict}\n"

    def handle_custom_data(self, **kwargs):
        '''get key-value from parsed_output_list or customed_kargs'''
        key: str = kwargs.get("title_key", "")
        previous_agent_message: Message = kwargs.get('previous_agent_message')

        keys = [
            "_".join([i.title() for i in key.split(" ")]),
            " ".join([i.title() for i in key.split("_")]), 
            key
        ]
        keys = list(set(keys))

        content = ""
        for key in keys:
            if key in previous_agent_message.spec_parsed_output:
                content = previous_agent_message.spec_parsed_output.get(key)
                content = "\n".join(content) if isinstance(content, list) else content
                break
            if key in previous_agent_message.customed_kargs:
                content = previous_agent_message.customed_kargs.get(key)
                content = "\n".join(content) if isinstance(content, list) else content
                break

        return content
    
    def handle_tool_data(self, **kwargs):
        if 'previous_agent_message' not in kwargs:
            return ""

        previous_agent_message = kwargs.get('previous_agent_message')
        tools: list[Tool] = previous_agent_message.tools
        
        if not tools:
            return ""
        
        tool_strings = []
        for tool in tools:
            args_str = f'args: {str(tool.args)}' if tool.args_schema else ""
            tool_strings.append(f"{tool.name}: {tool.description}, {args_str}")
        formatted_tools = "\n".join(tool_strings)
        
        tool_names = ", ".join([tool.name for tool in tools])
        
        tool_prompt = dedent(f"""
                Below is a list of tools that are available for your use:
                {formatted_tools}

                valid "tool_name" value is:
                {tool_names}
                """)
        while "\n " in tool_prompt:
            tool_prompt = tool_prompt.replace("\n ", "\n")
                        
        return tool_prompt

    def handle_agent_data(self, **kwargs):
        if 'agents' not in kwargs:
            return ""
        
        agents = kwargs.get('agents')
        random.shuffle(agents)
        agent_names = ", ".join([f'{agent.role.role_name}' for agent in agents])
        agent_descs = []
        for agent in agents:
            # role_desc = agent.role.role_prompt.split("####")[1]
            role_desc = self.role_prompt
            while "\n\n" in role_desc:
                role_desc = role_desc.replace("\n\n", "\n")
            role_desc = role_desc.replace("\n", ",")

            agent_descs.append(f'"role name: {agent.role.role_name}\nrole description: {role_desc}"')

        agents =  "\n".join(agent_descs)
        agent_prompt = f'''
        Please ensure your selection is one of the listed roles. Available roles for selection:
        {agents}
        Please ensure select the Role from agent names, such as {agent_names}'''

        while "\n " in agent_prompt:
            agent_prompt = agent_prompt.replace("\n ", "\n")

        return agent_prompt
    
    def handle_doc_info(self, **kwargs) -> str:
        if 'previous_agent_message' not in kwargs:
            return ""
        previous_agent_message: Message = kwargs.get('previous_agent_message')
        db_docs = previous_agent_message.db_docs
        doc_infos = "\n".join([doc.get_snippet() for doc in db_docs])
        return doc_infos
    
    def handle_search_info(self, **kwargs) -> str:
        if 'previous_agent_message' not in kwargs:
            return ""
        previous_agent_message: Message = kwargs.get('previous_agent_message')
        search_docs = previous_agent_message.search_docs
        doc_infos = "\n".join([doc.get_snippet() for doc in search_docs])
        return doc_infos

    def handle_code_info(self, **kwargs) -> str:
        if 'previous_agent_message' not in kwargs:
            return ""
        previous_agent_message: Message = kwargs.get('previous_agent_message')
        code_cocs = previous_agent_message.code_docs
        doc_infos = "\n".join([doc.get_code() for doc in code_cocs])
        return doc_infos
    
    def handle_session_records(self, **kwargs) -> str:

        memory_pool: Memory = kwargs.get('memory_pool', Memory(messages=[]))
        memory_pool = self.select_memory_by_agent_name(memory_pool)
        memory_pool = self.select_memory_by_parsed_key(memory_pool)

        return memory_pool.to_str_messages(content_key="parsed_output_list", with_tag=True)
    
    def handle_current_plan(self, **kwargs) -> str:
        if 'previous_agent_message' not in kwargs:
            return ""
        previous_agent_message = kwargs['previous_agent_message']
        return previous_agent_message.parsed_output.get("CURRENT_STEP", "")
    
    def handle_agent_profile(self, **kwargs) -> str:
        return extract_section(self.role_prompt, 'AGENT PROFILE') or self.role_prompt
    
    def handle_output_format(self, **kwargs) -> str:
        return extract_section(self.role_prompt, 'Response Output Format')
    
    def handle_response(self, **kwargs) -> str:
        if 'react_memory' not in kwargs:
            return ""

        react_memory = kwargs.get('react_memory', Memory(messages=[]))
        if react_memory is None:
            return ""

        return "\n".join(["\n".join([f"**{k}:**\n{v}" for k,v in _dict.items()]) for _dict in react_memory.get_parserd_output()])

    def handle_task_records(self, **kwargs) -> str:
        if 'task_memory' not in kwargs:
            return ""

        task_memory: Memory = kwargs.get('task_memory', Memory(messages=[]))
        if task_memory is None:
            return ""
        
        return "\n".join(["\n".join([f"**{k}:**\n{v}" for k,v in _dict.items() if k not in ["CURRENT_STEP"]]) for _dict in task_memory.get_parserd_output()])
    
    def handle_empty_key(self, **kwargs) -> str:
        return ""

    def handle_previous_message(self, message: Message) -> str: 
        pass
    
    def handle_message_by_role_name(self, message: Message) -> str: 
        pass
    
    def handle_message_by_role_type(self, message: Message) -> str:
        pass
    
    def handle_current_agent_react_message(self, message: Message) -> str:
        pass
    
    def extract_codedoc_info_for_prompt(self, message: Message) -> str: 
        code_docs = message.code_docs
        doc_infos = "\n".join([doc.get_code() for doc in code_docs])
        return doc_infos
    
    def select_memory_by_parsed_key(self, memory: Memory) -> Memory:
        return Memory(
            messages=[self.select_message_by_parsed_key(message) for message in memory.messages 
                      if self.select_message_by_parsed_key(message) is not None]
                      )

    def select_memory_by_agent_name(self, memory: Memory) -> Memory:
        return Memory(
            messages=[self.select_message_by_agent_name(message) for message in memory.messages 
                      if self.select_message_by_agent_name(message) is not None]
                      )

    def select_message_by_agent_name(self, message: Message) -> Message:
        # assume we focus all agents
        if self.monitored_agents == []:
            return message
        return None if message is None or message.role_name not in self.monitored_agents else self.select_message_by_parsed_key(message)
    
    def select_message_by_parsed_key(self, message: Message) -> Message:
        # assume we focus all key contents
        if message is None:
            return message
        
        if self.monitored_fields == []:
            return message
        
        message_c = copy.deepcopy(message)
        message_c.parsed_output = {k: v for k,v in message_c.parsed_output.items() if k in self.monitored_fields}
        message_c.parsed_output_list = [{k: v for k,v in parsed_output.items() if k in self.monitored_fields} for parsed_output in message_c.parsed_output_list]
        return message_c
    
    def get_memory(self, content_key="role_content"):
        return self.memory.to_tuple_messages(content_key="step_content")
    
    def get_memory_str(self, content_key="role_content"):
        return "\n".join([": ".join(i) for i in self.memory.to_tuple_messages(content_key="step_content")])
    
    def register_fields_from_config(self):
        
        for prompt_field in self.prompt_config:
            
            function_name = prompt_field.function_name
            # 检查function_name是否是self的一个方法
            if function_name and hasattr(self, function_name):
                function = getattr(self, function_name)
            else:
                function = self.handle_custom_data
                
            self.register_field(prompt_field.field_name, 
                                function=function, 
                                title=prompt_field.title,
                                description=prompt_field.description,
                                is_context=prompt_field.is_context,
                                omit_if_empty=prompt_field.omit_if_empty)
    
    def register_standard_fields(self):
        self.register_field('agent_profile', function=self.handle_agent_profile, is_context=False)
        self.register_field('tool_information', function=self.handle_tool_data, is_context=False)
        self.register_field('context_placeholder', is_context=True)  # 用于标记上下文数据部分的位置
        self.register_field('reference_documents', function=self.handle_doc_info, is_context=True)
        self.register_field('session_records', function=self.handle_session_records, is_context=True)
        self.register_field('output_format', function=self.handle_output_format, title='Response Output Format', is_context=False)
        self.register_field('response', function=self.handle_response, is_context=False, omit_if_empty=False)
        
    def register_executor_fields(self):
        self.register_field('agent_profile', function=self.handle_agent_profile, is_context=False)
        self.register_field('tool_information', function=self.handle_tool_data, is_context=False)
        self.register_field('context_placeholder', is_context=True)  # 用于标记上下文数据部分的位置
        self.register_field('reference_documents', function=self.handle_doc_info, is_context=True)
        self.register_field('session_records', function=self.handle_session_records, is_context=True)
        self.register_field('current_plan', function=self.handle_current_plan, is_context=True)
        self.register_field('output_format', function=self.handle_output_format, title='Response Output Format', is_context=False)
        self.register_field('response', function=self.handle_response, is_context=False, omit_if_empty=False)
        
    def register_fields_from_dict(self, fields_dict):
        # 使用字典注册字段的函数
        for field_name, field_config in fields_dict.items():
            function_name = field_config.get('function', None)
            title = field_config.get('title', None)
            description = field_config.get('description', None)
            is_context = field_config.get('is_context', True)
            omit_if_empty = field_config.get('omit_if_empty', True)
            
            # 检查function_name是否是self的一个方法
            if function_name and hasattr(self, function_name):
                function = getattr(self, function_name)
            else:
                function = self.handle_custom_data
            
            # 调用已存在的register_field方法注册字段
            self.register_field(field_name, function=function, title=title, description=description, is_context=is_context, omit_if_empty=omit_if_empty)



def main():
    manager = PromptManager()
    manager.register_standard_fields()

    manager.register_field('agents_work_progress', title=f"Agents' Work Progress", is_context=True)

    # 创建数据字典
    data_dict = {
        "agent_profile": "这是代理配置文件...",
        # "tool_list": "这是工具列表...",
        "reference_documents": "这是参考文档...",
        "session_records": "这是会话记录...",
        "agents_work_progress": "这是代理工作进展...",
        "output_format": "这是预期的输出格式...",
        # "response": "这是生成或继续回应的指令...",
        "response": "",
        "test": 'xxxxx'
        }

    # 组合完整的提示
    full_prompt = manager.generate_full_prompt(data_dict)
    print(full_prompt)

if __name__ == "__main__":
    main()