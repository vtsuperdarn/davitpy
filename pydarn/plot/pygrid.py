import pydarn,numpy,utils
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from mpl_toolkits.basemap import Basemap
from pydarn.proc.pygridLib import *
from pydarn.io.pygridIo import *
from utils.timeUtils import *

def plotPygrid(dateStr=None,rads=None,hemi='north',time=0,grid=0,vmax=500,plot='all'):
	"""
	*******************************
	PACKAGE: pydarn.plot.pygrid
	FUNCTION: plotPygrid
	
	a function that plots the contents of a pygrid file
	
	INPUTS:
		dateStr: a string indicating the date to plot in 
			yyyymmdd format, eg '20120710'.  If set to None,
			the map and grid (optional) is drawn.
			default = None
		rads: the radars to be plotted.  This can either be a list of 
	
	
	Written by AJ 20120919
	*******************************
	"""
	import math,os
	
	myGrid = pygrid()
	myFig = plt.figure()

	if(dateStr != None):
		assert(isinstance(dateStr,str) and len(dateStr) == 8),'error with date input'
		
		myMap = drawPygridMap(myFig,myGrid,grid=grid)
		
		#convert date string, time to datetime
		myDate = yyyymmddToDate(dateStr)
		hr = int(math.floor(time/100.))
		min = int(time-hr*100)
		stime = myDate.replace(hour=hr,minute=min)
		
		myFiles,fileNames = [],[]
		if(plot != 'mrg'):
			assert(rads != None and isinstance(rads,list)),"must input a LIST of radars if dateStr is given and plot is not 'mrg'"
			for r in rads:
				assert(isinstance(r,str) and len(r) == 3),'error, each radar code must be a 3 letter string'
				
				fileName = locatePygridFile(dateStr,r)
				if(fileName == None): continue
				print 'opening: '+fileName
				fileNames.append(fileName)
			
		else:
			assert(hemi == 'north' or hemi == 'south'),"hemi must equal 'north' or 'south'"
			
			fileName = locatePygridFile(dateStr,hemi)
			if(fileName == None): return
			print 'opening: '+fileName
			fileNames.append(fileName)

		for f in fileNames: myFiles.append(openPygrid(f,'r'))
	
		for f in myFiles:
			readPygridRec(f,myGrid,datetimeToEpoch(stime),-1)
			lines,intensities = [],[]
			li = drawPygridVecs(myGrid,myMap,lines,intensities,plot=plot,vmax=vmax)
			lines,intensities = li[0],li[1]

		lcoll = LineCollection(numpy.array(lines),linewidths=.2,zorder=10)
		lcoll.set_array(numpy.array(intensities))
		myFig.gca().add_collection(lcoll)
		
		pydarn.plot.plotUtils.genCmap(myMap,lcoll,'grid',[0,vmax],colors='aj',map=1)
		
		for f in myFiles: closePygrid(f)
		for f in fileNames:
			print 'zipping: '+f
			os.system('bzip2 '+f)
	
	myFig.show()

def drawPygridVecs(myGrid,myMap,lines,intensities,plot='all',vmax=500):

	for l in myGrid.lats:
		for c in l.cells:
			if(plot == 'all'): ls = c.allVecs
			elif(plot == 'avg'): ls = c.avgVecs
			elif(plot == 'mrg'): ls = [c.mrgVec]
			for v in ls:
				if(v == None): continue
				ept = utils.geoPack.greatCircleMove(c.center[0],c.center[1]*360./24.,v.v/vmax*400e3,v.azm)
				x1,y1 = myMap(c.center[1]*360./24., c.center[0])
				x2,y2 = myMap(ept[1],ept[0])
				lines.append(((x1,y1),(x2,y2)))
				intensities.append(v.v)
				plt.plot(x1,y1,'ko',ms=1)
				
	return [lines,intensities]

def drawPygridMap(myFig,myGrid,grid=0):
	
	myMap = pydarn.plot.map(boundingLat=40, lon_0=0.,grid=False,fillContinents='none',fillLakes='none')	
	myMap.drawmeridians(numpy.arange(0,360,30))
	myMap.drawparallels([0,20,40,60,80])
	myMap.boundinglat=0.

	
	for i in [20,40,60,80]:
		x=myMap(2.,i+1)
		plt.text(x[0],x[1],str(i),fontweight='bold',fontsize=13.)
		
	ha = ['center','left','center','right']
	va = ['top','center','bottom','center']
	
	for i in numpy.arange(0,360,90):
		x=myMap(i,39)
		plt.text(x[0],x[1],str(int(i/360.*24)),fontweight='bold',ha=ha[i/90],va=va[i/90])
		
	verts=[]
	if(grid == 1):
		for i in range(0,myGrid.nLats):
			for j in range(0,myGrid.lats[i].nCells):
				x1,y1 = myMap(myGrid.lats[i].cells[j].bl[1]*360./24.,myGrid.lats[i].cells[j].bl[0])
				x2,y2 = myMap(myGrid.lats[i].cells[j].tl[1]*360./24.,myGrid.lats[i].cells[j].tl[0])
				x3,y3 = myMap(myGrid.lats[i].cells[j].tr[1]*360./24.,myGrid.lats[i].cells[j].tr[0])
				x4,y4 = myMap(myGrid.lats[i].cells[j].br[1]*360./24.,myGrid.lats[i].cells[j].br[0])
				x,y = myMap(myGrid.lats[i].cells[j].center[1]*360./24.,myGrid.lats[i].cells[j].center[0])
				verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))
		pcoll = PolyCollection(numpy.array(verts),edgecolors='k',facecolors='none',linewidths=.1,closed=False,zorder=5)
		myFig.gca().add_collection(pcoll)
		
	return myMap
	