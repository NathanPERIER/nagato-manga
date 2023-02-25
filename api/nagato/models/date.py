
from .dataobj import DataObject

class SimpleDate(DataObject) :
    
	def __init__(self, day: int, month: int, year: int) :
		self.day   = day
		self.month = month
		self.year  = year
