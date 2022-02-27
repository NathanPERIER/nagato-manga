
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
	
	def getChaptersWithTags(self, cur: sqlite3.Cursor) -> "dict[str,str]" :
		l = cur.execute("SELECT id, mark FROM chapters WHERE site=? and manga=?", [self._site, self._id]).fetchall()
		return {e[0]: e[1] for e in l}


class ChapterMark(Enum) :
	DOWNLOADED = 'D'
	IGNORED    = 'I'

class SqlChapterEntry :
	
	def __init__(self, site: str, chapter_id: str, manga_id: str) :
		self._site = site
		self._id = chapter_id
		self._manga = manga_id

	def exists(self, cur: sqlite3.Cursor) -> bool :
		return self.getMark(cur) is not None
	
	def getMark(self, cur: sqlite3.Cursor) :
		l = cur.execute("SELECT mark FROM chapters WHERE site=? and id=? and manga=?", [self._site, self._id, self._manga]).fetchall()
		return ChapterMark(l[0]) if len(l) > 0 else None

	def setMark(self, cur: sqlite3.Cursor, mark: ChapterMark) -> bool :
		chapter_exists = self.exists(cur)
		if mark is not None and chapter_exists :
			cur.execute("UPDATE chapters SET mark=? WHERE site=? and id=? and manga=?", [mark.value, self._site, self._id, self._manga])
			return True
		if mark is not None and not chapter_exists :
			cur.execute("INSERT INTO chapters VALUES (?, ?, ?, ?)", [self._site, self._id, self._manga, mark.value])
			return True
		if mark is None and chapter_exists :
			cur.execute("DELETE FROM chapters WHERE site=? and id=? and manga=?", [self._site, self._id, self._manga])
			return True
		return False


with SqlConnection(__database_path) as con :

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
