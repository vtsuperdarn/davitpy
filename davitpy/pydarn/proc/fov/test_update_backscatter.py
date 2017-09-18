#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# test_update_backscatter.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Scripts to create plots and calculate statistics that test
#           the routines in update_backscatter that determine the origin
#           field-of-view (FoV) for radar backscatter
#-----------------------------------------------------------------------------
"""test_update_backscatter

Scripts to create plots and calculate statistics that test the routines in
update_backscatter that determine the origin field-of-view (FoV) for radar
backscatter

Functions
-------------------------------------------------------------
add_colorbar                add to existing figure
get_sorted_legend_labels    sort by hop and region
get_fractional_hop_labels   hop decimal to fraction
plot_yeoman_plate1          Yeoman(2001) based plot
plot_milan_figure9          Milan(1997) based plot
plot_storm_figures          plot E-region scatter
plot_single_column          plot subplots
load_test_beams             data for a test period
plot_scan_and_beam          plot attribute for front/rear FoV
plot_meteor_figure          compare HWM14 with LoS velocity
plot_map                    plot a FoV map
-------------------------------------------------------------

Author: Angeline G. Burrell (AGB)
Date: August 12, 2015
Inst: University of Leicester (UoL)

"""

# Import python packages
import os
import numpy as np
import datetime as dt
import logging
import matplotlib.ticker as ticker
import matplotlib.cm as cm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mpl_toolkits.basemap as basemap
import matplotlib.gridspec as gridspec
import matplotlib.collections as mcol
import matplotlib.colors as mcolors
# Import DaViTpy packages
import update_backscatter as ub

#--------------------------------------------------------------------------
# Define the colors (can be overwritten)
clinear = "Spectral_r"
ccenter = "Spectral"

morder =  {"region":{"D":0, "E":1, "F":2},
           "reg":{"0.5D":0, "1.0D":1, "0.5E":2, "1.0E":3, "1.5E":4, "2.0E":5,
                  "2.5E":6, "3.0E":7, "0.5F":8, "1.0F":9, "1.5F":10, "2.0F":11,
                  "2.5F":12, "3.0F":13},
           "hop":{0.5:0, 1.0:1, 1.5:2, 2.0:3, 2.5:4, 3.0:5},}
mc = {"region":{"D":"g", "E":"m", "F":"b"},
      "reg":{"0.5D":"g", "1.0D":"y", "0.5E":"r", "1.0E":"m",
             "1.5E":(1.0, 0.5, 1.0), "2.0E":(0.5, 0, 0.25),
             "2.5E":(1.0,0.7,0.2), "3.0E":(0.5, 0, 0.1),
             "0.5F":(0.0, 0.0, 0.75), "1.0F":(0.0, 0.5, 0.5), "1.5F":"b",
             "2.0F":"c", "2.5F":(0.25, 0.75, 1.0), "3.0F":(0.0, 1.0, 1.0)},
      "hop":{0.5:"b", 1.0:"r", 1.5:"c", 2.0:"m",
             2.5:(0.25, 0.75, 1.0), 3.0:(0.5, 0, 0.25)},}
mm = {"region":{"D":"d", "E":"o", "F":"^", "all":"|"},
      "reg":{"0.5D":"d", "1.0D":"Y", "0.5E":"^", "1.0E":"o", "1.5E":">",
             "2.0E":"8", "2.5E":"*", "3.0E":"H", "0.5F":"v", "1.0F":"p",
             "1.5F":"<", "2.0F":"h", "2.5F":"D", "3.0F":"s", "all":"|"},
      "hop":{0.5:"d", 1.0:"o", 1.5:"s", 2.0:"^", 2.5:"v", 3.0:"p",
             "all":"|"},}

#--------------------------------------------------------------------------
def add_colorbar(figure_handle, contour_handle, zmin, zmax, zinc=6, name=None,
                 units=None, orient="vertical", scale="linear", width=1,
                 loc=[0.9,0.1,0.03,0.8]):
    """Add a colorbar to an existing figure

    Parameters
    --------
    figure_handle : (pointer)
        handle to the figure
    contour_handle : (pointer)
        handle to contour plot
    zmin : (float or int)
        minimum z value
    zmax : (float or int)
        maximum z value
    zinc : (float or int)
        z tick incriment (default=6)
    name : (str or NoneType)
        z variable name (default=None)
    units : (str or NoneType)
        z variable units (default=None)
    orient : (str)
        bar orientation (horizontal, default=vertical)
    scale : (str)
        linear (default) or exponential
    width : (float or int)
        fraction of width (0-1), default=1
    loc : (list)
        location of colorbar (default=[0.95,0.1,0.03,0.8])

    Returns
    -------
    ax2 : (pointer)
        handle to the colorbar axis
    cb : (pointer)
        handle to the colorbar

    """
    # Set the z range and output the colorbar
    w  = np.linspace(zmin, zmax, zinc, endpoint=True)
    ax2 = figure_handle.add_axes(loc)
    cb = plt.colorbar(contour_handle, cax=ax2, ticks=w, orientation=orient)

    # See if the upper and lower limits are multiples of pi
    if zmin % np.pi == 0 and zmax % np.pi == 0:
        wfac = w / np.pi
        w = list(w)
        for i,wval in enumerate(wfac):
            if wval == 0.0:
                w[i] = "{:.0f}".format(wval)
            elif wval == 1.0:
                w[i] = "$\pi$"
            elif wval == -1.0:
                w[i] = "-$\pi$"
            elif wval == int(wval):
                w[i] = "{:.0f}$\pi$".format(wval)
            else:
                w[i] = "{:.2f}$\pi$".format(wval)

        if orient is "vertical":
            cb.ax.set_yticklabels(w)
        else:
            cb.ax.set_xticklabels(w)

    # Change the z scale, if necessary
    if(scale is "exponential"):
        cb.formatter = ticker.FormatStrFormatter('%7.2E')

    # Set the label and update the ticks
    if name is not None:
        if units is not None:
            cb.set_label(r'{:s} (${:s}$)'.format(name, units))
        else:
            cb.set_label(r'{:s}'.format(name))

    cb.update_ticks()

    # Return the handle for the colorbar (which is treated as a subplot)
    # to allow for additional adjustments
    return ax2, cb

#--------------------------------------------------------------------------
def get_sorted_legend_labels(ax, marker_key="reg"):
    """Sort legend labels by hop and region

    Parameters
    -----------
    ax : (pointer)
        handle to figure axis
    marker_key : (str)
        key to denote what type of marker labels are being used (default="reg")

    Returns
    ---------
    handles : (list)
        ordered list of marker handles
    labels : (list)
        ordered list of marker labels
    """
    handles, labels = ax.get_legend_handles_labels()

    try:
        lind = {morder[marker_key][ll]:il for il,ll in enumerate(labels)}
    except:
        labels = [float(ll) for ll in labels]
        lind = {morder[marker_key][ll]:il for il,ll in enumerate(labels)}
    order = [lind[k] for k in sorted(lind.keys())]

    return [handles[i] for i in order], [labels[i] for i in order]

#--------------------------------------------------------------------------
def get_fractional_hop_labels(legend_labels):
    """Change decimal hop labels to traditional fractions

    Parameters
    -----------
    legend_labels : (list)
        List of strings containing decimal hops (eg ["0.5", "1.0", "1.5"]) 

    Returns
    --------
    legend_labels : (list)
        List of strings containing fracitonal hops
    """
    for i,ll in enumerate(legend_labels):
        ll = ll.replace("0.5", r"$\frac{1}{2}$")
        ll = ll.replace(".5", r"$\frac{1}{2}$")
        ll = ll.replace(".0", "")
        legend_labels[i] = ll

    return(legend_labels)

