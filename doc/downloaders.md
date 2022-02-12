
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
	
	def getMangaId(self, url: str) -> str :
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
```

The `@custom.register` decorator is necessary for the downloader to be registered by the API. The `site` provided will be used to match the beginning of a URL to determine which downloader should be used to process the URL. 


### `__init__(self, config)`

The only thing required at the initilaisation stage is to call `super().__init__(config)` to set the configuration. You can also get custom configuration attributes here. For this, create an `example.com` (site of your downloader) section in the `downloaders` section of the configuration. Then, define a property with a name of your choosing in this newly created section. You will be able to get its value in the constructor using `config['name_of_your_property']. More details are available in the [configuration documentation](configuration.md). 

### `getChapterId(self, url)`

This method retrieves the identifier of a chapter from the URL of a page in the site corresponding to this chapter.

### `getMangaId(self, url)`

Similarily to the previous method, retrieves the identifier of a manga from the URL of a page in the site corresponding to this manga.

### `getMangaInfo(self, manga_id)`

Retrives information on the manga associated with the identfier. The data returned is stored in a `dict`, formatted as described [here](api-doc.md#get-apimangainfo).

### `getCover(self, manga_id)`

Retrieves the cover art for the manga associated with the identifier.

### `getChapters(self, manga_id)`

Retrieves the list of chapters in the manga associated with the identifier. The chapters are stored in a `list` and fomatted as described [here](api-doc.md#get-apimangachapters).

### `getChapterInfo(self, chapter_id)`

Retrives information on the chapter associated with the identfier. The data returned is stored in a `dict`, formatted as described [here](api-doc.md#get-apichapterinfo).

### `downloadChapter(self, chapter_id, archiver)`

Downloads the pages for the chapter associated with the identifier and adds them to the `Archiver` using the `archiver.addFile` method. Note that the example code given above is sub-optimal. It would be more efficient to have a separate function that retrieves one page at a time from the site and immediately adds it to the archiver. This should look like something along the lines of the following code, with `getImageFromSite` a function that retrieves a page of the chapter based on some kind of identifier and `getImageIds` a function that retrieves the identifiers of all the pages in the chapter :

```Python
def downloadChapter(self, chapter_id: str, archiver: Archiver) :
	images = getImageIds(chapter_id)
	for image_id in images :
		archiver.addFile(getImageFromSite(image_id))
```


## HTTP Requests

For optimisation purposes, we will require downloaders not to perform HTTP requests themselves. Instead, they must use the `Requester` class defined in the `nagato.utils.request` module. In order to build these objects easily, a `RequesterBuilder` is also available in this module. Here is an example of how a simple request can be performed using this system :

```Python
from nagato.util.request import RequesterBuilder

from requests import Response

# Makes two new attempts at a failed request before exiting
def retryTwiceHandler(response: Response, nb_trys: int) :
	return nb_trys <= 2

requester = RequesterBuilder.get()                \
			.setHeader('User-Agent', '...')       \
			.setHandler(503, retryTwiceHandler)   \
			.build()

json_data = requester.requestJson('example.com/...')
```

The `RequesterBuilder` has a bunch of static methods to create a new instance with the correct HTTP verb : `get`, `post`, `put`, `patch`, `delete`, `head`. We mainly expect `get` to be used but the other ones are there just in case.

Then, you can add headers to the builder with the `setHeader` method that takes two arguments : the name of the HTTP header and its value. You can also add handlers that will specify the behaviour when certain [HTTP error codes] are returned, using the `setHandler` method. A handler is a callable that takes the HTTP `Response` object (see the [`requests` module documentation]) and the number of attempts that have been performed for the URL, and returns a boolean indicating if another attempt should be performed. It can also raise an [error](#errors) if necessary. Both the `setHeader` and `setHandler` methods return the builder, which allows for chained calls. Once the builder has been properly configured, simply call the `build` method to create the `Requester`.

The method of the `Requester` used to perform a request is `requestMap`, which takes four arguments : 
 - `url`: the URL of the resource
 - `mapper`: a callable that takes the `Response` as an argument and outputs the actual data
 - `cache`: a boolean indicating if the result of the request (output of the `mapper`) should be cached, defaults to `True`
 - `delay`: the number of seconds the program should wait before performing the request (as a float), default to `0` (no delay)

For conveniency, other methods have also be defined to avoid rewriting common mappers :
 - `requestBinary` yields the body of the HTTP response as binary data
 - `requestJson` yields the body of the HTTP response interpreted as JSON

Note that these methods only take three arguments since the mapper is already defined. For `requestBinary`, the default value for `cache` is set to `False` since this method is mainly used to get the pages of a chapter, which are heavy and rarily requested twice.


## Errors

Due to the way `flask` works, errors raised during an API call will result in the server returning a `500` error code. In order to have a better control on the error codes, we implemented custom errors in the `nagato.utils.errors` module. These errors have a constructor that take a message as an argument, this message will be sent in the response to indicate what went wrong.

### `ApiError`

This is the base class for any error related to the API. All the following errors extend this class unless specified otherwise.

### `ApiNotFoundError`

Used when a resource is not found, typically when a URL for a manga or a chapter is well-formed but doesn't actually exist on the target website. Yields a `404` error code.

### `ApiQueryError`

Used when an HTTP request made by the API failed.

### `ApiFormatError`

Used when some data given to the API is poorly formatted. Yields a `400` error code.

### `ApiUrlError`

Extends `ApiFormatError`, used for badly formatted URLs.


[HTTP error codes]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status 
[`requests` module documentation]: https://docs.python-requests.org/en/latest/