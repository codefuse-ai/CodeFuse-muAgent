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



# test 1
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
model = ChatOpenAI(
    streaming=True,
    verbose=True,
    openai_api_key=api_key,
    openai_api_base=api_base_url,
    model_name=model_name,
    stop="123"
)
# test 1
print(model.predict("please output 123!"))


# # test 2
# from openai import OpenAI
# http_client = None
# client = OpenAI(api_key=os.environ.get("api_key"), http_client=http_client)
# model = 'gpt-3.5-turbo'
# messages=[{'role': 'user', 'content': 'Hello World'}]
# result = client.chat.completions.create(model=model, messages=messages)
# print(result)
