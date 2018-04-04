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
"""The fan module

Module generating fan plots

Methods
-----------------------------------------
plotFan     plot a scan of data
overlayFan  plot a scan of data on a map
-----------------------------------------

"""

# standard libraries
import numpy
import math
import matplotlib.pyplot as plot
from datetime import datetime, timedelta
from matplotlib.collections import PolyCollection, LineCollection
import matplotlib.patches as patches

# local libraries
from davitpy import utils, gme
from davitpy.pydarn.radar import site, radFov
from davitpy.pydarn.plotting.mapOverlay import overlayFov, overlayRadar
from davitpy.pydarn.sdio.radDataRead import radDataOpen, radDataReadRec
from davitpy.pydarn.sdio import beamData
from davitpy.utils.coordUtils import coord_conv
from davitpy.utils.davitpy_exceptions import DavitpyNoDataFoundError


def plotFan(sTime, rad, interval=60, fileType='fitex', param='velocity',
            filtered=False, fileName='', myFiles=[], scale=[], channel=None,
            coords='geo', colors='lasse', gsct=False, fov=True,
            edgeColors='face', lowGray=False, fill=True, velscl=1000.,
            legend=True, overlayPoes=False, poesparam='ted', poesMin=-3.,
            poesMax=0.5, poesLabel=r"Total Log Energy Flux [ergs cm$^{-2}$ s$^{-1}$]",
            overlayBnd=False, show=True, extension="ps", dpi=500,
            tFreqBands=[]):
    """A function to make a fan plot

    Parameters
    ----------
    sTime : datetime
        The start time you want to plot
    rad
        A list of 3 letter radar codes, e.g. ['bks'], e.g. ['bks','wal','gbr']
    interval : Optional[int]
        The the time period to be plotted, in seconds.  default = 60
    fileType : Optional[str]
        The file type to plot, valid inputs are 'fitex','fitacf', 'lmfit'.
        default = 'fitex'
    param : Optional[str]
        The parameter to be plotted, valid inputs are 'velocity', 'power',
        'width', 'elevation', 'phi0'.  default = 'velocity'
    filtered : Optional[boolean]
        A flag indicating whether the data should be boxcar filtered.
        default = False
    fileName : Optional[string]
        The filename you wish to save the fan plot image as.
    myFiles : optional[list of pydarn.sdio.radDataTyoes.radDatPtr]
        contains the pipeline to the data that you want to plot. If specified,
        then the datafiles will be used, otherwise the remote data will be used.
        default: []
    scale : Optional[list]
        The min and max values of the color scale, i.e. [min,max].  If this is
        set to [], then default values will be used
    channel : Optional[char]
        The channel for which to plot data.  default = 'a'
    coords : Optional[str]
        The coordinate system to use; valid inputs are anything handled by
        coord_conv (see davitpy.utils.get_coord_dict).  Default:  geo
    colors : Optional[str]
        The color map to use, valid inputs are 'lasse', 'aj'.
        default = 'lasse'
    gsct : Optional[boolean]
        A flag indicating whether to plot ground scatter as gray.
        default = False
    fov : Optional[boolean]
        A flag indicating whether to overplot the radar fields of view.
        default = True
    edgeColors : Optional[str]
        Edge colors of the polygons, default = 'face'
    lowGray : Optional[boolean]
        A flag indicating whether to plot low velocities in gray.
        default = False
    fill : Optional[boolean]
        A flag indicating whether to plot filled or point RB cells.
        default = True
    velscl : Optional[float]
        The velocity to use as baseline for velocity vector length, only
        applicable if fill = 0.  default = 1000
    legend : Optional[boolean]
        A flag indicating whether to plot the legend, only applicable if
        fill = 0.  default = True
    overlayPoes : Optional[boolean]
        A flag indicating whether to overlay poes data.  default = False
    poesparam : Optional[str]
        The poes parameter to plot.  default = 'ted'.  available params can be
        found in :class:`gme.sat.poes.poesRec`
    poesMin : Optional[float]
        The min value for the poes data color scale.  default = -3.
    poesMax : Optional[float]
        The max value for the poes data color scale.  default = 0.5
    poesLabel : Optional[str]
        The label for the poes color bar.  default = r"Total Log Energy Flux
        [ergs cm$^{-2}$ s$^{-1}$]"
    overlayBnd : Optional[boolean]
        A flag indicating whether to plot an auroral boundary determined from
        fitting poes data.  default = False
    show : Optional[boolean]
        A flag indicating whether to display the figure on the screen.  This
        can cause problems over ssh.  default = True
    extension : Optional[string]
        String repersenting the extention you wish to save the image in.
        Do not include the period, the extension postfix.
        default: "ps"
    dpi : Optional[int]
        Dots per inch if saving as png.  default = 300
    tFreqBands : optional
        Upper and lower bounds of frequency in kHz to be used.  Must be unset
        (or set to []) or have a pair for each radar, and for any band set to
        [] the default will be used.  default = [[8000,20000]],
        [[8000,20000],[8000,20000]], etc.

    Returns
    -------
    Nothing

    Examples
    --------
        import datetime as dt
        pydarn.plotting.fan.plotFan(datetime(2013,3,16,16,30),['fhe','fhw'],param='power',gsct=True)
        pydarn.plotting.fan.plotFan(datetime(2013,3,16,16,30),['fhe','fhw'],param='power',gsct=True,tFreqBands=[[10000,11000],[]])

    Modified by Marina Schmidt 20180312
    """
    # Plese avoid import libraries in the function this leads to circular dependencies which should not exist in the first place.
    # Very bad practice. If you do need to import in a function try to use conditionals as the library may not exist.
    possible_params = ["velocity", "power", "width", "elevation", "phi0"]
    color_options = ["lasse", "aj"]
    # Do not use asserts to throw exceptions, this is bad practice because it is unclear what the exception is about.
    # Also raising built in exceptions is the beauty of python :)
    if not isinstance(sTime, datetime):
        raise TypeError('sTime must be a datetime object')
    if not isinstance(rad, list):
        raise TypeError("rad must be a list, eg ['bks'] or ['bks','fhe']")

    for r in rad:
        if not isinstance(r, str) and len(r) == 3:
            raise TypeError('error, elements of rad '
                            'list must be 3 letter strings')
    if param not in possible_params:
        raise ValueError(" {} is not an allowable param. The possible params"
                         "are 'velocity','power','width','elevation',"
                         "'phi0'".format(param))
    # For non clear error messages please include the value of the parameter
    # or more information on which condition was not met, this helps the user to understand the expectations of the code
    if scale != [] and len(scale) != 2:
        raise ValueError("The length of scale is {}."
                         " Scale must have 2 elements".format(len(scale)))
    if colors not in color_options:
        raise ValueError("{} is not a valid color option. Possible colors are"
                         " 'lasse' and 'aj'".format(colors))

    # check freq band and set to default if needed
    if tFreqBands != [] and len(tFreqBands) != len(rad):
        raise ValueError("tFreeBands: {lfreqbands} and rad: {lrad} are "
                         "not the same length.tFreqBands must have "
                         "same number of elements "
                         "as rad".format(lfreqbands=len(tFreqBands),
                                         lrad=len(rad)))
    tbands = []
    for i in range(len(rad)):
        if tFreqBands == [] or tFreqBands[i] == []:
            tbands.append([8000, 20000])
        else:
            tbands.append(tFreqBands[i])
        if tbands[i][1] < tbands[i][0]:
            raise TypeError("Frequency upper bound {ub} must "
                            " be > lower bound {lb}".format(tbands[i][1],
                                                            tbands[i][0]))

    # Best practice is to indent if statements clauses instead of having them
    # on one line. It is less error prone if someone wants to add something to
    # this statement and matches PEP8 style.
    if scale == []:
        if param == 'velocity':
            scale = [-200, 200]
        elif param == 'power':
            scale = [0, 30]
        elif param == 'width':
            scale = [0, 150]
        elif param == 'elevation':
            scale = [0, 50]
        elif param == 'phi0':
            scale = [-numpy.pi, numpy.pi]

    cmap, norm, bounds = utils.plotUtils.genCmap(param, scale, colors=colors,
                                                 lowGray=lowGray)

    # TODO: remove file fetching. File fetching should be its own class, plotting should only have to worry about plotting. This will help with flexibility and bugs.
    myBands = []
    for i in range(len(rad)):
        if len(myFiles)-1 < i:  # TODO: Do we want to continue if there is no data for 1 of the radars? Is the order kept including when reading in files?
            myFiles.append(radDataOpen(sTime, rad[i],
                                       sTime + timedelta(seconds=interval),
                                       fileType=fileType,
                                       filtered=filtered,
                                       channel=channel))
        if myFiles[i]:
            myBands.append(tbands[i])

    if len(myFiles) == 0:
        pass
        #raise DavitpyNoDataFoundError("No data available for {}"
        #                              .format(sTime.strftime("%Y %m %d %H:%M")))

    # allBeams = [''] * len(myFiles)
    allBeams = []
    sites, fovs, oldCpids, lonFull, latFull = [], [], [], [], []
    lonC, latC = [], []

    # go through all open files
    for i in range(len(myFiles)):
        # read until we reach start time
        # allBeams[i] = radDataReadRec(myFiles[i])
        allBeams.append(radDataReadRec(myFiles[i]))
        if not allBeams[i]:
            myFiles[i].close()  # TODO: turn this into a pythonic method?
            myFiles[i] = None
            continue

        while allBeams[i].time < sTime:
            allBeams[i] = radDataReadRec(myFiles[i])

        # get to field of view coords in order to determine map limits
        t = allBeams[i].time
        radarSite = site(radId=allBeams[i].stid, dt=t)
        sites.append(radarSite)
        # Make lists of site lats and lons.  latC and lonC are used
        # for finding the map centre.
        xlon, xlat = coord_conv(radarSite.geolon, radarSite.geolat, "geo", coords,
                                altitude=0., date_time=t)
        latFull.append(xlat)
        lonFull.append(xlon)
        latC.append(xlat)
        lonC.append(xlon)
        myFov = radFov.fov(site=radarSite, rsep=allBeams[i].prm.rsep,
                                 ngates=allBeams[i].prm.nrang + 1,
                                 nbeams=radarSite.maxbeam, coords=coords,
                                 date_time=t)
        fovs.append(myFov)
        for b in range(0, radarSite.maxbeam + 1):
            for k in range(0, allBeams[i].prm.nrang + 1):
                lonFull.append(myFov.lonFull[b][k])
                latFull.append(myFov.latFull[b][k])
        oldCpids.append(allBeams[i].cp)

        k = allBeams[i].prm.nrang
        b = 0
        latC.append(myFov.latFull[b][k])
        lonC.append(myFov.lonFull[b][k])
        b = radarSite.maxbeam
        latC.append(myFov.latFull[b][k])
        lonC.append(myFov.lonFull[b][k])

    # Now that we have 3 points from the FOVs of the radars, calculate the
    # lat,lon pair to center the map on. We can simply do this by converting
    # from Spherical coords to Cartesian, taking the mean of each coordinate
    # and then converting back to get lat_0 and lon_0
    lonC, latC = (numpy.array(lonC) + 360.) % 360.0, numpy.array(latC)
    xs = numpy.cos(numpy.deg2rad(latC)) * numpy.cos(numpy.deg2rad(lonC))
    ys = numpy.cos(numpy.deg2rad(latC)) * numpy.sin(numpy.deg2rad(lonC))
    zs = numpy.sin(numpy.deg2rad(latC))
    xc = numpy.mean(xs)
    yc = numpy.mean(ys)
    zc = numpy.mean(zs)
    lon_0 = numpy.rad2deg(numpy.arctan2(yc, xc))
    lat_0 = numpy.rad2deg(numpy.arctan2(zc, numpy.sqrt(xc * xc + yc * yc)))

    # Now do some stuff in map projection coords to get necessary width and
    # height of map and also figure out the corners of the map
    lonFull = (numpy.array(lonFull) + 360.) % 360.0
    latFull = numpy.array(latFull)  # Try to avoid multiple assignments in one line when the input values are not the same. It becomes very hard to read.

    tmpmap = utils.mapObj(coords=coords, projection='stere', width=10.0**3,
                          height=10.0**3, lat_0=lat_0, lon_0=lon_0,
                          datetime=sTime)
    x, y = tmpmap(lonFull, latFull)
    minx = x.min() * 1.05     # since we don't want the map to cut off labels
    miny = y.min() * 1.05     # or FOVs of the radars we should alter the
    maxx = x.max() * 1.05     # extrema a bit.
    maxy = y.max() * 1.05
    width = (maxx - minx)
    llcrnrlon, llcrnrlat = tmpmap(minx, miny, inverse=True)
    urcrnrlon, urcrnrlat = tmpmap(maxx, maxy, inverse=True)

    dist = width / 50.
    cTime = sTime

    # Clear temporary figure from memory.
    fig = plot.gcf()
    fig.clf()

    myFig = plot.figure(figsize=(12, 8))

    # draw the actual map we want
    myMap = utils.mapObj(coords=coords, projection='stere', lat_0=lat_0,
                         lon_0=lon_0, llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat,
                         urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat,
                         coastLineWidth=0.5, coastLineColor='k',
                         fillOceans='w', fillContinents='w', fillLakes='w',
                         datetime=sTime)
    # overlay fields of view, if desired
    if(fov == 1):
        for i, r in enumerate(rad):
            overlayRadar(myMap, codes=r, dateTime=sTime)
            # this was missing fovObj! We need to plot the fov for this
            # particular sTime.
            overlayFov(myMap, codes=r, dateTime=sTime, fovObj=fovs[i])
    # manually draw the legend
    if not fill and legend:
        # draw the box
        y = [myMap.urcrnry * .82, myMap.urcrnry * .99]
        x = [myMap.urcrnrx * .86, myMap.urcrnrx * .99]
        verts = [x[0], y[0]], [x[0], y[1]], [x[1], y[1]], [x[1], y[0]]
        poly = patches.Polygon(verts, fc='w', ec='k', zorder=11)
        myFig.gca().add_patch(poly)
        labs = ['5 dB', '15 dB', '25 dB', '35 dB', 'gs', '1000 m/s']
        pts = [5, 15, 25, 35]
        # plot the icons and labels
        for w in range(6):
            myFig.gca().text(x[0] + .35 * (x[1] - x[0]), y[1] * (.98 - w *
                             .025), labs[w], zorder=15, color='k', size=8,
                             va='center')
            xctr = x[0] + .175 * (x[1] - x[0])
            if(w < 4):
                myFig.gca().scatter(xctr, y[1] * (.98 - w * .025),
                                    s=.1 * pts[w],
                                    zorder=15, marker='o', linewidths=.5,
                                    edgecolor='face', facecolor='k')
            elif(w == 4):
                myFig.gca().scatter(xctr, y[1] * (.98 - w * .025),
                                    s=.1 * 35.,
                                    zorder=15, marker='o', linewidths=.5,
                                    edgecolor='k', facecolor='w')
            elif(w == 5):
                # This is a really messy line, I am not sure what is going on here
                y = LineCollection(numpy.array([((xctr - dist / 2.,
                                                 y[1] * (.98 - w * .025)),
                                                 (xctr + dist / 2., y[1] *
                                                 (.98 - w * .025)))]),
                                   linewidths=.5, zorder=15, color='k')
                myFig.gca().add_collection(y)
    bbox = myFig.gca().get_position()
    # now, loop through desired time interval

    cols = []
    bndTime = sTime + timedelta(seconds=interval)

    # go though all files
    pcoll = None
    for i in range(len(myFiles)):
        scans = []
        # check that we have good data at this time
        if not myFiles[i]:  # we check if allbeams[i] is not None earlier is this still necessary?
            continue

        # until we reach the end of the time window
        while allBeams[i].time < bndTime:
            # filter on frequency
            if (allBeams[i].prm.tfreq >= myBands[i][0] and
                    allBeams[i].prm.tfreq <= myBands[i][1]):
                scans.append(allBeams[i])
            # read the next record
            allBeams[i] = radDataReadRec(myFiles[i])
        # if there is no data in scans, overlayFan will object
        if scans == []:
            continue
        intensities, pcoll = overlayFan(scans, myMap, myFig, param, coords,
                                        gsct=gsct, radarSite=sites[i], fov=fovs[i],
                                        fill=fill, velscl=velscl, dist=dist,
                                        cmap=cmap, norm=norm)

    # if no data has been found pcoll will not have been set, and the following
    # code will object
    if pcoll:
        cbar = myFig.colorbar(pcoll, orientation='vertical', shrink=.65,
                              fraction=.1, drawedges=True)

        y_labels = []  # Bad name for a variable
        # define the colorbar labels
        for i in range(len(bounds)):
            if param == 'phi0':
                num_labels = 4  # TODO: really bad name since ln typically mean natural log
                if bounds[i] == 0:
                    num_labels = 3
                elif bounds[i] < 0:
                    num_labels = 5
                y_labels.append(str(bounds[i])[:num_labels])
                continue
            if (i == 0 and param == 'velocity') or i == len(bounds) - 1:
                y_labels.append(' ')
                continue
            y_labels.append(str(int(bounds[i])))
        cbar.ax.set_yticklabels(y_labels)
        cbar.ax.tick_params(axis='y', direction='out')
        # set colorbar ticklabel size
        for ti in cbar.ax.get_yticklabels():
            ti.set_fontsize(12)
        if param == 'velocity':
            cbar.set_label('Velocity [m/s]', size=14)
            cbar.extend = 'max'

        if param == 'grid':  # TODO: Delete? There is no option for grid? Is this a mistake?
            cbar.set_label('Velocity [m/s]', size=14)
        if param == 'power':
            cbar.set_label('Power [dB]', size=14)
        if param == 'width':
            cbar.set_label('Spec Wid [m/s]', size=14)
        if param == 'elevation':
            cbar.set_label('Elev [deg]', size=14)
        if param == 'phi0':
            cbar.set_label('Phi0 [rad]', size=14)

    for i in range(len(rad)):
        myFig.text(bbox.x1 + .02, bbox.y1 - ((i + 1) * .015), rad[i] + ': ' +
                   str(tbands[i][0] / 1e3) + ' - ' + str(tbands[i][1] / 1e3) +
                   ' MHz', ha='right', size=8, weight=550)

    if(overlayPoes):
        pcols = gme.sat.poes.overlayPoesTed(myMap, myFig.gca(), cTime,
                                            param=poesparam, scMin=poesMin,
                                            scMax=poesMax)
        if pcols:
            cols.append(pcols)
            pTicks = numpy.linspace(poesMin, poesMax, 8)
            cbar = myFig.colorbar(pcols, ticks=pTicks, orientation='vertical',
                                  shrink=0.65, fraction=.1)
            cbar.ax.set_yticklabels(pTicks)
            cbar.set_label(poesLabel, size=14)
            cbar.ax.tick_params(axis='y', direction='out')
            # set colorbar ticklabel size
            for ti in cbar.ax.get_yticklabels():
                ti.set_fontsize(12)

    if(overlayBnd):
        gme.sat.poes.overlayPoesBnd(myMap, myFig.gca(), cTime)

    # handle the outputs
    if not fileName:
        fileName = "{date}.{interval}.fan.{ext}"\
                   "".format(date=sTime.strftime("%Y%m%d.%H%M"),
                             interval=interval,
                             ext=extension)
    myFig.savefig(fileName)

    if show:
        myFig.show()


