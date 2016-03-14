# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: utils
*********************
This subpackage contains various utilities for DaViT-py

**Modules**:
    * :mod:`utils.plotUtils`: Basic plotting tools 
    * :mod:`utils.geoPack`: geographic transformations
    * :mod:`utils.timeUtils`: date/time manipulations 
    * :mod:`utils.calcSun`: solar position calculator
    * :mod:`utils.coordUtils`: coordinate system tools

"""
try:
    from plotUtils import *
except Exception, e:
    print __file__+' -> utils.plotUtils: ', e

try:
    from geoPack import *
except Exception, e:
    print __file__+' -> utils.geoPack: ', e

try:
    from timeUtils import *
except Exception, e:
    print __file__+' -> utils.timeUtils: ', e

try:
    from calcSun import *
except Exception, e:
    print __file__+' -> utils.calcSun: ', e

try:
    from coordUtils import *
except Exception, e:
    print __file__+' -> utils.coordUtils: ', e


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

