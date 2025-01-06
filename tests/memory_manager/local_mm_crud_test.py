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
    api_key = os.environ["OPENAI_API_KEY"]
    api_base_url= os.environ["API_BASE_URL"]
    model_name = os.environ["model_name"]
    model_engine = os.environ["model_engine"]
    embed_model = os.environ["embed_model"]
    embed_model_path = os.environ["embed_model_path"]
except Exception as e:
    # set your config
    api_key = ""
    api_base_url= ""
    model_name = ""
    model_engine = os.environ["model_engine"]
    embed_model = ""
    embed_model_path = ""
    logger.error(f"{e}")

# test local code
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)


from muagent.utils.common_utils import getCurrentDatetime
from muagent.schemas.db import DBConfig, GBConfig, VBConfig, TBConfig
from muagent.schemas import Message
from muagent.models import ModelConfig, get_model

from muagent.memory_manager import LocalMemoryManager, TbaseMemoryManager


from muagent.llm_models.llm_config import EmbedConfig, LLMConfig

model_configs = json.loads(os.environ["MODEL_CONFIGS"])

# 
# llm_config = LLMConfig(
#     model_name=model_name, model_engine=model_engine, api_key=api_key,  api_base_url=api_base_url, temperature=0.3,
# )
model_type = "qwen_chat"
model_config = model_configs[model_type]
model_config = ModelConfig(
    config_name="model_test",
    model_type=model_type,
    model_name=model_config["model_name"],
    api_key=model_config["api_key"],
)


# embed_config = EmbedConfig(
#     embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
# )
model_type = "qwen_text_embedding"
embed_config = model_configs[model_type]
embed_config = ModelConfig(
    config_name="model_test",
    model_type=model_type,
    model_name=embed_config["model_name"],
    api_key=embed_config["api_key"],
)


# 初始化 TbaseHandler 实例
tb_config = TBConfig(
    tb_type="TbaseHandler",
    index_name="muagent_test",
    host="127.0.0.1",
    port=os.environ['tb_port'],
    username=os.environ['tb_username'],
    password=os.environ['tb_password'],
)

vb_config = VBConfig(vb_type="LocalFaissHandler")

# append or extend test
# memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=model_config, vb_config=vb_config, do_init=True)
memory_manager = TbaseMemoryManager(embed_config=embed_config, llm_config=model_config, tb_config=tb_config)


# prepare your message
message1 = Message(
    session_index="default", 
    message_index="default",
    role_name="crud_test", 
    role_type="user", 
    content="hello",
    role_tags=["shanshi"]
)

# append can ignore user_name
memory_manager.append(message=message1)
print(memory_manager.get_memory_pool("default").to_format_messages(format_type="raw"))

# prepare your message
message2 = Message(
    session_index="default", 
    message_index="default",
    role_name="crud_test", 
    role_type="user", 
    content="hello",
    role_tags=["test"]
)

memory_manager.append(message=message2, role_tag="test")
print(memory_manager.get_memory_pool("default").to_format_messages(format_type="raw"))