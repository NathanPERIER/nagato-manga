# Nagato API

This file lists the available endpoints for the API.

- [`GET /api/ping`](#get-apiping)
- [`GET /api/version`](#get-apiversion)
- [`GET /api/sites`](#get-apisites)
- [`GET /api/resource/site`](#get-apiresourcesite)
- [`GET /api/manga/id`](#get-apimangaid)
- [`GET /api/chapter/id`](#get-apichapterid)
- [`GET /api/manga/info`](#get-apimangainfo)
- [`GET /api/chapter/info`](#get-apichapterinfo)
- [`GET /api/manga/cover`](#get-apimangacover)
- [`GET /api/manga/chapters`](#get-apimangachapters)
- [`POST /api/download/chapter`](#post-apidownloadchapter)
- [`POST /api/download/chapters`](#post-apidownloadchapters)


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

1.0
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
 - `title`: the title of the manga
 - `alt_titles`: a list of objects that have a unique key being a language, associated with a title in this language
 - `description`: the description of the manga\*
 - `authors`: a list of objects representing an author with two attributes : `id` and `name`
 - `artists`: a list of objects representing an artist with two attributes : `id` and `name`
 - `tags`: a list of tags
 - `date`: an object representing the date of publication of the first chapter
     - `day`: the day between 1 and 31\*
	 - `month`: the month between 1 and 12\*
	 - `year`: the full year (e.g. 2021)\*
 - `rating`: one of `safe`, `suggestive`, `erotica` or `pornographic`\*
 - `status`: one of `completed`, `ongoing`, `hiatus`, `cancelled`\*

\* may be `null` if unknown

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

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

\* may be `null` if unknown

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

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

\* may be `null` if unknown

### Request parameters

- `url`: The URL of a page on the website
- `site`: The site for this resource
- `id`: the identifier of this resource on the site

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

**Note** : It is mandatory to set a value for either `url` or `site` and `id` for this request to succeed.

### Example request

```Bash
curl -X POST 'localhost:8090/api/download/chapter?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1'
```

### Example response

```
HTTP/1.1 200 OK
Content-Type: application/json

"yfu7Rf1Xe3UHjwDoA5fp7DxA0jYstHWn"
```

[`^ Back to top ^`][top]


## `POST /api/download/chapters`

[`^ Back to top ^`][top]



[top]: #nagato-api