#--------------------------------------------------------------------------
def plot_yeoman_plate1(intensity_all="p_l", intensity_sep="fovelv",
                       marker_key="reg", color={"p_l":clinear,"fovelv":clinear},
                       acolor="0.9", stime=dt.datetime(1998,10,15,12,10),
                       etime=dt.datetime(1998,10,15,12,50),
                       imin={"p_l":0.0, "fovelv":0.0},
                       imax={"p_l":30.0, "fovelv":40.0},
                       iinc={"p_l":6, "fovelv":6}, ymin=20, ymax=60,
                       rad_bms={"han":5, "pyk":15},
                       rad_cp={"han":-6312, "pyk":-6312},
                       fix_gs={"han":[[0,76]]}, figname=None, password=True,
                       file_type="fitacf", logfile=None, log_level=logging.WARN,
                       min_pnts=3, region_hmin={"D":75.0,"E":115.0,"F":150.0},
                       region_hmax={"D":115.0,"E":150.0,"F":900.0},
                       rg_box=[2,5,10,20], vh_box=[50.0,50.0,50.0,150.0],
                       max_rg=[5,25,40,76], max_hop=3.0,
                       ut_box=dt.timedelta(minutes=20.0), tdiff=None,
                       tdiff_args=list(), tdiff_e=None, tdiff_e_args=list(),
                       ptest=True, step=6, strict_gs=True, draw=True,
                       label_type="frac", beams=dict()):
    """Plot based on Plate 1  in Yeoman et al (2001) Radio Science, 36, 801-813.


    Parameters
    -----------
    intensity_all : (str)
        Intensity attribute to plot in the top figure with unseperated fields-
        of-view.  Uses SuperDARN beam fit attribute names. (default="p_l")
    intensity_sep : (str)
        Intensity attribute to plot in the separated fields-of-view.  Uses
        SuperDARN beam fit attribute names. (default="fovelv")
    marker_key : (str)
        key to denote what type of marker labels are being used (default="reg")
    color : (dict)
        Intensity color scheme.  Defaults to the standard centered color
        scheme for this program.  Yeoman et al (2001) used "jet".
        (default={"p_l":"Spectral_r","fovelv":"Spectral_r"})
    acolor : (str or tuple)
        Background color for subplots (default="0.9" - light grey)
    stime : (dt.datetime)
        Starting time of plot (will pad loaded data).
        (default=dt.datetime(1998,10,15,12,10))
    etime : (dt.datetime)
        Ending time of plot (will pad loaded data).
        (default=dt.datetime(1998,10,15,12,50))
    imin : (dict)
        Intensity minimums (default={"p_l":0.0, "fovelv":0.0})
    imax : (dict)
        Intensity maximums (default={"p_l":30.0, "fovelv":40.0})
    iinc : (dict)
        Intensity tick incriments (default={"p_l":6, "fovelv":6})
    ymin : (int or float)
        Lowest plotted range gate (default=20)
    ymax : (int or float)
        Highest plotted range gate (default=60)
    rad_bms : (dict)
        Dictionary with radar code names as keys and the beam to process
        as the value.  (default={"han":5,"pyk":15})
    rad_cp : (dict)
        Dictionary with radar program mode to load
        (default={"han":-6312, "pyk":-6312})
    fix_gs : (dict)
        Dictionary with radar code names as keys and min/max range gate pairs
        in a list, specifying the ranges where groundscatter should be flagged
        as ionospheric backscatter (heater backscatter behaves slightly
        differenntly than normal ionospheric backscatter).
        (default={"han":[[20,40]]})
    figname : (str or NoneType)
        Figure name or None if no figure is to be saved (default=None)
    password : (boolian or str)
        When downloading data from your specified SuperDARN mirror site, a
        password may be needed.  It may be included here or, if True is used,
        a prompt will appear for you to enter it securely.  (default=True)
    file_type : (str)
        Type of data file to download (default="fitacf")
    logfile : (str or NoneType)
        Name of file to hold the log output or None for stdout. (default=None)
    log_level : (int)
        Level of output to report.  Flag values explained in logging module.
        (default=logging.WARNING)
    min_pnts : (int)
        The minimum number of points necessary to perform certain range gate
        or beam specific evaluations. (default=3)
    region_hmin : (dict)
        Minimum virtual heights allowed in each ionospheric layer.
        (default={"D":75.0,"E":115.0,"F":150.0})
    region_hmax : (dict)
        Maximum virtual heights allowed in each ionospheric layer.
        (default={"D":115.0,"E":150.0,"F":900.0})
    rg_box : (list of int)
        The total number of range gates to include when examining the elevation
        angle across all beams. (default=[2,5,10,20])
    vh_box : (list of float)
        The total width of the altitude box to consider when examining the
        elevation angle across all beams at a given range gate.
        (default=[50.0,50.0,50.0,150.0])
    max_rg : (list)
        Maximum range gate to use each range gate and virtual height at
        (default=[5,25,40,76])
    max_hop : (float)
        Maximum hop that the corresponding rg_box and vh_box values applies
        to.  (default=3.0)
    ut_box : (class dt.timedelta)
        Total width of universal time box to examine for backscatter FoV
        continuity. (default=20.0 minutes)
    tdiff : (function or NoneType)
        A function to retrieve tdiff values (in microsec) using the radar ID
        number current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_args.  Example:
        def get_tdiff(stid, time, tfreq, filename) { do things } return tdiff
        tdiff=get_tdiff, tdiff_args=["tdiff_file"]
        (default=None)
    tdiff_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff function.
        (default=list())
    tdiff_e : function or NoneType)
        A function to retrieve tdiff error values (in microsec) using the radar
        ID number, current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_e_args.  Example:
        def get_tdiffe(stud, time, tfreq, filename) { do things } return tdiffe
        tdiff_e=get_tdiffe, tdiff_e_args=["tdiff_file"]
        (default=None)
    tdiff_e_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff_e function.
        (default=list())
    ptest : (boolian)
        Test to see if a propagation path is realistic (default=True)
    step : (int)
        Level of processing to perform (1-6).  6 performs all steps. (default=6)
    strict_gs : (boolian)
        Remove indeterminately flagged backscatter (default=True)
    draw : (boolian)
        Output figure to display? (default=True)
    label_type : (str)
        Type of hop label to use (frac/decimal) (default="frac")
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots.  Will create this data
        if it is not provided (default=dict())

    Returns
    ---------
    f : (pointer)
        Figure handle
    ax : (dict)
        Dictionary of axis handles
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots
    """
    import davitpy.pydarn.radar as pyrad

    # Load and process the desired data
    dout = load_test_beams(intensity_all, intensity_sep, stime, etime,
                           rad_bms, rad_cp, fix_gs=fix_gs,
                           marker_key=marker_key,  password=password,
                           file_type=file_type, logfile=logfile,
                           log_level=log_level, min_pnts=min_pnts,
                           region_hmax=region_hmax, region_hmin=region_hmin,
                           rg_box=rg_box, vh_box=vh_box, max_rg=max_rg,
                           max_hop=max_hop, ut_box=ut_box, tdiff=tdiff,
                           tdiff_args=tdiff_args, tdiff_e=tdiff_e,
                           tdiff_e_args=tdiff_e_args, ptest=ptest, step=step,
                           strict_gs=strict_gs, beams=beams)

    rad = rad_bms.keys()[0]
    if not dout[0].has_key(rad) or len(dout[0][rad]) == 0:
        estr = "can't find radar [" + rad + "] in data:" + dout[0].keys()
        logging.error(estr)
        return(dout[0], dout[1], dout[2], beams)

    # Recast the data as numpy arrays
    xtime = {rad:np.array(dout[0][rad]) for rad in rad_bms.keys()}
    yrange = {rad:np.array(dout[1][rad]) for rad in rad_bms.keys()}
    zdata = {rad:{ii:np.array(dout[2][ii][rad]) for ii in dout[2].keys()}
             for rad in rad_bms.keys()}
    zi = {rad:{ff:{hh:dout[3][ff][rad][hh] for hh in dout[3][ff][rad].keys()}
          for ff in dout[3].keys()} for rad in rad_bms.keys()}

    # Initialize the figure
    iax = {ff:i for i,ff in enumerate(["all",1,-1,0])}
    irad = {rad:i for i,rad in enumerate(rad_bms.keys())}
    f = plt.figure(figsize=(12,10))
    ax = {rad:{ff:f.add_subplot(4,2,2*(iax[ff]+1)-irad[rad])
               for ff in iax.keys()} for rad in irad.keys()}
    pos = {ff:[.91,.14+(3-iax[ff])*.209,.01,.183] for ff in iax.keys()}
    xpos = {13:2.3, 12:2.2, 11:2.1, 10:1.95, 9:1.9, 8:1.8, 7:1.7, 6:1.6, 5:1.5,
            4:1.4, 3:1.3, 2:1.2, 1:1.1}
    ylabel = {"all":"Range Gate",1:"Front\nRange Gate",-1:"Rear\nRange Gate",
              0:"Unassigned\nRange Gate"}
    cb = dict()
    handles = list()
    labels = list()

    # Cycle through each plot, adding the appropriate data
    for rad in irad.keys():
        # Cycle through the field-of-view keys
        for ff in ax[rad].keys():
            # Add a background color to the subplot
            ax[rad][ff].set_axis_bgcolor(acolor)

            # Plot the data
            if ff is "all":
                zz = zi[rad][ff]['all']
                ii = intensity_all
                con = ax[rad][ff].scatter(xtime[rad][zz], yrange[rad][zz],
                                          c=zdata[rad][ii][zz],
                                          cmap=cm.get_cmap(color[ii]),
                                          vmin=imin[ii], vmax=imax[ii], s=20,
                                          edgecolor="face", linewidth=2.0,
                                          marker=mm[marker_key][ff])
            else:
                ii = intensity_sep
                for hh in mc[marker_key].keys():
                    zz = zi[rad][ff][hh]
                    try:
                        label = "{:.1f}".format(hh)
                    except:
                        label = "{:}".format(hh)

                    if intensity_sep is "hop":
                        ax[rad][ff].plot(xtime[rad][zz], yrange[rad][zz], ms=8,
                                         edgecolor="face",
                                         marker=mm[marker_key][hh],
                                         color=mc[marker_key][hh], label=label)
                    elif len(zz) > 0:
                        con = ax[rad][ff].scatter(xtime[rad][zz],
                                                  yrange[rad][zz],
                                                  c=zdata[rad][ii][zz],
                                                  cmap=cm.get_cmap(color[ii]),
                                                  vmin=imin[ii], vmax=imax[ii],
                                                  s=20, edgecolor="face",
                                                  marker=mm[marker_key][hh],
                                                  label=label)

            # Format the axes; add titles, colorbars, and labels
            ax[rad][ff].set_xlim(mdates.date2num(stime),
                                 mdates.date2num(etime))
            ax[rad][ff].set_ylim(ymin-1,ymax+2)

            ax[rad][ff].xaxis.set_major_locator( \
                                            mdates.MinuteLocator(interval=10))
            ax[rad][ff].yaxis.set_major_locator(ticker.MultipleLocator(10))

            if irad[rad] == 1:
                ax[rad][ff].set_ylabel(ylabel[ff])

            if irad[rad] == 0:
                tfmt = ticker.FormatStrFormatter("")
                ax[rad][ff].yaxis.set_major_formatter(tfmt)
                if ii is not "hop":
                    label = pyrad.radUtils.getParamDict(ii)['label']
                    unit = pyrad.radUtils.getParamDict(ii)['unit']
                    if not iinc.has_key(ii):
                        iinc[ii] = 6
                    cb[ff] = add_colorbar(f, con, imin[ii], imax[ii], iinc[ii],
                                          label, unit, loc=pos[ff])


            if ff is "all":
                ax[rad][ff].set_title("{:s} Beam {:d}".format(rad.upper(),
                                                              rad_bms[rad]),
                                      fontsize="medium")

            if iax[ff] == 3:
                tfmt = mdates.DateFormatter("%H:%M")
                ax[rad][ff].set_xlabel("Universal Time (HH:MM)")

                # Add legend labels and handles
                hl, ll = get_sorted_legend_labels(ax[rad][ff], marker_key)

                if len(handles) == 0:
                    handles = hl
                    labels = ll
                else:
                    for il,label in enumerate(ll):
                        try:
                            labels.index(label)
                        except:
                            # This label is not currently available, add it
                            lind = morder[marker_key][label]
                            jl = 0
                            while lind > morder[marker_key][labels[jl]]:
                                jl += 1

                            labels.insert(jl, label)
                            handles.insert(jl, hl[il])
            else:
                tfmt = mdates.DateFormatter("")

            ax[rad][ff].xaxis.set_major_formatter(tfmt)

    if label_type.find("frac") >= 0:
        flabels = get_fractional_hop_labels(labels)

    ax[rad][0].legend(handles, flabels, fontsize="medium", scatterpoints=1,
                      ncol=len(flabels), title="Hop", labelspacing=.1,
                      columnspacing=0, markerscale=2, borderpad=0.3,
                      handletextpad=0, bbox_to_anchor=(xpos[len(flabels)],-0.3))
    plt.subplots_adjust(hspace=.15, wspace=.15, bottom=.14, left=.1, top=.95)

    if draw:
        # Draw to screen.
        if plt.isinteractive():
            plt.draw() #In interactive mode, you just "draw".
        else:
            # W/o interactive mode, "show" stops the user from typing more 
            # at the terminal until plots are drawn.
            plt.show()

    if figname is not None:
        f.savefig(figname)

    return(f, ax, beams)

#-------------------------------------------------------------------------
def plot_milan_figure9(intensity_all="p_l", intensity_sep="p_l",
                       marker_key="reg", color={"p_l":clinear, "p_l":clinear},
                       acolor="0.9", stime=dt.datetime(1995,12,14,5),
                       etime=dt.datetime(1995,12,14,16), imin={"p_l":0.0},
                       imax={"p_l":30.0}, rad="han", bmnum=2, cp=127,
                       figname=None, password=True, file_type="fitacf",
                       logfile=None, log_level=logging.WARN, min_pnts=3,
                       region_hmax={"D":115.0,"E":150.0,"F":900.0},
                       region_hmin={"D":75.0,"E":115.0,"F":150.0},
                       rg_box=[2,5,10,20], vh_box=[50.0,50.0,50.0,150.0],
                       max_rg=[5,25,40,76], max_hop=3.0,
                       ut_box=dt.timedelta(minutes=20.0), tdiff=None,
                       tdiff_args=list(), tdiff_e=None, tdiff_e_args=list(),
                       ptest=True, step=6, strict_gs=True, draw=True,
                       label_type="frac", beams=dict()):
    """Plot based on Figure 9 in Milan et al (1997) Annales Geophysicae, 15,
    29-39.

    Parameters
    -----------
    intensity_all : (str)
        Intensity attribute to plot in the top figure with unseperated fields-
        of-view.  Uses SuperDARN beam fit attribute names. (default="p_l")
    intensity_sep : (str)
        Intensity attribute to plot in the separated fields-of-view.  Uses
        SuperDARN beam fit attribute names. (default="fovelv")
    marker_key : (str)
        key to denote what type of marker labels are being used (default="reg")
    color : (dict of str)
        Intensity color scheme.  Defaults to the standard centered color
        scheme for this program.  Yeoman et al (2001) used "jet".
    acolor : (str or tuple)
        Background color for subplots (default="0.9" - light grey)
    stime : (dt.datetime)
        Starting time of plot (will pad loaded data).
        (default=dt.datetime(1998,10,15,12,10))
    etime : (dt.datetime)
        Ending time of plot (will pad loaded data).
        (default=dt.datetime(1998,10,15,12,50))
    imin : (dict)
        Intensity minimums (default={"p_l":0.0})
    imax : (dict)
        Intensity maximums (default={"p_l":30.0})
    rad : (str)
        radar code (default="han")
    bmnum : (int)
        Beam number (default=2)
    cp : (int)
        Radar programming code number. (default=127)
    figname : (str or NoneType)
        Figure name or None if no figure is to be saved (default=None)
    password : (boolian or str)
        When downloading data from your specified SuperDARN mirror site, a
        password may be needed.  It may be included here or, if True is used,
        a prompt will appear for you to enter it securely.  (default=True)
    file_type : (str)
        Type of data file to download (default="fitacf")
    logfile : (str or NoneType)
        Name of file to hold the log output or None for stdout. (default=None)
    log_level : (int)
        Level of output to report.  Flag values explained in logging module.
        (default=logging.WARNING)
    min_pnts : (int)
        The minimum number of points necessary to perform certain range gate
        or beam specific evaluations. (default=3)
    region_hmax : (dict)
        Maximum virtual heights allowed in each ionospheric layer.
        (default={"D":115.0,"E":150.0,"F":900.0})
    region_hmin : (dict)
        Minimum virtual heights allowed in each ionospheric layer.
        (default={"D":75.0,"E":115.0,"F":150.0})
    rg_box : (list of int)
        The total number of range gates to include when examining the elevation
        angle across all beams. (default=[2,5,10,20])
    vh_box : (list of float)
        The total width of the altitude box to consider when examining the
        elevation angle across all beams at a given range gate.
        (default=[50.0,50.0,50.0,150.0])
    max_rg : (list)
        Maximum range gate to use each range gate and virtual height at
        (default=[5,25,40,76])
    max_hop : (float)
        Maximum hop that the corresponding rg_box and vh_box values applies
        to.  (default=3.0)
    ut_box : (class dt.timedelta)
        Total width of universal time box to examine for backscatter FoV
        continuity. (default=20.0 minutes)
    tdiff : (function or NoneType)
        A function to retrieve tdiff values (in microsec) using the radar ID
        number current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_args.  Example:
        def get_tdiff(stid, time, tfreq, filename) { do things } return tdiff
        tdiff=get_tdiff, tdiff_args=["tdiff_file"]
        (default=None)
    tdiff_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff function.
        (default=list())
    tdiff_e : function or NoneType)
        A function to retrieve tdiff error values (in microsec) using the radar
        ID number, current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_e_args.  Example:
        def get_tdiffe(stud, time, tfreq, filename) { do things } return tdiffe
        tdiff_e=get_tdiffe, tdiff_e_args=["tdiff_file"]
        (default=None)
    tdiff_e_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff_e function.
        (default=list())
    ptest : (boolian)
        Test to see if a propagation path is realistic (default=True)
    step : (int)
        Level of processing to perform (1-6).  6 performs all steps. (default=6)
    strict_gs : (boolian)
        Remove indeterminately flagged backscatter (default=True)
    draw : (boolian)
        Output figure to display? (default=True)
    label_type : (str)
        Type of hop label to use (frac/decimal) (default="frac")
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots.  Will create this data
        if it is not provided (default=dict())

    Returns
    ---------
    f : (pointer)
        Figure handle
    ax : (dict)
        Dictionary of axis handles
    cb : (dict)
        Dictionary of colorbar handles
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots
    """

    # Load and process the desired data
    dout = load_test_beams(intensity_all, intensity_sep, stime, etime,
                           {rad:bmnum}, {rad:cp}, marker_key=marker_key,
                           password=password, file_type=file_type,
                           logfile=logfile,log_level=log_level,
                           min_pnts=min_pnts, region_hmax=region_hmax,
                           region_hmin=region_hmin, rg_box=rg_box,
                           vh_box=vh_box, max_rg=max_rg, max_hop=max_hop,
                           ut_box=ut_box, tdiff=tdiff, tdiff_args=tdiff_args,
                           tdiff_e=tdiff_e, tdiff_e_args=tdiff_e_args,
                           ptest=ptest, step=step, strict_gs=strict_gs,
                           beams=beams)

    if not dout[0].has_key(rad) or len(dout[0][rad]) == 0:
        estr = "can't find radar [" + rad + "] in data:" + dout[0].keys()
        logging.error(estr)
        return(dout[0], dout[1], dout[2], beams)

    # Recast the data as numpy arrays
    xtime = np.array(dout[0][rad])
    yrange = np.array(dout[1][rad])
    zdata = {ff:np.array(dout[2][ff][rad]) for ff in dout[2].keys()}
    zi = {ff:{hh:dout[3][ff][rad][hh] for hh in dout[3][ff][rad].keys()}
          for ff in dout[3].keys()}

    # Initialize the figure
    f = plt.figure(figsize=(7,10))

    if cp is not None:
        ftitle = "{:s} Beam {:d} CP {:d} on {:}".format(rad.upper(), bmnum, cp,
                                                        stime.date())
    else:
        ftitle = "{:s} Beam {:d} on {:}".format(rad.upper(), bmnum,
                                                stime.date())

    ax, cb = plot_single_column(f, xtime, yrange, zdata, zi,
                                {"all":intensity_all, "sep":intensity_sep},
                                color, marker_key=marker_key,
                                xmin=mdates.date2num(stime),
                                xmax=mdates.date2num(etime), ymin=-1, ymax=76,
                                zmin=imin, zmax=imax,
                                xfmt=mdates.DateFormatter("%H:%M"), yfmt=None,
                                xinc=mdates.HourLocator(interval=2),
                                yinc=ticker.MultipleLocator(15),
                                xlabel="Universal Time (HH:MM)",
                                ylabels=["Range Gate","Front\nRange Gate",
                                         "Rear\nRange Gate",
                                         "Unassigned\nRange Gate"],
                                titles=["","","",""], plot_title=ftitle,
                                label_type=label_type, acolor=acolor,
                                draw=False)

    if draw:
        # Draw to screen.
        if plt.isinteractive():
            plt.draw() #In interactive mode, you just "draw".
        else:
            # W/o interactive mode, "show" stops the user from typing more 
            # at the terminal until plots are drawn.
            plt.show()

    if figname is not None:
        f.savefig(figname)

    return(f, ax, cb, beams)

