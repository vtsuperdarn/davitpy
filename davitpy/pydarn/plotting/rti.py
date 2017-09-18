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

"""Range-time-intensity plotting

A module for generating rti plots.

Module author: AJ, 20130123

Functions
--------------------------------------------------
plot_rti            range-time-intensity plot
plot_freq           TX frequency data
plot_searchnoise    noise panel
plot_skynoise       sky noise panel
plot_cpid           control program ID panel
plot_nave           number of averges panel
rti_title           title an rti plot
draw_axes           draw empty axes
read_data           read data in
rti_panel           plot the main rti data
daynight_terminator calculate day/night terminator
--------------------------------------------------

"""
import logging


def plot_rti(sTime, rad, eTime=None, bmnum=7, fileType='fitacf',
             params=['power', 'velocity', 'width'], scales=[], channel=None,
             coords='gate', colors='lasse', yrng=-1, gsct=False,
             low_gray=False, show=True, filtered=False,
             fileName=None, txfreq_lims=None, myFile=None,
             xtick_size=9, ytick_size=9,
             xticks=None, axvlines=None,
             plot_terminator=False, cpidchange_lims=20):

    """ Create an rti plot for a specified radar and time period.

    Parameters
    ----------
    sTime : datetime
        a datetime object indicating the start time which you would like
        to plot
    rad : str
        the 3 letter radar code, e.g. 'bks'
    eTime : Optional[datetime]
        a datetime object indicating th end time you would like plotted.
        If this is None, 24 hours will be plotted.  default = None.
    bmnum : Optional[int]
        The beam to plot.  default: 7
    fileType : Optional[str]
        The file type to be plotted, one of ['fitex', 'fitacf', 'lmfit'].
        default = 'fitex'.
    params : Optional[list]
        a list of the fit parameters to plot, allowable values are:
        ['velocity', 'power', 'width', 'elevation', 'phi0'].  default:
        ['velocity', 'power', 'width']
    scales : Optional[list]
        a list of the min/max values for the color scale for each param.
        If omitted, default scales will be used.  If present, the list
        should be n x 2 where n is the number of elements in the params
        list.  Use an empty list for default range, e.g. [[-250,300],[],[]].
        default: [[-200,200], [0,30],[0,150]]
    channel : Optional[char]
        the channel you wish to plot, e.g. 'a', 'b', 'c', ...  default: 'a'
    coords : Optional[str]
        the coordinates to use for the y axis.  The allowable values are
        'gate', 'rng', 'geo', 'mag' default: 'gate'
    colors : Optional[str]
        a string indicating what color bar to use, valid inputs are
        'lasse' or 'aj'. Also can be a list of matplotlib colormaps names,
        for example ['jet','jet','jet'] if len(param)==3. default: 'lasse'.
    yrng : Optional[list or -1]
        a list indicating the min and max values for the y axis in the
        chosen coordinate system, or a -1 indicating to plot everything.
        default: -1.
    gsct : Optional[boolean]
        a flag indicating whether to plot ground scatter as gray. default:
        False (ground scatter plotted normally)
    low_gray : Optional[boolean]
        a flag indicating whether to plot low velocity scatter as gray.
        default: False (low velocity scatter plotted normally)
    show : Optional[boolean]
        a flag indicating whether to display the figure on the screen.
        This can cause problems over ssh.  default = True
    filtered : Optional[boolean]
        a flag indicating whether to boxcar filter the data.  default:
        False (no filter)
    fileName : Optional[string]
        If you want to plot for a specific file, indicate the name of the
        file as fileName.  Include the type of the file in custType.
    txfreq_lims : Optional[list]
        a list of the min/max values for the transmitter frequencies in
        kHz.  If omitted, the default band will be used.  If more than
        one band is specified, retfig will cause only the last one to be
        returned.  default: [[8000,20000]]
    myFile : Optional[pydarn.sdio.radDataTypes.radDataPtr]
        contains the pipeline to the data we want to plot. If specified,
        data will be plotted from the file pointed to by myFile. default: None
    xtick_size : Optional[int]
        fontsize of xtick labels
    ytick_size : Optional[int]
        fontsize of ytick labels
    xticks : Optional[list]
        datetime.datetime objects indicating the location of xticks
    axvlines : Optoinal[list]
        datetime.datetime objects indicating the location vertical lines
        marking the plot
    plot_terminator : Optional[boolean]
        Overlay the day/night terminator.
    cpidchange_lims : Optional[int]
        Input the limit on the amount of CPID changes for the CPID
        panel.  Default is 20.


    Returns
    -------
    A list of figures of length len(tfreqbands)

    Example
    -------
        import datetime as dt
        pydarn.plotting.rti.plot_rti(dt.datetime(2013,3,16), 'bks',
                                     eTime=dt.datetime(2013,3,16,14,30),
                                     bmnum=12, fileType='fitacf',
                                     scales=[[-500,500],[],[]], coords='geo',
                                     colors='aj', filtered=True, show=True,
                                     cpidchange_lims=2)

    Written by AJ 20121002
    Modified by Matt W. 20130715
    Modified by Nathaniel F. 20131031 (added plot_terminator)
    Modified by ASR 20150917 (refactored)

    """

    import os
    from davitpy import pydarn
    from davitpy import utils
    import numpy as np
    from datetime import datetime, timedelta
    from matplotlib import pyplot
    from matplotlib.dates import DateFormatter
    import matplotlib.cm as cm

    # Time how long this is going to take
    timing_start = datetime.now()

    # NOTE TO DEVS: List of available params. Can be simply expanded
    # as more parameters are added to SuperDARN data set (like index
    # of refraction)
    available_params = ['power', 'velocity', 'width', 'elevation', 'phi0',
                        'velocity_error']
    default_scales = [[0, 30], [-200, 200], [0, 150], [0, 50],
                      [-np.pi, np.pi], [0, 200]]

    available_text = 'Allowable parameters are '
    for p in available_params:
        available_text = available_text + p + ', '
    available_text = available_text[:-2]

    # Check the inputs
    assert(isinstance(sTime, datetime)), logging.error(
        'sTime must be a datetime object')
    assert(isinstance(rad, str) and len(rad) == 3), logging.error(
        'rad must be a string 3 chars long')
    assert(isinstance(eTime, datetime) or
           eTime is None), (
        logging.error('eTime must be a datetime object or None'))
    if eTime is None:
        eTime = sTime + timedelta(days=1)
    assert(sTime < eTime), logging.error("eTime must be greater than sTime!")
    assert(coords == 'gate' or coords == 'rng' or coords == 'geo' or
           coords == 'mag'), logging.error("coords must be one of 'gate', "
                                           "'rng', 'geo', 'mag'")
    assert(isinstance(bmnum, int)), logging.error('beam must be integer')
    assert(0 < len(params) < 6), (
        logging.error('must input between 1 and 5 params in LIST form'))
    for i in range(0, len(params)):
        assert(params[i] in available_params), (
            logging.error(available_text))
    for i in range(0, len(scales)):
        assert(isinstance(scales[i], list)), (
            logging.error('each item in scales must be a list of upper and '
                          'lower bounds on paramaters.'))
    assert(scales == [] or
           len(scales) == len(params)), (
        logging.error('if present, scales must have same number of elements '
                      'as params'))
    assert(yrng == -1 or
           (isinstance(yrng, list) and
            yrng[0] <= yrng[1])), (
        logging.error('yrng must equal -1 or be a list with the 2nd element '
                      'larger than the first'))
    assert((colors == 'lasse' or
            colors == 'aj')) or isinstance(colors, list), (
        logging.error("Valid inputs for color are 'lasse' and 'aj' or a list "
                      "of matplotlib colormaps"))

    assert((isinstance(txfreq_lims, list) and len(txfreq_lims) == 2) or
           isinstance(txfreq_lims, type(None))), (
        logging.error("txfreq_lims must be a list with the start and "
                      "end frequencies"))
    assert((isinstance(cpidchange_lims, int) and cpidchange_lims > 0)), (
        logging.error("cpidchange_lims must be an integer and greater "
                      "than zero"))

    # Assign any default color scale parameter limits.
    tscales = []
    for i in range(0, len(params)):
        if(scales == [] or scales[i] == []):
            if(params[i] in available_params):
                ind = available_params.index(params[i])
                tscales.append(default_scales[ind])
        else: tscales.append(scales[i])
    scales = tscales

    # Assign default frequency band.
    if txfreq_lims is None:
        tband = [8000, 20000]
    else:
        assert(txfreq_lims[0] < txfreq_lims[1]), (
            logging.error("Starting frequency must be less "
                          "than ending frequency!"))
        tband = txfreq_lims

    # Open the file if a pointer was not given to us
    # if fileName is specified then it will be read.
    if not myFile:
        from davitpy.pydarn.sdio import radDataOpen
        myFile = radDataOpen(sTime, rad, eTime, channel=channel, bmnum=bmnum,
                             fileType=fileType, filtered=filtered,
                             fileName=fileName)

        # Check that we have data available now that we may have tried
        # to read it using radDataOpen.
        if myFile is None:
            logging.error('No files available for the requested '
                          'time/radar/filetype combination')
            return None

    # Make sure that we will only plot data for the time range specified
    # by sTime and eTime.
    if (myFile.sTime <= sTime and myFile.eTime > sTime and
            myFile.eTime >= eTime):
        myFile.sTime = sTime
        myFile.eTime = eTime
    else:
        # If the times range is not covered by the file, warn the user.
        logging.warning('Data not available in myFile for the whole of '
                        'sTime to eTime!')

    # Finally we can start reading the data file
    myBeam = myFile.readRec()
    if myBeam is None:
        logging.error('Problem reading the data.')
        return None

    # Now read the data that we need to make the plots
    data_dict = read_data(myFile, bmnum, params, tband)

    # Check to ensure that data exists for the requested frequency
    # band else continue on to the next range of frequencies
    if len(data_dict['freq']) == 0:
        logging.error('No data found in frequency range ' +
                      str(tband[0]) + ' kHz to ' +
                      str(tband[1]) + ' kHz')
        return None

    # Create a figure.
    rti_fig = pyplot.figure(figsize=(11, 8.5))

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
    plot_skynoise(skynoise_ax, data_dict['times'],
                  data_dict['nsky'])
    # Plot the search noise.
    plot_searchnoise(searchnoise_ax, data_dict['times'],
                     data_dict['nsch'])
    # plot the frequency bar.
    plot_freq(freq_ax, data_dict['times'],
              data_dict['freq'])
    # Plot the nave data.
    plot_nave(nave_ax, data_dict['times'],
              data_dict['nave'])
    # Plot the cpid bar
    plot_cpid(cpid_ax, data_dict['times'],
              data_dict['cpid'], data_dict['mode'],
              cpidchange_lims)

    # Plot each of the parameter panels.
    figtop = .77
    if ((eTime - sTime) <= timedelta(days=1)) and \
            (eTime.day == sTime.day):
        figheight = .72 / len(params)
    elif ((eTime - sTime) > timedelta(days=1)) or \
            (eTime.day != sTime.day):
        figheight = .70 / len(params)

    for p in range(len(params)):
        # Use draw_axes to create and set formatting of the axes to
        # plot to.
        pos = [.1, figtop - figheight * (p + 1) + .02, .76,
               figheight - .02]
        ax = draw_axes(rti_fig, data_dict['times'], rad,
                       data_dict['cpid'], bmnum,
                       data_dict['nrang'],
                       data_dict['frang'], data_dict['rsep'],
                       p == len(params) - 1, yrng=yrng, coords=coords,
                       pos=pos, xtick_size=xtick_size,
                       ytick_size=ytick_size, xticks=xticks,
                       axvlines=axvlines)

        if(params[p] == 'velocity'): pArr = data_dict['vel']
        elif(params[p] == 'power'): pArr = data_dict['pow']
        elif(params[p] == 'width'): pArr = data_dict['wid']
        elif(params[p] == 'elevation'): pArr = data_dict['elev']
        elif(params[p] == 'phi0'): pArr = data_dict['phi0']
        elif(params[p] == 'velocity_error'):
            pArr = data_dict['velocity_error']
        if(pArr == []): continue

        # Generate the color map.

        if colors in ['aj', 'lasse']:
            cmap, norm, bounds = utils.plotUtils.genCmap(params[p], scales[p],
                                                         colors=colors,
                                                         lowGray=low_gray)
        else:
            from matplotlib import colors as mpl_colors
            norm = mpl_colors.Normalize(vmin=scales[p][0], vmax=scales[p][1])
            cmap = cm.get_cmap(colors[p])

        # Plot the data to the axis object.
        pcoll = rti_panel(ax, data_dict, pArr, gsct, rad, bmnum, coords, cmap,
                          norm, plot_terminator=plot_terminator)

        # Set xaxis formatting depending on amount of data plotted.
        if ((eTime - sTime) <= timedelta(days=1)) and \
                (eTime.day == sTime.day):
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        elif ((eTime - sTime) > timedelta(days=1)) or \
                (eTime.day != sTime.day):
            ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%y \n%H:%M'))
        ax.set_xlabel('UT')

        # Draw the colorbar.
        cb = utils.drawCB(rti_fig, pcoll, cmap, norm, map_plot=0,
                          pos=[pos[0] + pos[2] + .02, pos[1], 0.02,
                               pos[3]])

        if colors in ['aj', 'lasse']:
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
                     params[p] == 'velocity_error')) or i == len(bounds) - 1):
                    l.append(' ')
                    continue
                l.append(str(int(bounds[i])))
            cb.ax.set_yticklabels(l)
        else:
            # Turn off the edges that are drawn by drawCB unless we are
            # doing 'aj' or 'lasse' colors
            cb.dividers.set_visible(False)

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

    logging.info('plotting took:' + str(datetime.now() - timing_start))

    return rti_fig


