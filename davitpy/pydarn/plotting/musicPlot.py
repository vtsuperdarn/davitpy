# -*- coding: utf-8 -*-
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

"""musicPlot module

A module for plotting objects created and processed with the pydarn.proc.music module.

Notes
-----

    Please see the pydarn.proc.music module documentation and the iPython notebooks included in the docs
    folder of the DaViTPy distribution.

Module author: Nathaniel A. Frissell, Fall 2013

Functions
--------------------------------------------------
daynight_terminator Calculate day/night terminator
plotRelativeRanges  cell distances
rangeBeamPlot       range versus beam
timeSeriesMultiPlot time series
spectrumMultiPlot   1D line spectral data
multiPlot           time series or spectral data
plotFullSpectrum    full spectrum of musicArray
plotDlm             cross spectral matrix
plotKarr            horizontal wave number
plotKarrDetected    add in use of detectSignals()
plotKarrAxis        Karr plot without titles
--------------------------------------------------

Classes
---------------------------------------
musicFan    fan plot of musicArray data
musicRTI    RTI plot of musicArray data
---------------------------------------

"""
import numpy as np
import scipy as sp
import datetime

from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon
from matplotlib import dates as md
import matplotlib

from mpl_toolkits.basemap import Basemap

from davitpy import utils
from davitpy.pydarn.radar.radUtils import getParamDict

from davitpy.pydarn.proc.music import getDataSet

import logging

#Global Figure Size
figsize=(20,10)

def daynight_terminator(date, lons):
    """Calculates the latitude, Greenwich Hour Angle, and solar 
    declination from a given latitude and longitude.

    This routine is used by musicRTI for terminator calculations.

    Parameters
    ----------
    date : datetime.datetime
        UT date and time of terminator calculation.
    lons : np.array
        Longitudes of which to calculate the terminator.

    Returns
    -------
    lats : np.array
        Latitudes of solar terminator.
    tau : np.array
        Greenwhich Hour Angle.
    dec : np.array
        Solar declination.

    Notes
    -----
    Adapted from mpl_toolkits.basemap.solar by Nathaniel A. Frissell, Fall 2013

    """
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
    """Class to plot a fan plot using a pydarn.proc.music.musicArray object as the data source.

    Parameters
    ----------
    dataObj : pydarn.proc.music.musicArray
        musicArray object
    dataSet : Optional[str]
        Which dataSet in the musicArray object to plot
    time : Optional[None or datetime.datetime]
        Time scan plot.  If None, the first time in dataSet will be used.
    axis : Optional[None or matplotlib.figure.axis]
        Matplotlib axis on which to plot.  If None, a new figure and axis will be created.
    scale : Optional[None or 2-Element iterable]
        Colorbar scale.  If None, the default scale for the current SuperDARN parameter will be used.
    autoScale : Optional[bool]
        If True, automatically scale the color bar for good data visualization. Keyword scale must
        be None when using autoScale.
    plotZeros : Optional[bool]
        If True, plot cells that are exactly 0.
    markCell : Optional[None or 2-Element iterable]
        Mark the (beam, rangeGate) with black.
    markBeam : Optional[None or int]
        Mark a chosen beam.
    markBeam_dict : Optional[dict]
        dictionary of keywords defining markBeam line properties.
    plotTerminator : Optional[bool]
        If True, overlay day/night terminator on map.  Uses Basemap's nightshade.
    plot_title : Optional[bool]
        If True, plot the title information
    title : Optional[str]
        Overide default title text.
    parallels_ticks : Optional[list]
        Where to draw the parallel (latitude) lines
    meridians_ticks : Optional[list]
        Where to draw the meridian (longitude) lines
    zoom : Optional[float]
        Multiply the map height and width by this factor (bigger number shows more area).
    lat_shift : Optional[float]
        Add this number to the computed lat_0 sent to basemap.
    lon_shift : Optional[float]
        Add this number to the computed lon_0 sent to basemap.
    cmap_handling : Optional[str]
        'superdarn' to use SuperDARN-style colorbars, 'matplotlib' for direct use of matplotlib's colorbars.
        'matplotlib' is recommended when using custom scales and the 'superdarn' mode is not providing a desirable result.
    cmap : Optional[one or matplotlib colormap object]
        If Nonei and cmap_handling=='matplotlib', use jet.
    plot_cbar : Optional[bool]
        If True, plot the color bar.
    cbar_ticks : Optional[list]
        Where to put the ticks on the color bar.
    cbar_shrink : Optional[float]
        Fraction by which to shrink the colorbar
    cbar_fraction : Optional[float]
        Fraction of original axes to use for colorbar
    cbar_gstext_offset : Optional[float]
        y-offset from colorbar of "Ground Scatter Only" text
    cbar_gstext_fontsize : Optional[float]
        Fontsize of "Ground Scatter Only" text
    model_text_size : Optional[int]
        fontsize of model and coordinate indicator text
    draw_coastlines : Optional[bool]
        If True, draw the coastlines.
    basemap_dict : Optional[dict]
        Dictionary of keywords sent to the basemap invocation
    **kwArgs
        Keyword Arguments


    Attributes
    ----------
    map_obj

    pcoll

    Written by Nathaniel A. Frissell, Fall 2013

    """
    def __init__(self,dataObject,
        dataSet                 = 'active',
        time                    = None,
        axis                    = None,
        scale                   = None,
        autoScale               = False,
        plotZeros               = False,
        markCell                = None,
        markBeam                = None,
        markBeam_dict           = {'color':'white','lw':2},
        plotTerminator          = True,
        parallels_ticks         = None,
        meridians_ticks         = None,
        zoom                    = 1.,
        lat_shift               = 0.,
        lon_shift               = 0.,
        cmap_handling           = 'superdarn',
        cmap                    = None,
        plot_cbar               = True,
        cbar_ticks              = None,
        cbar_shrink             = 1.0,
        cbar_fraction           = 0.15,
        cbar_gstext_offset      = -0.075,
        cbar_gstext_fontsize    = None,
        model_text_size         = 'small',
        draw_coastlines         = True,
        basemap_dict            = {},
        plot_title              = True,
        title                   = None,
        **kwArgs):

        if axis is None:
            from matplotlib import pyplot as plt
            fig   = plt.figure(figsize=figsize)

        from scipy import stats

        # Make some variables easier to get to...
        currentData = getDataSet(dataObject,dataSet)
        metadata    = currentData.metadata
        latFull     = currentData.fov.latFull
        lonFull     = currentData.fov.lonFull

        coords      = metadata['coords']

        # Translate parameter information from short to long form.
        paramDict = getParamDict(metadata['param'])
        if paramDict.has_key('label'):
            param     = paramDict['param']
            cbarLabel = paramDict['label']
        else:
            param = 'width' # Set param = 'width' at this point just to not screw up the colorbar function.
            cbarLabel = metadata['param']

        # Set colorbar scale if not explicitly defined.
        if(scale is None):
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

        # See if an axis is provided... if not, set one up!
        if axis is None:
            axis  = fig.add_subplot(111)
        else:
            fig   = axis.get_figure()

        # Figure out which scan we are going to plot...
        if time is None:
            timeInx = 0
        else:
            timeInx = (np.where(currentData.time >= time))[0]
            if np.size(timeInx) == 0:
                timeInx = -1
            else:
                timeInx = int(np.min(timeInx))

        # do some stuff in map projection coords to get necessary width and height of map
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
        lon_0 = np.mean(goodLonFull)
        dist = width/50.


        # Fill the entire subplot area without changing the data aspect ratio.
        bbox        = axis.get_window_extent()
        bbox_width  = bbox.width
        bbox_height = bbox.height
        ax_aspect   = bbox_width / bbox_height
        map_aspect  = width / height
        if map_aspect < ax_aspect:
            width   = (height*bbox_width) / bbox_height

        if map_aspect > ax_aspect:
            height  = (width*bbox_height) / bbox_width

        # Zoom!
        width       = zoom * width
        height      = zoom * height
        lat_0       = lat_0 + lat_shift
        lon_0       = lon_0 + lon_shift

        bmd         = basemap_dict.copy()
        width       = bmd.pop('width',  width)
        height      = bmd.pop('height', height)
        lat_0       = bmd.pop('lat_0',  lat_0)
        lon_0       = bmd.pop('lon_0',  lon_0)

        # draw the actual map we want
        m = Basemap(projection='stere',width=width,height=height,lon_0=lon_0,lat_0=lat_0,ax=axis,**bmd)
        if parallels_ticks is None:
            parallels_ticks = np.arange(-80.,81.,10.)

        if meridians_ticks is None:
            meridians_ticks = np.arange(-180.,181.,20.)

        m.drawparallels(parallels_ticks,labels=[1,0,0,0])
        m.drawmeridians(meridians_ticks,labels=[0,0,0,1])

        if(coords == 'geo') and draw_coastlines == True:
            m.drawcoastlines(linewidth=0.5,color='k')
            m.drawmapboundary(fill_color='w')
            m.fillcontinents(color='w', lake_color='w')

        # Plot the SuperDARN data!
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

        if (cmap_handling == 'matplotlib') or autoScale:
            if cmap is None:
                cmap    = matplotlib.cm.jet
            bounds  = np.linspace(scale[0],scale[1],256)
            norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)
        elif cmap_handling == 'superdarn':
            colors  = 'lasse'
            cmap,norm,bounds = utils.plotUtils.genCmap(param,scale,colors=colors)

