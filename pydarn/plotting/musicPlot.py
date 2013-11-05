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

from pydarn.proc.music import getDataSet

def daynight_terminator(date, lons):
    """
    date is datetime object (assumed UTC).
    nlons is # of longitudes used to compute terminator."""
    import mpl_toolkits.basemap.solar as solar
    dg2rad = np.pi/180.
    # compute greenwich hour angle and solar declination
    # from datetime object (assumed UTC).
    tau, dec = solar.epem(date)
    # compute day/night terminator from hour angle, declination.
    longitude = lons + tau
    lats = np.arctan(-np.cos(longitude*dg2rad)/np.tan(dec*dg2rad))/dg2rad
    return lats,tau,dec

class musicFan(object):
  def __init__(self,dataObject,dataSet='active',time=None,axis=None,fileName=None,scale=None,autoScale=False, plotZeros=False, markCell=None, plotTerminator=True, **kwArgs):
    from scipy import stats
    if fileName != None:
      from matplotlib.backends.backend_agg import FigureCanvasAgg
      from matplotlib.figure import Figure
      if axis==None:
        fig   = Figure(figsize=(20,10))
    else:
      from matplotlib import pyplot as plt
      if axis==None:
        fig   = plt.figure(figsize=(20,10))

    #Make some variables easier to get to...
    currentData = getDataSet(dataObject,dataSet)
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
        if autoScale:
            sd          = stats.nanstd(np.abs(currentData.data),axis=None)
            mean        = stats.nanmean(np.abs(currentData.data),axis=None)
            scMax       = np.ceil(mean + 1.*sd)
            if np.min(currentData.data) < 0:
                scale   = scMax*np.array([-1.,1.])
            else:
                scale   = scMax*np.array([0.,1.])
        else:
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
    scan  = []
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

    if (scale[0] >= -1 and scale[1] <= 1) or autoScale:
      cmap = matplotlib.cm.jet
      bounds  = np.linspace(scale[0],scale[1],256)
      norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)
    else:
      colors  = 'lasse'
      cmap,norm,bounds = utils.plotUtils.genCmap(param,scale,colors=colors)

    pcoll = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    #Mark Cell
    if markCell != None:
      beamInx = int(np.where(currentData.fov.beams == markCell[0])[0])
      gateInx = int(np.where(currentData.fov.gates == markCell[1])[0])

      x1,y1 = m(lonFull[beamInx+0,gateInx+0],latFull[beamInx+0,gateInx+0])
      x2,y2 = m(lonFull[beamInx+1,gateInx+0],latFull[beamInx+1,gateInx+0])
      x3,y3 = m(lonFull[beamInx+1,gateInx+1],latFull[beamInx+1,gateInx+1])
      x4,y4 = m(lonFull[beamInx+0,gateInx+1],latFull[beamInx+0,gateInx+1])

      mkv = np.array([[x1,y1],[x2,y2],[x3,y3],[x4,y4],[x1,y1]])

      poly = Polygon(mkv,facecolor='#000000',edgecolor='none',zorder=100)
      axis.add_patch(poly)

    dataName = currentData.history[max(currentData.history.keys())] #Label the plot with the current level of data processing.
    axis.set_title(metadata['name']+' - '+dataName+currentData.time[timeInx].strftime('\n%Y %b %d %H%M UT')) 

#    cbar = fig.colorbar(pcoll,orientation='vertical',shrink=.65,fraction=.1)
    cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
    cbar.set_label(cbarLabel)
    labels = cbar.ax.get_yticklabels()
    labels[-1].set_visible(False)
    if currentData.metadata.has_key('gscat'):
      if currentData.metadata['gscat'] == 1:
        cbar.ax.text(0.5,-0.075,'Ground\nscat\nonly',ha='center')
    txt = 'Coordinates: ' + metadata['coords'] +', Model: ' + metadata['model']
    axis.text(1.01, 0, txt,
            horizontalalignment='left',
            verticalalignment='bottom',
            rotation='vertical',
            size='small',
            transform=axis.transAxes)

    if plotTerminator:
        m.nightshade(currentData.time[timeInx])

