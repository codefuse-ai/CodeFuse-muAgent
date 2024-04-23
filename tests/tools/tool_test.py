import os
from loguru import logger

try:
    import os, sys
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
    api_key = os.environ["OPENAI_API_KEY"]
    api_base_url= os.environ["API_BASE_URL"]
    model_name = os.environ["model_name"]
    embed_model = os.environ["embed_model"]
    embed_model_path = os.environ["embed_model_path"]
except Exception as e:
    # set your config
    api_key = ""
    api_base_url= ""
    model_name = ""
    embed_model = ""
    embed_model_path = ""
    logger.error(f"{e}")


from langchain.tools import StructuredTool
from muagent.tools import (
    WeatherInfo, Multiplier, toLangchainTools,
    TOOL_DICT, TOOL_SETS
)

# 函数执行
tools =  [
    StructuredTool(
            name=Multiplier.name,
            func=Multiplier.run,
            description=Multiplier.description,
            args_schema=Multiplier.ToolInputArgs,
        ), 
        StructuredTool(
            name=WeatherInfo.name,
            func=WeatherInfo.run,
            description=WeatherInfo.description,
            args_schema=WeatherInfo.ToolInputArgs,
        )
        ]

tools = toLangchainTools([TOOL_DICT["Multiplier"]])

# tool run 测试
print(tools[0].func(1,2))