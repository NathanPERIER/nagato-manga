from nagato.utils.errors import ApiNotFoundError
from nagato.utils.compression import Archiver

import time
import hashlib
import logging
import traceback
from enum import Enum
from base64 import b64encode
from concurrent.futures import Future, ThreadPoolExecutor

logger = logging.getLogger(__name__)


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
		return self in [DownloadState.COMPLETE, DownloadState.FAILED, DownloadState.CANCELLED]


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

	def __init__(self, downloader, chapter_id) :
		self._downloader = downloader
		self._chapter = chapter_id
		self._archiver : Archiver = downloader.getArchiver(chapter_id)
		self._creation = _timestamp()
		self._id = _generateId(self._creation, self._archiver.getFilename())
		self._status = DownloadState.CREATED
		self._future = None
		self._begin = None
		self._end = None
		self._cancel = False
		_active_downloads[self._id] = self
	
	def submit(self) :
		self._creation = _timestamp() # Update the creation date to be the time of submission (just in case)
		self._status = DownloadState.QUEUED
		self._future = _executor.submit(self.perform)
		self._future.add_done_callback(self.after)
		logger.info('Download %s submitted', self._id)
		return self._id

	def perform(self) :
		try :
			self._begin = _timestamp()
			self._status = DownloadState.PROCESSING
			logger.info('Download %s processing', self._id)
			with self.getArchiver() as archiver :
				self._downloader.downloadChapter(self._chapter, archiver)
				self._status = DownloadState.SAVING
			self._status = DownloadState.COMPLETE
		except Exception :
			logger.error('Error in download %s:\n%s', self._id, traceback.format_exc())
			self._status = DownloadState.FAILED

	def after(self, _=None) :
		if not self._status.isFinal() :
			self._status = DownloadState.CANCELLED if self._cancel else DownloadState.FAILED
		logger.info('Download %s exited with status %s', self._id, str(self._status))
		self._end = _timestamp()
		del _active_downloads[self._id]
		_completed_downloads[self._id] = self.getState()
	
	def getState(self) -> dict :
		res = {
			'file': self._archiver.getFilename(),
			'status': self._status.name,
			'completion': self._archiver.getProgress(),
			'created': self._creation
		}
		if self._begin is not None :
			res['begin'] = self._begin
		if self._end is not None :
			res['end'] = self._end
		return res
	
	def cancel(self) :
		self._cancel = True
		logger.info('Attempt to cancel download %s', self._id)
		return self._future.cancel()

	def getArchiver(self) -> Archiver :
		return self._archiver


def clearHistory() :
	_completed_downloads.clear()

def getDownloadState(download_id: str, best_effort=False) :
	if download_id in _active_downloads :
		return _active_downloads[download_id].getState()
	if download_id in _completed_downloads :
		return _completed_downloads[download_id]
	if best_effort :
		return None
	raise ApiNotFoundError(f"No download registered with the id {download_id}")

def getAllDownloadStates(download_ids: "list[str]" = None) :
	if download_ids is not None :
		return {dl_id: getDownloadState(dl_id, True) for dl_id in download_ids}
	return {
		**{dl_id: cdl.getState() for dl_id, cdl in _active_downloads.items()},
		**_completed_downloads
	}

def cancelDownload(download_id: str, best_effort=False) -> bool :
	if download_id in _active_downloads :
		return _active_downloads[download_id].cancel()
	if best_effort or download_id in _completed_downloads :
		return False
	raise ApiNotFoundError(f"No download registered with the id {download_id}")
	
def cancelDownloads(download_ids: "list[str]") -> "dict[str,bool]" :
	return {dl_id: cancelDownload(dl_id, True) for dl_id in download_ids}