#        pcoll = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
        pcoll = PolyCollection(np.array(verts),edgecolors='face',closed=False,cmap=cmap,norm=norm,zorder=99)
        pcoll.set_array(np.array(scan))
        axis.add_collection(pcoll,autolim=False)

        # Mark Cell
        if markCell is not None:
            beamInx = int(np.where(currentData.fov.beams == markCell[0])[0])
            gateInx = int(np.where(currentData.fov.gates == markCell[1])[0])

            x1,y1 = m(lonFull[beamInx+0,gateInx+0],latFull[beamInx+0,gateInx+0])
            x2,y2 = m(lonFull[beamInx+1,gateInx+0],latFull[beamInx+1,gateInx+0])
            x3,y3 = m(lonFull[beamInx+1,gateInx+1],latFull[beamInx+1,gateInx+1])
            x4,y4 = m(lonFull[beamInx+0,gateInx+1],latFull[beamInx+0,gateInx+1])

            mkv = np.array([[x1,y1],[x2,y2],[x3,y3],[x4,y4],[x1,y1]])

            poly = Polygon(mkv,facecolor='#000000',edgecolor='none',zorder=100)
            axis.add_patch(poly)

        # Mark Beam
        if markBeam is not None:
            beamInx = int(np.where(currentData.fov.beams == markBeam)[0])
            startedMarking = False
            for gateInx in range(ngates):
                if goodLatLon[beamInx,gateInx] == False: continue
                x1,y1 = m(lonFull[beamInx+0,gateInx+0],latFull[beamInx+0,gateInx+0])
                x2,y2 = m(lonFull[beamInx+1,gateInx+0],latFull[beamInx+1,gateInx+0])
                x3,y3 = m(lonFull[beamInx+1,gateInx+1],latFull[beamInx+1,gateInx+1])
                x4,y4 = m(lonFull[beamInx+0,gateInx+1],latFull[beamInx+0,gateInx+1])
                axis.plot([x1,x4],[y1,y4],zorder=150,**markBeam_dict)
                axis.plot([x2,x3],[y2,y3],zorder=150,**markBeam_dict)
                if not startedMarking:
                    axis.plot([x1,x2],[y1,y2],zorder=150,**markBeam_dict)
                    startedMarking = True
                if gateInx == ngates-1:
                    axis.plot([x3,x4],[y3,y4],zorder=150,**markBeam_dict)


        dataName = currentData.history[max(currentData.history.keys())] # Label the plot with the current level of data processing.
        if plot_title:
            if title is None:
                axis.set_title(metadata['name']+' - '+dataName+currentData.time[timeInx].strftime('\n%Y %b %d %H%M UT')) 
            else:
                axis.set_title(title)

        if plot_cbar:
            cbar = fig.colorbar(pcoll,orientation='vertical',shrink=cbar_shrink,fraction=cbar_fraction)
            cbar.set_label(cbarLabel)
            if cbar_ticks is None:
                labels = cbar.ax.get_yticklabels()
                labels[-1].set_visible(False)
            else:
                cbar.set_ticks(cbar_ticks)

            if currentData.metadata.has_key('gscat'):
                if currentData.metadata['gscat'] == 1:
                    cbar.ax.text(0.5,cbar_gstext_offset,'Ground\nscat\nonly',ha='center',fontsize=cbar_gstext_fontsize)

        txt = 'Coordinates: ' + metadata['coords'] +', Model: ' + metadata['model']
        axis.text(1.01, 0, txt,
                  horizontalalignment='left',
                  verticalalignment='bottom',
                  rotation='vertical',
                  size=model_text_size,
                  transform=axis.transAxes)

        if plotTerminator:
            m.nightshade(currentData.time[timeInx])

        self.map_obj    = m
        self.pcoll      = pcoll

class musicRTI(object):
    """Class to create an RTI plot using a pydarn.proc.music.musicArray object as the data source.

    Parameters
    ----------
    dataObj : pydarn.proc.music.musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to plot
    beam : Optional[int]
        Beam number to plot.
    xlim : Optoinal[None or 2-element iterable of datetime.datetime]
        Limits for x-axis.
    ylim : Optional[None or 2-element iterable of floats]
        Limits for y-axis.
    axis : Optional[None or matplotlib.figure.axis]
        Matplotlib axis on which to plot.  If None, a new figure and axis will be created.
    scale : Optional[None or 2-Element iterable]
        Colorbar scale.  If None, the default scale for the current SuperDARN parameter will be used.
    plotZeros : Optional[bool]
        If True, plot data cells that are identically zero.
    max_sounding_time : Optional[None or datetime.timedelta]
        Do not allow data to be plotted for longer than this duration.
    xBoundaryLimits: Optional[None or 2-element iterable of datetime.datetime]
        Mark a region of times on the RTI plot.  A green dashed vertical line will be plotted
        at each of the boundary times.  The region of time outside of the boundary will be shaded gray.
        If set to None, this will automatically be set to the timeLimits set in the metadata, if they exist.
    yBoundaryLimits : Optional[None or 2-element iterable of floats]
        Mark a region of range on the RTI plot.  A green dashed horizontal line will be plotted
        at each of the boundary ranges.  The region of time outside of the boundary will be shaded gray.
        If set to None, this will automatically be set to the gateLimits set in the metadata, if they exist.
    yticks : Optional[list]
        Where to put the ticks on the y-axis.
    ytick_lat_format : Optional[str]
         %-style string format code for latitude y-tick labels
    autoScale : Optional[bool]
        If True, automatically scale the color bar for good data visualization. Keyword scale must be None when using autoScale.
        ax.set_xlim(xlim)
    plotTerminator : Optional[bool]
        If True, overlay day/night terminator on the RTI plot.  Every cell is evaluated for day/night and shaded accordingly.  Therefore,
        terminator resolution will match the resolution of the RTI plot data.
    axvlines : Optional[None or list of datetime.datetime]
        Dashed vertical lines will be drawn at each specified datetime.datetime.
    axvline_color : Optional[str]
        Matplotlib color code specifying color of the axvlines.
    secondary_coords : Optional[str]
        Secondary coordate system for RTI plot y-axis ('lat' or 'range')
    plot_info : Optional[bool]
        If True, plot frequency/noise plots
    plot_title : Optional[bool]
        If True, plot the title information
    plot_range_limits_label : Optoinal[bool]
        If True, plot the label corresponding to the range limits on the right-hand y-axis.
    cmap_handling : Optional[str]
        'superdarn' to use SuperDARN-style colorbars, 'matplotlib' for direct use of matplotlib's colorbars.
        'matplotlib' is recommended when using custom scales and the 'superdarn' mode is not providing a desirable result.
    plot_cbar : Optional[bool]
        If True, plot the color bar.
    cbar_ticks : Optional[list]
        Where to put the ticks on the color bar.
    cbar_shrink : Optional[float]
        fraction by which to shrink the colorbar
    cbar_fraction : Optional[float]
        fraction of original axes to use for colorbar
    cbar_gstext_offset : Optional[float]
        y-offset from colorbar of "Ground Scatter Only" text
    cbar_gstext_fontsize : Optional[float]
        fontsize of "Ground Scatter Only" text
    model_text_size : Optional[int]
        fontsize of model and coordinate indicator text
    **kwArgs :
        Keyword Arguments

    Attributes
    ----------
    cbar_info : list


    Written by Nathaniel A. Frissell, Fall 2013

    """
    def __init__(self,dataObject,
        dataSet                 = 'active',
        beam                    = 7,
        coords                  = 'gate',
        xlim                    = None,
        ylim                    = None,
        axis                    = None,
        scale                   = None,
        plotZeros               = False, 
        max_sounding_time       = datetime.timedelta(minutes=4),
        xBoundaryLimits         = None,
        yBoundaryLimits         = None,
        yticks                  = None,
        ytick_lat_format        = '.0f',
        autoScale               = False,
        plotTerminator          = True,
        axvlines                = None, 
        axvline_color           = '0.25',
        secondary_coords        = 'lat',
        plot_info               = True,
        plot_title              = True,
        plot_range_limits_label = True,
        cmap_handling           = 'superdarn',
        cmap                    = None,
        bounds                  = None,
        norm                    = None,
        plot_cbar               = True,
        cbar_ticks              = None,
        cbar_shrink             = 1.0,
        cbar_fraction           = 0.15,
        cbar_gstext_offset      = -0.075,
        cbar_gstext_fontsize    = None,
        model_text_size         = 'small',
        y_labelpad              = None,
        **kwArgs):

        from scipy import stats
        from rti import plot_freq,plot_nave,plot_skynoise,plot_searchnoise

        if axis is None:
            from matplotlib import pyplot as plt
            fig   = plt.figure(figsize=figsize)

        # Make some variables easier to get to...
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

        # Translate parameter information from short to long form.
        paramDict = getParamDict(metadata['param'])
        if paramDict.has_key('label'):
            param     = paramDict['param']
            cbarLabel = paramDict['label']
        else:
            param = 'width' # Set param = 'width' at this point just to not screw up the colorbar function.
            cbarLabel = metadata['param']

        # Set colorbar scale if not explicitly defined.
        if(scale is None):
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

        # See if an axis is provided... if not, set one up!
        if axis is None:
            axis    = fig.add_subplot(111)
        else:
            fig   = axis.get_figure()

        if np.size(beamInx) == 0:
            beamInx = 0
            beam    = currentData.fov.beams[0]

        # Plot the SuperDARN data!
        verts = []
        scan  = []
        data  = np.squeeze(currentData.data[:,beamInx,:])

