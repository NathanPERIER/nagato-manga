
from .dataenum import DataEnum

class Rating(DataEnum) :
    UNKNOWN = 0
    SAFE    = 1
    DUBIOUS = 2
    NSFW    = 3
