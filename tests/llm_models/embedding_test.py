from loguru import logger
import os, sys
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(src_dir)
try:
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


src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)

from muagent.models import get_model
from muagent.schemas.models import ModelConfig
import json

model_configs = json.loads(os.environ["MODEL_CONFIGS"])

for model_type in model_configs.keys():
    if "_embedding" not in model_type: continue
    model_config = model_configs[model_type]
    embed_config = ModelConfig(
        config_name="model_test",
        model_type=model_type,
        model_name=model_config["model_name"],
        api_key=model_config["api_key"],
    )

    model = get_model(embed_config)


    print(model_type, model_config["model_name"], len(model.embed_query("hello")))