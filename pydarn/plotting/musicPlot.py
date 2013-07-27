# Copyright (C) 2013  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: pydarn.plotting 
*********************

This module contains the following functions:
    * :func:`utils.geoPack.geodToGeoc`: 
        converts from geodetic to geocentric (and vice-versa)
"""

import numpy as np
import datetime

from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon
from matplotlib import dates as md
import matplotlib

from mpl_toolkits.basemap import Basemap

import utils
from pydarn.radar.radUtils import getParamDict

class musicFan(object):
  def __init__(self,dataObject,dataSet='active',time=None,axis=None,fileName=None,scale=None, plotZeros=False, markCell=None, **kwArgs):
    if fileName != None:
      from matplotlib.backends.backend_agg import FigureCanvasAgg
      from matplotlib.figure import Figure
      if axis==None:
        fig   = Figure()
    else:
      from matplotlib import pyplot as plt
      plt.ion()
      if axis==None:
        fig   = plt.figure()

    #Make some variables easier to get to...
    currentData = getattr(dataObject,dataSet)
    metadata    = currentData.metadata
    latFull     = currentData.fov.latFull
    lonFull     = currentData.fov.lonFull

    coords      = metadata['coords']

    #Translate parameter information from short to long form.
    paramDict = getParamDict(metadata['param'])
    if paramDict.has_key('label'):
      param     = paramDict['param']
      cbarLabel = paramDict['label']
    else:
      param = 'width' #Set param = 'width' at this point just to not screw up the colorbar function.
      cbarLabel = metadata['param']

    #Set colorbar scale if not explicitly defined.
    if(scale == None):
      if paramDict.has_key('range'):
        scale = paramDict['range']
      else:
        scale = [-200,200]

    #See if an axis is provided... if not, set one up!
    if axis==None:
      axis  = fig.add_subplot(111)
    else:
      fig   = axis.get_figure()

    #Figure out which scan we are going to plot...
    if time == None:
      timeInx = 0
    else:
      timeInx = (np.where(currentData.time >= time))[0]
      if np.size(timeInx) == 0:
        timeInx = -1
      else:
        timeInx = int(np.min(timeInx))

    #do some stuff in map projection coords to get necessary width and height of map
    lonFull,latFull = (np.array(lonFull)+360.)%360.,np.array(latFull)

    goodLatLon  = np.logical_and( np.logical_not(np.isnan(lonFull)), np.logical_not(np.isnan(latFull)) )
    goodInx     = np.where(goodLatLon)
    goodLatFull = latFull[goodInx]
    goodLonFull = lonFull[goodInx]

    tmpmap = Basemap(projection='npstere', boundinglat=20,lat_0=90, lon_0=np.mean(goodLonFull))
    x,y = tmpmap(goodLonFull,goodLatFull)
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

    #draw the actual map we want
    m = Basemap(projection='stere',width=width,height=height,lon_0=np.mean(goodLonFull),lat_0=lat_0,ax=axis)
    m.drawparallels(np.arange(-80.,81.,10.),labels=[1,0,0,0])
    m.drawmeridians(np.arange(-180.,181.,20.),labels=[0,0,0,1])
    if(coords == 'geo'):
      m.drawcoastlines(linewidth=0.5,color='k')
      m.drawmapboundary(fill_color='w')
      m.fillcontinents(color='w', lake_color='w')
    #overlay fields of view, if desired
#    if(fov == 1):
#      for r in rad:
#        pydarn.plotting.overlayRadar(m, codes=r, dateTime=sTime)
#        pydarn.plotting.overlayFov(m, codes=r, dateTime=sTime)

    #Setup the map!!
#    m = Basemap(projection='merc',
#                  lon_0=0,lat_0=0,lat_ts=0,
#                  llcrnrlat=5,urcrnrlat=68,
#                  llcrnrlon=-180,urcrnrlon=-50,
#                  resolution='l',ax=axis,**kwArgs)
#    m.drawcountries(linewidth=1, color='k')
#    m.bluemarble(scale=1)
#    m.drawmapscale(-60, 12, -90, 5, 1000, barstyle='fancy',fontcolor='w')

    #Plot the SuperDARN data!
    ngates = np.shape(currentData.data)[2]
    nbeams = np.shape(currentData.data)[1]
    verts = []
    scan = []
    data  = currentData.data[timeInx,:,:]
    for bm in range(nbeams):
      for rg in range(ngates):
        if goodLatLon[bm,rg] == False: continue
        if np.isnan(data[bm,rg]): continue
        if data[bm,rg] == 0 and not plotZeros: continue
        scan.append(data[bm,rg])

        x1,y1 = m(lonFull[bm+0,rg+0],latFull[bm+0,rg+0])
        x2,y2 = m(lonFull[bm+1,rg+0],latFull[bm+1,rg+0])
        x3,y3 = m(lonFull[bm+1,rg+1],latFull[bm+1,rg+1])
        x4,y4 = m(lonFull[bm+0,rg+1],latFull[bm+0,rg+1])
        verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

    colors  = 'lasse'
    cmap,norm,bounds = utils.plotUtils.genCmap(param,scale,colors=colors)
    pcoll = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    #Mark Cell
    markVerts = []
    if markCell != None:
      beamInx = int(np.where(currentData.fov.beams == markCell[0])[0])
      gateInx = int(np.where(currentData.fov.gates == markCell[1])[0])

      x1,y1 = m(lonFull[beamInx+0,gateInx+0],latFull[beamInx+0,gateInx+0])
      x2,y2 = m(lonFull[beamInx+1,gateInx+0],latFull[beamInx+1,gateInx+0])
      x3,y3 = m(lonFull[beamInx+1,gateInx+1],latFull[beamInx+1,gateInx+1])
      x4,y4 = m(lonFull[beamInx+0,gateInx+1],latFull[beamInx+0,gateInx+1])
      markVerts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

      mkv = np.array([[x1,y1],[x2,y2],[x3,y3],[x4,y4],[x1,y1]])

      poly = Polygon(mkv,facecolor='#000000',edgecolor='none',zorder=100)
      axis.add_patch(poly)

    dataName = currentData.history[max(currentData.history.keys())] #Label the plot with the current level of data processing.
    axis.set_title(metadata['name']+' - '+dataName+currentData.time[timeInx].strftime('\n%Y %b %d %H%M UT')) 

    cbar = fig.colorbar(pcoll,orientation='vertical',shrink=.65,fraction=.1)
    cbar.set_label(cbarLabel)
    labels = cbar.ax.get_yticklabels()
    labels[-1].set_visible(False)
    txt = 'Coordinates: ' + metadata['coords'] +', Model: ' + metadata['model']
    axis.text(1.01, 0, txt,
            horizontalalignment='left',
            verticalalignment='bottom',
            rotation='vertical',
            size='small',
            transform=axis.transAxes)

def plotRelativeRanges(dataObj,dataSet='active',time=None,fig=None):
    """Plots the N-S and E-W distance from the center cell of a field-of-view in a vtMUSIC object.
       Also plots one scan of the chosen dataSet, with the center cell marked in black.

    **Args**:
        * **dataObj**:  vtMUSIC object
        * **dataSet**:  which dataSet in the vtMUSIC object to process
        * **time**:     datetime.datetime object giving the start scan time to plot.  If None, first time will be used.
        * **fig**:      matplotlib figure object that will be plotted to.  If not provided, one will be created.
    **Returns**:
        * **fig**:      matplotlib figure object that was plotted to
    """
  currentData = getattr(dataObj,dataSet)

  from matplotlib.backends.backend_agg import FigureCanvasAgg
  from matplotlib.figure import Figure
  import matplotlib

  #Get center of FOV.
  ctrBeamInx  = currentData.fov.relative_centerInx[0]
  ctrGateInx  = currentData.fov.relative_centerInx[1]
  ctrBeam     = currentData.fov.beams[ctrBeamInx]
  ctrGate     = currentData.fov.gates[ctrGateInx]

  if fig == None:
    fig   = Figure()

  gs    = matplotlib.gridspec.GridSpec(3, 2,hspace=None)
  axis  = fig.add_subplot(gs[0:2, 1]) 
  musicFan(dataObj,time=time,plotZeros=True,dataSet=dataSet,axis=axis,markCell=(ctrBeam,ctrGate))

  #Determine the color scale for plotting.
  def myround(x, base=50):
        return int(base * round(float(x)/base))
  absmax  = np.max(np.abs([currentData.fov.relative_x,currentData.fov.relative_y]))
  rnd     = myround(absmax)
  scale   = (-rnd, rnd)

  #Determine maximum ranges.
  xRange    = np.max(currentData.fov.relative_x) - np.min(currentData.fov.relative_x)
  yRange    = np.max(currentData.fov.relative_y) - np.min(currentData.fov.relative_y)
  latRange  = np.max(currentData.fov.latCenter)  - np.min(currentData.fov.latCenter)
  lonRange  = np.max(currentData.fov.lonCenter)  - np.min(currentData.fov.lonCenter)

  axis  = fig.add_subplot(gs[0:2, 0]) 
#    axis.set_visible(False)

  axis.set_axis_off()
  text = []
  text.append('X-Range [km]: %i' % xRange)
  text.append('Y-Range [km]: %i' % yRange)
  text.append('Lat Range [deg]: %.1f' % latRange)
  text.append('Lon Range [deg]: %.1f' % lonRange)
  text = '\n'.join(text)
  axis.text(0,0.75,text)

  xlabel    = 'Beam'
  ylabel    = 'Gate'
  cbarLabel = 'Distance from Center [km]'

  axis   = fig.add_subplot(gs[2,0]) 
  data    = currentData.fov.relative_y
  title   = 'N-S Distance from Center'
  title   = '\n'.join([title,'(Beam: %i, Gate: %i)' % (ctrBeam, ctrGate)])
  rangeBeamPlot(currentData,data,axis,title=title,xlabel=xlabel,ylabel=ylabel,scale=scale,cbarLabel=cbarLabel)

  axis   = fig.add_subplot(gs[2,1]) 
  data    = currentData.fov.relative_x
  title   = 'E-W Distance from Center'
  title   = '\n'.join([title,'(Beam: %i, Gate: %i)' % (ctrBeam, ctrGate)])
  rangeBeamPlot(currentData,data,axis,title=title,xlabel=xlabel,ylabel=ylabel,scale=scale,cbarLabel=cbarLabel)

  return fig

def rangeBeamPlot(currentData,data,axis,title=None,xlabel=None,ylabel=None,param='velocity',scale=None,cbarLabel=None):
    """Plots data on a range versus beam plot with a colorbar.

    **Args**:
        * **currentData**:  vtMUSIC.dataSet object
        * **data**:         nBeams x nGates Numpy array of data
        * **axis**:         matplotlib axis object on which to plot
        * **title**:        Title of plot.
        * **xlabel**:       X-axis label
        * **ylabel**:       Y-axis label
        * **param**:        Parameter used for colorbar selection.
        * **scale**:        Two-element colorbar scale.
        * **cbarLabel**:    Colorbar label.
    """
  fig     = axis.get_figure()

  ngates  = len(currentData.fov.gates)
  nbeams  = len(currentData.fov.beams)
  verts   = []
  scan    = []

  for bmInx in range(nbeams):
    for rgInx in range(ngates):
      scan.append(data[bmInx,rgInx])

      bm = currentData.fov.beams[bmInx]
      rg = currentData.fov.gates[rgInx]

      x1,y1 = bm+0, rg+0
      x2,y2 = bm+1, rg+0
      x3,y3 = bm+1, rg+1
      x4,y4 = bm+0, rg+1
      verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

  colors  = 'lasse'
  if scale == None:
    scale   = (np.min(scan),np.max(scan))

  cmap,norm,bounds = utils.plotUtils.genCmap(param,scale,colors=colors)
  pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
  pcoll.set_array(np.array(scan))
  axis.add_collection(pcoll,autolim=False)

  axis.set_xlim(min(currentData.fov.beams), max(currentData.fov.beams)+1)
  axis.set_ylim(min(currentData.fov.gates), max(currentData.fov.gates)+1)

  if title != None: axis.set_title(title)
  if xlabel != None: axis.set_xlabel(xlabel)
  if ylabel != None: axis.set_ylabel(ylabel)

  cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
  if cbarLabel != None: cbar.set_label(cbarLabel)
  labels = cbar.ax.get_yticklabels()
  labels[-1].set_visible(False)
  labels[0].set_visible(False)

def multiPlot(dataObj,dataSet='active',plotBeam=None,plotGate=None,fig=None,xlim=None,ylim=None):
    """Plots 1D line time series and spectral plots of selected cells in a vtMUSIC object.
    This defaults to 9 cells of the FOV.

    **Args**:
        * **dataObj**:  vtMUSIC object
        * **dataSet**:  which dataSet in the vtMUSIC object to process
        * **plotBeam**: list of beams to plot from
        * **plotGates*: list of range gates to plot from
        * **fig**:      matplotlib figure object that will be plotted to.  If not provided, one will be created.
        * **xlim**:     X-axis limits of all plots
        * **ylim**:     Y-axis limits of all plots
    **Returns**:
        * **fig**:      matplotlib figure object that was plotted to
    """
  from matplotlib import dates as md
  currentData = getattr(dataObj,dataSet)

  #Calculate three default beams and gates to plot.
  if plotBeam == None:
    beamMin = min(currentData.fov.beams)
    beamMed = int(np.median(currentData.fov.beams))
    beamMax = max(currentData.fov.beams)

    plotBeam     = np.array([beamMin,beamMed,beamMax])

  if plotGate == None:
    gateMin = min(currentData.fov.gates)
    gateMed = int(np.median(currentData.fov.gates))
    gateMax = max(currentData.fov.gates)

    plotGate     = np.array([gateMin,gateMed,gateMax])

  #Put things in the correct order.  Gates need to be backwards.
  plotBeam.sort()
  plotGate.sort()
  plotGate = plotGate[::-1] #Reverse the order.

  #Determine the indices of the beams and gates.
  plotBeamInx = []
  for item in plotBeam:
    plotBeamInx.append(int(np.where(currentData.fov.beams == item)[0]))

  plotGateInx = []
  for item in plotGate:
    plotGateInx.append(int(np.where(currentData.fov.gates == item)[0]))

  plotBeamInx = np.array(plotBeamInx)
  plotGateInx = np.array(plotGateInx)

  nCols = len(plotBeam)
  nRows = len(plotGate)

  if fig == None:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    fig = Figure()

  #Define x-axis range
  if xlim == None:
    xlim = (min(currentData.time),max(currentData.time))

  #Autorange y-axis... make all plots have the same range.
  data = []
  if ylim == None:
    for rg,rgInx in zip(plotGate,plotGateInx):
      for bm,bmInx in zip(plotBeam,plotBeamInx):
        data.append(currentData.data[:,bmInx,rgInx])
    mx  = np.max(data)
    mn  = np.min(data)
   
    if mx > 0 and mn >= 0:
      ylim = (0,mx)
    elif mn < 0 and mx <= 0:
      ylim = (mn,0)
    elif abs(mx) >= abs(mn):
      ylim = (-mx,mx)
    elif abs(mn) > abs(mx):
      ylim = (-abs(mn),abs(mn))


  ii = 1
  for rg,rgInx in zip(plotGate,plotGateInx):
    for bm,bmInx in zip(plotBeam,plotBeamInx):
      axis = fig.add_subplot(nCols,nRows,ii)
      axis.plot(currentData.time,currentData.data[:,bmInx,rgInx])

      axis.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))

      labels = axis.get_xticklabels()
      for label in labels:
        label.set_rotation(30)

      #Set axis limits.
      if xlim != None:
        axis.set_xlim(xlim)
      if ylim != None:
        axis.set_ylim(ylim)

      text = 'Beam: %i, Gate: %i' % (bm, rg)
      axis.text(0.02,0.92,text,transform=axis.transAxes)

      #Only have the last row have time ticks
      if ii <= (nRows-1)*nCols:
        axis.xaxis.set_visible(False)
      else:
        axis.set_xlabel('UT')


      ii = ii+1
    title = []
    title.append('Selected Cells')
    title.append(currentData.metadata['code'][0].upper() + ': ' +
        xlim[0].strftime('%Y %b %d %H:%M - ') + xlim[1].strftime('%Y %b %d %H:%M'))
    title = '\n'.join(title)
    fig.suptitle(title,size=24)

  return fig
