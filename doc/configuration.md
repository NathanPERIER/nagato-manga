# Configuring Nagato-Manga

## Configuring the API

The API can be configured via a JSON [configuration file](../api/config/conf.json). It has three main sections that associate properties with values :
 - `api` for the general configuration of the api
 - `global` that sets default values for the properties used by all the downloaders
 - `downloaders` that has une sub-section for each downloader, identified by site

Additionaly, there is a [secondary configuration file](../api/config/env.json) that is structured just like the previous one but associates some properties with an environment variable. Note that all properties don't have to be associated with an environment variable.

For a property, the utility in charge of the configuration of the API will first get all the properties from the main configuration file. Those values can be considered as default values in case there is no environment variable for the property or the environment variable is not set. Then, it checks the second configuration file to see if some values can be taken from the environment, if so they override the values from the first configuration file. This value's type will be inferred from the default configuration : if the default value is a string then it will be considered as a string, else it will be considered as JSON data and parsed accordingly.

You can also set the `NAGATO_API_HOST` and `NAGATO_API_PORT` indicating the host and port used by the API, defaulting respectively to `0.0.0.0` and `8090`. 

### General configuration

The `api` section contains the following attributes that are relevant to the general behaviour of the API :
 - `request.cache.maxlen`: the maximum HTTP requests that can be cached, this can be set to 0 to disable HTTP caching entirely but it is discouraged since certain requests may be repeated quite often.
 - `compression.cbz.additional_data`: a boolean indicating wether or not the API should spend more time (and resources) to infer metadata from the available data on a chapter and a manga for a cbz file. This implies for example loading each image with [`PIL`](https://pillow.readthedocs.io/en/stable/) to check if it is a double page (not implemented yet).

### Configuration of a downloader

The `global` section contains attributes that are common to all downloaders : 
 - `chapters.destination`: the base directory where chapters will be saved
 - `chapters.separate`: boolean indicating if the chapters of a same manga should be grouped in a subfolder (`true`) or if all chapters should be stored in the same folder (`false`)
 - `chapters.method`: the method used to save chapters once they are downloaded, should be one of `file`, `zip` or `cbz` (see below for more details).
 - `chapters.format`: A template for a Python [Template String] that will define the name of the chapter when it is saved to the disk (the name of the cbz/zip file or the name of the folder, depending on the selected storing method). The placeholders that can be used are listed below.

A sub-section in the `downloaders` section can contain any of the attributes listed above, these values will override those in `global`. A custom attribute specific to a downloader can be defined in the corresponding sub-section, its value will then be accessible in the constructor of said downloader via the `config` argument. One can also bound an environment variable to the value of a custom attribute by adding an entry in the `env.conf` file.

| `chapters.method` | chapter saved as ...                             |
|-------------------|--------------------------------------------------|
| `files`           | a folder containing the pages as separate images |
| `zip`             | a zip containing the images                      |
| `cbz`             | a [Comic Book Archive] (fancy zip)               |

The table below lists the placeholders that can be used in a chapter name template. For example, the template could be formatted like so : `[${id}] $manga C$chapter`.

| Template placeholder | Meaning                                                        |
|----------------------|----------------------------------------------------------------|
| `id`                 | The identifier of the chapter                                  |
| `title`              | The title of the chapter                                       |
| `manga_id`           | The identifier of the manga                                    |
| `manga`              | The title of the manga                                         |
| `volume`             | The number of the volume in which this chapter was published\* |
| `chapter`            | The number of this chapter                                     |
| `lang`               | The language of this chapter                                   |
| `team`               | The name of the translation team\*                             |

\* Can be `None`


[Template String]: https://docs.python.org/3/library/string.html#template-strings
[Comic Book Archive]: https://en.wikipedia.org/wiki/Comic_book_archive