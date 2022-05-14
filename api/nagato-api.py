#!/usr/bin/python3

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt='%d/%m/%Y %H:%M:%S')

from nagato.downloaders.base import BaseDownloader
from nagato.downloaders import listSites, siteForURL, downloaderForURL, downloaderForSite
from nagato.utils import errors, params, threads, database

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
	return Response('1.1', 200)

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
	if 'includeFav' in request.args and request.args['includeFav'] == 'true' :
		res['favourite'] = dl.isMangaStarred(manga_id)
	return Response(json.dumps(res), 200, content_type='application/json')


@app.route('/api/chapter/info', methods=['GET'])
@params.chapterFromArgs
def getChapterInfo(dl: BaseDownloader, chapter_id) :
	res = dl.getChapterInfo(chapter_id)
	if 'includeMark' in request.args and request.args['includeMark'] == 'true' :
		res['mark'] = dl.getChapterMarks([chapter_id])[chapter_id]
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
	if 'includeMarks' in request.args and request.args['includeMarks'] == 'true' :
		marks = dl.getChaptersMarksForManga(manga_id)
		for chapter_id, chapter_info in res.items() :
			chapter_info['mark'] = marks[chapter_id] if chapter_id in marks else None
	return Response(json.dumps(res), 200, content_type='application/json')


@app.route('/api/download/chapter', methods=['POST'])
@params.chapterFromArgs
def postChapterDownload(dl: BaseDownloader, chapter_id) :
	register_mark = 'addMark' in request.args and request.args['addMark'] == 'true'
	res = dl.downloadChapters([chapter_id], register_mark)[0]
	return Response(json.dumps(res), 202, content_type='application/json')

@app.route('/api/download/chapters', methods=['POST'])
@params.chaptersFromContent
def postChaptersDownload(data: dict) :
	register_mark = 'addMark' in request.args and request.args['addMark'] == 'true'
	res = []
	for site_data in data.values() :
		dl: BaseDownloader = site_data['downloader']
		res.extend(dl.downloadChapters(site_data['chapters'], register_mark))
	return Response(json.dumps(res), 202, content_type='application/json')

@app.route('/api/dl_state/<dl_id>', methods=['GET'])
def getDownloadState(dl_id) :
	res = threads.getDownloadState(dl_id)
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/dl_states/agregate', methods=['GET'])
def getDownloadStates() :
	ids = None
	if 'ids' in request.args :
		ids = request.args.getlist('ids')
	elif 'ids[]' in request.args :
		ids = request.args.getlist('ids[]')
	# Note : if `None`, just retrieve all the current downloads
	res = threads.getAllDownloadStates(ids)
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/cancel/download/<dl_id>', methods=['POST'])
def postCancelDownload(dl_id) :
	res = threads.cancelDownload(dl_id)
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/cancel/downloads', methods=['POST'])
def postCancelDownloads() :
	if 'ids' in request.args :
		ids = request.args.getlist('ids')
	elif 'ids[]' in request.args :
		ids = request.args.getlist('ids[]')
	else :
		ids = request.get_json(silent=True)
	if ids is None :
		raise errors.ApiQueryError('Missing ids of downloads to cancel')
	res = threads.cancelDownloads(ids)
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/downloads/history', methods=['DELETE'])
def deleteDownloadsHistory() :
	return {
		'deleted': threads.clearHistory()
	}

@app.route('/api/chapter/mark', methods=['GET'])
@params.chapterFromArgs
def getChapterMark(dl: BaseDownloader, chapter_id) :
	res = dl.getChapterMarks([chapter_id])[chapter_id]
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/chapter/mark/<mark>', methods=['PUT'])
@params.chapterFromArgs
def putChapterMark(dl: BaseDownloader, chapter_id, mark: str) :
	try :
		mark = database.ChapterMark[mark]
	except KeyError :
		raise errors.ApiQueryError(f"Invalid mark: {mark}")
	res = dl.setChapterMarks([chapter_id], mark)
	return Response(status=201 if res else 200)

@app.route('/api/chapters/mark/<mark>', methods=['PUT'])
@params.chaptersFromContent
def putChaptersMark(data: dict, mark: str) :
	try :
		mark = database.ChapterMark[mark]
	except KeyError :
		raise errors.ApiQueryError(f"Invalid mark: {mark}")
	res = False
	for site_data in data.values() :
		dl: BaseDownloader = site_data['downloader']
		res = dl.setChapterMarks(site_data['chapters'], mark) or res
	return Response(status=201 if res else 200)

@app.route('/api/chapter/mark', methods=['DELETE'])
@params.chapterFromArgs
def deleteChapterMark(dl: BaseDownloader, chapter_id) :
	dl.setChapterMarks([chapter_id], None)
	return Response(status=200)

@app.route('/api/chapters/mark', methods=['DELETE'])
@params.chaptersFromContent
def deleteChaptersMark(data: dict) :
	for site_data in data.values() :
		dl: BaseDownloader = site_data['downloader']
		dl.setChapterMarks(site_data['chapters'], None)
	return Response(status=200)

@app.route('/api/manga/fav', methods=['GET'])
@params.mangaFromArgs
def getMangaFav(dl: BaseDownloader, manga_id) :
	res = dl.isMangaStarred(manga_id)
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/manga/fav', methods=['PUT', 'DELETE'])
@params.mangaFromArgs
def changeMangaFav(dl: BaseDownloader, manga_id) :
	res = dl.setMangaStar(manga_id, request.method == 'PUT')
	return Response(status=201 if res and request.method == 'PUT' else 200)

@app.route('/api/manga/favs', methods=['GET'])
def getMangaFavs() :
	if 'site' in request.args :
		site = request.args['site']
		dl = downloaderForSite(site)
		res = {
			site: dl.getStarredMangas()
		}
	else :
		with database.getConnection() as con :
			cur = con.cursor()
			res = database.SqlMangaEntry.getAllStarred(cur)
	if 'includeInfo' in request.args and request.args['includeInfo'] == 'true' :
		sites = listSites()
		for site, manga_ids in res.items() :
			if site in sites :
				dl = downloaderForSite(site)
				res[site] = {manga_id: dl.getMangaInfo(manga_id) for manga_id in manga_ids}
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/manga/marked', methods=['GET'])
@params.mangaFromArgs
def getMangaMarked(dl: BaseDownloader, manga_id) :
	res = dl.getChaptersMarksForManga(manga_id)
	return Response(json.dumps(res), 200, content_type='application/json')

@app.route('/api/download/chapters/new', methods=['POST'])
@params.mangaFromArgs
def postDownloadNewChapters(dl: BaseDownloader, manga_id) :
	res = dl.downloadUnmarked(manga_id)
	return Response(json.dumps(res), 200, content_type='application/json')