#-------------------------------------------------------------------------
def plot_storm_figures(intensity_all="v", intensity_sep="v", marker_key="reg",
                       color={"v":ccenter}, acolor="0.9",
                       stime=dt.datetime(1997,10,10,15),
                       etime=dt.datetime(1997,10,10,20),
                       mtimes=[dt.datetime(1997,10,10,16),
                               dt.datetime(1997,10,10,17,30),
                               dt.datetime(1997,10,10,18,30),
                               dt.datetime(1997,10,10,19,30)], coords="mlt",
                       imin={"v":-500.0}, imax={"v":500.0}, zinc={"v":5.0},
                       rad="pyk", bmnum=0, cp=None, figname_time=None,
                       figname_maps=None, password=True, file_type="fitacf",
                       logfile=None, log_level=logging.WARN, min_pnts=3,
                       region_hmax={"D":115.0,"E":150.0,"F":900.0},
                       region_hmin={"D":75.0,"E":115.0,"F":150.0},
                       rg_box=[2,5,10,20], vh_box=[50.0,50.0,50.0,150.0],
                       max_rg=[5,25,40,76], max_hop=3.0,
                       ut_box=dt.timedelta(minutes=20.0), tdiff=None,
                       tdiff_args=list(), tdiff_e=None, tdiff_e_args=list(),
                       ptest=True, step=6, strict_gs=True, draw=True,
                       label_type="frac", beams=dict()):
    """Plot showing a period of time where E-region scatter past over the
    radar at pyk.

    Parameters
    -----------
    intensity_all : (str)
        Intensity attribute to plot in the top figure with unseperated fields-
        of-view.  Uses SuperDARN beam fit attribute names. (default='v')
    intensity_sep : (str)
        Intensity attribute to plot in the separated fields-of-view.  Uses
        SuperDARN beam fit attribute names. (default='fovelv')
    marker_key : (str)
        key to denote what type of marker labels are being used, including:
        'region', 'reg', and 'hop'. (default='reg')
    color : (dict of str)
        Intensity color scheme.  Defaults to the standard centered color
        scheme for this program.
    color : (dict of str)
        Intensity color scheme.  Defaults to the standard centered color
        scheme for this program.
    acolor : (str or tuple)
        Background color for subplots (default="0.9" - light grey)
    stime : (dt.datetime)
        Starting time of plot (will pad loaded data).
        (default=dt.datetime(1997,10,10,15))
    etime : (dt.datetime)
        Ending time of plot (will pad loaded data).
        (default=dt.datetime(1997,10,10,20))
    mtimes : (list of dt.datetimes)
        Times to plot maps, unless no times are provided.
        (default=[dt.datetime(1997,10,10,16), dt.datetime(1997,10,10,17,30),
                  dt.datetime(1997,10,10,18,30), dt.datetime(1997,10,10,19,30)])
    coords : (str)
        Type of map to plot ("geo" or "mlt") (default="mlt")
    imin : (dict)
        Dictionary of intensity minimums (default={"v":-500.0})
    imax : (dict)
        Dictionary of intensity maximums (default={"v":500.0})
    zinc : (dict)
        Dictionary of intensity colorbar tick incriments (default={"v":5.0})
    rad : (str)
        radar code (default="pyk")
    bmnum : (int)
        Beam number (default=0)
    cp : (int)
        Radar programming code number. (default=127)
    figname_time : (str or NoneType)
        Figure name or None if the time figure is not to be saved (default=None)
    figname_maps : (str or NoneType)
        Figure name or None if the map figure is not to be saved (default=None)
    password : (boolian or str)
        When downloading data from your specified SuperDARN mirror site, a
        password may be needed.  It may be included here or, if True is used,
        a prompt will appear for you to enter it securely.  (default=True)
    file_type : (str)
        Type of data file to download (default="fitacf")
    logfile : (str or NoneType)
        Name of file to hold the log output or None for stdout. (default=None)
    log_level : (int)
        Level of output to report.  Flag values explained in logging module.
        (default=logging.WARNING)
    min_pnts : (int)
        The minimum number of points necessary to perform certain range gate
        or beam specific evaluations. (default=3)
    region_hmax : (dict)
        Maximum virtual heights allowed in each ionospheric layer.
        (default={"D":115.0,"E":150.0,"F":900.0})
    region_hmin : (dict)
        Minimum virtual heights allowed in each ionospheric layer.
        (default={"D":75.0,"E":115.0,"F":150.0})
    rg_box : (list of int)
        The total number of range gates to include when examining the elevation
        angle across all beams. (default=[2,5,10,20])
    vh_box : (list of float)
        The total width of the altitude box to consider when examining the
        elevation angle across all beams at a given range gate.
        (default=[50.0,50.0,50.0,150.0])
    max_rg : (list)
        Maximum range gate to use each range gate and virtual height at
        (default=[5,25,40,76])
    max_hop : (list of floats)
        Maximum hop that the corresponding rg_box and vh_box values applies
        to.  (default=3.0)
    ut_box : (class dt.timedelta)
        Total width of universal time box to examine for backscatter FoV
        continuity. (default=20.0 minutes)
    tdiff : (function or NoneType)
        A function to retrieve tdiff values (in microsec) using the radar ID
        number current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_args.  Example:
        def get_tdiff(stid, time, tfreq, filename) { do things } return tdiff
        tdiff=get_tdiff, tdiff_args=["tdiff_file"]
        (default=None)
    tdiff_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff function.
        (default=list())
    tdiff_e : function or NoneType)
        A function to retrieve tdiff error values (in microsec) using the radar
        ID number, current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_e_args.  Example:
        def get_tdiffe(stud, time, tfreq, filename) { do things } return tdiffe
        tdiff_e=get_tdiffe, tdiff_e_args=["tdiff_file"]
        (default=None)
    tdiff_e_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff_e function.
        (default=list())
    ptest : (boolian)
        Test to see if a propagation path is realistic (default=True)
    step : (int)
        Level of processing to perform (1-6).  6 performs all steps. (default=6)
    strict_gs : (boolian)
        Remove indeterminately flagged backscatter (default=True)
    draw : (boolian)
        Output figure to display? (default=True)
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots.  Will create this data
        if it is not provided (default=dict())

    Returns
    ---------
    f : (pointer)
        Figure handle
    ax : (dict)
        Dictionary of axis handles
    cb : (dict)
        Dictionary of colorbar handles
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots
    """
    import davitpy.pydarn.radar as pyrad
    import davitpy.utils as dutils

    # Load and process the desired data
    dout = load_test_beams(intensity_all, intensity_sep, stime, etime,
                           {rad:bmnum}, {rad:None}, marker_key=marker_key,
                           password=password, file_type=file_type,
                           logfile=logfile, log_level=log_level,
                           min_pnts=min_pnts, region_hmax=region_hmax,
                           region_hmin=region_hmin, rg_box=rg_box,
                           vh_box=vh_box, max_rg=max_rg, max_hop=max_hop,
                           ut_box=ut_box, tdiff=tdiff, tdiff_args=tdiff_args,
                           tdiff_e=tdiff_e, tdiff_e_args=tdiff_e_args,
                           ptest=ptest, step=step, strict_gs=strict_gs,
                           beams=beams)

    if not dout[0].has_key(rad) or len(dout[0][rad]) == 0:
        estr = "can't find radar [" + rad + "] in data:" + dout[0].keys()
        logging.error(estr)
        return(dout[0], dout[1], dout[2], beams)

    # Recast the data as numpy arrays
    xtime = np.array(dout[0][rad])
    yrange = np.array(dout[1][rad])
    zdata = {ff:np.array(dout[2][ff][rad]) for ff in dout[2].keys()}
    zi = {ff:{hh:dout[3][ff][rad][hh] for hh in dout[3][ff][rad].keys()}
          for ff in dout[3].keys()}

    # Initialize the time figure
    f = plt.figure(figsize=(7,10))

    if cp is not None:
        ftitle = "{:s} Beam {:d} CP {:d} on {:}".format(rad.upper(), bmnum, cp,
                                                        stime.date())
    else:
        ftitle = "{:s} Beam {:d} on {:}".format(rad.upper(), bmnum,
                                                stime.date())

    ax, cb = plot_single_column(f, xtime, yrange, zdata, zi,
                                {"all":intensity_all, "sep":intensity_sep},
                                color, marker_key=marker_key,
                                xmin=mdates.date2num(stime),
                                xmax=mdates.date2num(etime), ymin=-1,
                                ymax=76, zmin=imin, zmax=imax, zinc=zinc,
                                xfmt=mdates.DateFormatter("%H:%M"), yfmt=None,
                                xinc=mdates.HourLocator(interval=2),
                                yinc=ticker.MultipleLocator(15),
                                xlabel="Universal Time (HH:MM)",
                                ylabels=["Range Gate","Front\nRange Gate",
                                         "Rear\nRange Gate",
                                         "Unassigned\nRange Gate"],
                                titles=["","","",""], plot_title=ftitle,
                                label_type=label_type, acolor=acolor,
                                draw=False)

    mlen = len(mtimes)
    if mlen > 0:
        # Add lines corresponding to map times to each line of the plot
        for mt in mtimes:
            for a in ax.values():
                a.plot([mt, mt], [-1, 76], "k--")

        # Initialize the map figure
        if coords.lower() == "geo":
            fmap = plt.figure(figsize=(12, 3 * mlen))
            nrows = int(np.ceil(0.5*mlen))
            axmap = [fmap.add_subplot(2, nrows, ia+1) for ia in range(mlen)]
            hard = None
            fovs = {1:None, -1:None}
            mmm = None
            for ia,mt in enumerate(sorted(mtimes)):
                scan = list()
                for k in beams[rad].keys():
                    j = 0
                    while j < len(beams[rad][k]):
                        if beams[rad][k][j].scan_time > mt:
                            break
                        elif beams[rad][k][j].scan_time == mt:
                            scan.append(beams[rad][k][j])
                        j += 1

                llab = True if ia % 2 == 0 else False
                axmap[ia].set_axis_bgcolor(acolor)
                mm, fovs, hard, con = plot_map(axmap[ia], scan, hard=hard,
                                               map_handle=mm, fovs=fovs,
                                               plot_beams={1:[bmnum],
                                                           -1:[bmnum]},
                                               color_beams={1:["0.6"],
                                                            -1:["0.6"]},
                                               maxgates=45,
                                               dat_attr=intensity_all,
                                               fov_attr="fovflg",
                                               dmax=imax[intensity_all],
                                               dmin=imin[intensity_all],
                                               dcolor=color[intensity_all],
                                               lat_label=llab, draw=False)

            label = pyrad.radUtils.getParamDict(intensity_all)['label']
            unit = pyrad.radUtils.getParamDict(intensity_all)['unit']
            cbmap = add_colorbar(fmap, con, imin[intensity_all],
                                 imax[intensity_all], zinc[intensity_all],
                                 label, unit, loc=[0.91,.1,.01,.8])
            plt.subplots_adjust(wspace=.05)
        elif coords.lower() == "mlt":
            fov_dir = {1:"front", -1:"back"}

            # Determine the largest and smallest MLTs
            mlts = np.ndarray(shape=mlen, dtype=float) * np.nan
            quarters = np.zeros(shape=mlen, dtype=int)
            hard = list()
            for ia,mt in enumerate(mtimes):
                hard.append(pyrad.site(code=rad, dt=mt))
                mlon = dutils.coordUtils.coord_conv(hard[ia].geolon,
                                                    hard[ia].geolat, "geo",
                                                    "mlt", 300.0, mt)[0]
                
                mlts[ia] = mlon * 24.0 / 360.0
                if mlts[ia] < 0.0:
                    mlts[ia] = mlts[ia] + 24.0
                if mlts[ia] >= 24.0:
                    mlts[ia] = mlts[ia] - 24.0

                # Assign MLT clock corners
                if mlts[ia] < 12.0 and mlts[ia] >= 6.0:
                    quarters[ia] = 1
                elif mlts[ia] < 6.0:
                    quarters[ia] = 2
                elif mlts[ia] >= 18.0:
                    quarters[ia] = 3
                else:
                    quarters[ia] = 4

            quarters = list(set(quarters))
            qlen = len(quarters)
            qmin = min(quarters)
            qmax = max(quarters)
            fwidth = 12 if qlen>2 or (qlen>1 and qmin<3 and qmax>2) else 6
            fheight = 6
            if(qlen > 2 or (qlen > 1 and (qmin > 1 and qmin < 4 and qmax == 4)
                            or (qmin == 1 and qmax < 4))):
               fheight *= 2
            proj = "npstere" if hard[0].geolat > 0.0 else "spstere"
            boundinglat = (np.sign(hard[0].geolat) *
                           (np.floor(abs(hard[0].geolat) / 10.0 - 1.0) * 10.0))
            boundinglat = 56.0
            mwidth = 111.0e3 * boundinglat * fwidth / 6.0
            mheight = 111.0e3 * boundinglat * fheight / 6.0
            lat_0 = np.sign(hard[0].geolat) * 90.0
            lon_0 = 0.0

            fmap = plt.figure(figsize=(12,12))
            axmap = fmap.add_subplot(1,1,1)
            axmap.set_axis_bgcolor(acolor)

            # Cycle through times
            for ia,mt in enumerate(sorted(mtimes)):
                # Load data
                scan = list()
                for k in beams[rad].keys():
                    j = 0
                    while j < len(beams[rad][k]):
                        if beams[rad][k][j].scan_time > mt:
                            break
                        elif beams[rad][k][j].scan_time == mt:
                            scan.append(beams[rad][k][j])
                        j += 1

                # Initialize map, hardware data, and fovs
                fovs = {ff:pyrad.radFov.fov(site=hard[ia],
                                            rsep=scan[0].prm.rsep,
                                            nbeams=hard[ia].maxbeam, ngates=45,
                                            bmsep=hard[ia].bmsep, model="IS",
                                            coords=coords, date_time=mt,
                                            fov_dir=fov_dir[ff])
                        for ff in [1,-1]}
                mmm = dutils.plotUtils.mapObj(ax=axmap, datetime=mt,
                                              coords=coords, projection=proj,
                                              resolution="c", lon_0=0, lat_0=90,
                                              boundinglat=boundinglat,
                                              draw_map=False, grid=True,
                                              gridLabels=False, round=True)

                mmm, fovs, hh, con = plot_map(axmap, scan, hard=hard[ia],
                                              map_handle=mmm, fovs=fovs,
                                              plot_beams={1:[bmnum],-1:[bmnum]},
                                              color_beams={1:["0.6"],
                                                           -1:["0.6"]},
                                              maxgates=45,
                                              dat_attr=intensity_all,
                                              fov_attr="fovflg",
                                              dmax=imax[intensity_all],
                                              dmin=imin[intensity_all],
                                              dcolor=color[intensity_all],
                                              draw_map=False, plot_name=False,
                                              draw=False)
                axmap.set_title("")

            # Add clock hours
            (xmin, xmax) = axmap.get_xlim()
            (ymin, ymax) = axmap.get_ylim()
            axmap.text(xmax*0.47, ymax*1.01, "12:00", fontsize="medium")
            axmap.text(xmax*0.47, -ymax*0.02, "00:00", fontsize="medium")
            axmap.text(-xmax*0.07, ymax*0.495, "18:00", fontsize="medium")
            axmap.text(xmax*1.01, ymax*0.495, "06:00", fontsize="medium")
            axmap.text(xmax*0.86, ymax*0.12, "03:00", fontsize="medium")
            axmap.text(xmax*0.09, ymax*0.12, "21:00", fontsize="medium")
            axmap.text(xmax*0.09, ymax*0.87, "15:00", fontsize="medium")
            axmap.text(xmax*0.86, ymax*0.86, "09:00", fontsize="medium")
            fmap.suptitle("{:s} Magnetic Local Time".format(rad.upper()))

            # Fix axis and figure limits
            if fwidth < 12:
                if qmin > 2:
                    axmap.set_xlim(xmin, xmax * 0.51)
                else:
                    axmap.set_xlim(xmax * 0.49, xmax)
            if fheight < 12:
                if qmax < 4 and qmin > 1:
                    axmap.set_ylim(ymin, ymax * 0.51)
                else:
                    axmap.set_ylim(ymax * 0.49, ymax)

            if fwidth < 12 or fheight < 12:
                fmap.set_size_inches(fwidth, fheight)

            label = pyrad.radUtils.getParamDict(intensity_all)['label']
            unit = pyrad.radUtils.getParamDict(intensity_all)['unit']
            cbmap = add_colorbar(fmap, con, imin[intensity_all],
                                 imax[intensity_all], zinc[intensity_all],
                                 label, unit, orient="horizontal",
                                 loc=[0.1,.05,.8,.01])

            
        else:
            estr = "{:s} WARNING: unknown coordinate ".format(rn)
            estr = "{:s}format [{:}]".format(estr, coords)
            logging.warning(estr)
            fmap = None
            axmap = None
            cbmap = None
    else:
        fmap = None
        axmap = None
        cbmap = None

    if draw:
        # Draw to screen.
        if plt.isinteractive():
            plt.draw() #In interactive mode, you just "draw".
        else:
            # W/o interactive mode, "show" stops the user from typing more 
            # at the terminal until plots are drawn.
            plt.show()

    # Save the figures, if desired
    if figname_time is not None:
        f.savefig(figname_time)

    if figname_maps is not None and fmap is not None:
        fmap.savefig(figname_maps)

    # Return figure, axis, and colorbar handles, as well as beams
    return({"time":f, "maps":fmap}, {"time":ax, "maps":axmap},
           {"time":cb, "maps":cbmap}, beams)

