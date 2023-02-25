'''
This module exports classes used to contain data with a well-defined structure.
These objects should be treated as C/C++ structs, as such direct access to their internal fields is allowed.
'''

from .enums   import *
from .dataobj import DataObject
from .date    import SimpleDate
from .person  import Person
