
from requests import Request, Response

from typing import Callable


HttpHandler = Callable[[Request, Response],bool]
ConnectionErrorHandler = Callable[[ConnectionError,int],bool]