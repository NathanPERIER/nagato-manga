# How to deploy Nagato-Manga on your server

## Docker deployment (recommanded)

There is currently no official build available, you must build the image yourself for now.

### Build the Docker image

Building a Docker image is super simple, just make sure you have [Docker installed](https://docs.docker.com/engine/install/). Then, you can run the following commands :

```Bash
$ git clone 'this repository'
$ cd nagato-manga/api
$ docker build .
```

### Set up the container

In the following code, replace `nagato-api` by the ID provided by Docker at the end of the `docker build`. You can see the list of you images with `docker images`.

You can deploy the container with the following command that will expose the API on port `8000` :

```Bash
docker run -d \
    --name nagato-api \
	-p 8000:8090 \
	-v /path/to/downloads:/data \
	-v /path/to/config:/opt/nagato-api/config \
	-e NAGATO_API_PORT=8090
	nagato-api
```

By default there is only one destination folder for all downloads, which is `/data`. This can change however if you edit the configuration file, as you can define a specific destination folder for any downloader. When you tweak such parameters, make sure to edit the binds and mounts accordingly.

As for the configuration file themselves, you don't necessarily have to modify them. You can set most global configuration with environment variables, so you will only have to meddle with the configuration files if you want to have a different configuration for a specific downloader (more details [here](configuration.md)). The configuration files will be created at the first launch of the API if they don't exist yet. You can also copy the json files in [the default configuration](/api/default-config) and put them in the folder that will be mapped onto `/opt/nagato-api/config`. If you switch to a newer version of the API with configuration entries that don't exist in your files, they will be added automatically.

Alternatively, you can use `docker-compose`. An example file equivalent to the code above is available [here](examples/docker-compose.yml).

## Manual deployment

If you want to deploy the API without Docker, you will need python >= 3.6 and pip3 to be installed.

```Bash
$ git clone 'this repository'
$ cd nagato-manga/api
$ pip3 install -r requirements.txt # Only the first time or if missing dependencies after a pull
$ gunicorn --config default-config/gunicorn.conf.py nagato-api:app
```
