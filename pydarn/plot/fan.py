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
.. module:: fan
   :synopsis: A module generating fan plots

.. moduleauthor:: AJ, 20130218

***************************
**Module**: pydarn.plot.fan
***************************
**Functions**:
  * :func:`plotFan`
  * :func:`overlayFan`
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
import matplotlib.cm as cm

def plotFan(sTime,rad,eTime=None,interval=60,fileType='fitex',param='velocity',filtered=False ,\
    scale=[],channel='a',coords='geo',colors='lasse',gsct=0,fov=1,edgeColors='face',gflg=0,fill=True,\
    velscl=1000.,legend=1,overlayPoes=False,poesparam='ted',poesMin=-3.,poesMax=0.5, \
    poesLabel=r"Total Log Energy Flux [ergs cm$^{-2}$ s$^{-1}$]",overlayBnd=False,output='gui'):
  """A function to make fan plots
  
  **Args**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the start time you want to plot
    * **rad** (str): a list of 3 letter radar codes
    * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): the last time you want to plot.  If this is None, it will be set equal to sTime.  default = None
    * **[interval]** (int): the interval between fan plots, in seconds
    * **[fileType]**: the file type to plot, valid inputs are 'fitex','fitacf',
      'lmfit'.  default = 'fitex'
    * **[param]**: the parameter to be plotted, valid inputs are 'velocity', 
      'power', 'width', 'elevation', 'phi0'.  default = 'velocity
    * **[filtered]**: a flag indicating whether the data should be boxcar filtered
      default = 0
    * **[scale]**: the min and max values of the color scale.  If this is set to []
      then default values will be used
    * **[channel]**: the channel for which to plot data.  default = 'a'
    * **[coords]**: the coordinate system to use, valid inputs are 'geo', 'mag'
      default = 'geo'
    * **[colors]**: the color map to use, valid inputs are 'lasse', 'aj'
      default = 'lasse'
    * **[gsct]**: a flag indicating whether to plot ground scatter as gray.
      default = 0
    * **[fov]**: a flag indicating whether to overplot the radar fields of view
      default = 0
    * **[edgeColors]**: edge colors of the polygons, default = 'face'
    * **[gflg]**: a flag indicating whether to plot low velocities in gray
      default = 0
    * **[fill]**: a flag indicating whether to plot filled or point RB cells
      default = True
    * **[velscl]**: the velocity to use as baseline for velocity vector length,
      only applicable if fill = 0.  default = 1000
    * **[legend]**: a flag indicating whether to plot the legend
      only applicable if fill = 0.  default = 1
  **Returns**:
    NONE

  **Example**:
    ::
    
      plotFan('20121001',['bks','fhw'],time=[0,24],interval=2,fileType='fitex',param='velocity',filtered=0 ,
                scale=[-400,400],channel='a',coords='geo',colors='lasse',gsct=0,pdf=0,fov=1,edgeColors='face',gflg=0)

  Written by AJ 20121004

  """

  
  import datetime as dt, gme, pickle
  from matplotlib.backends.backend_pdf import PdfPages
  import models.aacgm as aacgm, os, copy
  tt = dt.datetime.now()
  
  #check the inputs
  assert(isinstance(sTime,dt.datetime)),'error, sTime must be a datetime object'
  if(eTime == None): eTime = sTime
  assert(isinstance(eTime,dt.datetime)),'error, eTime must be a datetime object'
  assert(eTime >= sTime), 'error, eTime < sTime'
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
    
  fbase = d+'/'+sTime.strftime("%Y%m%d")+'.fan.'
    
  cmap,norm,bounds = utils.plotUtils.genCmap(param,scale,colors=colors,gflg=gflg)
  
  
  #open the data files
  myFiles = []
  for r in rad:
    f = radDataOpen(sTime,r,eTime+datetime.timedelta(seconds=interval),fileType=fileType,filtered=filtered,channel=channel)
    if(f != None): myFiles.append(f)

  assert(myFiles != []),'error, no data available for this period'

  xmin,ymin,xmax,ymax = 1e16,1e16,-1e16,-1e16

  allBeams = [''] * len(myFiles)
  sites,fovs,oldCpids,lonFull,latFull=[],[],[],[],[]
  #go through all open files
  for i in range(len(myFiles)):
    #read until we reach start time
    allBeams[i] = radDataReadRec(myFiles[i])
    while(allBeams[i].time < sTime and allBeams[i] != None):
      allBeams[i] = radDataReadRec(myFiles[i])
      
    #check that the file has data in the target interval
    if(allBeams[i] == None): 
      myFiles[i].close()
      myFiles[i] = None
      continue
  
    #get to field of view coords in order to determine map limits
    t=allBeams[i].time
    site = pydarn.radar.site(radId=allBeams[i].stid,dt=t)
    sites.append(site)
    if(coords == 'geo'):
      latFull.append(site.geolat)
      lonFull.append(site.geolon)
    elif(coords == 'mag'):
      x = aacgm.aacgmConv(site.geolat,site.geolon,0.,0)
      latFull.append(x[0])
      lonFull.append(x[1])
    myFov = pydarn.radar.radFov.fov(site=site,rsep=allBeams[i].prm.rsep,\
            ngates=allBeams[i].prm.nrang+1,nbeams=site.maxbeam,coords=coords)
    fovs.append(myFov)
    for b in range(0,site.maxbeam+1):
      for k in range(0,allBeams[i].prm.nrang+1):
        lonFull.append(myFov.lonFull[b][k])
        latFull.append(myFov.latFull[b][k])
    oldCpids.append(allBeams[i].cp)
      
  #do some stuff in map projection coords to get necessary width and height of map
  #lon_0 = (xmin+xmax)/2.
  #lat_0 = (ymin+ymax)/2.
  t1=dt.datetime.now()
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
    ty = dt.datetime.now()
    for r in rad:
      pydarn.plot.overlayRadar(myMap, codes=r, dateTime=sTime, coords=coords)
      pydarn.plot.overlayFov(myMap, codes=r, dateTime=sTime,coords=coords)
    print 'overlays',dt.datetime.now()-ty
  
  print dt.datetime.now()-t1
  #manually draw the legend
  if((not fill) and legend):
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
        
  pickle.dump(myFig,open('map.pickle','wb'),-1)
  
  bbox = myFig.gca().get_axes().get_position()
  first = True
  pnum,stot = 0,dt.timedelta(seconds=0)
  axes = AxesSequence()
  #now, loop through desired time interval
  while(cTime <= eTime):
    tz = dt.datetime.now()
    cols = []
    bndTime = cTime + datetime.timedelta(seconds=interval)
    
    ft = 'None'
    #go though all files
    for i in range(len(myFiles)):
      scans = [[] for j in range(len(myFiles))]
      #check that we have good data at this time
      if(myFiles[i] == None or allBeams[i] == None): continue
      ft = allBeams[i].fType
      #until we reach the end of the time window
      while(allBeams[i] != None and allBeams[i].time < bndTime):
        scans[i].append(allBeams[i])
        #read the next record
        allBeams[i] = radDataReadRec(myFiles[i])
      intensities, pcoll = overlayFan(scans[i],myMap,myFig,param,coords,gsct=gsct,site=sites[i],fov=fovs[i],\
                                        fill=fill,velscl=velscl,dist=dist,cmap=cmap,norm=norm)
                                        
                                        
    
    if(first):
      cbar = plot.colorbar(pcoll,orientation='vertical',shrink=.65,fraction=.1)
    
      l = []
      #define the colorbar labels
      for i in range(0,len(bounds)):
        if(param == 'phi0'):
          ln = 4
          if(bounds[i] == 0): ln = 3
          elif(bounds[i] < 0): ln = 5
          l.append(str(bounds[i])[:ln])
          continue
        if((i == 0 and param == 'velocity') or i == len(bounds)-1):
          l.append(' ')
          continue
        l.append(str(int(bounds[i])))
      cbar.ax.set_yticklabels(l)
      cbar.ax.tick_params(axis='y',direction='out')
      #set colorbar ticklabel size
      for ti in cbar.ax.get_yticklabels():
        ti.set_fontsize(7)
      if(param == 'velocity'): 
        cbar.set_label('Velocity [m/s]',size=10)
        cbar.extend='max'
        
      if(param == 'grid'): cbar.set_label('Velocity [m/s]',size=10)
      if(param == 'power'): cbar.set_label('Power [dB]',size=10)
      if(param == 'width'): cbar.set_label('Spec Wid [m/s]',size=10)
      if(param == 'elevation'): cbar.set_label('Elev [deg]',size=10)
      if(param == 'phi0'): cbar.set_label('Phi0 [rad]',size=10)
    
    #myFig.gca().set_rasterized(True)
    #label the plot
    tx1 = plot.figtext((bbox.x0+bbox.x1)/2.,bbox.y1+.02,cTime.strftime('%Y/%m/%d'),ha='center',size=14,weight=550)
    tx2 = plot.figtext(bbox.x1,bbox.y1+.02,cTime.strftime('%H:%M - ')+\
          bndTime.strftime('%H:%M      '),ha='right',size=13,weight=550)
    tx3 = plot.figtext(bbox.x0,bbox.y1+.02,'['+ft+']',ha='left',size=13,weight=550)
    
    if(overlayPoes):
      pcols = gme.poes.overlayPoesTed(myMap, myFig.gca(), cTime, param=poesparam, scMin=poesMin, scMax=poesMax)
      if(pcols != None and first):
        cols.append(pcols)
        pTicks = numpy.linspace(poesMin,poesMax,8)#[-3.0,-2.5,-2.0,-1.5,-1.0,-0.5,0.0,0.5]
        cbar = plot.colorbar(pcols,ticks=pTicks,orientation='vertical',shrink=0.65,fraction=.1)
        cbar.ax.set_yticklabels(pTicks)
        cbar.set_label(poesLabel,size=10)
        cbar.ax.tick_params(axis='y',direction='out')
        #set colorbar ticklabel size
        for ti in cbar.ax.get_yticklabels():
          ti.set_fontsize(7)
        
    if(overlayBnd):
      gme.poes.overlayPoesBnd(myMap, myFig.gca(), cTime)

    t1 = dt.datetime.now()
    #myFig.savefig(pp, format='pdf', dpi=300,orientation='landscape')
    if(output == 'gui'): axes.axes.append(myFig.gca())
    else: myFig.savefig(fbase+str(pnum)+'.svg', orientation='landscape')
    tsave=dt.datetime.now()-t1
    print 'save',tsave
    stot+=tsave
    #myFig.show()
    
    #try:
      ##if(fill == 1): 
        ##pcoll.remove()
      ##else: 
        ##ccoll.set_paths([])
        ##lcoll.remove()
      #for c in cols:
        #c.remove()
        #del c
      
      ##if(gsct == 1): x.remove()
    #except: pass
    
    #myFig.texts.remove(tx1)
    #myFig.texts.remove(tx2)
    #myFig.texts.remove(tx3)

    cTime = bndTime
    first = False
    pnum += 1
    myFig.clf()
    myFig = pickle.load(open('map.pickle','rb'))
    print 'plot loop',dt.datetime.now()-tz
    
  
  if(output != 'gui'): print 'file[s] is[are] at: '+d+'/'+sTime.strftime("%Y%m%d")+'.fan.%n.pdf'
  else: axes.show()
  print dt.datetime.now()-tt
  print stot/pnum

