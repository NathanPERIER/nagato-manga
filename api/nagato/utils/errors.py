
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