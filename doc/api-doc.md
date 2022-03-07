# Nagato API

This file lists the available endpoints for the API.

#### General API information
- [`GET /api/ping`](#get-apiping)
- [`GET /api/version`](#get-apiversion)
- [`GET /api/sites`](#get-apisites)

#### Retrieve information on a manga or chapter
- [`GET /api/resource/site`](#get-apiresourcesite)
- [`GET /api/manga/id`](#get-apimangaid)
- [`GET /api/chapter/id`](#get-apichapterid)
- [`GET /api/manga/info`](#get-apimangainfo)
- [`GET /api/chapter/info`](#get-apichapterinfo)
- [`GET /api/manga/cover`](#get-apimangacover)
- [`GET /api/manga/chapters`](#get-apimangachapters)

#### Perform and manage downloads
- [`POST /api/download/chapter`](#post-apidownloadchapter)
- [`POST /api/download/chapters`](#post-apidownloadchapters)
- [`GET /api/dl_state/<id>`](#get-apidl_stateid)
- [`GET /api/dl_states/agregate`](#get-apidl_statesagregate)
- [`POST /api/cancel/download/<id>`](#post-apicanceldownloadid)
- [`POST /api/cancel/downloads`](#post-apicanceldownloads)
- [`DELETE /api/downloads/history`](#delete-apidownloadshistory)

#### Manage marks on chapters
- [`GET /api/chapter/mark`](#get-apichaptermark)
- [`PUT /api/chapter/mark/<mark>`](#put-apichaptermarkmark)
- [`PUT /api/chapters/mark/<mark>`](#put-apichaptersmarkmark)
- [`DELETE /api/chapter/mark`](#delete-apichaptermark)
- [`DELETE /api/chapters/mark`](#delete-apichaptersmark)

#### Manage favourite mangas
- [`GET /api/manga/fav`](#get-apimangafav)
- [`PUT /api/manga/fav`](#put-apimangafav)
- [`DELETE /api/manga/fav`](#delete-apimangafav)
- [`GET /api/manga/favs`](#get-apimangafavs)

## `GET /api/ping`

### Example request

```Bash
curl -X GET 'localhost:8090/api/ping'
```

### Example Response

```
HTTP/1.1 200 OK
Content-Type: text/plain

pong
```

[`^ Back to top ^`][top]


## `GET /api/version`

### Example request

```Bash
curl -X GET 'localhost:8090/api/version'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: text/plain

1.1
```

[`^ Back to top ^`][top]


## `GET /api/sites`

Retrieves the list of sites supported by the application.

### Example request

```Bash
curl -X GET 'localhost:8090/api/sites'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

["mangadex.org"]
```

[`^ Back to top ^`][top]


## `GET /api/resource/site`

Checks if a URL is supported by the API. 
If so, indicates the site associated with the downloader for this resource.

Note that the URL doesn't have to link to a chapter or a manga on the website for this to work (see examples below).

### Request parameters

- `url`: The URL of a page on the website (required)

### Example request

```Bash
curl -X GET 'localhost:8090/api/resource/site?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1'
```

### Example response

If the site is known :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"url": "https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1",
	"registered": true,
	"site": "mangadex.org"
}
```

If the site is not known :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"url": "https://example.com",
	"registered": false
}
```

This also works, although the URL is not that of a manga or a chapter :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"url": "https://mangadex.org/my/history",
	"registered": true,
	"site": "mangadex.org"
}
```

[`^ Back to top ^`][top]


## `GET /api/manga/id`

Retrieves the ID of a manga on a website supported by the application.

### Request parameters

- `url`: The URL of the manga on the website (required)

### Example request

```Bash
curl -X GET 'localhost:8090/api/manga/id?url=https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"url": "https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone",
	"id": "cfc3d743-bd89-48e2-991f-63e680cc4edf"
}
```

If the site is not known to the application :
```
HTTP/1.1 404 NOT FOUND

No downloader found for URL "example.com"
```

If the URL doesn't link to any actual manga on the website :
```
HTTP/1.1 400 BAD REQUEST

URL https://mangadex.org does not link to any manga nor chapter on the Mangadex website
```

If the url has not been specified in the request :
```
HTTP/1.1 400 BAD REQUEST

Request is missing the URL parameter
```

[`^ Back to top ^`][top]


## `GET /api/chapter/id`

Retrieves the ID of a chapter on a website supported by the application.

### Request parameters

- `url`: The URL of the chapter on the website (required)

### Example request

```Bash
curl -X GET 'localhost:8090/api/chapter/id?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"url": "https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1",
	"id": "ec562f76-4654-4621-8198-247622955fdd"
}
```

If the site is not known to the application :
```
HTTP/1.1 404 NOT FOUND

No downloader found for URL "example.com"
```

If the URL doesn't link to any actual chapter on the website :
```
HTTP/1.1 400 BAD REQUEST

URL https://mangadex.org does not link to any chapter on the Mangadex website
```

If the url has not been specified in the request :
```
HTTP/1.1 400 BAD REQUEST

Request is missing the URL parameter
```

[`^ Back to top ^`][top]


## `GET /api/manga/info`

Retrieves some general information on a manga. The result is a JSON object with the following attributes :
 - `id`: the identifier of this manga
 - `site`: the site on which this manga is published
 - `title`: the title of the manga
 - `alt_titles`: a list of objects that have a unique key being a language, associated with a title in this language
 - `description`: the description of the manga\*
 - `authors`: a list of objects representing an author with two attributes : `id` and `name`
 - `artists`: a list of objects representing an artist with two attributes : `id` and `name`
 - `genres`: a list of genres
 - `tags`: a list of tags
 - `date`: an object representing the date of publication of the first chapter
     - `day`: the day between 1 and 31\*
	 - `month`: the month between 1 and 12\*
	 - `year`: the full year (e.g. 2021)\*
 - `rating`: one of `safe`, `suggestive`, `erotica` or `pornographic`\*
 - `status`: one of `completed`, `ongoing`, `hiatus`, `cancelled`\*
 - `favourite`: boolean indicating if the manga is a favourite (if requested)

\* may be `null` if unknown

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site
- `includeFav`: `true` if we want to retrieve the favourite boolean

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X GET 'localhost:8090/api/manga/info?url=https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"id": "cfc3d743-bd89-48e2-991f-63e680cc4edf", 
	"title": "Dr. Stone", 
	"alt_titles": [
		{"tr": "Doktor Ta\u015f"}, 
		{"en": "Dr.Stone"}, 
		{"ru": "\u0414\u043e\u043a\u0442\u043e\u0440 \u0421\u0442\u043e\u0443\u043d"}, 
		{"ru": "\u041f\u0440\u043e\u0444\u0435\u0441\u0441\u043e\u0440 \u043a\u0430\u043c\u0435\u043d\u043d\u043e\u0433\u043e \u0432\u0435\u043a\u0430"}, 
		{"ja": "\u30c9\u30af\u30bf\u30fc\u30b9\u30c8\u30fc\u30f3"}
	], 
	"description": "...", 
	"authors": [
		{
			"id": "6afbe7ae-36a4-4d95-aacc-610bd9c64332", 
			"name": "Inagaki Riichiro"
		}
	], 
	"artists": [
		{
			"id": "e2363c83-22b9-45ba-af27-2c7bcbef7d63", 
			"name": "Boichi"
		}
	], 
	"tags": ["Sci-Fi", "Action", "Comedy", "Survival", "Adventure", "Post-Apocalyptic", "Drama", "Slice of Life", "Cooking", "Supernatural", "Mystery"], 
	"lang": "ja", 
	"date": {"day": null, "month": null, "year": 2017}, 
	"rating": "safe", 
	"status": "ongoing"
}
```

[`^ Back to top ^`][top]


## `GET /api/chapter/info`

Retrieves some general information on a chapter. The result is a JSON object with the following attributes :
 - `id`: the identifier of this chapter
 - `manga`: the identifier of the manga
 - `volume`: the number of the volume in which this chapter was published\*
 - `chapter`: the number of this chapter
 - `title`: the title of this chapter\*
 - `lang`: the language in which this chapter is published (`"en"`, `"jp"`, `"fr"`, ...)
 - `pages`: the number of pages in this chapter
 - `team`: an object containing data on the translation/scanlation team\*
     - `id`: the identifier of the team on the website
	 - `name`: the name of the team
	 - `site`: the website of the scanlation team\*
 - `date`: an object representing the date at which this chapter was published/modified
     - `day`: the day between 1 and 31\*
	 - `month`: the month between 1 and 12\*
	 - `year`: the full year (e.g. 2021)\*
 - `mark`: the mark of the chapter (if requested), can be `"DOWNLOADED"`, `"IGNORED"` or `null`\*

\* may be `null` if unknown

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site
- `includeMark`: `true` if we want to retrieve the mark of the chapter

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X GET 'localhost:8090/api/chapter/info?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"volume": 1, 
	"chapter": 1, 
	"title": "Z=1: Stone World", 
	"lang": "en", 
	"pages": 48, 
	"team": {
		"id": "9348bde7-ed3e-43e7-88c6-0edcd1debb88", 
		"name": "Mangastream", 
		"site": "https://readms.net/"
	}, 
	"date": {
		"day": 30, 
		"month": 6, 
		"year": 2020
	},
	"id": "ec562f76-4654-4621-8198-247622955fdd", 
	"manga": "cfc3d743-bd89-48e2-991f-63e680cc4edf"
}
```

[`^ Back to top ^`][top]


## `GET /api/manga/cover`

Retrieves the cover art for a manga. 

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site
- `base64`: if set to `true`, a base64 representation of the image will be returned instead of binary data. The `Original-Content-Type` header will then be set to the actual MIME type of the image.

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X GET 'localhost:8090/api/manga/cover?site=mangadex.org&id=cfc3d743-bd89-48e2-991f-63e680cc4edf&base64=false'
```

### Example response

Without the `base64` parameter, or `base64 != true`:
```
HTTP/1.1 200 OK
Content-Type: image/jpeg

<binary data>
```

With `base64=true` :
```
HTTP/1.1 200 OK
Content-Type: text/plain
Original-Content-Type: image/jpeg

<base64 data>
```

[`^ Back to top ^`][top]


## `GET /api/manga/chapters`

Retrieves the list of chapters for a manga. The result is a JSON object where the keys are chapter IDs and the values are objects with the following attributes :
 - `volume`: the number of the volume in which this chapter was published\*
 - `chapter`: the number of this chapter
 - `title`: the title of this chapter\*
 - `lang`: the language in which this chapter is published (`"en"`, `"jp"`, `"fr"`, ...)
 - `pages`: the number of pages in this chapter
 - `team`: an object containing data on the translation/scanlation team\*
     - `id`: the identifier of the team on the website
	 - `name`: the name of the team
	 - `site`: the website of the scanlation team\*
 - `date`: an object representing the date at which this chapter was published/modified
     - `day`: the day between 1 and 31\*
	 - `month`: the month between 1 and 12\*
	 - `year`: the full year (e.g. 2021)\*
 - `mark`: the mark of the chapter (if requested), can be `"DOWNLOADED"`, `"IGNORED"` or `null`\*

\* may be `null` if unknown

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site
- `includeMarks`: `true` if we want to retrieve the marks of the chapters

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X GET 'localhost:8090/api/manga/chapters?url=https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"f97f19bb-d12d-4b7c-93fb-58c5ace73d09": {
		"volume": 1, 
		"chapter": 1, 
		"title": "Stone World", 
		"lang": "en", 
		"pages": 48, 
		"team": {
			"id": "58b9d508-86d0-48f1-866a-68323a177743", 
			"name": "Jaimini's~box~", 
			"site": "http://jaiminisbox.com"
		}
	},
	...
}
```

[`^ Back to top ^`][top]


## `POST /api/download/chapter`

Starts the download of a chapter to the server and returns an identifier that will allow to track the progress of the download.

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site
- `addMark`: `true` if we want to mark the chapter as `DOWNLOADED` if the download is successful

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example requests

```Bash
curl -X POST 'localhost:8090/api/download/chapter?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1'
```

```Bash
curl -X POST 'localhost:8090/api/download/chapter?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1&addMark=true'
```

### Example response

```
HTTP/1.1 202 ACCEPTED
Content-Type: application/json

"yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn"
```

[`^ Back to top ^`][top]


## `POST /api/download/chapters`

Starts the downloads for several chapters and returns a list of download identifiers.

### Request parameter (optional)

- `addMark`: `true` if we want to mark the chapters as `DOWNLOADED` if the download is successful

### Request content

The body of the request must be a json object that can have two fields :
 - `urls`: a list of URLs of chapters to download, potentially on several sites.
 - `sites`: an object where the keys are site names and the values are lists of chapter identifiers

*Note : if one field is associated to an empty list/object, you don't need to specify it*

### Example request

```Bash
curl --header "Content-Type: application/json" -d '{"urls": ["https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1"], "sites": {"mangadex.org": ["75011fda-0eec-4617-a677-e4eb8bb8f55b", "8a82dbff-60a2-4131-83c7-b42df0f7864d"]}}' -X POST 'localhost:8090/api/download/chapters'
```

### Example responses

```
HTTP/1.1 202 ACCEPTED
Content-Type: application/json

["yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn", "PGUiBStCng-vty0nSduNHegMunyIMWnN", "h2h2UQA_O05AMkkbZJs7mouXd3G5gQ1S"]
```

If the content type is not `application/json` or the json is invalid :
```
HTTP/1.1 400 BAD REQUEST

Content of request is not well-formed JSON
```

[`^ Back to top ^`][top]


## `GET /api/dl_state/<id>`

Retrieves the state of a download.

### Example request

```Bash
curl -X GET 'localhost:8090/api/dl_state/yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn'
```

### Example responses

For a download that was just created :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"file": "Dr. Stone -.- C1 Z=1: Stone World", 
	"status": "CREATED", 
	"completion": 0.0, 
	"size": 0,
	"created": 1645036100444
}
```

For a download that is waiting in the queue :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"file": "Dr. Stone -.- C1 Z=1: Stone World", 
	"status": "QUEUED", 
	"completion": 0.0, 
	"size": 0,
	"created": 1645036100444
}

For a download that is running :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"file": "Dr. Stone -.- C1 Z=1: Stone World", 
	"status": "PROCESSING", 
	"completion": 0.25, 
	"size": 3590383,
	"created": 1645036100444, 
	"begin": 1645036116016
}
```

For a download that is in the process of saving files to the disk :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"file": "Dr. Stone -.- C1 Z=1: Stone World", 
	"status": "SAVING", 
	"completion": 1.0, 
	"size": 9760627,
	"created": 1645036100444, 
	"begin": 1645036116016
}

For a download that succeeded :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"file": "Dr. Stone -.- C1 Z=1: Stone World", 
	"status": "COMPLETE", 
	"completion": 1.0, 
	"size": 9760627,
	"created": 1645036100444, 
	"begin": 1645036116016, 
	"end": 1645036142822
}
```

For a download that failed :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"file": "Dr. Stone -.- C1 Z=1: Stone World", 
	"status": "FAILED", 
	"completion": 0.33, 
	"size": 4242726,
	"created": 1645036100444, 
	"begin": 1645036116016, 
	"end": 1645036142822
}
```

For a download that was cancelled :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"file": "Dr. Stone -.- C1 Z=1: Stone World", 
	"status": "CANCELLED", 
	"completion": 0.0, 
	"size": 0,
	"created": 1645036100444, 
	"end": 1645036142822
}
```

For a download that doesn't exist :
```
HTTP/1.1 404 NOT FOUND

No download registered with the id AAAAAAAAAAAAAAAA
```

[`^ Back to top ^`][top]


## `GET /api/dl_states/agregate`

Retrieves the state of multiple downloads at once.

### Example requests

With arguments in the request parameters :
```Bash
curl -X GET 'localhost:8090/api/dl_states/agregate?ids=yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn&ids=PGUiBStCng-vty0nSduNHegMunyIMWnN&ids=AAAAAAAAAAAA'
```

Or equivalently :
```Bash
curl -X GET 'localhost:8090/api/dl_states/agregate?ids[]=yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn&ids[]=PGUiBStCng-vty0nSduNHegMunyIMWnN&ids[]=AAAAAAAAAAAA'
```

If there are no arguments in the request parameters, simply retrieves the states for all existing downloads :
```Bash
curl -X GET 'localhost:8090/api/dl_states/agregate'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn": {
		"file": "Dr. Stone -.- C1 Z=1: Stone World", 
		"status": "COMPLETE", 
		"completion": 1.0, 
		"created": 1645036100444, 
		"begin": 1645036116016, 
		"end": 1645036142822
	},
	"PGUiBStCng-vty0nSduNHegMunyIMWnN": {
		"file": "Dr. Stone -.- C1 Z=1: Stone World", 
		"status": "PROCESSING", 
		"completion": 0.375, 
		"created": 1645036100456, 
		"begin": 1645036142892
	},
	"AAAAAAAAAAAA": null
}
```

*Note : If an id doesn't correspond to a registered download, the associated value in the response will be `null` but the HTTP return code will still be `200`*

[`^ Back to top ^`][top]


## `POST /api/cancel/download/<id>`

Cancels a download that has been previously submitted, leaving it in the `CANCELLED` state. This is only possible if the download is still in the queue, a download that already begun cannot be stopped. 

A boolean is returned, indicating wether the download was successfully stopped or not.

### Example request

```Bash
curl -X POST 'localhost:8090/api/cancel/download/yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn'
```

### Example responses

If the download was succesfully stopped :
```
HTTP/1.1 200 OK
Content-Type: application/json

true
```

If the download could not be stopped :
```
HTTP/1.1 200 OK
Content-Type: application/json

false
```

For a download that doesn't exist :
```
HTTP/1.1 404 NOT FOUND

No download registered with the id AAAAAAAAAAAAAAAA
```

[`^ Back to top ^`][top]


## `POST /api/cancel/downloads`

Cancels several downloads at once, returning for each one a boolean indicating if it was successfully stopped.

### Example requests

With arguments in the request parameters :
```Bash
curl -X POST 'localhost:8090/api/cancel/downloads?ids=yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn&ids=PGUiBStCng-vty0nSduNHegMunyIMWnN&ids=AAAAAAAAAAAA'
```

Or equivalently :
```Bash
curl -X POST 'localhost:8090/api/cancel/downloads?ids[]=yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn&ids[]=PGUiBStCng-vty0nSduNHegMunyIMWnN&ids[]=AAAAAAAAAAAA'
```

With the arguments in the request's body (only checked if no request parameters are found) :
```Bash
curl --header "Content-Type: application/json" -d '["yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn", "PGUiBStCng-vty0nSduNHegMunyIMWnN", "AAAAAAAAAAAA"]' -X POST 'localhost:8090/api/cancel/downloads'
```

### Example responses

```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn": false,
	"PGUiBStCng-vty0nSduNHegMunyIMWnN": true,
	"AAAAAAAAAAAA": false
}
```

If no list of ids is provided :
```
HTTP/1.1 400 BAD REQUEST

Missing ids of downloads to cancel
```

*Note : If an id doesn't correspond to a registered download, the associated value in the response will be `false` but the HTTP return code will still be `200`*

[`^ Back to top ^`][top]


## `DELETE /api/downloads/history`

Clears the history of downloaded chapters.

### Example request

```Bash
curl -X DELETE 'localhost:8090/api/downloads/history'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"deleted": 3
}
```

[`^ Back to top ^`][top]


## `GET /api/chapter/mark`

Retrieves the mark of a chapter, if any. A chapter can be marked with `DOWNLOADED` or `IGNORED`.

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X GET 'localhost:8090/api/chapter/mark?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1'
```

### Example responses

```
HTTP/1.1 200 OK
Content-Type: application/json

"DOWNLOADED"
```

If the chapter is not tagged :
```
HTTP/1.1 200 OK
Content-Type: application/json

null
```

[`^ Back to top ^`][top]


## `PUT /api/chapter/mark/<mark>`

Sets the mark of a chapter to the one specified in the URL, either `DOWNLOADED` or `IGNORED`.

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X PUT 'localhost:8090/api/chapter/mark/DOWNLOADED?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1'
```

### Example response

```
HTTP/1.1 201 CREATED
```

[`^ Back to top ^`][top]


## `PUT /api/chapters/mark/<mark>`

Sets the mark of one or several chapters to the one specified in the URL, either `DOWNLOADED` or `IGNORED`.

### Request content

The body of the request must be a json object that can have two fields :
 - `urls`: a list of URLs of chapters to download, potentially on several sites.
 - `sites`: an object where the keys are site names and the values are lists of chapter identifiers

*Note : if one field is associated to an empty list/object, you don't need to specify it*

### Example request

```Bash
curl --header "Content-Type: application/json" -d '{"urls": ["https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1"], "sites": {"mangadex.org": ["75011fda-0eec-4617-a677-e4eb8bb8f55b", "8a82dbff-60a2-4131-83c7-b42df0f7864d"]}}' -X PUT 'localhost:8090/api/chapters/mark/DOWNLOADED'
```

### Example responses

```
HTTP/1.1 201 CREATED
```

If the content type is not `application/json` or the json is invalid :
```
HTTP/1.1 400 BAD REQUEST

Content of request is not well-formed JSON
```

[`^ Back to top ^`][top]


## `DELETE /api/chapter/mark`

Removes the mark of a chapter, if it has one.

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X DELETE 'localhost:8090/api/chapter/mark?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1'
```

### Example response

```
HTTP/1.1 200 OK
```

[`^ Back to top ^`][top]


## `DELETE /api/chapters/mark`

Removes the marks of one or several chapters, for those who have one.

### Request content

The body of the request must be a json object that can have two fields :
 - `urls`: a list of URLs of chapters to download, potentially on several sites.
 - `sites`: an object where the keys are site names and the values are lists of chapter identifiers

*Note : if one field is associated to an empty list/object, you don't need to specify it*

### Example request

```Bash
curl --header "Content-Type: application/json" -d '{"urls": ["https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1"], "sites": {"mangadex.org": ["75011fda-0eec-4617-a677-e4eb8bb8f55b", "8a82dbff-60a2-4131-83c7-b42df0f7864d"]}}' -X DELETE 'localhost:8090/api/chapters/mark'
```

### Example responses

```
HTTP/1.1 200 OK
```

If the content type is not `application/json` or the json is invalid :
```
HTTP/1.1 400 BAD REQUEST

Content of request is not well-formed JSON
```

[`^ Back to top ^`][top]


## `GET /api/manga/marked`

Fetches the list of marked chapters for a manga. The result will be a JSON object where the keys are chapter identifiers and the values are marks (`DOWNLOADED` or `IGNORED`)

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X GET 'localhost:8090/api/manga/marked?url=https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone'
```

### Example response

```
HTTP/1.1 200 OK

{
	"ec562f76-4654-4621-8198-247622955fdd": "DOWNLOADED",
	"75011fda-0eec-4617-a677-e4eb8bb8f55b": "IGNORED"
}
```

[`^ Back to top ^`][top]


## `GET /api/manga/fav`

Retrieves a boolean indicating if a manga is set as a favourite or not.

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X GET 'localhost:8090/api/manga/fav?url=https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

true
```

[`^ Back to top ^`][top]


## `PUT /api/manga/fav`

Adds a manga to the list of favourites.

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X PUT 'localhost:8090/api/manga/fav?url=https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone'
```

### Example responses

If the manga was successfully added :
```
HTTP/1.1 201 CREATED
```

If the manga was already a favourite :
```
HTTP/1.1 200 OK
```

[`^ Back to top ^`][top]


## `DELETE /api/manga/fav`

Removes a manga to the list of favourites.

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X DELETE 'localhost:8090/api/manga/fav?url=https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone'
```

### Example response

```
HTTP/1.1 200 OK
```

[`^ Back to top ^`][top]


## `GET /api/manga/favs`

Retrieves a JSON objects where the keys are sites and the values are lists of manga identifiers (the favourites). 

### Request parameters

- `site`: if present, only returns the identifier for the specified site
- `includeInfo`: if `true`, the values associated with the sites will be JSON objects where the keys are manga identifiers and the values are manga info

### Example requests

```Bash
curl -X GET 'localhost:8090/api/manga/favs'
```

```Bash
curl -X GET 'localhost:8090/api/manga/favs?site=mangadex.org&includeInfo=true'
```

### Example responses

```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"mangadex.org": [
		"cfc3d743-bd89-48e2-991f-63e680cc4edf",
		"a25e46ec-30f7-4db6-89df-cacbc1d9a900", 
		"28b5d037-175d-4119-96f8-e860e408ebe9"
	],
	"example.com": [
		"xLlgbg9d8nR2pX2-ry",
		"fDWYhxZ4UYRPVoZuGX"
	]
}
```

With the info included :
```
HTTP/1.1 200 OK
Content-Type: application/json

{
	"mangadex.org": {
		"cfc3d743-bd89-48e2-991f-63e680cc4edf": {
			"id": "cfc3d743-bd89-48e2-991f-63e680cc4edf", 
			"title": "Dr. Stone", 
			"alt_titles": [
				{"tr": "Doktor Ta\u015f"}, 
				{"en": "Dr.Stone"}, 
				{"ru": "\u0414\u043e\u043a\u0442\u043e\u0440 \u0421\u0442\u043e\u0443\u043d"}, 
				{"ru": "\u041f\u0440\u043e\u0444\u0435\u0441\u0441\u043e\u0440 \u043a\u0430\u043c\u0435\u043d\u043d\u043e\u0433\u043e \u0432\u0435\u043a\u0430"}, 
				{"ja": "\u30c9\u30af\u30bf\u30fc\u30b9\u30c8\u30fc\u30f3"}
			], 
			"description": "...", 
			"authors": [
				{
					"id": "6afbe7ae-36a4-4d95-aacc-610bd9c64332", 
					"name": "Inagaki Riichiro"
				}
			], 
			"artists": [
				{
					"id": "e2363c83-22b9-45ba-af27-2c7bcbef7d63", 
					"name": "Boichi"
				}
			], 
			"tags": ["Sci-Fi", "Action", "Comedy", "Survival", "Adventure", "Post-Apocalyptic", "Drama", "Slice of Life", "Cooking", "Supernatural", "Mystery"], 
			"lang": "ja", 
			"date": {"day": null, "month": null, "year": 2017}, 
			"rating": "safe", 
			"status": "ongoing"
		}
	}
}
```

[`^ Back to top ^`][top]


## `POST /api/download/chapters/new`

## `POST /api/download/chapters/allnew`


[top]: #nagato-api