class musicRTI(object):
    def __init__(self,dataObject,dataSet='active',beam=7,xlim=None,ylim=None,coords='gate',axis=None,fileName=None,scale=None, plotZeros=False, xBoundaryLimits=None, yBoundaryLimits=None, autoScale=False, plotTerminator=True, axvlines=None, axvline_color='0.25', **kwArgs):
        """create an rti plot for a secified radar and time period from a data set in a musicObj.

        **Args**:
          * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): a datetime object indicating the start time which you would like to plot
          * **rad** (str): the 3 letter radar code, e.g. 'bks'
          * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): a datetime object indicating th end time you would like plotted.  If this is None, 24 hours will be plotted.  default = None.
          * **[bmnum] (int)**: The beam to plot.  default: 7
          * **[fileType]** (str): The file type to be plotted, one of ['fitex','fitacf','lmfit'].  default = 'fitex'.
          * **[params]** (list): a list of the fit parameters to plot, allowable values are: ['velocity', 'power', 'width', 'elevation', 'phi0'].  default: ['velocity', 'power', 'width']
          * **[scales]** (list): a list of the min/max values for the color scale for each param.  If omitted, default scales will be used.  If present, the list should be n x 2 where n is the number of elements in the params list.  Use an empty list for default range, e.g. [[-250,300],[],[]].  default: [[-200,200],[0,30],[0,150]]
          * **[channel]** (char): the channel you wish to plot, e.g. 'a', 'b', 'c', ...  default: 'a'
          * **[coords]** (str): the coordinates to use for the y axis.  The allowable values are 'gate', 'rng', 'geo', 'mag' default: 'gate'
          * **[colors]** (str): a string indicating what color bar to use, valid inputs are ['lasse','aj'].  default: 'lasse'
          * **[yrng]** (list or -1): a list indicating the min and max values for the y axis in the chosen coordinate system, or a -1 indicating to plot everything.  default: -1.
          * **[gsct]** (boolean): a flag indicating whether to plot ground scatter as gray. default: False (ground scatter plotted normally)
          * **[lowGray]** (boolean): a flag indicating whether to plot low velocity scatter as gray. default: False (low velocity scatter plotted normally)
          * **[pdf]** (boolean): a flag indicating whether to output to a pdf file.  default = False.  WARNING: saving as pdf is slow.
          * **[png]** (boolean): a flag indicating whether to output to a png file.  default = False
          * **[dpi]** (int): dots per inch if saving as png.  default = 300
          * **[show]** (boolean): a flag indicating whether to display the figure on the screen.  This can cause problems over ssh.  default = True
          * **[retfig]** (boolean):  a flag indicating that you want the figure to be returned from the function.  Only the last figure in the list of frequency bands will be returned.  default = False
          * **[filtered]** (boolean): a flag indicating whether to boxcar filter the data.  default = False (no filter)
          * **[fileName]** (string): If you want to plot for a specific file, indicate the name of the file as fileName.  Include the type of the file in custType.
          * **[custType]** (string): the type (fitacf, lmfit, fitex) of file indicated by fileName
          * **[tFreqBands]** (list): a list of the min/max values for the transmitter frequencies in kHz.  If omitted, the default band will be used.  If more than one band is specified, retfig will cause only the last one to be returned.  default: [[8000,20000]]
          * **[myFile]** (:class:`pydarn.sdio.radDataTypes.radDataPtr`): contains the pipeline to the data we want to plot. If specified, data will be plotted from the file pointed to by myFile. default: None
          * **[figure]** (matplotlib.figure) figure object to plot on.  If None, a figure object will be created for you.
          * **[xtick_size]**: (int) fontsize of xtick labels
          * **[ytick_size]**: (int) fontsize of ytick labels
          * **[xticks]**: (list) datetime.datetime objects indicating the location of xticks
          * **[axvlines]**: (list) datetime.datetime objects indicating the location vertical lines marking the plot
          * **[plotTerminator]**: (boolean) Overlay the day/night terminator.
        **Returns**:
          * Possibly figure, depending on the **retfig** keyword

        **Example**:
          ::
          
            import datetime as dt
            pydarn.plotting.rti.plotRti(dt.datetime(2013,3,16), 'bks', eTime=dt.datetime(2013,3,16,14,30), bmnum=12, fileType='fitacf', scales=[[-500,500],[],[]], coords='geo',colors='aj', filtered=True, show=True)

          
        Written by Nathaniel A. Frissell Fall 2013
        """
        from scipy import stats
        from rti import plotFreq,plotNoise

        if fileName != None:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            from matplotlib.figure import Figure
            if axis==None:
                fig   = Figure(figsize=(20,10))
        else:
            from matplotlib import pyplot as plt
            if axis==None:
                fig   = plt.figure(figsize=(20,10))

        #Make some variables easier to get to...
        currentData = getDataSet(dataObject,dataSet)
        metadata    = currentData.metadata
        latFull     = currentData.fov.latFull
        lonFull     = currentData.fov.lonFull
        latCenter   = currentData.fov.latCenter
        lonCenter   = currentData.fov.lonCenter
        time        = currentData.time
        beamInx     = np.where(currentData.fov.beams == beam)[0]
        radar_lats  = latCenter[beamInx,:]
        nrTimes, nrBeams, nrGates = np.shape(currentData.data)

        # Calculate terminator. ########################################################
        if plotTerminator:
            daylight = np.ones([nrTimes,nrGates],np.bool)
            for tm_inx in range(nrTimes):
                tm                  = time[tm_inx]
                term_lons           = lonCenter[beamInx,:]
                term_lats,tau,dec   = daynight_terminator(tm,term_lons)

                if dec > 0: # NH Summer
                    day_inx = np.where(radar_lats < term_lats)[1]
                else:
                    day_inx = np.where(radar_lats > term_lats)[1]

                if day_inx.size != 0:
                    daylight[tm_inx,day_inx] = False
        ################################################################################

        coords      = metadata['coords']
        if coords not in ['gate','range']:
            print 'Coords "%s" not supported for RTI plots.  Using "gate".' % coords
            coords = 'gate'

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
            if autoScale:
                sd          = stats.nanstd(np.abs(currentData.data),axis=None)
                mean        = stats.nanmean(np.abs(currentData.data),axis=None)
                scMax       = np.ceil(mean + 1.*sd)
                if np.min(currentData.data) < 0:
                    scale   = scMax*np.array([-1.,1.])
                else:
                    scale   = scMax*np.array([0.,1.])
            else:
                if paramDict.has_key('range'):
                    scale = paramDict['range']
                else:
                    scale = [-200,200]

        #See if an axis is provided... if not, set one up!
        if axis==None:
            axis    = fig.add_subplot(111)
        else:
            fig   = axis.get_figure()

        if np.size(beamInx) == 0:
            beamInx = 0
            beam    = currentData.fov.beams[0]

        #Plot the SuperDARN data!
        verts = []
        scan  = []
        data  = np.squeeze(currentData.data[:,beamInx,:])

        rnge  = currentData.fov.gates
        xvec  = [matplotlib.dates.date2num(x) for x in currentData.time]
        for tm in range(nrTimes-1):
            for rg in range(nrGates-1):
                if np.isnan(data[tm,rg]): continue
                if data[tm,rg] == 0 and not plotZeros: continue
                scan.append(data[tm,rg])

                x1,y1 = xvec[tm+0],rnge[rg+0]
                x2,y2 = xvec[tm+1],rnge[rg+0]
                x3,y3 = xvec[tm+1],rnge[rg+1]
                x4,y4 = xvec[tm+0],rnge[rg+1]
                verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

        if (scale[0] >= -1 and scale[1] <= 1) or autoScale:
            cmap = matplotlib.cm.jet
            bounds  = np.linspace(scale[0],scale[1],256)
            norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)
        else:
            colors  = 'lasse'
            cmap,norm,bounds = utils.plotUtils.genCmap(param,scale,colors=colors)

        pcoll = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
        pcoll.set_array(np.array(scan))
        axis.add_collection(pcoll,autolim=False)

        # Plot the terminator! #########################################################
        if plotTerminator:
            #Plot the SuperDARN data!
            term_verts = []
            term_scan  = []

            rnge  = currentData.fov.gates
            xvec  = [matplotlib.dates.date2num(x) for x in currentData.time]
            for tm in range(nrTimes-1):
                for rg in range(nrGates-1):
                    if daylight[tm,rg]: continue
                    term_scan.append(1)

                    x1,y1 = xvec[tm+0],rnge[rg+0]
                    x2,y2 = xvec[tm+1],rnge[rg+0]
                    x3,y3 = xvec[tm+1],rnge[rg+1]
                    x4,y4 = xvec[tm+0],rnge[rg+1]
                    term_verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

            term_pcoll = PolyCollection(np.array(term_verts),facecolors='0.45',linewidth=0,zorder=99,alpha=0.25)
            axis.add_collection(term_pcoll,autolim=False)
        ################################################################################

        if axvlines is not None:
            for line in axvlines:
                axis.axvline(line,color=axvline_color,ls='--')

        if xlim == None:
            xlim = (np.min(time),np.max(time))
        axis.set_xlim(xlim)

        axis.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        axis.set_xlabel('Time [UT]')

        if ylim == None:
            ylim = (np.min(rnge),np.max(rnge))
        axis.set_ylim(ylim)
        axis.set_ylabel('Range Gate\nGeographic Latitude')

        yticks  = axis.get_yticks()
        ytick_str    = []
        for tck in yticks:
            txt = []
            txt.append('%d' % tck)

            rg_inx = np.where(tck == currentData.fov.gates)[0]
            if np.size(rg_inx) != 0:
                lat = currentData.fov.latCenter[beamInx,rg_inx]
                if np.isfinite(lat): 
                    txt.append(u'%.1f$^o$' % lat)
                else:
                    txt.append('')
            txt = '\n'.join(txt)
            ytick_str.append(txt)

        axis.set_yticklabels(ytick_str,rotation=90,ma='center')


        #Shade xBoundary Limits
        if xBoundaryLimits == None:
            if currentData.metadata.has_key('timeLimits'):
                xBoundaryLimits = currentData.metadata['timeLimits']

        if xBoundaryLimits != None:
            gray = '0.75'
            axis.axvspan(xlim[0],xBoundaryLimits[0],color=gray,zorder=150,alpha=0.5)
            axis.axvspan(xBoundaryLimits[1],xlim[1],color=gray,zorder=150,alpha=0.5)
            axis.axvline(x=xBoundaryLimits[0],color='g',ls='--',lw=2,zorder=150)
            axis.axvline(x=xBoundaryLimits[1],color='g',ls='--',lw=2,zorder=150)

        #Shade yBoundary Limits
        if yBoundaryLimits == None:
            if currentData.metadata.has_key('gateLimits') and coords == 'gate':
                yBoundaryLimits = currentData.metadata['gateLimits']

            if currentData.metadata.has_key('rangeLimits') and coords == 'range':
                yBoundaryLimits = currentData.metadata['rangeLimits']

        if yBoundaryLimits != None:
            gray = '0.75'
            axis.axhspan(ylim[0],yBoundaryLimits[0],color=gray,zorder=150,alpha=0.5)
            axis.axhspan(yBoundaryLimits[1],ylim[1],color=gray,zorder=150,alpha=0.5)
            axis.axhline(y=yBoundaryLimits[0],color='g',ls='--',lw=2,zorder=150)
            axis.axhline(y=yBoundaryLimits[1],color='g',ls='--',lw=2,zorder=150)
        
            for bnd_item in yBoundaryLimits:
                if coords == 'gate':
                    txt = []
                    txt.append('%d' % bnd_item)

                    rg_inx = np.where(bnd_item == currentData.fov.gates)[0]
                    if np.size(rg_inx) != 0:
                        lat = currentData.fov.latCenter[beamInx,rg_inx]
                        if np.isfinite(lat): 
                            txt.append(u'%.1f$^o$' % lat)
                        else:
                            txt.append('')
                    txt = '\n'.join(txt)
                else:
                    txt = '%.1f' % bnd_item
                axis.annotate(txt, (1.01, bnd_item) ,xycoords=('axes fraction','data'),rotation=90,ma='center')


        cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
        cbar.set_label(cbarLabel)
        labels = cbar.ax.get_yticklabels()
        labels[-1].set_visible(False)
        if currentData.metadata.has_key('gscat'):
            if currentData.metadata['gscat'] == 1:
                cbar.ax.text(0.5,-0.075,'Ground\nscat\nonly',ha='center')

        txt = 'Model: ' + metadata['model']
        axis.text(1.01, 0, txt,
                horizontalalignment='left',
                verticalalignment='bottom',
                rotation='vertical',
                size='small',
                transform=axis.transAxes)

        #Get axis position information.
        pos = list(axis.get_position().bounds)

        # Plot frequency and noise information. ######################################## 
        if hasattr(dataObject,'prm'):
            #Adjust current plot position to fit in the freq and noise plots.
            super_plot_hgt  = 0.06
            pos[3] = pos[3] - (2*super_plot_hgt)
            axis.set_position(pos)

            #Get current colorbar position and adjust it.
            cbar_pos = list(cbar.ax.get_position().bounds)
            cbar_pos[1] = pos[1]
            cbar_pos[3] = pos[3]
            cbar.ax.set_position(cbar_pos)

            curr_xlim   = axis.get_xlim()
            curr_xticks = axis.get_xticks()

            pos[1] = pos[1] + pos[3]
            pos[3] = super_plot_hgt
            plotFreq(fig,dataObject.prm.time,dataObject.prm.tfreq,dataObject.prm.nave,pos=pos,xlim=curr_xlim,xticks=curr_xticks)

            pos[1] = pos[1] + super_plot_hgt
            plotNoise(fig,dataObject.prm.time,dataObject.prm.noisesky,dataObject.prm.noisesearch,pos=pos,xlim=curr_xlim,xticks=curr_xticks)

        # Put a title on the RTI Plot. #################################################
        title_y = (pos[1] + pos[3]) + 0.015
        xmin    = pos[0]
        xmax    = pos[0] + pos[2]

        txt     = metadata['name']+'  ('+metadata['fType']+')'
        fig.text(xmin,title_y,txt,ha='left',weight=550)

        txt     = []
        txt.append(xlim[0].strftime('%Y %b %d %H%M UT - ')+xlim[1].strftime('%Y %b %d %H%M UT'))
        txt.append(currentData.history[max(currentData.history.keys())]) #Label the plot with the current level of data processing.
        txt     = '\n'.join(txt)
        fig.text((xmin+xmax)/2.,title_y,txt,weight=550,size='large',ha='center')

        txt     = 'Beam '+str(beam)
        fig.text(xmax,title_y,txt,weight=550,ha='right')

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

    Written by Nathaniel A. Frissell, Fall 2013
    """
    if fig == None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=(20,10))

    currentData = getDataSet(dataObj,dataSet)

    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    import matplotlib

    #Get center of FOV.
    ctrBeamInx  = currentData.fov.relative_centerInx[0]
    ctrGateInx  = currentData.fov.relative_centerInx[1]
    ctrBeam     = currentData.fov.beams[ctrBeamInx]
    ctrGate     = currentData.fov.gates[ctrGateInx]
    ctrLat      = currentData.fov.latCenter[ctrBeamInx,ctrGateInx]
    ctrLon      = currentData.fov.lonCenter[ctrBeamInx,ctrGateInx]

    gs    = matplotlib.gridspec.GridSpec(3, 2,hspace=None)
    axis  = fig.add_subplot(gs[0:2, 1]) 
    musicFan(dataObj,time=time,plotZeros=True,dataSet=dataSet,axis=axis,markCell=(ctrBeam,ctrGate))

    #Determine the color scale for plotting.
    def myround(x, base=50):
        return int(base * round(float(x)/base))

    absnanmax  = np.nanmax(np.abs([currentData.fov.relative_x,currentData.fov.relative_y]))
    rnd     = myround(absnanmax)
    scale   = (-rnd, rnd)

    #Determine nanmaximum ranges.
    xRange    = np.nanmax(currentData.fov.relative_x) - np.nanmin(currentData.fov.relative_x)
    yRange    = np.nanmax(currentData.fov.relative_y) - np.nanmin(currentData.fov.relative_y)
    latRange  = np.nanmax(currentData.fov.latCenter)  - np.nanmin(currentData.fov.latCenter)
    lonRange  = np.nanmax(currentData.fov.lonCenter)  - np.nanmin(currentData.fov.lonCenter)

    axis  = fig.add_subplot(gs[0:2, 0]) 

    axis.set_axis_off()
    text = []
    text.append('X-Range [km]: %i' % xRange)
    text.append('Y-Range [km]: %i' % yRange)
    text.append('Lat Range [deg]: %.1f' % latRange)
    text.append('Lon Range [deg]: %.1f' % lonRange)
    text.append('Center Lat [deg]: %.1f' % ctrLat)
    text.append('Center Lon [deg]: %.1f' % ctrLon)
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

  if scale == None:
    scale   = (np.min(scan),np.max(scan))

#  colors  = 'lasse'
#  cmap,norm,bounds = utils.plotUtils.genCmap(param,scale,colors=colors)

  cmap    = matplotlib.cm.jet
  bounds  = np.linspace(scale[0],scale[1],256)
  norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)

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
#  labels = cbar.ax.get_yticklabels()
#  labels[-1].set_visible(False)
#  labels[0].set_visible(False)

def timeSeriesMultiPlot(dataObj,dataSet='active',dataObj2=None,dataSet2=None,plotBeam=None,plotGate=None,fig=None,xlim=None,ylim=None,xlabel=None,ylabel=None,title=None,xBoundaryLimits=None):
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
        * **xlabel**:   X-axis label
        * **ylabel**:   Y-axis label
        * **xBoundaryLimits**: 2 Element sequence to shade out portions of the data.  Data outside of this range will be shaded gray,
            Data inside of the range will have a white background.  If set to None, this will automatically be set to the timeLimits set
            in the metadata, if they exist.

    **Returns**:
        * **fig**:      matplotlib figure object that was plotted to

    Written by Nathaniel A. Frissell, Fall 2013
    """
    currentData = getDataSet(dataObj,dataSet)
    xData1      = currentData.time
    yData1      = currentData.data
    beams       = currentData.fov.beams
    gates       = currentData.fov.gates

    if dataObj2 != None and dataSet2 == None: dataSet2 == 'active'

    if dataSet2 != None:
        if dataObj2 != None:
            currentData2  = getDataSet(dataObj2,dataSet2)
        else:
            currentData2  = getDataSet(dataObj,dataSet2)
        xData2        = currentData2.time
        yData2        = currentData2.data
        yData2_title  = currentData2.history[max(currentData2.history.keys())]
    else:
        xData2 = None
        yData2 = None
        yData2_title = None

    #Define x-axis range
    if xlim == None:
        tmpLim = []
        tmpLim.append(min(xData1))
        tmpLim.append(max(xData1))
        if xData2 != None:
            tmpLim.append(min(xData2))
            tmpLim.append(max(xData2))
        xlim = (min(tmpLim),max(tmpLim))

    #Set x boundary limits using timeLimits, if they exist.  Account for both dataSet1 and dataSet2, and write it so timeLimits can be any type of sequence.
    if xBoundaryLimits == None:
        tmpLim = []
        if currentData.metadata.has_key('timeLimits'):
            tmpLim.append(currentData.metadata['timeLimits'][0])
            tmpLim.append(currentData.metadata['timeLimits'][1])

        if dataSet2 != None:
          if currentData2.metadata.has_key('timeLimits'):
            tmpLim.append(currentData2.metadata['timeLimits'][0])
            tmpLim.append(currentData2.metadata['timeLimits'][1])

        if tmpLim != []:
            xBoundaryLimits = (min(tmpLim), max(tmpLim))

    #Get X-Axis title.
    if xlabel == None:
        xlabel = 'UT'

    #Get Y-Axis title.
    paramDict = getParamDict(currentData.metadata['param'])
    if ylabel == None and paramDict.has_key('label'):
        ylabel = paramDict['label']

    yData1_title = currentData.history[max(currentData.history.keys())] #Label the plot with the current level of data processing
    if title == None:
        title = []
        title.append('Selected Cells: '+yData1_title)
        title.append(currentData.metadata['code'][0].upper() + ': ' +
            xlim[0].strftime('%Y %b %d %H:%M - ') + xlim[1].strftime('%Y %b %d %H:%M'))
        title = '\n'.join(title)

    multiPlot(xData1,yData1,beams,gates,yData1_title=yData1_title,fig=fig,xlim=xlim,ylim=ylim,xlabel=xlabel,ylabel=ylabel,title=title,
          xData2=xData2,yData2=yData2,yData2_title=yData2_title,xBoundaryLimits=xBoundaryLimits)

