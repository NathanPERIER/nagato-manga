
from .types import HttpHandler, ConnectionErrorHandler
from nagato.utils import config

from typing import Optional, Union, Tuple, MutableMapping

Number = Union[int,float]

class RequesterBuilder :
    
	def __init__(self) :
		self.delay: int = 0
		self.timeout: Tuple[Number,Number] = (
			config.getApiConf('requests.timeout.connect'),
			config.getApiConf('requests.timeout.read')
		)
		self.headers: MutableMapping[str,str] = {}
		self.handlers: MutableMapping[int,HttpHandler] = {}
		self.c_handler: Optional[ConnectionErrorHandler]
	
	def setDelay(self, delay: int) -> "RequesterBuilder" :
		self.delay = delay
		return self
	
	def setTimeout(self, connect: Number, read: Number) -> "RequesterBuilder" :
		self.delay = (connect, read)
		return self
	
	def setHeader(self, header: str, value: str) -> "RequesterBuilder" :
		self.headers[header] = value
		return self
	
	def onHttpError(self, code: int, handler: HttpHandler) -> "RequesterBuilder" :
		self.handlers[code] = handler
		return self
	
	def onConnectionError(self, handler: ConnectionErrorHandler) -> "RequesterBuilder" :
		self.c_handler = handler
		return self
	
	def build(self) :
		pass # TODO Requester

	def session(self) :
		pass # TODO SessionRequester


