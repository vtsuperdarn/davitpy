import pydarn,numpy,math,matplotlib,calendar,datetime,utils,pylab
import matplotlib.pyplot as plot
import matplotlib.lines as lines
from matplotlib.ticker import MultipleLocator
from matplotlib.collections import PolyCollection
from mpl_toolkits.basemap import Basemap, pyproj
from utils.timeUtils import *

def plotFan(dateStr,rad,time=[0,0],interval=60,fileType='fitex',param='velocity', \
scale=[],channel='a',coords='geo',colors='lasse',gsct=0,pdf=0,fov=1,edgeColors='face'):
	"""
	*******************************
	
	plotFan(dateStr,rad,beam,[time],[fileType]):
	
	crate an rti plot for a secified radar and time period

	INPUTS:
		dateStr: a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		[time]: the range of times for which the file should be read,
			in SIMPLIFIED [hhmm,hhmm] format, eg [29,156], 
			instead of [0029,0156]
			note that an end time of 2400 will read to the end of the file
			default = [0,0]
		[interval]: the interval between fan plots, in seconds
	OUTPUTS:

	EXAMPLE:
		
	Written by AJ 20120905
	*******************************
	"""
	
	
	#check the inputs
	assert(isinstance(dateStr,str) and len(dateStr) == 8),'error, dateStr must be a string 8 chars long'
	assert(isinstance(rad,list)),"error, rad must be a list, eg ['bks'] or ['bks','fhe']"
	for r in rad:
		assert(isinstance(r,str) and len(r) == 3),'error, elements of rad list must be 3 letter strings'
	assert(coords == 'geo'),"error, coords must be one of 'geo' or 'mag'"
	assert(param == 'velocity' or param == 'power' or param == 'width' or \
		param == 'elevation' or param == 'phi0'), \
		"error, allowable params are 'velocity','power','width','elevation','phi0'"
	assert(scale == [] or len(scale)==2), \
	'error, if present, scales must have 2 elements'
	assert(colors == 'lasse' or colors == 'aj'),"error, valid inputs for color are 'lasse' and 'aj'"
	
	if(scale == []):
		if(param == 'velocity'): scale=[-200,200]
		elif(param == 'power'): scale=[0,30]
		elif(param == 'width'): scale=[0,150]
		elif(param == 'elevation'): scale=[0,50]
		elif(param == 'phi0'): scale=[-numpy.pi,numpy.pi]
			
	#convert date string, start time, end time to datetime
	myDate = yyyymmddToDate(dateStr)
	hr1,hr2 = int(math.floor(time[0]/100.)),int(math.floor(time[1]/100.))
	min1,min2 = int(time[0]-hr1*100),int(time[1]-hr2*100)
	sTime = myDate.replace(hour=hr1,minute=min1)
	if(hr2 == 24):
		sTime = myDate+datetime.timedelta(days=1)
	else:
		eTime = myDate.replace(hour=hr2,minute=min2)
		
	#read the radar data
	
	myData=[]
	for r in rad:
		tmpData = pydarn.io.radDataRead(dateStr,r,time=[time[0],int(round(time[1]+interval/60.))],fileType=fileType,vb=0)
		if(tmpData.nrecs > 0):
			myData.append(tmpData.getChannel(channel))

	t1 = datetime.datetime.now()

	xmin,ymin,xmax,ymax = 1e16,1e16,-1e16,-1e16

	sites,fovs,oldCpids,lonFull,latFull=[],[],[],[],[]
	for i in range(len(myData)):
		data=myData[i]
		t=data.times[0]
		site = pydarn.radar.network().getRadarById(data[t]['prm']['stid']).getSiteByDate(utils.yyyymmddToDate(dateStr))
		sites.append(site)
		latFull.append(site.geolat)
		lonFull.append(site.geolon)
		myFov = pydarn.radar.radFov.fov(site=site,rsep=data[t]['prm']['rsep'],ngates=data[t]['prm']['nrang'],nbeams=site.maxbeam)
		fovs.append(myFov)
		for b in range(0,site.maxbeam+1):
			for k in range(0,data[t]['prm']['nrang']+1):
				lonFull.append(myFov.lonFull[b][k])
				latFull.append(myFov.latFull[b][k])
		oldCpids.append(data[t]['prm']['cp'])
	lon_0 = (xmin+xmax)/2.
	lat_0 = (ymin+ymax)/2.
	
	d1=datetime.datetime.now()

	lonFull,latFull = (numpy.array(lonFull)+360.)%360.,numpy.array(latFull)
	
	tmpmap = Basemap(projection='npstere', boundinglat=20,lat_0=90, lon_0=numpy.mean(lonFull))
	
	x,y = tmpmap(lonFull,latFull)
	minx = x.min()
	miny = y.min()
	maxx = x.max()
	maxy = y.max()
	width = (maxx-minx)
	height = (maxy-miny)
	cx = minx + width/2.
	cy = miny + height/2.
	lon_0,lat_0 = tmpmap(cx, cy, inverse=True)
	
	cTime = sTime
	
	while(cTime <= eTime):
		bndTime = cTime + datetime.timedelta(seconds=interval)
		
		myFig = plot.figure()
		#myMap = Basemap(projection='stere',llcrnrlat=lat1,llcrnrlon=lon1,urcrnrlat=lat2,urcrnrlon=lon2,lon_0=lon_0,lat_0=lat_0)

		myMap = Basemap(projection='stere',width=width,height=height,lon_0=numpy.mean(lonFull),lat_0=lat_0)
		bbox = myFig.gca().get_axes().get_position()
		
		plot.figtext((bbox.x0+bbox.x1)/2.,bbox.y1+.02,cTime.strftime('%d/%m/%Y'),ha='center',size=14,weight=600)
		
				
		plot.figtext(bbox.x1,bbox.y1+.02,cTime.strftime('%H:%M - ')+\
		bndTime.strftime('%H:%M      '),ha='right',size=13,weight=600)
		
		plot.figtext(bbox.x0,bbox.y1+.02,'['+fileType+']',ha='left',size=13,weight=600)
		#plotTitle(fileType,cTime)
		#print lat1,lon1,lat2,lon2
		
		myMap.drawparallels(numpy.arange(-80.,81.,10.),labels=[1,0,0,0])
		myMap.drawmeridians(numpy.arange(-180.,181.,20.),labels=[0,0,0,1])
		myMap.drawcoastlines(linewidth=0.5,color='k')
		myMap.drawmapboundary(fill_color='w')
		myMap.fillcontinents(color='w', lake_color='w')


		for i in range(len(myData)):
			data = myData[i]
			if(fov == 1):
				pydarn.plot.overlayRadar(myMap, ids=data[data.times[0]]['prm']['stid'], dateTime=data.times[0], coords=coords)
				
				pydarn.plot.overlayFov(myMap, ids=data[data.times[0]]['prm']['stid'], dateTime=data.times[0], \
				coords=coords,maxGate=data[data.times[0]]['prm']['nrang'])
				
			nptimes = numpy.array(data.times)[numpy.array(data.times) >= cTime]
			for t in nptimes[nptimes < bndTime]:
				if(data[t]['prm']['cp'] != oldCpids[i]):
					sites[i] = pydarn.radar.network().getRadarById(data[t]['prm']['stid']).getSiteByDate(utils.yyyymmddToDate(dateStr))
					fovs[i] = pydarn.radar.radFov.fov(site=site,rsep=data[t]['prm']['rsep'],ngates=data[t]['prm']['nrang'],nbeams=site.maxbeam)
					oldCpids[i] = data[t]['prm']['cp']
				plotFanData(data[t],myFig,myMap,param,scale,coords,colors,gsct,site=sites[i],fov=fovs[i],edgeColors=edgeColors)
		
		myFig.show()
		
		cTime = bndTime
		
	print datetime.datetime.now()-t1

