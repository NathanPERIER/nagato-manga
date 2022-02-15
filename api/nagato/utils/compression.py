from nagato.utils.sanitise import sanitiseNodeName

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
		pass # Build Comicinfo.xml here
	return inMemoryZip(files)


# Patterns at the beginning of an image that allow us to determine its type
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

def nameImage(image: bytes, name, maxlen: int, fill: str = '0') :
	'''nameImage Generate a name for an image from the binary data

	Infers the type of the image and 

	Args:
		image (bytes): The binary data of the image
		name: The name of the file before the extension (stem)
		maxlen (int): The desired length for the stem of the file
		fill (str): The character used to pad the stem of the file

	Returns:
		str: The name of the file
	'''	
	for pattern, extension in binary_patterns.items() :
		if image.startswith(pattern) :
			realname = str(name).rjust(maxlen, fill)
			return f"{realname}.{extension}"
	logger.warning(f"Could not determine the type of an image with binary prefix {image[:10]}")
	return f"{name}.png"


_dl_methods = {}

def dl_method(method: str) :
	'''dl_method Decorator used to register an `Archiver` for a certain method

	Args:
		method (str): The name of the method for the `Archiver` we want to register
	'''	
	def annotation(f) :
		_dl_methods[method] = f
		return f
	return annotation

def getArchiverForMethod(method: str) :
	'''getArchiverForMethod Retrieves an `Archiver` class for a specific method name

	Args:
		method (str): The name of the method

	Raises:
		ValueError: If the method is not associated with an `Archiver`

	Returns:
		class: The class of the `Archiver` associated with the download method
	'''	
	if method not in _dl_methods :
			raise ValueError(f"Unrecognized download method {method}")
	return _dl_methods[method]


class Archiver :
	''' Archiver
	This is a base class that used to save files while they are being downloaded.
	This specific implementation mustn't be instanciated, one must create a child class
	with an actual implementation of `processFile`.
	'''	

	def __init__(self, downloader, chapter_id) :
		'''__init__ Method used to initialise the object

		This must be called by all classes extending Archiver.
		Fetches all the data required to format the name of the files
		thanks to the methods provided by the `BaseDownloader`.

		Args:
			downloader (BaseDownloader): The downloader that is downloading files
			chapter_id (str): The identifier of the chapter being downloaded
		'''		
		self._chapter = downloader.getChapterInfo(chapter_id)
		self._manga = downloader.getMangaInfo(self._chapter['manga'])
		self._format = downloader.getChapterFormattingData(self._chapter, self._manga)
		self._npages = self._chapter['pages']
		self._destination = downloader.getDestinationFolder(self._format)
		self._filename = sanitiseNodeName(downloader.getFilename(self._format))
		self._cpt = 0
		self._maxlen = len(str(self._npages))

	def getFilename(self) :
		'''getFilename Retrieves the name of the file (or folder) that will contain the pages

		Returns:
			str: the name of the file or folder
		'''		
		return self._filename
	
	def getProgress(self) -> float :
		'''getProgress Retrieves the proportion of files that have been downloaded so far

		Returns:
			float: The proprtion of downloaded files (between 0 and 1 included)
		'''
		return self._cpt / self._maxlen
	
	def __enter__(self) :
		'''__enter__ Method called at the beginning of a `with ... as ...` block

		All `Archiver`s must implement this method in order to be closed
		properly if necessary.

		Returns:
			Archiver: the resource that will be closed (`self`)
		'''		
		return self

	def addFile(self, file: bytes) :
		'''addFile Saves a new page of the chapter to the archive

		In theory there is no reason for a child class to modify this method.

		Args:
			file (bytes): The page as binary data
		'''	
		self._cpt += 1
		filename = nameImage(file, self._cpt, self._maxlen)
		self.processFile(file, filename)
	
	def processFile(self, file: bytes, name: str) :
		'''processFile Method that processes a file that has been added to the `Archiver`

		This is the method that child classes must override in order to define a
		specific behaviour when a file is added.

		Args:
			file (bytes): A file that has been added to the `Archiver`
			name (str): The name of the file

		Raises:
			NotImplementedError: This method is not implemented in this class, 
			see subclasses for an actual implementation
		'''		
		raise NotImplementedError
	
	def __exit__(self, exc_type, exc_value, tb) :
		'''__exit__ Method called at the end of a `with ... as ...` block

		Derived classes must override this method to free potential allocated resources.
		'''
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_value, tb)


@dl_method('files')
class FilesArchiver(Archiver) :
	'''FilesArchiver `Archiver` that downloads pages as individual files'''	

	def __init__(self, downloader, chapter_id) :
		'''__init__ Method used to initialise the object

		Creates the directory associated with the chapter (if it doesn't exist yet)

		Args:
			downloader (BaseDownloader): The downloader that is downloading files
			chapter_id (str): The identifier of the chapter being downloaded
		'''		
		super().__init__(downloader, chapter_id)
		self._download_dir = os.path.join(self._destination, self._filename)
		if not os.path.exists(self._download_dir) :
			os.mkdir(self._download_dir)

	def processFile(self, file: bytes, name: str) :
		'''processFile Processes a file that has been added to the `Archiver`

		Simply saves the file in the directory corresponding to the chapter.

		Args:
			file (bytes): A file that has been added to the `Archiver`
			name (str): The name of the file
		'''		
		filepath = os.path.join(self._download_dir, name)
		with open(filepath, 'wb') as f :
			f.write(file)


@dl_method('zip')
class ZipArchiver(Archiver) :
	'''FilesArchiver `Archiver` that downloads pages in a zip file'''	

	def __init__(self, downloader, chapter_id) :
		'''__init__ Method used to initialise the object

		Creates a buffer for the zip file.

		Args:
			downloader (BaseDownloader): The downloader that is downloading files
			chapter_id (str): The identifier of the chapter being downloaded
		'''		
		super().__init__(downloader, chapter_id)
		self._buffer = io.BytesIO()

	def __enter__(self) :
		'''__enter__ Method called at the beginning of a `with ... as ...` block

		Creates a zip object with the previously created buffer.

		Returns:
			ZipArchiver: the resource that will be closed (`self`)
		'''
		self._zipfile = zipfile.ZipFile(self._buffer, 'w')
		return self

	def processFile(self, file: bytes, name: str) :
		'''processFile Processes a file that has been added to the `Archiver`

		Adds the file to the zip object.

		Args:
			file (bytes): A file that has been added to the `Archiver`
			name (str): The name of the file
		'''
		self._zipfile.writestr(name, io.BytesIO(file).getvalue())

	def __exit__(self, exc_type, exc_value, tb):
		'''__exit__ Method called at the end of a `with ... as ...` block

		Saves the content of the zip file to the disc, then frees the zip object and the buffer.
		'''
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
