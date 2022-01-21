import io
import os
import traceback
import zipfile
import logging

logger = logging.getLogger(__name__)

def inMemoryZip(files) :
	buffer = io.BytesIO()
	with zipfile.ZipFile(buffer, 'w') as zip_file:
		for filename, data in files.items() :
			zip_file.writestr(filename, io.BytesIO(data).getvalue())
	return buffer.getvalue()

def makeCbz(images, description=None) :
	maxlen = len(str(len(images)))
	files = {nameImage(image, i+1, maxlen): image for i, image in enumerate(images)}
	if description is not None :
		pass # TODO description
	return inMemoryZip(files)


binary_patterns = {
	b'\x89PNG\r\n\x1a\n': 'png',
	b'\xff\xd8\xff': 'jpg',
	b'GIF89a': 'gif',
	b'GIF87a': 'gif',
	b'RIFF': 'webp',
	b'II*\x00': 'tiff',
	b'MM\x00*': 'tiff',
	b'BM': 'bmp'
}

def nameImage(image: bytes, name, maxlen) :
	for pattern, extension in binary_patterns.items() :
		if image.startswith(pattern) :
			realname = str(name).rjust(maxlen, '0')
			return f"{realname}.{extension}"
	logger.warning(f"Could not determine the type of an image with binary prefix {image[:10]}")
	return f"{name}.png"


_dl_methods = {}

def dl_method(method: str) :
	def annotation(f) :
		_dl_methods[method] = f
		return f
	return annotation

def getArchiverForMethod(method: str) :
	if method not in _dl_methods :
			raise ValueError(f"Unrecognized download method {method}")
	return _dl_methods[method]


class Archiver :

	def __init__(self, downloader, chapter_id) :
		self._chapter = downloader.getChapterInfo(chapter_id)
		self._manga = downloader.getMangaInfo(self._chapter['manga'])
		self._format = downloader.getChapterFormattingData(self._chapter, self._manga)
		self._npages = self._chapter['pages']
		self._destination = downloader.getDestinationFolder(self._format)
		self._filename = downloader.getFilename(self._format)
		self._cpt = 1
		self._maxlen = len(str(self._npages))

	def getFilename(self) :
		return self._filename
	
	def __enter__(self) :
		return self

	def addFile(self, file: bytes) :
		filename = nameImage(file, self._cpt, self._maxlen)
		self._cpt += 1
		self.processFile(file, filename)
	
	def processFile(self, file: bytes, name: str) :
		raise NotImplementedError
	
	def __exit__(self, exc_type, exc_value, tb) :
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_value, tb)


@dl_method('files')
class FilesArchiver(Archiver) :

	def __init__(self, downloader, chapter_id) :
		super().__init__(downloader, chapter_id)
		self._download_dir = os.path.join(self._destination, self._filename)
		if not os.path.exists(self._download_dir) :
			os.mkdir(self._download_dir)

	def processFile(self, file: bytes, name: str) :
		filepath = os.path.join(self._download_dir, name)
		with open(filepath, 'wb') as f :
			f.write(file)


@dl_method('zip')
class ZipArchiver(Archiver) :

	def __init__(self, downloader, chapter_id) :
		super().__init__(downloader, chapter_id)
		self._buffer = io.BytesIO()

	def __enter__(self) :
		self._zipfile = zipfile.ZipFile(self._buffer, 'w')
		return self

	def processFile(self, file: bytes, name: str) :
		self._zipfile.writestr(name, io.BytesIO(file).getvalue())

	def __exit__(self, exc_type, exc_value, tb):
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_value, tb)
		self._zipfile.close()
		filepath = os.path.join(self._destination, f"{self._filename}.zip")
		with open(filepath, 'wb') as f :
			f.write(self._buffer.getvalue())
		self._buffer.close()


@dl_method('cbz')
class CbzArchiver(Archiver) : # TODO comicinfo.xml

	def __init__(self, downloader, chapter_id) :
		super().__init__(downloader, chapter_id)
		self._buffer = io.BytesIO()

	def __enter__(self) :
		self._zipfile = zipfile.ZipFile(self._buffer, 'w')
		return self

	def processFile(self, file: bytes, name: str) :
		self._zipfile.writestr(name, io.BytesIO(file).getvalue())

	def __exit__(self, exc_type, exc_value, tb):
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_value, tb)
		self._zipfile.close()
		filepath = os.path.join(self._destination, f"{self._filename}.cbz")
		with open(filepath, 'wb') as f :
			f.write(self._buffer.getvalue())
		self._buffer.close()
