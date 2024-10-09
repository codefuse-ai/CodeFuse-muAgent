from muagent.llm_models.openai_model import OllamaModel
import ollama

class LLMConfig:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.temperature = 0.8
        self.stop = None

llm_config = LLMConfig(model_name='qwen2:0.5b')
# llm_config = LLMConfig(model_name='qwen2:7b')

ollama_model = OllamaModel(llm_config=llm_config)

prompt = "你好，请你做一个自我介绍"
response = ollama_model.unit_test(prompt)
print(response)
print()

prompt = "法国的首都是哪里"
response = ollama_model.unit_test(prompt)
print(response)
print()

prompt = "如何看待大模型对程序员的意义"
response = ollama_model.unit_test(prompt)
print(response)