def plotFanData(myData,myFig,myMap,param,scale,coords='geo',colors='lasse',gsct=0,site=None,fov=None,edgeColors='face'):
	"""
	*******************************
	
	plotData(myData,myFig,param,scale,bottom,[yrng],[coords],[pos],[colors]):
	
	plots a frequency and Nave panel on Figure myFig at position pos

	INPUTS:
	OUTPUTS:

		
	Written by AJ 20120905
	*******************************
	"""
	if(site == None):
		site = pydarn.radar.network().getRadarById(myData['prm']['stid']).getSiteByDate(myData['prm']['time'])
	if(fov == None):
		fov = pydarn.radar.radFov.fov(site=site,rsep=myData['prm']['rsep'],\
		ngates=myData['prm']['nrang'],nbeams= site.maxbeam)	
	verts,intensities,gs_flg = [],[],[]
	
		
	#loop through gates with scatter
	for k in range(0,len(myData['fit']['slist'])):
		r = myData['fit']['slist'][k]

		x1,y1 = myMap(fov.lonFull[myData['prm']['bmnum'],r],fov.latFull[myData['prm']['bmnum'],r])
		x2,y2 = myMap(fov.lonFull[myData['prm']['bmnum'],r+1],fov.latFull[myData['prm']['bmnum'],r+1])
		x3,y3 = myMap(fov.lonFull[myData['prm']['bmnum']+1,r+1],fov.latFull[myData['prm']['bmnum']+1,r+1])
		x4,y4 = myMap(fov.lonFull[myData['prm']['bmnum']+1,r],fov.latFull[myData['prm']['bmnum']+1,r])

		#save the polygon vertices
		verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))
		#save the param to use as a color scale
		if(param == 'velocity'): intensities.append(myData['fit']['v'][k])
		elif(param == 'power'): intensities.append(myData['fit']['p_l'][k])
		elif(param == 'width'): intensities.append(myData['fit']['w_l'][k])
		elif(param == 'elevation' and myData[j]['prm']['xcf']): intensities.append(myData['fit']['elv'][k])
		elif(param == 'phi0' and myData[j]['prm']['xcf']): intensities.append(myData['fit']['phi0'][k])
		if(gsct): gs_flg.append(myData['fit']['gflg'][k])

	if(gsct == 0):
		inx = numpy.arange(len(verts))
	else:
		inx = numpy.where(numpy.array(gs_flg)==0)
		x=PolyCollection(numpy.array(verts)[numpy.where(numpy.array(gs_flg)==1)],facecolors='.3',edgecolors=edgeColors,linewidths=.3,alpha=.5,zorder=10)
		myFig.gca().add_collection(x, autolim=True)
		
	pcoll = PolyCollection(numpy.array(verts)[inx],edgecolors=edgeColors,linewidths=.3,closed=False,zorder=5)
	#set color array to intensities
	pcoll.set_array(numpy.array(intensities)[inx])
	myFig.gca().add_collection(pcoll, autolim=True)
	
	pydarn.plot.plotUtils.genCmap(myMap,pcoll,param,scale,colors=colors,map=1)
