# UTILS
def parseTime( time ) :
	"""
*******************************
** atime = parseTime( time )
Parse HHMM or HHMMSS dates in HH, MM, SS and vice versa

Created by Sebastien
*******************************
	"""
	# transform time into an array for testing
	if ~isinstance(time, list): time = [time]
	
	# make sure we are getting integers
	for it in range( len(time) ):
		if isinstance(time[it], str): time[it] = int(time[it])
	
	# parse time one way or another
	if len(time) == 3:
		ttime = time[0]*10000 + time[1]*100 + time[2]
	elif len(time) == 2:
		ttime = time[0]*100 + time[1]
	elif len(time) == 1 and len(str(time[0])) > 4 and len(str(time[0])) <= 6:
		ttime = [time[0]/10000, time[0]/100-time[0]/10000*100, time[0]-time[0]/100*100]
	elif len(time) == 1 and len(str(time[0])) >=1  and len(str(time[0])) <= 4:
		ttime = [time[0]/100, time[0]-time[0]/100*100]
	else:
		print 'Invalid time format: ', time
		return
	
	return ttime
