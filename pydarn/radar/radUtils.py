import math

def getCpName(cpid):
	"""
	*******************************
	getCpName(cpid):
	
	get the name of a control program from cp id number

	INPUTS:
		cpid: the control prog. id number
	OUTPUTS:
		cpName: the name of a control program
	EXAMPLE:
		s = getCpName(3310)
		
	Written by AJ 20120820
	*******************************
	"""
	
	assert(isinstance(cpid,int) or isinstance(cpid,float)),'error, cpid must be a number'
	
	if(math.fabs(cpid) == 26003): return 'stereoscan (b)'
	if(math.fabs(cpid) == 153): return 'stereoscan (a)'
	if(math.fabs(cpid) == 3310): return 'themis-tauscan'
	if(math.fabs(cpid) == 3300): return 'themisscan'
	if(math.fabs(cpid) == 150): return 'katscan'
	if(math.fabs(cpid) == 151): return 'katscan -fast'
	if(math.fabs(cpid) == 503): return 'tauscan'
	if(math.fabs(cpid) == 1): return 'normalscan'
	return ' '

