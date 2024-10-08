import os, sys
from loguru import logger

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
from muagent.connector.memory_manager import BaseMemoryManager, LocalMemoryManager
# from muagent.connector.memory_manager import LocalMemoryManager, Message
# from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
# from muagent.schemas.db import DBConfig, GBConfig, VBConfig, TBConfig

# llm_config = LLMConfig(
#     model_name=model_name, model_engine=model_engine, api_key=api_key,  api_base_url=api_base_url, temperature=0.3,
# )

# embed_config = EmbedConfig(
#     embed_engine="model", embed_model=embed_model, embed_model_path=embed_model_path
# )


# # prepare your message
# message1 = Message(
#     chat_index="default", role_name="test1", role_type="user", role_content="hello",
#     parsed_output_list=[{"input": "hello"}], user_name="default"
# )

# text = "hi! how can I help you?"
# message2 = Message(
#     chat_index="shuimo", role_name="test2", role_type="assistant", role_content=text, parsed_output_list=[{"answer": text}],
#     user_name="shuimo"
# )

# text = "they say hello and hi to each other"
# message3 = Message(
#     chat_index="shanshi", role_name="test3", role_type="summary", role_content=text, 
#     parsed_output_list=[{"summary": text}],
#     user_name="shanshi"
#     )

# # append or extend test
# vb_config = VBConfig(vb_type="LocalFaissHandler")
# local_memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=llm_config, vb_config=vb_config, do_init=True)
# # append can ignore user_name
# local_memory_manager.append(message=message1)
# local_memory_manager.append(message=message2)
# local_memory_manager.append(message=message3)

# # # test init_local
# # local_memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=llm_config, vb_config=vb_config, do_init=True)
# # print(local_memory_manager.get_memory_pool("default").messages)
# # print(local_memory_manager.get_memory_pool("shuimo").messages)
# # print(local_memory_manager.get_memory_pool("shanshi").messages)

# # # test load from local
# # local_memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=llm_config, vb_config=vb_config, do_init=False)
# # print(local_memory_manager.get_memory_pool("shanshi").messages)

# # # test after clear local vs and jsonl
# # local_memory_manager.clear_local(re_init=True)
# # print(local_memory_manager.get_memory_pool("shanshi").messages)

# # # test init_local
# # local_memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=llm_config, vb_config=vb_config, do_init=False)
# # print(local_memory_manager.get_memory_pool("shanshi").messages)


# local_memory_manager = LocalMemoryManager(embed_config=embed_config, llm_config=llm_config, vb_config=vb_config, do_init=False)
# # embedding retrieval test
# text = "say hi to each other, i want some help"
# # retrieval_type=datetime => retrieval from datetime and jieba
# print(local_memory_manager.router_retrieval(chat_index="shanshi", text=text, datetime="2024-06-26 14:15:00", n=4, top_k=5, retrieval_type= "datetime"))
# # retrieval_type=eembedding => retrieval from embedding
# print(local_memory_manager.router_retrieval(chat_index="shanshi", text=text, top_k=5, retrieval_type= "embedding"))
# # retrieval_type=text => retrieval from jieba
# print(local_memory_manager.router_retrieval(chat_index="shanshi", text=text, top_k=5, retrieval_type= "text"))

# # # recursive_summary test
# print(local_memory_manager.recursive_summary(local_memory_manager.get_memory_pool("shanshi").messages, split_n=1, chat_index="shanshi"))

# # print(local_memory_manager.recursive_summary(local_memory_manager.get_memory_pool("shuimo").messages, split_n=1, chat_index="shanshi"))

# # print(local_memory_manager.recursive_summary(local_memory_manager.get_memory_pool("default").messages, split_n=1, chat_index="shanshi"))

