import pydarn
import numpy
import matplotlib
import matplotlib.pyplot as plot
import matplotlib.lines as lines
import calendar
import datetime
import utils
import pylab
from matplotlib.ticker import MultipleLocator
from matplotlib.collections import PolyCollection
from itertools import cycle

def plotRti(dateStr,rad,beam=7,time=[0,2400],fileType='fitex',params=['velocity','power','width'], \
scales=[[-200,200],[0,30],[0,150]],channel='a',coords='gate'):
	"""
	*******************************
	
	plotRti(dateStr,rad,beam,[time],[fileType]):
	
	crate an rti plot for a secified radar and time period

	INPUTS:
		dateStr: a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		[beam]: the beam to plot
			default: 7
		[times]: the range of times for which the file should be read,
			in SIMPLIFIED [hhmm,hhmm] format, eg [29,156], 
			instead of [0029,0156]
			note that an end time of 2400 will read to the end of the file
			default = [0,2400]
		[fileType]: one of ['fitex','fitacf','lmfit']
			default = 'fitex'
		[params]: a list of the fit parameters to plot, allowable values are:
			['velocity','power','width']
			default: ['velocity','power','width']
		[scales]: a list of the min/max values for the color scale for
			each param.  The list should be n x 2 where n is the number of
			elements in the params list
			default: [[-200,200],[0,30],[0,150]]
		[channel]: the channel you wish to plot, the allowable values are
			'a' and 'b'
			default: 'a'
		[coords]: the coordinates to use for the y axis.  The allowable values are
			'gate','rng','geo','mag'
			default: 'gate'
	OUTPUTS:

	EXAMPLE:
		plotRti('20120101','bks',beam=12,time=[10,1453],fileType='fitex',
		params=['vel','power'],scales=[[-200,200],[0,30]],channel='b',
		coords='mag'):
		
	Written by AJ 20120807
	*******************************
	"""
	
	#check the inputs
	assert(isinstance(dateStr,str) and len(dateStr) == 8),'error, dateStr must be a string 8 chars long'
	assert(isinstance(rad,str) and len(rad) == 3),'error, dateStr must be a string 3 chars long'
	assert(isinstance(beam,int)),'error, beam must be integer'
	assert(0 < len(params) < 4),'error, must input between 1 and 3'
	for i in range(0,len(params)):
		assert(params[i] == 'velocity' or params[i] == 'power' or params[i] == 'width'),\
		"error, allowable params are 'velocity','power','width'"
	assert(len(scales)==len(params)), \
	'error, input scales must have same number of elements as params'
	
	#read the radar data
	myData = pydarn.io.radDataRead(dateStr,rad,time=time,fileType=fileType,vb=0,beam=beam)
	
	myData = myData.getChannel(channel)
	
	assert(myData.nrecs > 0),'error, no data available'
	
	rtiFig = plot.figure()
	
	rtiTitle(myData,dateStr,beam)
	
	plotNoise(myData,rtiFig)
	
	plotFreq(myData,rtiFig)
	
	figtop = .77
	figheight = .72/len(params)
	for i in range(0,len(params)):
		plotData(myData,rtiFig,params[i],scales[i],i==len(params)-1, \
		coords=coords,pos=[.1,figtop-figheight*(i+1)+.02,.76,figheight-.02])
		
	rtiFig.show()
	
