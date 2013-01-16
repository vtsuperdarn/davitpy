# Utils module __init__.py
"""
*******************************
            UTILS
*******************************
This subpackage contains various utilities for DaViT-py
DEV: functions/modules/classes with a * have not been developed yet

This includes the following modules:
	calcSun

This includes the following functions:
	parseDate
	parseTime

*******************************
"""

from parseDate import parseDate
from parseTime import parseTime
from timeUtils import *
import geoPack
import calcSun
import profileUtils


# *************************************************************
# Define a few general-use constants

# Mean Earth radius [km]
Re = 6371.0
# Polar Earth radius [km]
RePol = 6378.1370
# Equatorial Earth radius [km]
ReEqu = 6356.7523

#thanks to Sasha Chedygov on stackoverflow for this idea
class twoWayDict(dict):
	#I added the initialization fucntion
	def __init__(self,initDict={}):
		for key,val in initDict.iteritems():
			self[key] = val
			self[val] = key
		
	def __len__(self):
		return dict.__len__(self) / 2
		
	def __setitem__(self, key, value):
		dict.__setitem__(self, key, value)
		dict.__setitem__(self, value, key)