#-------------------------------------------------------------------------
def plot_single_column(f, xdata, ydata, zdata, zindices, zname, color,
                       marker_key="reg", xmin=None, xmax=None, ymin=None,
                       ymax=None, zmin=None, zmax=None, xfmt=None, yfmt=None,
                       xinc=None, yinc=None, zinc=dict(), xlabel="",
                       ylabels=["All","Front","Rear","Unassigned"],
                       titles=["","","",""], plot_title="", label_type="frac",
                       acolor="w", draw=True):
    """Plot single column of subplots with all data in the first row using one
    type of data in the z-axis, and a second type of data in the z-axis for the
    final rows, which plot only data belonging to the front, rear, and no field-
    of-view

    Parameters
    -----------
    f : (pointer)
        Figure handle
    xdata : (numpy array)
        x data (typically time)
    ydata : (numpy array)
        y data (typically time)
    zdata : (dict of numpy arrays)
        Dictionary of numpy arrays containing z data
    zindices : (dict of dicts/lists)
        Dictionary of dictionaries or lists containing z indices
    zname : (dict of str)
        Dictionary of key names for data.  Keys are "all" and "sep".
    color : (dict of str)
        Intensity color scheme.  Defaults to the standard linear color
        scheme for this program.
    marker_key : (str)
        key to denote what type of marker labels are being used (default="reg")
    xmin : (float)
        Minimum x value to plot (default=None)
    xmax : (float)
        Maximum x value to plot (default=None)
    ymin : (float)
        Minimum y value to plot (default=None)
    ymax : (float)
        Maximum y value to plot (default=None)
    zmin : (dict of float)
        Dicitonary of minimum z values to plot (default=None)
    zmax : (dict of float)
        Dicitonary of maximum z values to plot (default=None)
    xfmt : (class)
        x-axis formatting class (default=None)
    yfmt : (class)
        y-axis formatting class (default=None)
    xinc : (float)
        x-axis tick incriment (default=None)
    yinc : (float)
        y-axis tick incriment (default=None)
    zinc : (dict of int)
        Dictionary of z colorbar tick incriments (default=dict())
    xlabel : (str)
        x axis label (default="")
    ylabels : (list of str)
        list of y axis labels (default=["All","Front","Rear","Unassigned"])
    titles : (list of str)
        list of subplot titles (default=["","","",""])
    plot_title : (str)
        Plot title (default="")
    label_type : (str)
        Type of hop label to use (frac/decimal) (default="frac")
    acolor : (str or tuple)
        Background color for subplots (default="0.9" - light grey)
    draw : (boolian)
        Output figure to display? (default=True)

    Returns
    ---------
    f : (pointer)
        Figure handle
    ax : (dict)
        Dictionary of axis handles
    """
    import davitpy.pydarn.radar as pyrad

    # Ensure the z limits have been set
    if zmin is None:
        zmin = {ff:zdata[ff].min() for ff in zdata.keys()}
    if zmax is None:
        zmax = {ff:zdata[ff].max() for ff in zdata.keys()}

    # Initialize the subplots
    xpos = {8:1.1, 7:1.1, 6:1.0, 5:0.9, 4:0.8, 3:0.7, 2:0.5, 1:0.0}
    iax = {ff:i for i,ff in enumerate(["all",1,-1,0])}
    ax = {ff:f.add_subplot(4,1,iax[ff]+1) for ff in iax.keys()}
    ypos = 0.89
    for zz in zmax.keys():
        if abs(zmin[zz]) > 100.0 or abs(zmax[zz]) > 100.0:
            ypos = 0.85

    pos = {ff:[ypos,.14+(3-iax[ff])*.209,.01,.184] for ff in iax.keys()}
    cb = dict()
    hops = list()
    for ff in zindices.keys():
        hops.extend([hh for hh in zindices[ff].keys()
                     if len(zindices[ff][hh]) > 0 and hh != "all"])
    hops = list(set(hops))
    handles = list()
    labels = list()

    # Cycle through the field-of-view keys
    for ff in iax.keys():
        # Set the plot background color
        ax[ff].set_axis_bgcolor(acolor)

        # Plot the data
        if ff is "all":
            ii = zname[ff]
            zz = zindices[ff]['all']
            cmap = cm.get_cmap(color[ii]) if isinstance(color[ii],
                                                        str) else color[ii]

            con = ax[ff].scatter(xdata[zz], ydata[zz], c=zdata[ii][zz],
                                 cmap=cmap, vmin=zmin[ii],
                                 vmax=zmax[ii], s=20, edgecolor="face",
                                 marker=mm[marker_key][ff], linewidth=2.5)
        else:
            ii = zname['sep']
            for hh in hops:
                zz = zindices[ff][hh]
                ll = hh if isinstance(hh, str) else "{:.1f}".format(hh)
                if ii is 'hop' or ii is 'reg':
                    ax[ff].plot(xdata[zz], ydata[zz], "|", ms=5, linewidth=3,
                                color=mc[marker_key][hh],
                                markeredgecolor=mc[marker_key][hh], label=ll)
                elif len(zz) > 0:
                    if isinstance(color[ii], str):
                        cmap = cm.get_cmap(color[ii])
                    else:
                        cmap = color[ii]

                    con = ax[ff].scatter(xdata[zz], ydata[zz], c=zdata[ii][zz],
                                         cmap=cmap, vmin=zmin[ii],
                                         vmax=zmax[ii], s=20, edgecolor="none",
                                         marker=mm[marker_key][hh], label=ll)

                # Save legend handles
                hl, ll = get_sorted_legend_labels(ax[ff], marker_key)

                for il,label in enumerate(ll):
                    try:
                        labels.index(label)
                    except:
                        # This label is not currently available, add it
                        lind = morder[marker_key][label]
                        jl = 0
                        try:
                            while lind > morder[marker_key][labels[jl]]:
                                jl += 1
                        except:
                            pass

                        labels.insert(jl, label)
                        handles.insert(jl, hl[il])

        # Format the axes; add titles, colorbars, and labels
        if xmin is None:
            try:
                xmin = xdata.min()
            except: pass
        if xmax is None:
            try:
                xmax = xdata.max()
            except: pass
        if xmin is not None and xmax is not None:
            ax[ff].set_xlim(xmin, xmax)

        if ymin is None:
            try:
                ymin = ydata.min()
            except: pass
        if ymax is None:
            try:
                ymax = ydata.max()
            except: pass
        if ymin is not None and ymax is not None:
            ax[ff].set_ylim(ymin, ymax)

        if xinc is not None:
            ax[ff].xaxis.set_major_locator(xinc)
        if yinc is not None:
            ax[ff].yaxis.set_major_locator(yinc)

        if iax[ff] == 3:
            ax[ff].set_xlabel(xlabel)
            if xfmt is not None:
                ax[ff].xaxis.set_major_formatter(xfmt)
                if label_type.find("frac") >= 0:
                    flabels = get_fractional_hop_labels(labels)
                ax[ff].legend(handles, flabels, fontsize="medium",
                              scatterpoints=1, ncol=len(hops), title="Hop",
                              labelspacing=.1, columnspacing=0, markerscale=2,
                              borderpad=0.3, handletextpad=0,
                              bbox_to_anchor=(xpos[len(hops)],-0.275))
        else:
            ax[ff].xaxis.set_major_formatter(ticker.FormatStrFormatter(""))
        ax[ff].set_ylabel(ylabels[iax[ff]])
        if yfmt is not None:
            ax[ff].yaxis.set_major_formatter(yfmt)

        if titles[iax[ff]] is not None:
            ax[ff].set_title(titles[iax[ff]], fontsize="medium")

        if ii is not "hop" and ii is not "reg":
            label = pyrad.radUtils.getParamDict(ii)['label']
            unit = pyrad.radUtils.getParamDict(ii)['unit']
            if not zinc.has_key(ii):
                zinc[ii] = 6
            cb[ff] = add_colorbar(f, con, zmin[ii], zmax[ii], zinc[ii], label,
                                  unit, loc=pos[ff])

        if plot_title is not None:
            f.suptitle(plot_title)

    plt.subplots_adjust(hspace=.15, wspace=.15, bottom=.14, left=.15,
                        right=ypos-.04, top=.95)

    if draw:
        # Draw to screen.
        if plt.isinteractive():
            plt.draw() #In interactive mode, you just "draw".
        else:
            # W/o interactive mode, "show" stops the user from typing more 
            # at the terminal until plots are drawn.
            plt.show()

    return ax, cb

