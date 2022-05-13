from nagato.utils.errors import ApiQueryError, ApiUrlError
from nagato.utils.request import Requester, RequesterBuilder
from nagato.utils.config import getExtraConf
from nagato.downloaders import custom
from nagato.downloaders.base import BaseDownloader

import re
import bs4
import logging

logger = logging.getLogger(__name__)

MANGA_ID = 'one-piece'
MANGA_URL = 'https://www.japscan.ws/manga/one-piece/'
BASE_URL = 'https://www.japscan.ws/lecture-en-ligne/one-piece'
LAST_PACKED_VOLUME = 40

conf_translate = getExtraConf('translate', 'japscan')
conf_split = getExtraConf('split', 'japscan')

chapter_reg = re.compile(r'https://www\.japscan\.ws/lecture-en-ligne/one-piece/(\d+|volume-\d+)(?:/(?:(\d+).html)?)?')
volume_name_reg = re.compile(r'\s*Volume (\d+)(?:: (.*[^\s]))?\s*')
chapter_name_reg = re.compile(r'\s*One Piece (\d+(?:.\d)?) VF(?:: (.*[^\s]))?\s*')

months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

def readChaptersInDiv(div, nb_vol: int, title_vol: str, chapters: dict) :
	"""
	Utility function used to read chapters in a div
	"""
	links = div.select('a')
	spans = div.select('span')
	for a, span in zip(links, spans) :
		m = chapter_name_reg.fullmatch(a.text)
		date = span.text.split(' ')
		chapter_id: str = m.group(1)
		chapters[chapter_id] = {
			'id': chapter_id,
			'manga': MANGA_ID,
			'volume': nb_vol, 
			'volume_title': title_vol,
			'chapter': float(chapter_id) if '.' in chapter_id else int(chapter_id), 
			'title': m.group(2), 
			'lang': 'fr',
			'pages': None,
			'date': {
				'day': int(date[0]), 
				'month': months[date[1]], 
				'year': int(date[2])
			},
			'team': None
		}

def chapters_mapper(soup: bs4.BeautifulSoup) -> dict :
	tags = [x for x in soup.select_one('#chapters_list') if x != '\n'] # children of #chapters_list element
	titles = [t for t in tags if t.name == 'h4']                       # all the titles
	divs = [t for t in tags if t.name == 'div']                        # all the divs (constaining chapters)
	indep_chapters = None
	max_volume = 0
	res = {}
	# If we have a bunch of chapters that aren't in a volume, they will be at the beginning
	if len(divs) == len(titles)+1 :
		indep_chapters = divs[0]
		divs = divs[1:]
	# Then, we have an alternation of titles and chapters
	for h4, div in zip(titles, divs) :
		m = volume_name_reg.fullmatch(h4.select_one('span').text)
		volume = m.group(1)
		title_vol = m.group(2)
		nb_vol = int(volume)
		if nb_vol > max_volume :
			max_volume = nb_vol
		if nb_vol > LAST_PACKED_VOLUME :
			readChaptersInDiv(div, nb_vol, title_vol, res)
		else :
			numbers = [n for n, split in conf_split.items() if split['tome'] == nb_vol]
			for n in numbers : 
				res[n] = {
					'id': n,
					'manga': MANGA_ID,
					'volume': nb_vol, 
					'volume_title': title_vol,
					'chapter': int(n),
					'title': None, 
					'lang': 'fr',
					'pages': None,
					'date': {
						'day': 28, 
						'month': 3, 
						'year': 2014
					},
					'team': None
				}
	if indep_chapters is not None :
		readChaptersInDiv(indep_chapters, max_volume + 1, None, res)
	return res

def translateUrl(url) :
	"""
	Translates an URL "encoded" by Japscan into a URL that can be used to retrieve a page
	"""
	ext = url[-4:]
	url = url[21:-4]
	res = []
	for char in url :
		if char in conf_translate :
			char = conf_translate[char]
		else :
			logger.warning("UNKNOWN char %s in %s", char, url)
		res.append(char)
	return "https://cdn.statically.io/img/c.japscan.ws/" + ''.join(res) + ext

def urls_mapper(soup: bs4.BeautifulSoup) -> "list[str]" :
	options = soup.select_one('div.div-select:nth-child(2) > select').select('option')
	return [translateUrl(option['data-img']) for option in options]


