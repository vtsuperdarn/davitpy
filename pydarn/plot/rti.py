import pydarn
import numpy
import matplotlib.pyplot as plot

def plotRti(dateStr,rad,beam,time=[0,2400],fileType='fitex'):
	"""
	*******************************
	
	plotRti(dateStr,rad,beam,[time],[fileType]):
	
	crate an rti plot for a secified radar and time period

	INPUTS:
		dateStr: a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		beam: the beam to plot
		[times]: the range of times for which the file should be read,
			in SIMPLIFIED [hhmm,hhmm] format, eg [29,156], 
			instead of [0029,0156]
			note that an end time of 2400 will read to the end of the file
			default = [0,2400]
		[fileType]: one of ['fitex','fitacf','lmfit']
			default = 'fitex'
	OUTPUTS:

	EXAMPLE
		
	Written by AJ 20120807
	*******************************
	"""
	
	#check the inputs
	assert(isinstance(dateStr,str)),'error, dateStr must be a string'
	assert(isinstance(rad,str)),'error, dateStr must be a string'
	assert(len(dateStr) == 8),'error, dateStr must be 8 characters long'
	assert(len(rad) == 3),'error, rad must be 3 characters long'
	assert(isinstance(beam,int)),'error, beam mest be integer'
	
	#read the radar data
	myData = pydarn.io.radDataRead(dateStr,rad,time=time,fileType=fileType,vb=0,beam=beam)
	
	assert(myData.nrecs > 0),'error, no data available'
	
	rtiFig = plot.figure()
	
	rtiTitle(myData,rtiFig)
	
	rtiFig.show()
	
def rtiTitle(myData,myFig):
	
	
	plot.figtext(.5,.95,'this is a test',ha='center')