#-----------------------------------------------------------------------
def load_test_beams(intensity_all, intensity_sep, stime, etime, rad_bms,
                    rad_cp, fix_gs=dict(), marker_key="hop", password=True,
                    file_type="fitacf", logfile=None, log_level=logging.WARN,
                    min_pnts=3, region_hmin={"D":75.0,"E":115.0,"F":150.0},
                    region_hmax={"D":115.0,"E":150.0,"F":900.0},
                    rg_box=[2,5,10,20], vh_box=[50.0,50.0,50.0,150.0],
                    max_rg=[5,25,40,76], max_hop=3.0,
                    ut_box=dt.timedelta(minutes=20.0),tdiff=None,
                    tdiff_args=list(), tdiff_e=None, tdiff_e_args=list(),
                    ptest=True, step=6, strict_gs=True, beams=dict()):
    """Load data for a test period, updating the beams to include origin field-
    of-view data and returning dictionaries of lists with time, range,
    and intensity data for a specified radar/beam combination.

    Parameters
    -----------
    intensity_all : (str)
        Intensity attribute to plot in the top figure with unseperated fields-
        of-view.  Uses SuperDARN beam fit attribute names.
    intensity_sep : (str)
        Intensity attribute to plot in the separated fields-of-view.  Uses
        SuperDARN beam fit attribute names.
    stime : (dt.datetime)
        Starting time of plot (will pad loaded data).
    etime : (dt.datetime)
        Ending time of plot (will pad loaded data).
    rad_bms : (dict)
        Dictionary with radar code names as keys and the beam to process
        as the value.  (example={"han":5,"pyk":15})
    fix_gs : (dict)
        Dictionary with radar code names as keys and min/max range gate pairs
        in a list, specifying the ranges where groundscatter should be flagged
        as ionospheric backscatter (heater backscatter behaves slightly
        differenntly than normal ionospheric backscatter).
        (example={"han":[[20,40]]})
    marker_key : (str)
        key to denote what type of marker labels are being used (default="reg")
    password : (boolian or str)
        When downloading data from your specified SuperDARN mirror site, a
        password may be needed.  It may be included here or, if True is used,
        a prompt will appear for you to enter it securely.  (default=True)
    file_type : (str)
        Type of data file to download (default="fitacf")
    logfile : (str or NoneType)
        Name of file to hold the log output or None for stdout. (default=None)
    log_level : (int)
        Level of output to report.  Flag values explained in logging module.
        (default=logging.WARNING)
    min_pnts : (int)
        The minimum number of points necessary to perform certain range gate
        or beam specific evaluations. (default=3)
    region_hmax : (dict)
        Maximum virtual heights allowed in each ionospheric layer.
        (default={"D":115.0,"E":150.0,"F":900.0})
    region_hmin : (dict)
        Minimum virtual heights allowed in each ionospheric layer.
        (default={"D":75.0,"E":115.0,"F":150.0})
    rg_box : (list of int)
        The total number of range gates to include when examining the elevation
        angle across all beams. (default=[2,5,10,20])
    vh_box : (list of float)
        The total width of the altitude box to consider when examining the
        elevation angle across all beams at a given range gate.
        (default=[50.0,50.0,50.0,150.0])
    max_rg : (list)
        Maximum range gate to use each range gate and virtual height at
        (default=[5,25,40,76])
    max_hop : (float)
        Maximum hop that the corresponding rg_box and vh_box values applies
        to.  (default=3.0)
    ut_box : (class dt.timedelta)
        Total width of universal time box to examine for backscatter FoV
        continuity. (default=20.0 minutes)
    tdiff : (function or NoneType)
        A function to retrieve tdiff values (in microsec) using the radar ID
        number current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_args.  Example:
        def get_tdiff(stid, time, tfreq, filename) { do things } return tdiff
        tdiff=get_tdiff, tdiff_args=["tdiff_file"]
        (default=None)
    tdiff_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff function.
        (default=list())
    tdiff_e : function or NoneType)
        A function to retrieve tdiff error values (in microsec) using the radar
        ID number, current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_e_args.  Example:
        def get_tdiffe(stud, time, tfreq, filename) { do things } return tdiffe
        tdiff_e=get_tdiffe, tdiff_e_args=["tdiff_file"]
        (default=None)
    tdiff_e_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff_e function.
        (default=list())
    ptest : (boolian)
        Test to see if a propagation path is realistic (default=True)
    step : (int)
        Level of processing to perform (1-6).  6 performs all steps. (default=6)
    strict_gs : (boolian)
        Remove indeterminately flagged backscatter (default=True)
    label_type : (str)
        Type of hop label to use (frac/decimal) (default="frac")
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots.  Will create this data
        if it is not provided (default=dict())

    Returns
    ---------
    xtime : (dict)
    yrange : (dict)
    zdata : (dict)
    zi : (dict)
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots
    """
    import davitpy.pydarn.sdio as sdio

    # Define local routines
    def range_gate_limits(rg_limits, rg):
        for lim in rg_limits:
            if rg >= lim[0] and rg < lim[1]:
                return True
        return False

    # Initialize the data dictionaries
    xtime = dict()
    yrange = dict()
    zdata = {k:dict() for k in set([intensity_all, intensity_sep])}
    zi = {"all":dict(), 1:dict(), 0:dict(), -1:dict()}

    # For each radar, load and process the desired data
    for rad in rad_bms.keys():
        if not beams.has_key(rad):
            # Load data for one radar, padding data based on the largest
            # temporal boxcar window used in the FoV processing
            rad_ptr = sdio.radDataRead.radDataOpen(stime-ut_box, rad,
                                                   eTime=etime+ut_box,
                                                   cp=rad_cp[rad],
                                                   fileType=file_type,
                                                   password=password)
            if fix_gs.has_key(rad):
                read_ptr = list()
                i = 0
                bm, i = ub.get_beam(rad_ptr, i)

                while bm is not None:
                    if(hasattr(bm, "fit") and hasattr(bm.fit, "gflg") and
                       bm.fit.gflg is not None):
                        bm.fit.gflg = [0 if range_gate_limits(fix_gs[rad],
                                                              bm.fit.slist[j])
                                       else gg for j,gg in
                                       enumerate(bm.fit.gflg)]
                    read_ptr.append(bm)
                    bm, i = ub.get_beam(rad_ptr, i)
            else:
                read_ptr = rad_ptr

            # Process the beams for this radar
            beams[rad] = ub.update_backscatter(read_ptr, min_pnts=min_pnts,
                                               region_hmax=region_hmax,
                                               region_hmin=region_hmin,
                                               rg_box=rg_box, vh_box=vh_box,
                                               max_rg=max_rg, max_hop=max_hop,
                                               ut_box=ut_box, tdiff=tdiff,
                                               tdiff_args=tdiff_args,
                                               tdiff_e=tdiff_e,
                                               tdiff_e_args=tdiff_e_args,
                                               ptest=ptest, strict_gs=strict_gs,
                                               logfile=logfile,
                                               log_level=log_level, step=step)

        # Load the data for this beam and radar
        xtime[rad] = list()
        yrange[rad] = list()
        idat = dict()
        for k in zdata.keys():
            zdata[k][rad] = list()
            idat[k] = list()
        for ff in zi.keys():
            zi[ff][rad] = {hh:list() for hh in mm[marker_key].keys()}

        if len(beams[rad][rad_bms[rad]]) > 0:
            j = 0
            for bm in beams[rad][rad_bms[rad]]:
                if(hasattr(bm, "fit") and hasattr(bm.fit, intensity_all)
                   and (hasattr(bm.fit, intensity_sep))):
                    for k in idat.keys():
                        idat[k] = getattr(bm.fit, k)

                    if hasattr(bm.fit, marker_key):
                        ikey = getattr(bm.fit, marker_key)
                    else:
                        ireg = getattr(bm.fit, "region")
                        ikey = ["{:.1f}{:s}".format(hh, ireg[ii])
                                if not np.isnan(hh) and len(ireg[ii]) == 1
                                else ""
                                for ii,hh in enumerate(getattr(bm.fit, "hop"))]
             
                    for i,s in enumerate(bm.fit.slist):
                        if(not np.isnan(bm.fit.hop[i]) and
                           len(bm.fit.region[i]) == 1 and
                           (not strict_gs or
                            (strict_gs and bm.fit.gflg[i] >= 0))):
                            xtime[rad].append(bm.time)
                            yrange[rad].append(s)
                            for k in idat.keys():
                                zdata[k][rad].append(idat[k][i])

                            zi[bm.fit.fovflg[i]][rad][ikey[i]].append(j)
                            zi["all"][rad][ikey[i]].append(j)
                            zi[bm.fit.fovflg[i]][rad]["all"].append(j)
                            zi["all"][rad]["all"].append(j)
                            j += 1

    return(xtime, yrange, zdata, zi, beams)

