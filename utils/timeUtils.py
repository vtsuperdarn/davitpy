# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
	return calendar.timegm(myDate.timetuple())+myDate.microsecond/1e6

def dateToDecYear(date):
	"""Convert :class:`datetime.datetime` object to decimal year
	
	**Args**: 
		* **date** (datetime.datetime): date and time
	**Returns**:
		* **dyear** (float): decimal year
			
	written by Sebastien, 2013-02
	"""
	from datetime import datetime as dt
	import time
	
	# returns seconds since epoch
	sE = lambda date: time.mktime(date.timetuple())

	year = date.year
	startOfThisYear = dt(year=year, month=1, day=1)
	startOfNextYear = dt(year=year+1, month=1, day=1)

	yearElapsed = sE(date) - sE(startOfThisYear)
	yearDuration = sE(startOfNextYear) - sE(startOfThisYear)
	fraction = yearElapsed/yearDuration

	return date.year + fraction

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


def parseTime( time ) : 
        """ 
*******************************
** atime = parseTime( time )
Parse HHMM or HHMMSS dates in HH, MM, SS and vice versa

INPUT:
TIME: time in HHMM or HHMMSS or [HH,MM] or [HH,MM,SS]

Created by Sebastien

*******************************
        """
        # transform time into an array for testing
        if not isinstance(time, list): time = [time]
    
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
