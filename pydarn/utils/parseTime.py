# UTILS
def parseTime( time ) :
    """
    *******************************
    ** atime = parseTime( time )
    Parse HHMM or HHMMSS dates in HH, MM, SS and vice versa

    INPUT:
    TIME: experiment date in HHMM or HHMMSS or numpy.array([HH,MM]) or numpy.array([HH,MM,SS])

    Created by Sebastien
    *******************************
    """

	from numpy import array
	
	# transform time into an array for testing
	if isinstance(time, ndarray): time = array([time])
	
	# parse time one way or another
	if len(time) == 3:
		ttime = time[0]*10000 + time[1]*100 + time[2]
	elif len(time) == 2:
		ttime = time[0]*100 + time[1]
	elif len(time) == 1 and len(str(time[0])) > 4 and len(str(time[0])) <= 6:
		ttime = array([time[0]/10000, time[0]/100-time[0]/10000*100, time[0]-time[0]/100*100])
	elif len(time) == 1 and len(str(time[0])) >=1  and len(str(time[0])) <= 4:
		ttime = array([time[0]/100, time[0]-time[0]/100*100])
	else:
		print 'Invalid time format: ', time
		return
	
	return ttime
