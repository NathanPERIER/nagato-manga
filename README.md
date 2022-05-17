# nagato-manga

Nagato is an API that is intended to download mangas on a server from various websites. 

## Supported sites

| Site           | Downloader           |
|----------------|----------------------|
| [mangadex.org] | `MangadexDownloader` |

## How to install

You can run the API with Docker easily :

```Bash
docker run -d \
    --name nagato-api \
    -p 8000:8090 \
    -v /path/to/downloads:/data \
    -v /path/to/config:/opt/nagato-api/config \
    -v /path/to/database:/opt/nagato-api/nagato.db \
    elpain/nagato-api:latest
```

More information [here](doc/deployment.md).

## Contribute

This project uses downloaders to get the chapters and various data. If you need to download from a site that is not supported, you can create your own downloader. We will gladly include new downloaders to this repository, for this please be sure to read [this documentation](doc/downloaders.md) and to work in a branch called `dl-<site>`.


[mangadex.org]: https://mangadex.org/