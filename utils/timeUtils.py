# UTILS
def dateToYyyymmdd(myDate):
	"""
	*******************************
	dateStr = dateToYyyymmdd(myDate)
	
	takes a python date object and returns a string in yyyymmdd format

	INPUTS:
		myDate : a python date object
	OUTPUTS:
		dateStr : a string in yyyymmdd format

	Written by AJ 20120718
	*******************************
	"""
	if isinstance(myDate,date):
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
		print 'error, input must be type date'
		sys.exit()
	
def yyyymmddToDate(dateStr):
	"""
	*******************************
	myDate = yyyymmddToDate(dateStr)
	
	takes a string in yyyymmdd format and returns a python date object

	INPUTS:
		dateStr : a string in yyyymmdd format
	OUTPUTS:
		myDate : a python date object
		
	Written by AJ 20120718
	*******************************
	"""
	from datetime import date
	#check input type
	if isinstance(dateStr,str):
		#try to make the date object
		try:
			return date(int(dateStr[0:4]),int(dateStr[4:6]),int(dateStr[6:8]))
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