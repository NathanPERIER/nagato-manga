
# Nagato Downloader

Downloaders are components that can be defined in the API and that enable downloading chapters from a website.

They must respect a handful of principles that will be defined below.


## Class definition

The class must be created in a `.py` file in the `/api/nagato/downloaders/custom` folder or a subfolder.

Here is a base template that you can fill to adapt it to a certain site :

```Python
from nagato.utils.request import RequesterBuilder
from nagato.utils.compression import Archiver
from nagato.downloaders import custom
from nagato.downloaders.base import BaseDownloader

@custom.register(site='example.com')
class MyDownloader(BaseDownloader) :
	
	def __init__(self, site: str, config) :
		super().__init__(site, config)

	def getChapterId(self, url: str) -> str :
		return ''
	
	def getMangaId(self, url: str) -> str :
		return ''

	def getMangaInfo(self, manga_id: str) :
		return {
			'id': manga_id,
			'site': self._site,
			'title': '',
			'alt_titles': [],
			'description': None,
			'authors': [],
			'artists': [],
			'genres': [],
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
		return {
			'id': {
				'volume': 1, 
				'chapter': 1, 
				'title': '', 
				'lang': 'en', 
				'pages': 1, 
				'date': {
					'day': None, 
					'month': None, 
					'year': None
				},
				'team': {
					'id': '', 
					'name': '', 
					'site': None
				}
			}
		}
	
	def getChapterInfo(self, chapter_id: str) : 
		return {
			'id': chapter_id, 
			'manga': '', # an identifier
			'volume': 1, 
			'chapter': 1, 
			'title': '', 
			'lang': 'en', 
			'pages': 1, 
			'date': {
				'day': None, 
				'month': None, 
				'year': None
			},
			'team': {
				'id': '', 
				'name': '', 
				'site': None
			}
		}
	
	def getMangaForChapter(self, chapter_id: str) -> str :
		# This is the default implementation, override if possible
		return self.getChapterInfo(chapter_id)['manga']
	
	def getChapterUrls(self, chapter_id: str) -> "tuple[list[str], RequesterBuilder]" :
		return self._requester.requestJson(f"https://exmple.com/api/pages/{chapter_id}"), builder

	def downloadChapter(self, chapter_id: str, archiver: Archiver) :
		# This is the default implementation, only override if necessary
		images, builder = self.getChapterUrls(chapter_id)
		with builder.session() as requester :
			for image_url in images :
				archiver.addFile(requester.requestBinary(image_url, delay=self._pagedelay))
```

The `@custom.register` decorator is necessary for the downloader to be registered by the API. The `site` provided will be used to match the beginning of a URL to determine which downloader should be used to process the URL. 


### `__init__(self, site, config)`

The only thing required at the initilaisation stage is to call `super().__init__(site, config)` to set the configuration. You can also get custom configuration attributes here. For this, create an `example.com` (site of your downloader) section in the `downloaders` section of the configuration. Then, define a property with a name of your choosing in this newly created section. You will be able to get its value in the constructor using `config['name_of_your_property']. More details are available in the [configuration documentation](configuration.md). 

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

### `getMangaForChapter(self, chapter_id)`

Retrieves the identifier of the manga to which the specified chapter belongs. By default, this calls the `getChapterInfo` method and retrieves the `manga` field, which is sub-optimal. It is advised to override this method if there exists a more optimised way of getting this information. In case this method is not overriden, **do not** use it in `getChapterInfo` as it would create an infinite loop, quickly crashing the program (stack overflow error).

### `getChapterUrls(self, chapter_id)`

Retrieves the URLs of the specified chapter's pages in a list, along with a `Requester` to download them (see [below](#http-requests)). 

### `downloadChapter(self, chapter_id, archiver)`

Downloads the pages for the chapter associated with the identifier and adds them to the `Archiver` using the `archiver.addFile` method. This uses the `getChapterUrls` method by default, downloading the resource at each URL in the list with the provided `Requester`. Only override this method if you need to do something more fancy (using different headers for each page for example).

Note that an implementation such as the following one would be sub-optimal :

```Python
def downloadChapter(self, chapter_id: str, archiver: Archiver) :
	urls, requester = self.getChapterUrls(chapter_id)
	images = [requester.requestBinary(image_url, 0.1) for image_url in urls]
	for image in images :
		archiver.addFile(image)
```

It would be more efficient to add each page to the `Archiver` immediately after it is downloaded. This should look like something along the lines of the following code, with `getImageFromSite` a function that retrieves a page of the chapter based on some kind of identifier and `getImageIds` a function that retrieves the identifiers of all the pages in the chapter :

```Python
def downloadChapter(self, chapter_id: str, archiver: Archiver) :
	images = getImageIds(chapter_id)
	for image_id in images :
		archiver.addFile(getImageFromSite(image_id))
```

Also note that we use `self._pagedelay` for the delay between the downloads of two pages. This is an attribute taken from the [configuration](configuration.md#configuration-of-a-downloader) that you can also use anywhere deemed fitting. 


## HTTP Requests

For optimisation purposes, we will require downloaders not to perform HTTP requests themselves. Instead, they must use the `Requester` class defined in the `nagato.utils.request` module. This is a wrapper for methods of the [`requests`](https://docs.python-requests.org/en/latest/) module with added features like caching and error handling. In order to build these objects easily, a `RequesterBuilder` is also available in this module. Here is an example of how a simple request can be performed using this system :

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

json_data = requester.requestJson('https://example.com/...')
```

