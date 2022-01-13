from nagato.downloaders.base import BaseDownloader
from nagato.downloaders.custom import custom_downloaders
from nagato.utils.errors import ApiNotFoundError
import re

scheme_reg = re.compile(r'[a-zA-Z][a-zA-Z0-9+-.]*://(.*)')

available_downloaders = {}

def instanciate_downloaders() :
	for site, downloader_class in sorted(custom_downloaders.items(), key = lambda e : len(e[0]), reverse=True) :
		available_downloaders[site] = downloader_class()


def listSites() :
	return list(available_downloaders.keys())


def siteForURL(url) -> str :
	m = scheme_reg.fullmatch(url)
	noscheme = m.group(1) if m is not None else url
	for site in available_downloaders :
		if noscheme.startswith(site) :
			return site
	return None

def downloaderForURL(url) -> BaseDownloader :
	m = scheme_reg.fullmatch(url)
	noscheme = m.group(1) if m is not None else url
	for site, downloader in available_downloaders.items() :
		if noscheme.startswith(site) :
			return downloader
	raise ApiNotFoundError(f"No downloader found for URL \"{url}\"")

def downloaderForSite(site) -> BaseDownloader :
	if site in available_downloaders :
		return available_downloaders[site]
	raise ApiNotFoundError(f"No downloader found for site \"{site}\"")

