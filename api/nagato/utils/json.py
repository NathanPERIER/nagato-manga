
from nagato.models import DataObject

import json

from typing import Union, Sequence, Mapping
# TODO TypeAlias available in Python 3.10

# Deserialised JSON
JsonLiteral = Union[None, bool, int, float, str]
JsonMap     = Mapping[str, JsonLiteral]
JsonList    = Sequence[JsonLiteral]
Json        = Union[JsonLiteral, JsonMap, JsonList]

# Extended JSON, including the `DataObject`
ExtJsonLiteral = Union[None, bool, int, float, str, DataObject]
ExtJsonMap     = Mapping[str, ExtJsonLiteral]
ExtJsonList    = Sequence[ExtJsonLiteral]
ExtJson        = Union[ExtJsonLiteral, ExtJsonMap, ExtJsonList]


def loadJson(path: str) -> Json :
	with open(path, 'r') as f :
		return json.load(f)

# TODO with a custom serialiser for DataObjects
# def dumpJson(data: ExtJson) -> str :
# def saveJson(data: ExtJson, path: str) :
