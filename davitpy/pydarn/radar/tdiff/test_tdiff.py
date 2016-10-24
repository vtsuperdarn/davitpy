#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------
# test_tdiff.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Functions to test the performance of the tdiff routines
#-----------------------------------------------------------------------------
"""This module contains routines to test the tdiff routines

Functions
-------------------------------------------------------------------------------
test_simplex               Test the rigorous_simplex routine in simplex.py
han_heater_field_line_lat  Trace basic field-lines for HAN-heater combos
test_calc_tdiff            Test calc_tdiff for an example from the RS article
-------------------------------------------------------------------------------

References
------------------------------------------------------------------------------
A.G. Burrell et al. (2016) submitted to Radio Science doi:xxx
------------------------------------------------------------------------------
"""
import numpy as np
import logging

def test_simplex(plot_handle=None):
    ''' Find the minimum of a sine function closest to a specified x-value

    Parameters
    ----------
    plot_handle : (figure handle or NoneType)
        Figure handle to plot output on or None if no plot is desired
        (default=None)

    Returns
    --------
    min0 : (float)
        Minimum closest to zero degrees (-90 degrees)
    min1 : (float)
        Minimum closest to 180 degrees (360 degrees)
    min2 : (float)
        Minimum closest to -271 degrees (-360 degrees)

    Example
    --------
    In [1]: import test_tdiff
    In [2]: min0, min1, min2 = test_tdiff.test_simplex()
    Optimization terminated successfully.
         Current function value: -1.000000
         Iterations: 26
         Function evaluations: 52
    Optimization terminated successfully.
         Current function value: -1.000000
         Iterations: 11
         Function evaluations: 22
    Optimization terminated successfully.
         Current function value: -1.000000
         Iterations: 11
         Function evaluations: 22
    Optimization terminated successfully.
         Current function value: -1.000000
         Iterations: 17
         Function evaluations: 34
    Optimization terminated successfully.
         Current function value: -1.000000
         Iterations: 13
         Function evaluations: 26
    Optimization terminated successfully.
         Current function value: -1.000000
         Iterations: 13
         Function evaluations: 26
    Optimization terminated successfully.
         Current function value: -1.000000
         Iterations: 19
         Function evaluations: 38
    Optimization terminated successfully.
         Current function value: -1.000000
         Iterations: 13
         Function evaluations: 26
    Optimization terminated successfully.
         Current function value: -1.000000
         Iterations: 13
         Function evaluations: 26
    In [3]: print min0, min1, min2
    -1.5708125 4.71238898038 -7.85400933085
    '''
    from simplex import rigerous_simplex
    
    def sin_func(angle_rad):
        return np.sin(angle_rad)

    x = np.arange(-3.0*np.pi, 3.0*np.pi, .1)
    x0 = 0.0
    x1 = np.pi
    x2 = np.radians(-271.0)

    tol = 1.0e-4
    args = ()

    min0, mi, res = rigerous_simplex(x0, args, sin_func, tol)
    min1, mi, res = rigerous_simplex(x1, args, sin_func, tol)
    min2, mi, res = rigerous_simplex(x2, args, sin_func, tol)

    if plot_handle is not None:
        import matplotlib as mpl
        # Initialize the figure
        ax = plot_handle.add_subplot(1,1,1)

        # Plot the data
        y = sin_func(x)
        ax.plot(np.degrees(x), y, "k-")
        ax.plot([np.degrees(x0), np.degrees(x0)], [-1,1], "k--")
        ax.plot([np.degrees(x1), np.degrees(x1)], [-1,1], "k--")
        ax.plot([np.degrees(x2), np.degrees(x2)], [-1,1], "k--")
        ax.plot([np.degrees(min0), np.degrees(min0)], [-1,1], "k-.")
        ax.plot([np.degrees(min1), np.degrees(min1)], [-1,1], "k-.")
        ax.plot([np.degrees(min2), np.degrees(min2)], [-1,1], "k-.")

        # Add labels
        ax.set_xlabel("x (degrees)")
        ax.set_ylabel("sin(x)")
        ax.text(np.degrees(x0) + 10,0,"x$_0$")
        ax.text(np.degrees(x1) + 10,0,"x$_1$")
        ax.text(np.degrees(x2) + 10,0,"x$_2$")
        ax.text(np.degrees(min0) + 10,0,"min$_0$")
        ax.text(np.degrees(min1) + 10,0,"min$_1$")
        ax.text(np.degrees(min2) + 10,0,"min$_2$")

        # Make the x-axis sensible
        ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(90))
        ax.set_xlim(-540, 540)

    return min0, min1, min2

