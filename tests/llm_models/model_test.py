from loguru import logger
import os, sys
import json

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(src_dir)
try:
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


src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)

from muagent.models import get_model
from muagent.schemas.models import ModelConfig

model_configs = json.loads(os.environ["MODEL_CONFIGS"])

# "openai_chat","yi_chat","qwen_chat", "dashscope_chat""moonshot_chat", "ollama_chat"

model_type = "ollama_chat"
model_config = model_configs[model_type]

model_config = ModelConfig(
    config_name="model_test",
    model_type=model_type,
    model_name=model_config["model_name"],
    api_key=model_config["api_key"],
)
model = get_model(model_config)

# 工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["c", "f"]},
                },
                "required": ["location", "unit"],
                "additionalProperties": False,
            },
        },
    }
]


# print(model.generate("输出 '今天你好'", stop="你", format_type='str'))
for i in model.generate_stream("hello", stop="你", format_type='str'):
    print(i)

# # 
# print(model.generate("hello", format_type='str'))

# # 
# for i in model.generate_stream("hello", format_type='str'):
#     print(i)

# # 
# print(model.chat([{"role": "user", "content":"hello"}], format_type='str'))

# #
# for i in model.chat_stream([{"role": "user", "content":"hello"}], format_type='str'):
#     print(i)

# # 
# print(model.function_call(tools=tools, prompt="我想查北京的天气"))

# # 
# for i in model.function_call_stream(tools=tools, messages=[{"role": "user", "content":"我想查北京的天气"}]):
#     print(i)