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

- `url`: The URL of the manga on the website

### Example request

```Bash
curl -X GET 'localhost:8090/api/manga/id?url=https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone'
```

### Example response

```
HTTP/1.1 200 OK
Content-type: application/json

{
	"url": "https://mangadex.org/title/cfc3d743-bd89-48e2-991f-63e680cc4edf/dr-stone"
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

- `url`: The URL of the chapter on the website

### Example request

```Bash
curl -X GET 'localhost:8090/api/chapter/id?url=https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1'
```

### Example response

```
HTTP/1.1 200 OK
Content-type: application/json

{
	"url": "https://mangadex.org/chapter/ec562f76-4654-4621-8198-247622955fdd/1"
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

## `GET /api/manga/info`

## `GET /api/chapter/info`

## `GET /api/manga/chapters`

## `GET /api/manga/cover`

## `GET /api/download/chapter`

## `GET /api/download/chapters`