### Create a `Requester`

The `RequesterBuilder` has a bunch of static methods to create a new instance with the correct HTTP verb : `get`, `post`, `put`, `patch`, `delete`, `head`. We mainly expect `get` to be used but the other ones are there just in case.

Then, you can add headers to the builder with the `setHeader` method that takes two arguments : the name of the HTTP header and its value. You can also add handlers that will specify the behaviour when certain [HTTP error codes] are returned, using the `setHandler` method. A handler is a callable that takes the HTTP `Response` object (see the [`requests` module documentation]) and the number of attempts that have been performed for the URL, and returns a boolean indicating if another attempt should be performed. It can also raise an [error](#errors) if necessary. You can also set a specific handler for a connection error with `onConnectionError`. It accepts a callable with two arguments : the exception that was raised and the number of attempts that have been performed. Like before, it returns a boolean indicating if another attempt should be performed. Finally, you can set the timeout using `setTimeout`. The accepted values for a timeout are the same as described [here](https://docs.python-requests.org/en/latest/user/advanced/#timeouts).

All the previously described methods return the builder, which allows for chained calls. Once the builder has been properly configured, simply call its `build` method to create the `Requester`.

### Perform a request

The method of the `Requester` used to perform a request is `requestMap`, which takes four arguments : 
 - `url`: the URL of the resource
 - `mapper`: a callable that takes the `Response` as an argument and outputs the actual data
 - `cache`: a boolean indicating if the result of the request (output of the `mapper`) should be cached, defaults to `True`
 - `delay`: the number of seconds the program should wait before performing the request (as a float), default to `0` (no delay)

For conveniency, other methods have also be defined to avoid rewriting common mappers :
 - `requestBinary` yields the body of the HTTP response as binary data
 - `requestJson` yields the body of the HTTP response interpreted as JSON

Note that these methods only take three arguments since the mapper is already defined. For `requestBinary`, the default value for `cache` is set to `False` since this method is mainly used to get the pages of a chapter, which are heavy and rarily requested twice.

For more complex structures (XML, HTML, ...) it is better to create your own method that retrieves the useful data from the response content and to pass it to `requestMap`. Then, the result of your treatment will be cached and it will be much faster to retrieve. Note however that a flaw of this system is that you can only have one cached result for one URL, so if you have several treatments to perform on a single URL you have to perform them all at once and select only the required bits each time. 

### Sessions

You can also use sessions to perform several requests to the same site in a row. With a session, the TLS connsection is kept alive, therefore chained requests are more efficient. This is mainly used to download the pages of a chapter :

```Python
with builder.session() as requester :
	for image_url in images :
		archiver.addFile(requester.requestBinary(image_url, delay=self._pagedelay))
```

The `session` method of a builder returns a special `Requester` that must only be used in a with statement in order for its resources to be freed properly.

### Agregation of requests

Sometimes a request to a single URL is not enough to get all the data you need, which is why the `requestAgregate` method was introduced. Its arguments are similar to those of `requestMap` except for the second argument. It is still a callable, but this time it takes three arguments : the `Response`, the previous result (or `None`) if it is the first request, and a `dict` used to record information that are retained between calls (you can put anything you want inside but it will not be returned). The callable must return a tuple where the first argument is the result obtained by processing the response and the second argument is either a URL or `None`.

Here is an example with an external API that returns entries per batches of 20. In order to get all of the entries, we agregate the results of several requests :

```Python
def agregator(response: Response, prev_results, state: dict) -> tuple :
	data = response.json()
	if prev_result is None : # First iteration
		state['batch'] = 1
		state['max'] = data['total'] # we assume the response has a field for the total number of elements
		res = []
	else :
		state['batch'] += 1 
		res = prev_results
	res.extend(data['content']) # we assume is a list of 20 elements or less
	next_url = None
	if state['batch'] * 20 >= state['max'] :
		next_url = f"https://example.com/api/resource/AAAA/{state['batch']+1}"
	return res, next_url

res = requester.requestAgregate('https://example.com/api/resource/AAAA/1', agregator) # cache = True, delay = 0
# At this point, res is cached for https://example.com/api/resource/AAAA/1, so if we make another
# request with this URL it will be much faster
```

The idea is that the callable will first be applied to the URL passed as a parameter of `requestAgregate`. If the second element of the returned tuple is not `None`, the function will be applied once again to this URL, with the previous result (first element of the tuple) passed as the second argument. This continues until the second element returned is `None`, in which case the first element is returned and cached if the `cache` boolean is set to `True`. If URL is requested twice, error is raised as we assume the program is looping. 

The `state` dict is the same object for all calls of a same agragation request. Anything can be put inside, although it is not possible to retrieve its content outside of `requestAgregate`.


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

### `ApiConfigurationError`

Should only be used during the initialisation of the API, indicates that some configuration entry had an unexpected value.


[HTTP error codes]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status 
[`requests` module documentation]: https://docs.python-requests.org/en/latest/