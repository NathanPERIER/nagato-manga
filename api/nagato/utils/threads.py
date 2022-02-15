from asyncio.log import logger
from nagato.utils.compression import Archiver

import time
import hashlib
from enum import Enum
from base64 import b64encode
from concurrent.futures import Future, ThreadPoolExecutor
import traceback


_active_downloads = {}

_completed_downloads = {}

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='nagato_dl')


class DownloadState(Enum) :
	CREATED    = 0
	QUEUED     = 1
	PROCESSING = 2
	SAVING     = 3
	COMPLETE   = 4
	FAILED     = -1
	CANCELLED  = -2


def _generateId(t, filename) :
	for _ in range(10) :
		digest = hashlib.md5(f"{t}-{filename}".encode()).digest()
		h = b64encode(digest, b'-_')[:-2].decode('utf-8')
		if h not in _active_downloads and h not in _completed_downloads :
			return h
	raise RuntimeError("Could not attribute and ID to a download thread")


class ChapterDownload :

	def __init__(self, downloader, chapter_id) :
		self._downloader = downloader
		self._chapter = chapter_id
		self._archiver : Archiver = downloader.getArchiver(chapter_id)
		self._creation = time.time()
		self._id = _generateId(self._creation, self._archiver.getFilename())
		self._status = DownloadState.CREATED
		self._future = None
		self._begin = None
		self._end = None
		_active_downloads[self._id] = self
	
	def submit(self) :
		self._creation = time.time() # Update the creation date to be the time of submission (just in case)
		self._status = DownloadState.QUEUED
		self._future = _executor.submit(self.perform)
		self._future.add_done_callback(self.after)
		logger.info('Download {} submitted', self._id)
		return self._id

	def perform(self) :
		try :
			self._begin = time.time()
			self._status = DownloadState.PROCESSING
			with self.getArchiver() as archiver :
				self._downloader.downloadChapter(self._chapter, archiver)
				self._status = DownloadState.SAVING
			self._status = DownloadState.COMPLETE
		except Exception :
			logger.error('Error in download {}:\n{}', self._id, traceback.format_exc())
			self._status = DownloadState.FAILED
	
	def after(self, _=None) :
		logger.info('Download {} exited with status {}', self._id, self._status)
		self._end = time.time()
		del _active_downloads[self._id]
		_completed_downloads[self._id] = self.getState()
	
	def getState(self) -> dict :
		res = {
			'file': self._archiver.getFilename(),
			'status': str(self._status),
			'completion': self._archiver.getProgress(),
			'created': self._creation
		}
		if self._begin is not None :
			res['begin'] = self._begin
		if self._end is not None :
			res['end'] = self._end
		return res
	
	def cancel(self) :
		res = self._future.cancel()
		if res :
			self._status = DownloadState.CANCELLED
			self.after()
		return res

	def getArchiver(self) -> Archiver :
		return self._archiver
	
	def getFuture(self) -> Future :
		return self._future


def clearHistory() :
	_completed_downloads.clear()