class AxesSequence(object):
  """Creates a series of axes in a figure where only one is displayed at any
  given time. Which plot is displayed is controlled by the arrow keys."""
  def __init__(self):
    self.fig=plot.figure()
    self.axes = []
    self._i = 0 # Currently displayed axes index
    self._n = 0 # Last created axes index
    self.fig.canvas.mpl_connect('key_press_event', self.on_keypress)

  def __iter__(self):
    while True:
      yield self.new()

  def new(self):
    # The label needs to be specified so that a new axes will be created
    # instead of "add_axes" just returning the original one.
    ax = self.fig.add_axes([0.15, 0.1, 0.8, 0.8], 
                            visible=False, label=self._n)
    self._n += 1
    self.axes.append(ax)
    return ax

  def on_keypress(self, event):
    if event.key == 'right':
      self.next_plot()
    elif event.key == 'left':
      self.prev_plot()
    else:
      return
    self.fig.canvas.draw()

  def next_plot(self):
    if self._i < len(self.axes):
      self.axes[self._i].set_visible(False)
      self.axes[self._i+1].set_visible(True)
      self._i += 1

  def prev_plot(self):
    if self._i > 0:
      self.axes[self._i].set_visible(False)
      self.axes[self._i-1].set_visible(True)
      self._i -= 1

  def show(self):
    self.axes[0].set_visible(True)
    plot.show()
        
