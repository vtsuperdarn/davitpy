# UTILS
"""
*******************************
** adate = parseDate( date )
Parse YYYYMMDD dates in YYYY, MM, DD and vice versa

INPUT:
DATE: experiment date in YYYYMMDD or numpy.array([YYYY,MM,DD])

Created by Sebastien
*******************************
"""
def parseDate( date ) :

	from numpy import array
	
	# transform date into an array for testing
	if type(date) != type(array([])): date = array([date])
	
	# parse date one way or another
	if len(date) == 3:
		tdate = date[0]*10000 + date[1]*100 + date[2]
	elif len(date) == 1:
		tdate = array([date[0]/10000, date[0]/100-date[0]/10000*100, date[0]-date[0]/100*100])
	else:
		print 'Invalid date format: ', date
		return
	
	return tdate