def draw_axes(myFig, times, rad, cpid, bmnum, nrang, frang, rsep, bottom,
              yrng=-1, coords='gate', pos=[.1, .05, .76, .72], xtick_size=9,
              ytick_size=9, xticks=None, axvlines=None):
    """ Draws empty axes for an rti plot.

    Parameters
    ----------
    myFig :
        the MPL figure we are plotting to
    times : list
        a list of datetime objects referencing the beam soundings
    rad : str
        3 letter radar code
    cpid : list
        list of the cpids or the beam soundings
    bmnum : int
        beam number being plotted
    nrang : list
        list of nrang for the beam soundings
    frang : list
        list of frang of the beam soundings
    rsep : list
        list of rsep of the beam soundings
    bottom : bool
        flag indicating if we are at the bottom of the figure
    yrng : Optional[list]
        range of y axis, -1=autoscale (default)
    coords : Optional[ ]
        y axis coordinate system, acceptable values are 'geo',
        'mag', 'gate', 'rng'
    pos : Optional[ ]
        position of the plot
    xtick_size : Optional[ ]
        fontsize of xtick labels
    ytick_size : Optional[ ]
        fontsize of ytick labels
    xticks : Optional[list]
        datetime.datetime objects indicating the location of xticks
    axvlines : Optional[list]
        datetime.datetime objects indicating the location vertical
        lines marking the plot

    Returns
    -------
    ax :
        an axes object

    Example
    -------
        ax = draw_axes(myFig,times,rad,cpid,beam,nrang,frang,rsep,0)

    Written by AJ 20121002
    Modified by ASR 20150917 (refactored)

    """

    from davitpy import pydarn
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter
    from matplotlib.dates import SecondLocator, DateFormatter, date2num
    from matplotlib.lines import Line2D
    import numpy as np

    nrecs = len(times)
    # Add an axes object to the figure.
    ax = myFig.add_axes(pos)
    ax.yaxis.set_tick_params(direction='out')
    ax.xaxis.set_tick_params(direction='out')
    ax.yaxis.set_tick_params(direction='out', which='minor')
    ax.xaxis.set_tick_params(direction='out', which='minor')

    # Draw the axes.
    ax.plot_date(date2num(times), np.arange(len(times)),
                 fmt='w', tz=None, xdate=True, ydate=False, alpha=0.0)

    # Determine the yaxis min/max unless it's been specified
    if(yrng == -1):
        ymin, ymax = 99999999, -999999999
        if(coords != 'gate'):
            oldCpid = -99999999
            for i in range(len(cpid)):
                if(cpid[i] == oldCpid): continue
                oldCpid = cpid[i]
                if(coords == 'geo' or coords == 'mag'):
                    # HACK NOT SURE IF YOU CAN DO THIS(Formatting)!
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
                    if(nrang[i] * rsep[i] + frang[i] > ymax):
                        ymax = nrang[i] * rsep[i] + frang[i]

        else:
            ymin, ymax = 0, max(nrang)
    else:
        ymin, ymax = yrng[0], yrng[1]

    # Format the xaxis.
    xmin = date2num(times[0])
    xmax = date2num(times[len(times) - 1])
    xrng = (xmax - xmin)
    inter = int(round(xrng / 6. * 86400.))
    inter2 = int(round(xrng / 24. * 86400.))
    ax.xaxis.set_minor_locator(SecondLocator(interval=inter2))
    ax.xaxis.set_major_locator(SecondLocator(interval=inter))

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
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        ax.xaxis.set_label_text('UT')

    # Set ytick size.
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(ytick_size)
    # Format yaxis depending on coords.
    if(coords == 'gate'):
        ax.yaxis.set_label_text('Range gate', size=10)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.yaxis.set_major_locator(MultipleLocator((ymax - ymin) / 5.))
        ax.yaxis.set_minor_locator(MultipleLocator((ymax - ymin) / 25.))
    elif(coords == 'geo' or coords == 'mag'):
        if(coords == 'mag'):
            ax.yaxis.set_label_text('Mag Lat [deg]', size=10)
        else:
            ax.yaxis.set_label_text('Geo Lat [deg]', size=10)
    elif(coords == 'rng'):
        ax.yaxis.set_label_text('Slant Range [km]', size=10)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.yaxis.set_major_locator(MultipleLocator(1000))
        ax.yaxis.set_minor_locator(MultipleLocator(250))
    ax.set_ylim(bottom=ymin, top=ymax)

    return ax


