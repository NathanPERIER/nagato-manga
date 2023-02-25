
from ..dataobj import DataObject
from nagato.utils.json import Json

from enum import Enum


class DataEnum(Enum, DataObject) :
    
	def toJson(self) -> Json:
		return self.name()