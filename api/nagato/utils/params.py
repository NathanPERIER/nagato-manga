from nagato.downloaders import downloaderForSite, downloaderForURL, siteForURL
from nagato.downloaders.base import BaseDownloader
from nagato.utils.compression import binary_patterns
from nagato.utils.errors import ApiFormatError, ApiQueryError

import logging
from functools import wraps
from flask import request

logger = logging.getLogger(__name__)


image_mime_types = {
	'png': 'image/png',
	'jpg': 'image/jpeg',
	'gif': 'image/gif',
	'webp': 'image/webp',
	'tiff': 'image/tiff',
	'bmp': 'image/bmp'
}

def imageMimeType(image: bytes) :
	for pattern, extension in binary_patterns.items() :
		if image.startswith(pattern) :
			return image_mime_types[extension]
	logger.warning(f"Could not determine the type of an image with binary prefix {image[:10]}")


def getMangaFromArgs() -> "tuple[BaseDownloader,str]" :
	if 'url' in request.args :
		url = request.args['url']
		dl = downloaderForURL(url)
		manga_id = dl.getMangaId(url)
	elif 'site' in request.args and 'id' in request.args :
		dl = downloaderForSite(request.args['site'])
		manga_id = request.args['id']
	else :
		raise ApiQueryError('Request is missing the URL parameter or the Site and ID parameters')
	return dl, manga_id

def mangaFromArgs(f) :
	@wraps(f)
	def wrapper(**kwargs) :
		return f(*getMangaFromArgs(), **kwargs)
	return wrapper

def getChapterFromArgs() -> "tuple[BaseDownloader,str]" :
	if 'url' in request.args :
		url = request.args['url']
		dl = downloaderForURL(url)
		chapter_id = dl.getChapterId(url)
	elif 'site' in request.args and 'id' in request.args :
		dl = downloaderForSite(request.args['site'])
		chapter_id = request.args['id']
	else :
		raise ApiQueryError('Request is missing the URL parameter or the Site and ID parameters')
	return dl, chapter_id

def chapterFromArgs(f) :
	@wraps(f)
	def wrapper(**kwargs) :
		return f(*getChapterFromArgs(), **kwargs)
	return wrapper

def getChapterRefs(data) :
	res = {
		site: {
			'downloader': downloaderForSite(site), 
			'chapters': set(chapters)
		}
		for site, chapters in data['sites'].items()
	} if 'sites' in data else {}
	if 'urls' in data :
		for url in data['urls'] :
			site = siteForURL(url)
			if site not in res :
				res[site] = {
					'downloader': downloaderForSite(site),
					'chapters': set()
				}
			dl: BaseDownloader = res[site]['downloader']
			res[site]['chapters'].add(dl.getChapterId(url))
	return res

def chaptersFromContent(f) :
	@wraps(f)
	def wrapper(**kwargs) :
		data = request.get_json(silent=True)
		if data is None :
			raise ApiFormatError('Content of request is not well-formed JSON')
		return f(getChapterRefs(data), **kwargs)
	return wrapper