#        The coords keyword needs to be tested better.  For now, just allow 'gate' only.
#        Even in 'gate' mode, the geographic latitudes are plotted along with gate.
#        if coords is None and metadata.has_key('coords'):
#            coords      = metadata['coords']
#
        if coords not in ['gate','range']:
            logging.warning('Coords "%s" not supported for RTI plots.  Using "gate".' % coords)
            coords = 'gate'

        if coords == 'gate':
            rnge  = currentData.fov.gates
        elif coords == 'range':
            rnge  = currentData.fov.slantRFull[beam,:]

        xvec  = [matplotlib.dates.date2num(x) for x in currentData.time]
        for tm in range(nrTimes-1):
            for rg in range(nrGates-1):
                if np.isnan(data[tm,rg]): continue
                if data[tm,rg] == 0 and not plotZeros: continue
                if max_sounding_time is not None:
                    if (currentData.time[tm+1] - currentData.time[tm+0]) > max_sounding_time: continue
                scan.append(data[tm,rg])

                x1,y1 = xvec[tm+0],rnge[rg+0]
                x2,y2 = xvec[tm+1],rnge[rg+0]
                x3,y3 = xvec[tm+1],rnge[rg+1]
                x4,y4 = xvec[tm+0],rnge[rg+1]
                verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

        if (cmap_handling == 'matplotlib') or autoScale:
            if cmap is None:
                cmap = matplotlib.cm.jet
            if bounds is None:
                bounds  = np.linspace(scale[0],scale[1],256)
            if norm is None:
                norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)
        elif cmap_handling == 'superdarn':
            colors  = 'lasse'
            cmap,norm,bounds = utils.plotUtils.genCmap(param,scale,colors=colors)

        pcoll = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
        pcoll.set_array(np.array(scan))
        axis.add_collection(pcoll,autolim=False)

        # Plot the terminator! #########################################################
        if plotTerminator:
#            print 'Terminator functionality is disabled until further testing is completed.'
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

        if xlim is None:
            xlim = (np.min(time),np.max(time))
        axis.set_xlim(xlim)

        axis.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        axis.set_xlabel('Time [UT]')

        if ylim is None:
            ylim = (np.min(rnge),np.max(rnge))
        axis.set_ylim(ylim)

        if yticks is not None:
            axis.set_yticks(yticks)

        # Y-axis labeling ##############################################################
        if coords == 'gate':
            if secondary_coords:
                if secondary_coords == 'range':
                    if metadata['model'] == 'IS':
                        axis.set_ylabel('Range Gate\nSlant Range [km]',labelpad=y_labelpad)
                    elif metadata['model'] == 'GS':
                        axis.set_ylabel('Range Gate\nGS Mapped Range [km]',labelpad=y_labelpad)
                else:
                    geo_mag = 'Geographic' if currentData.fov.coords == 'geo' else 'Magnetic'
                    if metadata['model'] == 'IS':
                        axis.set_ylabel('Range Gate\n%s Latitude' % geo_mag,labelpad=y_labelpad)
                    elif metadata['model'] == 'GS':
                        axis.set_ylabel('Range Gate\nGS Mapped %s Latitude' % geo_mag,labelpad=y_labelpad)

                yticks  = axis.get_yticks()
                ytick_str    = []
                for tck in yticks:
                    txt = []
                    txt.append('%d' % tck)

                    rg_inx = np.where(tck == currentData.fov.gates)[0]
                    if np.size(rg_inx) != 0:
                        if secondary_coords == 'range':
                            rang = currentData.fov.slantRCenter[beamInx,rg_inx]
                            if np.isfinite(rang): 
                                txt.append('%d' % rang)
                            else:
                                txt.append('')
                        else:
                            lat = currentData.fov.latCenter[beamInx,rg_inx]
                            if np.isfinite(lat): 
                                txt.append((u'%'+ytick_lat_format+'$^o$') % lat)
                            else:
                                txt.append('')
                    txt = '\n'.join(txt)
                    ytick_str.append(txt)
                axis.set_yticklabels(ytick_str,rotation=90,ma='center')
            else:
                axis.set_ylabel('Range Gate',labelpad=y_labelpad)
        elif coords == 'range':
            if secondary_coords == 'lat':
                # Use linear interpolation to get the latitude associated with a particular range.
                # Make sure we only include finite values in the interpolation function.
                finite_inx  = np.where(np.isfinite(currentData.fov.latCenter[beam,:]))[0]
                tmp_ranges  = currentData.fov.slantRCenter[beam,:][finite_inx]
                tmp_lats    = currentData.fov.latCenter[beam,:][finite_inx]
                tmp_fn      = sp.interpolate.interp1d(tmp_ranges,tmp_lats)

                yticks  = axis.get_yticks()
                ytick_str    = []
                for tck in yticks:
                    txt = []

                    # Append Latitude
                    try:
                        lat = tmp_fn(tck)
                        txt.append((u'%'+ytick_lat_format+'$^o$') % lat)
                    except:
                        txt.append('')

                    # Append Range
                    txt.append('%d' % tck)
                    txt = '\n'.join(txt)

                    ytick_str.append(txt) # Put both lat and range on same string
                axis.set_yticklabels(ytick_str,rotation=90,ma='center') # Set yticklabels
                # Label y-axis
                geo_mag = 'Geographic' if currentData.fov.coords == 'geo' else 'Magnetic'
                if metadata['model'] == 'IS':
                    axis.set_ylabel('%s Latitude\nSlant Range [km]' % geo_mag,labelpad=y_labelpad)
                elif metadata['model'] == 'GS':
                    axis.set_ylabel('GS Mapped %s Latitude\nGS Mapped Range [km]' % geo_mag,labelpad=y_labelpad)
            else:
                if metadata['model'] == 'IS':
                    axis.set_ylabel('Slant Range [km]',labelpad=y_labelpad)
                elif metadata['model'] == 'GS':
                    axis.set_ylabel('GS Mapped Range [km]',labelpad=y_labelpad)

        axis.set_ylim(ylim)
        # Shade xBoundary Limits
        if xBoundaryLimits is None:
            if currentData.metadata.has_key('timeLimits'):
                xBoundaryLimits = currentData.metadata['timeLimits']

        if xBoundaryLimits is not None:
            gray = '0.75'
