
from nagato.utils.request import RequesterBuilder
from nagato.utils.errors import ApiConfigurationError
from nagato.utils.sanitise import sanitiseNodeName
from nagato.utils.compression import Archiver, getArchiverForMethod
from nagato.utils.threads import ChapterDownload
from nagato.utils.database import getConnection, SqlChapterEntry, SqlMangaEntry, ChapterMark

import os
import logging
from string import Template

logger = logging.getLogger(__name__)


class BaseDownloader :

	def __init__(self, site: str, config) :
		self._site = site
		self._archiver_class = getArchiverForMethod(config['chapters.method'])
		self._destination = config['chapters.destination']
		if not os.path.exists(self._destination) :
			logger.info(f"Recursively creating directory \"{self._destination}\"")
			os.makedirs(self._destination)
		if not os.path.isdir(self._destination) :
			raise NotADirectoryError(f"\"{self._destination}\" is a file")
		self._format = Template(config['chapters.format'])
		try :
			fake_info = {k: k for k in ['id', 'title', 'manga_id', 'manga', 'volume', 'chapter', 'lang', 'team']}
			self._format.substitute(fake_info)
		except ValueError :
			raise ApiConfigurationError(f"Invalid template \"{config['chapters.format']}\" in class {type(self).__name__}")
		except KeyError as e :
			raise ApiConfigurationError(f"Template \"{config['chapters.format']}\" in class {type(self).__name__} contains the invalid placeholder \"{e}\"")
		if config['mangas.separate'] :
			self.getDestinationFolder = self.destFolderSeparated
		else :
			self.getDestinationFolder = self.destFolderMixed
		self._pagedelay = config['chapters.pagedelay']
	
	
	def getSite(self) -> str :
		return self._site

	def getMangaId(self, url) :
		raise NotImplementedError
	
	def getChapterId(self, url) :
		raise NotImplementedError
	
	def getMangaForChapter(self, chapter_id) :
		return self.getChapterInfo(chapter_id)['manga']

	def getMangaInfo(self, manga_id) :
		raise NotImplementedError
	
	def getCover(self, manga_id) :
		raise NotImplementedError

	def getChapters(self, manga_id) :
		raise NotImplementedError
	 
	def downloadChapters(self, ids) -> "list[str]" :
		return [ChapterDownload(self, chapter_id).submit() for chapter_id in ids]
	
	def downloadChapter(self, chapter_id, archiver: Archiver) :
		images, builder = self.getChapterUrls(chapter_id)
		with builder.session() as requester :
			for image_url in images :
				archiver.addFile(requester.requestBinary(image_url, delay=self._pagedelay))
	
	def getChapterUrls(self, chapter_id) -> "tuple[list[str], RequesterBuilder]" :
		raise NotImplementedError

	def getChapterInfo(self, chapter_id) :
		raise NotImplementedError

	def getArchiver(self, chapter_id) -> Archiver :
		return self._archiver_class(self, chapter_id)

	def getChapterFormattingData(self, chapter_info, manga_info) :
		return {
			'id': chapter_info['id'],
			'title': chapter_info['title'],
			'manga_id': manga_info['id'],
			'manga': manga_info['title'],
			'volume': chapter_info['volume'],
			'chapter': chapter_info['chapter'],
			'lang': chapter_info['lang'],
			'team': chapter_info['team']['name'] if chapter_info['team'] is not None else None
		}

	def getFilename(self, format_info) :
		return self._format.substitute(format_info)

	def getDestinationFolder(self, format_info) :
		raise NotImplementedError
	
	def destFolderSeparated(self, format_info) :
		path = os.path.join(self._destination, sanitiseNodeName(format_info['manga']))
		if not os.path.exists(path) :
			os.mkdir(path)
		return path
	
	def destFolderMixed(self, format_info) :
		return self._destination
	
	def getChapterTags(self, chapter_ids: str) :
		res = {}
		with getConnection() as con :
			cur = con.cursor()
			for chapter_id in chapter_ids :
				entry = SqlChapterEntry(self._site, chapter_id, self)
				mark = entry.getMark(cur)
				res[chapter_id] = mark.name if mark is not None else None
		return res
			
	def setChapterTags(self, chapter_ids: "list[str]", mark: ChapterMark) -> bool :
		res = False
		with getConnection() as con :
			cur = con.cursor()
			for chapter_id in chapter_ids :
				entry = SqlChapterEntry(self._site, chapter_id, self)
				res = entry.setMark(cur, mark) or res
			con.commit()
		return res
	
	def isMangaStarred(self, manga_id) :
		with getConnection() as con :
			cur = con.cursor()
			entry = SqlMangaEntry(self._site, manga_id)
			return entry.isStarred(cur)

	def setMangaStar(self, manga_id, star: bool) :
		with getConnection() as con :
			cur = con.cursor()
			entry = SqlMangaEntry(self._site, manga_id)
			res = entry.star(cur) if star else entry.unstar(cur)
			con.commit()
		return res
	
	def getChaptersTagsForManga(self, manga_id) :
		with getConnection() as con :
			cur = con.cursor()
			entry = SqlMangaEntry(self._site, manga_id)
			res = entry.getChaptersWithTags(cur)
		return {a: b.name for a, b in res.items()}