#------------------------------------------------------------------------
def plot_scan_and_beam(scan, beam, fattr="felv", rattr="belv", fhop_attr="fhop",
                       bhop_attr="bhop", fov_attr="fovflg",
                       contour_color=clinear, mcolor="k", bmin=0, bmax=15,
                       tmin=None, tmax=None, ymin=0, ymax=75, zmin=None,
                       zmax=None, bfmt=None, tlabel="Universal Time (HH:MM)",
                       tfmt=mdates.DateFormatter("%H:%M"), yfmt=None,
                       binc=ticker.MultipleLocator(3),
                       tinc=mdates.MinuteLocator(interval=15),
                       yinc=ticker.MultipleLocator(15), zinc=6, plot_title="",
                       label_type="frac", acolor="w", make_plot=True,
                       draw=True):
    """Plot a specified attribute (elevation angle or virtual height) for the
    front and rear field-of-view, using a scan of beams and a single beam for
    a longer period of time.

    Parameters
    -----------
    scan : (list of beams)
        List of beam class objects denoting one scan across all beams
    beam : (list of beams)
        List of beam class objects denoting one beam for a period of time
    fattr : (str)
        Front field-of-view fit attribute (default="felv")
    rattr : (str)
        Rear field-of-view fit attribute (default="belv")
    fhop_attr : (str)
        Front field-of-view fit attribute containing hop (default="fhop")
    rhop_attr : (str)
        Rear field-of-view fit attribute containing hop (default="bhop")
    fov_attr : (str)
        Beam fit attribute containing the field-of-view flag (default="fovflg")
    contour_color : (str)
        Contour colormap (default="Spectral_r")
    mcolor : (str)
        Marker color (default="k")
    bmin : (float or int)
        Minimum beam number to plot (default=0)
    bmax : (float or int)
        Maximum beam number to plot (default=15)
    tmin : (datetime or NoneType)
        Minimum time to plot (default=None)
    tmax : (datetime or NoneType)
        Maximum time to plot (default=None)
    ymin : (float or int)
        Minimum range gate to plot (default=0)
    ymax : (float or int)
        Maximum range gate to plot (default=75)
    zmin : (float or int)
        Minimum z value to plot (default=None)
    zmax : (float or int)
        Maximum z value to plot (default=None)
    bfmt : (str or NoneType)
        Beam axis format (default=None)
    tlabel : (str)
        Time axis label (default="Universal Time (HH:MM)")
    tfmt : (class)
        Time axis format (default=mdates.DateFormatter("%H:%M"))
    yfmt : (class or NoneType)
        Range gate axis format (default=None)
    binc : (class)
        Beam axis multiple locator (default=ticker.MultipleLocator(3))
    tinc : (class)
        Time axis multiple locator (default=mdates.MinuteLocator(interval=15))
    yinc : (class)
        Range gate axis multiple locator
        (default=ticker.MultipleLocator(15))
    zinc : (float or int)
        Z data colorbar incriment (default=6)
    plot_title : (str)
        Plot title (default="")
    label_type : (str)
        Type of hop label to use (frac/decimal) (default="frac")
    acolor : (str or tuple)
        Background color for subplots (default="0.9" - light grey)
    make_plot : (boolian)
        Make plot (True) or just process data (False) (default=True)
    draw : (boolian)
        Output figure to display? (default=True)

    Returns
    ---------
    f : (pointer)
        Figure handle
    ax : (list)
        List of axis handles
    cb : (set)
        Output from colorbar
    """
    import davitpy.pydarn.radar as pyrad

    mkey = fhop_attr if mm.has_key(fhop_attr) else fhop_attr[1:]
    xpos = {7:1.1, 6:0.49, 5:0.35, 4:0.8, 3:0.7, 2:0.5, 1:0.0}

    # Extract the scan data
    scan_times = list()
    xbeam = list()
    brange = list()
    fbeam = list()
    rbeam = list()
    bhop = {ff:{hh:list() for hh in mc[mkey].keys()} for ff in [1,0,-1]}
    bfov = {ff:{hh:list() for hh in mm[mkey].keys()} for ff in [1,0,-1]}
    j = 0

    for bm in scan:
        scan_times.append(bm.time)
        if(hasattr(bm, "fit") and hasattr(bm.fit, fattr)
           and hasattr(bm.fit, rattr) and hasattr(bm.fit, fov_attr)
           and (hasattr(bm.fit, fhop_attr) or fhop_attr.find("reg") >= 0)
           and (hasattr(bm.fit, bhop_attr) or bhop_attr.find("reg") >= 0)
           and hasattr(bm.fit, "region")):
            fd = getattr(bm.fit, fattr)
            rd = getattr(bm.fit, rattr)
            ff = getattr(bm.fit, fov_attr)
            hh = dict()
            if fhop_attr == "freg":
                temp = getattr(bm.fit, "fhop")
                hh[1] = ["{:.1f}{:s}".format(temp[i],rr)
                         if not np.isnan(temp[i]) and len(rr) == 1 else ""
                         for i,rr in enumerate(getattr(bm.fit, "fregion"))]
            else:
                hh[1] = getattr(bm.fit, fhop_attr)

            if bhop_attr == "breg":
                temp = getattr(bm.fit, "bhop")
                hh[-1] = ["{:.1f}{:s}".format(temp[i],rr)
                          if not np.isnan(temp[i]) and len(rr) == 1 else ""
                          for i,rr in enumerate(getattr(bm.fit, "bregion"))]
            else:
                hh[-1] = getattr(bm.fit, bhop_attr)

            for i,s in enumerate(bm.fit.slist):
                fi = ff[i] if abs(ff[i]) == 1 else (1 if not np.isnan(fd[i])
                                                    else -1)
                fe = fd[i] if fi == 1 else rd[i]
                if not np.isnan(fe) and bhop[fi].has_key(hh[fi][i]):
                    xbeam.append(bm.bmnum)
                    brange.append(s)
                    fbeam.append(fd[i])
                    rbeam.append(rd[i])
                    bfov[ff[i]][hh[fi][i]].append(j)
                    bfov[ff[i]]['all'].append(j)
                    bhop[fi][hh[fi][i]].append(j)
                    if bhop[fi].has_key(hh[-fi][i]):
                        bhop[-fi][hh[-fi][i]].append(j)
                    j += 1

    xbeam = np.array(xbeam)
    brange = np.array(brange)
    fbeam = np.array(fbeam)
    rbeam = np.array(rbeam)

    # Extract the beam data
    bmnum = beam[0].bmnum
    xtime=list()
    trange=list()
    ftime=list()
    rtime=list()
    thop={ff:{hh:list() for hh in mc[mkey].keys()} for ff in [1,0,-1]}
    tfov={ff:{hh:list() for hh in mm[mkey].keys()} for ff in [1,0,-1]}
    j = 0

    for bm in beam:
        if(hasattr(bm.fit, fattr) and hasattr(bm.fit, rattr)
           and (hasattr(bm.fit, fhop_attr) or fhop_attr.find("reg") >= 0)
           and (hasattr(bm.fit, bhop_attr) or bhop_attr.find("reg") >= 0)
           and hasattr(bm.fit, fov_attr) and hasattr(bm.fit, "region")):
            fd = getattr(bm.fit, fattr)
            rd = getattr(bm.fit, rattr)
            ff = getattr(bm.fit, fov_attr)
            hh = dict()
            if fhop_attr == "freg":
                temp = getattr(bm.fit, "fhop")
                hh[1] = ["{:.1f}{:s}".format(temp[i],rr)
                         if not np.isnan(temp[i]) and len(rr) == 1 else ""
                         for i,rr in enumerate(getattr(bm.fit, "fregion"))]
            else:
                hh[1] = getattr(bm.fit, fhop_attr)

            if bhop_attr == "breg":
                temp = getattr(bm.fit, "bhop")
                hh[-1] = ["{:.1f}{:s}".format(temp[i],rr)
                          if not np.isnan(temp[i]) and len(rr) == 1 else ""
                          for i,rr in enumerate(getattr(bm.fit, "bregion"))]
            else:
                hh[-1] = getattr(bm.fit, bhop_attr)

            for i,s in enumerate(bm.fit.slist):
                fi = ff[i] if abs(ff[i]) == 1 else (1 if not np.isnan(fd[i])
                                                    else -1)
                fe = fd[i] if fi == 1 else rd[i]

                if not np.isnan(fe) and thop[fi].has_key(hh[fi][i]):
                    xtime.append(bm.time)
                    trange.append(s)
                    ftime.append(fd[i])
                    rtime.append(rd[i])
                    tfov[ff[i]][hh[fi][i]].append(j)
                    tfov[ff[i]]['all'].append(j)
                    thop[fi][hh[fi][i]].append(j)
                    if thop[-fi].has_key(hh[-fi][i]):
                        thop[-fi][hh[-fi][i]].append(j)
                    j += 1
    xtime = np.array(xtime)
    trange = np.array(trange)
    ftime = np.array(ftime)
    rtime = np.array(rtime)

    if not make_plot:
        return({1:[xbeam[bfov[1]['all']], xtime[tfov[1]['all']]],
                -1:[xbeam[bfov[-1]['all']], xtime[tfov[-1]['all']]]},
               {1:[brange[bfov[1]['all']], trange[tfov[1]['all']]],
                -1:[brange[bfov[-1]['all']], trange[tfov[-1]['all']]]},
               {1:[fbeam[bfov[1]['all']], ftime[tfov[1]['all']]],
                -1:[rbeam[bfov[-1]['all']], rtime[tfov[-1]['all']]]})

    # Initialize the figure
    f = plt.figure(figsize=(12,8))
    gb = gridspec.GridSpec(1, 2)
    gb.update(left=0.075, wspace=0.05, right=0.48, top=.85)
    gt = gridspec.GridSpec(2, 1)
    gt.update(left=0.55, hspace=0.075, right=0.91, top=.85)

    # Initialize the subplots
    fbax = plt.subplot(gb[:,0])
    rbax = plt.subplot(gb[:,1])
    ftax = plt.subplot(gt[0,:])
    rtax = plt.subplot(gt[1,:])

    # Set the plot background color
    fbax.set_axis_bgcolor(acolor)
    rbax.set_axis_bgcolor(acolor)
    ftax.set_axis_bgcolor(acolor)
    rtax.set_axis_bgcolor(acolor)

    if zmin is None:
        zmin = min(np.nanmin(ftime), np.nanmin(rtime), np.nanmin(fbeam),
                   np.nanmin(rbeam))

    if zmax is None:
        zmax = min(np.nanmax(ftime), np.nanmax(rtime), np.nanmax(fbeam),
                   np.nanmax(rbeam))

    if len(xtime) > 0:
        if tmin is None:
            tmin = mdates.date2num(min(xtime))

        if tmax is None:
            tmax = mdates.date2num(max(xtime))

    # Plot the contours and markers
    for hh in mc[mkey].keys():
        if len(bhop[1][hh]) > 0:
            # Scans
            con = fbax.scatter(xbeam[bhop[1][hh]], brange[bhop[1][hh]],
                               c=fbeam[bhop[1][hh]], vmin=zmin, vmax=zmax,
                               cmap=cm.get_cmap(contour_color), s=80,
                               edgecolor="face", marker=mm[mkey][hh])
            fbax.plot(xbeam[bfov[1][hh]], brange[bfov[1][hh]], mm[mkey][hh],
                      ms=8, markerfacecolor="none", markeredgecolor=mcolor)
        if len(bhop[-1][hh]) > 0:
            con = rbax.scatter(xbeam[bhop[-1][hh]], brange[bhop[-1][hh]],
                               c=rbeam[bhop[-1][hh]], vmin=zmin, vmax=zmax,
                               cmap=cm.get_cmap(contour_color), s=80,
                               edgecolor="face", marker=mm[mkey][hh])
            rbax.plot(xbeam[bfov[-1][hh]], brange[bfov[-1][hh]], mm[mkey][hh],
                      ms=8, markerfacecolor="none", markeredgecolor=mcolor)
        if len(thop[1][hh]) > 0:
            # Beams
            try:
                label = "{:.1f}".format(hh)
            except:
                label = "{:}".format(hh)

            con = ftax.scatter(xtime[thop[1][hh]], trange[thop[1][hh]],
                               c=ftime[thop[1][hh]], vmin=zmin, vmax=zmax,
                               cmap=cm.get_cmap(contour_color), s=80,
                               edgecolor="face", marker=mm[mkey][hh],
                               label=label)
            ftax.plot(xtime[tfov[1][hh]], trange[tfov[1][hh]], mm[mkey][hh],
                      ms=8, markerfacecolor="none", markeredgecolor=mcolor)
        if len(thop[-1][hh]) > 0:
            # Beams
            try:
                label = "{:.1f}".format(hh)
            except:
                label = "{:}".format(hh)

            con = rtax.scatter(xtime[thop[-1][hh]], trange[thop[-1][hh]],
                               c=rtime[thop[-1][hh]], vmin=zmin, vmax=zmax,
                               cmap=cm.get_cmap(contour_color), s=80,
                               edgecolor="face", marker=mm[mkey][hh])
            rtax.plot(xtime[tfov[-1][hh]], trange[tfov[-1][hh]], mm[mkey][hh],
                      ms=8, markerfacecolor="none", markeredgecolor=mcolor)

    # Add lines indicating the beam plotted versus time in the scans
    fbax.plot([bmnum-.5, bmnum-.5], [ymin-1, ymax+1], "k--")
    rbax.plot([bmnum-.5, bmnum-.5], [ymin-1, ymax+1], "k--")
    fbax.plot([bmnum+.5, bmnum+.5], [ymin-1, ymax+1], "k--")
    rbax.plot([bmnum+.5, bmnum+.5], [ymin-1, ymax+1], "k--")

    # Add lines indicating the time plotted in the beam vs time plots
    stime = min(scan_times)
    etime = max(scan_times)
    ftax.plot([stime, stime], [ymin-1, ymax+1], "k--")
    ftax.plot([etime, etime], [ymin-1, ymax+1], "k--")
    rtax.plot([stime, stime], [ymin-1, ymax+1], "k--")
    rtax.plot([etime, etime], [ymin-1, ymax+1], "k--")

    # Add legend
    handles, labels = get_sorted_legend_labels(ftax, mkey)
    hl, ll = get_sorted_legend_labels(rtax, mkey)

    for il,label in enumerate(ll):
        try:
            labels.index(label)
        except:
            # This label is not currently available, add it
            lind = morder[mkey][label]
            jl = 0
            while lind > morder[mkey][labels[jl]]:
                jl += 1

            labels.insert(jl, label)
            handles.insert(jl, hl[il])

    if label_type.find("frac") >= 0:
        flabels = get_fractional_hop_labels(labels)
    else:
        flabels = labels

    ftax.legend(handles, flabels, fontsize="medium", scatterpoints=1,
                ncol=len(flabels), title="Hop", labelspacing=.1,
                columnspacing=0, markerscale=1, borderpad=0.3, handletextpad=0,
                bbox_to_anchor=(xpos[len(flabels)],1.4))

    # Add colorbar
    label = pyrad.radUtils.getParamDict(fattr)['label']
    unit = pyrad.radUtils.getParamDict(fattr)['unit']
    cb = add_colorbar(f, con, zmin, zmax, zinc, label, unit,
                      loc=[.92,.1,.01,.75])

    # Add a global title, if desired
    if len(plot_title) > 0:
        f.suptitle(plot_title)

    # For subplot, adjust the axis and labels
    fbax.set_title("Front", fontsize="medium")
    fbax.set_ylabel("Range Gate")
    fbax.set_ylim(ymin-.5, ymax+.5)
    fbax.set_xlim(bmin-.5, bmax+.5)
    fbax.text(6.0, -6, "Beams at {:}".format(stime))
    rbax.set_title("Rear", fontsize="medium")
    rbax.set_ylim(ymin-.5, ymax+.5)
    rbax.set_xlim(bmin-.5, bmax+.5)
    rbax.yaxis.set_major_formatter(ticker.FormatStrFormatter(""))

    ftax.set_title("Beam {:d}".format(bmnum), fontsize="medium")
    ftax.set_ylabel("Front Range Gate")
    ftax.set_ylim(ymin-.5, ymax+.5)
    ftax.xaxis.set_major_formatter(ticker.FormatStrFormatter(""))

    rtax.set_ylabel("Rear Range Gate")
    rtax.set_xlabel(tlabel)
    rtax.set_ylim(ymin-.5, ymax+.5)

    if tmin is not None and tmax is not None:
        ftax.set_xlim(tmin, tmax)
        rtax.set_xlim(tmin, tmax)

    # Set the tick formats and locations
    if bfmt is not None:
        fbax.xaxis.set_major_formatter(bfmt)
        rbax.xaxis.set_major_formatter(bfmt)

    if tfmt is not None:
        rtax.xaxis.set_major_formatter(tfmt)

    if yfmt is not None:
        fbax.yaxis.set_major_formatter(yfmt)
        ftax.yaxis.set_major_formatter(yfmt)
        rtax.yaxis.set_major_formatter(yfmt)

    if binc is not None:
        fbax.xaxis.set_major_locator(binc)
        rbax.xaxis.set_major_locator(binc)

    if tinc is not None:
        ftax.xaxis.set_major_locator(tinc)
        rtax.xaxis.set_major_locator(tinc)

    if yinc is not None:
        fbax.yaxis.set_major_locator(yinc)
        rbax.yaxis.set_major_locator(yinc)
        ftax.yaxis.set_major_locator(yinc)
        rtax.yaxis.set_major_locator(yinc)

    if draw:
        # Draw to screen.
        if plt.isinteractive():
            plt.draw() #In interactive mode, you just "draw".
        else:
            # W/o interactive mode, "show" stops the user from typing more 
            # at the terminal until plots are drawn.
            plt.show()

    return f, [fbax, rbax, ftax, rtax], cb

