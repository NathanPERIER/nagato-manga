from nagato.utils.compression import makeCbz

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
		self.saveChapter = _dl_methods[dl_method]
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
		manga_info = None
		for chapter_id in ids :
			images = self.downloadChapter(chapter_id)
			chapter_info = self.getChapterInfo(chapter_id)
			if manga_info is None :
				manga_info = self.getMangaInfo(chapter_info['manga'])
			self.saveChapter(self, images, manga_info, chapter_info)
	
	def downloadChapter(self, chapter_id) :
		raise NotImplementedError

	def getChapterInfo(self, chapter_id) :
		raise NotImplementedError

	def saveChapter(self, images, manga_info, chapter_info) :
		raise NotImplementedError

	@dl_method('zip')
	def saveToZip(self, images, manga_info, chapter_info) :
		folder = self.getDestinationFolder(manga_info)
		filename = self.getFilename(manga_info, chapter_info)
		with open(os.path.join(folder, filename), 'wb') as f :
			f.write(makeCbz(images))
	
	@dl_method('cbz')
	def saveToCbz(self, images, manga_info, chapter_info) :
		raise NotImplementedError

	@dl_method('files')
	def saveAsFiles(self, images, manga_info, chapter_info) :
		raise NotImplementedError

	def getFilename(self, manga_info, chapter_info) :
		return f"{chapter_info['title']}.zip"

	def getDestinationFolder(self, manga_info) :
		raise NotImplementedError
	
	def destFolderSeparated(self, manga_info) :
		path = os.path.join(self._destination, manga_info['title'])
		if not os.path.exists(path) :
			os.mkdir(path)
		return path
	
	def destFolderMixed(self, manga_info) :
		return self._destination
