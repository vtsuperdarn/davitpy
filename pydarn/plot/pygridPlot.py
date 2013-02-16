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

"""
*******************************
MODULE: pydarn.plot.pygridPlot
*******************************

This module contains the following functions:

	plotPygrid
	
	drawPygridVecs
	
	drawPygridMap

"""

import pydarn,numpy,utils
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from mpl_toolkits.basemap import Basemap
from pydarn.proc.pygridLib import *
from pydarn.sdio.pygridIo import *
from utils.timeUtils import *

def plotPygrid(dateStr=None,plot='all',rads=None,hemi='north',time=[0,0],interval=2,grid=0,vmax=500,vwidth=.2):
	"""

	PACKAGE: pydarn.plot.pygrid
	
	FUNCTION: plotPygrid(dateStr=None,plot='all',rads=None,hemi='north',time=0,interval=2,grid=0,vmax=500,vwidth=.2)
	
	PURPOSE: a function that plots the contents of a pygrid file
	
	INPUTS:
		[dateStr]: a string indicating the date to plot in 
			yyyymmdd format, eg '20120710'.  If set to None,
			the map and grid (optional) is drawn.
			default = None
		[plot]; the plot type.  This can be either 'all' to plot all
			LOS	 velocities for each grid cell, 'avg' to plot the averaged LOS
			velocities in each grid cell, or 'mrg' to plot the merged 2D 
			velocities.  default = 'all'
		[rads]: the radars to be plotted.  This input is only used when plot 
			is either 'all' or 'avg'.  This can be either a list of one or more 
			radars, eg ['bks','cvw',...], or a hemisphere 'north' or 'south'
			indicating to plot all the radars for a given hemisphere.
			default = None
		[hemi]: the hemisphere for which to plot all radars.  This is only
			used when plot = 'mrg'.  This can be either 'north' or 'south'.
			default = 'north'
		[time]: the range of times to be plotted in 
			MINIMIZED hhmm format, ie [23,456], NOT [0023,0456]
			default = [0,0].
		[interval]: the time interval to be used between plots in
			minutes.  default = 2
		[grid]: a flag to determine whether to plot the grid or not,
			1 = yes, 0 = no.  Note that plotting the grid can make the
			output plot file very large.  default = 0
		[vmax]: the maximum value for the color and vector length
			scale in m/s.  default = 500
		[vwidth]: the width of the velocity vectors, default = .2
		
		OUTPUTS:
			None
			
			
		EXAMPLES:
			plotPygrid(dateStr='20110409',plot='avg',rads=['bks'],time=[840,840],vmax=700)
			
			plotPygrid(dateStr='20110409',plot='all',rads='north',time=[840,840],vmax=760)
			
			plotPygrid(dateStr='20110409',plot='mrg',hemi='south',time=[840,840],vmax=200)
	
	Written by AJ 20120919

	"""
	
	import os,math,datetime as dt,random
	from matplotlib.backends.backend_pdf import PdfPages
	import multiprocessing as mp
	
	
	d = os.environ['PYPLOTS']+'/pygrid'
	if not os.path.exists(d):
		os.makedirs(d)
	fnamebase = str(int((random.random()*1e9)))
	nt = mp.cpu_count()
		
	#check for a dateStr
	if(dateStr != None):
		#check dateStr input
		assert(isinstance(dateStr,str) and len(dateStr) == 8),'error with date input'
		

		#convert date string, start time, end time to datetime
		myDate = yyyymmddToDate(dateStr)
		hr1,hr2 = int(math.floor(time[0]/100.)),int(math.floor(time[1]/100.))
		min1,min2 = int(time[0]-hr1*100),int(time[1]-hr2*100)
		stime = myDate.replace(hour=hr1,minute=min1)
		if(hr2 == 24):
			stime = myDate+datetime.timedelta(days=1)
		else:
			etime = myDate.replace(hour=hr2,minute=min2)
		
		myFiles,fileNames = [],[]
		#check for plot type to be either 'avg' or 'all'
		if(plot != 'mrg'):
			#check for valid rads input
			assert(rads != None),"must input rads if dateStr is given and plot is not 'mrg'"
			if(rads == 'north' or rads == 'south'):
				rads = pydarn.radar.network().getAllCodes(hemi=hemi)
			else: 
				assert(isinstance(rads,list)),\
				"must input a LIST of radars or a hemisphere name if dateStr is given and plot is not 'mrg'"
				for r in rads:
					assert(isinstance(r,str) and (len(r) == 3)),'error, each radar code must be a 3 letter string'
			
			#iterate through radar codes
			for r in rads:
				#find the file
				fileName = locatePygridFile(dateStr,r)
				#check that the file exists
				if(fileName == None): continue
				#append it to the list of filename to open
				fileNames.append(fileName)
		#check for 'mrg' plot
		else:
			#check for hemispher input
			assert(hemi == 'north' or hemi == 'south'),"hemi must equal 'north' or 'south'"
			#locate the file
			fileName = locatePygridFile(dateStr,hemi)
			#check if file exists
			if(fileName == None): return
			#append the filename to the list of files to open
			fileNames.append(fileName)

		#open all of the files we need to
		for f in fileNames: 
			print 'opening: '+f
			myFiles.append(openPygrid(f,'r'))
		
		tlist=[]
		ctime = stime
		while ctime <= etime:
			tlist.append(ctime)
			ctime += dt.timedelta(minutes=interval)
		div = len(tlist)/nt
		args = []
		jobs = []
		for i in range(nt-1):
			p = mp.Process(target=plotLoop, args=(myFiles,fnamebase,tlist[i*div:(i+1)*div],grid,plot,vmax,vwidth,d,dateStr))
			jobs.append(p)
			p.start()
		p = mp.Process(target=plotLoop, args=(myFiles,fnamebase,tlist[(nt-1)*div:],grid,plot,vmax,vwidth,d,dateStr))
		jobs.append(p)
		p.start()
		
		for j in jobs:
			j.join()
			del j
		
		#args = zip([myFiles]*nt,[fnamebase]*nt,tsplit,[grid]*nt)
		#print args
		
		#pool = mp.Pool(processes=nt)
		#pool.map(plotLoop, args)
		
		#close all our open files and zip them
		for f in myFiles: closePygrid(f)
		for f in fileNames:
			print 'zipping: '+f
			os.system('bzip2 '+f)
			
	