def han_heater_field_line_lat(alt, heater="Tromso"):
    '''Calculate the latitude for a field line irregularity produced by heater
    and observed by Hankasalmi

    Parameters
    --------------
    alt : (float or np.ndarray)
        Altitude in kilometers
    heater : (str)
        Heater name (SPEAR or Tromso, case insensitive) (default="Tromso")

    Returns
    lat : (float or np.ndarray)
        Latitude in degrees
    '''

    heater_lat = 78.15 if heater.lower() == "spear" else 69.90
    heater_ang = 7.7 if heater.lower() == "spear" else 12.0
    line_lat = heater_lat - (alt * np.tan(np.radians(heater_ang)) / 111.0)
    
    return line_lat

def test_calc_tdiff(file_type="fitacf", password=True, tdiff_plot=None):
    '''Test calc_tdiff

    Parameters
    -----------
    file_type : (str)
        Type of file to load (default="fitacf")
    password : (str, bool, NoneType)
        Password to access SuperDARN database (default=True)
    tdiff_plot : (matplotlib.figure.Figure or NoneType)
        figure handle for output or None to not produce a plot (default=None)

    Returns
    -----------
    test_tdiff : (float)
        tdiff for 11.075-11.275 MHz at han on 13 Oct 2006
    trange : (np.ndarray)
        Numpy array of tdiff values spanning 6 periods centred about test_tdiff
    ldist : (np.ndarray)
        Numpy array of latitude distribution values for each trange value.
        Can be used with trange to examine the function that was minimized to
        find test_tdiff

    Example
    ----------
    In[1]: import davitpy.radar.tdiff as dtdiff
    In[5]: tt, trange, ldist = dtdiff.test_tdiff.test_calc_tdiff()
    --- shows simplex output ---
    In[6]: print tt
    0.155995791387
    '''
    import datetime as dt
    import davitpy.pydarn.radar as pyrad
    import davitpy.pydarn.sdio as sdio
    import davitpy.pydarn.proc.fov as fov
    import davitpy.pydarn.radar.tdiff.bscatter_distribution as bs_dist

    # Set the radar beam selection criteria
    rad = 'han'
    radcp = -6401
    stime = dt.datetime(2006, 10, 13, 15)
    etime = dt.datetime(2006, 10, 13, 15, 30)

    # Load the data
    try:
        rad_ptr = sdio.radDataRead.radDataOpen(stime, rad, eTime=etime,
                                               fileType=file_type,
                                               password=password, cp=radcp)
    except:
        print "Unable to load tdiff test data:\nRadar: {:s}".format(rad)
        print "Program: {:d}\nTime: {:} to {:}".format(radcp, stime, etime)
        return None, None, None

    hard = pyrad.site(code=rad, dt=stime)
    rad_bands = pyrad.tdiff.rad_freqbands.radFreqBands(rad)
    
    # Set the beam selection criteria
    tb = 3
    bnum = 5
    pmin = 10.0
    rmin = 10
    rmax = 25
    tmins = [dt.datetime(2006, 10, 13, 15, 4), dt.datetime(2006, 10, 13, 15, 8),
             dt.datetime(2006, 10, 13, 15, 12)]
    tmaxs = [dt.datetime(2006, 10, 13, 15, 6),dt.datetime(2006, 10, 13, 15, 10),
             dt.datetime(2006, 10, 13, 15, 14)]
    sattr = ["slist", "time", "tfreq", "p_l", "phi0", "phi0e", "bmnum", "dist"]
    
    bm = rad_ptr.readRec()
    beams = list()
    while bm is not None:
        tband = rad_bands.get_tfreq_band_num(bm.prm.tfreq)
        if bm.bmnum == bnum and tband == tb:
            if hasattr(bm, "fit"):
                # Add attribute to beam
                bm.fit.dist = fov.update_backscatter.calc_distance(bm)
                beams.append(bm)
        bm = rad_ptr.readRec()

    sdata = pyrad.tdiff.calc_tdiff.select_bscatter(beams, sattr, radcp, tb,
                                                   bnum, min_power=pmin,
                                                   min_rg=rmin, max_rg=rmax,
                                                   stimes=tmins, etimes=tmaxs)

    # Set the reference location
    tperiod = 1000.0 / rad_bands.get_mean_tband_freq(tb)
    ref_alt = 230.0
    ref_lat = han_heater_field_line_lat(ref_alt, heater="tromso")
    ref_err = max(abs(han_heater_field_line_lat(np.array([ref_alt - 10.0,
                                                          ref_alt + 10.0]),
                                                heater="tromso") - ref_lat))
    ttol = 1.0e-4
    fovflg = [1 for i in sdata["phi0"]]
    bm_az = [np.radians(hard.beamToAzim(b) - hard.boresite)
             for b in sdata['bmnum']]
    lat_args = (hard, sdata["phi0"], sdata["phi0e"], fovflg, bm_az,
                sdata["tfreq"], sdata['dist']) 

    # Estimate tdiff
    tout = pyrad.tdiff.calc_tdiff.calc_tdiff(hard.tdiff, ref_lat, ref_err,
                                             lat_args, bs_dist.lat_distribution,
                                             0.01, tdiff_tol=ttol,
                                             tperiod=tperiod)

    # Calculate the latitude distribution as a function of tdiff
    trange = np.arange(tout[0] - 3.0 * tperiod, tout[0] + 3.0 * tperiod, ttol)
    ldist = np.array([bs_dist.lat_distribution(t, *((ref_lat,) + lat_args))
                      for t in trange])

    # If desired, create the figure showing the data selection results,
    # tdiff functional variations, and difference in the location distributions
    # using the initial and final tdiffs
    if tdiff_plot is not None:
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        from davitpy.utils import calcDistPnt
        fov_dir = {1:"front", -1:"back"}
        try:
            sax = tdiff_plot.add_subplot(3,1,1)
            hax = tdiff_plot.add_subplot(2,2,4)
            tax = tdiff_plot.add_subplot(2,2,3)
        except:
            print "Unable to add subplots to figure"
            return tout[0], trange, ldist

        # Add the title
        stitle = "{:s} Beam {:d} on {:}\n".format(rad, bnum, stime.date())
        stitle = "{:s}{:.3f}-{:.3f} MHz with {:d}".format(stitle, \
                    rad_bands.tmins[tb] / 1000.0, rad_bands.tmaxs[tb] / 1000.0,
                                                          len(sdata['phi0']))
        stitle = "{:s} heater backscatter observations".format(stitle)
        tdiff_plot.suptitle(stitle)

        # Extract all of the read in data for the selected beam
        sax_time = list()
        sax_range = list()
        sax_p = list()

        for bm in beams:
            for i,ss in enumerate(bm.fit.slist):
                sax_time.append(bm.time)
                sax_range.append(ss)
                sax_p.append(bm.fit.p_l[i])

        # Identify selected data over RTI using power as intensity
        sax.scatter(sax_time, sax_range, c=sax_p, vmin=0, vmax=40,
                    cmap=mpl.cm.get_cmap("Spectral_r"), marker="|",
                    linewidth=14, s=45, zorder=2)
        sax.plot(sdata["time"], sdata["slist"], "k.", zorder=3)

        for i,ss in enumerate(tmins):
            p = mpl.patches.Rectangle((mpl.dates.date2num(ss), rmin),
                                      (tmaxs[i]-ss).total_seconds()/86400.,
                                      rmax-rmin, color="0.6", zorder=1)
            sax.add_patch(p)
        
        sax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%H:%M"))
        sax.xaxis.set_major_locator(mpl.dates.MinuteLocator(interval=5))
        sax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5))
        sax.set_xlim(stime, etime)
        sax.set_ylim(rmin - 1, rmax + 1)
        sax.set_xlabel("Universal Time (HH:MM)")
        sax.set_ylabel("Range Gate")
        sax.set_axis_bgcolor("0.9")

        cb = fov.test_update_backscatter.add_colorbar(tdiff_plot, \
                sax.collections[0], 0, 40, 5, name="Power", units="dB",
                                                      loc=[.91, .67, .01, .22])

        # Add the tdiff-lat dist function 
        tax.plot(trange, ldist, "b-", linewidth=2)
        ymin, ymax = tax.get_ylim()
        tax.plot([hard.tdiff, hard.tdiff], [ymin, ymax], "k--", linewidth=2,
                 label="Initial $\delta t_c$")
        tax.plot([tout[0], tout[0]], [ymin, ymax], "k-", linewidth=2,
                 label="Estimated $\delta t_c$")
        tax.plot([tout[0]+tperiod, tout[0]+tperiod], [ymin, ymax], "-", c="0.6",
                 linewidth=2, label="Estimated $\delta t_c$ $\pm$ T")
        tax.plot([tout[0]-tperiod, tout[0]-tperiod], [ymin, ymax], "-", c="0.6",
                 linewidth=2)
        tax.plot([tout[0]+2.0*tperiod, tout[0]+2.0*tperiod], [ymin, ymax], "-",
                 c="0.8", linewidth=2, label="Estimated $\delta t_c$ $\pm$ 2T")
        tax.plot([tout[0]-2.0*tperiod, tout[0]-2.0*tperiod], [ymin, ymax], "-",
                 c="0.8", linewidth=2)

        tax.set_xlim(tout[0]-2.5*tperiod, tout[0]+2.5*tperiod)
        tax.set_ylim(ymin, ymax)
        tax.set_xlabel("$\delta t_c$ ($\mu s$)")
        tax.set_ylabel("g($\delta t_c$) ($^\circ$)")
        tax.legend(ncol=2, fontsize="xx-small", bbox_to_anchor=(1.1,1.33))

        # Add the latitude histogram
        elv = np.array(fov.calc_elevation.calc_elv_list(sdata['phi0'],
                                                        sdata['phi0e'], fovflg,
                                                        bm_az, sdata['tfreq'],
                                                        hard.interfer,
                                                        hard.tdiff))
        elv = np.degrees(elv)
        az = np.array([pyrad.radFov.calcAzOffBore(e, np.degrees(bm_az[i]),
                                                  fov_dir[fovflg[i]]) +
                       hard.boresite for i,e in enumerate(elv)])
        loc = calcDistPnt(hard.geolat, hard.geolon, hard.alt, az=az, el=elv,
                          dist=np.array(sdata['dist']))

        hax.hist(loc['distLat'], 8, color="0.6",
                 label="{:.3f}".format(hard.tdiff))
       
        elv = np.array(fov.calc_elevation.calc_elv_list(sdata['phi0'],
                                                        sdata['phi0e'], fovflg,
                                                        bm_az, sdata['tfreq'],
                                                        hard.interfer, tout[0]))
        
        elv = np.degrees(elv)
        az = np.array([pyrad.radFov.calcAzOffBore(e, np.degrees(bm_az[i]),
                                                  fov_dir[fovflg[i]]) +
                       hard.boresite for i,e in enumerate(elv)])
        loc = calcDistPnt(hard.geolat, hard.geolon, hard.alt, az=az, el=elv,
                          dist=np.array(sdata['dist']))

        hax.hist(loc['distLat'], 8, color="c", alpha=.5,
                 label="{:.3f}".format(tout[0]))

        # Set the main axis labels and limits
        xmin, xmax = hax.get_xlim()
        hax.set_ylim(0, 15)
        hax.set_ylabel("Counts")
        hax.yaxis.set_label_coords(-.08, .5)
        hax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(3))
        hax.set_xlabel("Latitude ($^\circ$)")
        hax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1))
        hax.legend(ncol=2, fontsize="xx-small", title="$\delta t_c$ ($\mu s$)",
                   bbox_to_anchor=(.85,1.33))
       
        # Add the reference locations to a twin of the histogram plot
        hax2 = hax.twinx()
        line_alt = np.arange(0.0, 315.0, 15.0)
        line_lat = han_heater_field_line_lat(line_alt, heater="tromso")
        hax2.plot(line_lat, line_alt, "k-", linewidth=4)
        hax2.plot([xmin, xmax], [ref_alt, ref_alt], "k:")
        hax2.plot([ref_lat, ref_lat], [0, 300], "k--", linewidth=2)
        
        hax.set_xlim(xmin, xmax)
        hax2.set_ylabel("Altitude (km)")

    return tout[0], trange, ldist
