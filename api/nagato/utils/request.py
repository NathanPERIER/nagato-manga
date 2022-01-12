from nagato.utils.errors import ApiNotFoundError, ApiQueryError

import requests

def get(url) :
	res = requests.get(url)
	if res.ok :
		return res
	elif res.status_code == 404 :
		raise ApiNotFoundError(f"Could not find resource at {url}")
	else :
		raise ApiQueryError(f"Request to {url} yielded return code {res.status_code} {res.reason}")

def getBinary(url) :
	return get(url).content

def getJson(url) :
	return get(url).json()