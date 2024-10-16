import os
from typing import Union, Optional, List
from loguru import logger

from langchain.callbacks import AsyncIteratorCallbackHandler
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.llms.base import LLM

from .llm_config import LLMConfig
# from configs.model_config import (llm_model_dict, LLM_MODEL)

import ollama
from ollama import Client
from guidance import models, gen , select
from guidance import user, system, assistant, instruction
import guidance



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

import re
@guidance(stateless=True)
def constrained_ner(lm, input_message):
    # Split into words
    pattern = r"\*\*(.*?)\*\*"
    matches = re.findall(pattern, input_message)
    bold_strings = [match.strip() for match in matches]
    ret = ''
    for x in bold_strings:
        x = '**' + x +'**'
        ret += x + gen(name=x[2:-3], temperature= 0.8)
    return lm + ret


class OllamaModel(CustomLLMModel):

    def __init__(self, llm_config: LLMConfig = None, callBack: AsyncIteratorCallbackHandler = None,):
        
        self.llm_name = llm_config.model_name

        try:
            ollama.chat(model=self.llm_name)
        except ollama.ResponseError as e:
            print('Error:', e.error)
            if e.status_code == 404:
                ollama.pull(self.llm_name)
        self.client = Client(host='http://localhost:11434')

    def __call__(self, prompt: str,
                  stop: Optional[List[str]] = None):
        if type(prompt)==list:
            prompt=prompt[0].content

        # guidance目前没有专门集成ollama，或者使用0.1.10版本参考guidance/issues/687，或者使用尚未合并的pr:microdev1/guidance
        local_model=models.LiteLLMCompletion(api_base="http://localhost:11434", model='ollama/'+self.llm_name)

        with system():
            lm = local_model + "You are a code expert."

        with user():
            lm += prompt

        start_index = max(prompt.find("#### Response Output Format"), prompt.find("#### RESPONSE OUTPUT FORMAT"))
        if start_index == -1:
            with assistant():
                lm += gen("answer")
            return lm["answer"]

        lm += constrained_ner(prompt[start_index:])
        response = ''
        # for k, v in lm._variables.items:
        for k, v in lm._variables.items():
            response = '**' + k + ':**' + v + '\n'

        return response

    def unit_test(self, prompt: str,
                  stop: Optional[List[str]] = None):
        try:
            if type(prompt)!=str:
                prompt=prompt[0].content
            response = ollama.chat(model=self.llm_name, messages=[{'role': 'user', 'content': prompt}])
        except Exception as e:
            print("input type:",type(prompt))
            print("prompt:",prompt)
            print("error:",e)        
            return "Error occurred"  
        # response = ollama.chat(model=self.llm_name, messages=[{'role': 'user', 'content': prompt}])
        # print(response)
        return response['message']['content']

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
            # logger.debug(f"{VISIT_DOMAIN}, {VISIT_BIZ}, {VISIT_BIZ_LINE}, {aes_secret_key}")
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
        if type(prompt)==list:
            prompt=prompt[0].content
        openai_model=models.OpenAI(self.llm.model_name)

        with system():
            lm = openai_model + "You are a code expert."

        with user():
            lm += prompt

        start_index = max(prompt.find("#### Response Output Format"), prompt.find("#### RESPONSE OUTPUT FORMAT"))
        if start_index == -1:
            with assistant():
                lm += gen("answer")
            return lm["answer"]

        lm += constrained_ner(prompt[start_index:])
        response = ''
        # for k, v in lm._variables.items:
        for k, v in lm._variables.items():
            response = '**' + k + ':**' + v + '\n'

        return response

    

class LYWWLLMModel(OpenAILLMModel):

    def __init__(self, llm_config: LLMConfig, callBack: AsyncIteratorCallbackHandler = None,):
        if llm_config is None:
            api_key=os.environ.get("api_key")
            base_url=os.environ.get("api_base_url")
            model_name=os.environ.get("LLM_MODEL", "yi-34b-chat-0205")
            temperature=os.environ.get("temperature", 0.5)
            stop = [os.environ.get("stop", "")] if os.environ.get("stop", "") else None
            model_kwargs={"stop": stop}
        else:
            api_key=llm_config.api_key
            base_url=llm_config.api_base_url
            model_name=llm_config.model_name
            temperature=llm_config.temperature
            stop = [llm_config.stop] if llm_config.stop else None
            model_kwargs={"stop": stop}

        self.llm = ChatOpenAI(
                streaming=True,
                verbose=True,
                api_key=api_key,
                base_url=base_url,
                model_name=model_name,
                temperature=temperature,
                model_kwargs=model_kwargs,
            )


def getChatModelFromConfig(llm_config: LLMConfig, callBack: AsyncIteratorCallbackHandler = None, ) -> Union[ChatOpenAI, LLM, CustomLLMModel]:
    # logger.debug(f"{llm_config}")
    if llm_config and llm_config.llm and isinstance(llm_config.llm, LLM):
        return CustomLLMModel(llm=llm_config.llm)
    elif llm_config:
        model_class_dict = {"openai": OpenAILLMModel, "lingyiwanwu": LYWWLLMModel, "ollama": OllamaModel}
        model_class = model_class_dict[llm_config.model_engine]
        model = model_class(llm_config, callBack)
        # logger.debug(f"{model.llm}")
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