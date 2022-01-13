#!/usr/bin/python3
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt='%d/%m/%Y %H:%M:%S')

import json
from flask import Flask, Response, request

from nagato.downloaders.base import BaseDownloader
from nagato.downloaders import listSites, siteForURL, downloaderForURL
from nagato.utils import errors

app = Flask(__name__)

@app.route('/api/ping', methods=['GET'])
def getPing() :
	return Response('pong', 200)

@app.route('/api/sites', methods=['GET'])
def getSites() :
	return Response(json.dumps(listSites()), 200, content_type='application/json')


@app.route('/api/manga/id', methods=['GET'])
@errors.wrap
def getMangaId() :
	if 'url' not in request.args :
		return Response('Request is missing the URL parameter', 400)
	url = request.args.get('url')
	manga_id = downloaderForURL(url).getMangaId(url)
	res = {
		'url': url,
		'id': manga_id
	}
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/chapter/id', methods=['GET'])
@errors.wrap
def getChapterId() :
	if 'url' not in request.args :
		return Response('Request is missing the URL parameter', 400)
	url = request.args.get('url')
	chapter_id = downloaderForURL(url).getChapterId(url)
	res = {
		'url': url,
		'id': chapter_id
	}
	return Response(json.dumps(res), 200, content_type='application/json')


@app.route('/api/resource/site', methods=['GET'])
def getResourceSite() :
	if 'url' not in request.args :
		return Response('Request is missing the URL parameter', 400)
	url = request.args.get('url')
	site = siteForURL(url)
	res = {
		'url': url,
		'site': site
	}
	return Response(json.dumps(res), 200, content_type='application/json')


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


# /api/download/chapter
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
