#!/usr/bin/python3

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt='%d/%m/%Y %H:%M:%S')

from nagato.downloaders.base import BaseDownloader
from nagato.downloaders import listSites, siteForURL, downloaderForURL
from nagato.utils import errors
from nagato.utils import http

import json
import base64
from flask import Flask, Response, request

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
		'registered': site is not None
	}
	if site is not None :
		res['site'] = site
	return Response(json.dumps(res), 200, content_type='application/json')


@app.route('/api/manga/info', methods=['GET'])
@errors.wrap
@http.mangaFromArgs
def getMangaInfo(dl: BaseDownloader, manga_id) :
	res = dl.getMangaInfo(manga_id)
	return Response(json.dumps(res), 200, content_type='application/json')


@app.route('/api/chapter/info', methods=['GET'])
@errors.wrap
@http.chapterFromArgs
def getChapterInfo(dl: BaseDownloader, chapter_id) :
	res = dl.getChapterInfo(chapter_id)
	return Response(json.dumps(res), 200, content_type='application/json')


@app.route('/api/manga/cover', methods=['GET'])
@errors.wrap
@http.mangaFromArgs
def getMangaCover(dl: BaseDownloader, manga_id) :
	res = dl.getCover(manga_id)
	mime_type = http.imageMimeType(res)
	if 'base64' in request.args and request.args.get('base64') == 'true' :
		b64 = base64.b64encode(res)
		return Response(b64, 200, content_type='text/plain', headers={'Original-Content-Type': mime_type})
	return Response(res, 200, content_type=mime_type)


@app.route('/api/manga/chapters', methods=['GET'])
@errors.wrap
@http.mangaFromArgs
def getMangaChapters(dl: BaseDownloader, manga_id) :
	res = dl.getChapters(manga_id)
	return Response(json.dumps(res), 200, content_type='application/json')


# /api/download/chapter
# @errors.wrap
# @http.chapterFromArgs
def postChapterDownloadParam(dl: BaseDownloader, chapter_id) :
	pass

# /api/download/chapters
# @errors.wrap
def postChaptersDownloadBody() :
	pass

