import pydarn
import numpy
import matplotlib
import matplotlib.pyplot as plot
import calendar
import datetime
import utils

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
	
	rtiTitle(myData,dateStr,beam)
	
	x=plotNoise(myData)
	
	rtiFig.show()
	return x
def rtiTitle(myData,dateStr,beam):
	
	rname = 'Radar Name'
	plot.figtext(.1,.95,rname+'  ('+myData.ftype+')',ha='left',weight=550)
	
	d = utils.yyyymmddToDate(dateStr)
	plot.figtext(.5,.95,str(d.day)+'/'+calendar.month_name[d.month][:3]+'/'+str(d.year), \
	weight=550,size='large',ha='center')
	
	plot.figtext(.9,.95,'Beam '+str(beam),weight=550,ha='right')
	

def plotNoise(myData,position=[.1,.88,.8,.06]):
	
	y=[]
	
	for i in range(0,myData.nrecs):
		y.append(myData[myData.times[i]]['prm']['noise.sky'])
	
	ax = plot.axes(position)
	ax.yaxis.set_tick_params(direction='out')
	ax.xaxis.set_tick_params(labelsize=0)
	
	
	plot.plot_date(matplotlib.dates.date2num(myData.times), numpy.log10(y), fmt='ko-', \
	tz=None, xdate=True, ydate=False,markersize=2)
	
	loc,lab = plot.xticks()
	plot.xticks(loc,(' '))
	#customize yticks
	plot.yticks(numpy.arange(0,6,5),('10^0','10^5'),fontsize=9,weight=550)
	plot.ylabel('N.Sky',fontsize=10,weight=550)
	return ax
	
	