def rti_title(fig, sTime, rad, fileType, beam, eTime=None, xmin=.1, xmax=.86):
    """Draws title for an rti plot.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        a matplotlib.figure.Figure object
    sTime : datetime
        the start time for the data being plotted as a datetime object
    rad : str
        the 3 letter radar code
    fileType : str
        the file type being plotted
    beam : int
        the beam number being plotted
    eTime : Optional[datetime]
        the end time for the data being plotted as a datetime object
    xmin : Optional[ ]
        minimum x value o the plot in page coords
    xmax : Optional[ ]
        maximum x value o the plot in page coords

    Returns
    -------
    Nothing.

    Example
    -------
        import datetime as dt
        from matplotlib import pyplot
        fig = pyplot.figure()
        rti_title(fig,dt.datetime(2011,1,1),'bks','fitex',7)

    Written by AJ 20121002
    Modified by ASR 20150916

    """
    from davitpy import pydarn
    from datetime import timedelta
    import calendar

    # Obtain the davitpy.pydarn.radar.radStruct.radar object for rad.
    r = pydarn.radar.network().getRadarByCode(rad)

    # Plot the main title
    fig.text(xmin, .95, r.name + '  (' + fileType + ')', ha='left', weight=550)

    # Determine what time information should be plotted in the secondary title
    if ((eTime is not None) and
        (((eTime - sTime) > timedelta(days=1)) or
         (eTime.day != sTime.day))):
        title_text = str(sTime.day) + ' ' \
            + calendar.month_name[sTime.month][:3] + ' ' \
            + str(sTime.year) + ' - ' + str(eTime.day) + ' ' \
            + calendar.month_name[eTime.month][:3] + ' ' \
            + str(eTime.year)

    else:
        title_text = str(sTime.day) + ' ' \
            + calendar.month_name[sTime.month][:3] + ' ' \
            + str(sTime.year)

    # Plot the secondary title.
    fig.text((xmin + xmax) / 2., .95, title_text, weight=550,
             size='large', ha='center')
    fig.text(xmax, .95, 'Beam ' + str(beam), weight=550, ha='right')


