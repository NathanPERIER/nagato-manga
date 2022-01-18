import time
import hashlib
from enum import Enum
from threading import Thread
from base64 import b64encode


_active_threads = {}

_terminated_downloads = {}

def getThreadStatus(thread_id) : # TODO
	raise NotImplementedError

def getAllThreadStatus() : # TODO
	raise NotImplementedError

def clearArchive() :
	_terminated_downloads.clear()

def _archiveThread(thread) :
	thread_id = thread.getId()
	del _active_threads[thread_id]
	_terminated_downloads[thread_id] = (thread.getFilename(), thread.getState())



class DownloadState(Enum) :
	CREATED    = 0
	QUEUED     = 1
	PROCESSING = 2
	SAVING     = 3
	COMPLETE   = 4
	FAILED     = -1


class DownloadThread(Thread) :

	def __init__(self, downloader, chapter_id) :
		super().__init__()
		self._state = DownloadState.CREATED
		self._downloader = downloader
		self._chapter_id = chapter_id
		self._format_data = downloader.getChapteFormattingData(chapter_id)
		self._filename = downloader.getFilename(self._format_data)
		self._generateId()

	def _generateId(self) :
		for _ in range(10) :
			t = time.time()
			digest = hashlib.md5(f"{t}-{self._filename}".encode()).digest()
			h = b64encode(digest, b'-_')[:-2].decode('utf-8')
			if h not in _active_threads and h not in _terminated_downloads :
				self._id = h
				_active_threads[h] = self
				return
		raise RuntimeError("Could not attribute and ID to a download thread")

	def getFilename(self) :
		return self._filename
	
	def getState(self) -> DownloadState :
		return self._state
	
	def getId(self) :
		return self._id

	def run(self) :
		self._state = DownloadState.PROCESSING
		images = self._downloader.downloadChapter(self._chapter_id)
		self._state = DownloadState.SAVING
		self._downloader.saveChapter(images, self._format_data)
		self._state = DownloadState.COMPLETE
		_archiveThread(self)
