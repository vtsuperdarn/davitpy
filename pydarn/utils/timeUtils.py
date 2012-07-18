#COPYRIGHT:
#Copyright (C) 2011 by Virginia Tech

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

# UTILS
from datetime import date
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
		return
	
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
	
	#check input type
	if isinstance(dateStr,str):
		#try to make the date object
		try:
			return date(int(dateStr[0:4]),int(dateStr[4:6]),int(dateStr[6:8]))
		#if there was a problem with the input
		except:
			print 'error in input '+dateStr 
			return
	else:
		print 'error, input must be a string'
		return
		
		
		