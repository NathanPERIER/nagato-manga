#!/usr/bin/python3

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt='%d/%m/%Y %H:%M:%S')

from nagato.downloaders.base import BaseDownloader
from nagato.downloaders import downloaderForSite, listSites, siteForURL, downloaderForURL
from nagato.utils import errors, params

import json
import base64
from flask import Flask, Response, request

app = Flask('nagato-api')

errors.setHandlers(app)


@app.route('/api/ping', methods=['GET'])
def getPing() :
	return Response('pong', 200)

@app.route('/api/version', methods=['GET'])
def getVersion() :
	return Response('1.0', 200)

@app.route('/api/sites', methods=['GET'])
def getSites() :
	return Response(json.dumps(listSites()), 200, content_type='application/json')


@app.route('/api/manga/id', methods=['GET'])
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
@params.mangaFromArgs
def getMangaInfo(dl: BaseDownloader, manga_id) :
	res = dl.getMangaInfo(manga_id)
	return Response(json.dumps(res), 200, content_type='application/json')


@app.route('/api/chapter/info', methods=['GET'])
@params.chapterFromArgs
def getChapterInfo(dl: BaseDownloader, chapter_id) :
	res = dl.getChapterInfo(chapter_id)
	return Response(json.dumps(res), 200, content_type='application/json')


@app.route('/api/manga/cover', methods=['GET'])
@params.mangaFromArgs
def getMangaCover(dl: BaseDownloader, manga_id) :
	res = dl.getCover(manga_id)
	mime_type = params.imageMimeType(res)
	if 'base64' in request.args and request.args.get('base64') == 'true' :
		b64 = base64.b64encode(res)
		return Response(b64, 200, content_type='text/plain', headers={'Original-Content-Type': mime_type})
	return Response(res, 200, content_type=mime_type)


@app.route('/api/manga/chapters', methods=['GET'])
@params.mangaFromArgs
def getMangaChapters(dl: BaseDownloader, manga_id) :
	res = dl.getChapters(manga_id)
	return Response(json.dumps(res), 200, content_type='application/json')


@app.route('/api/download/chapter', methods=['POST'])
@params.chapterFromArgs
def postChapterDownloadParam(dl: BaseDownloader, chapter_id) :
	res = dl.downloadChapters([chapter_id])[0]
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/download/chapters', methods=['POST'])
@params.chaptersFromContent
def postChaptersDownloadBody(data: dict) :
	res = []
	for site_data in data.values() :
		dl: BaseDownloader = site_data['downloader']
		res.extend(dl.downloadChapters(site_data['chapters']))
	return Response(json.dumps(res), 200, content_type='application/json')

