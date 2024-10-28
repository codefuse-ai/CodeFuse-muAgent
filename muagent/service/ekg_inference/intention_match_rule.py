import re
import Levenshtein
from muagent.schemas.common import GNode


class MatchRule:
    @classmethod
    def edit_distance(cls, node: GNode, pattern=None, **kwargs):
        if len(kwargs) == 0:
            return -float('inf')

        s = list(kwargs.values())[0]
        desc: str = node.attributes.get('description', '')

        if pattern is None:
            return -Levenshtein.distance(desc, s)

        desc_list = re.findall(pattern, desc)
        if not desc_list:
            return -float('inf')

        return max([-Levenshtein.distance(x, s) for x in desc_list])
    
    @classmethod
    def edit_distance_integer(cls, node: GNode, **kwargs):
        return cls.edit_distance(node, pattern='\d+', **kwargs)
