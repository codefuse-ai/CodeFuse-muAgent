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




from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
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
# chat_prompt = ChatPromptTemplate.from_messages([("human", "{input}")])
# chain = LLMChain(prompt=chat_prompt, llm=model)
# content = chain({"input": "who are you!"})
# print(content)

# test 3
# import openai
# # openai.api_key = "EMPTY" # Not support yet
# openai.api_base = api_base_url
# # create a chat completion
# completion = openai.ChatCompletion.create(
#     model=model_name,
#     messages=[{"role": "user", "content": "Hello! What is your name? "}],
#     max_tokens=100,
# )
# # print the completion
# print(completion.choices[0].message.content)

# import openai
# # openai.api_key = "EMPTY" # Not support yet
# openai.api_base = "http://127.0.0.1:8888/v1"
# model = "example"
# # create a chat completion
# completion = openai.ChatCompletion.create(
#     model=model,
#     messages=[{"role": "user", "content": "Hello! What is your name? "}],
#     max_tokens=100,
# )
# # print the completion
# print(completion.choices[0].message.content)