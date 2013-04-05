# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: pydarn.radar.radUtils
*********************
		
**Functions**:
	* :func:`getCpName`: get the name of a control program from cp id number

"""

def getCpName(cpid):
	"""Get the name of a control program from cp id number
	
	**Args**: 
		* **cpid** (int): the control prog. id number
	**Returns**:
		* **cpName** (str): the name of a control program
	**Example**:
		::

			s = getCpName(3310)
			
	written by AJ, 2012-08
	"""
	from math import fabs
	
	assert(isinstance(cpid,int) or isinstance(cpid,float)),'error, cpid must be a number'
	
	if(fabs(cpid) == 26003): return 'stereoscan (b)'
	if(fabs(cpid) == 153): return 'stereoscan (a)'
	if(fabs(cpid) == 3310): return 'themis-tauscan'
	if(fabs(cpid) == 3300): return 'themisscan'
	if(fabs(cpid) == 150): return 'katscan'
	if(fabs(cpid) == 151): return 'katscan -fast'
	if(fabs(cpid) == 503): return 'tauscan'
	if(fabs(cpid) == 9213): return 'pcpscan'
	if(fabs(cpid) == 1): return 'normalscan'
	return ''

