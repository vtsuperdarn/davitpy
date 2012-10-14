# UTILS
def parseDate( date ) :
	"""
*******************************
** adate = parseDate( date )
Parse YYYYMMDD dates in YYYY, MM, DD and vice versa

INPUT:
DATE: experiment date in YYYYMMDD or [YYYY,MM,DD]

Created by Sebastien

*******************************
	"""
	# transform date into an array for testing
	if not isinstance(date, list): date = [date]
	
	# make sure we are getting integers
	for id in range( len(date) ):
		if isinstance(date[id], str): date[id] = int(date[id])
	
	# parse date one way or another
	if len(date) == 3:
		tdate = date[0]*10000 + date[1]*100 + date[2]
	elif len(date) == 1:
		tdate = [date[0]/10000, date[0]/100-date[0]/10000*100, date[0]-date[0]/100*100]
	else:
		print 'Invalid date format: ', date
		return
	
	return tdate