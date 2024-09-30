from muagent.llm_models.openai_model import OllamaModel, OpenAILLMModel
import openai, os
from guidance import models, gen , select
from guidance import user, system, assistant, instruction
from guidance import one_or_more, zero_or_more
import guidance

class LLMConfig:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.temperature = 0.8
        self.stop = None
os.environ["OPENAI_API_KEY"] = "sk-xx"

llm_config = LLMConfig(model_name='gpt-3.5-turbo',
)
openai_model =  OpenAILLMModel(llm_config=llm_config)

prompt = "法国的首都是巴黎吗\n\n#### Response Output Format:\n**判断:**给出结论：是/不是"
response = openai_model(prompt)
print(response)

prompt = "把大象塞进冰柜，首先要做什么\n\n#### Response Output Format:\n**Action:**说明下一步要采取的行为"
response = openai_model(prompt)
print(response)