def plot_cpid(ax, times, cpid, mode, cpidchange_lims):
    """Plots control program ID (cpid) panel at position pos.

    Parameters
    ----------
    ax :
        a MPL axis object to plot to
    times : list
        a list of the times of the beam soundings
    cpid : list
        a list of the cpids of the beam soundings.
    mode : list
        a list of the ifmode param
    cpidchange_lims : int
        Limit on the number of times the cpid can change


    Returns
    -------
    Nothing.

    Example
    -------
        plot_cpid(ax,times,cpid,mode, cpidchange_lims=10)

    Written by AJ 20121002
    Modified by ASR 20150916

    """
    from davitpy import pydarn
    from matplotlib.ticker import MultipleLocator
    from matplotlib.dates import SecondLocator
    from matplotlib.dates import date2num
    from datetime import timedelta
    import numpy as np
    oldCpid = -9999999

    # Format the yaxis.
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=0, top=1)
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Draw the axes.
    ax.plot_date(date2num(times), np.arange(len(times)),
                 fmt='w', tz=None, xdate=True, ydate=False, alpha=0.0)

    # Initialize CPID change counter
    cpid_change = 0
    # Label the CPIDs.
    for i in range(0, len(times)):
        if(cpid[i] != oldCpid):
            cpid_change += 1
            # If the cpid is changing too much, it won't be readible
            if (cpid_change >= cpidchange_lims):
                # Clear the current axis
                ax.cla()
                # Kick out error messages
                diff_time = (times[-1] - times[0]).total_seconds() / 2.
                cpid_time = times[0] + timedelta(seconds=diff_time)
                temp = ', '.join([str(x) for x in list(set(cpid))])
                cpid_text = 'CPIDs: ' + temp
                ax.text(cpid_time, .5, cpid_text,
                        ha='center', va='center', size=10)
                logging.error('CPID is changing too frequently to be '
                              'legibly printed. Please consider using '
                              'radDataOpen cp param. CPIDs found: ' +
                              str(list(set(cpid))))
                break
            ax.plot_date([date2num(times[i]), date2num(times[i])],
                         [0, 1], fmt='k-', tz=None, xdate=True, ydate=False)
            oldCpid = cpid[i]
            s = ' ' + pydarn.radar.radUtils.getCpName(oldCpid)
            istr = ' '
            if(mode[i] == 1): istr = ' IF'
            if(mode == 0): istr = ' RF'
            ax.text(times[i], .5, ' ' + str(oldCpid) + s + istr, ha='left',
                    va='center', size=10)

    # Format the xaxis.
    xmin = date2num(times[0])
    xmax = date2num(times[len(times) - 1])
    xrng = (xmax - xmin)
    inter = int(round(xrng / 6. * 86400.))
    inter2 = int(round(xrng / 24. * 86400.))
    ax.xaxis.set_minor_locator(SecondLocator(interval=inter2))
    ax.xaxis.set_major_locator(SecondLocator(interval=inter))

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
    fig.text(pos[0] - .07, pos[1] + pos[3] / 2., 'CPID', ha='center',
             va='center', size=8.5, rotation='vertical')
    ax.set_yticks([])