def plotLoop(myFiles,fbase,tlist,grid,plot,vmax,vwidth,d,dateStr):
	import datetime as dt
	#print args
	#myFiles,fbase,tlist,grid = args
	#create a pygrid item
	myGrid = pygrid()
	#create a MPL figure
	myFig = plt.figure()
	print tlist
	#draw a map
	myMap = drawPygridMap(myFig,myGrid,grid=grid)
	for ctime in tlist:
		
		myGrid.delVecs()
		print ctime
		print 'plotting'
		#read the files we have opened
		for f in myFiles:
			#print 'reading'
			#read a record
			print ctime
			readPygridRec(f,myGrid,datetimeToEpoch(ctime),-1)
			
		t1=dt.datetime.now()
		#get the vectors
		print 'drawing'
		
		circs,lines,intensities = drawPygridVecs(myGrid,myMap,plot=plot,vmax=vmax)

		#add the collection of vectors to the figure
		ccoll = plt.scatter(circs[0],circs[1],s=.5,c='k')
		lcoll = LineCollection(numpy.array(lines),linewidths=vwidth,zorder=10)
		lcoll.set_array(numpy.array(intensities))
		myFig.gca().add_collection(lcoll)
		
		#do the colormapping
		pydarn.plot.plotUtils.genCmap(myMap,lcoll,'grid',[0,vmax],colors='aj',map=1)
		
		txt = plt.figtext(.5,.95,ctime.strftime("%Y/%m/%d  %H:%M:%S"),weight=550,size='large',ha='center')
		t2 = dt.datetime.now()
		myFig.savefig(d+'/'+str(int(datetimeToEpoch(ctime)))+'.'+fbase+'.'+plot+'.svg', bbox_inches=0)
		t3 = dt.datetime.now()
		print 'drawing took', t2-t1
		print 'saving took',t3-t2
		ccoll.remove()
		lcoll.remove()
		myFig.texts.remove(txt)
		