#            axis.axvspan(xlim[0],xBoundaryLimits[0],color=gray,zorder=150,alpha=0.5)
#            axis.axvspan(xBoundaryLimits[1],xlim[1],color=gray,zorder=150,alpha=0.5)
            axis.axvspan(xlim[0],xBoundaryLimits[0],color=gray,zorder=1)
            axis.axvspan(xBoundaryLimits[1],xlim[1],color=gray,zorder=1)
            axis.axvline(x=xBoundaryLimits[0],color='g',ls='--',lw=2,zorder=150)
            axis.axvline(x=xBoundaryLimits[1],color='g',ls='--',lw=2,zorder=150)

        # Shade yBoundary Limits
        if yBoundaryLimits is None:
            if currentData.metadata.has_key('gateLimits') and coords == 'gate':
                yBoundaryLimits = currentData.metadata['gateLimits']

            if currentData.metadata.has_key('rangeLimits') and coords == 'range':
                yBoundaryLimits = currentData.metadata['rangeLimits']

        if yBoundaryLimits is not None:
            gray = '0.75'
#            axis.axhspan(ylim[0],yBoundaryLimits[0],color=gray,zorder=150,alpha=0.5)
#            axis.axhspan(yBoundaryLimits[1],ylim[1],color=gray,zorder=150,alpha=0.5)
            axis.axhspan(ylim[0],yBoundaryLimits[0],color=gray,zorder=1)
            axis.axhspan(yBoundaryLimits[1],ylim[1],color=gray,zorder=1)
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
                if plot_range_limits_label:
                    axis.annotate(txt, (1.01, bnd_item) ,xycoords=('axes fraction','data'),rotation=90,ma='center')

        if plot_cbar:
            cbar = fig.colorbar(pcoll,orientation='vertical',shrink=cbar_shrink,fraction=cbar_fraction)
            cbar.set_label(cbarLabel)
            if cbar_ticks is None:
                labels = cbar.ax.get_yticklabels()
                labels[-1].set_visible(False)
            else:
                cbar.set_ticks(cbar_ticks)

            if currentData.metadata.has_key('gscat'):
                if currentData.metadata['gscat'] == 1:
                    cbar.ax.text(0.5,cbar_gstext_offset,'Ground\nscat\nonly',ha='center',fontsize=cbar_gstext_fontsize)

        txt = 'Model: ' + metadata['model']
        axis.text(1.01, 0, txt,
                horizontalalignment='left',
                verticalalignment='bottom',
                rotation='vertical',
                size=model_text_size,
                transform=axis.transAxes)

        # Get axis position information.
        pos = list(axis.get_position().bounds)

        # Plot frequency and noise information. ######################################## 
        if hasattr(dataObject,'prm') and plot_info:
            # Adjust current plot position to fit in the freq and noise plots.
            super_plot_hgt  = 0.06
            pos[3] = pos[3] - (2*super_plot_hgt)
            axis.set_position(pos)

            # Get current colorbar position and adjust it.
            cbar_pos = list(cbar.ax.get_position().bounds)
            cbar_pos[1] = pos[1]
            cbar_pos[3] = pos[3]
            cbar.ax.set_position(cbar_pos)

            curr_xlim   = axis.get_xlim()
            curr_xticks = axis.get_xticks()

            pos[1]      = pos[1] + pos[3]
            pos[3]      = super_plot_hgt
            freq_pos    = pos[:]

            pos[1]      = pos[1] + super_plot_hgt
            noise_pos   = pos[:]

            skynoise_ax = fig.add_axes(noise_pos, label='sky')
            searchnoise_ax = fig.add_axes(noise_pos, label='search', frameon=False)
            freq_ax = fig.add_axes(freq_pos, label='freq')
            nave_ax = fig.add_axes(freq_pos, label='nave', frameon=False)
#            cpid_ax = fig.add_axes(cpid_pos)
            plot_freq(freq_ax,dataObject.prm.time,dataObject.prm.tfreq,xlim=curr_xlim,xticks=curr_xticks)
            plot_nave(nave_ax,dataObject.prm.time,dataObject.prm.nave,xlim=curr_xlim,xticks=curr_xticks)

            plot_skynoise(skynoise_ax,dataObject.prm.time,dataObject.prm.noisesky,xlim=curr_xlim,xticks=curr_xticks)
            plot_searchnoise(searchnoise_ax,dataObject.prm.time,dataObject.prm.noisesearch,xlim=curr_xlim,xticks=curr_xticks)

        # Put a title on the RTI Plot. #################################################
        if plot_title:
            title_y = (pos[1] + pos[3]) + 0.015
            xmin    = pos[0]
            xmax    = pos[0] + pos[2]

            txt     = metadata['name']+'  ('+metadata['fType']+')'
            fig.text(xmin,title_y,txt,ha='left',weight=550)

            txt     = []
            txt.append(xlim[0].strftime('%Y %b %d %H%M UT - ')+xlim[1].strftime('%Y %b %d %H%M UT'))
            txt.append(currentData.history[max(currentData.history.keys())]) # Label the plot with the current level of data processing.
            txt     = '\n'.join(txt)
            fig.text((xmin+xmax)/2.,title_y,txt,weight=550,size='large',ha='center')

            txt     = 'Beam '+str(beam)
            fig.text(xmax,title_y,txt,weight=550,ha='right')

        cbar_info           = {}
        cbar_info['cmap']   = cmap
        cbar_info['bounds'] = bounds 
        cbar_info['norm']   = norm 
        cbar_info['label']  = cbarLabel
        cbar_info['ticks']  = cbar_ticks
        cbar_info['mappable']  = pcoll
        self.cbar_info      = cbar_info


def plotRelativeRanges(dataObj,dataSet='active',time=None,fig=None):
    """Plots the N-S and E-W distance from the center cell of a field-of-view in a
    pydarn.proc.music.musicArray object.  Also plots one scan of the chosen
    dataSet, with the center cell marked in black.

    Parameters
    ----------
    dataObj : pydarn.proc.music.musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to plot
    time : Optional[None or datetime.datetime]
        Time scan plot.  If None, the first time in dataSet will be used.
    fig : Optional[None of matplotlib.figure]
        matplotlib figure object that will be plotted to.  If not provided, one will be created.

    Returns
    -------
    fig : None of matplotlib.figure
        matplotlib figure object that was plotted to

    Written by Nathaniel A. Frissell, Fall 2013

    """
    if fig is None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=figsize)

    currentData = getDataSet(dataObj,dataSet)

    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    import matplotlib

    # Get center of FOV.
    ctrBeamInx  = currentData.fov.relative_centerInx[0]
    ctrGateInx  = currentData.fov.relative_centerInx[1]
    ctrBeam     = currentData.fov.beams[ctrBeamInx]
    ctrGate     = currentData.fov.gates[ctrGateInx]
    ctrLat      = currentData.fov.latCenter[ctrBeamInx,ctrGateInx]
    ctrLon      = currentData.fov.lonCenter[ctrBeamInx,ctrGateInx]

    gs    = matplotlib.gridspec.GridSpec(3, 2,hspace=None)
    axis  = fig.add_subplot(gs[0:2, 1]) 
    musicFan(dataObj,time=time,plotZeros=True,dataSet=dataSet,axis=axis,markCell=(ctrBeam,ctrGate))

    # Determine the color scale for plotting.
    def myround(x, base=50):
        return int(base * round(float(x)/base))

    absnanmax  = np.nanmax(np.abs([currentData.fov.relative_x,currentData.fov.relative_y]))
    rnd     = myround(absnanmax)
    scale   = (-rnd, rnd)

    # Determine nanmaximum ranges.
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

    Parameters
    ----------
    currentData : pydarn.proc.music.musicDataObj
        musicDataObj
    data : numpy.array
        nBeams x nGates Numpy array of data
    axis : matplotlib.axis
        matplotlib axis object on which to plot
    title : Optional[None or str]
        Title of plot.
    xlabel : Optional[None or str]
        X-axis label
    ylabel : Optional[None or str]
        Y-axis label
    param : Optional[None or str]
        Parameter used for colorbar selection.
    scale : Optional[None or 2-element iterable]
        Two-element colorbar scale.
    cbarLabel : Optional[str]
        Colorbar label.

    Written by Nathaniel A. Frissell, Fall 2013

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

    if scale is None:
        scale   = (np.min(scan),np.max(scan))

    cmap    = matplotlib.cm.jet
    bounds  = np.linspace(scale[0],scale[1],256)
    norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)

    pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    axis.set_xlim(min(currentData.fov.beams), max(currentData.fov.beams)+1)
    axis.set_ylim(min(currentData.fov.gates), max(currentData.fov.gates)+1)

    if title is not None: axis.set_title(title)
    if xlabel is not None: axis.set_xlabel(xlabel)
    if ylabel is not None: axis.set_ylabel(ylabel)

    cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
    if cbarLabel is not None: cbar.set_label(cbarLabel)

