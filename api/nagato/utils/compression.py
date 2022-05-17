from nagato.utils.sanitise import sanitiseNodeName
from nagato.utils import config

import io
import os
import zipfile
import logging
from lxml import etree
from PIL import Image

logger = logging.getLogger(__name__)


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
		self._rawsize = 0
		self._maxlen = len(str(self._npages))

	def getFilename(self) :
		'''getFilename Retrieves the name of the file (or folder) that will contain the pages

		Returns:
			str: the name of the file or folder
		'''		
		return self._filename
	
	def getFormatInfo(self) -> "dict[str,str]" :
		'''getFormatInfo Retrieves the data used to format the filename

		Returns:
			dict[str,str]: the data used for formatting
		'''		
		return self._format
	
	def getProgress(self) -> float :
		'''getProgress Retrieves the proportion of files that have been downloaded so far

		Returns:
			float: The proportion of downloaded files (between 0 and 1 included), or -1 if the number of pages is not known
		'''
		if self._npages is None :
			return -1
		return self._cpt / self._npages
	
	def getRawSize(self) -> int :
		'''getRawSize Retrieves the total size of files downloaded so far (uncompressed)

		Returns:
			int: the size of the files, in bytes
		'''		
		return self._rawsize
	
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
		self._rawsize += len(file)
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
	
	def after(self) :
		'''after Method exectued at the end of a successful download
		'''		
		pass
	
	def __exit__(self, exc_type, exc_value, tb) :
		'''__exit__ Method called at the end of a `with ... as ...` block

		Derived classes must override this method to free potential allocated resources.
		'''
		if exc_type is not None:
			# traceback.print_exception(exc_type, exc_value, tb)
			return False


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

	def __init__(self, downloader, chapter_id, ext='zip') :
		'''__init__ Method used to initialise the object

		Creates a buffer for the zip file.

		Args:
			downloader (BaseDownloader): The downloader that is downloading files
			chapter_id (str): The identifier of the chapter being downloaded
		'''		
		super().__init__(downloader, chapter_id)
		self._buffer = io.BytesIO()
		self._extension = ext

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
		self._zipfile.close()
		if exc_type is not None:
			# traceback.print_exception(exc_type, exc_value, tb)
			self._buffer.close()
			return False
		if self._npages is not None and self._npages != self._cpt :
			logger.warning('Expected %d pages, got %d', self._npages, self._cpt)
		filepath = os.path.join(self._destination, f"{self._filename}.{self._extension}")
		with open(filepath, 'wb') as f :
			f.write(self._buffer.getvalue())
		self._buffer.close()


@dl_method('cbz')
class CbzArchiver(ZipArchiver) :

	def __init__(self, downloader, chapter_id):
		super().__init__(downloader, chapter_id, 'cbz')


@dl_method('cbz+comicinfo')
class CbzComicinfoArchiver(CbzArchiver) :

	def __init__(self, downloader, chapter_id) :
		super().__init__(downloader, chapter_id)
		self._files_info = []
	
	def fullPageInfo(file: bytes) :
		res = {
			'ImageSize': len(file)
		}
		with Image.open(io.BytesIO(file)) as img :
			res['ImageWidth'] = img.width
			res['ImageHeight'] = img.height
		return res
	
	def minimalPageInfo(file: bytes) :
		return {
			'ImageSize': len(file)
		}

	def getPageInfo(file: bytes) :
		raise NotImplementedError

	def processFile(self, file: bytes, name: str) :
		self._files_info.append(CbzComicinfoArchiver.getPageInfo(file))
		super().processFile(file, name)

	def after(self) :
		'''after Method executed at the end of a successful download
		'''		
		self._zipfile.writestr('ComicInfo.xml', createComicInfo(self._manga, self._chapter, self._files_info))

CbzComicinfoArchiver.getPageInfo = CbzComicinfoArchiver.fullPageInfo if config.getApiConf('compression.cbz.additional_data') else CbzComicinfoArchiver.minimalPageInfo



rating_mapping = {
	'safe':         'Everyone', 
	'suggestive':   'Everyone 10+', 
	'erotica':      'Mature 17+', 
	'pornographic': 'Adults Only 18+'
}

def createComicInfo(manga_info: dict, chapter_info: dict, images_info: list) :
	root = etree.Element('ComicInfo')
	etree.SubElement(root, 'Title').text = chapter_info['title']
	etree.SubElement(root, 'Series').text = manga_info['title']
	if chapter_info['volume'] is not None :
		etree.SubElement(root, 'Number').text = str(chapter_info['volume'])
	etree.SubElement(root, 'Volume').text = str(chapter_info['chapter'])
	if manga_info['description'] is not None :
		etree.SubElement(root, 'Summary').text = manga_info['description']
	etree.SubElement(root, 'Notes').text = 'Generated by Nagato API'
	for tag, dt_id in [('Year', 'year'), ('Month', 'month'), ('Day', 'day')] :
		if chapter_info['date'][dt_id] is not None :
			etree.SubElement(root, tag).text = chapter_info['date'][dt_id]
	for tag, list_id in [('Writer', 'authors'), ('Penciller', 'artists')] :
		if len(manga_info[list_id]) > 0 :
			etree.SubElement(root, tag).text = ', '.join([a['name'] for a in manga_info[list_id]])
	if chapter_info['team'] is not None :
		etree.SubElement(root, 'Translator').text = chapter_info['team']['name']
	for tag, list_id in [('Genre', 'genres'), ('Tags', 'tags')] :
		if len(manga_info[list_id]) > 0 :
			etree.SubElement(root, tag).text = ', '.join(manga_info[list_id])
	etree.SubElement(root, 'PageCount').text = str(len(images_info))
	etree.SubElement(root, 'LanguageISO').text = chapter_info['lang']
	etree.SubElement(root, 'Manga').text = 'Yes'
	if manga_info['rating'] is not None :
		etree.SubElement(root, 'AgeRating').text = rating_mapping[manga_info['rating']]
	pages = etree.SubElement(root, 'Pages')
	for i, img_info in enumerate(images_info) :
		page = etree.SubElement(pages, 'Page')
		page.set('Image', str(i))
		for attr, val in img_info.items() :
			page.set(attr, str(val))
	if len(images_info) > 0 :
		pages[0].set('Type', 'FrontCover')
	return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8')
	