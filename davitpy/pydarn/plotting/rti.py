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
.. module:: rti
   :synopsis: A module for generating rti plots.

.. moduleauthor:: AJ, 20130123

*********************
**Module**: pydarn.plotting.rti
*********************
**Functions**:
  * :func:`pydarn.plotting.rti.plotRti`
  * :func:`pydarn.plotting.rti.plot_freq`
  * :func:`pydarn.plotting.rti.plot_searchnoise`
  * :func:`pydarn.plotting.rti.plot_skynoise`
  * :func:`pydarn.plotting.rti.plot_cpid`
  * :func:`pydarn.plotting.rti.plot_nave`
  * :func:`pydarn.plotting.rti.rti_title`
  * :func:`pydarn.plotting.rti.draw_axes`
  * :func:`pydarn.plotting.rti.read_data`
  * :func:`pydarn.plotting.rti.rti_panel`
  * :func:`pydarn.plotting.rti.daynight_terminator`
"""

import numpy
import math
import matplotlib
import calendar
import datetime
import pylab
import matplotlib.pyplot as plot
import matplotlib.lines as lines
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import MultipleLocator
from matplotlib.collections import PolyCollection
from davitpy.utils.timeUtils import *
from davitpy.pydarn.sdio import *
from matplotlib.figure import Figure


def plotRti(sTime, rad, eTime=None, bmnum=7, fileType='fitex',
            params=['velocity', 'power', 'width'], scales=[], channel=None,
            coords='gate', colors='lasse', yrng=-1, gsct=False, lowGray=False,
            show=True, filtered=False, fileName=None, tFreqBands=[],
            myFile=None, xtick_size=9, ytick_size=9, xticks=None,
            axvlines=None, plotTerminator=False):

    """ Wrapper for plot_rti. This function is being deprecated.

    """
    print "Warning: This function is being deprecated. Use plot_rti instead."
    print "Calling plot_rti."

    return plot_rti(sTime, rad, eTime=eTime, bmnum=bmnum, fileType=fileType,
                    params=params, scales=scales, channel=channel,
                    coords=coords, colors=colors, yrng=yrng, gsct=gsct,
                    low_gray=lowGray, show=show, filtered=filtered,
                    fileName=fileName, tfreqbands=tFreqBands, myFile=myFile,
                    xtick_size=xtick_size, ytick_size=ytick_size,
                    xticks=xticks, axvlines=axvlines,
                    plot_terminator=plotTerminator)


def plot_rti(sTime, rad, eTime=None, bmnum=7, fileType='fitex',
             params=['velocity', 'power', 'width'], scales=[], channel=None,
             coords='gate', colors='lasse', yrng=-1, gsct=False,
             low_gray=False, show=True, filtered=False, fileName=None,
             tfreqbands=[], myFile=None, xtick_size=9, ytick_size=9,
             xticks=None, axvlines=None, plot_terminator=False):

    """ Create an rti plot for a secified radar and time period.

    **Args**:
        * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): a datetime
            object indicating the start time which you would like to plot
        * **rad** (str): the 3 letter radar code, e.g. 'bks'
        * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): a datetime
            object indicating th end time you would like plotted.  If this
            is None, 24 hours will be plotted.  default = None.
        * **[bmnum] (int)**: The beam to plot.  default: 7
        * **[fileType]** (str): The file type to be plotted, one of ['fitex',
            'fitacf', 'lmfit'].  default = 'fitex'.
        * **[params]** (list): a list of the fit parameters to plot, allowable
            values are: ['velocity', 'power', 'width', 'elevation',
            'phi0'].  default: ['velocity', 'power', 'width']
        * **[scales]** (list): a list of the min/max values for the color scale
            for each param.  If omitted, default scales will be used.  If
            present, the list should be n x 2 where n is the number of elements
            in the params list.  Use an empty list for default range, e.g.
            [[-250,300],[],[]].  default: [[-200,200], [0,30],[0,150]]
        * **[channel]** (char): the channel you wish to plot, e.g. 'a', 'b',
            'c', ...  default: 'a'
        * **[coords]** (str): the coordinates to use for the y axis.  The
            allowable values are 'gate', 'rng', 'geo', 'mag' default: 'gate'
        * **[colors]** (str): a string indicating what color bar to use, valid
            inputs are ['lasse','aj'].  default: 'lasse'
        * **[yrng]** (list or -1): a list indicating the min and max values
            for the y axis in the chosen coordinate system, or a -1 indicating
            to plot everything.  default: -1.
        * **[gsct]** (boolean): a flag indicating whether to plot ground
            scatter as gray. default: False (ground scatter plotted normally)
        * **[low_gray]** (boolean): a flag indicating whether to plot low
            velocity scatter as gray. default: False (low velocity scatter
            plotted normally)
        * **[show]** (boolean): a flag indicating whether to display the figure
            on the screen.  This can cause problems over ssh.  default = True
        * **[retfig]** (boolean):  a flag indicating that you want the figure
            to be returned from the function.  Only the last figure in the list
            of frequency bands will be returned.  default = False
        * **[filtered]** (boolean): a flag indicating whether to boxcar filter
            the data.  default = False (no filter)
        * **[fileName]** (string): If you want to plot for a specific file,
            indicate the name of the file as fileName.  Include the type of
            the file in custType.
        * **[tfreqbands]** (list): a list of the min/max values for the
            transmitter frequencies in kHz.  If omitted, the default band will
            be used.  If more than one band is specified, retfig will cause
            only the last one to be returned.  default: [[8000,20000]]
        * **[myFile]** (:class:`pydarn.sdio.radDataTypes.radDataPtr`): contains
            the pipeline to the data we want to plot. If specified, data will
            be plotted from the file pointed to by myFile. default: None
        * **[figure]** (matplotlib.figure) figure object to plot on.  If None,
            a figure object will be created for you.
        * **[xtick_size]**: (int) fontsize of xtick labels
        * **[ytick_size]**: (int) fontsize of ytick labels
        * **[xticks]**: (list) datetime.datetime objects indicating the
            location of xticks
        * **[axvlines]**: (list) datetime.datetime objects indicating the
            location vertical lines marking the plot
        * **[plot_terminator]**: (boolean) Overlay the day/night terminator.
    **Returns**:
        * A list of figures of length len(tfreqbands)

    **Example**:
        ::

      import datetime as dt
      pydarn.plotting.rti.plot_rti(dt.datetime(2013,3,16), 'bks',
                                  eTime=dt.datetime(2013,3,16,14,30),
                                  bmnum=12, fileType='fitacf',
                                  scales=[[-500,500],[],[]], coords='geo',
                                  colors='aj', filtered=True, show=True)


    Written by AJ 20121002
    Modified by Matt W. 20130715
    Modified by Nathaniel F. 20131031 (added plot_terminator)
    Modified by ASR 20150917 (refactored)
    """
    import os
    from davitpy import pydarn
    from davitpy import utils

    t1 = datetime.datetime.now()
    # check the inputs
    assert(isinstance(sTime, datetime.datetime)), 'error, sTime must be a ' \
                                                  'datetime object'
    assert(isinstance(rad, str) and len(rad) == 3), 'error, rad must be a ' \
                                                    'string 3 chars long'
    assert(isinstance(eTime, datetime.datetime) or
           eTime is None), 'error, eTime must be a datetime object or None'
    if eTime is None:
        eTime = sTime+datetime.timedelta(days=1)
    assert(sTime < eTime), "eTime must be greater than sTime!"
    assert(coords == 'gate' or coords == 'rng' or coords == 'geo' or
           coords == 'mag'), "error, coords must be one of 'gate', 'rng', " \
                             "'geo', 'mag'"
    assert(isinstance(bmnum, int)), 'error, beam must be integer'
    assert(0 < len(params) < 6), 'error, must input between 1 and 5 params \
           in LIST form'
    for i in range(0, len(params)):
        assert(params[i] == 'velocity' or params[i] == 'power' or
               params[i] == 'width' or params[i] == 'elevation' or
               params[i] == 'phi0' or params[i] == 'velocity_error'), \
               "error, allowable params are 'velocity', 'power', 'width'," \
               " 'elevation', 'phi0', 'velocity_error'"
    for i in range(0, len(scales)):
        assert(isinstance(scales[i], list)), \
               'error, each item in scales must be a list of upper and ' \
               'lower bounds on paramaters.'
    assert(scales == [] or
           len(scales) == len(params)), 'error, if present, scales must ' \
                                        'have same number of elements as ' \
                                        'params'
    assert(yrng == -1 or
           (isinstance(yrng, list) and
            yrng[0] <= yrng[1])), 'error, yrng must equal -1 or be a list ' \
                                  'with the 2nd element larger than the first'
    assert(colors == 'lasse' or
           colors == 'aj'), "error, valid inputs for color are " \
                            "'lasse' and 'aj'"

    # Assign any default color scale parameter limits.
    tscales = []
    for i in range(0, len(params)):
        if(scales == [] or scales[i] == []):
            if(params[i] == 'velocity'): tscales.append([-200, 200])
            elif(params[i] == 'power'): tscales.append([0, 30])
            elif(params[i] == 'width'): tscales.append([0, 150])
            elif(params[i] == 'elevation'): tscales.append([0, 50])
            elif(params[i] == 'velocity_error'): tscales.append([0, 200])
            elif(params[i] == 'phi0'): tscales.append([-numpy.pi, numpy.pi])
        else: tscales.append(scales[i])
    scales = tscales

    # Assign default frequency band.
    tbands = []
    if tfreqbands == []:
        tbands.append([8000, 20000])
    else:
        for band in tfreqbands:
            # Make sure that starting frequncy is less than the ending
            # frequency for each band.
            assert(band[0] < band[1]), "Starting frequency must be less " \
                                       "than ending frequency!"
            tbands.append(band)

    # Open the file if a pointer was not given to us
    # if fileName is specified then it will be read.
    if not myFile:
        myFile = radDataOpen(sTime, rad, eTime, channel=channel, bmnum=bmnum,
                             fileType=fileType, filtered=filtered,
                             fileName=fileName)
    else:
        # Make sure that we will only plot data for the time range specified
        # by sTime and eTime.
        if myFile.sTime <= sTime and myFile.eTime > sTime and \
                myFile.eTime >= eTime:

            myFile.sTime = sTime
            myFile.eTime = eTime
        else:
            # If the times range is not covered by the file, throw an error.
            print 'error, data not available in myFile for the whole sTime ' \
                  'to eTime'
            return None

    # Check that we have data available now that we may have tried
    # to read it using radDataOpen.
    if not myFile:
        print 'error, no files available for the requested ' \
              'time/radar/filetype combination'
        return None

    # Finally we can start reading the data file
    myBeam = myFile.readRec()
    if not myBeam:
        print 'error, no data available for the requested ' \
              'time/radar/filetype combination'
        return None

    # Now read the data that we need to make the plots
    data_dict = read_data(myFile, myBeam, bmnum, params, tbands)

    rti_figs = list()
    for fplot in range(len(tbands)):
        # Check to ensure that data exists for the requested frequency
        # band else continue on to the next range of frequencies
        if not data_dict['freq'][fplot]:
            print 'error, no data in frequency range ' + \
                  str(tbands[fplot][0]) + ' kHz to ' + \
                  str(tbands[fplot][1]) + ' kHz'
            rti_figs.append(None)
            continue

        # Create a figure.
        rti_fig = plot.figure(figsize=(11, 8.5))
        rti_figs.append(rti_fig)

        # Create the axes for noise, tx freq, and cpid.
        noise_pos = [.1, .88, .76, .06]
        freq_pos = [.1, .82, .76, .06]
        cpid_pos = [.1, .77, .76, .05]

        skynoise_ax = rti_fig.add_axes(noise_pos, label='sky')
        searchnoise_ax = rti_fig.add_axes(noise_pos, label='search',
                                          frameon=False)
        freq_ax = rti_fig.add_axes(freq_pos, label='freq')
        nave_ax = rti_fig.add_axes(freq_pos, label='nave', frameon=False)
        cpid_ax = rti_fig.add_axes(cpid_pos)

        # Give the plot a title.
        rti_title(rti_fig, sTime, rad, fileType, bmnum, eTime=eTime)

        # Plot the sky noise.
        plot_skynoise(skynoise_ax, data_dict['times'][fplot],
                      data_dict['nsky'][fplot])
        # Plot the search noise.
        plot_searchnoise(searchnoise_ax, data_dict['times'][fplot],
                         data_dict['nsch'][fplot])
        # plot the frequency bar.
        plot_freq(freq_ax, data_dict['times'][fplot],
                  data_dict['freq'][fplot])
        # Plot the nave data.
        plot_nave(nave_ax, data_dict['times'][fplot],
                  data_dict['nave'][fplot])
        # Plot the cpid bar
        plot_cpid(cpid_ax, data_dict['times'][fplot],
                  data_dict['cpid'][fplot], data_dict['mode'][fplot])

        # Plot each of the parameter panels.
        figtop = .77
        if ((eTime - sTime) <= datetime.timedelta(days=1)) and \
                (eTime.day == sTime.day):
            figheight = .72/len(params)
        elif ((eTime - sTime) > datetime.timedelta(days=1)) or \
                (eTime.day != sTime.day):
            figheight = .70/len(params)

        for p in range(len(params)):
            # Use draw_axes to create and set formatting of the axes to plot to.
            pos = [.1, figtop-figheight*(p+1)+.02, .76, figheight-.02]
            ax = draw_axes(rti_fig, data_dict['times'][fplot], rad,
                           data_dict['cpid'][fplot], bmnum,
                           data_dict['nrang'][fplot],
                           data_dict['frang'][fplot], data_dict['rsep'][fplot],
                           p == len(params)-1, yrng=yrng, coords=coords,
                           pos=pos, xtick_size=xtick_size,
                           ytick_size=ytick_size, xticks=xticks,
                           axvlines=axvlines)

            if(params[p] == 'velocity'): pArr = data_dict['vel'][fplot]
            elif(params[p] == 'power'): pArr = data_dict['pow'][fplot]
            elif(params[p] == 'width'): pArr = data_dict['wid'][fplot]
            elif(params[p] == 'elevation'): pArr = data_dict['elev'][fplot]
            elif(params[p] == 'phi0'): pArr = data_dict['phi0'][fplot]
            elif(params[p] == 'velocity_error'):
                pArr = data_dict['velocity_error'][fplot]

            if(pArr == []): continue

            # Generate the color map.
            cmap, norm, bounds = utils.plotUtils.genCmap(params[p], scales[p],
                                                         colors=colors,
                                                         lowGray=low_gray)

            # Plot the data to the axis object.
            pcoll = rti_panel(ax, data_dict, pArr, fplot, gsct, rad, bmnum,
                              coords, cmap, norm,
                              plot_terminator=plot_terminator)

            # Set xaxis formatting depending on amount of data plotted.
            if ((eTime - sTime) <= datetime.timedelta(days=1)) and \
                    (eTime.day == sTime.day):
                ax.xaxis.set_major_formatter(
                    matplotlib.dates.DateFormatter('%H:%M'))
            elif ((eTime - sTime) > datetime.timedelta(days=1)) or \
                    (eTime.day != sTime.day):
                ax.xaxis.set_major_formatter(
                    matplotlib.dates.DateFormatter('%d/%m/%y \n%H:%M'))
            ax.set_xlabel('UT')

            # Draw the colorbar.
            cb = utils.drawCB(rti_fig, pcoll, cmap, norm, map_plot=0,
                              pos=[pos[0]+pos[2]+.02, pos[1], 0.02, pos[3]])

            # Label the colorbar.
            l = []
            # Define the colorbar labels.
            for i in range(0, len(bounds)):
                if(params[p] == 'phi0'):
                    ln = 4
                    if(bounds[i] == 0): ln = 3
                    elif(bounds[i] < 0): ln = 5
                    l.append(str(bounds[i])[:ln])
                    continue
                if((i == 0 and
                    (params[p] == 'velocity' or
                     params[p] == 'velocity_error')) or i == len(bounds)-1):
                    l.append(' ')
                    continue
                l.append(str(int(bounds[i])))
            cb.ax.set_yticklabels(l)

            # Set colorbar ticklabel size.
            for t in cb.ax.get_yticklabels():
                t.set_fontsize(9)

            # Set colorbar label.
            if(params[p] == 'velocity'):
                cb.set_label('Velocity [m/s]', size=10)
            if(params[p] == 'grid'): cb.set_label('Velocity [m/s]', size=10)
            if(params[p] == 'power'): cb.set_label('SNR [dB]', size=10)
            if(params[p] == 'width'): cb.set_label('Spec Wid [m/s]', size=10)
            if(params[p] == 'elevation'): cb.set_label('Elev [deg]', size=10)
            if(params[p] == 'phi0'): cb.set_label('Phi0 [rad]', size=10)
            if(params[p] == 'velocity_error'):
                cb.set_label('Velocity Error [m/s]', size=10)

        if show:
            rti_fig.show()

        print 'plotting took:', datetime.datetime.now()-t1
        # End of plotting for loop.

        return rti_figs


def draw_axes(myFig, times, rad, cpid, bmnum, nrang, frang, rsep, bottom,
              yrng=-1, coords='gate', pos=[.1, .05, .76, .72], xtick_size=9,
              ytick_size=9, xticks=None, axvlines=None):
    """ Draws empty axes for an rti plot.

    **Args**:
        * **myFig**: the MPL figure we are plotting to
        * **times**: a list of datetime objects referencing the beam soundings
        * **rad**: 3 letter radar code
        * **cpid**: list of the cpids or the beam soundings
        * **bmnum**: beam number being plotted
        * **nrang**: list of nrang for the beam soundings
        * **frang**: list of frang of the beam soundings
        * **rsep**: list of rsep of the beam soundings
        * **bottom**: flag indicating if we are at the bottom of the figure
        * **[yrng]**: range of y axis, -1=autoscale (default)
        * **[coords]**: y axis coordinate system, acceptable values are 'geo',
            'mag', 'gate', 'rng'
        * **[pos]**: position of the plot
        * **[xtick_size]**: fontsize of xtick labels
        * **[ytick_size]**: fontsize of ytick labels
        * **[xticks]**: (list) datetime.datetime objects indicating the
            location of xticks
        * **[axvlines]**: (list) datetime.datetime objects indicating the
            location vertical lines marking the plot
    **Returns**:
        * **ax**: an axes object

    **Example:
        ::

            ax = draw_axes(myFig,times,rad,cpid,beam,nrang,frang,rsep,0)

    Written by AJ 20121002
    Modified by ASR 20150917 (refactored)
    """

    from davitpy import pydarn

    nrecs = len(times)
    # Add an axes object to the figure.
    ax = myFig.add_axes(pos)
    ax.yaxis.set_tick_params(direction='out')
    ax.xaxis.set_tick_params(direction='out')
    ax.yaxis.set_tick_params(direction='out', which='minor')
    ax.xaxis.set_tick_params(direction='out', which='minor')

    # Draw the axes.
    ax.plot_date(matplotlib.dates.date2num(times), numpy.arange(len(times)),
                 fmt='w', tz=None, xdate=True, ydate=False, alpha=0.0)

    # Determine the yaxis min/max.
    if(yrng == -1):
        ymin, ymax = 99999999, -999999999
        if(coords != 'gate'):
            oldCpid = -99999999
            for i in range(len(cpid)):
                if(cpid[i] == oldCpid): continue
                oldCpid = cpid[i]
                if(coords == 'geo' or coords == 'mag'):
                    # HACK NOT SURE IF YOU CAN DO THIS!
                    site = pydarn.radar.network().getRadarByCode(rad) \
                           .getSiteByDate(times[i])
                    myFov = pydarn.radar.radFov.fov(site=site, ngates=nrang[i],
                                                    nbeams=site.maxbeam,
                                                    rsep=rsep[i],
                                                    coords=coords,
                                                    date_time=times[i])
                    if(myFov.latFull[bmnum].max() > ymax):
                        ymax = myFov.latFull[bmnum].max()
                    if(myFov.latFull[bmnum].min() < ymin):
                        ymin = myFov.latFull[bmnum].min()
                else:
                    ymin = 0
                    if(nrang[i]*rsep[i]+frang[i] > ymax):
                        ymax = nrang[i]*rsep[i]+frang[i]

        else:
            ymin, ymax = 0, max(nrang)
    else:
        ymin, ymax = yrng[0], yrng[1]

    # Format the xaxis.
    xmin = matplotlib.dates.date2num(times[0])
    xmax = matplotlib.dates.date2num(times[len(times)-1])
    xrng = (xmax-xmin)
    inter = int(round(xrng/6.*86400.))
    inter2 = int(round(xrng/24.*86400.))
    ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
    ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))

    # If axis is at bottom of figure, draw xticks.
    if(not bottom):
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(0)
    else:
        if xticks is not None:
            ax.xaxis.set_ticks(xticks)

    if axvlines is not None:
        for line in axvlines:
            ax.axvline(line, color='0.25', ls='--')

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(xtick_size)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        ax.xaxis.set_label_text('UT')

    # Set ytick size.
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(ytick_size)
    # Format yaxis depending on coords.
    if(coords == 'gate'):
        ax.yaxis.set_label_text('Range gate', size=10)
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FormatStrFormatter('%d'))
        ax.yaxis.set_major_locator(MultipleLocator((ymax-ymin)/5.))
        ax.yaxis.set_minor_locator(MultipleLocator((ymax-ymin)/25.))
    elif(coords == 'geo' or coords == 'mag'):
        if(coords == 'mag'): ax.yaxis.set_label_text('Mag Lat [deg]', size=10)
        else: ax.yaxis.set_label_text('Geo Lat [deg]', size=10)
    elif(coords == 'rng'):
        ax.yaxis.set_label_text('Slant Range [km]', size=10)
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FormatStrFormatter('%d'))
        ax.yaxis.set_major_locator(MultipleLocator(1000))
        ax.yaxis.set_minor_locator(MultipleLocator(250))
    ax.set_ylim(bottom=ymin, top=ymax)

    return ax


def rti_title(fig, sTime, rad, fileType, beam, eTime=None, xmin=.1, xmax=.86):
    """Draws title for an rti plot.

    **Args**:
        * **fig**: a matplotlib.figure.Figure object
        * **sTime**: the start time for the data being plotted as a
            datetime object
        * **rad**: the 3 letter radar code
        * **fileType**: the file type being plotted
        * **beam**: the beam number being plotted
        * **[eTime]**: the end time for the data being plotted as a
            datetime object
        * **[xmin]**: minimum x value o the plot in page coords
        * **[xmax]**: maximum x value o the plot in page coords
    * **Returns**:
        *Nothing.

    **Example**:
        ::

            import datetime as dt
            from matplotlib import pyplot
            fig = pyplot.figure()
            rti_title(fig,dt.datetime(2011,1,1),'bks','fitex',7)

    Written by AJ 20121002
    Modified by ASR 20150916
    """

    from davitpy import pydarn

    # Obtain the davitpy.pydarn.radar.radStruct.radar object for rad.
    r = pydarn.radar.network().getRadarByCode(rad)

    # Plot the main title
    fig.text(xmin, .95, r.name+'  ('+fileType+')', ha='left', weight=550)

    # Determine what time information should be plotted in the secondary title
    if ((eTime is not None) and
        (((eTime - sTime) > datetime.timedelta(days=1)) or
         (eTime.day != sTime.day))):
        title_text = str(sTime.day) + '/' \
                     + calendar.month_name[sTime.month][:3] + '/' \
                     + str(sTime.year) + ' - ' + str(eTime.day) + '/' \
                     + calendar.month_name[eTime.month][:3]+'/'+str(eTime.year)

    else:
        title_text = str(sTime.day) + '/' \
                     + calendar.month_name[sTime.month][:3] + '/' \
                     + str(sTime.year)

    # Plot the secondary title.
    fig.text((xmin+xmax)/2., .95, title_text, weight=550,
             size='large', ha='center')
    fig.text(xmax, .95, 'Beam ' + str(beam), weight=550, ha='right')


def plot_cpid(ax, times, cpid, mode):
    """Plots cpid panel at position pos.

    **Args**:
        * **ax**: a MPL axis object to plot to
        * **times**: a list of the times of the beam soundings
        * **cpid**: a lsit of the cpids of th beam soundings
        * **mode**: a list of the ifmode param
    **Returns**:
        * Nothing.

    **Example**:
        ::

            plot_cpid(ax,times,cpid,mode)

        Written by AJ 20121002
        Modified by ASR 20150916
    """

    from davitpy import pydarn
    oldCpid = -9999999

    # Format the yaxis.
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=0, top=1)
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Draw the axes.
    ax.plot_date(matplotlib.dates.date2num(times), numpy.arange(len(times)),
                 fmt='w', tz=None, xdate=True, ydate=False, alpha=0.0)

    # Label the CPIDs.
    for i in range(0, len(times)):
        if(cpid[i] != oldCpid):
            ax.plot_date([matplotlib.dates.date2num(times[i]),
                         matplotlib.dates.date2num(times[i])],
                         [0, 1], fmt='k-', tz=None, xdate=True, ydate=False)
            oldCpid = cpid[i]
            s = ' '+pydarn.radar.radUtils.getCpName(oldCpid)
            istr = ' '
            if(mode[i] == 1): istr = ' IF'
            if(mode == 0): istr = ' RF'
            ax.text(times[i], .5, ' ' + str(oldCpid) + s + istr, ha='left',
                    va='center', size=10)

    # Format the xaxis.
    xmin = matplotlib.dates.date2num(times[0])
    xmax = matplotlib.dates.date2num(times[len(times)-1])
    xrng = (xmax-xmin)
    inter = int(round(xrng/6.*86400.))
    inter2 = int(round(xrng/24.*86400.))
    ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
    ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(0)

    # Identify the CPID axis with a label.
    fig = ax.get_figure()
    bb = ax.get_position()
    x0 = bb.x0
    y0 = bb.y0
    height = bb.height
    width = bb.width
    pos = [x0, y0, width, height]
    fig.text(pos[0]-.07, pos[1]+pos[3]/2., 'CPID', ha='center', va='center',
             size=8.5, rotation='vertical')
    ax.set_yticks([])


def plot_skynoise(ax, times, sky, xlim=None, xticks=None):
    """Plots a noise panel at position pos.

    **Args**:
        * **ax**: a MPL axis object to plot to
        * **times**: a list of the times of the beam soundings
        * **sky**: a lsit of the noise.sky of the beam soundings
        * **search**: a list of the noise.search param
        * **[xlim]**: 2-element limits of the x-axis.  None for default.
        * **[xticks]**: List of xtick poisitions.  None for default.
    **Returns**:
        * Nothing

    **Example**:
        ::

            plot_skynoise(ax,times,sky)

    Written by AJ 20121002
    Modified by NAF 20131101
    Modified by ASR 20150916
    """

    # Format the yaxis.
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=0, top=6)
    ax.yaxis.set_minor_locator(MultipleLocator())
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Plot the sky noise data.
    ax.plot_date(matplotlib.dates.date2num(times), numpy.log10(sky), fmt='k-',
                 tz=None, xdate=True, ydate=False)

    # Format the xaxis.
    if xlim is not None: ax.set_xlim(xlim)
    if xticks is not None: ax.set_xticks(xticks)

    # Add labels to identify the noise axis.
    fig = ax.get_figure()
    bb = ax.get_position()
    x0 = bb.x0
    y0 = bb.y0
    height = bb.height
    width = bb.width
    pos = [x0, y0, width, height]
    fig.text(pos[0]-.01, pos[1]+.004, '10^0', ha='right', va='bottom', size=8)
    fig.text(pos[0]-.01, pos[1]+pos[3], '10^6', ha='right', va='top', size=8)
    fig.text(pos[0]-.07, pos[1]+pos[3]/2., 'N.Sky', ha='center', va='center',
             size=8.5, rotation='vertical')
    l = lines.Line2D([pos[0]-.06, pos[0]-.06], [pos[1]+.01, pos[1]+pos[3]-.01],
                     transform=fig.transFigure, clip_on=False, ls='-',
                     color='k', lw=1.5)
    ax.add_line(l)
    ax.set_xticklabels([' '])
    # Only use 2 major yticks.
    ax.set_yticks([0, 6])
    ax.set_yticklabels([' ', ' '])


def plot_searchnoise(ax, times, search, xlim=None, xticks=None,
                     ytickside='right'):
    """Plots a noise panel at position pos.

    **Args**:
        * **ax**: a MPL axis object to plot to
        * **times**: a list of the times of the beam soundings
        * **sky**: a lsit of the noise.sky of the beam soundings
        * **search**: a list of the noise.search param
        * **[xlim]**: 2-element limits of the x-axis.  None for default.
        * **[xticks]**: List of xtick poisitions.  None for default.
    **Returns**:
        * Nothing

    **Example**:
        ::

            plot_searchnoise(ax,times,search)

    Written by AJ 20121002
    Modified by NAF 20131101
    Modified by ASR 20150916
    """

    # Format the yaxis.
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=0, top=6)
    ax.yaxis.set_minor_locator(MultipleLocator())
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Plot the search noise data.
    ax.plot_date(matplotlib.dates.date2num(times), numpy.log10(search),
                 fmt='k:', tz=None, xdate=True, ydate=False, lw=1.5)

    # Format the xaxis.
    if xlim is not None: ax.set_xlim(xlim)
    if xticks is not None: ax.set_xticks(xticks)

    # Add labels to identify the noise axis.
    fig = ax.get_figure()
    bb = ax.get_position()
    x0 = bb.x0
    y0 = bb.y0
    height = bb.height
    width = bb.width
    pos = [x0, y0, width, height]

    fig.text(pos[0]+pos[2]+.01, pos[1]+.004, '10^0', ha='left', va='bottom',
             size=8)
    fig.text(pos[0]+pos[2]+.01, pos[1]+pos[3], '10^6', ha='left', va='top',
             size=8)
    fig.text(pos[0]+pos[2]+.06, pos[1]+pos[3]/2., 'N.Sch', ha='center',
             va='center', size=8.5, rotation='vertical')

    l = lines.Line2D([pos[0]+pos[2]+.07, pos[0]+pos[2]+.07],  [pos[1]+.01,
                     pos[1]+pos[3]-.01], transform=fig.transFigure,
                     clip_on=False, ls=':', color='k', lw=1.5)
    ax.add_line(l)
    ax.set_xticklabels([' '])
    # use only 2 major yticks
    ax.set_yticks([0, 6])
    ax.set_yticklabels([' ', ' '])
    if ytickside == 'right':
        ax.yaxis.tick_right()


def plot_freq(ax, times, freq, xlim=None, xticks=None):
    """Plots the tx frequency data to an axis object.

    **Args**:
        * **ax**: a MPL axis object to plot to
        * **times**: a list of the times of the beam soundings
        * **freq**: a lsit of the tfreq of the beam soundings
        * **search**: a list of the nave param
        * **[pos]**: position of the panel
        * **[xlim]**: 2-element limits of the x-axis.  None for default.
        * **[xticks]**: List of xtick poisitions.  None for default.
    **Returns**:
        *Nothing.

    **Example**:
        ::

            plot_freq(ax, times, tfreq)

    Written by AJ 20121002
    Modified by NAF 20131101
    Modified by ASR 20150916
    """

    # Format the yaxis.
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=8, top=20)
    ax.yaxis.set_minor_locator(MultipleLocator())
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Plot the TX frequency.
    ax.plot_date(matplotlib.dates.date2num(times), freq, fmt='k-',
                 tz=None, xdate=True, ydate=False, markersize=2)

    # Format the xaxis.
    if xlim is not None: ax.set_xlim(xlim)
    if xticks is not None: ax.set_xticks(xticks)

    # Add labels to identify the frequency axis.
    fig = ax.get_figure()
    bb = ax.get_position()
    x0 = bb.x0
    y0 = bb.y0
    height = bb.height
    width = bb.width
    pos = [x0, y0, width, height]
    fig.text(pos[0]-.01, pos[1]+.005, '10', ha='right', va='bottom',
             size=8)
    fig.text(pos[0]-.01, pos[1]+pos[3]-.015, '16', ha='right', va='top',
             size=8)
    fig.text(pos[0]-.07, pos[1]+pos[3]/2., 'Freq', ha='center', va='center',
             size=9, rotation='vertical')
    fig.text(pos[0]-.05, pos[1]+pos[3]/2., '[MHz]', ha='center', va='center',
             size=7, rotation='vertical')
    l = lines.Line2D([pos[0]-.04, pos[0]-.04],  [pos[1]+.01,
                     pos[1]+pos[3]-.01], transform=fig.transFigure,
                     clip_on=False, ls='-', color='k', lw=1.5)
    ax.add_line(l)
    ax.set_xticklabels([' '])
    # use only 2 major yticks
    ax.set_yticks([10, 16])
    ax.set_yticklabels([' ', ' '])


def plot_nave(ax, times, nave, xlim=None, xticks=None, ytickside='right'):
    """Plots the nave data to an axis object.

    **Args**:
        * **ax**: a MPL axis object to plot to
        * **times**: a list of the times of the beam soundings
        * **nave**: a lsit of the nave of the beam soundings
        * **search**: a list of the nave param
        * **[pos]**: position of the panel
        * **[xlim]**: 2-element limits of the x-axis.  None for default.
        * **[xticks]**: List of xtick poisitions.  None for default.
    **Returns**:
        *Nothing.

    **Example**:
        ::

            plot_nave(ax, times, nave)

    Written by AJ 20121002
    Modified by NAF 20131101
    Modified by ASR 20150916
    """

    # Format the yaxis
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=0, top=80)
    ax.yaxis.set_minor_locator(MultipleLocator(base=5))
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Plot the number of averages.
    ax.plot_date(matplotlib.dates.date2num(times), nave, fmt='k:',
                 tz=None, xdate=True, ydate=False, markersize=2)

    # Format the xaxis.
    if xlim is not None: ax.set_xlim(xlim)
    if xticks is not None: ax.set_xticks(xticks)

    # Add labels to identify the nave axis.
    fig = ax.get_figure()
    bb = ax.get_position()
    x0 = bb.x0
    y0 = bb.y0
    height = bb.height
    width = bb.width
    pos = [x0, y0, width, height]
    fig.text(pos[0]+pos[2]+.01, pos[1]-.004, '0', ha='left', va='bottom',
             size=8)
    fig.text(pos[0]+pos[2]+.01, pos[1]+pos[3], '80', ha='left', va='top',
             size=8)
    fig.text(pos[0]+pos[2]+.06, pos[1]+pos[3]/2., 'Nave', ha='center',
             va='center', size=8.5, rotation='vertical')

    l = lines.Line2D([pos[0]+pos[2]+.07, pos[0]+pos[2]+.07],  [pos[1]+.01,
                     pos[1]+pos[3]-.01], transform=fig.transFigure,
                     clip_on=False, ls=':', color='k', lw=1.5)
    ax.add_line(l)
    ax.set_xticklabels([' '])
    # use only 2 major yticks
    ax.set_yticks([0, 80])
    ax.set_yticklabels([' ', ' '])
    if ytickside == 'right':
        ax.yaxis.tick_right()


def read_data(myPtr, myBeam, bmnum, params, tbands):
    """Reads data from the file pointed to by myPtr

    **Args**:
        * **myPtr**: a davitpy file pointer object
        * **myBeam**: a davitpy beam object
        * **bmnum**: beam number of data to read in
        * **params**: a list of the parameters to read
        * **tbands**: a list of the frequency bands to separate data into
    **Returns**:
        * A dictionary of the data. Data is stored in lists and separated in
            to tbands.

    **Example**:
        ::
            from davitpy import pydarn
            from datetime import datetime
            myPtr = pydarn.sdio.radDataOpen(datetime(2012,11,24),'sas')
            myBeam = myPtr.readRec()
            data_dict = read_data(myPtr, myBeam, 7, ['velocity'], [8000,20000])

    Written by ASR 20150914
    """

    # Initialize some things.
    data = dict()
    data_keys = ['vel', 'pow', 'wid', 'elev', 'phi0', 'times', 'freq', 'cpid',
                 'nave', 'nsky', 'nsch', 'slist', 'mode', 'rsep', 'nrang',
                 'frang', 'gsflg', 'velocity_error']
    for d in data_keys:
        data[d] = []
        for i in range(len(tbands)):
            data[d].append([])

    # Read the parameters of interest.
    while(myBeam is not None):
        if(myBeam.time > myPtr.eTime): break
        if(myBeam.bmnum == bmnum and (myPtr.sTime <= myBeam.time)):
            for i in range(len(tbands)):
                if (myBeam.prm.tfreq >= tbands[i][0] and
                        myBeam.prm.tfreq <= tbands[i][1]):
                    data['times'][i].append(myBeam.time)
                    data['cpid'][i].append(myBeam.cp)
                    data['nave'][i].append(myBeam.prm.nave)
                    data['nsky'][i].append(myBeam.prm.noisesky)
                    data['rsep'][i].append(myBeam.prm.rsep)
                    data['nrang'][i].append(myBeam.prm.nrang)
                    data['frang'][i].append(myBeam.prm.frang)
                    data['nsch'][i].append(myBeam.prm.noisesearch)
                    data['freq'][i].append(myBeam.prm.tfreq/1e3)
                    data['slist'][i].append(myBeam.fit.slist)
                    data['mode'][i].append(myBeam.prm.ifmode)
                    # To save time and RAM, only keep the data specified
                    # in params.
                    if('velocity' in params):
                        data['vel'][i].append(myBeam.fit.v)
                    if('power' in params):
                        data['pow'][i].append(myBeam.fit.p_l)
                    if('width' in params):
                        data['wid'][i].append(myBeam.fit.w_l)
                    if('elevation' in params):
                        data['elev'][i].append(myBeam.fit.elv)
                    if('phi0' in params):
                        data['phi0'][i].append(myBeam.fit.phi0)
                    if('velocity_error' in params):
                        data['velocity_error'][i].append(myBeam.fit.v_e)
                    data['gsflg'][i].append(myBeam.fit.gflg)
        myBeam = myPtr.readRec()
    return data


def rti_panel(ax, data_dict, pArr, fplot, gsct, rad, bmnum, coords, cmap,
              norm, plot_terminator=True):

    """Plots the data given by pArr to an axis object.

    **Args**:
        * **ax**: a MPL axis object to plot to
        * **data_dict**: the data dictionary returned by
                pydarn.plotting.read_data
        * **pArr**: the list of data to be plotted (e.g. data_dict['vel'] for
                velocity)
        * **fplot**: the index of the frequency band of data to plot
        * **gsct**: a boolean stating whether to flag ground scatter
                data or not
        * **rad**: the 3 letter radar code
        * **bmnum**: The beam number of the data to plot
        * **coords**: plotting coordinates ('gate', 'range', 'geo', 'mag')
        * **cmap**: a matplotlib.colors.ListedColormap (such as that returned
                by utils.plotUtils.genCmap)
        * **norm**: a matplotlib.colors.BoundaryNorm (such as that returned by
                utils.plotUtils.genCmap)
        * **[plot_terminator]**: A boolean stating whether or not to plot
                the terminator
    **Returns**:
        *pcoll, the polygon collection returned by matplotib.pyplot.pcolormesh.

    Written by ASR 20150916
    """

    from davitpy import pydarn
    # Initialize things.
    rmax = max(data_dict['nrang'][fplot])
    tmax = (len(data_dict['times'][fplot]))*2
    data = numpy.zeros((tmax, rmax))*numpy.nan
    x = numpy.zeros(tmax)
    tcnt = 0

    # Build a list of datetimes to plot each data point at.
    dt_list = []
    for i in range(len(data_dict['times'][fplot])):
        x[tcnt] = matplotlib.dates.date2num(data_dict['times'][fplot][i])
        dt_list.append(data_dict['times'][fplot][i])

        if(i < len(data_dict['times'][fplot])-1):
            if(matplotlib.dates.date2num(
                    data_dict['times'][fplot][i+1])-x[tcnt] > 4./1440.):
                tcnt += 1
                # 1440 minutes in a day, hardcoded 1 minute step per data point
                # but only if time between data points is > 4 minutes
                x[tcnt] = x[tcnt-1]+1./1440.
                dt_list.append(matplotlib.dates.num2date(x[tcnt]))
        tcnt += 1

        if(pArr[i] == []): continue

        if data_dict['slist'][fplot][i] is not None:
            for j in range(len(data_dict['slist'][fplot][i])):
                if(not gsct or data_dict['gsflg'][fplot][i][j] == 0):
                    data[tcnt][data_dict['slist'][fplot][i][j]] = pArr[i][j]
                elif gsct and data_dict['gsflg'][fplot][i][j] == 1:
                    data[tcnt][data_dict['slist'][fplot][i][j]] = -100000.

    # For geo or mag coords, get radar FOV lats/lons.
    if (coords != 'gate' and coords != 'rng') or plot_terminator is True:
        site = pydarn.radar.network().getRadarByCode(rad) \
               .getSiteByDate(data_dict['times'][fplot][0])
        myFov = pydarn.radar.radFov.fov(site=site, ngates=rmax,
                                        nbeams=site.maxbeam,
                                        rsep=data_dict['rsep'][fplot][0],
                                        coords=coords,
                                        date_time=data_dict['times'][fplot][0])
        myLat = myFov.latCenter[bmnum]
        myLon = myFov.lonCenter[bmnum]

    # Determine the yaxis range limits to plot data to.
    if(coords == 'gate'):
        y = numpy.linspace(0, rmax, rmax+1)
    elif(coords == 'rng'):
        y = numpy.linspace(data_dict['frang'][fplot][0],
                           rmax*data_dict['rsep'][fplot][0],
                           rmax+1)
    else:
        y = myFov.latFull[bmnum]

    # Generate a mesh of x and y coords to plot data to.
    X, Y = numpy.meshgrid(x[:tcnt], y)

    # Calculate terminator as required.
    if plot_terminator:
        daylight = np.ones([len(dt_list), len(myLat)], np.bool)
        for tm_inx in range(len(dt_list)):
            tm = dt_list[tm_inx]
            term_lats, tau, dec = daynight_terminator(tm, myLon)
            if dec > 0:
                # NH Summer
                day_inx = np.where(myLat < term_lats)[0]
            else:
                day_inx = np.where(myLat > term_lats)[0]

            if day_inx.size != 0:
                daylight[tm_inx, day_inx] = False
            from numpy import ma
            daylight = ma.array(daylight, mask=daylight)
            ax.pcolormesh(X, Y, daylight.T, lw=0, alpha=0.10,
                          cmap=matplotlib.cm.binary_r, zorder=99)

    # Mask the nan's in the data array so they aren't plotted.
    Zm = numpy.ma.masked_where(numpy.isnan(data[:tcnt][:].T), data[:tcnt][:].T)
    # Set colormap so that masked data (bad) is transparent.
    cmap.set_bad('w', alpha=0.0)

    # Now let's plot all data.
    pcoll = ax.pcolormesh(X, Y, Zm, lw=0.01, edgecolors='None', lod=True,
                          cmap=cmap, norm=norm)

    return pcoll


def daynight_terminator(date, lons):
    """ Return the coordinates of day/night terminator for RTI plotting.

    **Args**:
        * **date**: a datetime.datetime object (assumed UTC)
        * **lons**: a numpy array of lons

    **Returns**:
        *lat, the latitude of the day night terminator
        *tau, grenwich hour angle
        *dec, solar declination

    """

    import mpl_toolkits.basemap.solar as solar
    dg2rad = np.pi/180.
    # compute greenwich hour angle and solar declination
    # from datetime object (assumed UTC).
    tau, dec = solar.epem(date)
    # compute day/night terminator from hour angle, declination.
    longitude = lons + tau
    lats = np.arctan(-np.cos(longitude*dg2rad)/np.tan(dec*dg2rad))/dg2rad
    return lats, tau, dec
