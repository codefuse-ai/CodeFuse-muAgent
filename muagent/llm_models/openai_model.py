import os
import re
from typing import Union, Optional, List, Dict, Literal
from loguru import logger

from langchain.callbacks import AsyncIteratorCallbackHandler
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.llms.base import LLM

from .llm_config import LLMConfig
from .llm_shemas import *

try:
    import ollama
except:
    pass

# from configs.model_config import (llm_model_dict, LLM_MODEL)
def replacePrompt(prompt: str, keys: list[str] = []):
    prompt = prompt.replace("{", "{{").replace("}", "}}")
    for key in keys:
        prompt = prompt.replace(f"{{{{{key}}}}}", f"{{{key}}}")
    return prompt



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

    def fc(
        self, 
        messages: List[ChatMessage],
        tools: List[Union[str, object]] = [],
        system_prompt: Optional[str] = None,
        tool_choice: Optional[Literal["auto", "required"]] = "auto",
        parallel_tool_calls: Optional[bool] = None,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        '''
        '''
        from muagent.base_configs.prompts.functioncall_template_prompt import (
            FUNCTION_CALL_PROMPT_en,
            FC_AUTO_PROMPT_en,
            FC_REQUIRED_PROMPT_en,
            FC_PARALLEL_PROMPT_en,
            FC_RESPONSE_PROMPT_en
        )

        use_tools = len(tools) > 0

        prompts = []
        if use_tools:
            prompts.append(FUNCTION_CALL_PROMPT_en)

        if system_prompt:
            prompts.append(system_prompt)
        
        if use_tools and tool_choice =="auto":
            prompts.append(FC_AUTO_PROMPT_en)
        elif use_tools and tool_choice =="required":
            prompts.append(FC_REQUIRED_PROMPT_en)
        
        if use_tools and parallel_tool_calls:
            prompts.append(FC_PARALLEL_PROMPT_en)
        
        prompts.append("you are a helpful assistant to respond user's question:\n## Question Input\n{content}")

        if use_tools:
            prompts.append(FC_RESPONSE_PROMPT_en)

        system_prompt = "\n".join(prompts)
        # 
        content = "\n\n".join([f"{i.role}: {i.content}" for i in messages])
        content = "\n\n".join([f"{i.content}" for i in messages])
        if use_tools:
            system_prompt = replacePrompt(system_prompt, keys=["content", "tool_desc"])
            prompt = system_prompt.format(content=content, tool_desc="\n".join(tools))
        else:
            system_prompt = replacePrompt(system_prompt, keys=["content"])
            prompt = system_prompt.format(content=content)

        llm_output = self.predict(prompt)

        # logger.info(f"prompt: {prompt}")
        # logger.info(f"llm_output: {llm_output}")
        # parse llm functioncall
        if "```json" in llm_output:
            match_value = re.search(r'```json\n(.*?)```', llm_output, re.DOTALL)
        else:
            match_value = llm_output

        try:
            function_call_output = json.loads(match_value.group(1).strip())
        except:
            function_call_output = eval(match_value.group(1).strip())

        function_call_output = function_call_output if isinstance(function_call_output, list) \
              else [function_call_output]
        # 
        fc_response = LLMResponse(
            choices=[Choice(
                finish_reason="tool_calls",
                message=LLMOuputMessage(
                    content=None,
                    role="assistant",
                    tool_calls=[
                        ToolCall(
                            function=FunctionCallData(
                                name=fco["name"],
                                arguments=fco["arguments"],
                            )
                        )
                        for fco in function_call_output
                    ],
                )
            )],
            id="",
            model="",
            object="chat.completion",
            usage=None
        )
        return fc_response


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
                    http_client=http_client,
                    timeout=120
                )
        elif http_client:
            self.llm = ChatOpenAI(
                    streaming=True,
                    verbose=True,
                    api_key=llm_config.api_key,
                    model_name=llm_config.model_name,
                    temperature=llm_config.temperature,
                    model_kwargs={"stop": llm_config.stop},
                    http_client=http_client,
                    timeout=120
                    # callbacks=[callBack],
                )
        else:
            self.llm = ChatOpenAI(
                    streaming=True,
                    verbose=True,
                    api_key=llm_config.api_key,
                    model_name=llm_config.model_name,
                    base_url=llm_config.api_base_url,
                    temperature=llm_config.temperature,
                    model_kwargs={"stop": llm_config.stop},
                    timeout=120
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
                timeout=120
            )


class OllamaLLMModel(CustomLLMModel):
    def __init__(self, llm_config: LLMConfig, callBack: AsyncIteratorCallbackHandler = None,):
        self.llm = ollama.Client()
        self.model_name = llm_config.model_name

    def __call__(self, prompt: str,
                  stop: Optional[List[str]] = None):
        stream = self.llm.generate(
                model=self.model_name,
                prompt=prompt,
                stream=True,
            )
        answer = ""
        for chunk in stream:
            answer += chunk['response']
        return answer


class KIMILLMModel(LYWWLLMModel):
    pass

class QwenLLMModel(LYWWLLMModel):
    pass


def getChatModelFromConfig(llm_config: LLMConfig, callBack: AsyncIteratorCallbackHandler = None, ) -> Union[ChatOpenAI, LLM, CustomLLMModel]:
    # logger.debug(f"{llm_config}")
    if llm_config and llm_config.llm and isinstance(llm_config.llm, LLM):
        return CustomLLMModel(llm=llm_config.llm)
    elif llm_config:
        model_class_dict = {
            "openai": OpenAILLMModel, "lingyiwanwu": LYWWLLMModel, 
            "kimi": KIMILLMModel, "moonshot": KIMILLMModel,
            "qwen": QwenLLMModel, "ollama": OllamaLLMModel
        }
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