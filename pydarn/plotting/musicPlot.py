import numpy as np
import datetime

from matplotlib.collections import PolyCollection
from matplotlib import dates as md
import matplotlib

from mpl_toolkits.basemap import Basemap

import utils

class musicFan(object):
  def __init__(self,dataObject,dataSet='active',time=None,axis=None,fileName=None,scale=None, plotZeros=False, **kwArgs):
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
    if    metadata['param'] == 'p_l'  :
      param     =  'power'
      cbarLabel = r'$\lambda$ Power [dB]'
    elif  metadata['param'] == 'p_s'  :
      param     =  'power'
      cbarLabel = r'$\sigma$ Power [dB]'
    elif  metadata['param'] == 'v'    :
      param     = 'velocity'
      cbarLabel = 'Velocity [m/s]'
    elif  metadata['param'] == 'w_l'  :
      param     = 'width'
      cbarLabel = r'$\lambda$ Spectral Width [m/s]'
    elif  metadata['param'] == 'w_s'  : 
      param     = 'width'
      cbarLabel = r'$\sigma$ Spectral Width [m/s]'
    elif  metadata['param'] == 'elv'  :
      param     = 'elevation'
      cbarLabel = 'Elevation [deg]'
    elif  metadata['param'] == 'phi0' :
      param     = 'phi0'
      cbarLabel = r'$\phi_0$'
    else:
      param     = metadata['param']
      cbarLabel = metadata['param']

    #Set colorbar scale if not explicitly defined.
    if(scale == None):
      if(param == 'velocity'):
        scale=[-200,200]
      elif(param == 'power'):
        scale=[0,30]
      elif(param == 'width'):
        scale=[0,150]
      elif(param == 'elevation'): 
        scale=[0,50]
      elif(param == 'phi0'):
        scale=[-np.pi,np.pi]
      else:
        param = 'width' #Set param = 'width' at this point just to not screw up the colorbar function.
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
#    plt.show()

class plotRelativeRanges(object):
  def __init__(self,dataObj,dataSet='active',time=None):

    currentData = getattr(dataObj,dataSet)

    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    import matplotlib

    fig   = Figure(figsize=(11,8.5))

    gs    = matplotlib.gridspec.GridSpec(3, 2,hspace=None)
    axis  = fig.add_subplot(gs[0:2, 1]) 
    musicFan(dataObj,time=time,plotZeros=True,dataSet=dataSet,axis=axis)

    #Determine the color scale for plotting.
    def myround(x, base=50):
          return int(base * round(float(x)/base))
    absmax  = np.max(np.abs([currentData.fov.relative_x,currentData.fov.relative_y]))
    rnd     = myround(absmax)
    scale   = (-rnd, rnd)

    xlabel    = 'Beam'
    ylabel    = 'Gate'
    cbarLabel = 'Distance from Center [km]'

    axis   = fig.add_subplot(gs[2,0]) 
    data    = currentData.fov.relative_y
    title   = 'N-S Distance from Center'
    ctrBeamInx  = currentData.fov.relative_centerInx[0]
    ctrGateInx  = currentData.fov.relative_centerInx[1]
    ctrBeam     = currentData.fov.beams[ctrBeamInx]
    ctrGate     = currentData.fov.gates[ctrGateInx]
    title   = '\n'.join([title,'(Beam: %i, Gate: %i)' % (ctrBeam, ctrGate)])
    rangeBeamPlot(currentData,data,axis,title=title,xlabel=xlabel,ylabel=ylabel,scale=scale,cbarLabel=cbarLabel)

    axis   = fig.add_subplot(gs[2,1]) 
    data    = currentData.fov.relative_x
    title   = 'E-W Distance from Center'
    ctrBeamInx  = currentData.fov.relative_centerInx[0]
    ctrGateInx  = currentData.fov.relative_centerInx[1]
    ctrBeam     = currentData.fov.beams[ctrBeamInx]
    ctrGate     = currentData.fov.gates[ctrGateInx]
    title   = '\n'.join([title,'(Beam: %i, Gate: %i)' % (ctrBeam, ctrGate)])
    rangeBeamPlot(currentData,data,axis,title=title,xlabel=xlabel,ylabel=ylabel,scale=scale,cbarLabel=cbarLabel)

    outFName = '/data/pymusic/ranges.png'
    canvas  = FigureCanvasAgg(fig)
    canvas.print_figure(outFName,format='png',facecolor='white',edgecolor='white')

def rangeBeamPlot(currentData,data,axis,title=None,xlabel=None,ylabel=None,param='velocity',scale=None,cbarLabel=None):
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

#    cbar = fig.colorbar(pcoll,orientation='vertical',shrink=.65,fraction=.1)
  cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
  if cbarLabel != None: cbar.set_label(cbarLabel)
  labels = cbar.ax.get_yticklabels()
  labels[-1].set_visible(False)
  labels[0].set_visible(False)
#  txt = 'Coordinates: ' + metadata['coords'] +', Model: ' + metadata['model']
#  txt = 'txt'
#  axis.text(1.01, 0, txt,
#          horizontalalignment='left',
#          verticalalignment='bottom',
#          rotation='vertical',
#          size='small',
#          transform=axis.transAxes