def overlayFan(myData, myMap, myFig, param, coords='geo', gsct=0, radarSite=None,
               fov=None, gs_flg=[], fill=True, velscl=1000., dist=1000.,
               cmap=None, norm=None, alpha=1):

    # TODO: go over this list again, they do not match up
    """A function of overlay radar scan data on a map

    Parameters
    ----------
    myData : pydarn.sdio.radDataTypes.scanData or
             pydarn.sdio.radDataTypes.beamData or
             list of pydarn.sdio.radDataTypes.beamData objects
        A radar beam object, a radar scanData object, or simply a list of
        radar beams
    myMap :
        The map we are plotting on
    myFig :
        Figure object that we are plotting to
    coords : Optional[str]
        The coordinates we are plotting in.  Default: geo
    param : Optional[str]
        The parameter to be plotted, valid inputs are 'velocity', 'power',
        'width', 'elevation', 'phi0'.  default = 'velocity
    gsct : Optional[boolean]
        A flag indicating whether we are distinguishing ground scatter.
        default = 0
    intensities : Optional[  ]
        A list of intensities (used for colorbar)
    fov : Optional[pydarn.radar.radFov.fov]
        A radar fov object
    gs_flg : Optional[  ]
        A list of gs flags, 1 per range gate
    fill : Optional[boolean]
        A flag indicating whether to plot filled or point RB cells.
        default = True
    velscl : Optional[float]
        The velocity to use as baseline for velocity vector length, only
        applicable if fill = 0.  default = 1000
    lines : Optional[  ]
        An array to have the endpoints of velocity vectors.  only applicable if
        fill = 0.  default = []
    dist : Optional [float]
        The length in map projection coords of a velscl length velocity vector.
        default = 1000. km

    Returns
    -------
    intensities

    pcoll

    lcoll


    Example
    -------
        overlayFan(aBeam,myMap,param,coords,gsct=gsct,site=sites[i],fov=fovs[i],
                   verts=verts,intensities=intensities,gs_flg=gs_flg)

    """
    if isinstance(myData, beamData):
        myData = [myData]
    if not radarSite:
        radarSite = site(radId=myData[0].stid, dt=myData[0].time)
    if not fov:
        fov = radFov.fov(site=radarSite, rsep=myData[0].prm.rsep,
                         ngates=myData[0].prm.nrang + 1,
                         nbeams=site.maxbeam, coords=coords,
                         date_time=myData[0].time)

    gs_flg, lines = [], []
    if fill:
        verts, intensities = [], []
    else:
        verts, intensities = [[], []], [[], []]

    # loop through gates with scatter
    for myBeam in myData:
        for k in range(0, len(myBeam.fit.slist)):
            if myBeam.fit.slist[k] not in fov.gates:
                continue
            r = myBeam.fit.slist[k]

            if fill:
                x1, y1 = myMap(fov.lonFull[myBeam.bmnum, r],
                               fov.latFull[myBeam.bmnum, r])
                x2, y2 = myMap(fov.lonFull[myBeam.bmnum, r + 1],
                               fov.latFull[myBeam.bmnum, r + 1])
                x3, y3 = myMap(fov.lonFull[myBeam.bmnum + 1, r + 1],
                               fov.latFull[myBeam.bmnum + 1, r + 1])
                x4, y4 = myMap(fov.lonFull[myBeam.bmnum + 1, r],
                               fov.latFull[myBeam.bmnum + 1, r])

                # save the polygon vertices
                verts.append(((x1, y1), (x2, y2), (x3, y3), (x4, y4),
                              (x1, y1)))

                # save the param to use as a color scale
                if param == 'velocity':
                    intensities.append(myBeam.fit.v[k])
                elif param == 'power':
                    intensities.append(myBeam.fit.p_l[k])
                elif param == 'width':
                    intensities.append(myBeam.fit.w_l[k])
                elif param == 'elevation' and myBeam.prm.xcf:
                    intensities.append(myBeam.fit.elv[k])
                elif param == 'phi0' and myBeam.prm.xcf:
                    intensities.append(myBeam.fit.phi0[k])

            else:
                x1, y1 = myMap(fov.lonCenter[myBeam.bmnum, r],
                               fov.latCenter[myBeam.bmnum, r])
                verts[0].append(x1)
                verts[1].append(y1)

                x2, y2 = myMap(fov.lonCenter[myBeam.bmnum, r + 1],
                               fov.latCenter[myBeam.bmnum, r + 1])

                theta = math.atan2(y2 - y1, x2 - x1)
                # Avoid assinging multiple variables in one line. Harder to debug
                x2 = x1 + myBeam.fit.v[k] / velscl * (-1.0) * \
                    math.cos(theta) * dist,
                y2 = y1 + myBeam.fit.v[k] / velscl * \
                    (-1.0) * math.sin(theta) * dist

                lines.append(((x1, y1), (x2, y2)))
                # save the param to use as a color scale
                if param == 'velocity':
                    intensities[0].append(myBeam.fit.v[k])
                elif param == 'power':
                    intensities[0].append(myBeam.fit.p_l[k])
                elif param == 'width':
                    intensities[0].append(myBeam.fit.w_l[k])
                elif param == 'elevation' and myBeam.prm.xcf:
                    intensities[0].append(myBeam.fit.elv[k])
                elif param == 'phi0' and myBeam.prm.xcf:
                    intensities[0].append(myBeam.fit.phi0[k])

                if myBeam.fit.p_l[k] > 0:
                    intensities[1].append(myBeam.fit.p_l[k])
                else:
                    intensities[1].append(0.)
            if gsct:
                gs_flg.append(myBeam.fit.gflg[k])

    # do the actual overlay
    # TODO: can we add this to the above if fill clause?
    if fill:
        # if we have data
        if verts != []:
            if gsct == 0:
                inx = numpy.arange(len(verts))
            else:
                inx = numpy.where(numpy.array(gs_flg) == 0)
                x = PolyCollection(numpy.array(verts)[numpy.where(
                                   numpy.array(gs_flg) == 1)], facecolors='.3',
                                   linewidths=0, zorder=5, alpha=alpha)
                myFig.gca().add_collection(x, autolim=True)

            pcoll = PolyCollection(numpy.array(verts)[inx],
                                   edgecolors='face', linewidths=0,
                                   closed=False, zorder=4, alpha=alpha,
                                   cmap=cmap, norm=norm)
            # set color array to intensities
            pcoll.set_array(numpy.array(intensities)[inx])
            myFig.gca().add_collection(pcoll, autolim=True)
            return intensities, pcoll
    else:
        # if we have data
        if verts != [[], []]:
            if gsct == 0:
                inx = numpy.arange(len(verts[0]))
            else:
                inx = numpy.where(numpy.array(gs_flg) == 0)
                # plot the ground scatter as open circles
                x = myFig.scatter(numpy.array(verts[0])[numpy.where(
                                  numpy.array(gs_flg) == 1)],
                                  numpy.array(verts[1])[numpy.where(
                                      numpy.array(gs_flg) == 1)],
                                  s=.1 * numpy.array(intensities[1])[
                                  numpy.where(numpy.array(gs_flg) == 1)],
                                  zorder=5, marker='o', linewidths=.5,
                                  facecolors='w', edgecolors='k')
                myFig.gca().add_collection(x, autolim=True)

            # plot the i-s as filled circles
            ccoll = myFig.gca().scatter(numpy.array(verts[0])[inx],
                                        numpy.array(verts[1])[inx],
                                        s=.1 * numpy.array(
                                        intensities[1])[inx], zorder=10,
                                        marker='o', linewidths=.5,
                                        edgecolors='face', cmap=cmap,
                                        norm=norm)

            # set color array to intensities
            ccoll.set_array(numpy.array(intensities[0])[inx])
            myFig.gca().add_collection(ccoll)
            # plot the velocity vectors
            lcoll = LineCollection(numpy.array(lines)[inx], linewidths=.5,
                                   zorder=12, cmap=cmap, norm=norm)
            lcoll.set_array(numpy.array(intensities[0])[inx])
            myFig.gca().add_collection(lcoll)

            return intensities, lcoll


# PEP8 standard have 2 blank spaces between functions that are not in the same class
if __name__ == "__main__":
    # you do not need to import libraries that are used in the functions as well.
    # If you need the library only in the main portion (testing purposes) then
    # import the library.
    time = datetime(2014, 8, 7, 18, 30)

    print("Testing some of the plotFan stuff.  Time used is:")
    print(time)
    print("Generating a plot of Saskatoon and Hankasalmi velocity")
    print("in geographic coords with ground scatter on.")
    plotFan(time, ["sas", "han"], param="velocity", coords="geo", gsct=True,
            show=True)
    print("Now a plot of power.")
    plotFan(time, ["sas", "han"], param="power", coords="geo", gsct=True,
            show=True)
    print("Now change to magnetic coords.")
    plotFan(time, ["sas", "han"], param="power", coords="mag", gsct=True,
            show=True)
    print("Now change to MLT coords.")
    plotFan(time, ["sas", "han"], param="power", coords="mlt", gsct=True,
            show=True)
    print("Now generate a png instead of showing the plot.")
    plotFan(time, ["sas", "han"], param="power", coords="mag", gsct=True,
            show=False, png=True)