def timeSeriesMultiPlot(dataObj,dataSet='active',dataObj2=None,dataSet2=None,plotBeam=None,plotGate=None,fig=None,xlim=None,ylim=None,xlabel=None,ylabel=None,title=None,xBoundaryLimits=None):
    """Plots 1D line time series of selected cells in a pydarn.proc.music.musicArray object.
    This defaults to 9 cells of the FOV.

    Parameters
    ----------
    dataObj : pydarn.proc.music.musicArray
        musicArray object
    dataSet : Optoinal[str]
        which dataSet in the musicArray object to plot
    dataObj2 : Optional[pydarn.proc.music.musicArray]
        A second musicArray object to be overlain on the the first dataObj plot.
    dataSet2 : Optional[str]
        which dataSet in the second musicArray to plot
    plotBeam : Optional[list of int]
        list of beams to plot from
    plotGate : Optional[list of int]
        list of range gates to plot from
    fig : Optional[matplotlib.figure]
        matplotlib figure object that will be plotted to.  If not provided, one will be created.
    xlim : Optional[None or 2-element iterable]
        X-axis limits of all plots
    ylim : Optional[None or 2-element iterable]
        Y-axis limits of all plots
    xlabel : Optional[None or str]
        X-axis label
    ylabel : Optional[None or str]
        Y-axis label
    title : Optional[None or str]
        Title of plot
    xBoundaryLimits : Optional[None or 2-element iterable]
        Element sequence to shade out portions of the data.  Data outside of this range will be shaded gray,
        Data inside of the range will have a white background.  If set to None, this will automatically be set to the timeLimits set
        in the metadata, if they exist.

    Returns
    -------
    fig : matplotlib.figure
        matplotlib figure object that was plotted to

    Written by Nathaniel A. Frissell, Fall 2013

    """
    currentData = getDataSet(dataObj,dataSet)
    xData1      = currentData.time
    yData1      = currentData.data
    beams       = currentData.fov.beams
    gates       = currentData.fov.gates

    if dataObj2 is not None and dataSet2 is None: dataSet2 == 'active'

    if dataSet2 is not None:
        if dataObj2 is not None:
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

    # Define x-axis range
    if xlim is None:
        tmpLim = []
        tmpLim.append(min(xData1))
        tmpLim.append(max(xData1))
        if xData2 is not None:
            tmpLim.append(min(xData2))
            tmpLim.append(max(xData2))
        xlim = (min(tmpLim),max(tmpLim))

    # Set x boundary limits using timeLimits, if they exist.  Account for both dataSet1 and dataSet2, and write it so timeLimits can be any type of sequence.
    if xBoundaryLimits is None:
        tmpLim = []
        if currentData.metadata.has_key('timeLimits'):
            tmpLim.append(currentData.metadata['timeLimits'][0])
            tmpLim.append(currentData.metadata['timeLimits'][1])

        if dataSet2 is not None:
          if currentData2.metadata.has_key('timeLimits'):
            tmpLim.append(currentData2.metadata['timeLimits'][0])
            tmpLim.append(currentData2.metadata['timeLimits'][1])

        if tmpLim != []:
            xBoundaryLimits = (min(tmpLim), max(tmpLim))

    # Get X-Axis title.
    if xlabel is None:
        xlabel = 'UT'

    # Get Y-Axis title.
    paramDict = getParamDict(currentData.metadata['param'])
    if ylabel is None and paramDict.has_key('label'):
        ylabel = paramDict['label']

    yData1_title = currentData.history[max(currentData.history.keys())] # Label the plot with the current level of data processing
    if title is None:
        title = []
        title.append('Selected Cells: '+yData1_title)
        title.append(currentData.metadata['code'][0].upper() + ': ' +
            xlim[0].strftime('%Y %b %d %H:%M - ') + xlim[1].strftime('%Y %b %d %H:%M'))
        title = '\n'.join(title)

    multiPlot(xData1,yData1,beams,gates,yData1_title=yData1_title,fig=fig,xlim=xlim,ylim=ylim,xlabel=xlabel,ylabel=ylabel,title=title,
          xData2=xData2,yData2=yData2,yData2_title=yData2_title,xBoundaryLimits=xBoundaryLimits)

