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
	
	def __init__(self, verb, headers={}, handlers={}, ceh=None, timeout=None) :
		self._verb = verb
		self._headers = headers
		self._handlers = handlers
		self._connectionErrorHandle = ceh if ceh is not None else Requester.defaultConnectionErrorHandle
		self._timeout = timeout
	
	def defaultConnectionErrorHandle(error, _) :
		raise ApiQueryError(error)

	def _request(self, url) :
		return requests.request(self._verb, url, headers=self._headers, timeout=self._timeout)

	def _handleRequest(self, url, delay=0) -> requests.Response :
		if delay > 0 :
			sleep(delay)
		keep_going = True
		nb_attempts = 0
		while keep_going :
			nb_attempts += 1
			logging.info(f"Request to \"{url}\"")
			try :
				res = self._request(url)
				if res.ok :
					return res
				logger.warning(f"Request n°{nb_attempts} to {url} failed with return code {res.status_code} {res.reason} : {res.text}")
				if res.status_code in self._handlers :
					keep_going = self._handlers[res.status_code](res, nb_attempts)
				elif res.status_code == 404 :
					raise ApiNotFoundError(f"Could not find resource at {url}")
				else :
					raise ApiQueryError(f"Request to {url} failed with return code {res.status_code} {res.reason}")
			except ConnectionError as e :
				logger.warning(f"Request n°{nb_attempts} to {url} failed with error of type {type(e).__name__}")
				keep_going = self._connectionErrorHandle(e, nb_attempts)
		raise ApiQueryError(f"Request to {url} failed after {nb_attempts} attempts with return code {res.status_code} {res.reason}")
	
	def requestMap(self, url, mapper, cache=True, delay=0) :
		if cache :
			res = _request_cache.get(url)
			if res is not None :
				return res
		with self._handleRequest(url, delay) as response :
			res = mapper(response)
		if cache :
			_request_cache.add(url, res)
		return res

	def requestBinary(self, url, cache=False, delay=0) -> bytes :
		return self.requestMap(url, lambda r : r.content, cache, delay)
	
	def requestJson(self, url, cache=True, delay=0) :
		return self.requestMap(url, lambda r : r.json(), cache, delay)
	
	def requestAgregate(self, url, agregator, cache=True, delay=0) :
		if cache :
			res = _request_cache.get(url)
			if res is not None :
				return res
		res = None
		next_url = url
		state = {}
		visited = [url]
		while next_url is not None :
			with self._handleRequest(next_url, delay) as response :
				res, next_url = agregator(response, res, state)
			if next_url is not None :
				if next_url in visited :
					raise ApiQueryError(f"Loop detected in agregation request to url {url} with state {state}")
				logger.info('Request redirected to %d (redirection n°%d)', next_url, len(visited))
				visited.append(next_url)
		if cache :
			_request_cache.add(url, res)
		return res
	
	def __enter__(self) :
		return self
	
	def __exit__(self, exc_type, exc_value, tb) :
		if exc_type is not None :
			return False

	
class SessionRequester(Requester) :

	def __init__(self, verb, headers={}, handlers={}, ceh=None, timeout=None) :
		super().__init__(verb, headers, handlers, ceh, timeout)
		self._session = requests.session()

	def _request(self, url) :
		return self._session.request(self._verb, url, headers=self._headers)
	
	def __exit__(self, exc_type, exc_value, tb) :
		self._session.close()
		return super().__exit__(exc_type, exc_value, tb)


class RequesterNoCache(Requester) :

	def __init__(self, verb, headers={}, handlers={}, ceh=None, timeout=None) :
		super().__init__(verb, headers, handlers, ceh, timeout)
	
	def requestMap(self, url, mapper, cache=False, delay=0) :
		with self._handleRequest(url, delay) as response :
			return mapper(response)
	
	def requestAgregate(self, url, agregator, cache=False, delay=0) :
		res = None
		next_url = url
		visited = [url]
		state = {}
		while next_url is not None :
			with self._handleRequest(next_url, delay) as response :
				res, next_url = agregator(response, res, state)
			if next_url is not None :
				if next_url in visited :
					raise ApiQueryError(f"Loop detected in agregation request to url {url} with state {state}")
				logger.info('Request redirected to %d (redirection n°%d)', next_url, len(visited))
				visited.append(next_url)
		return res


class SessionRequesterNoCache(RequesterNoCache) :

	def __init__(self, verb, headers={}, handlers={}, ceh=None, timeout=None) :
		super().__init__(verb, headers, handlers, ceh, timeout)
		self._session = requests.session()

	def _request(self, url) :
		return self._session.request(self._verb, url, headers=self._headers)
	
	def __exit__(self, exc_type, exc_value, tb) :
		self._session.close()
		return super().__exit__(exc_type, exc_value, tb)


class RequesterBuilder :

	def __init__(self, verb) :
		self._verb = verb
		self._headers = {}
		self._handlers = {}
		self._connectionErrorHandler = None
		self._timeout = (3.05, 5)
	
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

	def head() :
		return RequesterBuilder('HEAD')
	
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
	
	def onConnectionError(self, handler) :
		self._connectionErrorHandler = handler
	
	def setTimeout(self, timeout) :
		self._timeout = timeout

	def build(self) -> Requester :
		if _request_cache_maxlen > 0 :
			return Requester(self._verb, self._headers, self._handlers, self._connectionErrorHandler, self._timeout)
		return RequesterNoCache(self._verb, self._headers, self._handlers, self._connectionErrorHandler, self._timeout)

	def session(self) -> Requester :
		if _request_cache_maxlen > 0 :
			return SessionRequester(self._verb, self._headers, self._handlers, self._connectionErrorHandler, self._timeout)
		return SessionRequesterNoCache(self._verb, self._headers, self._handlers, self._connectionErrorHandler, self._timeout)

