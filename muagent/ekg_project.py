from typing import (
    Union,
    Sequence,
    Literal,
    Mapping,
    Optional,
    Dict,
    List
)
from pydantic import BaseModel
import os
import json
from loguru import logger
import concurrent.futures
import time
import random

os.environ["operation_mode"] = "open_source"
os.environ["intention_url"] = ""

from .llm_models import LLMConfig, EmbedConfig
from .schemas.db import TBConfig, GBConfig
from .schemas.models import ModelConfig
from .schemas import EKGProjectConfig, Message, Memory, AgentConfig, PromptConfig
from .schemas.common import GNode, GEdge
from .db_handler import *
from .agents import FunctioncallAgent

from .service.utils import decode_biznodes, encode_biznodes

# from .connector.schema import Memory, Message
from .connector.memory_manager import TbaseMemoryManager
from .service.ekg_construct.ekg_construct_base import EKGConstructService
from .service.ekg_inference import IntentionRouter
from .service.ekg_reasoning.src.graph_search.graph_search_main import main as reasoning


class LingSiResponse(BaseModel):
    '''lingsi的输出值， 算法的输入值
    The following is an example:

    .. code-block:: python

        from xx import LingSiResponse
        ls_resp = LingSiResponse(
            observation={'content': '一起来玩谁是卧底'},
            sessionId='default_sessionId',
            scene="UNDERCOVER",
        )

        ls_resp = LingSiResponse(
            observation={'toolResponse': '我的单词是一种工业品'},
            currentNodeId='剧本杀/谁是卧底/智能交互/开始新一轮的讨论'
            sessionId='default_sessionId',
            scene="UNDERCOVER",
            type='reactExecution'
        )
    '''
    sessionId: str
    """The session index"""

    currentNodeId: Optional[str] = None
    """The last node index, the first is null"""

    type: Optional[str] = None
    """The last execute type, the first is null"""

    agentName:Optional[str]=None
    """The agent name from last node output, the first is null"""

    scene: Literal["UNDERCOVER", "WEREWOLF" , "NEXA" ] = "NEXA"
    """The scene type of this task."""

    observation: Optional[Union[str,Dict]] # jsonstr
    '''last observation from last node
    .. code-block:: python
        observation: Literal["content", "tool_response"]
    '''

    userAnswer: Optional[str]=None
    """no use"""

    startRootNodeId: Optional[str] = ''
    """The default team root id"""

    intentionData: Optional[Union[List,str] ] = None
    """equal query, only once at first"""

    startFromRoot: Literal['True', 'false', 'true', 'False'] = 'True'
    """"""

    intentionRule: Optional[Union[List,str]]= ["nlp"]
    """no use"""


class QuestionContent(BaseModel):
    '''
        {'question': '请玩家根据当前情况发言',     'candidate': None }
    '''
    question:str
    candidate:Optional[str]=None
    
class QuestionDescription(BaseModel):
    '''
        {'questionType': 'essayQuestion',
        'questionContent': {'question': '请玩家根据当前情况发言','candidate': None }}
    '''
    questionType: Literal["essayQuestion", "multipleChoice"] = "essayQuestion"
    questionContent: QuestionContent 

class ToolPlanOneStep(BaseModel):
    '''
            tool_plan_one_step =  {'toolDescription': '请用户回答',
            'currentNodeId': nodeId,
            'memory': None,
            'type': 'userProblem',
            'questionDescription': {'questionType': 'essayQuestion',
            'questionContent': {'question': '请玩家根据当前情况发言',
            'candidate': None }}} 
    '''
    currentNodeId: Optional[str] = None
    """from last node index"""

    toolDescription:str 
    """the input for functioncalling"""

    currentNodeInfo: Optional[str] = None
    """equal agent name"""

    memory: Optional[str] = None
    """memory"""

    questionDescription: Optional[QuestionDescription]=None
    """反问的过程"""

    type: Optional[Literal["onlyTool", "userProblem", "reactExecution"]] = None
    """request type"""


