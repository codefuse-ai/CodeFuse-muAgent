import requests
import json
import base64
import sys
import os

import threading

import ast
import html
import json
import random
import time
import traceback

import urllib.parse
from binascii import a2b_hex, b2a_hex

import openai
import requests
from colorama import Fore
from Crypto.Cipher import AES
from loguru import logger

try:
    from call_antgroup_llm import call_antgroup_llm
except:
    logger.warning("it's ok")

MOST_RETRY_TIMES = 5

SLEEP_TIME_BEFORE_RETRY = 10

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
)
sys.path.append(src_dir)
sys.path.append(src_dir + '/examples/')
print(src_dir)
from muagent.llm_models.llm_config import  LLMConfig
from muagent.llm_models import getChatModelFromConfig



def call_llm(
        input_content = '中国的首都是哪儿', 
        llm_model = None, 
        stop = None, 
        temperature = 0.1,
        presence_penalty=0,
        llm_config=None
        ):
    
    if os.environ['operation_mode'] == 'open_source': # 'open_source' or 'antcode'
    
        #开源环境，call_llm 依靠用户的配置
        try:
            src_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            sys.path.append(src_dir)
            #import test_config
            # api_key = os.environ["OPENAI_API_KEY"]
            # api_base_url= os.environ["API_BASE_URL"]
            # model_name = os.environ["model_name"]
            # model_engine = os.environ["model_engine"]
            # llm_temperature = os.environ["llm_temperature"] 
           
           
            api_key         = os.environ["gpt4-OPENAI_API_KEY"]
            api_base_url    = os.environ["gpt4-API_BASE_URL"]
            model_name      = os.environ["gpt4-model_name"]
            model_engine    = os.environ["gpt4-model_engine"]
            llm_temperature = os.environ["gpt4-llm_temperature"] 
            
        except Exception as e:
            # set your config
            api_key = ""
            api_base_url= ""
            model_name = ""
            model_engine = os.environ["model_engine"]
            model_engine = ""
            embed_model = ""
            embed_model_path = ""
            #logger.error(f"{e}")
            
        
        logger.info(f'os.environ["model_name"] is {os.environ["model_name"]}, llm_model is {llm_model}, llm_config is {llm_config}')

        if ( llm_model == 'gpt-4' or llm_model == 'gpt_4'):
            logger.info("强制调用gpt-4 的配置")
            llm_config = LLMConfig(
                model_name=model_name, model_engine=model_engine, 
                api_key=api_key, api_base_url=api_base_url, 
                temperature=llm_temperature)
        elif llm_model == None:
                logger.info("llm_config 未输入， 强制调用默认大模型配置")
                llm_config = LLMConfig(
                    model_name      =os.environ["model_name"], 
                    model_engine    =os.environ["model_engine"], 
                    api_key         =os.environ["OPENAI_API_KEY"], 
                    api_base_url    =os.environ["API_BASE_URL"], 
                    temperature     =os.environ["llm_temperature"] )
            
        # elif ( llm_model == 'qwen-72B' or llm_model == 'Qwen2_72B_Instruct_OpsGPT'):
        #     logger.info("强制调用 Qwen2_72B_Instruct_OpsGPT 的配置")
        #     llm_config = LLMConfig(
        #         model_name      =os.environ["qwen-model_name"], 
        #         model_engine    =os.environ["qwen-model_engine"], 
        #         api_key         =os.environ["qwen-OPENAI_API_KEY"], 
        #         api_base_url    =os.environ["qwen-API_BASE_URL"], 
        #         temperature     =os.environ["qwen-llm_temperature"] )
        else:
            logger.info("使用默认 llm_config 的配置") 
        
        logger.info(f'llm_config is {llm_config}')
        llm_model = getChatModelFromConfig(llm_config) if llm_config else None
        

        retry_times = 0
        while retry_times < MOST_RETRY_TIMES:
            try:
                aaa = llm_model(input_content)
                break
            except Exception as e:
                retry_times += 1
                time.sleep(random.randint(1, SLEEP_TIME_BEFORE_RETRY))
                print('retry_times is ',retry_times,'call llm error is ', e)

        return aaa
    
    return call_antgroup_llm(input_content, llm_model, stop, temperature,presence_penalty)



import string
import re


def remove_punctuation(text):
    # 定义中英文标点符号
    punctuations = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~，。、【】《》？；：‘’“”…！￥（）——+·"""
    # 使用正则表达式替换掉标点符号
    text_without_punctuation = re.sub(f"[{re.escape(punctuations)}]", "", text)
    return text_without_punctuation


def extract_final_result(input_string, special_str = "最终结果为：" ):
    # 从一个字符串中，截取最后一次出现special_str 之后的内容
    index = input_string.rfind(special_str)
    if index == -1:
        return "Substring not found"
    else:
        jiequ_str = input_string[index + len(special_str):]
        jiequ_str = remove_punctuation(jiequ_str)
        for char in jiequ_str:
            if char.isupper():
                return char
        return "Substring not found"

        #return  jiequ_str

def robust_call_llm(prompt_temp, llm_model = None, stop = None, temperature = 0, presence_penalty = 0):
    if os.environ['operation_mode'] != 'antcode':
        res = call_llm(input_content = prompt_temp, llm_model = llm_model ,  stop = stop,temperature=temperature, presence_penalty=presence_penalty)
        return res
    else:
        try:
            print('gpt_4')
            res = call_llm(input_content = prompt_temp, llm_model = 'gpt_4',  stop = stop,temperature=temperature, presence_penalty=presence_penalty)
        except:
            print('Qwen2_72B_Instruct_OpsGPT')
            res = call_llm(input_content = prompt_temp, llm_model = 'Qwen2_72B_Instruct_OpsGPT',stop = stop, temperature=temperature,presence_penalty=presence_penalty)
        return res


if __name__ == '__main__':
    import test_config
    res = call_llm("你的名字是什么？")
    print(res)
