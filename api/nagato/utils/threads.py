from nagato.utils.errors import ApiNotFoundError
from nagato.utils.compression import Archiver
from nagato.utils.database import getConnection, ChapterMark, SqlChapterEntry

import time
import hashlib
import logging
import threading
import traceback
from enum import Enum
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


mutex = threading.Lock()

_active_downloads: "dict[str,ChapterDownload]" = {}

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

	def isFinal(self) :
		return self in [
			DownloadState.COMPLETE, 
			DownloadState.FAILED, 
			DownloadState.CANCELLED
		]


class MutexLock() :

	def __init__(self, mutex: threading.Lock) :
		self._mutex = mutex
	
	def __enter__(self) :
		if self._mutex is not None :
			self._mutex.acquire()
		return self

	def __exit__(self, exc_type, exc_value, tb) :
		if self._mutex is not None :
			self._mutex.release()
		if exc_type is not None :
			# traceback.print_exception(exc_type, exc_value, tb)
			return False


def _generateId(t, filename) :
	for _ in range(10) :
		digest = hashlib.md5(f"{t}-{filename}".encode()).digest()
		h = b64encode(digest, b'-_')[:-2].decode('utf-8')
		if h not in _active_downloads and h not in _completed_downloads :
			return h
	raise RuntimeError("Could not attribute and ID to a download thread")

def _timestamp() :
	return int(time.time() * 1000)


class ChapterDownload :

	def __init__(self, downloader, chapter_id, register=False) :
		self._downloader = downloader
		self._chapter = chapter_id
		self._register = register
		self._archiver : Archiver = downloader.getArchiver(chapter_id)
		self._creation = _timestamp()
		self.setStatus(DownloadState.CREATED)
		self._future = None
		self._begin = None
		self._end = None
		self._cancelled = False
		with MutexLock(mutex) :
			self._id = _generateId(self._creation, self._archiver.getFilename())
			_active_downloads[self._id] = self
	
	def submit(self) -> str:
		self._creation = _timestamp() # Update the creation date to be the time of submission (just in case)
		self.setStatus(DownloadState.QUEUED)
		self._future = _executor.submit(self.perform)
		self._future.add_done_callback(self.after)
		logger.info('Download %s submitted', self._id)
		return self._id

	def perform(self) :
		try :
			self._begin = _timestamp()
			self.setStatus(DownloadState.PROCESSING)
			logger.info('Download %s processing', self._id)
			with self.getArchiver() as archiver :
				self._downloader.downloadChapter(self._chapter, archiver)
				archiver.after()
				self.setStatus(DownloadState.SAVING)
			self.setStatus(DownloadState.COMPLETE)
		except Exception :
			logger.error('Error in download %s:\n%s', self._id, traceback.format_exc())
			self.setStatus(DownloadState.FAILED)

	def setStatus(self, status: DownloadState) :
		if status.isFinal() :
			self._end = _timestamp()
			mutex.acquire()
			self._status = status
			if self._id in _active_downloads :
				del _active_downloads[self._id]
			else :
				logger.warning('Download %s was already inactive', self._id)
			_completed_downloads[self._id] = self.getState()
			mutex.release()
		else :
			self._status = status

	def after(self, _=None) :
		if not self._status.isFinal() :
			self.setStatus(DownloadState.CANCELLED if self._cancelled else DownloadState.FAILED)
		if self._status == DownloadState.COMPLETE and self._register :
			with getConnection() as con :
				cur = con.cursor()
				entry = SqlChapterEntry(self._downloader.getSite(), self._chapter, 
						self._downloader, self._archiver.getFormatInfo()['manga_id'])
				entry.setMark(cur, ChapterMark.DOWNLOADED)
				con.commit()
		logger.info('Download %s exited with status %s', self._id, str(self._status))
	
	def getState(self) -> dict :
		res = {
			'file': self._archiver.getFilename(),
			'status': self._status.name,
			'completion': self._archiver.getProgress(),
			'size': self._archiver.getRawSize(),
			'created': self._creation
		}
		if self._begin is not None :
			res['begin'] = self._begin
		if self._end is not None :
			res['end'] = self._end
		return res
	
	def cancel(self) :
		if self._cancelled :
			return False
		logger.info('Attempt to cancel download %s', self._id)
		self._cancelled = self._future.cancel()
		return self._cancelled

	def getArchiver(self) -> Archiver :
		return self._archiver


def clearHistory() -> int :
	mutex.acquire()
	res = len(_completed_downloads)
	_completed_downloads.clear()
	mutex.release()
	return res

def getDownloadState(download_id: str, best_effort=False) :
	with MutexLock(None if best_effort else mutex) :
		if download_id in _active_downloads :
			return _active_downloads[download_id].getState()
		if download_id in _completed_downloads :
			return _completed_downloads[download_id]
		if best_effort :
			return None
	raise ApiNotFoundError(f"No download registered with the id {download_id}")

def getAllDownloadStates(download_ids: "list[str]" = None) :
	with MutexLock(mutex) :
		if download_ids is not None :
			return {dl_id: getDownloadState(dl_id, True) for dl_id in download_ids}
		return {
			**{dl_id: cdl.getState() for dl_id, cdl in _active_downloads.items()},
			**_completed_downloads
		}

def cancelDownload(download_id: str, best_effort=False) -> bool :
	with MutexLock(None if best_effort else mutex) :
		if download_id in _active_downloads :
			return _active_downloads[download_id].cancel()
		if best_effort or download_id in _completed_downloads :
			return False
	raise ApiNotFoundError(f"No download registered with the id {download_id}")
	
def cancelDownloads(download_ids: "list[str]") -> "dict[str,bool]" :
	with MutexLock(mutex) :
		return {dl_id: cancelDownload(dl_id, True) for dl_id in download_ids}