def drawPygridVecs(myGrid,myMap,plot='all',vmax=500):
	"""
	*******************************
	
	PACKAGE: pydarn.plot.pygrid
	
	FUNCTION: drawPygridVecs(myGrid,myMap,lines,intensities,plot='all',vmax=500)
	
	a function that assigns the information for the gridded velocity vectors
	
	INPUTS:
	
		myGrid: the pygrid data being plotted
		myMap: the map object to draw onto
		lines: the line array to be filled
		intensities: the color scale array to be filled
		[plot]: the plot type, one of 'all','avg','mrg'. default = 'all'
		[vmax]: the max value for the color and velocity vector scale.
			default: 500
			
	OUTPUTS: 
		[lines,intensities]: a list of the lines and intensities lists
		
	EXAMPLE:
		drawPygridVecs(myGrid,myMap,lList,iList,plot='mrg',vmax=360)
	
	Written by AJ 20120919

	*******************************
	"""
	circs,lines,intensities = [[],[]],[],[]
	#iterate through the lat cells
	for l in myGrid.lats:
		#iterate through the lon cells
		for c in l.cells:
			#check for plot type
			if(plot == 'all'): ls = c.allVecs
			elif(plot == 'avg'): ls = c.avgVecs
			elif(plot == 'mrg'): ls = [c.mrgVec]
			if(len(ls) > 0 and ls[0] != None):
				#convert start point to map cords
				x1,y1 = myMap(c.center[1]*360./24., c.center[0])
				circs[0].append(x1)
				circs[1].append(y1)
			#iterate through the vectors in the cell
			for v in ls:
				#check if the vector has a value
				if(v == None): continue
				#get the end pouint of the vector
				ept = utils.geoPack.greatCircleMove(c.center[0],c.center[1]*360./24.,v.v/vmax*400e3,v.azm)
				#convert end point to map coords
				x2,y2 = myMap(ept[1],ept[0])
				#append the vector line to the lines list
				lines.append(((x1,y1),(x2,y2)))
				#append the velocity to the intensities list
				intensities.append(v.v)
				
	return circs,lines,intensities

def drawPygridMap(myFig,myGrid,grid=0):
	"""
	*******************************
	
	PACKAGE: pydarn.plot.pygrid
	
	FUNCTION: drawPygridMap(myFig,myGrid,grid=0)
	
	a function that draws the pygrid map
	
	INPUTS:
		myFig: the MPL figure we are plotting on
		myGrid: a pygrid object
		[grid]: a flag indicating whether to draw the grid or not, 1 = yes,
		0 = no.  default = 0
		
	OUTPUTS: 
		myMap: a Basemap object
		
	EXAMPLE:
		drawPygridMap(myF,myG,grid=1)
	
	Written by AJ 20120919
	
	*******************************
	"""
	
	#create a basemap object
	myMap = pydarn.plot.map(boundingLat=40, lon_0=0.,grid=False,fillContinents='none',fillLakes='none')
	myMap.drawmeridians(numpy.arange(0,360,30))
	myMap.drawparallels([0,20,40,60,80])
	#myMap.boundinglat=0.

	#manually label the latitudes
	for i in [40,60,80]:
		x=myMap(2.,i+1)
		plt.text(x[0],x[1],str(i),fontweight='bold',fontsize=13.)
		
	#manuallt label MLT
	ha = ['center','left','center','right']
	va = ['top','center','bottom','center']
	for i in numpy.arange(0,360,90):
		x=myMap(i,39)
		plt.text(x[0],x[1],str(int(i/360.*24)),fontweight='bold',ha=ha[i/90],va=va[i/90])
		
	
	#if we want to draw the grid
	if(grid == 1):
		verts=[]
		for l in myGrid.lats:
			for c in l.cells:
				#convert the corners of the grid cell to map coords
				x1,y1 = myMap(c.bl[1]*360./24.,c.bl[0])
				x2,y2 = myMap(c.tl[1]*360./24.,c.tl[0])
				x3,y3 = myMap(c.tr[1]*360./24.,c.tr[0])
				x4,y4 = myMap(c.br[1]*360./24.,c.br[0])
				#append the cell coords to the list of vertices
				verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))
		#create a polygon collection using the vertices
		pcoll = PolyCollection(numpy.array(verts),edgecolors='k',facecolors='none',linewidths=.1,closed=False,zorder=5)
		#add the collection to the figure
		myFig.gca().add_collection(pcoll)
		
	#return the basemap object
	return myMap
	