#-------------------------------------------------------------------------
def plot_meteor_figure(fcolor="b", rcolor="m", stime=dt.datetime(2001,12,14),
                       etime=dt.datetime(2001,12,28), rad="sas", radar_ns=-1.0,
                       fbmnum=0, rbmnum=15, cp=150, malt=102.7, figname=None,
                       password=True, file_type="fitacf", logfile=None,
                       log_level=logging.WARN, min_pnts=3,
                       region_hmax={"D":115.0,"E":150.0,"F":900.0},
                       region_hmin={"D":75.0,"E":115.0,"F":150.0},
                       rg_box=[2,5,10,20], vh_box=[50.0,50.0,50.0,150.0],
                       max_rg=[5,25,40,76], max_hop=3.0,
                       ut_box=dt.timedelta(minutes=20.0), tdiff=None,
                       tdiff_args=list(), tdiff_e=None, tdiff_e_args=list(),
                       ptest=True, step=6, strict_gs=True, draw=True,
                       beams=dict()):
    """Plot comparing HWM14 neutral winds with the line-of-site velocity
    for two beams at Saskatoon

    Parameters
    -----------
    fcolor : (str)
        Front field-of-view color (default="b")
    rcolor : (str)
        Rear field-of-view color (default="m")
    stime : (dt.datetime)
        Starting time for finding meteor data (default=dt.datetime(2001,12,14))
    etime : (dt.datetime)
        Ending time for finding meteor data (default=dt.datetime(2001,12,28))
    rad : (str)
        radar code (default="sas")
    radar_ns : (float)
        Sign denoting whether or not the front field-of-view line-of-sight
        velocity is positive to the North (positive) or not (negative)
        (default=-1.0)
    fbmnum : (int)
        Front field-of-view beam number (default=0)
    rbmnum : (int)
        Rear field-of-view beam number (default=15)
    cp : (int)
        Radar programming code number. (default=150)
    malt : (float)
        Meteor altitude to use for map (default=102.7)
    figname : (str or NoneType)
        Figure name or None if no figure is to be saved (default=None)
    password : (boolian or str)
        When downloading data from your specified SuperDARN mirror site, a
        password may be needed.  It may be included here or, if True is used,
        a prompt will appear for you to enter it securely.  (default=True)
    file_type : (str)
        Type of data file to download (default="fitacf")
    logfile : (str or NoneType)
        Name of file to hold the log output or None for stdout. (default=None)
    log_level : (int)
        Level of output to report.  Flag values explained in logging module.
        (default=logging.WARNING)
    min_pnts : (int)
        The minimum number of points necessary to perform certain range gate
        or beam specific evaluations. (default=3)
    region_hmax : (dict)
        Maximum virtual heights allowed in each ionospheric layer.
        (default={"D":125.0,"E":200.0,"F":900.0})
    region_hmin : (dict)
        Minimum virtual heights allowed in each ionospheric layer.
        (default={"D":75.0,"E":125.0,"F":200.0})
    rg_box : (list of int)
        The total number of range gates to include when examining the elevation
        angle across all beams. (default=[2,5,10,20])
    vh_box : (list of float)
        The total width of the altitude box to consider when examining the
        elevation angle across all beams at a given range gate.
        (default=[50.0,50.0,50.0,150.0])
    max_rg : (list)
        The maximum range gates to apply the range gate and virtual height
        boxes (default=[5,25,40,76])
    max_hop : (float)
        Maximum hop that the corresponding rg_box and vh_box values applies
        to.  (default=3.0)
    ut_box : (class dt.timedelta)
        Total width of universal time box to examine for backscatter FoV
        continuity. (default=20.0 minutes)
    tdiff : (function or NoneType)
        A function to retrieve tdiff values (in microsec) using the radar ID
        number current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_args.  Example:
        def get_tdiff(stid, time, tfreq, filename) { do things } return tdiff
        tdiff=get_tdiff, tdiff_args=["tdiff_file"]
        (default=None)
    tdiff_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff function.
        (default=list())
    tdiff_e : function or NoneType)
        A function to retrieve tdiff error values (in microsec) using the radar
        ID number, current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_e_args.  Example:
        def get_tdiffe(stud, time, tfreq, filename) { do things } return tdiffe
        tdiff_e=get_tdiffe, tdiff_e_args=["tdiff_file"]
        (default=None)
    tdiff_e_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff_e function.
        (default=list())
    ptest : (boolian)
        Test to see if a propagation path is realistic (default=True)
    step : (int)
        Level of processing to perform (1-6).  6 performs all steps. (default=6)
    strict_gs : (bool)
        Use indeterminately flagged backscatter (default=True)
    draw : (boolian)
        Output figure to display? (default=True)
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots.  Will create this data
        if it is not provided (default=dict())

    Returns
    ---------
    f : (pointer)
        Figure handle
    ax : (dict)
        Dictionary of axis handles
    cb : (dict)
        Dictionary of colorbar handles
    beams : (dict)
        Dictionary with radar codes as keys for the dictionaries containing
        beams with the data used to create the plots
    """
    import davitpy.pydarn.plotting as plotting
    import davitpy.pydarn.radar as pyrad
    import davitpy.pydarn.sdio as sdio
    import davitpy.models.hwm as hwm

    #-------------------------------------------------------------------------
    # Define local routines
    def ismeteor(p, verr, werr):
        """Gareth's threshold test for meteor scatter (Chisham and Freeman 2013)

        Parameters
        ----------
        p : (float)
            Power
        verr : (float)
            Doppler velocity error
        werr : (float)
            Spectral width error

        Returns
        --------
        good : (bool)
            True if fits characteristics for meteor, else false
        """
        # Initialize output
        good = False

        # Set constants for exponential function that defines the upper limit of
        # velocity and spectral width error at a given power
        va = 10.0
        vb = -np.log(50.0) / 50.0
        wa = 40.0
        wb = -np.log(40.0 / .2) / 50.0

        # Only test the values if the power and error values are set
        if(not np.isnan(p) and p >= 0.0 and not np.isnan(verr)
           and verr >= 0.0 and not np.isnan(werr) and werr >= 0.0):
            # Calculate the upper limits of the error
            vtest = va * np.exp(vb * p)
            wtest = wa * np.exp(wb * p)

            # Test the calculated errors
            if verr <= vtest and werr <= wtest:
                good = True

        return good

    def dec2001ap(bm_time):
        """Look up Ap using time.  Only available for December 2001.
        Data from: ftp://ftp.ngdc.noaa.gov/STP/GEOMAGNETIC_DATA/INDICES/KP_AP/

        Parameters
        -----------
        bm_time : (datetime)
            Time to find Ap

        Returns
        ---------
        bm_ap : (float)
        """
        ap_times = [dt.datetime(2001,12,1) + dt.timedelta(hours=i)
                    for i in range(744)]
        ap_vals = [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0,
                   3.0, 3.0, 3.0, 3.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0,
                   4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0,
                   2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 6.0, 6.0, 6.0, 6.0,
                   6.0, 6.0, 6.0, 6.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0,
                   15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 9.0, 9.0,
                   9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0,
                   6.0, 6.0, 27.0, 27.0, 27.0, 27.0, 27.0, 27.0, 27.0, 27.0,
                   12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 5.0, 5.0,
                   5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 15.0, 15.0, 15.0, 15.0, 15.0,
                   15.0, 15.0, 15.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0,
                   7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 9.0, 9.0, 9.0, 9.0,
                   9.0, 9.0, 9.0, 9.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                   3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 18.0, 18.0, 18.0,
                   18.0, 18.0, 18.0, 18.0, 18.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                   5.0, 5.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 2.0, 2.0,
                   2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0,
                   3.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0,
                   2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0,
                   2.0, 2.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 3.0, 3.0,
                   3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0,
                   4.0, 4.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 7.0, 7.0,
                   7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0,
                   9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 7.0, 7.0,
                   7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0,
                   6.0, 6.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0,
                   3.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.0, 9.0,
                   9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 15.0, 15.0, 15.0, 15.0, 15.0,
                   15.0, 15.0, 15.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0,
                   12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 18.0, 18.0,
                   18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0,
                   18.0, 18.0, 18.0, 18.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0,
                   12.0, 12.0, 22.0, 22.0, 22.0, 22.0, 22.0, 22.0, 22.0, 22.0,
                   15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 22.0, 22.0,
                   22.0, 22.0, 22.0, 22.0, 22.0, 22.0, 7.0, 7.0, 7.0, 7.0, 7.0,
                   7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 15.0,
                   15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 9.0, 9.0, 9.0, 9.0,
                   9.0, 9.0, 9.0, 9.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0,
                   4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0,
                   2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 7.0, 7.0, 7.0, 7.0,
                   7.0, 7.0, 7.0, 7.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0,
                   15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0,
                   15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 9.0, 9.0, 9.0, 9.0, 9.0,
                   9.0, 9.0, 9.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 7.0,
                   7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                   5.0, 5.0, 5.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 18.0,
                   18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 39.0, 39.0, 39.0,
                   39.0, 39.0, 39.0, 39.0, 39.0, 12.0, 12.0, 12.0, 12.0, 12.0,
                   12.0, 12.0, 12.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0,
                   6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 9.0, 9.0, 9.0, 9.0,
                   9.0, 9.0, 9.0, 9.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0,
                   3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 9.0, 9.0, 9.0, 9.0,
                   9.0, 9.0, 9.0, 9.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0,
                   4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 3.0, 3.0, 3.0, 3.0,
                   3.0, 3.0, 3.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0,
                   6.0, 6.0, 6.0, 6.0, 27.0, 27.0, 27.0, 27.0, 27.0, 27.0, 27.0,
                   27.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 18.0, 18.0,
                   18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 39.0, 39.0, 39.0, 39.0,
                   39.0, 39.0, 39.0, 39.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0,
                   18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0,
                   18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 7.0, 7.0,
                   7.0, 7.0, 7.0, 7.0, 7.0, 7.0]

        # Indices apply to the entire hour.  To avoid rounding by minutes,
        # recast requested time without minutes, seconds, or microseconds
        htime = dt.datetime(bm_time.year, bm_time.month, bm_time.day,
                            bm_time.hour)
        tdelta = np.array([abs((t-htime).total_seconds()) for t in ap_times])
        bm_ap = ap_vals[tdelta.argmin()]

        return bm_ap

    # End local routines
    #-------------------------------------------------------------------------
    # Load and process the desired data
    if not beams.has_key(fbmnum) or not beams.has_key(rbmnum):
        # Load the SuperDARN data, padding data based on the largest
        # temporal boxcar window used in the FoV processing
        rad_ptr = sdio.radDataRead.radDataOpen(stime-ut_box, rad,
                                               eTime=etime+ut_box, cp=cp,
                                               fileType=file_type,
                                               password=password)
        beams = ub.update_backscatter(rad_ptr, min_pnts=min_pnts,
                                      region_hmax=region_hmax,
                                      region_hmin=region_hmin, rg_box=rg_box,
                                      vh_box=vh_box, max_rg=max_rg,
                                      max_hop=max_hop, ut_box=ut_box,
                                      tdiff=tdiff, tdiff_args=tdiff_args,
                                      tdiff_e=tdiff_e,
                                      tdiff_e_args=tdiff_e_args, ptest=ptest,
                                      logfile=logfile, log_level=log_level,
                                      step=step)

    if not beams.has_key(fbmnum) or not beams.has_key(rbmnum):
        return(None, None, None, beams)

    if len(beams[fbmnum]) == 0 or len(beams[rbmnum]) == 0:
        return(None, None, None, beams)

    # Load the radar location data
    hard = pyrad.site(code=rad, dt=stime)
    fovs = {1:pyrad.radFov.fov(site=hard, ngates=5, altitude=malt, coords="geo",
                               fov_dir="front"),
            -1:pyrad.radFov.fov(site=hard, ngates=5, altitude=malt,
                                coords="geo", fov_dir="back")}

    # Select the meteor data
    bmnum = {1:fbmnum, -1:rbmnum}
    yspeed = {fbmnum:list(), rbmnum:list(), "reject":list()} # FoV speeds
    hspeed = {fbmnum:list(), rbmnum:list(), "reject":list()} # HWM speeds

    for ff in bmnum.keys():
        for bm in beams[bmnum[ff]]:
            for i,ifov in enumerate(bm.fit.fovflg):
                if bm.fit.slist[i] >= 5:
                    break

                if((ifov == ff or ifov == 0) and bm.fit.hop[i] == 0.5 and
                   bm.fit.vheight[i] < 125.0 and len(bm.fit.region[i]) == 1):
                    # Test to see if this is meteor backscatter using the
                    # rules outlined by Chisham and Freeman
                    if ismeteor(bm.fit.p_l[i], bm.fit.v_e[i], bm.fit.w_l_e[i]):
                        skey = None
                        if ifov == ff:
                            skey = bmnum[ff]
                            yspeed[skey].append(ff*bm.fit.v[i]*radar_ns)
                            glat = fovs[ff].latCenter[bmnum[ff],bm.fit.slist[i]]
                            glon = fovs[ff].lonCenter[bmnum[ff],bm.fit.slist[i]]
                            alt = bm.fit.vheight[i]
                        elif ff == 1:
                            skey = "reject"
                            yspeed[skey].append(bm.fit.v[i]*radar_ns)
                            glat = fovs[1].latCenter[bmnum[1],bm.fit.slist[i]]
                            glon = fovs[1].lonCenter[bmnum[1],bm.fit.slist[i]]
                            alt = bm.fit.fvheight[i]

                        if skey is not None:
                            ap = dec2001ap(bm.time)
                            ihwm = hwm.hwm_input.format_hwm_input(bm.time, alt,
                                                                  glat, glon,
                                                                  ap)
                            try:
                                winds = hwm.hwm14.hwm14(*ihwm)
                            except:
                                # The first call to hwm14 creates the module,
                                # but it works just the same as calling the
                                # module
                                winds = hwm.hwm14(*ihwm)
                            hspeed[skey].append(winds[0])

    # Recast the data as numpy arrays
    for skey in yspeed.keys():
        yspeed[skey] = np.array(yspeed[skey])
        hspeed[skey] = np.array(hspeed[skey])

    # Initialize the figure
    f = plt.figure(figsize=(12,8))
    f.suptitle("{:} to {:}".format(stime.date(), etime.date()))

    # Add a map with the field-of-view and beams highlighted
    ax = f.add_subplot(1,2,1)
    urlat = np.ceil(fovs[1].latFull.max())
    urlon = np.ceil(max(fovs[1].lonFull.max(), fovs[-1].lonFull.max()))
    lllat = np.floor(fovs[-1].latFull.min()) - 1.0
    lllon = np.ceil(min(fovs[1].lonFull.min(), fovs[-1].lonFull.min())) - 1.0

    m = basemap.Basemap(ax=ax, projection="stere", lon_0=hard.geolon,
                        lat_0=hard.geolat, llcrnrlon=lllon, llcrnrlat=lllat,
                        urcrnrlon=urlon, urcrnrlat=urlat, resolution="l")
    
    m.drawcoastlines(linewidth=0.5, color="0.6")
    m.fillcontinents(color="0.6", alpha=.1)
    m.drawmeridians(np.arange(min(lllon, urlon), max(lllon, urlon), 2.0),
                    labels=[0,0,0,1])
    m.drawparallels(np.arange(lllat, urlat+1.0, 2.0), labels=[1,0,0,0])

    # Add the field-of-view boundaries
    plotting.mapOverlay.overlayFov(m, codes=rad, dateTime=stime, beams=[fbmnum],
                                   beamsColors=[fcolor], fovObj=fovs[1])
    plotting.mapOverlay.overlayFov(m, codes=rad, dateTime=stime, beams=[rbmnum],
                                   beamsColors=[rcolor], fovObj=fovs[-1])

    # Add the radar location and name
    plotting.mapOverlay.overlayRadar(m, codes=rad, dateTime=stime,
                                     annotate=True, fontSize=16)

    # Add the velocity difference histograms
    diff_range = (-200.0, 200.0)
    diff_inc = int((diff_range[1] - diff_range[0]) / 5.0)
    fax = f.add_subplot(3,2,2)
    rax = f.add_subplot(3,2,4)
    nax = f.add_subplot(3,2,6)
    vdiff = {skey:yspeed[skey]-hspeed[skey] for skey in yspeed.keys()}
    fnum = fax.hist(vdiff[bmnum[1]], diff_inc, range=diff_range, color=fcolor)
    rnum = rax.hist(vdiff[bmnum[-1]], diff_inc, range=diff_range, color=rcolor)
    nnum = nax.hist(vdiff["reject"], diff_inc, range=diff_range, color="0.6")
    fax.set_ylabel("Front\nNumber Points")
    rax.set_ylabel("Rear\nNumber Points")
    nax.set_ylabel("Removed from Front\nNumber Points")
    fax.xaxis.set_major_locator(ticker.MultipleLocator(75))
    rax.xaxis.set_major_locator(ticker.MultipleLocator(75))
    nax.xaxis.set_major_locator(ticker.MultipleLocator(75))
    fax.xaxis.set_major_formatter(ticker.FormatStrFormatter(""))
    rax.xaxis.set_major_formatter(ticker.FormatStrFormatter(""))
    nax.set_xlabel("LoS Velocity - HWM Meridional Wind (m s$^{-1}$)")
    fax.set_xlim(diff_range[0], diff_range[1])
    rax.set_xlim(diff_range[0], diff_range[1])
    nax.set_xlim(diff_range[0], diff_range[1])
    mnum = (int(max(fnum[0].max(), rnum[0].max(), nnum[0].max()))/10 + 1) * 10.0
    fax.set_ylim(0,mnum)
    rax.set_ylim(0,mnum)
    nax.set_ylim(0,mnum)
    fax.plot([0, 0], [0, mnum], "k:")
    rax.plot([0, 0], [0, mnum], "k:")
    nax.plot([0, 0], [0, mnum], "k:")
    unit = "(m s$^{-1}$)"
    fax.text(-190, 0.65*mnum,
             "$\mu$={:.1f} {:s}\n$\sigma$={:.1f} {:s}".format( \
            np.mean(vdiff[bmnum[1]]), unit, np.std(vdiff[bmnum[1]]), unit))
    rax.text(-190, 0.65*mnum,
             "$\mu$={:.1f} {:s}\n$\sigma$={:.1f} {:s}".format( \
            np.mean(vdiff[bmnum[-1]]), unit, np.std(vdiff[bmnum[-1]]), unit))
    nax.text(-190, 0.65*mnum,
             "$\mu$={:.1f} {:s}\n$\sigma$={:.1f} {:s}".format( \
            np.mean(vdiff["reject"]), unit, np.std(vdiff["reject"]), unit))
    plt.subplots_adjust(wspace=.3, hspace=.1, right=.93)

    if draw:
        # Draw to screen.
        if plt.isinteractive():
            plt.draw() #In interactive mode, you just "draw".
        else:
            # W/o interactive mode, "show" stops the user from typing more 
            # at the terminal until plots are drawn.
            plt.show()

    # Save figure
    if figname is not None:
        f.savefig(figname)

    return(f, [ax, fax, rax, nax], beams)

