import os, sys
from loguru import logger
import json

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



from muagent.db_handler import LocalFaissHandler
from muagent.schemas.db import DBConfig, GBConfig, VBConfig, TBConfig
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.models import ModelConfig
import numpy as np

llm_config = LLMConfig(
    model_name=model_name, model_engine=model_engine, api_key=api_key,  api_base_url=api_base_url, temperature=0.3,
)

model_configs = json.loads(os.environ["MODEL_CONFIGS"])
model_type = "ollama_embedding"
model_config = model_configs[model_type]

embed_config = ModelConfig(
    config_name="model_test",
    model_type=model_type,
    model_name=model_config["model_name"],
    api_key=model_config["api_key"],
)
# 
import random
embedding = [random.random() for _ in range(768)]
print(len(embedding), np.mean(embedding))


vb_config = VBConfig(vb_type="LocalFaissHandler")
vb = LocalFaissHandler(embed_config, vb_config)

vb.create_vs("shanshi")
vector = np.array([embedding], dtype=np.float32)
scores, indices = vb.search_index.index.search(vector, 20)
print(scores)
