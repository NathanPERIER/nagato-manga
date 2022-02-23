
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

