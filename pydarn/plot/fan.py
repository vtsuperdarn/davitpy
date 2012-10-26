"""
*******************************
MODULE: pydarn.plot.fan
*******************************

This module contains the following functions:

	plotFan

	plotFanData
"""
	
import pydarn,numpy,math,matplotlib,calendar,datetime,utils,pylab
import matplotlib.pyplot as plot
import matplotlib.lines as lines
from matplotlib.ticker import MultipleLocator
import matplotlib.patches as patches
from matplotlib.collections import PolyCollection,LineCollection
from mpl_toolkits.basemap import Basemap, pyproj
from utils.timeUtils import *
from pydarn.sdio.radDataRead import *

def plotFan(dateStr,rad,time=[0,0],interval=1,fileType='fitex',param='velocity',filter=0 ,\
		scale=[],channel='a',coords='geo',colors='lasse',gsct=0,fov=1,edgeColors='face',gflg=0,fill=1,\
		velscl=1000.,legend=1):
	"""
|	*************************************************
|	**PACKAGE**: pydarn.plot.fan
|	**FUNCTION**: plotFan(dateStr,rad,time=[0,0],interval=1,fileType='fitex',param='velocity',filter=0 ,
|								scale=[],channel='a',coords='geo',colors='lasse',gsct=0,pdf=0,fov=1,edgeColors='face',gflg=0)
|	**PURPOSE**: makes fov (fan) plots
|
|	**INPUTS**:
|		**dateStr**: a string containing the target date in yyyymmdd format
|		**rad**: a list of 3 letter radar codes
|		**[time]**: the range of times for which should be plotted
|			in SIMPLIFIED [hhmm,hhmm] format, eg [29,156], instead of [0029,0156]
|			note that an end time of 2400 will read to the end of the file
|			default = [0,0]
|		**[interval]**: the interval between fan plots, in minutes
|		**[fileType]**: the file type to plot, valid inputs are 'fitex','fitacf',
|			'lmfit'.  default = 'fitex'
|		**[param]**: the parameter to be plotted, valid inputs are 'velocity', 
|			'power', 'width', 'elevation', 'phi0'.  default = 'velocity
|		**[filter]**: a flag indicating whether the data should be boxcar filtered
|			default = 0
|		**[scale]**: the min and max values of the color scale.  If this is set to []
|			then default values will be used
|		**[channel]**: the channel for which to plot data.  default = 'a'
|		**[coords]**: the coordinate system to use, valid inputs are 'geo' and 'mag'
|			default = 'geo'
|		**[colors]**: the color map to use, valid inputs are 'lasse', 'aj'
|			default = 'lasse'
|		**[gsct]**: a flag indicating whether to plot ground scatter as gray.
|			default = 0
|		**[fov]**: a flag indicating whether to overplot the radar fields of view
|			default = 0
|		**[edgeColors]**: edge colors of the polygons, default = 'face'
|		**[gflg]**: a flag indicating whether to plot low velocities in gray
|			default = 0
|		**[fill]**: a flag indicating whether to plot filled or point RB cells
|			default = 1
|		**[velscl]**: the velocity to use as baseline for velocity vector length,
|			only applicable if fill = 0.  default = 1000
|		**[legend]**: a flag indicating whether to plot the legend
|			only applicable if fill = 0.  default = 1
|	**OUTPUTS**:
|		NONE
|
|	**EXAMPLE**:
|		plotFan('20121001',['bks','fhw'],time=[0,24],interval=2,fileType='fitex',param='velocity',filter=0 ,
|								scale=[-400,400],channel='a',coords='geo',colors='lasse',gsct=0,pdf=0,fov=1,edgeColors='face',gflg=0)
|
|	Written by AJ 20121004
|
	"""
	
	from matplotlib.backends.backend_pdf import PdfPages
	import models.aacgm as aacgm
	
	#check the inputs
	assert(isinstance(dateStr,str) and len(dateStr) == 8),'error, dateStr must be a string 8 chars long'
	assert(isinstance(rad,list)),"error, rad must be a list, eg ['bks'] or ['bks','fhe']"
	for r in rad:
		assert(isinstance(r,str) and len(r) == 3),'error, elements of rad list must be 3 letter strings'
	assert(coords == 'geo' or coords == 'mag'),"error, coords must be one of 'geo' or 'mag'"
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
			
	#check for plotting directory, create if does not exist
	d = os.environ['PYPLOTS']+'/fan'
	if not os.path.exists(d):
		os.makedirs(d)
		
	pp = PdfPages(d+'/'+dateStr+'.fan.pdf')
	
	#convert date string, start time, end time to datetime
	myDate = yyyymmddToDate(dateStr)
	hr1,hr2 = int(math.floor(time[0]/100.)),int(math.floor(time[1]/100.))
	min1,min2 = int(time[0]-hr1*100),int(time[1]-hr2*100)
	sTime = myDate.replace(hour=hr1,minute=min1)
	if(hr2 == 24):
		sTime = myDate+datetime.timedelta(days=1)
	else:
		eTime = myDate.replace(hour=hr2,minute=min2)
		
	#open the data files
	myFiles = []
	for r in rad:
		f = dmapOpen(dateStr,r,time=time,fileType=fileType,filter=filter)
		if(f != None): myFiles.append(f)

	assert(myFiles != []),'error, no data available for this period'

	xmin,ymin,xmax,ymax = 1e16,1e16,-1e16,-1e16

	allBeams = [''] * len(myFiles)
	sites,fovs,oldCpids,lonFull,latFull=[],[],[],[],[]
	#go through all open files
	for i in range(len(myFiles)):
		#read until we reach start time
		allBeams[i] = radDataReadRec(myFiles[i],channel=channel)
		while(allBeams[i]['prm']['time'] < sTime and allBeams[i] != None):
			allBeams[i] = radDataReadRec(myFiles[i],channel=channel)
			
		#check that the file has data in the target interval
		if(allBeams[i] == None): 
			myFiles[i].close()
			myFiles[i] = None
			continue
	
		#get to field of view coords in order to determine map limits
		t=allBeams[i]['prm']['time']
		site = pydarn.radar.network().getRadarById(allBeams[i]['prm']['stid']).getSiteByDate(t)
		sites.append(site)
		if(coords == 'geo'):
			latFull.append(site.geolat)
			lonFull.append(site.geolon)
		elif(coords == 'mag'):
			x = aacgm.aacgmConv(site.geolat,site.geolon,0.,0)
			latFull.append(x[0])
			lonFull.append(x[1])
		myFov = pydarn.radar.radFov.fov(site=site,rsep=allBeams[i]['prm']['rsep'],\
						ngates=allBeams[i]['prm']['nrang']+1,nbeams=site.maxbeam,coords=coords)
		fovs.append(myFov)
		for b in range(0,site.maxbeam+1):
			for k in range(0,allBeams[i]['prm']['nrang']+1):
				lonFull.append(myFov.lonFull[b][k])
				latFull.append(myFov.latFull[b][k])
		oldCpids.append(allBeams[i]['prm']['cp'])
			
	#do some stuff in map projection coords to get necessary width and height of map
	lon_0 = (xmin+xmax)/2.
	lat_0 = (ymin+ymax)/2.
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
	dist = width/50.
	cTime = sTime
	
	myFig = plot.figure()

	#draw the actual map we want
	myMap = Basemap(projection='stere',width=width,height=height,lon_0=numpy.mean(lonFull),lat_0=lat_0)
	myMap.drawparallels(numpy.arange(-80.,81.,10.),labels=[1,0,0,0])
	myMap.drawmeridians(numpy.arange(-180.,181.,20.),labels=[0,0,0,1])
	if(coords == 'geo'):
		myMap.drawcoastlines(linewidth=0.5,color='k')
		myMap.drawmapboundary(fill_color='w')
		myMap.fillcontinents(color='w', lake_color='w')
	#overlay fields of view, if desired
	if(fov == 1):
		for r in rad:
			pydarn.plot.overlayRadar(myMap, codes=r, dateTime=sTime, coords=coords)
			pydarn.plot.overlayFov(myMap, codes=r, dateTime=sTime,coords=coords)
				
	#manually draw the legend
	if(fill == 0 and legend == 1):
		#draw the box
		y = [myMap.urcrnry*.82,myMap.urcrnry*.99]
		x = [myMap.urcrnrx*.86,myMap.urcrnrx*.99]
		verts = [x[0],y[0]],[x[0],y[1]],[x[1],y[1]],[x[1],y[0]]
		poly = patches.Polygon(verts,fc='w',ec='k',zorder=11)
		myFig.gca().add_patch(poly)
		labs = ['5 dB','15 dB','25 dB','35 dB','gs','1000 m/s']
		pts = [5,15,25,35]
		#plot the icons and labels
		for w in range(6):
			myFig.gca().text(x[0]+.35*(x[1]-x[0]),y[1]*(.98-w*.025),labs[w],zorder=15,color='k',size=6,va='center')
			xctr = x[0]+.175*(x[1]-x[0])
			if(w < 4):
				plot.scatter(xctr,y[1]*(.98-w*.025),s=.1*pts[w],zorder=15,marker='o',linewidths=.5,\
				edgecolor='face',facecolor='k')
			elif(w == 4):
				plot.scatter(xctr,y[1]*(.98-w*.025),s=.1*35.,zorder=15,marker='o',\
				linewidths=.5,edgecolor='k',facecolor='w')
			elif(w == 5):
				y=LineCollection(numpy.array([((xctr-dist/2.,y[1]*(.98-w*.025)),(xctr+dist/2.,y[1]*(.98-w*.025)))]),linewidths=.5,zorder=15,color='k')
				myFig.gca().add_collection(y)
				
	bbox = myFig.gca().get_axes().get_position()
	#now, loop through desired time interval
	while(cTime <= eTime):
		bndTime = cTime + datetime.timedelta(minutes=interval)

		gs_flg,lines = [],[]
		if(fill == 1): verts,intensities = [],[]
		
		else: verts,intensities = [[],[]],[[],[]]
		
		ft = 'None'
		#go though all files
		for i in range(len(myFiles)):
			#check that we have good data at this time
			if(myFiles[i] == None or allBeams[i] == None): continue
			
			ft = allBeams[i].ftype
			#read until we reach out time window
			while(allBeams[i]['prm']['time'] < cTime and allBeams[i] != None):
				allBeams[i] = radDataReadRec(myFiles[i],channel=channel)
				
			#until we reach the end of the time window
			while(allBeams[i]['prm']['time'] <= bndTime and allBeams[i] != None):
				
				#check for a control program change
				#if(allBeams[i]['prm']['cp'] != oldCpids[i]):
					#sites[i] = pydarn.radar.network().getRadarById(allBeams[i]['prm']['stid']).getSiteByDate(allBeams[i]['prm']['time'])
					
					#fovs[i] = pydarn.radar.radFov.fov(site=site,rsep=allBeams[i]['prm']['rsep'],\
					#ngates=allBeams[i]['prm']['nrang']+1,nbeams=site.maxbeam)
					
					#oldCpids[i] = allBeams[i]['prm']['cp']
					
				#get verts and intesities for polygon along current beam
				plotFanData(allBeams[i],myMap,param,coords,gsct=gsct,site=sites[i],fov=fovs[i],\
										verts=verts,intensities=intensities,gs_flg=gs_flg,fill=fill,velscl=velscl,\
										lines=lines,dist=dist)
				#read the next record
				allBeams[i] = radDataReadRec(myFiles[i],channel=channel)
				
		#if we are filling rb cells
		if(fill == 1):
			#if we have data
			if(verts != []):
				if(gsct == 0):
					inx = numpy.arange(len(verts))
				else:
					inx = numpy.where(numpy.array(gs_flg)==0)
					x=PolyCollection(numpy.array(verts)[numpy.where(numpy.array(gs_flg)==1)],facecolors='.3',linewidths=0,alpha=.5,zorder=5)
					myFig.gca().add_collection(x, autolim=True)
					
				pcoll = PolyCollection(numpy.array(verts)[inx],edgecolors=edgeColors,linewidths=0,closed=False,zorder=10,rasterized=True)
				#set color array to intensities
				pcoll.set_array(numpy.array(intensities)[inx])
				myFig.gca().add_collection(pcoll, autolim=True)
				#generate color map
				pydarn.plot.plotUtils.genCmap(myMap,pcoll,param,scale,colors=colors,map=1,gflg=gflg)
		#if we are plotting points and vectors
		else:
			#if we have data
			if(verts != [[],[]]):
				if(gsct == 0):
					inx = numpy.arange(len(verts[0]))
				else:
					inx = numpy.where(numpy.array(gs_flg)==0)
					#plot the ground scatter as open circles
					x = plot.scatter(numpy.array(verts[0])[numpy.where(numpy.array(gs_flg)==1)],\
							numpy.array(verts[1])[numpy.where(numpy.array(gs_flg)==1)],\
							s=.1*numpy.array(intensities[1])[numpy.where(numpy.array(gs_flg)==1)],\
							zorder=5,marker='o',linewidths=.5,facecolors='w',edgecolors='k')
					myFig.gca().add_collection(x, autolim=True)
					
				#plot the i-s as filled circles
				ccoll = myFig.gca().scatter(numpy.array(verts[0])[inx],numpy.array(verts[1])[inx],\
								s=.1*numpy.array(intensities[1])[inx],zorder=10,marker='o',linewidths=.5,edgecolors='face')
				
				#set color array to intensities
				ccoll.set_array(numpy.array(intensities[0])[inx])
				#generate color map
				pydarn.plot.plotUtils.genCmap(myMap,ccoll,param,scale,colors=colors,map=1,gflg=gflg)
				myFig.gca().add_collection(ccoll)
				#plot the velocity vectors
				lcoll = LineCollection(numpy.array(lines)[inx],linewidths=.5,zorder=12)
				lcoll.set_array(numpy.array(intensities[0])[inx])
				pydarn.plot.plotUtils.genCmap(myMap,lcoll,param,scale,colors=colors,map=1,gflg=gflg)
				myFig.gca().add_collection(lcoll)

		myFig.gca().set_rasterized(True)
		#label the plot
		tx1 = plot.figtext((bbox.x0+bbox.x1)/2.,bbox.y1+.02,cTime.strftime('%d/%m/%Y'),ha='center',size=14,weight=550)
		tx2 = plot.figtext(bbox.x1,bbox.y1+.02,cTime.strftime('%H:%M - ')+\
					bndTime.strftime('%H:%M      '),ha='right',size=13,weight=550)
		tx3 = plot.figtext(bbox.x0,bbox.y1+.02,'['+ft[1:]+']',ha='left',size=13,weight=550)
		#save plot to pdf
		myFig.savefig(pp, format='pdf', dpi=300,orientation='landscape')
		myFig.show()
		#return myFig,ccoll
		#ccoll.remove()
		#lcoll.remove()
		if(verts != [[],[]] and verts != []):
			if(fill == 1): 
				pcoll.remove()
			else: 
				ccoll.set_paths([])
				lcoll.remove()
			
			if(gsct == 1): x.remove()
			
		myFig.texts.remove(tx1)
		myFig.texts.remove(tx2)
		myFig.texts.remove(tx3)
		#increment time by interval
		cTime = bndTime
	#close the pdf
	pp.close()
	#close the open files
	for f in myFiles:
		if(f != None): f.close()
		
	print 'file is at: '+d+'/'+dateStr+'.fan.pdf'

