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

from muagent.memory_manager import LocalMemoryManager


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

# prepare your message
message1 = Message(
    session_index="default", 
    role_name="test1", 
    role_type="user", 
    content="hello",
    spec_parsed_contents=[{"input": "hello"}],
)

text = "hi! how can I help you?"
message2 = Message(
    session_index="shuimo", 
    role_name="test2", 
    role_type="assistant", 
    content=text,
    arsed_output_list=[{"answer": text}],
)

text = "they say hello and hi to each other"
message3 = Message(
    session_index="shanshi", 
    role_name="test3", 
    role_type="summary", 
    content=text, 
    spec_parsed_contents=[{"summary": text}],
)

vb_config = VBConfig(vb_type="LocalFaissHandler")

# append or extend test
print("###"*10 + "append or extend" + "###"*10)
local_memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=model_config, vb_config=vb_config, do_init=True)
# append can ignore user_name
local_memory_manager.append(message=message1)
local_memory_manager.append(message=message2)
local_memory_manager.append(message=message3)

# test init_local
print("###"*10 + "dont load local" + "###"*10)
local_memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=model_config, vb_config=vb_config, do_init=True)
print(local_memory_manager.get_memory_pool("default").to_format_messages(
    content_key="content", format_type='str'))
print(local_memory_manager.get_memory_pool("shuimo").to_format_messages(
    content_key="content", format_type='str'))
print(local_memory_manager.get_memory_pool("shanshi").to_format_messages(
    content_key="content", format_type='str'))

# test load from local
print("###"*10 + "load local" + "###"*10)
local_memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=model_config, vb_config=vb_config, do_init=False)
print(local_memory_manager.get_memory_pool("default").to_format_messages(
    content_key="content", format_type='str'))
print(local_memory_manager.get_memory_pool("shuimo").to_format_messages(
    content_key="content", format_type='str'))
print(local_memory_manager.get_memory_pool("shanshi").to_format_messages(
    content_key="content", format_type='str'))



local_memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=model_config, vb_config=vb_config, do_init=False)
# embedding retrieval test
print("###"*10 + "retrieval" + "###"*10)
text = "say hi to each other,"
# retrieval_type=datetime => retrieval from datetime and jieba
print(local_memory_manager.router_retrieval(
    session_index="shanshi", text=text, datetime=getCurrentDatetime(), 
    n=4, top_k=5, retrieval_type= "datetime"))
# retrieval_type=embedding => retrieval from embedding
print(local_memory_manager.router_retrieval(
    session_index="shanshi", text=text, top_k=5, retrieval_type= "embedding"))
# retrieval_type=text => retrieval from jieba
print(local_memory_manager.router_retrieval(
    session_index="shanshi", text=text, top_k=5, retrieval_type= "text"))

# # recursive_summary test
print("###"*10 + "recursive_summary" + "###"*10)
print(local_memory_manager.recursive_summary(local_memory_manager.get_memory_pool("shanshi").messages, split_n=1, session_index="shanshi"))

# print(local_memory_manager.recursive_summary(local_memory_manager.get_memory_pool("shuimo").messages, split_n=1, session_index="shanshi"))

# print(local_memory_manager.recursive_summary(local_memory_manager.get_memory_pool("default").messages, split_n=1, session_index="shanshi"))


# test after clear local vs and jsonl
print("###"*10 + "test after clear local vs and jsonl" + "###"*10)
local_memory_manager.clear_local(re_init=True)
print(local_memory_manager.get_memory_pool("shanshi").to_format_messages(
    content_key="content", format_type='str'))