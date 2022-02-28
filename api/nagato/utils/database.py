
from enum import Enum
from nagato.utils import config

import os
import sqlite3
import logging

logger = logging.getLogger(__name__)


__database_path: str = config.getApiConf('database.path')
if not __database_path.startswith('/') :
	__database_path = os.path.join(config.API_DIR, __database_path)

class SqlConnection :

	def __init__(self, path) :
		self._path = path
	
	def __enter__(self) :
		self._con = sqlite3.connect(self._path)
		return self._con
	
	def __exit__(self, exc_type, exc_value, tb) :
		self._con.close()
		if exc_type is not None :
			return False


class ChapterMark(Enum) :
	DOWNLOADED = 'D'
	IGNORED    = 'I'


def getConnection() :
	return SqlConnection(__database_path)

def tableExists(cur: sqlite3.Cursor, table_name: str) -> bool :
	l = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table_name]).fetchall()
	return len(l) > 0


class SqlMangaEntry :

	def __init__(self, site: str, manga_id: str) :
		self._site = site
		self._id = manga_id
	
	def isStarred(self, cur: sqlite3.Cursor) -> bool :
		c = cur.execute("SELECT * FROM mangas WHERE site=? and id=?", [self._site, self._id])
		return len(c.fetchall()) > 0
	
	def star(self, cur: sqlite3.Cursor) -> bool :
		if self.isStarred(cur) :
			return False
		cur.execute("INSERT INTO mangas VALUES (?, ?)", [self._site, self._id])
		return True
	
	def unstar(self, cur: sqlite3.Cursor) -> bool :
		if not self.isStarred(cur) :
			return False
		cur.execute("DELETE FROM mangas WHERE site=? and id=?", [self._site, self._id])
		return True
	
	def getChaptersWithTags(self, cur: sqlite3.Cursor) -> "dict[str,ChapterMark]" :
		l = cur.execute("SELECT id, mark FROM chapters WHERE site=? and manga=?", [self._site, self._id]).fetchall()
		return {e[0]: ChapterMark(e[1]) for e in l}
	
	def getAllStarred(cur: sqlite3.Cursor) -> "dict[str,list[str]]" :
		l = cur.execute("SELECT site, id FROM mangas").fetchall()
		res = {}
		for e in l :
			if e[0] not in res : 
				res[e[0]] = [e[1]]
			else :
				res[e[0]].append(e[1])
		return res
	
	def getStarredForSite(cur: sqlite3.Cursor, site: str) -> "list[str]" :
		return cur.execute("SELECT id FROM mangas WHERE site=?", [site]).fetchall()

class SqlChapterEntry :
	
	def __init__(self, site: str, chapter_id: str, downloader) :
		self._site = site
		self._id = chapter_id
		self._dl = downloader

	def exists(self, cur: sqlite3.Cursor) -> bool :
		return self.getMark(cur) is not None
	
	def getMark(self, cur: sqlite3.Cursor) :
		l = cur.execute("SELECT mark FROM chapters WHERE site=? and id=?", [self._site, self._id]).fetchall()
		return ChapterMark(l[0][0]) if len(l) > 0 else None

	def setMark(self, cur: sqlite3.Cursor, mark: ChapterMark) -> bool :
		chapter_exists = self.exists(cur)
		if mark is not None and chapter_exists :
			cur.execute("UPDATE chapters SET mark=? WHERE site=? and id=?", [mark.value, self._site, self._id])
			return True
		if mark is not None and not chapter_exists :
			manga = self._dl.getMangaForChapter(self._id)
			cur.execute("INSERT INTO chapters VALUES (?, ?, ?, ?)", [self._site, self._id, manga, mark.value])
			return True
		if mark is None and chapter_exists :
			cur.execute("DELETE FROM chapters WHERE site=? and id=?", [self._site, self._id])
			return True
		return False


with getConnection() as con :

	cur = con.cursor()

	if not tableExists(cur, 'chapters') :
		logger.info('Create table chapters')
		cur.execute(
			'''
			CREATE TABLE chapters (
				site VARCHAR(255) NOT NULL,
				id VARCHAR(255) NOT NULL,
				manga VARCHAR(255) NOT NULL,
				mark CHAR(1) NOT NULL,
				PRIMARY KEY (site, id)
			)
			'''
		)

	if not tableExists(cur, 'mangas') :
		logger.info('Create table mangas')
		cur.execute(
			'''
			CREATE TABLE mangas (
				site VARCHAR(255) NOT NULL,
				id VARCHAR(255) NOT NULL,
				PRIMARY KEY (site, id)
			)
			'''
		)

	con.commit()
