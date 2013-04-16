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
MODULE: pydarn.plotting.pygridPlot
*******************************

This module contains the following functions:

  plotPygrid
  
  drawPygridVecs
  
  drawPygridMap

"""

import pydarn
import numpy
import utils
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from mpl_toolkits.basemap import Basemap
from pydarn.proc.pygridLib import *
from pydarn.sdio.pygridIo import *
from utils.timeUtils import *
import gme

def plotPygrid(sTime=None,eTime=None,plot='all',rads=None,hemi='north',interval=120,grid=0, \
                vmax=500,vwidth=.8,overlayPoes=False,poesparam='ted',poesMin=-3.,poesMax=0.5, \
                poesLabel=r"Total Log Energy Flux [ergs cm$^{-2}$ s$^{-1}$]",overlayBnd=False):

  """a function that plots the contents of a pygrid file
  
  **Args**:
    * **[dateStr]**: a string indicating the date to plot in yyyymmdd format, eg '20120710'.  If set to None, the map and grid (optional) is drawn. default = None
    * **[plot]**; the plot type.  This can be either 'all' to plot all LOS  velocities for each grid cell, 'avg' to plot the averaged LOS velocities in each grid cell, or 'mrg' to plot the merged 2D  velocities.  default = 'all'
    * **[rads]**: the radars to be plotted.  This input is only used when plot  is either 'all' or 'avg'.  This can be either a list of one or more  radars, eg ['bks','cvw',...], or a hemisphere 'north' or 'south' indicating to plot all the radars for a given hemisphere. default = None
    * **[hemi]**: the hemisphere for which to plot all radars.  This is only used when plot = 'mrg'.  This can be either 'north' or 'south'. default = 'north'
    * **[time]**: the range of times to be plotted in  MINIMIZED hhmm format, ie [23,456], NOT [0023,0456] default = [0,0].
    * **[interval]**: the time interval to be used between plots inminutes.  default = 2
    * **[grid]**: a flag to determine whether to plot the grid or not, 1 = yes, 0 = no.  Note that plotting the grid can make the output plot file very large.  default = 0
    * **[vmax]**: the maximum value for the color and vector length scale in m/s.  default = 500
    * **[vwidth]**: the width of the velocity vectors, default = .2
  **Returns**:
    * Nothing.
    
    
  **Examples**:
    ::

      plotPygrid(dateStr='20110409',plot='avg',rads=['bks'],time=[840,840],vmax=700)
      plotPygrid(dateStr='20110409',plot='all',rads='north',time=[840,840],vmax=760)
      plotPygrid(dateStr='20110409',plot='mrg',hemi='south',time=[840,840],vmax=200)
  
  Written by AJ 20120919

  """
  
  import os,math,datetime as dt,random
  from matplotlib.backends.backend_pdf import PdfPages
  
  ddir = os.environ.get('DATADIR')
  if ddir == None: ddir = os.getcwd()
  baseDir = ddir+'/pygrid'


  ddir = os.environ.get('PYPLOTS')
  if ddir == None: ddir = os.getcwd()
  d = ddir+'/pygrid'
  if not os.path.exists(d):
    os.makedirs(d)
    
  #check for a dateStr
  if(sTime != None):
    #check dateStr input
    if not isinstance(sTime,dt.datetime):
      print 'error with date input'
      return None
    if eTime == None:
      eTime = sTime
    else:
      if not isinstance(eTime,dt.datetime):
        print 'error, end time must be datetime object'
        return None
    

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
        fileName = locatePygridFile(dateToYyyymmdd(dt.datetime(sTime.year,sTime.month,sTime.day)),r)
        #check that the file exists
        if fileName == None: continue
        #append it to the list of filename to open
        fileNames.append(fileName)
    #check for 'mrg' plot
    else:
      #check for hemispher input
      assert(hemi == 'north' or hemi == 'south'),"hemi must equal 'north' or 'south'"
      #locate the file
      fileName = locatePygridFile(dateToYyyymmdd(dt.datetime(sTime.year,sTime.month,sTime.day)),hemi)
      #check if file exists
      if fileName == None: return
      #append the filename to the list of files to open
      fileNames.append(fileName)

    #open all of the files we need to
    for f in fileNames: 
      print 'opening: '+ f
      ff = openPygrid(f,'r')
      if ff != None:
        myFiles.append(ff)
    
    tlist=[]
    ctime = sTime
    #create a pygrid item
    myGrid = pygrid()

    while ctime <= eTime:
      print 'in loop'
      #remove the vectors
      myGrid.delVecs()
      #create a MPL figure
      print 'makefig'
      myFig = plt.figure()
      #draw a map
      'print drawmap'
      myMap = drawPygridMap(myFig,myGrid,grid=grid)

      print ctime
      print 'plotting'
      #read the files we have opened
      for f in myFiles:
        print ctime
        readPygridRec(f,myGrid,datetimeToEpoch(ctime),-1)
        
      t1=dt.datetime.now()
      #get the vectors
      print 'drawing'
      
      circs,lines,intensities = [[],[],[],[]],[],[]
      #iterate through the lat cells
      for l in myGrid.lats:
        #iterate through the lon cells
        for c in l.cells:
          #check for plot type
          if(plot == 'all'): ls = c.allVecs
          elif(plot == 'avg'): ls = c.avgVecs
          elif(plot == 'mrg'): ls = [c.mrgVec]
          if len(ls) > 0 and ls[0] != None :
            #convert start point to map cords
            for v in ls:
              x1,y1 = myMap(c.center[1]*360./24., c.center[0])
              circs[0].append(x1)
              circs[1].append(y1)
              for v in ls:
                ept = utils.geoPack.greatCircleMove(c.center[0],c.center[1]*360./24.,v.v/vmax*500e3,v.azm)
                x2,y2 = myMap(ept[1], ept[0])
                circs[2].append(x2)
                circs[3].append(y2)
                lines.append(((x1,y1),(x2,y2)))
                intensities.append(v.v)

      cm,norm,bnds = utils.plotUtils.genCmap('power',[0,vmax],colors='aj')
      ccoll = plt.scatter(circs[0],circs[1],c='k',s=.8,zorder=10,cmap=cm,norm=norm)
      lcoll = LineCollection(numpy.array(lines),linewidths=vwidth,zorder=11,cmap=cm,norm=norm)
      lcoll.set_array(numpy.array(intensities))
      myFig.gca().add_collection(lcoll)
      plt.title(ctime.strftime("%Y/%m/%d %H:%M")+'   Plot Type: %s vecs' % plot)

      pcols = gme.sat.poes.overlayPoesTed(myMap,myFig.gca(),ctime,coords='mag',param=poesparam, scMin=poesMin, scMax=poesMax)
      if(pcols != None):
        # cols.append(pcols)
        pTicks = numpy.linspace(poesMin,poesMax,8)#[-3.0,-2.5,-2.0,-1.5,-1.0,-0.5,0.0,0.5]
        cbar = plt.colorbar(pcols,ticks=pTicks,orientation='vertical',shrink=0.65,fraction=.1)
        cbar.ax.set_yticklabels(pTicks)
        cbar.set_label(poesLabel,size=10)
        cbar.ax.tick_params(axis='y',direction='out')
        #set colorbar ticklabel size
        for ti in cbar.ax.get_yticklabels():
          ti.set_fontsize(7)


      gme.sat.poes.overlayPoesBnd( myMap, myFig.gca(), ctime, coords = 'mag')

      cbar = plt.colorbar(lcoll,orientation='vertical',shrink=.65,fraction=.1)
      cbar.ax.tick_params(axis='y',direction='out')
      cbar.set_label('Velocity [m/s]',size=10)
      ll = []
      for b in bnds:
        ll.append(str(b)[:str(b).index('.')])
      ll[-1] = ''
      cbar.ax.set_yticklabels(ll)

      print 'show'
      myFig.show()

      # circs,lines,intensities = drawPygridVecs(myGrid,myMap,plot=plot,vmax=vmax)

      # #add the collection of vectors to the figure
      # ccoll = plt.scatter([50.],[60.],s=.5,c='k')
      # lcoll = LineCollection(numpy.array(lines),linewidths=vwidth,zorder=10)
      # lcoll.set_array(numpy.array(intensities))
      # myFig.gca().add_collection(lcoll)
      
      # #do the colormapping
      
      # cm,norm,bnds = utils.plotUtils.genCmap('power',[0,vmax],colors='aj')
      # utils.drawCB(myMap,lcoll,cm,norm=norm,map=1,pos=[.8,.3,.9,.9])
      

      # txt = plt.figtext(.5,.95,ctime.strftime("%Y/%m/%d  %H:%M:%S"),weight=550,size='large',ha='center')
      # t2 = dt.datetime.now()
      # # myFig.savefig(d+'/'+str(int(datetimeToEpoch(ctime)))+'.'+fbase+'.'+plot+'.svg', bbox_inches=0)
      # t3 = dt.datetime.now()
      # print 'drawing took', t2-t1
      # print 'saving took',t3-t2
      # ccoll.remove()
      # lcoll.remove()
      # myFig.texts.remove(txt)

      ctime += dt.timedelta(seconds=interval)

    #close all our open files and zip them
    for f in myFiles: closePygrid(f)
    # for f in fileNames:
    #   print 'zipping: '+f
    #   os.system('bzip2 '+f)
      
    
def drawPygridVecs(myGrid,myMap,plot='all',vmax=500):
  """
  *******************************
  
  PACKAGE: pydarn.plotting.pygrid
  
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
        print c.center[1]*360./24., c.center[0]
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
  
  PACKAGE: pydarn.plotting.pygrid
  
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
  import utils
  #create a basemap object
  myMap = utils.mapObj(boundinglat=50, lon_0=0.,coords='mag',gridLabels=True,grid=False)
  myMap.drawmeridians(numpy.arange(0,360,30))
  myMap.drawparallels([0,20,40,60,80])
  #myMap.boundinglat=0.

  #manually label the latitudes
  for i in [60,80]:
    x=myMap(2.,i+1)
    plt.text(x[0],x[1],str(i),fontweight='bold',fontsize=13.)
    
  #manuallt label MLT
  ha = ['center','left','center','right']
  va = ['top','center','bottom','center']
  for i in numpy.arange(0,360,90):
    x = myMap(i,48)
    plt.text(x[0],x[1],str(int(i/360.*24)),fontweight='bold',ha=ha[i/90],va=va[i/90])
    
  
  #if we want to draw the grid
  if(grid == 1):
    verts=[]
    for l in myGrid.lats:
      for c in l.cells:
        #convert the corners of the grid cell to map coords
        x1,y1 = myMap(c.bl[1],c.bl[0])
        x2,y2 = myMap(c.tl[1],c.tl[0])
        x3,y3 = myMap(c.tr[1],c.tr[0])
        x4,y4 = myMap(c.br[1],c.br[0])
        #append the cell coords to the list of vertices
        verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))
    #create a polygon collection using the vertices
    pcoll = PolyCollection(numpy.array(verts),edgecolors='k',facecolors='none',linewidths=.1,closed=False,zorder=5)
    #add the collection to the figure
    myFig.gca().add_collection(pcoll)
    
  #return the basemap object
  return myMap
  
  # def plotLoop(myFiles,fbase,tlist,grid,plot,vmax,vwidth,d):
