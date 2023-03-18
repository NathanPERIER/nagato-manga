
from nagato.models.dataobj import DataObject, ExtJson, RedExtJson

import json

from typing import Union, Sequence, Mapping, Any
# TODO TypeAlias available in Python 3.10

# Deserialised JSON
JsonLiteral = Union[None, bool, int, float, str]
JsonMap     = Mapping[str, JsonLiteral]
JsonList    = Sequence[JsonLiteral]
Json        = Union[JsonLiteral, JsonMap, JsonList]


def loadJson(path: str) -> Json :
	with open(path, 'r') as f :
		return json.load(f)


class DataObjectEncoder(json.JSONEncoder) :

	def default(self, o: Any) -> Any :
		if issubclass(type(o), DataObject) :
			return o.toJson()
		return super().default(o)

def dumpJson(data: ExtJson) -> str :
	json.dumps(data, cls=DataObjectEncoder)

def saveJson(data: ExtJson, path: str) :
	with open(path, 'w') as f :
		json.dump(data, f, cls=DataObjectEncoder)
