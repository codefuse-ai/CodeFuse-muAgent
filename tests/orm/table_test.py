import os
from loguru import logger
os.environ["do_create_dir"] = "1"

# from muagent.orm import create_tables
from muagent.db_handler import create_tables


# use to test, don't create some directory
create_tables()