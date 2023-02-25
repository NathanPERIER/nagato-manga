
from .dataobj import DataObject

from typing import Optional, Final

class Person(DataObject) :
    
	def __init__(self, identifier: str, name: str) :
		self.identifier          = identifier
		self.name: Final[str]    = name
		self.link: Optional[str] = None
