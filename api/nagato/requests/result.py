
import time
from typing import Any


class Result :
    
	def __init__(self, url: str, data: Any) :
		self.url = url
		self.data = data
		self.created = int(time.time())
		self.updated = self.created
	
	def update(self) :
		self.updated = int(time.time())
	
	def age(self) :
		return int(time.time()) - self.created
	