
from abc import ABC
from typing import Union, Sequence, Mapping
# TODO TypeAlias available in Python 3.10


class DataObject(ABC) :
    
	def toJson(self) -> "RedExtJson" :
		return self.__dict__


# Extended JSON, including the `DataObject`
ExtJsonLiteral = Union[None, bool, int, float, str, DataObject]
ExtJsonMap     = Mapping[str, ExtJsonLiteral]
ExtJsonList    = Sequence[ExtJsonLiteral]
ExtJson        = Union[ExtJsonLiteral, ExtJsonMap, ExtJsonList]

# Extended JSON but with no root `DataObject` ("Reduced Extended Json")
RedExtJson = Union[None, bool, int, float, str, ExtJsonMap, ExtJsonList]
