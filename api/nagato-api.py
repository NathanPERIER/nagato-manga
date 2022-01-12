#!/usr/bin/python3
import logging

from werkzeug.wrappers import response
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt='%d/%m/%Y %H:%M:%S')

from flask import Flask, Response, request

from nagato.downloaders.base import BaseDownloader
from nagato.downloaders import forURL as downloaderForURL

app = Flask(__name__)

@app.route('/api/ping', methods=['GET'])
def getPing() :
	return Response('"pong"', 200, content_type='application/json')

@app.route('/api/manga/id', methods=['GET'])
def getMangaId() :
	if 'url' not in request.args :
		return Response('Request is missing an URL parameter', 400)
	url = request.args.get('url')
	dl = downloaderForURL(url)
	manga_id = dl().getMangaId(url) # FIXME the downloaders should have been instanciated earlier
	return Response(manga_id, 200)

@app.route('/api/chapter/id', methods=['GET'])
def getChapterId() :
	if 'url' not in request.args :
		return Response('Request is missing an URL parameter', 400)
	url = request.args.get('url')
	dl = downloaderForURL(url)
	chapter_id = dl().getChapterId(url) # FIXME the downloaders should have been instanciated earlier
	return Response(chapter_id, 200)


# /api/manga/info
def getMangaInfo() :
	pass

# /api/chapter/info
def getChapterInfo() :
	pass


# /api/manga/chapters
def getMangaChapters() :
	pass


# /api/manga/cover
def getMangaCover() :
	pass


# /api/download/chapters
def postChapterDownloadParam() :
	pass

# /api/download/chapters
def postChaptersDownloadBody() :
	pass

"""
url = 'https://mangadex.org/chapter/19e28470-4239-4cd5-8a56-05f4cf589478/1'

dl_class = downloaderForURL(url)

dl: BaseDownloader = dl_class()

chapter_id = dl.getChapterId(url)

dl.saveToZip([chapter_id])
"""
