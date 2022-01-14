from nagato.utils.errors import ApiNotFoundError, ApiQueryError
from nagato.utils import config

import logging
import requests
from collections import deque
from time import sleep

logger = logging.getLogger(__name__)

_request_cache_maxlen = config.getApiConf('requests.cache.maxlen')


class HttpCache :
	
	def __init__(self, maxlen) :
		self._maxlen = maxlen
		self._saved_requests = {}
		self._urls = deque(maxlen = maxlen)
	
	def get(self, url) :
		if url in self._saved_requests :
			self._urls.remove(url)
			self._urls.append(url)
			return self._saved_requests[url]
		return None
	
	def add(self, url, response) :
		if len(self._saved_requests) == self._maxlen :
			oldest = self._urls.popleft()
			del self._saved_requests[oldest]
		self._saved_requests[url] = response
		self._urls.append(url)


if _request_cache_maxlen > 0 :
	_request_cache = HttpCache(_request_cache_maxlen)
else :
	_request_cache = None


class Requester :
	
	def __init__(self, verb, headers={}, handlers={}) :
		self._verb = verb
		self._headers = headers
		self._handlers = handlers

	def _requestURL(self, url, delay=0) -> requests.Response :
		if delay > 0 :
			sleep(delay)
		keep_going = True
		nb_attempts = 0
		while keep_going :
			nb_attempts += 1
			res = requests.request(self._verb, url, headers=self._headers)
			if res.ok :
				return res
			logger.warning(f"Request n°{nb_attempts} to {url} failed with return code {res.status_code} {res.reason} : {res.text}")
			if res.status_code in self._handlers :
				keep_going = self._handlers[res.status_code]()
			elif res.status_code == 404 :
				raise ApiNotFoundError(f"Could not find resource at {url}")
			else :
				raise ApiQueryError(f"Request to {url} failed with return code {res.status_code} {res.reason}")
		raise ApiQueryError(f"Request to {url} failed after {nb_attempts} attempts with return code {res.status_code} {res.reason}")
	
	def requestMap(self, url, mapper, cache=True) :
		if cache :
			res = _request_cache.get(url)
			if res is not None :
				return res
		res = mapper(self._requestURL(url))
		if cache :
			_request_cache.add(url, res)
		return res

	def requestBinary(self, url, cache=False) -> bytes :
		return self.requestMap(url, lambda r : r.content, cache)
	
	def requestJson(self, url, cache=True) :
		return self.requestMap(url, lambda r : r.json(), cache)


class RequesterNoCache(Requester) :

	def __init__(self, verb, headers={}, handlers={}) :
		super().__init__(verb, headers, handlers)
	
	def requestMap(self, url, mapper, cache=False) :
		return mapper(self._requestURL(url))


class RequesterBuilder :

	def __init__(self, verb) :
		self._verb = verb
		self._headers = {}
		self._handlers = {}
	
	def get() :
		return RequesterBuilder('GET')
	
	def post() :
		return RequesterBuilder('POST') # TODO maybe method to add content for the post at some point
	
	def put() :
		return RequesterBuilder('PUT')

	def patch() :
		return RequesterBuilder('PATCH')
	
	def delete() :
		return RequesterBuilder('DELETE')
	
	def setHeader(self, header, value) :
		self._headers[header] = value
		return self
	
	def removeHeader(self, header) :
		if header in self._headers :
			del self._headers[header]
	
	def setHandler(self, error_code, handler) :
		self._handlers[error_code] = handler
	
	def removeHandler(self, error_code) :
		if error_code in self._handlers :
			del self._handlers[error_code]

	def build(self) -> Requester :
		if _request_cache_maxlen > 0 :
			return Requester(self._verb, self._headers, self._handlers)
		return RequesterNoCache(self._verb, self._headers, self._handlers)

