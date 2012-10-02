import pydarn,numpy,math,matplotlib,calendar,datetime,utils,pylab
import matplotlib.pyplot as plot
import matplotlib.lines as lines
from matplotlib.ticker import MultipleLocator
from matplotlib.collections import PolyCollection
from utils.timeUtils import *

def plotRti(dateStr,rad,beam=7,time=[0,2400],fileType='fitex',params=['velocity','power','width'], \
scales=[],channel='a',coords='gate',colors='lasse',yrng=-1,gsct=0,pdf=0,filter=0,gflg=0):
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
			['velocity','power','width','elevation','phi0']
			default: ['velocity','power','width']
		[scales]: a list of the min/max values for the color scale for
			each param.  If omitted, default scales will be used.  If present,
			the list should be n x 2 where n is the number of
			elements in the params list.  Use an empty list for default range,
			e.g. [[-250,300],[],[]]
			default: [[-200,200],[0,30],[0,150]]
		[channel]: the channel you wish to plot, the allowable values are
			'a' and 'b'
			default: 'a'
		[coords]: the coordinates to use for the y axis.  The allowable values are
			'gate','rng','geo'
			default: 'gate'
		[colors]: a string indicating what color bar to use, valid inputs are
			['lasse','aj']
			default: 'lasse'
		[yrng]: a list indicating the min and max values for the y axis in the
			chosen coordinate system, or a -1 indicating to plot everything
			default: -1
		[gsct]: a flag indicating whether to plot ground scatter as transparent
			default: 0 (ground scatter plotted normally)
	OUTPUTS:

	EXAMPLE:
		plotRti('20120101','bks',beam=12,time=[10,1453],fileType='fitex',
		params=['vel','power'],scales=[[-200,200],[]],channel='b',
		coords='mag'):
		
	Written by AJ 20120807
	*******************************
	"""
	t1 = datetime.datetime.now()
	#check the inputs
	assert(isinstance(dateStr,str) and len(dateStr) == 8),'error, dateStr must be a string 8 chars long'
	assert(isinstance(rad,str) and len(rad) == 3),'error, dateStr must be a string 3 chars long'
	assert(coords == 'gate' or coords == 'rng' or coords == 'geo' or coords == 'mag'),\
	"error, coords must be one of 'gate','rng','geo','mag"
	assert(isinstance(beam,int)),'error, beam must be integer'
	assert(0 < len(params) < 6),'error, must input between 1 and 5 params in LIST form'
	for i in range(0,len(params)):
		assert(params[i] == 'velocity' or params[i] == 'power' or params[i] == 'width' or \
		params[i] == 'elevation' or params[i] == 'phi0'), \
		"error, allowable params are 'velocity','power','width','elevation','phi0'"
	assert(scales == [] or len(scales)==len(params)), \
	'error, if present, scales must have same number of elements as params'
	assert(yrng == -1 or (isinstance(yrng,list) and yrng[0] <= yrng[1])), \
	'error, yrng must equal -1 or be a list with the 2nd element larger than the first'
	assert(colors == 'lasse' or colors == 'aj'),"error, valid inputs for color are 'lasse' and 'aj'"
	
	tscales = []
	for i in range(0,len(params)):
		if(scales == [] or scales[i] == []):
			if(params[i] == 'velocity'): tscales.append([-200,200])
			elif(params[i] == 'power'): tscales.append([0,30])
			elif(params[i] == 'width'): tscales.append([0,150])
			elif(params[i] == 'elevation'): tscales.append([0,50])
			elif(params[i] == 'phi0'): tscales.append([-numpy.pi,numpy.pi])
		else: tscales.append(scales[i])
	scales = tscales
			
	#convert date string, start time, end time to datetime
	myDate = yyyymmddToDate(dateStr)
	hr1,hr2 = int(math.floor(time[0]/100.)),int(math.floor(time[1]/100.))
	min1,min2 = int(time[0]-hr1*100),int(time[1]-hr2*100)
	stime = myDate.replace(hour=hr1,minute=min1)
	if(hr2 == 24):
		etime = myDate+datetime.timedelta(days=1)
	else:
		etime = myDate.replace(hour=hr2,minute=min2)
		
	#open the file
	myFile = pydarn.io.dmapOpen(dateStr,rad,time=time,fileType=fileType,filter=filter)
	
	assert(myFile != None),'error, no data available for the requested time/radar/filetype combination'
	myBeam = pydarn.io.radDataReadRec(myFile,beam=beam,channel=channel)
	assert(myBeam != None),'error, no data available for the requested time/radar/filetype combination'
	
	vel,pow,wid,elev,phi0,times,freq,cpid,nave,nsky,nsch,slist,mode,rsep,nrang,frang=[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
	
	while(myBeam != None):
		if(myBeam['prm']['time'] > etime): break
		if(myBeam['prm']['bmnum'] == beam and (stime <= myBeam['prm']['time'])):
			times.append(myBeam['prm']['time'])
			cpid.append(myBeam['prm']['cp'])
			nave.append(myBeam['prm']['nave'])
			nsky.append(myBeam['prm']['noise.sky'])
			rsep.append(myBeam['prm']['rsep'])
			nrang.append(myBeam['prm']['nrang'])
			frang.append(myBeam['prm']['frang'])
			nsch.append(myBeam['prm']['noise.search'])
			freq.append(myBeam['prm']['tfreq']/1e3)
			slist.append(myBeam['fit']['slist'])
			mode.append(myBeam['prm']['ifmode'])
			if('velocity' in params): vel.append(myBeam['fit']['v'])
			if('power' in params): pow.append(myBeam['fit']['p_l'])
			if('width' in params): wid.append(myBeam['fit']['w_l'])
			if('elevation' in params): elev.append(myBeam['fit']['elv'])
			if('phi0' in params): phi0.append(myBeam['fit']['phi0'])
			

		myBeam = pydarn.io.radDataReadRec(myFile,beam=beam,channel=channel)
		
	myFile.close()
	
	rtiFig = plot.figure()

	rtiTitle(dateStr,rad,fileType,beam)
	
	plotNoise(rtiFig,times,nsky,nsch)
	
	plotFreq(rtiFig,times,freq,nave)
	
	plotCpid(rtiFig,times,cpid,mode)
	
	
	
	figtop = .77
	figheight = .72/len(params)
	for p in range(len(params)):
		if(params[p] == 'velocity'): pArr = vel
		elif(params[p] == 'power'): pArr = pow
		elif(params[p] == 'width'): pArr = wid
		elif(params[p] == 'elevation'): pArr = elev
		elif(params[p] == 'phi0'): pArr = phi0
		pos = [.1,figtop-figheight*(p+1)+.02,.76,figheight-.02]
		
		ax = drawAxes(rtiFig,times,rad,cpid,beam,nrang,frang,rsep,p==len(params)-1,yrng=yrng,coords=coords,\
		pos=pos)
			

		if(pArr == []): continue
		
		rmax = max(nrang)
		data=numpy.zeros((len(times)*2,rmax))+100000
		x=numpy.zeros(len(times)*2)
		tcnt = 0
		#x = matplotlib.dates.date2num(times)
		for i in range(len(times)):
			x[tcnt]=matplotlib.dates.date2num(times[i])
			if(i < len(times)-1):
				if(matplotlib.dates.date2num(times[i+1])-x[tcnt] > 4./1440.):
					tcnt += 1
					x[tcnt] = x[tcnt-1]+1./1440.
			tcnt += 1
					
			if(pArr[i] == []): continue
			
			for j in range(len(slist[i])):
				data[tcnt][slist[i][j]] = pArr[i][j]
				
		if(coords == 'gate'): y = numpy.linspace(0,rmax,rmax+1)
		elif(coords == 'rng'): y = numpy.linspace(frang[0],rmax*rsep[0],rmax+1)
		else:
			site = pydarn.radar.network().getRadarByCode(rad).getSiteByDate(times[0])
			myFov = pydarn.radar.radFov.fov(site=site, ngates=rmax,nbeams=site.maxbeam,rsep=rsep[0],coords=coords)
			y =  myFov.latFull[beam]
			
		X, Y = numpy.meshgrid(x[:tcnt], y)
		

		
		#data = numpy.ma.masked_where(data == 100000., data)
		pcoll = plot.pcolormesh(X, Y, data[:tcnt][:].T, lw=0.01,edgecolors='None',alpha=1,lod=True)
		
			
		pydarn.plot.plotUtils.genCmap(rtiFig,pcoll,params[p],scales[p],pos=pos,colors=colors,gflg=gflg)
			
	print 'done plot'
	


	if(pdf):
		rtiFig.savefig('/home/miker/temp.png',orientation='landscape', papertype='letter',dpi=300)
	else:
		rtiFig.show()
		
	print datetime.datetime.now()-t1

	
def drawAxes(myFig,times,rad,cpid,bmnum,nrang,frang,rsep,bottom,yrng=-1,coords='gate',pos=[.1,.05,.76,.72]):
	"""
	*******************************

	Written by AJ 20120807
	*******************************
	"""
	nrecs = len(times)
	#add an axes to the figure
	ax = myFig.add_axes(pos)
	ax.yaxis.set_tick_params(direction='out')
	ax.xaxis.set_tick_params(direction='out')
	ax.yaxis.set_tick_params(direction='out',which='minor')
	ax.xaxis.set_tick_params(direction='out',which='minor')

	#draw the axes
	ax.plot_date(matplotlib.dates.date2num(times), numpy.arange(len(times)), fmt='w', \
	tz=None, xdate=True, ydate=False, alpha=0.0)
	
	if(yrng == -1):
		ymin,ymax = 99999999,-999999999
		if(coords != 'gate'):
			oldCpid = -99999999
			for i in range(len(cpid)):
				if(cpid[i] == oldCpid): continue
				oldCpid = cpid[i]
				if(coords == 'geo' or coords == 'mag'):
					site = pydarn.radar.network().getRadarByCode(rad).getSiteByDate(times[i])
					myFov = pydarn.radar.radFov.fov(site=site, ngates=nrang[i],nbeams=site.maxbeam,rsep=rsep[i],coords=coords)
					if(myFov.latFull[bmnum].max() > ymax): ymax = myFov.latFull[bmnum].max()
					if(myFov.latFull[bmnum].min() < ymin): ymin = myFov.latFull[bmnum].min()
				else:
					ymin = 0
					if(nrang[i]*rsep[i]+frang[i] > ymax): ymax = nrang[i]*rsep[i]+frang[i]
		
		else:
			ymin,ymax = 0,max(nrang)
	else:
		ymin,ymax = yrng[0],yrng[1]

	xmin,xmax = matplotlib.dates.date2num(times[0]),matplotlib.dates.date2num(times[len(times)-1])
	xrng = (xmax-xmin)
	inter = int(round(xrng/6.*86400.))
	inter2 = int(round(xrng/24.*86400.))
	#format the x axis
	ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
	ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))
	plot.xticks(size=9)
	if(not bottom):
		loc,lab = plot.xticks()
		plot.xticks(loc,(' '))
	else:
		ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
		ax.xaxis.set_label_text('UT')
		
	#set ytick size
	plot.yticks(size=9)
	#format y axis depending on coords
	if(coords == 'gate'): 
		ax.yaxis.set_label_text('Range gate',size=10)
		ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))
		ax.yaxis.set_major_locator(MultipleLocator((ymax-ymin)/5.))
		ax.yaxis.set_minor_locator(MultipleLocator((ymax-ymin)/25.))
	elif(coords == 'geo' or coords == 'mag'): 
		if(coords == 'mag'): ax.yaxis.set_label_text('Mag Lat [deg]',size=10)
		else: ax.yaxis.set_label_text('Geo Lat [deg]',size=10)
		ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%0.2f'))
		ax.yaxis.set_major_locator(MultipleLocator((ymax-ymin)/5.))
		ax.yaxis.set_minor_locator(MultipleLocator((ymax-ymin)/25.))
	elif(coords == 'rng'): 
		ax.yaxis.set_label_text('Slant Range [km]',size=10)
		ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))
		ax.yaxis.set_major_locator(MultipleLocator(1000))
		ax.yaxis.set_minor_locator(MultipleLocator(250))
	
	ax.set_ylim(bottom=ymin,top=ymax)

	return ax
		
def rtiTitle(dateStr,rad,fileType,beam,xmin=.1,xmax=.86):
	"""
	*******************************
	
	rtiTitle(myData,dateStr,beam,[xmin],[xmax]):
	
	prints a title on an rti plot

	INPUTS:
		myData: a radarData object containing the data to be plotted
		dateStr: the date in yyyymmdd format
		beam: the beam number
		[xmin]: coord for left alignment
		[xmax]: coord for right alignment
	OUTPUTS:

		
	Written by AJ 20120807
	*******************************
	"""
	r=pydarn.radar.network().getRadarByCode(rad)
	
	plot.figtext(xmin,.95,r.name+'  ('+fileType+')',ha='left',weight=550)
	
	d = utils.yyyymmddToDate(dateStr)
	plot.figtext((xmin+xmax)/2.,.95,str(d.day)+'/'+calendar.month_name[d.month][:3]+'/'+str(d.year), \
	weight=550,size='large',ha='center')
	
	plot.figtext(xmax,.95,'Beam '+str(beam),weight=550,ha='right')
	
def plotCpid(myFig,times,cpid,mode,pos=[.1,.77,.76,.05]):
	"""
	*******************************
	
	plotCpid(myData,myFig,[pos]):
	
	plots a cpid panel on Figure myFig at position pos

	INPUTS:
		myData: a radarData object containing the data to be plotted
		myFig: the figure to plot the panel on
		[pos]: the position of the panel, [xmin, ymin, xsize, ysize]
	OUTPUTS:

		
	Written by AJ 20120807
	*******************************
	"""
	oldCpid = -9999999
	
	#add an axes to the figure
	ax = myFig.add_axes(pos)
	ax.yaxis.tick_left()
	ax.yaxis.set_tick_params(direction='out')
	ax.set_ylim(bottom=0,top=1)
	ax.yaxis.set_minor_locator(MultipleLocator(1))
	ax.yaxis.set_tick_params(direction='out',which='minor')
	
	#draw the axes
	ax.plot_date(matplotlib.dates.date2num(times), numpy.arange(len(times)), fmt='w', \
	tz=None, xdate=True, ydate=False, alpha=0.0)
	
	for i in range(0,len(times)):
		if(cpid[i] != oldCpid):
			
			ax.plot_date([matplotlib.dates.date2num(times[i]),matplotlib.dates.date2num(times[i])],\
			[0,1], fmt='k-', tz=None, xdate=True, ydate=False)
			
			oldCpid = cpid[i]
			
			s = ' '+pydarn.radar.radUtils.getCpName(oldCpid)
		
			istr = ' '
			if(mode[i] == 1): istr = ' IF'
			if(mode == 0): istr = ' RF'
			
			ax.text(times[i],.5,' '+str(oldCpid)+s+istr,ha='left',va='center', size=10)
			
			
	xmin,xmax = matplotlib.dates.date2num(times[0]),matplotlib.dates.date2num(times[len(times)-1])
	xrng = (xmax-xmin)
	inter = int(round(xrng/6.*86400.))
	inter2 = int(round(xrng/24.*86400.))
	#format the x axis
	ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
	ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))
	plot.xticks(size=9)
			
	#remove the x tick labels
	loc,lab = plot.xticks()
	plot.xticks(loc,(' '))
	#use only 2 major yticks
	plot.yticks([],(' '))
	plot.figtext(pos[0]-.07,pos[1]+pos[3]/2.,'CPID',ha='center',va='center', \
	size=8.5,rotation='vertical')
	
	
	
		
def plotNoise(myFig,times,sky,search,pos=[.1,.88,.76,.06]):
	"""
	*******************************
	
	plotNoise(myData,myFig,[pos]):
	
	plots a noise panel on Figure myFig at position pos

	INPUTS:
		myData: a radarData object containing the data to be plotted
		myFig: the figure to plot the panel on
		[pos]: the position of the panel, [xmin, ymin, xsize, ysize]
	OUTPUTS:

		
	Written by AJ 20120807
	*******************************
	"""
	#read the data
	#add an axes to the figure
	ax = myFig.add_axes(pos)
	ax.yaxis.tick_left()
	ax.yaxis.set_tick_params(direction='out')
	ax.set_ylim(bottom=0,top=6)
	ax.yaxis.set_minor_locator(MultipleLocator())
	ax.yaxis.set_tick_params(direction='out',which='minor')
	
	xmin,xmax = matplotlib.dates.date2num(times[0]),matplotlib.dates.date2num(times[len(times)-1])
	xrng = (xmax-xmin)
	inter = int(round(xrng/6.*86400.))
	inter2 = int(round(xrng/24.*86400.))
	#format the x axis
	ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
	ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))
	plot.xticks(size=9)
	
	#plot the sky noise data
	ax.plot_date(matplotlib.dates.date2num(times), numpy.log10(sky), fmt='k-', \
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
	ax2.plot_date(matplotlib.dates.date2num(times), numpy.log10(search), fmt='k:', \
	tz=None, xdate=True, ydate=False,lw=1.5)
	
	#remove the x tick labels
	loc,lab = plot.xticks()
	plot.xticks([0],(' '))
	#use only 2 major yticks
	plot.yticks([0,6],(' '))
	
	#right y axis annotation
	plot.figtext(pos[0]+pos[2]+.01,pos[1]+.004,'10^0',ha='left',va='bottom',size=8)
	plot.figtext(pos[0]+pos[2]+.01,pos[1]+pos[3],'10^6',ha='left',va='top',size=8)
	plot.figtext(pos[0]+pos[2]+.06,pos[1]+pos[3]/2.,'N.Sch',ha='center',va='center',size=8.5,rotation='vertical')
	l=lines.Line2D([pos[0]+pos[2]+.07,pos[0]+pos[2]+.07], [pos[1]+.01,pos[1]+pos[3]-.01], \
	transform=myFig.transFigure,clip_on=False,ls=':',color='k',lw=1.5)                              
	ax2.add_line(l)
	
def plotFreq(myFig,times,freq,nave,pos=[.1,.82,.76,.06]):
	"""
	*******************************
	
	plotFreq(myData,myFig,[pos]):
	
	plots a frequency and Nave panel on Figure myFig at position pos

	INPUTS:
		myData: a radarData object containing the data to be plotted
		myFig: the figure to plot the panel on
		[pos]: the position of the panel, [xmin, ymin, xsize, ysize]
	OUTPUTS:

		
	Written by AJ 20120807
	*******************************
	"""
		
	#FIRST, DO THE TFREQ PLOTTING
	ax = myFig.add_axes(pos)
	ax.yaxis.tick_left()
	ax.yaxis.set_tick_params(direction='out')
	ax.set_ylim(bottom=10,top=16)
	ax.yaxis.set_minor_locator(MultipleLocator())
	ax.yaxis.set_tick_params(direction='out',which='minor')
	
	for f in freq:
		if(f > 16): f = 16
		if(f < 10): f = 10
		
	ax.plot_date(matplotlib.dates.date2num(times), freq, fmt='k-', \
	tz=None, xdate=True, ydate=False,markersize=2)
	
	loc,lab = plot.xticks()
	plot.xticks(loc,(' '))
	#customize yticks
	plot.yticks([10,16],(' '))
	
	xmin,xmax = matplotlib.dates.date2num(times[0]),matplotlib.dates.date2num(times[len(times)-1])
	xrng = (xmax-xmin)
	inter = int(round(xrng/6.*86400.))
	inter2 = int(round(xrng/24.*86400.))
	#format the x axis
	ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
	ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))
	plot.xticks(size=9)
	
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
	
	ax2.plot_date(matplotlib.dates.date2num(times), nave, fmt='k:', \
	tz=None, xdate=True, ydate=False,markersize=2)
	
	loc,lab = plot.xticks()
	plot.xticks([0],(' '))
	#customize yticks
	plot.yticks([0,80],(' '))
	
	plot.figtext(pos[0]+pos[2]+.01,pos[1]+.004,'0',ha='left',va='bottom',size=8)
	plot.figtext(pos[0]+pos[2]+.01,pos[1]+pos[3],'80',ha='left',va='top',size=8)
	plot.figtext(pos[0]+pos[2]+.06,pos[1]+pos[3]/2.,'Nave',ha='center',va='center',size=8.5,rotation='vertical')
	l=lines.Line2D([pos[0]+pos[2]+.07,pos[0]+pos[2]+.07], [pos[1]+.01,pos[1]+pos[3]-.01], \
	transform=myFig.transFigure,clip_on=False,ls=':',color='k',lw=1.5)                              
	ax2.add_line(l)
