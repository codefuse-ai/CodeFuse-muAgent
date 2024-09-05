from pydantic import BaseModel
from typing import List, Dict
from enum import Enum



class EKGIntentResp(BaseModel):
    intent_leaf_nodes: List[str]
    intent_nodes: List[str]

    