def spectrumMultiPlot(dataObj,dataSet='active',plotType='real_imag',plotBeam=None,plotGate=None,fig=None,xlim=None,ylim=None,xlabel=None,ylabel=None,title=None,xBoundaryLimits=None):
    """Plots 1D line spectral plots of selected cells in a pydarn.proc.music.musicArray object.
    This defaults to 9 cells of the FOV.

    Parameters
    ----------
    dataObj : pydarn.proc.music.musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to plot
    plotType : Optional[str]
        {'real_imag'|'magnitude'|'phase'}
    plotBeam : Optional[list of int]
        list of beams to plot from
    plotGate : Optional[list of int]
        list of range gates to plot from
    fig : Optional[matplotlib.figure]
        matplotlib figure object that will be plotted to.  If not provided, one will be created.
    xlim : Optional[None or 2-element iterable]
        X-axis limits of all plots
    ylim : Optional[None or 2-element iterable]
        Y-axis limits of all plots
    xlabel : Optional[None or str]
        X-axis label
    ylabel : Optional[None or str]
        Y-axis label
    title : Optional[None or str]
        Title of plot
    xBoundaryLimits : Optional[None or 2-element iterable]
        Element sequence to shade out portions of the data.  Data outside of this range will be shaded gray,
        Data inside of the range will have a white background.  If set to None, this will automatically be set to the timeLimits set
        in the metadata, if they exist.

    Returns
    -------
    fig : matplotlib.figure
        matplotlib figure object that was plotted to

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

        if xlim is None:
            xlim = (0,np.max(xData1))

        if ylim is None:
            ylim = (0,np.max(yData1))
    elif plotType == 'phase':
        xData1        = currentData.freqVec
        yData1        = np.angle(currentData.spectrum)
        yData1_title  = 'Magnitude'
        ylabel        = 'Phase [rad]'

        xData2        = None
        yData2        = None
        yData2_title  = None

        if xlim is None:
            xlim = (0,np.max(xData1))
    else:
        xData1        = currentData.freqVec
        yData1        = np.real(currentData.spectrum)
        yData1_title  = 'Real Part'
        ylabel        = 'Amplitude'

        xData2      = currentData.freqVec
        yData2      = np.imag(currentData.spectrum)
        yData2_title  = 'Imaginary Part'

        if xlim is None:
            xlim = (np.min(xData1),np.max(xData1))
      
    beams       = currentData.fov.beams
    gates       = currentData.fov.gates

    # Get the time limits.
    timeLim = (np.min(currentData.time),np.max(currentData.time))

    # Get X-Axis title.
    if xlabel is None:
        xlabel = 'Frequency [Hz]'

    if title is None:
        title = []
        title.append('Selected Cells: '+currentData.history[max(currentData.history.keys())]) # Label the plot with the current level of data processing.
        title.append(currentData.metadata['code'][0].upper() + ': ' +
            timeLim[0].strftime('%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M'))
        title = '\n'.join(title)

    multiPlot(xData1,yData1,beams,gates,yData1_title=yData1_title,fig=fig,xlim=xlim,ylim=ylim,xlabel=xlabel,ylabel=ylabel,title=title,
          xData2=xData2,yData2=yData2,yData2_title=yData2_title,xBoundaryLimits=xBoundaryLimits)

    return fig

def multiPlot(xData1,yData1,beams,gates,yData1_title=None,plotBeam=None,plotGate=None,fig=None,xlim=None,ylim=None,xlabel=None,ylabel=None,title=None,
    xData2=None,yData2=None,yData2_title=None,xBoundaryLimits=None):
    """Plots 1D time series or line spectral plots of selected cells in a 3d-array. Two data sets can be plotted simultaneously for comparison.
    This defaults to 9 cells of the 3d-array.

    Parameters
    ----------
    xData1 : 1d list or numpy.array
        x-axis values
    yData1 : 3d numpy.array
        Data to plot.  First axis should correspond to xData1.
    beams : Optional[list]
        list identifying the beams present in the second axis of xData1.
    gates : Optional[list]
        list identifying the gates present in the second axis of xData1.
    yData1_title : Optional[str]
        Name of yData1 data.
    plot_beam : Optional[list of int]
        list of beams to plot from (corresponds to yData1 second axis)
    plot_gate : Optional[list of int]
        list of range gates to plot from (corresponds to yData1 third axis)
    fig : Optional[matplotlib.figure]
        matplotlib figure object that will be plotted to.  If not provided, one will be created.
    xlim : Optional[None or 2-element iterable]
        X-axis limits of all plots
    ylim : Optional[None or 2-element iterable]
        Y-axis limits of all plots
    xlabel : Optional[None or str]
        X-axis label
    ylabel : Optional[None or str]
        Y-axis label
    title : Optional[None or str]
        Title of plot
    xData2 : Optional[1d list or numpy.array]
        x-axis values of second data set
    yData1 : Optional[3d numpy.array]
        Second data set data to plot.  First axis should correspond to xData1.
    yData2_title : Optional[str]
        Name of yData2 data.
    xBoundaryLimits : Optional[None or 2-element iterable]
        Element sequence to shade out portions of the data.  Data outside of this range will be shaded gray,
        Data inside of the range will have a white background.  If set to None, this will automatically be set to the timeLimits set
        in the metadata, if they exist.

    Returns
    -------
    fig : matplotlib.figure
        matplotlib figure object that was plotted to

    Written by Nathaniel A. Frissell, Fall 2013

    """
    if fig is None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=figsize)

    from matplotlib import dates as md

    # Calculate three default beams and gates to plot.
    if plotBeam is None:
        beamMin = min(beams)
        beamMed = int(np.median(beams))
        beamMax = max(beams)

        plotBeam     = np.array([beamMin,beamMed,beamMax])

    if plotGate is None:
        gateMin = min(gates)
        gateMed = int(np.median(gates))
        gateMax = max(gates)

        plotGate     = np.array([gateMin,gateMed,gateMax])

    # Put things in the correct order.  Gates need to be backwards.
    plotBeam.sort()
    plotGate.sort()
    plotGate = plotGate[::-1] # Reverse the order.

    # Determine the indices of the beams and gates.
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

    # Define x-axis range
    if xlim is None:
        tmpLim = []
        tmpLim.append(min(xData1))
        tmpLim.append(max(xData1))
        if xData2 is not None:
            tmpLim.append(min(xData2))
            tmpLim.append(max(xData2))
        xlim = (min(tmpLim),max(tmpLim))

    # Autorange y-axis... make all plots have the same range.
    data = []
    if ylim is None:
        for rg,rgInx in zip(plotGate,plotGateInx):
            for bm,bmInx in zip(plotBeam,plotBeamInx):
                for item in yData1[:,bmInx,rgInx]:
                    data.append(item)
                if yData2 is not None:
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

            if yData2 is not None:
                l2, = axis.plot(xData2,yData2[:,bmInx,rgInx],label=yData2_title)

            # Set axis limits.
            axis.set_xlim(xlim)
            axis.set_ylim(ylim)

            # Special handling for time axes.
            if xlabel == 'UT': 
                axis.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))

                labels = axis.get_xticklabels()
                for label in labels:
                    label.set_rotation(30)

            # Gray out area outside of the boundary.
            if xBoundaryLimits is not None:
                gray = '0.75'
                axis.axvspan(xlim[0],xBoundaryLimits[0],color=gray)
                axis.axvspan(xBoundaryLimits[1],xlim[1],color=gray)
                axis.axvline(x=xBoundaryLimits[0],color='g',ls='--',lw=2)
                axis.axvline(x=xBoundaryLimits[1],color='g',ls='--',lw=2)

            text = 'Beam: %i, Gate: %i' % (bm, rg)
            axis.text(0.02,0.92,text,transform=axis.transAxes)

            # Only the first column gets labels.
            if ii % nCols == 1:
                axis.set_ylabel(ylabel)

            # Only have the last row have time ticks
            if ii <= (nRows-1)*nCols:
                axis.xaxis.set_visible(False)
            else:
                axis.set_xlabel(xlabel)

            ii = ii+1

    if yData1_title is not None and yData2_title is not None:
        fig.legend((l1,l2),(yData1_title,yData2_title),loc=(0.55,0.92))

    if title is not None:
        fig.text(0.12,0.92,title,size=24)

    return fig

def plotFullSpectrum(dataObj,dataSet='active',
        fig                     = None,
        axis                    = None,
        xlim                    = None,
        normalize               = False,
        scale                   = None,
        plot_title              = True,
        maxXTicks               = 10.,
        plot_cbar               = True,
        cbar_label              = 'ABS(Spectral Density)',
        cbar_ticks              = None,
        cbar_shrink             = 1.0,
        cbar_fraction           = 0.15,
        cbar_pad                = 0.05,
        cbar_gstext_offset      = -0.075,
        cbar_gstext_fontsize    = None,
        cbar_gstext_enable      = True,
        **kwArgs):
    """Plot full spectrum of a pydarn.proc.music.musicArray object.  The spectrum must have already been calculated with
    pydarn.proc.music.calculateFFT().

    In this plot, major divisions on the x-axis are FFT bins.  Every bin contains one slice representing each beam of the given radar
    data, from left to right.  The y-axis shows the range gates of the data object.  The color bar at the top of the plot shows which
    FFT bin contains the most power when integrating over the entire bin.

    Parameters
    ----------
    dataObj : pydarn.proc.music.musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to plot
    fig : Optional[matplotlib.figure]
        matplotlib figure object that will be plotted to.  If not provided, one will be created.
    axis : Optional[ ]
        Matplotlib axis object to plot on.
    xlim : Optional[None or 2-element iterable]
        X-axis limits in Hz
    plot_title : Optional[bool]
        If True, plot the title information
    maxXTicks : Optional[int]
        Maximum number of xtick labels.
    cbar_label : Optional[str]
        Text for color bar label
    cbar_ticks : Optional[list]
        Where to put the ticks on the color bar.
    cbar_shrink : Optional[float]
        fraction by which to shrink the colorbar
    cbar_fraction : Optional[float]
        fraction of original axes to use for colorbar
    cbar_gstext_offset : Optional[float]
        y-offset from colorbar of "Ground Scatter Only" text
    cbar_gstext_fontsize : Optional[float]
        fontsize of "Ground Scatter Only" text
    cbar_gstext_enable : Optional[bool]
        Enable "Ground Scatter Only" text
    **kwArgs :
        Keyword Arguments


    Returns
    -------
    return_dict

    Written by Nathaniel A. Frissell, Fall 2013

    """
    from scipy import stats

    return_dict = {}
    currentData = getDataSet(dataObj,dataSet)

    nrFreqs,nrBeams,nrGates = np.shape(currentData.spectrum)

    if xlim is None:
        posFreqInx  = np.where(currentData.freqVec >= 0)[0]
    else:
        posFreqInx  = np.where(np.logical_and(currentData.freqVec >= xlim[0],currentData.freqVec <= xlim[1]))[0]

    posFreqVec  = currentData.freqVec[posFreqInx]
    npf         = len(posFreqVec) # Number of positive frequencies

    data        = np.abs(currentData.spectrum[posFreqInx,:,:]) # Use the magnitude of the positive frequency data.

    if normalize:
        data    = data / data.max()

    # Determine scale for colorbar.
    sd          = stats.nanstd(data,axis=None)
    mean        = stats.nanmean(data,axis=None)
    scMax       = mean + 2.*sd
    if scale is None:
        scale       = scMax*np.array([0,1.])

    nXBins      = nrBeams * npf # number of bins we are going to plot

    # Average Power Spectral Density
    avg_psd = np.zeros(npf)
    for x in range(npf): avg_psd[x] = np.mean(data[x,:,:])

    # Do plotting here!
    if fig is None and axis is None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=figsize)
    elif axis is not None:
        fig = axis.get_figure()

    if axis is None:
        axis = fig.add_subplot(111)

    verts   = []
    scan    = []
    # Plot Spectrum
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

    param = 'power'
    cmap = matplotlib.cm.Blues_r

    bounds  = np.linspace(scale[0],scale[1],256)
    norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)
    pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)
    spect_pcoll = pcoll

    # Colorbar
    if plot_cbar:
        cbar = fig.colorbar(pcoll,orientation='vertical',shrink=cbar_shrink,fraction=cbar_fraction,pad=cbar_pad)
        cbar.set_label(cbar_label)
        if cbar_ticks is None:
            labels = cbar.ax.get_yticklabels()
            labels[-1].set_visible(False)
        else:
            cbar.set_ticks(cbar_ticks)

        if currentData.metadata.has_key('gscat') and cbar_gstext_enable:
            if currentData.metadata['gscat'] == 1:
                cbar.ax.text(0.5,cbar_gstext_offset,'Ground\nscat\nonly',ha='center',fontsize=cbar_gstext_fontsize)

    # Plot average values.
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

    # Mark maximum PSD column.
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

    # X-Labels
    modX      = np.ceil(npf / np.float(maxXTicks))

    xlabels = []
    xpos    = []
    for ff in range(npf-1):
        if (ff % modX) != 0: continue
        freqLabel = '%.2f'  % (posFreqVec[ff]*1000.)
        if posFreqVec[ff] == 0:
            periodLabel = 'Inf'
        else:
            periodLabel = '%.0f' % (1./posFreqVec[ff] / 60.)
        xlabels.append(freqLabel+'\n'+periodLabel)
        xpos.append(nrBeams* (ff + 0.1))

    xlabels.append('freq [mHz]\nPer. [min]')
    xpos.append(nrBeams* (npf-1 + 0.1))

    axis.set_xticks(xpos)
    axis.set_xticklabels(xlabels,ha='left')

    # Y-Labels
    maxYTicks       = 10.
    modY            = np.ceil(nrGates/maxYTicks)

    ylabels = []
    ypos    = []
    for gg in range(nrGates):
        if (gg % modY) != 0: continue
        ylabels.append('%i' % currentData.fov.gates[gg])
        ypos.append(gg+0.5)
        
    ylabels.append('$\Sigma$PSD') 
    ypos.append(nrGates+0.5)
    axis.set_yticks(ypos)
    axis.set_yticklabels(ylabels)
    axis.set_ylabel('Range Gate')

    for ff in range(npf):
        axis.axvline(x=ff*nrBeams,color='k',lw=2)

#    axis.set_xlim([0,nXBins])
    axis.set_ylim([0,nrGates+1])

    if plot_title:
        xpos = 0.130
        fig.text(xpos,0.99,'Full Spectrum View',fontsize=20,va='top')

        # Get the time limits.
        timeLim = (np.min(currentData.time),np.max(currentData.time))
        md = currentData.metadata

        # Translate parameter information from short to long form.
        paramDict = getParamDict(md['param'])
        param     = paramDict['param']
#        cbarLabel = paramDict['label']

        text = md['name'] + ' ' + param.capitalize() + timeLim[0].strftime(' (%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M)')

        if md.has_key('fir_filter'):
            filt = md['fir_filter']
            if filt[0] is None:
                low = 'None'
            else:
                low = '%.2f' % (1000. * filt[0])
            if filt[1] is None:
                high = 'None'
            else:
                high = '%.2f' % (1000. * filt[1])

            text = text + '\n' + 'Digital Filter: [' + low + ', ' + high + '] mHz'

        fig.text(xpos,0.95,text,fontsize=14,va='top')

    return_dict['cbar_pcoll']   = spect_pcoll
    return_dict['cbar_label']   = cbar_label
    return return_dict

def plotDlm(dataObj,dataSet='active',fig=None):
    """Plot the cross spectral matrix of a pydarn.proc.music.musicArray object.  The cross-spectral matrix must have already
    been calculated for the chosen data set using pydarn.proc.music.calculateDlm().

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to plot
    fig : Optional[matplotlib.figure]
        matplotlib figure object that will be plotted to.  If not provided, one will be created.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    if fig is None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=figsize)

    import copy
    from scipy import stats

    currentData = getDataSet(dataObj,dataSet)


    data        = np.abs(currentData.Dlm)

    # Determine scale for colorbar.
    sd          = stats.nanstd(data,axis=None)
    mean        = stats.nanmean(data,axis=None)
    scMax       = mean + 4.*sd
    scale       = scMax*np.array([0,1.])

    # Do plotting here!
    axis = fig.add_subplot(111)

    nrL, nrM = np.shape(data)

    verts   = []
    scan    = []
    # Plot Spectrum
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
    if scale is None:
        scale   = (np.min(scan),np.max(scan))
    cmap = matplotlib.cm.jet
    bounds  = np.linspace(scale[0],scale[1],256)
    norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)

    pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    # Colorbar
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
    # Get the time limits.
    timeLim = (np.min(currentData.time),np.max(currentData.time))
    md = currentData.metadata

    # Translate parameter information from short to long form.
    paramDict = getParamDict(md['param'])
    param     = paramDict['param']
    cbarLabel = paramDict['label']

    text = md['name'] + ' ' + param.capitalize() + timeLim[0].strftime(' (%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M)')

    if md.has_key('fir_filter'):
        filt = md['fir_filter']
        if filt[0] is None:
            low = 'None'
        else:
            low = '%.2f' % (1000. * filt[0])
        if filt[1] is None:
            high = 'None'
        else:
            high = '%.2f' % (1000. * filt[1])

        text = text + '\n' + 'Digital Filter: [' + low + ', ' + high + '] mHz'

    fig.text(xpos,0.95,text,fontsize=14,va='top')