class ResToLingsi(BaseModel):
    '''lingsi的输入值， 算法的输出值
    The following is an example:

    .. code-block:: python

        from xx import ResToLingsi
        resp_to_ls = ResToLingsi(
            sessionId = "default_sessionId",
            type="onlyTool",
            summary=None,
            toolPlan=ToolPlan(
                toolDescription="agent_李静",
                currentNodeId='26921eb05153216c5a1f585f9d318c77%%@@#agent_李静',
                currentNodeInfo='agent_李静',
                memory="",
                questionDescription=None,
                type="reactExecution"
            userInteraction='开始新一轮的讨论<br><br>**主持人:**  <br>各位玩家请注意，现在所有玩家均存活，我们将按照座位顺序进行发言。发言顺序为1号李静、2号张伟、3号人类玩家、4号王鹏。现在，请1号李静开始发言。'
            intentionRecognitionSituation=None,
        )
    '''
    sessionId: str
    """session index from last node output"""

    toolPlan:Optional[List[ToolPlanOneStep]] = None
    """"""

    userInteraction:Optional[str]=None
    """if userInteraction, yield"""

    summary: Optional[str] = None
    """if summary, end, yield"""

    type: Optional[str] = None
    """no use"""

    intentionRecognitionSituation: Optional[str]=None
    """no use"""


def get_ekg_project_config_from_env(
    model_configs: Optional[Dict[str, Union[LLMConfig, ModelConfig]]] = None,
    embed_configs: Optional[Dict[str, Union[EmbedConfig, ModelConfig]]] = None,
    db_configs: Optional[Mapping[str, Union[GBConfig, TBConfig]]] = None,
    agent_configs: Optional[Mapping[str, AgentConfig]] = None,
    prompt_configs: Optional[Mapping[str,PromptConfig]] = None,
) -> EKGProjectConfig:
    """"""
    project_configs = {
        "model_configs": {},
        "embed_configs": {},
        "db_configs": {},
        "agent_configs": {},
        "prompt_configs": {},
    }
    #
    db_config_name_to_class = {
        "gb_config": GBConfig,
        "tb_config": TBConfig,   
    }
    # init model configs
    if model_configs:
        for k, v in model_configs.items():
            if isinstance(v, LLMConfig) or isinstance(v, ModelConfig):
                project_configs["model_configs"][k] = v
            else:
                try:
                    project_configs["model_configs"][k] = ModelConfig(**v)
                except:
                    project_configs["model_configs"][k] = LLMConfig(**v)
    elif "model_configs".upper() in os.environ:
        _model_configs = json.loads(os.environ["model_configs".upper()])
        for k, v in _model_configs.items():
            try:
                project_configs["model_configs"][k] = ModelConfig(**v)
            except:
                project_configs["model_configs"][k] = LLMConfig(**v)

    chat_list = [_type for _type in project_configs["model_configs"].keys() if "chat" in _type]
    embedding_list = [_type for _type in project_configs["model_configs"].keys() if "embedding" in _type]
    if chat_list:
        model_type = random.choice(chat_list)
        default_model_config = project_configs["model_configs"][model_type]
        project_configs["model_configs"]["default_chat"] = default_model_config
        os.environ["DEFAULT_MODEL_TYPE"] = model_type
        os.environ["DEFAULT_MODEL_NAME"] = default_model_config.model_name
        os.environ["DEFAULT_API_KEY"] = default_model_config.api_key or ""
        os.environ["DEFAULT_API_URL"] = default_model_config.api_url or ""

    if embedding_list:
        model_type = random.choice(embedding_list)
        default_model_config = project_configs["model_configs"][model_type]
        project_configs["model_configs"]["default_embed"] = default_model_config

    # init embedding configs
    if embed_configs:
        for k, v in embed_configs.items():
            if isinstance(v, EmbedConfig) or isinstance(v, ModelConfig):
                project_configs["embed_configs"][k] = v
            else:
                try:
                    project_configs["embed_configs"][k] = EmbedConfig(**v)
                except:
                    project_configs["embed_configs"][k] = ModelConfig(**v)
    elif "embed_configs".upper() in os.environ:
        embed_configs = json.loads(os.environ["embed_configs".upper()])
        for k, v in embed_configs.items():
            if isinstance(v, EmbedConfig) or isinstance(v, ModelConfig):
                project_configs["embed_configs"][k] = v
            else:
                try:
                    project_configs["embed_configs"][k] = EmbedConfig(**v)
                except:
                    project_configs["embed_configs"][k] = ModelConfig(**v)

    # init db configs
    db_configs = db_configs or json.loads(os.environ["DB_CONFIGS"])
    for k in ["tb_config", "gb_config"]:
        if db_configs and k not in db_configs:
            raise KeyError(
                f"EKG must have {k}. "
                f"please check your env config or input."
            )
        else:
            project_configs["db_configs"][k] = db_config_name_to_class[k](
                **db_configs[k])

    # init agent configs
    if "AGENT_CONFIGS" in os.environ:
        agent_configs = agent_configs or json.loads(os.environ["AGENT_CONFIGS"])
        agent_configs = {
            kk: AgentConfig(**vv)
            for kk, vv in agent_configs.items()
        }
        project_configs["agent_configs"] = agent_configs
    else:
        logger.warning(
            f"Cant't init any AGENT_CONFIGS in this env."
        ) 

    # init prompt configs
    if "PROMPT_CONFIGS" in os.environ:
        prompt_configs = prompt_configs or json.loads(os.environ["PROMPT_CONFIGS"])
        prompt_configs = {
            kk: PromptConfig(**vv)
            for kk, vv in prompt_configs.items()
        }
        project_configs["prompt_configs"] = prompt_configs
    else:
        logger.warning(
            f"Cant't init any PROMPT_CONFIGS in this env."
        ) 
        

    return EKGProjectConfig(**project_configs)
    

