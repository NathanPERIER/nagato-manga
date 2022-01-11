#!/usr/bin/python3
import logging
logging.basicConfig(level=logging.INFO)

from nagato.downloaders import forURL as downloaderForURL

downloaderForURL('https://mangadex.org/title/6e445564-d9a8-4862-bff1-f4d6be6dba2c/karakai-jouzu-no-takagi-san').f()