def spectrumMultiPlot(dataObj,dataSet='active',plotType='real_imag',plotBeam=None,plotGate=None,fig=None,xlim=None,ylim=None,xlabel=None,ylabel=None,title=None,xBoundaryLimits=None):
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
        * **xlabel**:   X-axis label
        * **ylabel**:   Y-axis label
        * **xBoundaryLimits**: 2 Element sequence to shade out portions of the data.  Data outside of this range will be shaded gray,
            Data inside of the range will have a white background.
        * **plotType**: {'real_imag'|'magnitude'|'phase'}

    **Returns**:
        * **fig**:      matplotlib figure object that was plotted to

    Written by Nathaniel A. Frissell, Fall 2013
    """
    currentData   = getattr(dataObj,dataSet)

    if plotType == 'magnitude':
        xData1        = currentData.freqVec
        yData1        = np.abs(currentData.spectrum)
        yData1_title  = 'Magnitude'
        ylabel        = 'Magnitude'

        xData2        = None
        yData2        = None
        yData2_title  = None

        if xlim == None:
            xlim = (0,np.max(xData1))

        if ylim == None:
            ylim = (0,np.max(yData1))
    elif plotType == 'phase':
        xData1        = currentData.freqVec
        yData1        = np.angle(currentData.spectrum)
        yData1_title  = 'Magnitude'
        ylabel        = 'Phase [rad]'

        xData2        = None
        yData2        = None
        yData2_title  = None

        if xlim == None:
            xlim = (0,np.max(xData1))
    else:
        xData1        = currentData.freqVec
        yData1        = np.real(currentData.spectrum)
        yData1_title  = 'Real Part'
        ylabel        = 'Amplitude'

        xData2      = currentData.freqVec
        yData2      = np.imag(currentData.spectrum)
        yData2_title  = 'Imaginary Part'

        if xlim == None:
            xlim = (np.min(xData1),np.max(xData1))
      
    beams       = currentData.fov.beams
    gates       = currentData.fov.gates

    #Get the time limits.
    timeLim = (np.min(currentData.time),np.max(currentData.time))

    #Get X-Axis title.
    if xlabel == None:
        xlabel = 'Frequency [Hz]'

    if title == None:
        title = []
        title.append('Selected Cells: '+currentData.history[max(currentData.history.keys())]) #Label the plot with the current level of data processing.
        title.append(currentData.metadata['code'][0].upper() + ': ' +
            timeLim[0].strftime('%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M'))
        title = '\n'.join(title)

    multiPlot(xData1,yData1,beams,gates,yData1_title=yData1_title,fig=fig,xlim=xlim,ylim=ylim,xlabel=xlabel,ylabel=ylabel,title=title,
          xData2=xData2,yData2=yData2,yData2_title=yData2_title,xBoundaryLimits=xBoundaryLimits)

    return fig

def multiPlot(xData1,yData1,beams,gates,yData1_title=None,plotBeam=None,plotGate=None,fig=None,xlim=None,ylim=None,xlabel=None,ylabel=None,title=None,
    xData2=None,yData2=None,yData2_title=None,xBoundaryLimits=None):
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
        * **xlabel**:   X-axis label
        * **ylabel**:   Y-axis label
        * **xBoundaryLimits**: 2 Element sequence to shade out portions of the data.  Data outside of this range will be shaded gray,
            Data inside of the range will have a white background.

    **Returns**:
        * **fig**:      matplotlib figure object that was plotted to
    
    Written by Nathaniel A. Frissell, Fall 2013
    """
    if fig == None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=(20,10))

    from matplotlib import dates as md

    #Calculate three default beams and gates to plot.
    if plotBeam == None:
        beamMin = min(beams)
        beamMed = int(np.median(beams))
        beamMax = max(beams)

        plotBeam     = np.array([beamMin,beamMed,beamMax])

    if plotGate == None:
        gateMin = min(gates)
        gateMed = int(np.median(gates))
        gateMax = max(gates)

        plotGate     = np.array([gateMin,gateMed,gateMax])

    #Put things in the correct order.  Gates need to be backwards.
    plotBeam.sort()
    plotGate.sort()
    plotGate = plotGate[::-1] #Reverse the order.

    #Determine the indices of the beams and gates.
    plotBeamInx = []
    for item in plotBeam:
        plotBeamInx.append(int(np.where(beams == item)[0]))

    plotGateInx = []
    for item in plotGate:
        plotGateInx.append(int(np.where(gates == item)[0]))

    plotBeamInx = np.array(plotBeamInx)
    plotGateInx = np.array(plotGateInx)

    nCols = len(plotBeam)
    nRows = len(plotGate)

    #Define x-axis range
    if xlim == None:
        tmpLim = []
        tmpLim.append(min(xData1))
        tmpLim.append(max(xData1))
        if xData2 != None:
            tmpLim.append(min(xData2))
            tmpLim.append(max(xData2))
        xlim = (min(tmpLim),max(tmpLim))

    #Autorange y-axis... make all plots have the same range.
    data = []
    if ylim == None:
        for rg,rgInx in zip(plotGate,plotGateInx):
            for bm,bmInx in zip(plotBeam,plotBeamInx):
                for item in yData1[:,bmInx,rgInx]:
                    data.append(item)
                if yData2 != None:
                    for item in yData2[:,bmInx,rgInx]:
                        data.append(item)

        mx  = np.nanmax(data)
        mn  = np.nanmin(data)
       
        if np.logical_and(mx > 0,mn >= -0.001):
            ylim = (0,mx)
        elif np.logical_and(mn < 0, mx <= 0.001):
            ylim = (mn,0)
        elif abs(mx) >= abs(mn):
            ylim = (-mx,mx)
        elif abs(mn) > abs(mx):
            ylim = (-abs(mn),abs(mn))

    ii = 1
    for rg,rgInx in zip(plotGate,plotGateInx):
        for bm,bmInx in zip(plotBeam,plotBeamInx):
            axis = fig.add_subplot(nCols,nRows,ii)
            l1, = axis.plot(xData1,yData1[:,bmInx,rgInx],label=yData1_title)

            if yData2 != None:
                l2, = axis.plot(xData2,yData2[:,bmInx,rgInx],label=yData2_title)

            #Set axis limits.
            axis.set_xlim(xlim)
            axis.set_ylim(ylim)

            #Special handling for time axes.
            if xlabel == 'UT': 
                axis.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))

                labels = axis.get_xticklabels()
                for label in labels:
                    label.set_rotation(30)

            #Gray out area outside of the boundary.
            if xBoundaryLimits != None:
                gray = '0.75'
                axis.axvspan(xlim[0],xBoundaryLimits[0],color=gray)
                axis.axvspan(xBoundaryLimits[1],xlim[1],color=gray)
                axis.axvline(x=xBoundaryLimits[0],color='g',ls='--',lw=2)
                axis.axvline(x=xBoundaryLimits[1],color='g',ls='--',lw=2)

            text = 'Beam: %i, Gate: %i' % (bm, rg)
            axis.text(0.02,0.92,text,transform=axis.transAxes)

            #Only the first column gets labels.
            if ii % nCols == 1:
                axis.set_ylabel(ylabel)

            #Only have the last row have time ticks
            if ii <= (nRows-1)*nCols:
                axis.xaxis.set_visible(False)
            else:
                axis.set_xlabel(xlabel)

            ii = ii+1

    if yData1_title != None and yData2_title != None:
        fig.legend((l1,l2),(yData1_title,yData2_title),loc=(0.55,0.92))

    if title != None:
        fig.text(0.12,0.92,title,size=24)

    return fig

