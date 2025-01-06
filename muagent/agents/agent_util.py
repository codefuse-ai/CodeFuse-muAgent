import re, uuid, os
from typing import (
    Union, 
    Tuple,
    List
)
from loguru import logger

from ..schemas import Memory, Message
from ..schemas.common import ActionStatus, LogVerboseEnum
from ..tools import get_tool
from ..sandbox import NBClientBox

from muagent.base_configs.env_config import KB_ROOT_PATH

class MessageUtil:
    """Utility class for processing messages and executing code or tools based on message content."""

    def __init__(
            self,
            workdir_path: str = KB_ROOT_PATH,
            log_verbose: str = "0",
            **kwargs
        ) -> None:
        """Initialize the MessageUtil with the specified working directory and log verbosity.

        Args:
            workdir_path (str): Path to the working directory where files may be saved.
            log_verbose (str): Verbosity level for logging.
            **kwargs: Additional keyword arguments for future extensions.
        """
        self.codebox = NBClientBox(do_code_exe=True)  # Initialize code execution box

        self.workdir_path = workdir_path  # Set the working directory path
        self.log_verbose = os.environ.get("log_verbose", "0") or log_verbose  # Configure logging verbosity
    
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
        code_answer = self.codebox.chat(
            '```python\n{}```'.format(msg.spec_parsed_content.get("code_content", ""))
        )

        # Prepare a response message based on code execution result
        code_prompt = (
            f"The return error after executing the above code is {code_answer.code_exe_response}，need to recover.\n" 
            if code_answer.code_exe_type == "error" else 
            f"The return information after executing the above code is {code_answer.code_exe_response}.\n"
        )
        
        # Create an observation message for logging code execution outcome
        observation_msg = Message(
            session_index=session_index,
            role_name="function",
            role_type="observation",
            content="",
            step_content="",
            input_text=msg.spec_parsed_content.get("code_content", ""),
        )

        uid = str(uuid.uuid1())  # Generate a unique identifier for related content
        if code_answer.code_exe_type == "image/png":
            # If the code execution produces an image, log the result and update the message
            msg.global_kwargs[uid] = code_answer.code_exe_response
            msg.step_content += f"\n**Observation:**: The return figure name is {uid} after executing the above code.\n"
            msg.parsed_contents.append({"Observation": f"The return figure name is {uid} after executing the above code.\n"})
            observation_msg.update_content(f"\n**Observation:**: The return figure name is {uid} after executing the above code.\n")
            observation_msg.update_parsed_content({"Observation": f"The return figure name is {uid} after executing the above code.\n"})
        else:
            # Log the standard execution result
            msg.step_content += f"\n**Observation:**: {code_prompt}\n"
            observation_msg.update_content(code_prompt)
            observation_msg.update_parsed_content({"Observation": f"{code_prompt}\n"})
        
        # Log the observations at the defined verbosity level
        if LogVerboseEnum.ge(LogVerboseEnum.Log1Level, self.log_verbose):
            logger.info(f"**Observation:** {msg.action_status}, {observation_msg.content}")
        
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