def plotFanData(myData,myMap,param,coords='geo',gsct=0,site=None,\
		fov=None,verts=[],intensities=[],gs_flg=[],fill=1,velscl=1000.,lines=[],dist=1000.):
	"""
| *************************************************
|	**PACKAGE**: pydarn.plot.fan
|	**FUNCTION**: plotFanData(myData,myMap,param,coords='geo',gsct=0,site=None,
|								fov=None,verts=[],intensities=[],gs_flg=[])
|	**PURPOSE**: gets vertices and intensities of polygons in a beam 
|
|	**INPUTS**:
|		**myData**: a radar beam object
|		**myMap**: the map we are plotting on
|		**[param]**: the parameter we are plotting
|		**[coords]**: the coordinates we are plotting in
|		**[param]**: the parameter to be plotted, valid inputs are 'velocity', 
|			'power', 'width', 'elevation', 'phi0'.  default = 'velocity
|		**[gsct]**: a flag indicating whether we are distinguishing groudn  scatter
|			default = 0
|		**[intensities]**: a list of intensities
|		**[verts]**: a list of vertices
|		**[fov]**: a radar fov object
|		**[gs_flg]**: a list of gs flags, 1 per range gate
|		**[fill]**: a flag indicating whether to plot filled or point RB cells
|			default = 1
|		**[velscl]**: the velocity to use as baseline for velocity vector length,
|			only applicable if fill = 0.  default = 1000
|		**[lines]**: an array to have the endpoints of velocity vectors
|			only applicable if fill = 0.  default = []
|		**[dist]**: the length in map projection coords of a velscl length
|			velocity vector.  default = 1000. km
|	**OUTPUTS**:
|		NONE
|
|	**EXAMPLE**:
|		plotFanData(aBeam,myMap,param,coords,gsct=gsct,site=sites[i],fov=fovs[i],\
|														verts=verts,intensities=intensities,gs_flg=gs_flg)
|
|	Written by AJ 20121004
	"""
	if(site == None):
		site = pydarn.radar.network().getRadarById(myData['prm']['stid']).getSiteByDate(myData['prm']['time'])
	if(fov == None):
		fov = pydarn.radar.radFov.fov(site=site,rsep=myData['prm']['rsep'],\
		ngates=myData['prm']['nrang']+1,nbeams= site.maxbeam,coords=coords)	
	
		
	#loop through gates with scatter
	for k in range(0,len(myData['fit']['slist'])):
		r = myData['fit']['slist'][k]

		if(fill == 1):
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
		else:
			x1,y1 = myMap(fov.lonCenter[myData['prm']['bmnum'],r],fov.latCenter[myData['prm']['bmnum'],r])
			verts[0].append(x1)
			verts[1].append(y1)
			
			x2,y2 = myMap(fov.lonCenter[myData['prm']['bmnum'],r+1],fov.latCenter[myData['prm']['bmnum'],r+1])
			
			theta = math.atan2(y2-y1,x2-x1)
			
			x2,y2 = x1+myData['fit']['v'][k]/velscl*(-1.0)*math.cos(theta)*dist,y1+myData['fit']['v'][k]/velscl*(-1.0)*math.sin(theta)*dist
			
			lines.append(((x1,y1),(x2,y2)))
			#save the param to use as a color scale
			if(param == 'velocity'): intensities[0].append(myData['fit']['v'][k])
			elif(param == 'power'): intensities[0].append(myData['fit']['p_l'][k])
			elif(param == 'width'): intensities[0].append(myData['fit']['w_l'][k])
			elif(param == 'elevation' and myData[j]['prm']['xcf']): intensities[0].append(myData['fit']['elv'][k])
			elif(param == 'phi0' and myData[j]['prm']['xcf']): intensities[0].append(myData['fit']['phi0'][k])
			
			if(myData['fit']['p_l'][k] > 0): intensities[1].append(myData['fit']['p_l'][k])
			else: intensities[1].append(0.)

		if(gsct): gs_flg.append(myData['fit']['gflg'][k])