def plotFullSpectrum(dataObj,dataSet='active',fig=None,xlim=None):
    if fig == None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=(20,10))

    from scipy import stats

    currentData = getDataSet(dataObj,dataSet)

    nrFreqs,nrBeams,nrGates = np.shape(currentData.spectrum)

    if xlim == None:
        posFreqInx  = np.where(currentData.freqVec >= 0)[0]
    else:
        posFreqInx  = np.where(np.logical_and(currentData.freqVec >= xlim[0],currentData.freqVec <= xlim[1]))[0]

    posFreqVec  = currentData.freqVec[posFreqInx]
    npf         = len(posFreqVec) #Number of positive frequencies

    data        = np.abs(currentData.spectrum[posFreqInx,:,:]) #Use the magnitude of the positive frequency data.

    #Determine scale for colorbar.
    sd          = stats.nanstd(data,axis=None)
    mean        = stats.nanmean(data,axis=None)
    scMax       = mean + 2.*sd
    scale       = scMax*np.array([0,1.])

    nXBins      = nrBeams * npf #number of bins we are going to plot

    #Average Power Spectral Density
    avg_psd = np.zeros(npf)
    for x in range(npf): avg_psd[x] = np.mean(data[x,:,:])

    #Do plotting here!
    axis = fig.add_subplot(111)

    verts   = []
    scan    = []
    #Plot Spectrum
    sep     = 0.1
    for ff in range(npf):
        for bb in range(nrBeams):
            xx0      = nrBeams*(ff + 0.5*sep) + bb*(1-sep)
            xx1      = xx0 + (1-sep)
            for gg in range(nrGates):
                scan.append(data[ff,bb,gg])

                yy0  = gg
                yy1  = gg + 1

                x1,y1 = xx0, yy0
                x2,y2 = xx1, yy0
                x3,y3 = xx1, yy1
                x4,y4 = xx0, yy1
                verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

    colors  = 'lasse'
    if scale == None:
        scale   = (np.min(scan),np.max(scan))
    param = 'power'
    cmap = matplotlib.cm.Blues_r

    bounds  = np.linspace(scale[0],scale[1],256)
    norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)

    pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    #Colorbar
    cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
    cbar.set_label('ABS(Spectral Density)')
    if currentData.metadata.has_key('gscat'):
        if currentData.metadata['gscat'] == 1:
            cbar.ax.text(0.5,-0.075,'Ground\nscat\nonly',ha='center')

    #Plot average values.
    verts   = []
    scan    = []
    yy0      = nrGates
    yy1      = nrGates + 1
    for ff in range(npf):
        scan.append(avg_psd[ff])

        xx0      = nrBeams*(ff + 0.5*sep)
        xx1      = xx0 + nrBeams*(1-sep)

        x1,y1 = xx0, yy0
        x2,y2 = xx1, yy0
        x3,y3 = xx1, yy1
        x4,y4 = xx0, yy1

        verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

    param = 'power'
    cmap = matplotlib.cm.winter
    norm = matplotlib.colors.Normalize(vmin = 0, vmax = np.max(avg_psd))
    pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    #Mark maximum PSD column.
    maxInx = np.argmax(avg_psd)
    xx0      = nrBeams*(maxInx + 0.5*sep)
    xx1      = xx0 + nrBeams*(1-sep)

    x1,y1 = xx0, yy0
    x2,y2 = xx1, yy0
    x3,y3 = xx1, yy1
    x4,y4 = xx0, yy1
    mkv = np.array([[x1,y1],[x2,y2],[x3,y3],[x4,y4],[x1,y1]])
    poly = Polygon(mkv,facecolor='Red',edgecolor='none',zorder=100)
    axis.add_patch(poly)

    #X-Labels
    maxXTicks = 10.
    modX      = np.ceil(npf / maxXTicks)
    fCharSize= 0.60

    xlabels = []
    xpos    = []
    for ff in range(npf-1):
        if (ff % modX) != 0: continue
        freqLabel = '%.2f'  % (posFreqVec[ff]*1000.)
        if posFreqVec[ff] == 0:
            periodLabel = 'Inf'
        else:
            periodLabel = '%i' % (1./posFreqVec[ff] / 60.)
        xlabels.append(freqLabel+'\n'+periodLabel)
        xpos.append(nrBeams* (ff + 0.1))

    xlabels.append('freq [mHz]\nPer. [min]')
    xpos.append(nrBeams* (npf-1 + 0.1))

    axis.set_xticks(xpos)
    axis.set_xticklabels(xlabels,ha='left')

    #Y-Labels
    maxYTicks       = 10.
    modY            = np.ceil(nrGates/maxYTicks)

    ylabels = []
    ypos    = []
    for gg in range(nrGates):
        if (gg % modY) != 0: continue
        ylabels.append('%i' % currentData.fov.gates[gg])
        ypos.append(gg+0.5)
        
    ylabels.append('Norm\nAvg\PSD') 
    ypos.append(nrGates+0.5)
    axis.set_yticks(ypos)
    axis.set_yticklabels(ylabels)
    axis.set_ylabel('Range Gate')

    for ff in range(npf):
        axis.axvline(x=ff*nrBeams,color='k',lw=2)

