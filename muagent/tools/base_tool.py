from abc import ABCMeta

from langchain.agents import Tool
from langchain.tools import StructuredTool
from langchain.tools.base import ToolException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Type
try:
    import jsonref
except:
    pass

import json
import copy


def simplify_schema(schema: Dict[str, Any], definitions, no_required=False,depth=0) -> Dict[str, Any]:
    """简化 schema，去除 $ref 引用和 definitions"""
    if definitions is None: return schema
    schema_new = copy.deepcopy(schema)
    # 去掉 title 字段
    schema_new.pop('title', None)
    # 遍历 properties
    if 'properties' in schema:
        for key, value in schema['properties'].items():
            for k,v in value.items():
                
                if k == "allOf":
                    ref_model_name = v[0]['$ref'].split('/')[-1]  # 提取模型名称
                    ref_model_value = simplify_schema(definitions[ref_model_name], definitions, no_required=True, depth=depth+1)
                    schema_new["properties"][key].pop(k)
                    schema_new["properties"][key].update(ref_model_value)
                    
                if isinstance(v, dict) and '$ref' in v:
                    ref_model_name = v['$ref'].split('/')[-1]  # 提取模型名称
                    ref_model_value = simplify_schema(definitions[ref_model_name], definitions, no_required=True, depth=depth+1)
                    schema_new["properties"][key][k] = ref_model_value
                    
            schema_new["properties"][key].pop("title")
    # 去掉 definitions 部分
    if no_required:
        schema_new.pop('required', None)
    schema_new.pop('definitions', None)

    return schema_new


class _ToolWrapperMeta(ABCMeta):
    """A meta call to replace the tool wrapper's run function with
    wrapper about error handling."""

    def __new__(mcs, name: Any, bases: Any, attrs: Any) -> Any:
        if "__call__" in attrs:
            attrs["__call__"] = attrs["__call__"]
        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name: Any, bases: Any, attrs: Any) -> None:
        if not hasattr(cls, "_registry"):
            cls._registry = {} # class name 
            cls._toolname_registry = {} # class attribute name
        else:
            cls._registry[name] = cls
            cls._toolname_registry[cls.name] = cls
        super().__init__(name, bases, attrs)


class BaseToolModel(metaclass=_ToolWrapperMeta):
    name = "BaseToolModel"
    description = "Tool Description"

    @classmethod
    def _from_name(cls, tool_name: str) -> 'BaseToolModel':
        
        """Get the specific model wrapper"""
        if tool_name in cls._registry:
            return cls._registry[tool_name]()  # type: ignore[return-value]
        elif tool_name in cls._toolname_registry:
            return cls._toolname_registry[tool_name]()  # type: ignore[return-value]
        else:
            raise KeyError(
                f"Tool Library is missiong"
                f" {tool_name}, please check your tool name"
            )

    @classmethod
    def intput_to_json_schema(cls) -> Dict[str, Any]:
        '''Transform schema to json structure'''
        try:
            return jsonref.loads(cls.ToolInputArgs.schema_json())
        except:
            return simplify_schema(
            cls.ToolInputArgs.schema(),
            cls.ToolInputArgs.schema().get("definitions")
        )

    @classmethod
    def output_to_json_schema(cls) -> Dict[str, Any]:
        '''Transform schema to json structure'''
        try:
            return jsonref.loads(cls.ToolInputArgs.schema_json())
        except:
            return simplify_schema(
                cls.ToolOutputArgs.schema(),
                cls.ToolOutputArgs.schema().get("definitions")
            )

    class ToolInputArgs(BaseModel):
        """
        Input for MoveFileTool.
        Tips:
            default control Required, e.g.  key1 is not Required/key2 is Required
        """

        key1: str = Field(default=None, description="hello world!")
        key2: str = Field(..., description="hello world!!")

    class ToolOutputArgs(BaseModel):
        """
        Input for MoveFileTool.
        Tips:
            default control Required, e.g.  key1 is not Required/key2 is Required
        """

        key1: str = Field(default=None, description="hello world!")
        key2: str = Field(..., description="hello world!!")

    @classmethod
    def run(cls) -> ToolOutputArgs:
        """excute your tool!"""
        pass


class BaseTools:
    tools: List[BaseToolModel]


def get_tool_schema(tool: BaseToolModel) -> Dict:
    '''转json schema结构'''
    data = jsonref.loads(tool.schema_json())
    _ = json.dumps(data, indent=4)
    del data["definitions"]
    return data


def _handle_error(error: ToolException) -> str:
    return (
        "The following errors occurred during tool execution:"
        + error.args[0]
        + "Please try again."
    )

import requests
from loguru import logger
def fff(city, extensions):
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    json_data = {"key": "4ceb2ef6257a627b72e3be6beab5b059", "city": city, "extensions": extensions}
    logger.debug(f"json_data: {json_data}")
    res = requests.get(url, params={"key": "4ceb2ef6257a627b72e3be6beab5b059", "city": city, "extensions": extensions})
    return res.json()


def toLangchainTools(tools: BaseTools) -> List:
    ''''''
    return [
        StructuredTool(
            name=tool.name,
            func=tool.run,
            description=tool.description,
            args_schema=tool.ToolInputArgs,
            handle_tool_error=_handle_error,
        ) for tool in tools
    ]
