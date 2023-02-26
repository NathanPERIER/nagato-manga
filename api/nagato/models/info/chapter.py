
from ..dataobj import DataObject
from ..person  import Person
from ..date    import SimpleDate
from ..enums.chapter_mark import ChapterMark

from typing import Optional, Final


class ChapterInfo(DataObject) :
    
	def __init__(self, chapter_id: str, manga_id: str, site: str, number: str, lang: str) :
		self.chapter_id: Final[str] = chapter_id
		self.manga_id:   Final[str] = manga_id
		self.site:       Final[str] = site
		self.number:     Final[str] = number
		self.lang:       Final[str] = lang
		self.title:  Optional[str] = None
		self.volume: Optional[int] = None
		self.pages:  Optional[int] = None
		self.date:   Optional[SimpleDate]  = None
		self.mark:   Optional[ChapterMark] = None
		self.translator: Optional[Person]  = None