#    axis.set_xlim([0,nXBins])
    axis.set_ylim([0,nrGates+1])

    xpos = 0.130
    fig.text(xpos,0.99,'Full Spectrum View',fontsize=20,va='top')
    #Get the time limits.
    timeLim = (np.min(currentData.time),np.max(currentData.time))
    md = currentData.metadata

    #Translate parameter information from short to long form.
    paramDict = getParamDict(md['param'])
    param     = paramDict['param']
    cbarLabel = paramDict['label']

    text = md['name'] + ' ' + param.capitalize() + timeLim[0].strftime(' (%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M)')

    if md.has_key('fir_filter'):
        filt = md['fir_filter']
        if filt[0] == None:
            low = 'None'
        else:
            low = '%.2f' % (1000. * filt[0])
        if filt[1] == None:
            high = 'None'
        else:
            high = '%.2f' % (1000. * filt[1])

        text = text + '\n' + 'Digital Filter: [' + low + ', ' + high + '] mHz'

    fig.text(xpos,0.95,text,fontsize=14,va='top')

def plotDlm(dataObj,dataSet='active',fig=None,type='magnitude'):
    if fig == None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=(20,10))

    import copy
    from scipy import stats

    currentData = getDataSet(dataObj,dataSet)


    data        = np.abs(currentData.Dlm)

    #Determine scale for colorbar.
    sd          = stats.nanstd(data,axis=None)
    mean        = stats.nanmean(data,axis=None)
    scMax       = mean + 4.*sd
    scale       = scMax*np.array([0,1.])

    #Do plotting here!
    axis = fig.add_subplot(111)

    nrL, nrM = np.shape(data)

    verts   = []
    scan    = []
    #Plot Spectrum
    for ll in range(nrL):
        xx0      = ll
        xx1      = ll+1
        for mm in range(nrM):
            scan.append(data[ll,mm])

            yy0  = mm
            yy1  = mm + 1

            x1,y1 = xx0, yy0
            x2,y2 = xx1, yy0
            x3,y3 = xx1, yy1
            x4,y4 = xx0, yy1
            verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

    colors  = 'lasse'
    if scale == None:
        scale   = (np.min(scan),np.max(scan))
    cmap = matplotlib.cm.jet
    bounds  = np.linspace(scale[0],scale[1],256)
    norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)

    pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    #Colorbar
    cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
    cbar.set_label('ABS(Spectral Density)')
    if currentData.metadata.has_key('gscat'):
        if currentData.metadata['gscat'] == 1:
            cbar.ax.text(0.5,-0.075,'Ground\nscat\nonly',ha='center')
    #  labels[-1].set_visible(False)
    axis.set_xlim([0,nrL])
    axis.set_ylim([0,nrM])

    axis.set_xlabel('l')
    axis.set_ylabel('m')

    nrTimes, nrBeams, nrGates = np.shape(currentData.data)
    ticks   = []
    labels  = []
    mod = int(np.floor(nrGates / 10))
    for x in xrange(nrGates):
        if x % mod != 0: continue
        ll = nrBeams*x
        ticks.append(ll)
        txt = '%i\n%i' % (ll, currentData.fov.gates[x])
        labels.append(txt)
      
    ticks.append(nrL)
    xlabels = copy.copy(labels)
    xlabels.append('l\ngate')

    axis.set_xticks(ticks)
    axis.set_xticklabels(xlabels,ha='left')

    ylabels = copy.copy(labels)
    ylabels.append('m\ngate')
    axis.set_yticks(ticks)
    axis.set_yticklabels(ylabels)

    xpos = 0.130
    fig.text(xpos,0.99,'ABS(Cross Spectral Density Matrix Dlm)',fontsize=20,va='top')
    #Get the time limits.
    timeLim = (np.min(currentData.time),np.max(currentData.time))
    md = currentData.metadata

    #Translate parameter information from short to long form.
    paramDict = getParamDict(md['param'])
    param     = paramDict['param']
    cbarLabel = paramDict['label']

    text = md['name'] + ' ' + param.capitalize() + timeLim[0].strftime(' (%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M)')

    if md.has_key('fir_filter'):
        filt = md['fir_filter']
        if filt[0] == None:
            low = 'None'
        else:
            low = '%.2f' % (1000. * filt[0])
        if filt[1] == None:
            high = 'None'
        else:
            high = '%.2f' % (1000. * filt[1])

        text = text + '\n' + 'Digital Filter: [' + low + ', ' + high + '] mHz'

    fig.text(xpos,0.95,text,fontsize=14,va='top')

