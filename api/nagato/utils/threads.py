from nagato.utils.compression import Archiver

import time
import hashlib
from enum import Enum
from base64 import b64encode
from concurrent.futures import Future, ThreadPoolExecutor
import traceback


_active_downloads = {}

_downloads_status = {}

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='nagato_dl')


class DownloadState(Enum) :
	CREATED    = 0
	QUEUED     = 1
	PROCESSING = 2
	SAVING     = 3
	COMPLETE   = 4
	FAILED     = -1


def _generateId(filename) :
	for _ in range(10) :
		t = time.time()
		digest = hashlib.md5(f"{t}-{filename}".encode()).digest()
		h = b64encode(digest, b'-_')[:-2].decode('utf-8')
		if h not in _downloads_status :
			return h
	raise RuntimeError("Could not attribute and ID to a download thread")


class ChapterDownload :

	def __init__(self, downloader, chapter_id) :
		self._downloader = downloader
		self._chapter = chapter_id
		self._archiver : Archiver = downloader.getArchiver(chapter_id)
		self._id = _generateId(self._archiver.getFilename())
		self._status = DownloadState.CREATED
		self._future = None
	
	def submit(self) :
		self._status = DownloadState.QUEUED
		self._future = _executor.submit(self.perform)
		return self._id

	def perform(self) :
		try :
			self._status = DownloadState.PROCESSING
			with self.getArchiver() as archiver :
				self._downloader.downloadChapter(self._chapter, archiver)
				self._status = DownloadState.SAVING
			self._status = DownloadState.COMPLETE
		except Exception :
			print(traceback.format_exc())
			self._status = DownloadState.FAILED
	
	def getArchiver(self) -> Archiver :
		return self._archiver
	
	def getFuture(self) -> Future :
		return self._future
