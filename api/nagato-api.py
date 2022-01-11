#!/usr/bin/python3
import logging
from nagato.downloaders.base import BaseDownloader
logging.basicConfig(level=logging.INFO)

from nagato.downloaders import forURL as downloaderForURL

url = 'https://mangadex.org/chapter/19e28470-4239-4cd5-8a56-05f4cf589478/1'

dl_class = downloaderForURL(url)

dl: BaseDownloader = dl_class()

chapter_id = dl.getChapterId(url)

dl.saveToZip([chapter_id])
