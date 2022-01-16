# Nagato API

This file lists the available endpoints for the API.

## `GET /api/ping`

### Example request

```Bash
curl -X GET 'localhost:8090/api/ping'
```

### Example Response

```
HTTP/1.1 200 OK

pong
```


## `GET /api/version`

### Example request

```Bash
curl -X GET 'localhost:8090/api/version'
```

### Example response

```
HTTP/1.1 200 OK

1.1
```


## `GET /api/sites`

Retrieves the list of sites supported by the application.

### Example request

```Bash
curl -X GET 'localhost:8090/api/sites'
```

### Example response

```
HTTP/1.1 200 OK
Content-type: application/json

["mangadex.org"]
```

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
Content-type: application/json

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
Content-type: application/json

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
Content-type: application/json

{
	"url": "https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1",
	"registered": true,
	"site": "mangadex.org"
}
```

If the site is not known :
```
HTTP/1.1 200 OK
Content-type: application/json

{
	"url": "https://example.com",
	"registered": false
}
```

This also works, although the URL is not that of a manga or a chapter :
```
HTTP/1.1 200 OK
Content-type: application/json

{
	"url": "https://mangadex.org/my/history",
	"registered": true,
	"site": "mangadex.org"
}
```


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


## `GET /api/chapter/info`

Retrieves some general information on a chapter. The result is a JSON object with the following attributes :
 - `id`: the identifier of this chapter
 - `manga`: the identifier of the manga\*
 - `volume`: the number of the volume in which this chapter was published\*
 - `chapter`: the number of this chapter
 - `title`: the title of this chapter\*
 - `lang`: the language in which this chapter is published (`"en"`, `"jp"`, `"fr"`, ...)\*
 - `pages`: the number of pages in this chapter\*
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
curl -X GET 'localhost:8090/api/manga/cover?site=mangadex.org&id=cfc3d743-bd89-48e2-991f-63e680cc4edf&base64=true'
```


## `GET /api/manga/chapters`

Retrieves the list of chapters for a manga. The result is a JSON object where the keys are chapter IDs and the values are objects with the following attributes :
 - `volume`: the number of the volume in which this chapter was published\*
 - `chapter`: the number of this chapter
 - `title`: the title of this chapter\*
 - `lang`: the language in which this chapter is published (`"en"`, `"jp"`, `"fr"`, ...)\*
 - `pages`: the number of pages in this chapter\*
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


## `POST /api/download/chapter`

## `POST /api/download/chapters`