def plotKarr(dataObj,dataSet='active',fig=None,maxSignals=5):
    if fig == None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=(20,10))

    currentData = getDataSet(dataObj,dataSet)

    #Do plotting here!
    axis = fig.add_subplot(111,aspect='equal')
    plotKarrAxis(dataObj,dataSet=dataSet,axis=axis,maxSignals=maxSignals)

    xpos = 0.130
    fig.text(xpos,0.99,'Horizontal Wave Number',fontsize=20,va='top')
    #Get the time limits.
    timeLim = (np.min(currentData.time),np.max(currentData.time))
    md = currentData.metadata

    #Translate parameter information from short to long form.
    paramDict = getParamDict(md['param'])
    param     = paramDict['param']
    cbarLabel = paramDict['label']

    text = md['name'] + ' ' + param.capitalize() + timeLim[0].strftime(' (%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M)')

    if md.has_key('fir_filter'):
        filt = md['fir_filter']
        if filt[0] == None:
            low = 'None'
        else:
            low = '%.2f' % (1000. * filt[0])
        if filt[1] == None:
            high = 'None'
        else:
            high = '%.2f' % (1000. * filt[1])

        text = text + '\n' + 'Digital Filter: [' + low + ', ' + high + '] mHz'

    fig.text(xpos,0.95,text,fontsize=14,va='top')