def plotKarr(dataObj,dataSet='active',fig=None,axis=None,maxSignals=None, sig_fontsize=24,
            plot_title=True, cbar_ticks=None, cbar_shrink=1.0, cbar_fraction=0.15,
            cbar_gstext_offset=-0.075, cbar_gstext_fontsize=None, **kwArgs):
    """Plot the horizontal wave number array for a pydarn.proc.music.musicArray object.  The kArr must have aready
    been calculated for the chosen data set using pydarn.proc.music.calculateKarr().

    If the chosen data set has signals stored in the sigDetect attribute, numbers identifying each of the signals will
    be plotted on the kArr plot.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to plot
    fig : Optional[None or matplotlib.figure]
        matplotlib figure object that will be plotted to.  If not provided, one will be created.
    axis : Optional[ ]
        Matplotlib axis object to plot on.
    maxSignals : Optional[None or int]
        Maximum number of signals to plot if detected signals exist for the chosen data set.
    sig_fontsize : Optional[float]
        fontsize of signal markers
    plot_title : Optional[bool]
        If True, plot the title information
    cbar_ticks : Optional[list]
        Where to put the ticks on the color bar.
    cbar_shrink : Optional[float]
        fraction by which to shrink the colorbar
    cbar_fraction : Optional[float]
        fraction of original axes to use for colorbar
    cbar_gstext_offset : Optional[float]
        y-offset from colorbar of "Ground Scatter Only" text
    cbar_gstext_fontsize : Optional[float]
        fontsize of "Ground Scatter Only" text
    **kwArgs
        Keywords arguments

    Written by Nathaniel A. Frissell, Fall 2013

    """
    if fig is None and axis is None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=figsize)

    currentData = getDataSet(dataObj,dataSet)

    # Do plotting here!
    if axis is None:
        axis = fig.add_subplot(111,aspect='equal')
    else:
        fig = axis.get_figure()

    plotKarrAxis(dataObj,dataSet=dataSet,axis=axis,maxSignals=maxSignals,
            cbar_ticks=cbar_ticks, cbar_shrink=cbar_shrink, cbar_fraction=cbar_fraction,sig_fontsize=sig_fontsize,
            cbar_gstext_offset=cbar_gstext_offset, cbar_gstext_fontsize=cbar_gstext_fontsize,**kwArgs)

    if plot_title:
        xpos = 0.130
        fig.text(xpos,0.99,'Horizontal Wave Number',fontsize=20,va='top')
        # Get the time limits.
        timeLim = (np.min(currentData.time),np.max(currentData.time))
        md = currentData.metadata

        # Translate parameter information from short to long form.
        paramDict = getParamDict(md['param'])
        param     = paramDict['param']

        text = md['name'] + ' ' + param.capitalize() + timeLim[0].strftime(' (%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M)')

        if md.has_key('fir_filter'):
            filt = md['fir_filter']
            if filt[0] is None:
                low = 'None'
            else:
                low = '%.2f' % (1000. * filt[0])
            if filt[1] is None:
                high = 'None'
            else:
                high = '%.2f' % (1000. * filt[1])

            text = text + '\n' + 'Digital Filter: [' + low + ', ' + high + '] mHz'

        fig.text(xpos,0.95,text,fontsize=14,va='top')

