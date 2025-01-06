from enum import Enum
from typing import Union


class LogVerboseEnum(Enum):
    Log0Level = "0" # don't print log
    Log1Level = "1" # print level-1 log
    Log2Level = "2" # print level-2 log
    Log3Level = "3" # print level-3 log

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value.lower() == other.lower()
        if isinstance(other, LogVerboseEnum):
            return self.value == other.value
        return False

    def __ge__(self, other):
        if isinstance(other, LogVerboseEnum):
            return int(self.value) >= int(other.value)
        if isinstance(other, str):
            return int(self.value) >= int(other)
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, LogVerboseEnum):
            return int(self.value) <= int(other.value)
        if isinstance(other, str):
            return int(self.value) <= int(other)
        return NotImplemented
    
    @classmethod
    def ge(self, enum_value: 'LogVerboseEnum', other: Union[str, 'LogVerboseEnum']):
        return enum_value <= other
    
    @classmethod
    def le(self, enum_value: 'LogVerboseEnum', other: Union[str, 'LogVerboseEnum']):
        return enum_value <= other