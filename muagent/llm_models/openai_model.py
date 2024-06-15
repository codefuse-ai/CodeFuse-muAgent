import os
from typing import Union, Optional, List
from loguru import logger

from langchain.callbacks import AsyncIteratorCallbackHandler
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.llms.base import LLM

from .llm_config import LLMConfig
# from configs.model_config import (llm_model_dict, LLM_MODEL)


class CustomLLMModel:
    
    def __init__(self, llm: LLM):
        self.llm: LLM = llm

    def __call__(self, prompt: str,
                  stop: Optional[List[str]] = None):
        return self.llm(prompt, stop)

    def _call(self, prompt: str,
                  stop: Optional[List[str]] = None):
        return self(prompt, stop)
    
    def predict(self, prompt: str,
                  stop: Optional[List[str]] = None):
        return self(prompt, stop)

    def batch(self, prompts: str,
                  stop: Optional[List[str]] = None):
        return [self(prompt, stop) for prompt in prompts]



class OpenAILLMModel(CustomLLMModel):

    def __init__(self, llm_config: LLMConfig, callBack: AsyncIteratorCallbackHandler = None,):
        # logger.debug(f"llm type is {type(llm_config.llm)}")
        try:
            from zdatafront import ZDataFrontClient
            from zdatafront.openai import SyncProxyHttpClient
            # zdatafront 分配的业务标记
            VISIT_DOMAIN = os.environ.get("visit_domain")
            VISIT_BIZ = os.environ.get("visit_biz")
            VISIT_BIZ_LINE = os.environ.get("visit_biz_line")
            # zdatafront 提供的统一加密密钥
            aes_secret_key = os.environ.get("aes_secret_key")

            zdatafront_client = ZDataFrontClient(visit_domain=VISIT_DOMAIN, visit_biz=VISIT_BIZ, visit_biz_line=VISIT_BIZ_LINE, aes_secret_key=aes_secret_key)
            http_client = SyncProxyHttpClient(zdatafront_client=zdatafront_client, prefer_async=True)
        except Exception as e:
            logger.warning("There is no zdatafront, you just do as openai config")
            http_client = None

        if llm_config is None:
            self.llm = ChatOpenAI(
                    streaming=True,
                    verbose=True,
                    api_key=os.environ.get("api_key"),
                    base_url=os.environ.get("api_base_url"),
                    model_name=os.environ.get("LLM_MODEL", "gpt-3.5-turbo"),
                    temperature=os.environ.get("temperature", 0.5),
                    model_kwargs={"stop": os.environ.get("stop", "")},
                    http_client=http_client
                )
        else:
            self.llm = ChatOpenAI(
                    streaming=True,
                    verbose=True,
                    model_name=llm_config.model_name,
                    temperature=llm_config.temperature,
                    model_kwargs={"stop": llm_config.stop},
                    http_client=http_client,
                    # callbacks=[callBack],
                )
        if callBack is not None:
            self.llm.callBacks = [callBack]

    def __call__(self, prompt: str,
                  stop: Optional[List[str]] = None):
        return self.llm.predict(prompt, stop=stop)
    

class LYWWLLMModel(OpenAILLMModel):

    def __init__(self, llm_config: LLMConfig, callBack: AsyncIteratorCallbackHandler = None,):
        if llm_config is None:
            api_key=os.environ.get("api_key")
            base_url=os.environ.get("api_base_url")
            model_name=os.environ.get("LLM_MODEL", "yi-34b-chat-0205")
            temperature=os.environ.get("temperature", 0.5)
            model_kwargs={"stop": os.environ.get("stop", "")}
        else:
            api_key=llm_config.api_key
            base_url=llm_config.api_base_url
            model_name=llm_config.model_name
            temperature=llm_config.temperature
            model_kwargs={"stop": llm_config.stop}

        self.llm = ChatOpenAI(
                streaming=True,
                verbose=True,
                api_key=api_key,
                base_url=base_url,
                model_name=model_name,
                temperature=temperature,
                model_kwargs=model_kwargs,
            )



def getChatModelFromConfig(llm_config: LLMConfig, callBack: AsyncIteratorCallbackHandler = None, ) -> Union[ChatOpenAI, LLM]:

    if llm_config and llm_config.llm and isinstance(llm_config.llm, LLM):
        return CustomLLMModel(llm=llm_config.llm)
    elif llm_config:
        model_class_dict = {"openai": OpenAILLMModel, "lingyiwanwu": LYWWLLMModel}
        model_class = model_class_dict[llm_config.model_engine]
        model = model_class(llm_config, callBack)
        logger.debug(f"{model}")
        return model
    else:
        return OpenAILLMModel(llm_config, callBack)


import json, requests


def getExtraModel():
    return TestModel()

class TestModel:
    
    def predict(self, request_body):
        headers = {"Content-Type":"application/json;charset=UTF-8",
        "codegpt_user":"",
        "codegpt_token":""
                }
        url = ""
        xxx = requests.post(
            url, 
            data=json.dumps(request_body,ensure_ascii=False).encode('utf-8'), 
            headers=headers)
        return xxx.json()["data"]