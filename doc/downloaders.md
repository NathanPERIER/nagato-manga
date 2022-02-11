
# Nagato Downloader

Downloaders are components that can be defined in the API and that enable downloading chapters from a website.

They must respect a handful of principles that will be defined below.


## Class definition

The class must be created in a `.py` file in the `/api/nagato/downloaders/custom` folder or a subfolder.

Here is a base template that you can fill to adapt it to a certain site :

```Python
from nagato.utils.compression import Archiver
from nagato.downloaders import custom
from nagato.downloaders.base import BaseDownloader

@custom.register(site='example.com')
class MyDownloader(BaseDownloader) :
	
	def __init__(self, config) :
		super().__init__(config)

	def getChapterId(self, url: str) -> str :
		return ''
	
	def getMangaId(self, url: str) -> str:
		return ''

	def getMangaInfo(self, manga_id: str) :
		return {
			'id': '',
			'title': '',
			'alt_titles': [],
			'description': None,
			'authors': [],
			'artists': [],
			'tags': [],
			'lang': 'en',
			'date': {
				'day': None, 
				'month': None, 
				'year': None
			},
			'rating': None,
			'status': None
		}
	
	def getCover(self, manga_id: str) -> bytes :
		return None

	def getChapters(self, manga_id: str) :
		return [
			'id': {
				'volume': 1, 
				'chapter': 1, 
				'title': '', 
				'lang': 'en', 
				'pages': 1, 
				'team': {
					'id': '', 
					'name': '', 
					'site': None
				}
			}
		]
	
	def getChapterInfo(self, chapter_id: str) : 
		return {
			'id': '', 
			'manga': '', # an identifier
			'volume': 1, 
			'chapter': 1, 
			'title': '', 
			'lang': 'en', 
			'pages': 1, 
			'team': {
				'id': '', 
				'name': '', 
				'site': None
			}
		}
	
	def downloadChapter(self, chapter_id: str, archiver: Archiver) :
		images = [] # get images from the site
		for image in images :
			archiver.addFile(image)
		# Note that it would be better to have a function that retrieves images
		# one by one from the site and do something like that :
		# for image_id in images :
		#     archiver.addFile(getImageFromSite(image_id))
```

The `@custom.register` decorator is necessary for the downloader to be registered by the API. The `site` provided will be used to match the beginning of a URL to determine which downloader should be used to process the URL. 


### `__init__(self, config)`

### `getChapterId(self, url)`

### `getMangaId(self, url)`

### `getMangaInfo(self, manga_id)`

### `getCover(self, manga_id)`

### `getChapters(self, manga_id)`

### `getChapterInfo(self, chapter_id)`

### `downloadChapter(self, chapter_id, archiver)`