def overlayFan(myData,myMap,myFig,param,coords='geo',gsct=0,site=None,\
                fov=None,gs_flg=[],fill=True,velscl=1000.,dist=1000.,
                cmap=None,norm=None):
  """A function of overlay radar scan data on a map

  **Args**:
    * **myData (:class:`radDataTypes.scanData` or :class:`radDataTypes.beamData` or list)**: a radar beam object, a radar scanData object, or simply a list of radar beams
    * **myMap**: the map we are plotting on
    * **[param]**: the parameter we are plotting
    * **[coords]**: the coordinates we are plotting in
    * **[param]**: the parameter to be plotted, valid inputs are 'velocity', 
      'power', 'width', 'elevation', 'phi0'.  default = 'velocity
    * **[gsct]**: a flag indicating whether we are distinguishing groudn  scatter
      default = 0
    * **[intensities]**: a list of intensities (used for colorbar)
    * **[fov]**: a radar fov object
    * **[gs_flg]**: a list of gs flags, 1 per range gate
    * **[fill]**: a flag indicating whether to plot filled or point RB cells
      default = True
    * **[velscl]**: the velocity to use as baseline for velocity vector length,
      only applicable if fill = 0.  default = 1000
    * **[lines]**: an array to have the endpoints of velocity vectors
      only applicable if fill = 0.  default = []
    * **[dist]**: the length in map projection coords of a velscl length
      velocity vector.  default = 1000. km
  **OUTPUTS**:
    NONE

  **EXAMPLE**:
    overlayFan(aBeam,myMap,param,coords,gsct=gsct,site=sites[i],fov=fovs[i],\
                            verts=verts,intensities=intensities,gs_flg=gs_flg)

  Written by AJ 20121004
  """
  
  if(site == None):
    site = pydarn.radar.network().getRadarById(myData[0].stid).getSiteByDate(myData[0].time)
  if(fov == None):
    fov = pydarn.radar.radFov.fov(site=site,rsep=myData[0].prm.rsep,\
    ngates=myData.prm.nrang+1,nbeams= site.maxbeam,coords=coords) 
  
  verts = []
  
  if(isinstance(myData,pydarn.sdio.beamData)): myData = [myData]
  
  gs_flg,lines = [],[]
  if(fill == 1): verts,intensities = [],[]
  else: verts,intensities = [[],[]],[[],[]]
  
  #loop through gates with scatter
  for myBeam in myData:
    for k in range(0,len(myBeam.fit.slist)):
      r = myBeam.fit.slist[k]

      if(fill):
        x1,y1 = myMap(fov.lonFull[myBeam.bmnum,r],fov.latFull[myBeam.bmnum,r])
        x2,y2 = myMap(fov.lonFull[myBeam.bmnum,r+1],fov.latFull[myBeam.bmnum,r+1])
        x3,y3 = myMap(fov.lonFull[myBeam.bmnum+1,r+1],fov.latFull[myBeam.bmnum+1,r+1])
        x4,y4 = myMap(fov.lonFull[myBeam.bmnum+1,r],fov.latFull[myBeam.bmnum+1,r])

        #save the polygon vertices
        verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))
        
        #save the param to use as a color scale
        if(param == 'velocity'): intensities.append(myBeam.fit.v[k])
        elif(param == 'power'): intensities.append(myBeam.fit.p_l[k])
        elif(param == 'width'): intensities.append(myBeam.fit.w_l[k])
        elif(param == 'elevation' and myBeam.prm.xcf): intensities.append(myBeam.fit.elv[k])
        elif(param == 'phi0' and myBeam.prm.xcf): intensities.append(myBeam.fit.phi0[k])
        
      else:
        x1,y1 = myMap(fov.lonCenter[myBeam.bmnum,r],fov.latCenter[myBeam.bmnum,r])
        verts[0].append(x1)
        verts[1].append(y1)
        
        x2,y2 = myMap(fov.lonCenter[myBeam.bmnum,r+1],fov.latCenter[myBeam.bmnum,r+1])
        
        theta = math.atan2(y2-y1,x2-x1)
        
        x2,y2 = x1+myBeam.fit.v[k]/velscl*(-1.0)*math.cos(theta)*dist,y1+myBeam.fit.v[k]/velscl*(-1.0)*math.sin(theta)*dist
        
        lines.append(((x1,y1),(x2,y2)))
        #save the param to use as a color scale
        if(param == 'velocity'): intensities[0].append(myBeam.fit.v[k])
        elif(param == 'power'): intensities[0].append(myBeam.fit.p_l[k])
        elif(param == 'width'): intensities[0].append(myBeam.fit.w_l[k])
        elif(param == 'elevation' and myBeam.prm.xcf): intensities[0].append(myBeam.fit.elv[k])
        elif(param == 'phi0' and myBeam.prm.xcf): intensities[0].append(myBeam.fit.phi0[k])
        
        if(myBeam.fit.p_l[k] > 0): intensities[1].append(myBeam.fit.p_l[k])
        else: intensities[1].append(0.)
      if(gsct): gs_flg.append(myBeam.fit.gflg[k])
      
  #do the actual overlay
  if(fill):
    #if we have data
    if(verts != []):
      if(gsct == 0):
        inx = numpy.arange(len(verts))
      else:
        inx = numpy.where(numpy.array(gs_flg)==0)
        x = PolyCollection(numpy.array(verts)[numpy.where(numpy.array(gs_flg)==1)],facecolors='.3',linewidths=0,alpha=.5,zorder=5)
        myFig.gca().add_collection(x, autolim=True)
        
      pcoll = PolyCollection(numpy.array(verts)[inx],edgecolors='face',linewidths=0,closed=False,zorder=4,cmap=cmap,norm=norm)
      #set color array to intensities
      pcoll.set_array(numpy.array(intensities)[inx])
      myFig.gca().add_collection(pcoll, autolim=True)
      return intensities,pcoll
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