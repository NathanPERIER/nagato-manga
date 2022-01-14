from nagato.utils.compression import makeCbz

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
		self._format = config['chapters.format']
		

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
			images = self.downloadChapter(chapter_id)
			self.saveChapter(chapter_id, images)
	
	def downloadChapter(self, chapter_id) :
		raise NotImplementedError

	def getChapterInfo(self, chapter_id) :
		raise NotImplementedError

	def saveChapter(self, chapter_id, images) :
		raise NotImplementedError
	
	@dl_method('zip')
	def saveToZip(self, chapter_id, images) :
		with open(f"{chapter_id}.zip", 'wb') as f :
			f.write(makeCbz(images))
	
	@dl_method('cbz')
	def saveToCbz(self, chapter_id, images) :
		raise NotImplementedError

	@dl_method('files')
	def saveAsFiles(self, chapter_id, images) :
		raise NotImplementedError