def plotData(myData,myFig,param,scale,bottom,yrng=-1,coords='gate',pos=[.1,.05,.76,.72]):

	#add an axes to the figure
	ax = myFig.add_axes(pos)
	ax.yaxis.set_tick_params(direction='out')
	ax.xaxis.set_tick_params(direction='out')
	ax.yaxis.set_minor_locator(MultipleLocator(5))
	ax.yaxis.set_tick_params(direction='out',which='minor')
	ax.xaxis.set_tick_params(direction='out',which='minor')
	
	#check that we have data
	if(myData.nrecs == 0): return None
	
	#check if we want default y axis
	if(isinstance(yrng,int) and yrng == -1):
		ymin = 0
		ymax = -1
		for i in range(0,myData.nrecs):
			if(myData[myData.times[0]]['prm']['nrang'] > ymax): ymax = myData[myData.times[0]]['prm']['nrang']
			
	ax.set_ylim(bottom=ymin,top=ymax)
		
	#draw the axes
	ax.plot_date(matplotlib.dates.date2num(myData.times), numpy.arange(len(myData.times)), fmt='w', \
	tz=None, xdate=True, ydate=False)
	
		
	verts,intensities=[],[]
	fcs = ['b','g','m']
	#collect the data into a list of vertices to be plotted
	for i in range(0,myData.nrecs):
		t = myData.times[i]
		x1 = matplotlib.dates.date2num(t)
		if(i < myData.nrecs-1): 
			x2 =  matplotlib.dates.date2num(myData.times[i+1])
			if(x2-x1 > 4./1440.): x2 = x1+2./1440.
		else: x2 = x1+1./1440.

		for j in range(0,len(myData[t]['fit']['slist'])):
			y1,y2 = myData[t]['fit']['slist'][j],myData[t]['fit']['slist'][j]+1
			verts.append(((x1,y1),(x1,y2),(x2,y2),(x2,y1)))
			if(param == 'velocity'): intensities.append(myData[t]['fit']['v'][j])
			if(param == 'power'): intensities.append(myData[t]['fit']['p_l'][j])
			if(param == 'width'): intensities.append(myData[t]['fit']['w_l'][j])


	#create a collection of polygons with the specified vertices, use numpy arrays to increase speed
	pcoll = PolyCollection(numpy.array(verts), closed=False, edgecolor='none')
	pcoll.set_array(numpy.array(intensities))
	
	if(param == 'velocity'):
		cmj = matplotlib.cm.jet
		cmap = matplotlib.colors.ListedColormap([cmj(1.),cmj(.85),cmj(.75),cmj(.65),cmj(.55),cmj(.45),cmj(.3),cmj(0.)])
		bounds = numpy.linspace(scale[0],scale[1],7)
		bounds = numpy.insert(bounds,0,-9999999.)
		bounds = numpy.append(bounds,9999999.)
		norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
	else:
		cmj = matplotlib.cm.jet
		cmap = matplotlib.colors.ListedColormap([cmj(0.),cmj(.125),cmj(.25),cmj(.375),cmj(.5),cmj(.625),cmj(.75),cmj(.99)])
		bounds = numpy.linspace(scale[0],scale[1],8)
		bounds = numpy.append(bounds,9999999.)
		norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
		
	pcoll.set_cmap(cmap)
	pcoll.set_norm(norm)
	#add the collection of polygons to the axes
	cax = ax.add_collection(pcoll, autolim=True)
	
	loc,lab = plot.yticks()
	ax.yaxis.set_ticklabels(loc,lab,size=9)
	#format the x axis
	ax.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator(interval=20))
	plot.xticks(size=9)
	if(not bottom):
		loc,lab = plot.xticks()
		plot.xticks(loc,(' '))
	else:
		ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
		ax.xaxis.set_label_text('UT')
		
	if(coords == 'gate'): ax.yaxis.set_label_text('Range gate',size=10)
	if(coords == 'geo'): ax.yaxis.set_label_text('Geo Lat [deg]',size=10)
	if(coords == 'mag'): ax.yaxis.set_label_text('Mag Lat [deg]',size=10)
	if(coords == 'rng'): ax.yaxis.set_label_text('Slant Range [km]',size=10)
	
	#create a new axes for the colorbar
	cax = myFig.add_axes([pos[0]+pos[2]+.03, pos[1], 0.03, pos[3]])
	cb = plot.colorbar(pcoll,cax=cax)
	
	for t in cb.ax.get_yticklabels():
		t.set_fontsize(10)
	if(param == 'velocity'): cb.set_label('Velocity [m/s]',size=10)
	if(param == 'power'): cb.set_label('Power [dB]',size=10)
	if(param == 'width'): cb.set_label('Spec Wid [m/s]',size=10)
	
def rtiTitle(myData,dateStr,beam,xmin=.1,xmax=.86):
	
	n=pydarn.radar.network()
	r=n.getRadarById(33)
	
	plot.figtext(xmin,.95,r.name+'  ('+myData.ftype+')',ha='left',weight=550)
	
	d = utils.yyyymmddToDate(dateStr)
	plot.figtext((xmin+xmax)/2.,.95,str(d.day)+'/'+calendar.month_name[d.month][:3]+'/'+str(d.year), \
	weight=550,size='large',ha='center')
	
	plot.figtext(xmax,.95,'Beam '+str(beam),weight=550,ha='right')
	

