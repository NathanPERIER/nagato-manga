
from abc import ABC

from nagato.utils.json import Json


class DataObject(ABC) :
    
	def toJson(self) -> Json :
		return self.__dict__
