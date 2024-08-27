import sys
from guidance import models, gen , select
sys.path.append('D:/CodeFuse-muAgent-main')
import examples.test_config

import os
from typing import Union, Optional, List
from loguru import logger

from langchain.callbacks import AsyncIteratorCallbackHandler
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.llms.base import LLM
from muagent.llm_models.llm_config import LLMConfig
# from .llm_config import LLMConfig
# from configs.model_config import (llm_model_dict, LLM_MODEL)
import ollama
from ollama import Client

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

    def __init__(self, llm_config: LLMConfig = None, callBack: AsyncIteratorCallbackHandler = None,):
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
        # print('prompt:')
        # print(prompt)
        # print("response:")
        prompt='#### AGENT PROFILE\n\n### ROLE\nWhen users seek assistance in breaking down complex issues into manageable and actionable steps,\nyour responsibility is to deliver a well-organized strategy or resolution through the use of tools or coding.\n\nATTENTION: response carefully referenced "Response Output Format" in format.\n### TOOL INFORMATION\n\nBelow is a list of tools that are available for your use:\nStockName: 通过股票名称查询股票代码, args: {\'stock_name\': {\'title\': \'Stock Name\', \'description\': \'股票名称\', \'type\': \'integer\'}}\nStockInfo: 根据提供的股票代码、日期范围和数据频率提供股票市场数据。, args: {\'code\': {\'title\': \'Code\', \'description\': "要查询的股票代码，格式为\'marketcode\'", \'type\': \'string\'}, \'end_date\': {\'title\': \'End Date\', \'description\': \'数据查询的结束日期。留空则为当前日期。如果没有提供结束日期，就留空\', \'default\': \'\', \'type\': \'string\'}, \'count\': {\'title\': \'Count\', \'description\': \'返回数据点的数量。\', \'default\': 10, \'type\': \'integer\'}, \'frequency\': {\'title\': \'Frequency\', \'description\': "数据点的频率，例如，\'1d\'表示每日，\'1w\'表示每周，\'1M\'表示每月，\'1m\'表示每分钟等。", \'default\': \'1d\', \'type\': \'string\'}}\n\nvalid "tool_name" value is:\nStockName, StockInfo\n\n### ATTENTION\nIncorporate the context of the SESSION RECORDS, answer question concisely and professionally.\nresponse carefully referenced in \'Response Output Format\'.\n\n#### CONTEXT FORMAT\nUse the content provided in the context.\n### SESSION RECORDS\nthis is SESSION RECORDS\n\n#### INPUT FORMAT\n\n**Question:** First, clarify the problem to be solved.\n\n#### RESPONSE OUTPUT FORMAT\n\n **Action Status:** Set to \'planning\' to provide a sequence of tasks, or \'only_answer\' to provide a direct response without a plan.\n\n**Action:** \n```list\n  "First, we should ...",\n]\n```\n\nOr, provide the direct answer.\n\n## BEGIN!!!\n#### CONTEXT\n\n### SESSION RECORDS\n<user-human-message>\n查询贵州茅台的股票代码，并查询截止到当前日期(2023年12月24日)的最近10天的每日时序数据，然后用代码画出折线图并分析\n</user-human-message>\n#### RESPONSE OUTPUT'
        
        # response='**Action Status:** planning\n\n**Action:** \n```list\n  "First, we should use the StockName tool to find the stock code for Guizhou Maotai.",\n  "Next, we will use the StockInfo tool to retrieve the daily time series data for the last 10 days up to December 24, 2023.",\n  "After obtaining the data, we will use coding to plot a line graph and analyze the trends."\n```'
        try:
            cur_llm=models.OpenAI(self.llm)
            response = cur_llm.predict(prompt, stop=stop)
        except Exception as e:
            print("prompt:",prompt)
            print("error:",e)        
            return "Error occurred"  # 返回一个错误信息或采取其他适当的措施

        # print(response)
        return self.llm.predict(prompt, stop=stop)

    # def __call__2(self, prompt: str,
    #               stop: Optional[List[str]] = None):
    #     # print('prompt:')
    #     # print(prompt)
    #     # print("response:")
    #     prompt='#### AGENT PROFILE\n\n### ROLE\nWhen users seek assistance in breaking down complex issues into manageable and actionable steps,\nyour responsibility is to deliver a well-organized strategy or resolution through the use of tools or coding.\n\nATTENTION: response carefully referenced "Response Output Format" in format.\n### TOOL INFORMATION\n\nBelow is a list of tools that are available for your use:\nStockName: 通过股票名称查询股票代码, args: {\'stock_name\': {\'title\': \'Stock Name\', \'description\': \'股票名称\', \'type\': \'integer\'}}\nStockInfo: 根据提供的股票代码、日期范围和数据频率提供股票市场数据。, args: {\'code\': {\'title\': \'Code\', \'description\': "要查询的股票代码，格式为\'marketcode\'", \'type\': \'string\'}, \'end_date\': {\'title\': \'End Date\', \'description\': \'数据查询的结束日期。留空则为当前日期。如果没有提供结束日期，就留空\', \'default\': \'\', \'type\': \'string\'}, \'count\': {\'title\': \'Count\', \'description\': \'返回数据点的数量。\', \'default\': 10, \'type\': \'integer\'}, \'frequency\': {\'title\': \'Frequency\', \'description\': "数据点的频率，例如，\'1d\'表示每日，\'1w\'表示每周，\'1M\'表示每月，\'1m\'表示每分钟等。", \'default\': \'1d\', \'type\': \'string\'}}\n\nvalid "tool_name" value is:\nStockName, StockInfo\n\n### ATTENTION\nIncorporate the context of the SESSION RECORDS, answer question concisely and professionally.\nresponse carefully referenced in \'Response Output Format\'.\n\n#### CONTEXT FORMAT\nUse the content provided in the context.\n### SESSION RECORDS\nthis is SESSION RECORDS\n\n#### INPUT FORMAT\n\n**Question:** First, clarify the problem to be solved.\n\n#### RESPONSE OUTPUT FORMAT\n\n **Action Status:** Set to \'planning\' to provide a sequence of tasks, or \'only_answer\' to provide a direct response without a plan.\n\n**Action:** \n```list\n  "First, we should ...",\n]\n```\n\nOr, provide the direct answer.\n\n## BEGIN!!!\n#### CONTEXT\n\n### SESSION RECORDS\n<user-human-message>\n查询贵州茅台的股票代码，并查询截止到当前日期(2023年12月24日)的最近10天的每日时序数据，然后用代码画出折线图并分析\n</user-human-message>\n#### RESPONSE OUTPUT'
        
    #     # response='**Action Status:** planning\n\n**Action:** \n```list\n  "First, we should use the StockName tool to find the stock code for Guizhou Maotai.",\n  "Next, we will use the StockInfo tool to retrieve the daily time series data for the last 10 days up to December 24, 2023.",\n  "After obtaining the data, we will use coding to plot a line graph and analyze the trends."\n```'
    #     try:
    #         # response = self.llm+f'{prompt}'+gen(stop='.')
    #         self.llm=models.OpenAI(llm_config.model_name) 
    #         response = self.llm+f'{prompt}'+gen(stop='.')
    #     except Exception as e:
    #         print("prompt:",prompt)
    #         print("error:",e)        
    #         return "Error occurred"  # 返回一个错误信息或采取其他适当的措施

    #     # print(response)
    #     return response

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
        # model_class_dict = {"openai": OpenAILLMModel, "lingyiwanwu": LYWWLLMModel}
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
    