def plotKarrDetected(dataObj,dataSet='active',fig=None,type='magnitude',maxSignals=5,roiPlot=True):
if fig == None:
    from matplotlib import pyplot as plt
    fig   = plt.figure(figsize=(20,10))
currentData = getDataSet(dataObj,dataSet)

from scipy import stats
import matplotlib.patheffects as PathEffects

#Do plotting here!
if roiPlot:
    axis = fig.add_subplot(121,aspect='equal')
else:
    axis = fig.add_subplot(111,aspect='equal')

# Page-wide header #############################################################
xpos = 0.130
fig.text(xpos,0.99,'Horizontal Wave Number',fontsize=20,va='top')
#Get the time limits.
timeLim = (np.min(currentData.time),np.max(currentData.time))
md = currentData.metadata

#Translate parameter information from short to long form.
paramDict = getParamDict(md['param'])
param     = paramDict['param']
cbarLabel = paramDict['label']

text = md['name'] + ' ' + param.capitalize() + timeLim[0].strftime(' (%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M)')

if md.has_key('fir_filter'):
    filt = md['fir_filter']
    if filt[0] == None:
        low = 'None'
    else:
        low = '%.2f' % (1000. * filt[0])
    if filt[1] == None:
        high = 'None'
    else:
        high = '%.2f' % (1000. * filt[1])

    text = text + '\n' + 'Digital Filter: [' + low + ', ' + high + '] mHz'

fig.text(xpos,0.95,text,fontsize=14,va='top')
# End Page-wide header #########################################################

plotKarrAxis(dataObj,dataSet=dataSet,axis=axis,maxSignals=maxSignals)