#-------------------------------------------------------------------------
def plot_map(ax, scan, hard=None, map_handle=None, fovs={1:None,-1:None},
             plot_beams={1:list(),-1:list()}, color_beams={1:list(),-1:list()},
             maxgates=None, fan_model='IS', model_alt=300.0, elv_attr="fovelv",
             alt_attr="vheight", dat_attr="v", fov_attr="fovflg", dmax=500.0,
             dmin=-500.0, dcolor=ccenter, lat_label=True, lon_label=True,
             gscatter=True, draw_map=True, plot_name=True, draw=True):
    """Plot a fov map

    Parameters
    -----------
    ax : (axis handle)
        Axis handle
    scan : (list of beams)
        List of beam class objects
    hard : (pydarn.radar.site or NoneType)
        Hardware data (default=None)
    map_handle : (basemap or NoneType)
        Basemap handle or NoneType (default=None)
    fovs : (dict)
        Dictionary containing radar fields-of-view.  If None, FoV will be
        loaded.  If False, FoV will not be plotted.
        (default={1:None,-1:None})
    plot_beams : (dict)
        Dictionary containing lists of radar beam numbers to highlight
        (default={1:list(),-1:list()})
    color_beams : (dict)
        Dictionary containing lists of colors to use to highlight radar beams
        (default={1:list(),-1:list()})
    maxgates : (int, float, or NoneType)
        Maximum range gate to plot (default=None)
    fan_model : (str or NoneType)
        Type of model to use when plotting data (default="IS")
        IS : Ionospheric Backscatter model
        GS : Ground Backscatter model
        S  : standard projection model
        E1 : for Chisham E-region 1/2-hop ionospheric projection model
        F1 : for Chisham F-region 1/2-hop ionospheric projection model
        F3 : for Chisham F-region 1 1/2-hop ionospheric projection model
        C  : Chisham projection model
        None : No model, use elevation and altitude
    model_alt : (float)
        Model altitude if IS or GS is used (default=300.0)
    elv_attr : (str)
        Beam fit attribute containing elevation (default="fovelv")
    alt_attr : (str)
        Beam fit attribute containing altitude (default="vheight")
    dat_attr : (str)
        Beam fit attribute containing data to plot (default="v")
    fov_attr : (str)
        Beam fit attribute contaiing field-of-view flag (default="fovflg")
    dmax : (float)
        Minimum data value to plot (default=500.0)
    dmin : (float)
        Maximum data value to plot (default=-500.0)
    dcolor : (str)
        Color map for data (default="RdYlBu"
    lat_label : (boolian)
        Include latitude label on the y-axis (default=True)
    lon_label : (boolian)
        Include longitude label on the x-axis (default=True)
    gscatter : (boolian)
        Include groundscatter (default=True)
    draw : (boolian)
        Output figure to display? (default=True)

    Returns
    ---------
    map_handle : (basemap)
        map handle
    fov : (dict)
        Dictionary of fields-of-view
    hard : ( or NoneType)
        Hardware data (default=None)
    """
    import davitpy.pydarn.plotting as plotting
    import davitpy.pydarn.radar as pyrad

    fov_dir = {1:"front", -1:"back"}

    # Load the radar location data, if necessary
    if hard is None:
        try:
            hard = pyrad.site(radId=scan[0].stid, dt=scan[0].time)
        except:
            return None, None, None, None

    # Initialize the FoV model parameters, and save the data as well
    maxgates = maxgates if maxgates is not None else scan[0].prm.nrang+1
    fan_data = np.ones(shape=(hard.maxbeam, maxgates), dtype=float) * np.nan
    fan_fov = np.zeros(shape=(hard.maxbeam, maxgates), dtype=int)
    if fan_model.find('IS') != 0 and fan_model.find('GS') != 0:
        fan_model = None
        fan_elv = np.ones(shape=(hard.maxbeam, maxgates), dtype=float) * np.nan
        fan_alt = np.ones(shape=(hard.maxbeam, maxgates), dtype=float) * np.nan
    else:
        fan_elv = None
        fan_alt = model_alt

    for bm in scan:
        try:
            dat = getattr(bm.fit, dat_attr)
        except:
            continue

        try:
            fovflg = getattr(bm.fit, fov_attr)
        except:
            fovflg = [1 for d in dat]

        if fan_model is None:
            try:
                elv = getattr(bm.fit, elv_attr)
                alt = getattr(bm.fit, alt_attr)
            except:
                continue

        for i,d in enumerate(dat):
            if bm.fit.slist[i] >= maxgates:
                break

            gflg = False
            if fan_model is None:
                fan_elv[bm.bmnum, bm.fit.slist[i]] = elv[i]
                fan_alt[bm.bmnum, bm.fit.slist[i]] = alt[i]
                gflg = True
            elif gscatter:
                gflg = True
            elif((fan_model.find('IS') == 0 and bm.fit.gflg[i] == 0)
                 or (fan_model.find('GS') == 0 and bm.fit.gflg[i] == 1)):
                gflg = True

            if gflg:
                fan_data[bm.bmnum, bm.fit.slist[i]] = d
                fan_fov[bm.bmnum, bm.fit.slist[i]] = fovflg[i]

    # Load the field-of-view data, if necessary
    for ff in fovs.keys():
        if fovs[ff] is None:
            fovs[ff] = pyrad.radFov.fov(site=hard, rsep=scan[0].prm.rsep,
                                        nbeams=hard.maxbeam, ngates=maxgates,
                                        bmsep=hard.bmsep, elevation=fan_elv,
                                        altitude=fan_alt, model=fan_model,
                                        coords="geo", date_time=scan[0].time,
                                        fov_dir=fov_dir[ff])

    # Add a map with the field-of-view and beams highlighted
    urlat = np.ceil(fovs[1].latFull.max())
    urlon = np.ceil(max(fovs[1].lonFull.max(), fovs[-1].lonFull.max()))
    urlon = urlon + 15.0 if urlat > 65.0 else urlon + 1.0
    lllat = np.floor(fovs[-1].latFull.min()) - 1.0
    lllon = np.ceil(min(fovs[1].lonFull.min(), fovs[-1].lonFull.min()))
    lllon = lllon - 15.0 if lllat < -65.0 else lllon - 1.0
    if map_handle is None:
        map_handle = basemap.Basemap(projection="stere", lon_0=hard.geolon,
                                     lat_0=hard.geolat, llcrnrlon=lllon,
                                     llcrnrlat=lllat, urcrnrlon=urlon,
                                     urcrnrlat=urlat, resolution="l")

    map_handle.ax = ax

    if draw_map:
        map_handle.drawcoastlines(linewidth=0.5, color="0.6")
        map_handle.fillcontinents(color="0.6", alpha=.1)
        map_handle.drawmeridians(np.arange(-180.0, 180.0, 15.0),
                                 labels=[0,0,0,lon_label])
        map_handle.drawparallels(np.arange(lllat, urlat+1.0, 10.0),
                                 labels=[lat_label,0,0,0])

    # Add the field-of-view boundaries
    for ff in fovs.keys():
        plotting.mapOverlay.overlayFov(map_handle, ids=scan[0].stid,
                                       dateTime=scan[0].time,
                                       beams=plot_beams[ff],
                                       beamsColors=color_beams[ff],
                                       fovObj=fovs[ff])

    # Add the radar location and name
    norm = mcolors.Normalize(vmin=dmin, vmax=dmax)
    plotting.mapOverlay.overlayRadar(map_handle, ids=scan[0].stid,
                                     dateTime=scan[0].time, annotate=plot_name,
                                     fontSize=16)

    # Add the data to each field-of-view
    bi, si = np.where(fan_fov != 0)
    verts = list()
    vals = np.ones(shape=bi.shape, dtype=float) * np.nan

    for ii,bb in enumerate(bi):
        # Get the field-of-view
        ff = fovs[fan_fov[bb,si[ii]]]

        # Get the polygon vertices
        x1, y1 = map_handle(ff.lonFull[bb, si[ii]], ff.latFull[bb, si[ii]])
        x2, y2 = map_handle(ff.lonFull[bb, si[ii]+1], ff.latFull[bb, si[ii]+1])
        x3, y3 = map_handle(ff.lonFull[bb+1, si[ii]+1],
                            ff.latFull[bb+1, si[ii]+1])
        x4, y4 = map_handle(ff.lonFull[bb+1, si[ii]], ff.latFull[bb+1, si[ii]])
        verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))
        # Assign the data
        vals[ii] = (fan_data[bb,si[ii]] if(fan_data[bb,si[ii]] < dmax and
                                           fan_data[bb,si[ii]] > dmin)
                    else (dmin if fan_data[bb,si[ii]] <= dmin else dmax))

    # Overlay the data over the fields-of-view
    if len(verts) > 0:
        inx = np.arange(len(verts))
        pcoll = mcol.PolyCollection(np.array(verts)[inx], edgecolors='face',
                                    linewidths=0, closed=False, zorder=4,
                                    cmap=cm.get_cmap(dcolor), norm=norm)
        pcoll.set_array(vals[inx])
        ax.add_collection(pcoll, autolim=True)

    if hasattr(scan[0], "scan_time"):
        ax.set_title("{:}".format(scan[0].scan_time), fontsize="medium")
    else:
        ax.set_title("{:}".format(scan[0].time), fontsize="medium")

    if draw:
        # Draw to screen.
        if plt.isinteractive():
            plt.draw() #In interactive mode, you just "draw".
        else:
            # W/o interactive mode, "show" stops the user from typing more 
            # at the terminal until plots are drawn.
            plt.show()

    # Return
    return(map_handle, fovs, hard, pcoll)
