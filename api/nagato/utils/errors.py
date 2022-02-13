from flask import Response
from functools import wraps


class ApiError(Exception) :
	def __init__(self, message) :
		super().__init__(message)


class ApiNotFoundError(ApiError) :
	def __init__(self, message) :
		super().__init__(message)


class ApiQueryError(ApiError) :
	def __init__(self, message) :
		super().__init__(message)


class ApiFormatError(ApiError) :
	def __init__(self, message) :
		super().__init__(message)

class ApiUrlError(ApiFormatError) :
	def __init__(self, message) :
		super().__init__(message)


class ApiConfigurationError(ApiError) :
	def __init__(self, message) :
		super().__init__(message)


def wrap(route) :
	@wraps(route)
	def wrapper() :
		try :
			response = route()
		except ApiNotFoundError as e :
			return Response(str(e), 404)
		except ApiFormatError as e :
			return Response(str(e), 400)
		except ApiError as e :
			return Response(str(e), 500)
		return response
	return wrapper
