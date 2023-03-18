
from nagato.utils.errors import ApiConfigurationError, ApiNotFoundError, ApiQueryError
from nagato.utils import config

import time
from collections import deque
from typing import MutableMapping, Tuple, Any

_request_cache_maxlen = config.getApiConf('requests.cache.maxlen')
_request_cache_threshold = config.getApiConf('requests.cache.threshold')


class HttpCache :
	"""
	Used for caching the responses of HTTP requests
	"""
	
	def __init__(self, maxlen: int, threshold: int) :
		self._maxlen = maxlen
		self._threshold = threshold
		self._saved_requests: MutableMapping[str,Tuple[Any,int]] = {}
		self._urls: deque[str] = deque(maxlen = maxlen)
	
	def checkValid(self, ts: int) -> bool :
		return ts - int(time.time()) < self._threshold

	def get(self, url) :
		if url in self._saved_requests :
			self._urls.remove(url)
			res, ts = self._saved_requests[url]
			if self.checkValid(ts) :
				self._urls.append(url)
				return res
			else :
				del self._saved_requests[url]
		return None
	
	def add(self, url: str, response: Any) :
		if len(self._saved_requests) == self._maxlen :
			oldest = self._urls.popleft()
			del self._saved_requests[oldest]
		self._saved_requests[url] = response, int(time.time())
		self._urls.append(url)

if _request_cache_threshold < 60 :
	raise ApiConfigurationError(f"The threshold for the request cache must be greater than a minute, but was set to {_request_cache_threshold} seconds")

if _request_cache_maxlen < 50 :
	raise ApiConfigurationError(f"The request cache size must be at least 50, but was set to {_request_cache_maxlen}")

request_cache = HttpCache(_request_cache_maxlen, _request_cache_threshold)
