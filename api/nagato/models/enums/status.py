
from .dataenum import DataEnum

class Status(DataEnum) :
    UNKNOW    = 0
    CANCELLED = 1
    PAUSED    = 2
    ONGOING   = 3
    COMPLETED = 4
