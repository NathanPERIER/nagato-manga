
from ..dataobj import DataObject
from ..person  import Person
from ..date    import SimpleDate
from ..enums.status      import Status
from ..enums.rating      import Rating
from ..enums.demographic import Demographic

from typing import Final, Optional, MutableSequence


class MangaInfo(DataObject) :
    
	def __init__(self, manga_id: str, site: str, name: str, lang: str) :
		self.manga_id: Final[str] = manga_id
		self.site:     Final[str] = site
		self.name:     Final[str] = name
		self.lang:     Final[str] = lang
		self.description: Optional[str] = None
		self.status:      Status        = Status.UNKNOW
		self.rating:      Rating        = Rating.UNKNOWN
		self.demographic: Demographic   = Demographic.UNKNOWN
		self.date:       Optional[SimpleDate] = None
		self.alt_titles: MutableSequence[str] = []
		self.genres:     MutableSequence[str] = []
		self.tags:       MutableSequence[str] = []
		self.authors:    MutableSequence[Person] = []
		self.artists:    MutableSequence[Person] = []
