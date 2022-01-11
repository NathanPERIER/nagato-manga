from nagato.downloaders import custom
from nagato.downloaders.base import BaseDownloader
from nagato.utils.errors import ApiUrlError, ApiNotFoundError
from nagato.utils import request

import re

CDN_URL = 'https://uploads.mangadex.org'
API_URL = 'https://api.mangadex.org'
API_MANGA_URL = f"{API_URL}/manga"
API_CHAPTER_URL = f"{API_URL}/chapter"
API_ATHOME_URL = f"{API_URL}/at-home/server"

manga_page_reg = re.compile(r'https://mangadex\.org/title/([a-z0-9\-]+)/.*')
chapter_page_reg = re.compile(r'https://mangadex\.org/chapter/([a-z0-9\-]+)(?:/[0-9]+)?')

@custom.register(site='mangadex.org')
class MangadexDownloader(BaseDownloader) :
	
	def __init__(self) :
		super().__init__()

	def getChapterId(self, url) :
		m = chapter_page_reg.fullmatch(url)
		if m is not None :
			return m.group(1)
		raise ApiUrlError(f"URL {url} does not link to any manga on the Mangadex website")
	
	def getMangaForChapter(self, chapter_id) :
		data = request.get(f"{API_CHAPTER_URL}/{chapter_id}").json()['data']['relationships']
		for elt in data :
			if elt['type'] == 'manga' :
				return elt['id']
		raise ApiNotFoundError(f"No manga found for chapter {chapter_id}")

	def getMangaId(self, url):
		m = manga_page_reg.fullmatch(url)
		if m is not None :
			return m.group(1)
		try:
			chapter_id = self.getChapterId(url)
			return self.getMangaForChapter(chapter_id)
		except ApiUrlError :
			raise ApiUrlError(f"URL {url} does not link to any manga nor chapter on the Mangadex website")

	def getMangaInfo(self, manga_id):
		data = request.get(f"{API_MANGA_URL}/{manga_id}").json()
		raise NotImplementedError

	def formatChapter(self, chapter_data) :
		attributes = chapter_data['attributes']
		return {
			'id': chapter_data['id'],
			'volume': attributes['volume'],
			'chapter': attributes['chapter'],
			'title': attributes['title']
		}

	def getChapters(self, manga_id) :
		data = request.get(f"{API_MANGA_URL}/{manga_id}/feed?translatedLanguage[]=en&offset=0").json()
		limit = data['limit']
		total = data['total']
		nb_req = 1
		res = [self.formatChapter(chap) for chap in data['data']]
		while nb_req * limit < total :
			data = request.get(f"{API_MANGA_URL}/{manga_id}/feed?translatedLanguage[]=en&offset={nb_req * limit}").json()
			res.extend([self.formatChapter(chap) for chap in data['data']])
			nb_req += 1
		return res
	
	def getChapterInfo(self, chapter_id): 
		raise NotImplementedError
	
	def downloadChapter(self, chapter_id) :
		data = request.get(f"{API_ATHOME_URL}/{chapter_id}").json()['chapter']
		hash = data['hash']
		images = data['data']
		return [request.getBinary(f"{CDN_URL}/data/{hash}/{image}") for image in images]


	