if roiPlot:
    ################################################################################
    #Feature detection...
    data2 = currentData.sigDetect.labels
    nrL, nrM = np.shape(data2)
    scale = [0,data2.max()]

    #Do plotting here!
    axis = fig.add_subplot(122,aspect='equal')
    verts   = []
    scan    = []
    #Plot Spectrum
    for ll in range(nrL-1):
        xx0      = currentData.kxVec[ll]
        xx1      = currentData.kxVec[ll+1]
        for mm in range(nrM-1):
            scan.append(data2[ll,mm])

            yy0  = currentData.kyVec[mm]
            yy1  = currentData.kyVec[mm + 1]

            x1,y1 = xx0, yy0
            x2,y2 = xx1, yy0
            x3,y3 = xx1, yy1
            x4,y4 = xx0, yy1
            verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

    cmap    = matplotlib.cm.jet
    bounds  = np.linspace(scale[0],scale[1],256)
    norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)

    pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    axis.axvline(color='0.82',lw=2,zorder=150)
    axis.axhline(color='0.82',lw=2,zorder=150)

    #Colorbar
    cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
    cbar.set_label('Region of Interest')
    cbar.set_ticks([])

    axis.set_xlim([np.min(currentData.kxVec),np.max(currentData.kxVec)])
    axis.set_ylim([np.min(currentData.kyVec),np.max(currentData.kyVec)])

    # Add wavelength to x/y tick labels ############################################ 
    ticks     = axis.get_xticks()
    newLabels = []
    for x in xrange(len(ticks)):
        tck = ticks[x]
        if tck != 0:
            km = 2*np.pi/tck
            km_txt = '%i' % km
        else:
            km_txt = ''

        rad_txt = '%.2f' % tck
        txt = '\n'.join([rad_txt,km_txt])
        newLabels.append(txt)

    axis.set_xticklabels(newLabels)
    axis.set_xlabel(u'kx [rad]\n$\lambda$ [km]',ha='center')

    ticks     = axis.get_yticks()
    newLabels = []
    for y in xrange(len(ticks)):
        tck = ticks[y]
        if tck != 0:
            km = 2*np.pi/tck
            km_txt = '%i' % km
        else:
            km_txt = ''

        rad_txt = '%.2f' % tck
        txt = '\n'.join([rad_txt,km_txt])
        newLabels.append(txt)
    axis.set_yticklabels(newLabels)
    axis.set_ylabel(u'ky [rad]\n$\lambda$ [km]',va='center')
    # End add wavelength to x/y tick labels ######################################## 

    if hasattr(currentData,'sigDetect'):
        pe = [PathEffects.withStroke(linewidth=3,foreground='w')]
        tmpList = range(currentData.sigDetect.nrSigs)[::-1] #Force list to plot backwards so number 1 is on top!
        for signal in currentData.sigDetect.info:
            if signal['order'] > maxSignals: continue 
            xpos = currentData.kxVec[signal['maxpos'][0]]
            ypos = currentData.kyVec[signal['maxpos'][1]]
            txt  = '%i' % signal['order']
            axis.text(xpos,ypos,txt,color='k',zorder=200-signal['order'],size=24,path_effects=pe)

def plotKarrAxis(dataObj,dataSet='active',axis=None,maxSignals=5):
    if axis == None: return
    fig = axis.get_figure()
    from scipy import stats
    import matplotlib.patheffects as PathEffects

    currentData = getDataSet(dataObj,dataSet)

    data        = np.abs(currentData.karr) - np.min(np.abs(currentData.karr))
    #Determine scale for colorbar.
    sd          = stats.nanstd(data,axis=None)
    mean        = stats.nanmean(data,axis=None)
    scMax       = mean + 6.5*sd

    data = data / scMax
    scale       = [0.,1.]

    nrL, nrM = np.shape(data)
    verts   = []
    scan    = []
    #Plot Spectrum
    for ll in range(nrL-1):
        xx0      = currentData.kxVec[ll]
        xx1      = currentData.kxVec[ll+1]
        for mm in range(nrM-1):
            scan.append(data[ll,mm])

            yy0  = currentData.kyVec[mm]
            yy1  = currentData.kyVec[mm + 1]

            x1,y1 = xx0, yy0
            x2,y2 = xx1, yy0
            x3,y3 = xx1, yy1
            x4,y4 = xx0, yy1
            verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

    cmap = matplotlib.cm.jet
    bounds  = np.linspace(scale[0],scale[1],256)
    norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)

    pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    ################################################################################
    #Annotations
    axis.axvline(color='0.82',lw=2,zorder=150)
    axis.axhline(color='0.82',lw=2,zorder=150)

    #Colorbar
    cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
    cbar.set_label('ABS(Spectral Density)')
    cbar.set_ticks(np.arange(10)/10.)
    if currentData.metadata.has_key('gscat'):
        if currentData.metadata['gscat'] == 1:
            cbar.ax.text(0.5,-0.075,'Ground\nscat\nonly',ha='center')

    axis.set_xlim([np.min(currentData.kxVec),np.max(currentData.kxVec)])
    axis.set_ylim([np.min(currentData.kyVec),np.max(currentData.kyVec)])

    # Add wavelength to x/y tick labels ############################################ 
    ticks     = axis.get_xticks()
    newLabels = []
    for x in xrange(len(ticks)):
        tck = ticks[x]
        if tck != 0:
            km = 2*np.pi/tck
            km_txt = '%i' % km
        else:
            km_txt = ''

        rad_txt = '%.2f' % tck
        txt = '\n'.join([rad_txt,km_txt])
        newLabels.append(txt)

    axis.set_xticklabels(newLabels)
    axis.set_xlabel(u'kx [rad]\n$\lambda$ [km]',ha='center')

    ticks     = axis.get_yticks()
    newLabels = []
    for y in xrange(len(ticks)):
        tck = ticks[y]
        if tck != 0:
            km = 2*np.pi/tck
            km_txt = '%i' % km
        else:
            km_txt = ''

        rad_txt = '%.2f' % tck
        txt = '\n'.join([rad_txt,km_txt])
        newLabels.append(txt)
    axis.set_yticklabels(newLabels)
    axis.set_ylabel(u'ky [rad]\n$\lambda$ [km]',va='center')
    # End add wavelength to x/y tick labels ######################################## 

    md = currentData.metadata

    #Translate parameter information from short to long form.
    paramDict = getParamDict(md['param'])
    param     = paramDict['param']
    cbarLabel = paramDict['label']

    if hasattr(currentData,'sigDetect'):
        pe = [PathEffects.withStroke(linewidth=3,foreground='w')]
        for signal in currentData.sigDetect.info:
            if signal['order'] > maxSignals: continue 
            xpos = currentData.kxVec[signal['maxpos'][0]]
            ypos = currentData.kyVec[signal['maxpos'][1]]
            txt  = '%i' % signal['order']
            axis.text(xpos,ypos,txt,color='k',zorder=200-signal['order'],size=24,path_effects=pe)