def plotNoise(myData,myFig,pos=[.1,.88,.76,.06]):
	
	#read the data
	sky=[]
	search = []
	for i in range(0,myData.nrecs):
		sky.append(myData[myData.times[i]]['prm']['noise.sky'])
		search.append(myData[myData.times[i]]['prm']['noise.search'])
	
	#add an axes to the figure
	ax = myFig.add_axes(pos)
	ax.yaxis.tick_left()
	ax.yaxis.set_tick_params(direction='out')
	ax.set_ylim(bottom=0,top=6)
	ax.yaxis.set_minor_locator(MultipleLocator())
	ax.yaxis.set_tick_params(direction='out',which='minor')

	
	#plot the sky noise data
	ax.plot_date(matplotlib.dates.date2num(myData.times), numpy.log10(sky), fmt='k-', \
	tz=None, xdate=True, ydate=False)
	#remove the x tick labels
	loc,lab = plot.xticks()
	plot.xticks(loc,(' '))
	#use only 2 major yticks
	plot.yticks([0,6],(' '))
	
	#left y axis annotation
	plot.figtext(pos[0]-.01,pos[1]+.004,'10^0',ha='right',va='bottom',size=8)
	plot.figtext(pos[0]-.01,pos[1]+pos[3],'10^6',ha='right',va='top',size=8)
	plot.figtext(pos[0]-.07,pos[1]+pos[3]/2.,'N.Sky',ha='center',va='center', \
	size=8.5,rotation='vertical')
	l=lines.Line2D([pos[0]-.06,pos[0]-.06], [pos[1]+.01,pos[1]+pos[3]-.01], \
	transform=myFig.transFigure,clip_on=False,ls='-',color='k',lw=1.5)                              
	ax.add_line(l)
	
	
	#add an axes to the figure
	ax2 = myFig.add_axes(pos,frameon=False)
	ax2.yaxis.tick_right()
	ax2.yaxis.set_tick_params(direction='out')
	ax2.set_ylim(bottom=0,top=6)
	ax2.yaxis.set_minor_locator(MultipleLocator())
	ax2.yaxis.set_tick_params(direction='out',which='minor')
	
	#plot the search noise data
	ax2.plot_date(matplotlib.dates.date2num(myData.times), numpy.log10(search), fmt='k:', \
	tz=None, xdate=True, ydate=False,lw=1.5)
	
	#remove the x tick labels
	loc,lab = plot.xticks()
	plot.xticks(loc,(' '))
	#use only 2 major yticks
	plot.yticks([0,6],(' '))
	
	#right y axis annotation
	plot.figtext(pos[0]+pos[2]+.01,pos[1]+.004,'10^0',ha='left',va='bottom',size=8)
	plot.figtext(pos[0]+pos[2]+.01,pos[1]+pos[3],'10^6',ha='left',va='top',size=8)
	plot.figtext(pos[0]+pos[2]+.06,pos[1]+pos[3]/2.,'N.Sch',ha='center',va='center',size=8.5,rotation='vertical')
	l=lines.Line2D([pos[0]+pos[2]+.07,pos[0]+pos[2]+.07], [pos[1]+.01,pos[1]+pos[3]-.01], \
	transform=myFig.transFigure,clip_on=False,ls=':',color='k',lw=1.5)                              
	ax2.add_line(l)
	
def plotFreq(myData,myFig,pos=[.1,.82,.76,.06]):
	
	y=[]
	nave=[]
	for i in range(0,myData.nrecs):
		y.append(myData[myData.times[i]]['prm']['tfreq']/1e3)
		if(y[i] > 16): y[i] = 16
		if(y[i] < 10): y[i] = 10
		nave.append(myData[myData.times[i]]['prm']['nave'])
		
		
	#FIRST, DO THE TFREQ PLOTTING
	ax = myFig.add_axes(pos)
	ax.yaxis.tick_left()
	ax.yaxis.set_tick_params(direction='out')
	ax.set_ylim(bottom=10,top=16)
	ax.yaxis.set_minor_locator(MultipleLocator())
	ax.yaxis.set_tick_params(direction='out',which='minor')
	
	ax.plot_date(matplotlib.dates.date2num(myData.times), y, fmt='k-', \
	tz=None, xdate=True, ydate=False,markersize=2)
	
	loc,lab = plot.xticks()
	plot.xticks(loc,(' '))
	#customize yticks
	plot.yticks([10,16],(' '))
	
	plot.figtext(pos[0]-.01,pos[1],'10',ha='right',va='bottom',size=8)
	plot.figtext(pos[0]-.01,pos[1]+pos[3]-.003,'16',ha='right',va='top',size=8)
	plot.figtext(pos[0]-.07,pos[1]+pos[3]/2.,'Freq',ha='center',va='center',size=9,rotation='vertical')
	plot.figtext(pos[0]-.05,pos[1]+pos[3]/2.,'[MHz]',ha='center',va='center',size=7,rotation='vertical')
	l=lines.Line2D([pos[0]-.04,pos[0]-.04], [pos[1]+.01,pos[1]+pos[3]-.01], \
	transform=myFig.transFigure,clip_on=False,ls='-',color='k',lw=1.5)                              
	ax.add_line(l)
	
	
	#NEXT, DO THE NAVE PLOTTING
	ax2 = myFig.add_axes(pos,frameon=False)
	ax2.yaxis.tick_right()
	ax2.yaxis.set_tick_params(direction='out')
	ax2.set_ylim(bottom=0,top=80)
	ax2.yaxis.set_minor_locator(MultipleLocator(20))
	ax2.yaxis.set_tick_params(direction='out',which='minor')
	
	ax2.plot_date(matplotlib.dates.date2num(myData.times), nave, fmt='k:', \
	tz=None, xdate=True, ydate=False,markersize=2)
	
	loc,lab = plot.xticks()
	plot.xticks(loc,(' '))
	#customize yticks
	plot.yticks([0,80],(' '))
	
	plot.figtext(pos[0]+pos[2]+.01,pos[1]+.004,'0',ha='left',va='bottom',size=8)
	plot.figtext(pos[0]+pos[2]+.01,pos[1]+pos[3],'80',ha='left',va='top',size=8)
	plot.figtext(pos[0]+pos[2]+.06,pos[1]+pos[3]/2.,'Nave',ha='center',va='center',size=8.5,rotation='vertical')
	l=lines.Line2D([pos[0]+pos[2]+.07,pos[0]+pos[2]+.07], [pos[1]+.01,pos[1]+pos[3]-.01], \
	transform=myFig.transFigure,clip_on=False,ls=':',color='k',lw=1.5)                              
	ax2.add_line(l)
