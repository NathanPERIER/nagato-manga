from nagato.downloaders.base import BaseDownloader
from nagato.downloaders.custom import custom_downloaders
from nagato.utils.errors import ApiNotFoundError
import re

scheme_reg = re.compile(r'[a-zA-Z][a-zA-Z0-9+-.]*://(.*)')

def forURL(url) -> BaseDownloader :
	m = scheme_reg.fullmatch(url)
	noscheme = m.group(1) if m is not None else url
	for site, downloader in custom_downloaders.items() :
		if noscheme.startswith(site) :
			return downloader
	raise ApiNotFoundError(f"No downloader found for URL \"{url}\"")

