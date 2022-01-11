from nagato.utils.compression import makeCbz

class BaseDownloader :

	def __init__(self) :
		pass

	def getMangaId(self, url):
		raise NotImplementedError
	
	def getChapterId(self, url):
		raise NotImplementedError

	def getMangaInfo(self, manga_id):
		raise NotImplementedError
	
	def getChapters(self, manga_id) :
		raise NotImplementedError
	 
	def downloadChapters(self, ids) :
		return {chapter_id: self.downloadChapter(chapter_id) for chapter_id in ids}
	
	def downloadChapter(self, chapter_id) :
		raise NotImplementedError

	def getChapterInfo(self, chapter_id) :
		raise NotImplementedError
	
	def saveToZip(self, ids) :
		data = self.downloadChapters(ids)
		for chapter_id, images in data.items() :
			with open(f"{chapter_id}.zip", 'wb') as f :
				f.write(makeCbz(images))
	
	def saveToCbz(self, ids) :
		data = self.downloadChapters(ids)

	def saveAsFiles(self, ids) :
		data = self.downloadChapters(ids)