def plotKarrDetected(dataObj,dataSet='active',fig=None,maxSignals=None,roiPlot=True):
    """Plot the horizontal wave number array for a pydarn.proc.music.musicArray object.  The kArr must have aready
    been calculated for the chosen data set using pydarn.proc.music.calculateKarr().

    Unlike plotKarr, this routine can plot a region-of-interest map showing features detected by pydarn.proc.music.detectSignals().

    If the chosen data set has signals stored in the sigDetect attribute, numbers identifying each of the signals will
    be plotted on the kArr plot.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to plot
    fig : Optional[None or matplotlib.figure]
        matplotlib figure object that will be plotted to.  If not provided, one will be created.
    maxSignals : Optional[None or int]
        Maximum number of signals to plot if detected signals exist for the chosen data set.
    roiPlot : Optional[bool]
        If true, a region of interest plot showing the features detected using pydarn.proc.music.detectSignals()
        will be displayed alongside the kArr plot.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    if fig is None:
        from matplotlib import pyplot as plt
        fig   = plt.figure(figsize=figsize)
    currentData = getDataSet(dataObj,dataSet)

    from scipy import stats
    import matplotlib.patheffects as PathEffects

    # Do plotting here!
    if roiPlot:
        axis = fig.add_subplot(121,aspect='equal')
    else:
        axis = fig.add_subplot(111,aspect='equal')

    # Page-wide header #############################################################
    xpos = 0.130
    fig.text(xpos,0.99,'Horizontal Wave Number',fontsize=20,va='top')
    # Get the time limits.
    timeLim = (np.min(currentData.time),np.max(currentData.time))
    md = currentData.metadata

    # Translate parameter information from short to long form.
    paramDict = getParamDict(md['param'])
    param     = paramDict['param']
    cbarLabel = paramDict['label']

    text = md['name'] + ' ' + param.capitalize() + timeLim[0].strftime(' (%Y %b %d %H:%M - ') + timeLim[1].strftime('%Y %b %d %H:%M)')

    if md.has_key('fir_filter'):
        filt = md['fir_filter']
        if filt[0] is None:
            low = 'None'
        else:
            low = '%.2f' % (1000. * filt[0])
        if filt[1] is None:
            high = 'None'
        else:
            high = '%.2f' % (1000. * filt[1])

        text = text + '\n' + 'Digital Filter: [' + low + ', ' + high + '] mHz'

    fig.text(xpos,0.95,text,fontsize=14,va='top')
    # End Page-wide header #########################################################

    plotKarrAxis(dataObj,dataSet=dataSet,axis=axis,maxSignals=maxSignals)

    if roiPlot:
        ################################################################################
        # Feature detection...
        data2 = currentData.sigDetect.labels
        nrL, nrM = np.shape(data2)
        scale = [0,data2.max()]

        # Do plotting here!
        axis = fig.add_subplot(122,aspect='equal')
        verts   = []
        scan    = []
        # Plot Spectrum
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

        # Colorbar
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
            tmpList = range(currentData.sigDetect.nrSigs)[::-1] # Force list to plot backwards so number 1 is on top!
            for signal in currentData.sigDetect.info:
                if maxSignals is not None:
                    if signal['order'] > maxSignals: continue 
                xpos = currentData.kxVec[signal['maxpos'][0]]
                ypos = currentData.kyVec[signal['maxpos'][1]]
                txt  = '%i' % signal['order']
                axis.text(xpos,ypos,txt,color='k',zorder=200-signal['order'],size=24,path_effects=pe)

def plotKarrAxis(dataObj,dataSet='active',axis=None,maxSignals=None, sig_fontsize=24,x_labelpad=None,y_labelpad=None,
            cbar_ticks=None, cbar_shrink=1.0, cbar_fraction=0.15,
            cbar_gstext_offset=-0.075, cbar_gstext_fontsize=None,cbar_pad=0.05,cmap=None,plot_colorbar=True):
    """Plot the horizontal wave number array for a pydarn.proc.music.musicArray object.  The kArr must have aready
    been calculated for the chosen data set using pydarn.proc.music.calculateKarr().

    If the chosen data set has signals stored in the sigDetect attribute, numbers identifying each of the signals will
    be plotted on the kArr plot.

    This routine will make the plot without titles, etc.  It is used as the foundation for plotKarr() and plotKarrDetected().

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to plot
    axis : Optional[matplotlib.figure.axis]
        matplotlib axis object that will be plotted to.  If not provided, this function will return.
    maxSignals : Optional[None or int]
        Maximum number of signals to plot if detected signals exist for the chosen data set.
    sig_fontsize : Optional[float]
        fontsize of signal markers
    cbar_ticks : Optional[list]
        Where to put the ticks on the color bar.
    cbar_shrink : Optional[float]
        fraction by which to shrink the colorbar
    cbar_fraction : Optional[float]
        fraction of original axes to use for colorbar
    cbar_gstext_offset : Optional[float]
        y-offset from colorbar of "Ground Scatter Only" text
    cbar_gstext_fontsize : Optional[float]
        fontsize of "Ground Scatter Only" text
    cmap : Optional[None or matplotlib colormap object]
        If None and cmap_handling=='matplotlib', use jet.
    plot_colorbar : Optional[bool]
        Enable or disable colorbar plotting.

    Returns
    -------
    return_dict


    Written by Nathaniel A. Frissell, Fall 2013

    """
    if axis is None: return
    return_dict = {}

    fig = axis.get_figure()
    from scipy import stats
    import matplotlib.patheffects as PathEffects

    currentData = getDataSet(dataObj,dataSet)

    data        = np.abs(currentData.karr) - np.min(np.abs(currentData.karr))
    # Determine scale for colorbar.
    sd          = stats.nanstd(data,axis=None)
    mean        = stats.nanmean(data,axis=None)
    scMax       = mean + 6.5*sd

    data = data / scMax
    scale       = [0.,1.]

    nrL, nrM = np.shape(data)
    verts   = []
    scan    = []
    # Plot Spectrum
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

    if cmap is None:
        cmap = matplotlib.cm.jet
    bounds  = np.linspace(scale[0],scale[1],256)
    norm    = matplotlib.colors.BoundaryNorm(bounds,cmap.N)

    pcoll   = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    ################################################################################
    # Annotations
    axis.axvline(color='0.82',lw=2,zorder=150)
    axis.axhline(color='0.82',lw=2,zorder=150)

    # Colorbar
    cbar_label  = 'Normalized Wavenumber Power'
    if plot_colorbar:
        cbar = fig.colorbar(pcoll,orientation='vertical',shrink=cbar_shrink,fraction=cbar_fraction,pad=cbar_pad)
        cbar.set_label(cbar_label)
        if not cbar_ticks:
            cbar_ticks = np.arange(10)/10.
        cbar.set_ticks(cbar_ticks)

        if currentData.metadata.has_key('gscat'):
            if currentData.metadata['gscat'] == 1:
                cbar.ax.text(0.5,cbar_gstext_offset,'Ground\nscat\nonly',ha='center',fontsize=cbar_gstext_fontsize)

#    cbar = fig.colorbar(pcoll,orientation='vertical')#,shrink=.65,fraction=.1)
#    cbar.set_label('ABS(Spectral Density)')
#    cbar.set_ticks(np.arange(10)/10.)
#    if currentData.metadata.has_key('gscat'):
#        if currentData.metadata['gscat'] == 1:
#            cbar.ax.text(0.5,-0.075,'Ground\nscat\nonly',ha='center')

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
    axis.set_xlabel(u'kx [rad]\n$\lambda$ [km]',ha='center',labelpad=x_labelpad)
#    axis.set_xlabel('%f' % x_labelpad,ha='center',labelpad=x_labelpad)

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
        txt = '\n'.join([km_txt,rad_txt])
        newLabels.append(txt)
    axis.set_yticklabels(newLabels,rotation=90.)
    axis.set_ylabel(u'ky [rad]\n$\lambda$ [km]',va='center',labelpad=y_labelpad)
    # End add wavelength to x/y tick labels ######################################## 

    md = currentData.metadata

    # Translate parameter information from short to long form.
    paramDict = getParamDict(md['param'])
    param     = paramDict['param']
    cbarLabel = paramDict['label']

    if hasattr(currentData,'sigDetect'):
        pe = [PathEffects.withStroke(linewidth=3,foreground='w')]
        for signal in currentData.sigDetect.info:
            if maxSignals is not None:
                if signal['order'] > maxSignals: continue 
            xpos = currentData.kxVec[signal['maxpos'][0]]
            ypos = currentData.kyVec[signal['maxpos'][1]]
            txt  = '%i' % signal['order']
            axis.text(xpos,ypos,txt,color='k',zorder=200-signal['order'],size=sig_fontsize,path_effects=pe)

    return_dict['cbar_pcoll']   = pcoll
    return_dict['cbar_label']   = cbar_label
    return return_dict
