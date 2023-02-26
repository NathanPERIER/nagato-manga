
import threading


class Mutex :
    
	def __init__(self) :
		self._lock = threading.Lock()
	
	def __enter__(self) -> "Mutex" :
		self._lock.acquire()
		return self

	def __exit__(self, exc_type, exc_value, tb) :
		self._lock.release()
		if exc_type is not None :
			# traceback.print_exception(exc_type, exc_value, tb)
			return False