def plot_skynoise(ax, times, sky, xlim=None, xticks=None):
    """Plots a noise panel at position pos.

    Parameters
    ----------
    ax :
        a MPL axis object to plot to
    times : list
        a list of the times of the beam soundings
    sky: list
        a list of the noise.sky of the beam soundings
    search : list
        a list of the noise.search param
    xlim : Optional[list]
        2-element limits of the x-axis.  None for default.
    xticks : Optional[list]
        List of xtick poisitions.  None for default.

    Returns
    -------
    Nothing

    Example
    -------
        plot_skynoise(ax,times,sky)

    Written by AJ 20121002
    Modified by NAF 20131101
    Modified by ASR 20150916

    """

    from matplotlib.ticker import MultipleLocator
    from matplotlib.dates import date2num
    from matplotlib.lines import Line2D
    import numpy as np

    # Format the yaxis.
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=0, top=6)
    ax.yaxis.set_minor_locator(MultipleLocator())
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Plot the sky noise data.
    ax.plot_date(date2num(times), np.log10(sky), fmt='k-',
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
    fig.text(pos[0] - .01, pos[1] + .004, '10^0', ha='right', va='bottom',
             size=8)
    fig.text(pos[0] - .01, pos[1] + pos[3], '10^6', ha='right', va='top',
             size=8)
    fig.text(pos[0] - .07, pos[1] + pos[3] / 2., 'N.Sky', ha='center',
             va='center', size=8.5, rotation='vertical')
    l = Line2D([pos[0] - .06, pos[0] - .06], [pos[1] + .01,
               pos[1] + pos[3] - .01], transform=fig.transFigure,
               clip_on=False, ls='-', color='k', lw=1.5)
    ax.add_line(l)
    ax.set_xticklabels([' '])
    # Only use 2 major yticks.
    ax.set_yticks([0, 6])
    ax.set_yticklabels([' ', ' '])


def plot_searchnoise(ax, times, search, xlim=None, xticks=None,
                     ytickside='right'):
    """Plots a noise panel at position pos.

    Parameters
    ----------
    ax :
        a MPL axis object to plot to
    times : list
        a list of the times of the beam soundings
    sky : list
        a list of the noise.sky of the beam soundings
    search : list
        a list of the noise.search param
    xlim : Optional[list]
        2-element limits of the x-axis.  None for default.
    xticks : Optional[list]
        List of xtick poisitions.  None for default.
    ytickside : Optional[string]
        Default is right.

    Returns
    -------
    Nothing

    Example
    -------
        plot_searchnoise(ax,times,search)

    Written by AJ 20121002
    Modified by NAF 20131101
    Modified by ASR 20150916

    """

    from matplotlib.ticker import MultipleLocator
    from matplotlib.dates import date2num
    from matplotlib.lines import Line2D
    import numpy as np

    # Format the yaxis.
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=0, top=6)
    ax.yaxis.set_minor_locator(MultipleLocator())
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Plot the search noise data.
    ax.plot_date(date2num(times), np.log10(search),
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

    fig.text(pos[0] + pos[2] + .01, pos[1] + .004, '10^0', ha='left',
             va='bottom', size=8)
    fig.text(pos[0] + pos[2] + .01, pos[1] + pos[3], '10^6', ha='left',
             va='top', size=8)
    fig.text(pos[0] + pos[2] + .06, pos[1] + pos[3] / 2., 'N.Sch', ha='center',
             va='center', size=8.5, rotation='vertical')

    l = Line2D([pos[0] + pos[2] + .07, pos[0] + pos[2] + .07],
               [pos[1] + .01, pos[1] + pos[3] - .01],
               transform=fig.transFigure, clip_on=False, ls=':',
               color='k', lw=1.5)
    ax.add_line(l)
    ax.set_xticklabels([' '])
    # use only 2 major yticks
    ax.set_yticks([0, 6])
    ax.set_yticklabels([' ', ' '])
    if ytickside == 'right':
        ax.yaxis.tick_right()


def plot_freq(ax, times, freq, xlim=None, xticks=None):
    """Plots the tx frequency data to an axis object.

    Parameters
    ----------
    ax :
        a MPL axis object to plot to
    times : list
        a list of the times of the beam soundings
    freq : list
        a list of the tfreq of the beam soundings
    xlim : Optional[list]
        2-element limits of the x-axis.  None for default.
    xticks : Optional[list]
        List of xtick poisitions.  None for default.

    Returns
    -------
    Nothing.


    Example
    -------
        plot_freq(ax, times, tfreq)

    Written by AJ 20121002
    Modified by NAF 20131101
    Modified by ASR 20150916

    """

    from matplotlib.ticker import MultipleLocator
    from matplotlib.dates import date2num
    from matplotlib.lines import Line2D

    # Format the yaxis.
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=8, top=20)
    ax.yaxis.set_minor_locator(MultipleLocator())
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Plot the TX frequency.
    ax.plot_date(date2num(times), freq, fmt='k-',
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
    fig.text(pos[0] - .01, pos[1] + .005, '10', ha='right', va='bottom',
             size=8)
    fig.text(pos[0] - .01, pos[1] + pos[3] - .015, '16', ha='right', va='top',
             size=8)
    fig.text(pos[0] - .07, pos[1] + pos[3] / 2., 'Freq', ha='center',
             va='center', size=9, rotation='vertical')
    fig.text(pos[0] - .05, pos[1] + pos[3] / 2., '[MHz]', ha='center',
             va='center', size=7, rotation='vertical')
    l = Line2D([pos[0] - .04, pos[0] - .04], [pos[1] + .01,
               pos[1] + pos[3] - .01], transform=fig.transFigure,
               clip_on=False, ls='-', color='k', lw=1.5)
    ax.add_line(l)
    ax.set_xticklabels([' '])
    # use only 2 major yticks
    ax.set_yticks([10, 16])
    ax.set_yticklabels([' ', ' '])


def plot_nave(ax, times, nave, xlim=None, xticks=None, ytickside='right'):
    """Plots the number of averages (nave) data to an axis object.

    Parameters
    ----------
    ax :
        a MPL axis object to plot to
    times : list
        a list of the times of the beam soundings
    nave : list
        a list of the nave of the beam soundings
    xlim : Optional[list]
        2-element limits of the x-axis.  None for default.
    xticks : Optional[list]
        List of xtick poisitions.  None for default.
    ytickside : Optional[str]
        Default is right.

    Returns
    -------
    Nothing.

    Example
    -------
        plot_nave(ax, times, nave)

    Written by AJ 20121002
    Modified by NAF 20131101
    Modified by ASR 20150916

    """

    from matplotlib.ticker import MultipleLocator
    from matplotlib.dates import date2num
    from matplotlib.lines import Line2D

    # Format the yaxis
    ax.yaxis.tick_left()
    ax.yaxis.set_tick_params(direction='out')
    ax.set_ylim(bottom=0, top=80)
    ax.yaxis.set_minor_locator(MultipleLocator(base=5))
    ax.yaxis.set_tick_params(direction='out', which='minor')

    # Plot the number of averages.
    ax.plot_date(date2num(times), nave, fmt='k:',
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
    fig.text(pos[0] + pos[2] + .01, pos[1] - .004, '0', ha='left', va='bottom',
             size=8)
    fig.text(pos[0] + pos[2] + .01, pos[1] + pos[3], '80', ha='left', va='top',
             size=8)
    fig.text(pos[0] + pos[2] + .06, pos[1] + pos[3] / 2., 'Nave', ha='center',
             va='center', size=8.5, rotation='vertical')

    l = Line2D([pos[0] + pos[2] + .07, pos[0] + pos[2] + .07],
               [pos[1] + .01, pos[1] + pos[3] - .01],
               transform=fig.transFigure, clip_on=False, ls=':',
               color='k', lw=1.5)
    ax.add_line(l)
    ax.set_xticklabels([' '])
    # use only 2 major yticks
    ax.set_yticks([0, 80])
    ax.set_yticklabels([' ', ' '])
    if ytickside == 'right':
        ax.yaxis.tick_right()


def read_data(myPtr, bmnum, params, tbands):
    """Reads data from the file pointed to by myPtr

    Parameter
    ---------
    myPtr :
        a davitpy file pointer object
    bmnum : int
        beam number of data to read in
    params : list
        a list of the parameters to read
    tbands : list
        a list of the frequency bands to separate data into

    Returns
    -------
    A dictionary of the data. Data is stored in lists and separated in
    to tbands.

    Example
    -------
        from davitpy import pydarn
        from datetime import datetime
        myPtr = pydarn.sdio.radDataOpen(datetime(2012,11,24),'sas')
        myBeam = myPtr.readRec()
        data_dict = read_data(myPtr, myBeam, 7, ['velocity'], [8000,20000])

    Written by ASR 20150914

    """

    import numpy as np

    # Initialize some things.
    data = dict()
    data_keys = ['vel', 'pow', 'wid', 'elev', 'phi0', 'times', 'freq', 'cpid',
                 'nave', 'nsky', 'nsch', 'slist', 'mode', 'rsep', 'nrang',
                 'frang', 'gsflg', 'velocity_error']
    for d in data_keys:
        data[d] = []

    # Read the parameters of interest.
    myPtr.rewind()
    myBeam = myPtr.readRec()
    while(myBeam is not None):
        if(myBeam.time > myPtr.eTime): break
        if(myBeam.bmnum == bmnum and (myPtr.sTime <= myBeam.time)):
            if (myBeam.prm.tfreq >= tbands[0] and
                    myBeam.prm.tfreq <= tbands[1]):
                data['times'].append(myBeam.time)
                data['cpid'].append(myBeam.cp)
                data['nave'].append(myBeam.prm.nave)
                data['nsky'].append(myBeam.prm.noisesky)
                data['rsep'].append(myBeam.prm.rsep)
                data['nrang'].append(myBeam.prm.nrang)
                data['frang'].append(myBeam.prm.frang)
                data['nsch'].append(myBeam.prm.noisesearch)
                data['freq'].append(myBeam.prm.tfreq / 1e3)
                data['slist'].append(myBeam.fit.slist)
                data['mode'].append(myBeam.prm.ifmode)
                data['gsflg'].append(myBeam.fit.gflg)
                # To save time and RAM, only keep the data specified
                # in params.
                if('velocity' in params):
                    data['vel'].append(myBeam.fit.v)
                if('power' in params):
                    data['pow'].append(myBeam.fit.p_l)
                if('width' in params):
                    data['wid'].append(myBeam.fit.w_l)
                if('elevation' in params):
                    data['elev'].append(myBeam.fit.elv)
                if('phi0' in params):
                    data['phi0'].append(myBeam.fit.phi0)
                if('velocity_error' in params):
                    data['velocity_error'].append(myBeam.fit.v_e)

        myBeam = myPtr.readRec()
    return data


def rti_panel(ax, data_dict, pArr, gsct, rad, bmnum, coords, cmap,
              norm, plot_terminator=True):
    """Plots the data given by pArr to an axis object.

    Parameters
    ----------
    ax :
        a MPL axis object to plot to
    data_dict :
        the data dictionary returned by pydarn.plotting.read_data
    pArr : list
        the list of data to be plotted (e.g. data_dict['vel'] for
        velocity)
    gsct : bool
        a boolean stating whether to flag ground scatter data or not
    rad : str
        the 3 letter radar code
    bmnum : int
        The beam number of the data to plot
    coords : str
        plotting coordinates ('gate', 'range', 'geo', 'mag')
    cmap :
        a matplotlib.colors.ListedColormap (such as that returned
        by utils.plotUtils.genCmap)
    norm :
        a matplotlib.colors.BoundaryNorm (such as that returned by
        utils.plotUtils.genCmap)
    plot_terminator : Optional[bool]
        A boolean stating whether or not to plot the terminator; default
        is true.

    Returns
    -------
    pcoll
        the polygon collection returned by matplotib.pyplot.pcolormesh.

    Written by ASR 20150916

    """
    from davitpy import pydarn
    import matplotlib
    from matplotlib.dates import date2num, num2date
    import numpy as np

    # Initialize things.
    rmax = max(data_dict['nrang'])
    tmax = (len(data_dict['times'])) * 2
    data = np.zeros((tmax, rmax)) * np.nan
    x = np.zeros(tmax)
    tcnt = 0

    # Build a list of datetimes to plot each data point at.
    dt_list = []
    for i in range(len(data_dict['times'])):
        x[tcnt] = date2num(data_dict['times'][i])
        dt_list.append(data_dict['times'][i])

        if(i < len(data_dict['times']) - 1):
            if(date2num(data_dict['times'][i + 1]) - x[tcnt] > 4. / 1440.):
                tcnt += 1
                # 1440 minutes in a day, hardcoded 1 minute step per data point
                # but only if time between data points is > 4 minutes
                x[tcnt] = x[tcnt - 1] + 1. / 1440.
                dt_list.append(num2date(x[tcnt]))
        tcnt += 1

        if(pArr[i] == [] or pArr[i] is None): continue

        if data_dict['slist'][i] is not None:
            for j in range(len(data_dict['slist'][i])):
                if(not gsct or data_dict['gsflg'][i][j] == 0):
                    data[tcnt][data_dict['slist'][i][j]] = pArr[i][j]
                elif gsct and data_dict['gsflg'][i][j] == 1:
                    data[tcnt][data_dict['slist'][i][j]] = -100000.

    # For geo or mag coords, get radar FOV lats/lons.
    if (coords != 'gate' and coords != 'rng') or plot_terminator is True:
        site = pydarn.radar.network().getRadarByCode(rad) \
            .getSiteByDate(data_dict['times'][0])
        myFov = pydarn.radar.radFov.fov(site=site, ngates=rmax,
                                        nbeams=site.maxbeam,
                                        rsep=data_dict['rsep'][0],
                                        coords=coords,
                                        date_time=data_dict['times'][0])
        myLat = myFov.latCenter[bmnum]
        myLon = myFov.lonCenter[bmnum]

    # Determine the yaxis range limits to plot data to.
    if(coords == 'gate'):
        y = np.linspace(0, rmax, rmax + 1)
    elif(coords == 'rng'):
        y = np.linspace(data_dict['frang'][0],
                        rmax * data_dict['rsep'][0],
                        rmax + 1)
    else:
        y = myFov.latFull[bmnum]

    # Generate a mesh of x and y coords to plot data to.
    X, Y = np.meshgrid(x[:tcnt], y)

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
        daylight = np.ma.array(daylight, mask=daylight)
        ax.pcolormesh(X, Y, daylight.T, lw=0, alpha=0.10,
                      cmap=matplotlib.cm.binary_r, zorder=99)

    # Mask the nan's in the data array so they aren't plotted.
    Zm = np.ma.masked_where(np.isnan(data[:tcnt][:].T), data[:tcnt][:].T)
    # Set colormap so that masked data (bad) is transparent.
    cmap.set_bad('w', alpha=0.0)

    # Now let's plot all data.
    pcoll = ax.pcolormesh(X, Y, Zm, lw=0.01, edgecolors='None',
                          cmap=cmap, norm=norm)

    return pcoll


def daynight_terminator(date, lons):
    """ Return the coordinates of day/night terminator for RTI plotting.

    Parameters
    ----------
    date : datetime.datetime
        a datetime.datetime object (assumed UTC)
    lons : list
        a numpy array of lons

    Returns
    -------
    lat
        the latitude of the day night terminator
    tau
        grenwich hour angle
    dec
        solar declination

    """
    import mpl_toolkits.basemap.solar as solar
    import numpy as np

    dg2rad = np.pi / 180.
    # compute greenwich hour angle and solar declination
    # from datetime object (assumed UTC).
    tau, dec = solar.epem(date)
    # compute day/night terminator from hour angle, declination.
    longitude = lons + tau
    lats = np.arctan(-np.cos(longitude * dg2rad) /
                     np.tan(dec * dg2rad)) / dg2rad
    return lats, tau, dec
