from nagato.utils.compression import nameImage, makeCbz
from nagato.utils.threads import DownloadThread

import os
import logging

logger = logging.getLogger(__name__)

_dl_methods = {}

def dl_method(method) :
	def annotation(f) :
		_dl_methods[method] = f
		return f
	return annotation


class BaseDownloader :

	def __init__(self, config) :
		dl_method = config['chapters.method']
		if dl_method not in _dl_methods :
			raise ValueError(f"Unrecognized download method {dl_method}")
		self._saveChapter = _dl_methods[dl_method]
		self._destination = config['chapters.destination'] # TODO test and create folder
		if not os.path.exists(self._destination) :
			logger.info(f"Recursively creating directory \"{self._destination}\"")
			os.makedirs(self._destination)
		if not os.path.isdir(self._destination) :
			raise NotADirectoryError(f"\"{self._destination}\" is a file")
		self._format = config['chapters.format']
		if config['chapters.separate'] :
			self.getDestinationFolder = self.destFolderSeparated
		else :
			self.getDestinationFolder = self.destFolderMixed
		

	def getMangaId(self, url):
		raise NotImplementedError
	
	def getChapterId(self, url):
		raise NotImplementedError

	def getMangaInfo(self, manga_id):
		raise NotImplementedError
	
	def getCover(self, manga_id) :
		raise NotImplementedError

	def getChapters(self, manga_id) :
		raise NotImplementedError
	 
	def downloadChapters(self, ids) :
		for chapter_id in ids :
			DownloadThread(self, chapter_id).start()
	
	def downloadChapter(self, chapter_id) :
		raise NotImplementedError

	def getChapterInfo(self, chapter_id) :
		raise NotImplementedError

	def getChapteFormattingData(self, chapter_id) :
		chapter_info = self.getChapterInfo(chapter_id)
		manga_info = self.getMangaInfo(chapter_info['manga'])
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

	def saveChapter(self, images, format_info) :
		self._saveChapter(self, images, format_info)

	@dl_method('zip')
	def saveToZip(self, images, format_info) :
		folder = self.getDestinationFolder(format_info)
		filename = self.getFilename(format_info)
		with open(os.path.join(folder, f"{filename}.zip"), 'wb') as f :
			f.write(makeCbz(images))
	
	@dl_method('cbz')
	def saveToCbz(self, images, format_info) :
		folder = self.getDestinationFolder(format_info)
		filename = self.getFilename(format_info)
		with open(os.path.join(folder, f"{filename}.cbz"), 'wb') as f :
			f.write(makeCbz(images))

	@dl_method('files')
	def saveAsFiles(self, images, format_info) :
		folder = os.path.join(self.getDestinationFolder(format_info), self.getFilename(format_info))
		if not os.path.exists(folder) :
			os.mkdir(folder)
		maxlen = len(str(len(images)))
		for i, image in enumerate(images) :
			filename = nameImage(image, i+1, maxlen)
			with open(os.path.join(folder, filename), 'wb') as f :
				f.write(image)

	def getFilename(self, format_info) : # TODO format with a format string
		return format_info['title']

	def getDestinationFolder(self, format_info) :
		raise NotImplementedError
	
	def destFolderSeparated(self, format_info) :
		path = os.path.join(self._destination, format_info['manga'])
		if not os.path.exists(path) :
			os.mkdir(path)
		return path
	
	def destFolderMixed(self, format_info) :
		return self._destination
