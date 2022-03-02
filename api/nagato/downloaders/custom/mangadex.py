from nagato.downloaders import custom
from nagato.downloaders.base import BaseDownloader
from nagato.utils.errors import ApiUrlError, ApiNotFoundError
from nagato.utils.request import RequesterBuilder

import re
from requests import Response
from datetime import datetime, timezone

CDN_URL = 'https://uploads.mangadex.org'
API_URL = 'https://api.mangadex.org'
API_MANGA_URL = f"{API_URL}/manga"
API_CHAPTER_URL = f"{API_URL}/chapter"
API_ATHOME_URL = f"{API_URL}/at-home/server"

manga_page_reg = re.compile(r'https://mangadex\.org/title/([a-z0-9\-]+)/.*')
chapter_page_reg = re.compile(r'https://mangadex\.org/chapter/([a-z0-9\-]+)(?:/[0-9]+)?')


@custom.register(site='mangadex.org')
class MangadexDownloader(BaseDownloader) :
	
	def __init__(self, site: str, config) :
		super().__init__(site, config)
		self._lang = config['language.filter']
		self._builder = RequesterBuilder.get()
		self._requester = self._builder.build()

	def getChapterId(self, url) :
		m = chapter_page_reg.fullmatch(url)
		if m is not None :
			return m.group(1)
		raise ApiUrlError(f"URL {url} does not link to any manga on the Mangadex website")
	
	def _findRelationshipId(self, relationships, type) :
		for elt in relationships :
			if elt['type'] == type :
				return True, elt['id']
		return False, None
	
	def _findRelationshipAttributes(self, relationships, type) :
		for elt in relationships :
			if elt['type'] == type :
				return True, elt['id'], elt['attributes']
		return False, None, None
	
	def _findRelationships(self, relationships, type) :
		return {elt['id']: elt['attributes'] for elt in relationships if elt['type'] == type}

	def getMangaForChapter(self, chapter_id) :
		data = self._requester.requestJson(f"{API_CHAPTER_URL}/{chapter_id}")['data']
		found, res = self._findRelationshipId(data['relationships'], 'manga')
		if found :
			return res
		raise ApiNotFoundError(f"No manga found for chapter {chapter_id}")

	def getMangaId(self, url):
		m = manga_page_reg.fullmatch(url)
		if m is not None :
			return m.group(1)
		try:
			chapter_id = self.getChapterId(url)
			return self.getMangaForChapter(chapter_id)
		except ApiUrlError or ApiNotFoundError :
			raise ApiUrlError(f"URL {url} does not link to any manga nor chapter on the Mangadex website")

	def getMangaInfo(self, manga_id) :
		data = self._requester.requestJson(f"{API_MANGA_URL}/{manga_id}?includes[]=author&includes[]=artist")['data']
		attributes = data['attributes']
		data_title = attributes['title'].values()
		title = next(iter(data_title)) if len(data_title) > 0 else 'Untitled'
		data_desc = attributes['description']
		desc = None
		if self._lang in data_desc :
			desc = data_desc[self._lang]
		elif len(data_desc) > 0 :
			desc = next(iter(data_desc.values()))
		authors = [{'id': author_id, 'name': attributes['name']} for author_id, attributes 
					in self._findRelationships(data['relationships'], 'author').items()]
		artists = [{'id': artist_id, 'name': attributes['name']} for artist_id, attributes 
					in self._findRelationships(data['relationships'], 'artist').items()]
		genres = []
		tags = []
		for t in attributes['tags'] :
			(genres if t['attributes']['group'] == 'genre' else tags).append(t['attributes']['name']['en'])
		return {
			'id': manga_id,
			'site': self._site,
			'title': title,
			'alt_titles': attributes['altTitles'],
			'description': desc,
			'authors': authors,
			'artists': artists,
			'genres': genres,
			'tags': tags,
			'lang': attributes['originalLanguage'],
			'links': attributes['links'],
			'date': {
				'day': None, 
				'month': None, 
				'year': attributes['year']
			},
			'rating': attributes['contentRating'],
			'status': attributes['status']
		}
	
	def getCover(self, manga_id) -> bytes:
		data = self._requester.requestJson(f"{API_MANGA_URL}/{manga_id}?includes[]=cover_art")['data']
		found, _, attributes = self._findRelationshipAttributes(data['relationships'], 'cover_art')
		if not found :
			return None
		cover_file = attributes['fileName']
		return self._requester.requestBinary(f"{CDN_URL}/covers/{manga_id}/{cover_file}")

	def _formatChapter(self, chapter_data) :
		attributes = chapter_data['attributes']
		volume = attributes['volume']
		if volume is not None :
			volume = int(volume)
		chapter = attributes['chapter']
		chapter = float(chapter)
		if int(chapter) == chapter :
			chapter = int(chapter)
		team_data = self._findRelationshipAttributes(chapter_data['relationships'], 'scanlation_group')
		team = None
		if team_data[0] :
			team = {
				'id': team_data[1],
				'name': team_data[2]['name'],
				'site': team_data[2]['website']
			}
		dts = attributes['updatedAt']
		dts = dts[:-3] + dts[-2:]
		dt = datetime.strptime(dts, '%Y-%m-%dT%H:%M:%S%z')
		dt.astimezone(timezone.utc)
		dtf = dt.strftime('%Y %m %d').split(' ')
		return chapter_data['id'], {
			'volume': volume,
			'chapter': chapter,
			'title': attributes['title'],
			'lang': attributes['translatedLanguage'],
			'pages': attributes['pages'],
			'team': team,
			'date': {
				'day': dtf[2], 
				'month': dtf[1], 
				'year': dtf[0]
			}
		}
	
	def _chaptersFromApi(self, manga_id) :
		first_url = f"{API_MANGA_URL}/{manga_id}/feed?translatedLanguage[]={self._lang}&includes[]=scanlation_group&offset=0"
		def agregator(response: Response, prev_res, state: dict) -> tuple :
			data = response.json()
			if prev_res is None :
				res = {}
				state['limit'] = data['limit']
				state['total'] = data['total']
				state['nb_req'] = 1
			else :
				state['nb_req'] += 1
				res = prev_res
			for chapter_data in data['data'] :
				chapter_id, chapter = self._formatChapter(chapter_data)
				res[chapter_id] = chapter
			next_url = None
			if state['nb_req'] * state['limit'] < state['total'] :
				next_url = f"{API_MANGA_URL}/{manga_id}/feed?translatedLanguage[]={self._lang}&includes[]=scanlation_group&offset={state['nb_req'] * state['limit']}"
			return res, next_url
		return first_url, agregator

	def getChapters(self, manga_id) :
		url, agregator = self._chaptersFromApi(manga_id)
		return self._requester.requestAgregate(url, agregator)
	
	def getChapterInfo(self, chapter_id): 
		data = self._requester.requestJson(f"{API_CHAPTER_URL}/{chapter_id}?includes[]=scanlation_group")['data']
		chapter = self._formatChapter(data)[1]
		chapter['id'] = chapter_id
		chapter['manga'] = self._findRelationshipId(data['relationships'], 'manga')[1]
		return chapter
	
	def getChapterUrls(self, chapter_id) -> "tuple[list[str], RequesterBuilder]" :
		data = self._requester.requestJson(f"{API_ATHOME_URL}/{chapter_id}")
		base_url = data['baseUrl']
		chapter = data['chapter']
		hash = chapter['hash']
		return [f"{base_url}/data/{hash}/{image}" for image in chapter['data']], self._builder