@custom.register(site='www.japscan.ws/lecture-en-ligne/one-piece')
class JapscanOnePieceDownloader(BaseDownloader) :
	
	def __init__(self, site: str, config) :
		super().__init__(site, config)
		self._builder = RequesterBuilder.get()
		self._builder.setHeader('User-Agent', config['requests.user-agent'])
		self._requester = self._builder.build()

	def getChapterId(self, url: str) -> str :
		m = chapter_reg.fullmatch(url)
		if m is None :
			raise ApiUrlError(f"URL {url} does not correspond to a One Piece chapter on the Japscan site")
		res: str = m.group(1)
		# for chapters that are bundled in a single volume
		if res.startswith('volume-') :
			volume = int(res[7:])
			chapters = {n: split for n, split in conf_split.items() if split['tome'] == volume}
			items = list(chapters.items())
			if m.group(2) is not None :
				# if we are targetting a specific page
				page = int(m.group(2))
				# if this page is before the first chapter of the volume, return the first chapter
				if(page <= items[0][1]['offset']) :
					return items[0][0]
				# else, we retain the id of the chapter
				prev = items[0][0]
				# for all the other chapters, find the first one that starts after the page and return the previous one
				for n, split in items[1:] :
					if(page < split['offset']) :
						return prev
					prev = n
				# if no chapter was found, it has to be the last chapter
				return items[-1][0]
			return min(chapters.keys(), key=int)
		return m.group(1)
	
	def getMangaId(self, url: str) -> str :
		return MANGA_ID

	def getMangaInfo(self, manga_id: str) :
		if(manga_id != MANGA_ID) :
			raise ApiQueryError(f"Manga {manga_id} is not supported by the Japscan One Piece downloader")
		return {
			'id': manga_id,
			'site': self._site,
			'title': 'One Piece',
			'alt_titles': [],
			'description': None,
			'authors': [{'id': 'Eiichirou-Oda', 'name': 'Eiichirō Oda'}],
			'artists': [],
			'genres': ['Action', 'Adventure', 'Comedy', 'Fantasy'],
			'tags': ['Shounen', 'Pirates'],
			'lang': 'fr',
			'date': {
				'day': 22, 
				'month': 7, 
				'year': 1997
			},
			'rating': 'safe',
			'status': 'ongoing'
		}
	
	def getCover(self, manga_id: str) -> bytes :
		if(manga_id != MANGA_ID) :
			raise ApiQueryError(f"Manga {manga_id} is not supported by the Japscan One Piece downloader")
		return self._requester.requestBinary('https://s4.anilist.co/file/anilistcdn/media/manga/cover/large/bx30013-oT7YguhEK1TE.jpg')
	
	def _getChapterList(self) :
		return self._requester.requestSoup(MANGA_URL, chapters_mapper) 

	def getChapters(self, manga_id: str) :
		if(manga_id != MANGA_ID) :
			raise ApiQueryError(f"Manga {manga_id} is not supported by the Japscan One Piece downloader")
		return self._getChapterList()
	
	def _getChapterUrls(self, chapter_id: str) -> "list[str]" :
		if chapter_id in conf_split :
			split = conf_split[chapter_id]
			urls = self._requester.requestSoup(f"{BASE_URL}/volume-{split['tome']}/1.html", urls_mapper)
			start = split['offset'] - 1
			next_id = str(int(chapter_id) + 1)
			if next_id in conf_split and conf_split[next_id]['tome'] == split['tome'] :
				# Basically, if the next chapter is still in the same tome
				end = conf_split[next_id]['offset'] - 1
				return urls[start:end]
			return urls[start:]
		return self._requester.requestSoup(f"{BASE_URL}/{chapter_id}/1.html", urls_mapper)
	
	def getChapterInfo(self, chapter_id: str) : 
		chapters = self._getChapterList()
		if chapter_id not in chapters :
			raise ApiQueryError(f"No chapter of id {chapter_id} found for One Piece on the Japscan site")
		res = chapters[chapter_id]
		urls = self._getChapterUrls(chapter_id)
		return {**res, 'pages': len(urls)}
	
	def getMangaForChapter(self, chapter_id: str) -> str :
		chapters = self._getChapterList()
		if chapter_id not in chapters :
			raise ApiQueryError(f"No chapter of id {chapter_id} found for One Piece on the Japscan site")
		return MANGA_ID
	
	def getChapterUrls(self, chapter_id: str) -> "tuple[list[str], RequesterBuilder]" :
		return self._getChapterUrls(chapter_id), self._builder

