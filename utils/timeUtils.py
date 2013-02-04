# UTILS

def dateToYyyymmdd(myDate):
	"""
	*******************************
	dateStr = dateToYyyymmdd(myDate)
	
	takes a python datetime object and returns a string in yyyymmdd format

	INPUTS:
		myDate : a python date object
	OUTPUTS:
		dateStr : a string in yyyymmdd format

	Written by AJ 20120718
	
	*******************************
	"""
	from datetime import datetime
	
	if isinstance(myDate,datetime):
		dateStr = ''
		#create year string
		yr = myDate.year
		if(yr < 10):
			dateStr += '000'+str(yr)
		elif(yr < 100):
			dateStr += '00'+str(yr)
		elif(yr < 1000):
			dateStr += '0'+str(yr)
		else:
			dateStr += str(yr)
			
		#create month string
		mon = myDate.month
		if(mon < 10):
			dateStr += '0'+str(mon)
		else:
			dateStr += str(mon)
			
		#create day string
		day = myDate.day
		if(day < 10):
			dateStr += '0'+str(day)
		else:
			dateStr += str(day)
			
		#return everything together
		return dateStr
	else:
		print 'error, input must be type datetime'
		sys.exit()
	
def yyyymmddToDate(dateStr):
	"""
	*******************************
	myDate = yyyymmddToDate(dateStr)
	
	takes a string in yyyymmdd format and returns a python date object

	INPUTS:
		dateStr : a string in yyyymmdd format
	OUTPUTS:
		myDate : a python datetime object
		
	Written by AJ 20120718
	*******************************
	"""
	
	from datetime import datetime
	import sys
	#check input type
	if isinstance(dateStr,str):
		#try to make the date object
		try:
			return datetime(int(dateStr[0:4]),int(dateStr[4:6]),int(dateStr[6:8]))
		#if there was a problem with the input
		except:
			print 'error in input '+dateStr 
			sys.exit()
	else:
		print 'error, input must be a string'
		sys.exit()
		
		
def timeYrsecToDate(yrsec, year):
	"""
	*******************************
	myDate = timeYrsecToDate(yrsec, year)
	
	Converts time expressed in seconds from start of year to a python DATETIME object

	INPUTS:
		yrsec : seconds since start of year
		year : year in YYYY 
	OUTPUTS:
		myDate : a python DATETIME object
		
	Written by Sebastien, Jul. 2012
	*******************************
	"""
	from datetime import datetime
	from datetime import timedelta
	
	if year >= 2038: 
		print 'timeYrsecToDate: Year {:d} out of range: forcing 2038'.format(year)
		year = 2038
	myDate = datetime(year, 1, 1) + timedelta(seconds = yrsec)
	
	return myDate

def julToDatetime( ndarray ) :
  """ 
  ****************************
  adate = julToDatetime( ndarray )
  Convert a julian date to a datetime object.

  INPUT: 
  NDARRAY: single float64 or a numpy array of Julian Dates.

  Created by Nathaniel Frissell 20120810
  *******************************
  """
  import datetime
  import dateutil.parser
  import numpy
  import spacepy.time as spt

  t = spt.Ticktock(ndarray,'JD')

  dt = list()
  for iso in t.ISO: dt.append(dateutil.parser.parse(iso))

  return dt
  
	
def datetimeToEpoch(myDate):
	"""
	*******************************
	myEpoch = datetimeToEpoch(dateStr)
	
	reads in a datetime and outputs the equivalent epoch time

	INPUTS:
		myDate : a datetime object
	OUTPUTS:
		myEpoch : an epoch time equal to the datetime object
		
	Written by AJ 20120914
	*******************************
	"""
	
	import datetime,calendar
	print myDate
	return calendar.timegm(myDate.timetuple())+myDate.microsecond/1e6

