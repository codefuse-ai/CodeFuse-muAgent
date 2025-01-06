import os
from loguru import logger

try:
    import os, sys
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
except Exception as e:
    # set your config
    logger.error(f"{e}")


src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)

from muagent import get_tool
from muagent.tools import toLangchainTools


tools = toLangchainTools([get_tool("Multiplier")])

print(get_tool("Multiplier").intput_to_json_schema())
print(get_tool("Multiplier").output_to_json_schema())
# tool run 测试
print(tools[0].func(1,2))