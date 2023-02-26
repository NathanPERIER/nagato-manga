
import threading


class Counter :
    
	def __init__(self) :
		self._current: int = 1
		self._mutex = threading.Lock()
	
	def next(self) -> int :
		self._mutex.acquire()
		res = self._current
		self._current += 1
		self._mutex.release()
		return res