class EKG:
    """Class to represent and manage the EKG project."""
    
    def __init__(
            self,
            tb_config: Optional[TBConfig] = None,
            gb_config: Optional[GBConfig] = None, 
            embed_config: Union[ModelConfig, EmbedConfig] = None,
            llm_config: Union[ModelConfig, LLMConfig] = None,
            project_config: EKGProjectConfig = None,
            agents: List[str] = [],
            tools: List[str] = [],
            *,
            initialize_space = True
        ):

        # Initialize various configuration settings for the EKG project.
        self.tb_config = tb_config
        self.gb_config = gb_config
        self.embed_config = embed_config
        self.llm_config = llm_config
        self.project_config = project_config
        self.agents = agents
        self.tools = tools

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.futures = []
        # Set whether to initialize space
        self.initialize_space = initialize_space
        self.init_from_project()

    @classmethod
    def from_project(cls, project_config: EKGProjectConfig, initialize_space=False) -> 'EKG':
        """Create an instance of EKG from a project configuration."""
        return cls(project_config=project_config, initialize_space=initialize_space)

    def init_from_project(self):
        """Initialize settings from the provided project configuration."""

        # Setup the time-based configuration
        if self.project_config and self.project_config.db_configs:
            self.tb_config = self.tb_config or \
                    self.project_config.db_configs.get("tb_config")
        elif self.tb_config:
            pass
        else:
            raise KeyError(
                    f"EKG Project must have 'tb_config' in "
                    f"db_configs"
                )
        
        # Setup the graph-based configuration
        if self.project_config and self.project_config.db_configs:
            self.gb_config = self.gb_config or \
                    self.project_config.db_configs.get("gb_config")
        elif self.gb_config:
            pass
        else:
            raise KeyError(
                    f"EKG Project must have 'gb_config' in "
                    f"db_configs"
                )
        
        # Setup embedding configuration
        if self.project_config and self.project_config.embed_configs:
            if "default" not in self.project_config.embed_configs:
                raise KeyError(
                    f"EKG Project must have key=default in "
                    f"embed_configs"
                )
            self.embed_config = self.project_config.embed_configs.get("default")

        # Setup LLM configuration and environment variables
        if self.project_config and self.project_config.model_configs:
            # if "default_chat" not in self.project_config.llm_configs:
            #     raise KeyError(
            #         f"EKG Project must have key=default in "
            #         f"llm_configs"
            #     )

            # os.environ["API_BASE_URL"] = self.project_config.llm_configs["default"].api_base_url
            # os.environ["OPENAI_API_KEY"] = self.project_config.llm_configs["default"].api_key
            # os.environ["model_name"] = self.project_config.llm_configs["default"].model_name
            # os.environ["model_engine"] = self.project_config.llm_configs["default"].model_engine
            # os.environ["llm_temperature"] = self.project_config.llm_configs["default"].temperature
            self.llm_config = self.project_config.model_configs.get("default_chat")
            self.llm_config = LLMConfig(
                model_name=os.environ["model_name"],
                model_engine=os.environ["model_engine"],
                api_key=os.environ["OPENAI_API_KEY"],
                api_base_url=os.environ["API_BASE_URL"],
            )

            # Ensure 'codefuser' config exists
            if "codefuser" not in self.project_config.model_configs:
                raise KeyError(
                    f"EKG Project must have key=codefuser in "
                    f"llm_configs"
                )

            os.environ["gpt4-API_BASE_URL"] = self.project_config.model_configs["codefuser"].api_base_url
            os.environ["gpt4-OPENAI_API_KEY"] = self.project_config.model_configs["codefuser"].api_key
            os.environ["gpt4-model_name"] = self.project_config.model_configs["codefuser"].model_name
            os.environ["gpt4-model_engine"] = self.project_config.model_configs["codefuser"].model_engine
            os.environ["gpt4-llm_temperature"] = self.project_config.model_configs["codefuser"].temperature

        self._init_ekg_construt_service()  # Initialize the EKG construction service
        self._init_memory_manager()  # Initialize the memory manager
        self._init_intention_router()  # Initialize the intention router

    def _init_ekg_construt_service(self):
        """Initialize the service responsible for building the EKG graph."""
        self.ekg_construct_service = EKGConstructService(
            embed_config=self.embed_config,
            llm_config=self.llm_config,
            tb_config=self.tb_config,
            gb_config=self.gb_config,
            initialize_space=self.initialize_space
        )

    def _init_memory_manager(self):
        """Initialize the memory manager with the appropriate configuration."""
        tb = TbaseHandler(
            self.tb_config, 
            self.tb_config.index_name, 
            definition_value=self.tb_config.extra_kwargs.get(
                "memory_definition_value")
        )

        self.memory_manager = TbaseMemoryManager(
            unique_name="EKG", 
            embed_config=self.embed_config, 
            llm_config=self.llm_config,
            tbase_handler=tb,  # Use the Tbase handler for database management
            use_vector=False
        )

    def _init_intention_router(self):
        """Initialize the routing mechanism for intentions within the EKG project."""
        self.intention_router = IntentionRouter(
            self.ekg_construct_service.model,
            self.ekg_construct_service.gb,
            self.ekg_construct_service.tb,
            self.embed_config
        )

    def __call__(self):
        """Call method for EKG class instance (to be implemented)."""
        pass

    def add_node(
            self,
            node: Union[Dict, GNode],
            *,
            teamid: str = "default",
        ) -> None:
        """Add a node to the EKG graph."""
        gnode = GNode(**node) if isinstance(node, Dict) else node
        gnodes, _ = decode_biznodes([gnode])  # Decode the business nodes
        self.ekg_construct_service.add_nodes(gnodes, teamid)  # Add nodes to the construct service

    def add_edge(
            self,
            start_id: str,
            end_id: str,
            *,
            teamid: str = "",
        ) -> None:
        """Add an edge between two nodes in the EKG graph."""
        start_node = self.ekg_construct_service.get_node_by_id(start_id)
        end_node = self.ekg_construct_service.get_node_by_id(end_id)

        # If both start and end nodes exist, create an edge
        if start_node and end_node:
            edge = {
                "start_id": start_id, 
                "end_id": end_id, 
                "type": f"{start_node.type}_route_{end_node.type}",
                "attributes": {}
            }
            edges = [GEdge(**edge)]  # Create an edge object
            self.ekg_construct_service.add_edges(edges, teamid)  # Add edges to the construct service

    def run(
            self,
            query: str,
            scene: str = "NEXA",
            rootid: str = "ekg_team_default",
        ):
        """Run the EKG processing with the provided query and scene."""
        import uuid
        sessionId = str(uuid.uuid4()).replace("-", "")  # Generate a unique session ID
        request = LingSiResponse(
                observation={"content": query},
                intentionData=query,
                startRootNodeId=rootid,
                sessionId=sessionId,
                scene=scene,
            )
        logger.error(query)

        summary = ""  # Initialize summary variable
        history_done = []
        while True:
            # Wait for the first completed future object
            done, not_done = concurrent.futures.wait(
                self.futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            history_done.extend(done)
            for future in done:
                self.futures.remove(future)

            if history_done:
            # for future in done:
                future = history_done.pop(0)
                try:
                    result = future.result()  # Retrieve the result of the completed task
                    # logger.error(f"Task completed: {result}")
                    # self.futures.remove(future)  # Remove completed task from the futures list
                            
                    # Assemble the new request with the result data
                    request = LingSiResponse(
                        observation={"toolResponse": result.get("toolResponse")},
                        currentNodeId=result.get("currentNodeId"),
                        type=result.get("type"),
                        agentName=result.get("agentName"),
                        startRootNodeId=rootid,
                        sessionId=sessionId,
                        scene=scene,
                    )
                except Exception as e:
                    logger.error(f"Task generated an exception: {e}")

            # Perform inference using the request
            if request:
                # logger.error(f"{request}")
                result = reasoning(
                    request.dict(), 
                    self.memory_manager, 
                    self.ekg_construct_service.gb, 
                    self.intention_router, 
                    self.llm_config
                )
                # logger.error(f"{result}")
                # Yield user interaction if present
                if result.get("userInteraction"): 
                    print(result["userInteraction"])
                    yield result["userInteraction"]

                summary = summary or result.get("summary")  # Update summary if empty

            # If a summary is available, yield it and break the loop
            if summary: 
                print(summary)
                yield summary
                break

            # Update tasks in the pool based on the result
            user_tasks = []
            toolPlans = result.get("toolPlan", []) or []
            for toolplan in toolPlans:
                # 当存在关键信息，直接返回 " "
                if  "关键信息" in toolplan["toolDescription"]:
                    self.futures.append(
                        self.executor.submit(
                            self.empty_function,
                            **{
                                "content": " ",
                                "toolResponse": " ",
                                "type": toolplan["type"],
                                "currentNodeId": toolplan["currentNodeId"],
                                "agentName": toolplan.get("currentNodeInfo"),
                            }
                        )
                    )
                    continue

                # if toolplan
                if toolplan["type"] == "userProblem":
                    user_tasks.append(toolplan)

                if toolplan["type"] in ["onlyTool", "reactExecution"]:
                    # Submit function call to the executor for execution
                    future = self.executor.submit(
                            self.function_call, 
                            **{
                                "content": toolplan["toolDescription"],
                                "type": toolplan["type"],
                                "currentNodeId": toolplan["currentNodeId"],
                                "agentName": toolplan.get("currentNodeInfo"),
                                "memory": toolplan.get("memory"),
                                "toolDescription": toolplan.get("toolDescription")
                            }
                        )
                    self.futures.append(future)

            # Process user tasks and gather user input
            for user_task in user_tasks:
                questionType = user_task.get(
                    "questionDescription").get("questionType")
                user_query = user_task.get(
                    "questionDescription").get(
                        "questionContent").get(
                            "question")
                if user_query is None or questionType is None:
                    continue

                print(user_query)
                yield user_query  # Yield the user query for input
                user_answer = input()  # Get user input

                # Submit the user answer as a future task
                self.futures.append(
                    self.executor.submit(
                        self.empty_function,
                        **{
                            "content": user_answer,
                            "toolResponse": user_answer,
                            "type": user_task["type"],
                            "currentNodeId": user_task["currentNodeId"],
                            "agentName": user_task["currentNodeInfo"]
                        }
                    )
                )

            if not self.futures:  # If there are no tasks, pause briefly before checking again
                time.sleep(0.1)

            # Reset request to prepare for the next inference loop
            request = None
            toolPlans = None
            result = None

    def empty_function(self, **kwargs) -> Dict:
        """Return the input parameters as is (placeholder function)."""
        return kwargs

    def function_call(self, **kwargs) -> Dict:
        """Perform a single step function call and return the result."""

        function_caller = FunctioncallAgent(
            agent_name="codefuse_function_caller",  # Set the agent name
            project_config=self.project_config,  # Provide the project configuration
            tools=self.tools  # Provide the tools available for use
        )

        query = Message(
            role_type="user",
            content=f"帮我选择匹配的工具并进行执行，工具描述为'{kwargs['content']}'"
        )
        for msg in function_caller.step_stream(query, extra_params={"memory": kwargs.get("memory")}):
            pass  # Process the stream, if any

        observation = ""
        # Extract the observation from the processed messages
        if msg.parsed_contents:
            observation = msg.parsed_contents[-1].get("Observation", "")
        result = {
            "toolResponse": observation,
            "currentNodeId": kwargs.get("currentNodeId"),
            "type": kwargs.get("type"),
            "agentName": kwargs.get("agentName"),
        }
        return result  # Return the result of the function call