#   import datetime as dt
#   #print args

#   #create a pygrid item
#   myGrid = pygrid()
#   #create a MPL figure
#   myFig = plt.figure()
#   print tlist
#   #draw a map
#   myMap = drawPygridMap(myFig,myGrid,grid=grid)
#   for ctime in tlist:
    
#     myGrid.delVecs()
#     print ctime
#     print 'plotting'
#     #read the files we have opened
#     for f in myFiles:
#       #print 'reading'
#       #read a record
#       print ctime
#       readPygridRec(f,myGrid,datetimeToEpoch(ctime),-1)
      
#     t1=dt.datetime.now()
#     #get the vectors
#     print 'drawing'
    
#     circs,lines,intensities = drawPygridVecs(myGrid,myMap,plot=plot,vmax=vmax)

#     #add the collection of vectors to the figure
#     ccoll = plt.scatter(circs[0],circs[1],s=.5,c='k')
#     lcoll = LineCollection(numpy.array(lines),linewidths=vwidth,zorder=10)
#     lcoll.set_array(numpy.array(intensities))
#     myFig.gca().add_collection(lcoll)
    
#     #do the colormapping
    
#     cm,norm,bnds = utils.plotUtils.genCmap('velocity',[0,vmax],colors='aj')
#     utils.drawCB(myMap,lcoll,cm,norm=norm,map=1,pos=[.8,.3,.9,.9])
    

#     txt = plt.figtext(.5,.95,ctime.strftime("%Y/%m/%d  %H:%M:%S"),weight=550,size='large',ha='center')
#     t2 = dt.datetime.now()
#     myFig.savefig(d+'/'+str(int(datetimeToEpoch(ctime)))+'.'+fbase+'.'+plot+'.svg', bbox_inches=0)
#     t3 = dt.datetime.now()
#     print 'drawing took', t2-t1
#     print 'saving took',t3-t2
#     ccoll.remove()
#     lcoll.remove()
#     myFig.texts.remove(txt)