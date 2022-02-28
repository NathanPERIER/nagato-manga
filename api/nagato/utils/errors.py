from flask import Flask


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


def setHandlers(app: Flask) :
	@app.errorhandler(ApiNotFoundError)
	def handle_not_found(e) :
		return str(e), 404
	
	@app.errorhandler(ApiFormatError)
	def handle_bad_format(e) :
		return str(e), 400
	
	@app.errorhandler(ApiError)
	def handle_generic(e) :
		return str(e), 500
