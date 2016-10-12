#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# update_backscatter.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Update the beam's groundscatter flag, calculate the virtual height
#           and propagation path, determine the origin field-of-view, update
#           the elevation.
#-----------------------------------------------------------------------------
"""update_backscatter

Routines to update the groundscatter and elevation angle, as well as determine
the virtual height, hop, and origin field-of-view for each backscatter point.

Functions
------------------------------------------------------------------------------
assign_region               ionosphere region based on virtual height
test_propagation            test propgation against reality
select_alt_groups           determine altitude limits for range gate
get_beam                    load beams from list or pointer
calc_distance               calculate slant range
select_beam_groundscatter   filter to select groundscatter data
calc_frac_points            calculate precentage of groundscatter
update_bs_w_scan            update propagation parameters, 1 > beam
update_beam_fit             update beam data
update_backscatter          update propagation parameters, one beam
beam_ut_struct_test         test for continuity in UT across beams
------------------------------------------------------------------------------

Author: Angeline G. Burrell (AGB)
Date: January 15, 2015
Inst: University of Leicester (UoL)
"""

# Import python packages
import numpy as np
from scipy import constants as scicon
from scipy import stats as stats
from scipy import optimize as optimize
from scipy import signal as scisig
import datetime as dt
import logging
# Import DaViTpy packages is done within routines to prevent this causing
# an error when initially loading davitpy

#---------------------------------------------------------------------------
def assign_region(vheight, region_hmax={"D":115.0,"E":150.0,"F":900.0},
                  region_hmin={"D":75.0,"E":115.0,"F":150.0}, case="upper"):
    """Assign an ionospheric region based on virtual height.

    "D" (75 - 115 km)
    "E" (115 - 200 km) is detected at distances lass than 900 km
    "F" (200 -900 km) is detected at all distances
    "" if values fall outside of specified altitudes

    Parameters
    -------------
    vheight : (float)
        Virtual height of peak of propagation path
    region_hmax : (dict)
        Maximum virtual heights allowed in each ionospheric layer.
        (default={"D":115.0,"E":150.0,"F":400.0})
    region_hmin : (dict)
        Minimum virtual heights allowed in each ionospheric layer.
        (default={"D":75.0,"E":115.0,"F":150.0})
    case : (str)
        Provide the output in uppercase or lowercase (default=upper)

    Returns
    -----------
    region : (str)
        one (or zero) character string denoting region
    """
    region = ""
    rpad = {"D":0.0, "E":0.0, "F":1.0}

    for rr in region_hmax.keys():
        if region_hmin[rr] <= vheight and vheight < region_hmax[rr] + rpad[rr]:
            region = rr.lower() if case is "lower" else rr

    return region

#---------------------------------------------------------------------------
def test_propagation(hop, vheight, dist,
                     region_hmax={"D":115.0,"E":150.0,"F":900.0},
                     region_hmin={"D":75.0,"E":115.0,"F":150.0}):
    """Test the propagation path for realism.  Use the basic properties of HF
    radars.
    D-region (<= 115 km) is detected at distances less than 500 km
    E-region (115 - 150(or 200?) km) is detected at distances lass than X km
    F-region (>= 150 km) is detected at all distances

    Parameters
    -------------
    hop : (float)
        Number of hops traveled by this radar signal
    vheight : (float)
        Virtual height of the peak of the propagation path
    dist : (float)
        Distance from the radar to the first peak of the propagation path in km
    region_hmax : (dict)
        Maximum virtual heights allowed in each ionospheric layer.
        (default={"D":115.0,"E":150.0,"F":400.0})
    region_hmin : (dict)
        Minimum virtual heights allowed in each ionospheric layer.
        (default={"D":75.0,"E":115.0,"F":150.0})

    Returns
    -----------
    good : (boolian)
        True if the path is realistic, False if it is not
    """
    good = True

    if region_hmax.has_key("D") and vheight <= region_hmax["D"]:
        if hop > 0.5 or dist > 500.0:
            # D-region backscatter is restricted to 0.5 hop ionospheric
            # backscatter near the radar (flat earth-approximation holds,
            # great circle distance is rounded down, to simplify things)
            good = False
    elif region_hmax.has_key("E") and vheight <= region_hmax["E"]:
        if hop < 1.5 and dist > 900.0:
            # 0.5E and 1.0E backscatter is restrictued to slant path distances
            # of 1000 km or less.  1.5E backscatter is typically seen at far
            # range gates and can be entirely E-region or F/E-region
            good = False

    return good

#---------------------------------------------------------------------------
def select_alt_groups(gate, vheight, rmin, rmax, vh_box, min_pnts=3):
    """Determine appropriate altitude limits for the data in this range gate
    box.  This is done by fitting a Gaussian curve to each of the occurance
    peaks and setting the range to +/-3 sigma from the mean.  Areas with points
    not encompassed by the fitted limits are constructed using the vh_box as
    a guide for total width.

    Parameters
    -------------
    gate : (np.ndarray)
        Array of range gates for the selected points
    vheight : (np.ndarray)
        Array of virtual heights for the selected points (km)
    rmin : (float)
        Minimum virtual height for this region in km
    rmax : (float)
        Maximum virtual height for this region in km
    vh_box : (float)
        Suggested virtual height width in km
    min_pnts : (int)
        Minimum number of points needed to actually use a height bracket.
        (default=3)

    Returns
    -----------
    vh_mins : (list)
        list of virtual height minima
    vh_maxs : (list)
        List of virtual height maxima
    """
    # Define local functions
    def gaussian(x, *p):
        A, mu, sigma = p
        return A * np.exp(-(x - mu)**2 / (2. * sigma**2))

    # Initialize output
    vh_mins = list()
    vh_maxs = list()
    vh_peaks = list()

    # Create a histogram of the number of observations at each virtual height
    bnum = int((rmax-rmin) / (vh_box * 0.25))
    hnum, hbin = np.histogram(vheight, bnum if bnum > 10 else 10, (rmin,rmax))

    # Find the maxima in the histogram
    hmax = scisig.argrelmax(hnum, order=2)[0]

    # Since the signal routine won't be able to identify a maxima if two bins
    # next to each other have the same value, use the global maximum if no
    # local maxima were identified
    if len(hmax) == 0 and max(hnum) > min_pnts:
        hmax = np.array([list(hnum).index(max(hnum))])

    # Consider each maxima seperately or, if none could be found, set limits
    # using the suggested width.
    tmin = np.nanmin(vheight)
    tmax = np.nanmax(vheight)
    if len(hmax) == 0:
        if np.isnan(tmin) or np.isnan(tmax):
            return vh_mins, vh_maxs

        vnum = np.ceil((tmax - tmin) / vh_box)
        vmin = (tmax - tmin) / vnum + tmin - vh_box

        vh_mins = [vmin + n * vh_box for n in np.arange(vnum)]
        vh_maxs = [n + vh_box for n in vh_mins]
    else:
        # For each maxima, fit a Gaussian
        param = [0.0, 0.0, vh_box * 0.5]
        cbin = (hbin[:-1] + hbin[1:]) / 2.0
        hpeak = {hnum[ih]:ih for ih in hmax}
        for hh in sorted(hpeak.keys(), reverse=True):
            ih = hpeak[hh]
            param[0] = hh
            param[1] = cbin[ih]
            try:
                coeff, var = optimize.curve_fit(gaussian, cbin, hnum, p0=param)
                # Evaluate for np.nan in coefficients
                try:
                    np.isnan(coeff).tolist().index(True)
                except:
                    # Get the 3 sigma limits
                    vmin = coeff[1] - 3.0 * coeff[2]
                    if vmin < rmin:
                        vmin = rmin
                    vmax = coeff[1] + 3.0 * coeff[2]
                    if vmax > rmax:
                        vmax = rmax

                    # Get the 2 sigma limits
                    vlow = coeff[1] - 2.0 * coeff[2]
                    if vlow < rmin:
                        vlow = rmin
                    vhigh = coeff[1] + 2.0 * coeff[2]
                    if vhigh > rmax:
                        vhigh = rmax

                    # If the fitted curve does not include the detected peak
                    # within a 2 sigma limit, throw out this fit.
                    if cbin[ih] < vlow or cbin[ih] > vhigh:
                        coeff = list()
                    else:
                        # To allow secondary peaks to be fitted, remove this
                        # peak from consideration
                        hnum = [hnum[ic] if cc < vmin or cc >= vmax else 0
                                for ic,cc in enumerate(cbin)]

                        # Save the initial peak boundaries
                        vh_mins.append(vmin)
                        vh_maxs.append(vmax)
                        vh_peaks.append(coeff[1])
            except:
                pass

        # Evaluate the current limits to see if they overlap other limits
        # or to see if there are gaps.  Re-order the limits to start at the
        # lowest and end at the highest.  If no limits were found, set them.
        if len(vh_maxs) == 0:
            vnum = np.ceil((tmax - tmin) / vh_box)
            vmin = (tmax - tmin) / vnum + tmin - vh_box

            vh_mins = [vmin + n * vh_box for n in np.arange(vnum)]
            vh_maxs = [n + vh_box if n + vh_box < rmax else rmax
                       for n in vh_mins]

            for n,vmin in enumerate(vh_mins):
                if vmin < rmin:
                    vh_mins[n] = rmin
                else:
                    break
        else:
            new_min = list()
            new_max = list()
            new_peak = list()
            priority = list() # Low number means high priority to keep limits

            # If there are points that fall below the lower limit, add more
            # regions to include these points.
            if min(vh_mins) > tmin:
                vmax = min(vh_mins)
                vnum = round((vmax - tmin) / vh_box)
                if vnum == 0.0:
                    # The outlying points are close enough that the lower limit
                    # should be expanded
                    imin = vh_mins.index(min(vh_mins))
                    vh_mins[imin] = np.floor(tmin)
                    if vh_mins[imin] < rmin:
                        vh_mins[imin] = rmin
                else:
                    vspan = (vmax - tmin) / vnum

                    for n in np.arange(vnum):
                        nmin = tmin + n * vspan
                        if nmin < rmin:
                            nmin = rmin
                        new_min.append(nmin)
                        new_max.append(tmin + (n + 1.0) * vspan)
                        new_peak.append(tmin + (n + 0.5) * vspan)
                        priority.append(len(vh_mins) + len(new_min))

            # Sort the Gaussian limits by minimum virtual height and cycle
            # through them.
            for vmin in sorted(vh_mins):
                iv = vh_mins.index(vmin)

                if len(new_min) > 0:
                    # Test for overlaps or gaps with the previous height window
                    if new_max[-1] >= vh_peaks[iv] or vmin <= new_peak[-1]:
                        # There is a significant overlap between the two regions
                        if priority[-1] < iv:
                            # Adjust the current boundaries
                            vmin = new_max[-1]
                        else:
                            # Adjust the previous boundaries
                            new_max[-1] = vmin

                            # If this adjustment places the previous maximum
                            # at or below the previous minimum, remove that
                            # division
                            if new_max[-1] <= new_min[-1]:
                                new_max.pop()
                                new_min.pop()
                                new_peak.pop()
                                priority.pop()
                    elif new_max[-1] < vmin:
                        # There is a gap between the two windows.  Construct
                        # bridging window(s) before adding the current max and
                        # min to the list.
                        bmin = new_max[-1]
                        bmax = vmin
                        vnum = round((bmax - bmin) / vh_box)
                        if vnum == 0.0:
                            # The outlying points are close enough that the
                            # last upper limit should be expanded
                            new_max[-1] = vmin
                        else:
                            vspan = (bmax - bmin) / vnum

                            for n in np.arange(vnum):
                                new_min.append(bmin + n * vspan)
                                new_max.append(bmin + (n + 1.0) * vspan)
                                new_peak.append(bmin + (n + 0.5) * vspan)
                                priority.append(len(vh_mins) + len(new_min))

                # Now append the current window, if it is wide enough to
                # be sensible
                if vmin < vh_maxs[iv]:
                    new_min.append(vmin)
                    new_max.append(vh_maxs[iv])
                    new_peak.append(vh_peaks[iv])
                    priority.append(iv)

            # If there are points that fall above the upper limit, add more
            # regions to include these points.
            if len(new_max) == 0 or max(new_max) < tmax:
                vmin = max(new_max)
                vnum = round((tmax - vmin) / vh_box)
                if vnum == 0.0:
                    # The outlying points are close enough that the upper limit
                    # should be expanded
                    imax = new_max.index(max(new_max))
                    new_max[imax] = np.ceil(tmax)
                    if new_max[imax] > rmax:
                        new_max[imax] = rmax
                else:
                    vspan = (tmax - vmin) / vnum

                    for n in np.arange(vnum):
                        nmax = vmin + (n + 1.0) * vspan
                        if nmax > rmax:
                            nmax = rmax
                        new_min.append(vmin + n * vspan)
                        new_max.append(rmax)
                        new_peak.append(vmin + (n + 0.5) * vspan)
                        priority.append(len(vh_mins) + len(new_min))

            # Rename the output
            vh_mins = new_min
            vh_maxs = new_max

    # Return the limits
    return vh_mins, vh_maxs

#---------------------------------------------------------------------------
def get_beam(radar_beams, nbeams):
    """Define a routine to load the beams from either a list/np.array or
    pointer

    Parameters
    ------------
    radar_beams : (list, numpy array, or class `sdio.radDataTypes.radDataPtr`)
        Object containing the radar beam data
    nbeams : (int)
        Number of beams returned before this beam

    Returns
    --------
    beam : (class `sdio.radDataTypes.radDataBeam` or NoneType)
        Beam containing radar data or None, if no data is available
    nbeams : (int)
        Number of beams retrieved from radar_beams, including this beam
    """
    import davitpy.pydarn.sdio as sdio

    if((isinstance(radar_beams, list) or isinstance(radar_beams, np.ndarray))
        and nbeams < len(radar_beams)):
        beam = radar_beams[nbeams]
        nbeams += 1
    elif isinstance(radar_beams, sdio.radDataTypes.radDataPtr):
        beam = radar_beams.readRec()
        nbeams += 1
    else:
        beam = None

    return beam, nbeams

#----------------------------------------------------------------------------
def calc_distance(beam, rg_attr="slist", dist_units="km", hop=.5):
    """A routine to calculate distance in either meters or kilometers along the
    slant path from the radar to the first ionospheric reflection/refraction
    point using the range gate and a propagation path specified by the hop
    number.  Currently only simple propagation paths (same ionospheric region)
    are allowed.

    Hop examples
    -------------
    0.5 hop : For ionospheric backscatter located in the observed range gate.
              The distance is the distance to the observed range gate.
    1.0 hop : For ground backscatter; the distance is half the distance to the
              observed range gate
    1.5 hop : For ionospheric backscatter; the distance is one thrid the of the
              distance to the observed range gate

    Parameters
    -----------
    beam : (class `pydarn.sdio.radDataTypes.beamData`)
        Data for a single radar and beam along all range gates at a given time
    rg_attr : (str)
        Beam attribute for range gate (default="slist")
    dist_units : (str)
        Units of the distance to backscatter location data.  May supply "km" or
        "m".  (default="km")
    hop : (float)
        Specifies the hop location of the range gate.  Nominally, range gates
        are located at 0.5 hop (assumes ionospheric scatter).  (default=0.5)
    
    Returns
    --------
    dist : (np.array or NoneType)
        A list of floats of the same size as the myBeam.fit.slist list,
        containing the distance along the slant path from the radar to the first
        ionospheric reflection/refraction point given the specified propagation
        path for for each range gate. Returns None upon input error.
    """
    import davitpy.pydarn.sdio as sdio

    #---------------------------------
    # Check the input
    estr = None
    if not isinstance(beam, sdio.radDataTypes.beamData):
        estr = 'the beam must be a beamData class'
    elif not isinstance(rg_attr, str) or not hasattr(beam.fit, rg_attr):
        estr = 'no range gate attribute [{:}]'.format(rg_attr)
    elif dist_units is not "km" and dist_units is not "m":
        estr = 'unknown units for distance [{:}]'.format(dist_units)
    elif not isinstance(hop, float) and hop > 0.0 and hop % 0.5 == 0.0:
        estr = 'unknown hop number [{:}]'.format(hop)
    else:
        # Load the range gate data
        try:
            rg = getattr(beam.fit, rg_attr)

            if not isinstance(rg, list) or len(rg) == 0:
                estr = 'unable to load range gate'
        except:
            estr = 'unable to load range gate'

    #---------------------------------------------------------
    # Convert from range gates to distance or exit with error
    if estr is None:
        # Determine the number of reflection/refraction points along the
        # propagation path
        bounces = 2.0 * hop

        # Determine the unit conversion
        units = 1000.0 if dist_units is "m" else 1.0

        # Calculate the distance
        dist = 5.0e-10 * scicon.c * units * (np.array(rg) * beam.prm.smsep
                                             + beam.prm.lagfr) / bounces
    else:
        logging.error(estr)
        dist = None

    return dist

#---------------------------------------------------------------------------
def select_beam_groundscatter(beam, dist, min_rg=10, max_rg=76, rg_box=5,
                              max_p=5.0, max_v=30.0, max_w=90.0, gs_tol=.5,
                              nmin=5):
    """A routine to select groundscatter data.  Currently uses a range gate
    limit where all data beyond the maximum range gate is rejected, all
    data with 0.5 hop distances closer than 160 km are rejected, and all points
    closer than the minimum range gate that have a power greater than the
    specified power maximum are also rejected.  One these requirements have
    been met, the data must have positive power, and have the groundscatter
    flag set.

    Parameters
    ------------
    beam : (class beamData)
        An object with radar data for a certain beam, channel, and radar
    dist : (list or np.array)
        List of slant path (radar to reflection point) distances in km
    min_rg : (int)
        Minimum range gate to look for groundscatter with any power level
        (default=10)
    max_rg : (int)
        Maximum range gate to look for groundscatter with any power level
        (default=76)
    rg_box : (int)
        Number of range gates to search above and below the range gate
        specified by rg_index. (default=10)
    max_p : (float)
        Maximum power to allow at range gates closer than the minimum range
        gate (default=5 dB)
    max_v : (float)
        Maximum velocity to allow at range gates closer than the minimum range
        gate (default=30 m/s)
    max_w : (float)
        Maximum spectral width to allow at range gates closer than the minimum
        rangegate (default=90 m/s)
    gs_tol : (float)
        Minimum fraction of points within a range gate box that should be
        groundscatter if this point is to actually be considered groundscatter.
        (default=0.5)
    nmin : (int)
        Minimum number of points that must bepresent within a range gate box to
        consider the backscatter anything other than noise. (default=3)

    Returns
    ------------
    gnd_index : (list)
        List of indices corresponding to selected groundscatter data in the
        input beam (eg slist, p_l, etc.)

    If there is an input error, exits with an exception
    """
    import davitpy.pydarn.sdio as sdio

    #---------------------
    # Check input
    assert isinstance(beam, sdio.radDataTypes.beamData), \
        logging.error("beam is not a beamData object")
    assert((isinstance(dist, list) or isinstance(dist, np.ndarray))
           and len(dist) == len(beam.fit.slist)), \
        logging.error("distance list does not match this beam")
    if isinstance(min_rg, float):
        min_rg = int(min_rg)
    assert isinstance(min_rg, int), \
        logging.error("min_rg is not an integer")
    if isinstance(max_rg, float):
        max_rg = int(max_rg)
    assert isinstance(max_rg, int), \
        logging.error("max_rg is not an integer")
    if isinstance(rg_box, float):
        rg_box = int(rg_box)
    assert(isinstance(rg_box, int) and rg_box > 0), \
        logging.error("rg_box is not a positive integer")
    if isinstance(max_p, int):
        max_p = float(max_p)
    assert isinstance(max_p, float), \
        logging.error("maximum power is not a float")
    if isinstance(max_v, int):
        max_v = float(max_v)
    assert isinstance(max_v, float), \
        logging.error("maximum velocity is not a float")
    if isinstance(max_w, int):
        max_w = float(max_w)
    assert isinstance(max_w, float), \
        logging.error("maximum spectral width is not a float")
    assert(isinstance(gs_tol, float) and gs_tol >= 0.0 and gs_tol <= 1.0), \
        logging.error("gs_tol is not a positive fraction")
    if isinstance(nmin, float):
        nmin = int(nmin)
    assert(isinstance(nmin, int) and nmin > 0), \
        logging.error("rg_box is not a positive integer")

    #--------------------------------------------------------------------
    # Identify all instances that are flagged as ground scatter and have
    # appropriate power fits based on their location
    def isgroundscatter(rg, dist, p_l, p_s, sd_gflg):
        """A routine to apply the logic that states whether or not a point is
        groundscatter or not, rejecting groundscatter points that are
        ambiguous

        Parameters
        -----------
        rg : (int)
            Range gate
        dist : (float)
            Slant path distance to from radar to reflection point (km)
        p_l : (float)
            Power determined using exponential fit (dB)
        p_s : (float)
            Power determined using Gaussian fit (dB)
        sd_gflg : (int)
            SuperDARN groundscatter flag

        Returns
        ---------
        gflg : (boolean)
            New groundscatter flag
        """
        gflg = False

        # To be groundscatter, the point must have been identified by the
        # SuperDARN routine (which uses velocity and spectral width to flag
        # all points that are most likely not ionospheric scatter) and have
        # successful exponential and Gaussain power fits.  The distance
        # must also be greater than 78 km from the radar, since this is the
        # smallest imaginable distance that groundscatter could possibly occur
        # at (yeilds a virtual height of 110 km for an elevation angle of 45
        # deg)
        if sd_gflg == 1 and p_l >= 0.0 and p_s >= 0.0 and dist > 78.0:
            # Test the nearby range gates to ensure the power is not too high.
            # This will remove slow moving ionospheric scatter
            if rg < min_rg:
                if p_l <= max_p and p_s <= max_p:
                    gflg = True
            else:
                gflg = True

        return gflg
        # END isgroundscatter

    gi = [i for i,s in enumerate(beam.fit.slist)
          if(s <= max_rg and isgroundscatter(s, dist[i], beam.fit.p_l[i],
                                             beam.fit.p_s[i],
                                             beam.fit.gflg[i]))]
        
    #--------------------------------------------------------------------------
    # Ensure that the flagged groundscatter is not mislabeled by testing to see
    # if it is an isolated point surrounded by ionospheric scatter or not.
    gnd_index = list()
    for i in gi:
        gs_frac, npnts = calc_frac_points(beam, "slist", gi, i, box=rg_box,
                                          dat_min=0, dat_max=beam.prm.nrang)

        if gs_frac >= gs_tol and npnts >= nmin:
            gnd_index.append(i)

    return(gnd_index)

#----------------------------------------------------------------------
def calc_frac_points(beam, dat_attr, dat_index, central_index, box,
                     dat_min=None, dat_max=None):
    """Calculate the fraction of points within a certain distance about a
    specified range gate are groundscatter.

    Parameters
    ------------
    beam : (class beamData)
        An object with radar data for a certain beam, channel, and radar
    dat_attr : (str)
        Attribute of data type
    dat_index : (list of int)
        A list containing the indexes of acceptable data points within the
        specified beam.fit attribute list
    central_index : (int)
        The index of the desired data point to search about.
    box : (float or int)
        Size of to data box to search above and below the central data value
        specified by the central_index.  This must be in units of the specified
        data.
    dat_min : (float or int)
        Lowest possible value of the data (eg 0 for range gates). (default=None)
    dat_max : (float or int)
        Highest possible value of the data (eg 75 for range gates at han).
        (default=None)

    Returns
    ----------
    frac : (float)
        A number between 0.0 and 1.0, indicating the fraction of points in the
        specified area that are acceptable according to the dat_index list.
    npnts : (int)
        Total number of observations in the specified box.

    If there is an input error, exits with an exception
    """
    import davitpy.pydarn.sdio as sdio

    #----------------
    # Check input
    assert isinstance(beam, sdio.radDataTypes.beamData), \
        logging.error("beam is not a beamData object")
    assert isinstance(dat_attr, str) and hasattr(beam.fit, dat_attr), \
        logging.error("beam does not contain attribute {:}".format(dat_attr))
    assert isinstance(dat_index, list) and isinstance(dat_index[0], int), \
        logging.error("dat_index is not a list of integers")
    assert box > 0, logging.error("box is not positive")
    assert isinstance(dat_min, type(box)) or dat_min is None, \
        logging.error("dat_min is of a different type is suspect")
    assert isinstance(dat_max, type(box)) or dat_max is None, \
        logging.error("dat_max is of a different type is suspect")

    # Get the data list and ensure there is a value to search about
    data = getattr(beam.fit, dat_attr)
    assert isinstance(central_index, int) and central_index < len(data), \
        logging.error("no value for central_index in {:s}".format(dat_attr))

    #-------------------------------------------------------------------------
    # Set evaluation variables, restraining range gate box to realistic values
    dmin = data[central_index] - box
    dmax = data[central_index] + box

    if dat_min is not None and dmin < dat_min:
        dmin = dat_min
    if dat_max is not None and dmax > dat_max:
        dinc = 1 if isinstance(dat_max, int) else 1.0
        dmax = dat_max + dinc

    #---------------------
    # Initialize output
    frac = 0.0
    npnts = 0

    #-----------------------------------------------------------------------
    # Cycle through the range gates, updating the total number of points and
    # total number of groundscatter ponts
    for i,d in enumerate(data):
        if d >= dmin and d < dmax:
            npnts += 1

            try:
                dat_index.index(i)
                frac += 1.0
            except Exception:
                pass

    if npnts > 0 and frac > 0.0:
        frac /= float(npnts)

    return(frac, npnts)

#---------------------------------------------------------------------------
def update_bs_w_scan(scan, hard, min_pnts=3,
                     region_hmax={"D":115.0,"E":150.0,"F":900.0},
                     region_hmin={"D":75.0,"E":115.0,"F":150.0},
                     rg_box=[2,5,10,20], rg_max=[5,25,40,76],
                     vh_box=[50.0,50.0,50.0,150.0], max_hop=3.0, tdiff=None,
                     tdiff_args=list(), tdiff_e=None, tdiff_e_args=list(),
                     ptest=True, strict_gs=False, bmaz_e=0.0, boresite_e=0.0,
                     ix_e=0.0, iy_e=0.0, iz_e=0.0, step=6):
    """Updates the propagation path, elevation, backscatter type, structure
    flag, and origin field-of-view (FoV) for all backscatter observations in
    each beam for a scan of data.  A full scan is not necessary, but if the
    number of beams is less than the specified minimum, a less rigerous
    evaluation method is used.

    Parameters
    -------------
    scan : (list or np.array)
        A list of beamData class objects, representing a scan across the
        radar's field-of-view (as performed in most common operational modes).
    hard : (class `pydarn.radar.radStruct.site`)
        Radar hardware data for this scan
    min_pnts : (int)
        The minimum number of points necessary to perform certain range gate
        or beam specific evaluations. (default=3)
    region_hmax : (dict)
        Maximum virtual heights allowed in each ionospheric layer.
        (default={"D":115.0,"E":150.0,"F":900.0})
    region_hmin : (dict)
        Minimum virtual heights allowed in each ionospheric layer.
        (default={"D":75.0,"E":115.0,"F":150.0})
    rg_box : (list or np.array of int)
        The total number of range gates to include when examining the elevation
        angle across all beams. (default=[2,5,10,20])
    vh_box : (list or np.array of float)
        The total width of the altitude box to consider when examining the
        elevation angle across all beams at a given range gate.
        (default=[50.0,50.0,50.0,150.0])
    max_hop : (list or np.array of float)
        The maximum hop to consider for the range gate and height criteria
        specified by each list element in rg_box, srg_box, vh_box, and svh_box.
        (default=[3.0])
    tdiff : (function or NoneType)
        A function to retrieve tdiff values (in microsec) using the radar ID
        number, current datetime, and transmisson frequency as input.
        Additional inputs may be specified using tdiff_args.  Example:
        def get_tdiff(stid, time, tfreq, filename) { do things } return tdiff
        tdiff=get_tdiff, tdiff_args=["tdiff_file"]
        (default=None)
    tdiff_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff function.
        (default=list())
    tdiff_e : (function or NoneType)
        A function to retrieve tdiff error values (in microsec) using the radar
        ID number, current datetime, and transmisson frequency as input.
        Additionalinputs may be specified using tdiff_e_args.  Example:
        def get_tdiffe(stid, time, tfreq, filename) { do things } return tdiffe
        tdiff_e=get_tdiffe, tdiff_e_args=["tdiff_file"]
        (default=None)
    tdiff_e_args : (list)
        A list specifying any arguements other than radar, time, and
        transmission frequency to run the specified tdiff_e function.
        (default=list())
    ptest : (boolian)
        Perform test to see if propagation modes are realistic? (default=True)
    strict_gs : (boolian)
        Remove indeterminately flagged backscatter (default=False)
    bmaz_e : (float)
        Error in beam azimuth in degrees (default=0.0)
    boresite_e : (float)
        Error in the boresite location in degrees (default=0.0)
    ix_e : (float)
        Error in the interferometer x coordinate in meters (default=0.0)
    iy_e : (float)
        Error in the interferometer y coordinate in meters (default=0.0)
    iz_e : (float)
        Error in the interferometer z coordinate in meters (default=0.0)
    step : (int)
        Integer denoting the number of processing steps to perform.  This should
        always be set to 6 (or greater) unless one wishes to reproduce the
        demonstration plots in Burrell et al (2015). (default=6)  The step
        numbers coincide with those indicated in the paper:
        1 or 2: Examine the elevation structure across each scan
        3: Add assignments for points with realistic heights in only one FoV
        4: Add assignments using single-beam elevation angle variations
        5 or more: Test assignements for consistency along the scan.

    Returns
    ---------
    beams : (np.array)
        An array of updated beamData class objects.  These updated objects have
        the following additional/updated attributes

        beam.fit.fovelv : added : Accounts for adjusted tdiff and origin FoV
        beam.fit.fovelv_e : added : elevation error
        beam.fit.felv : added : Elevation angle assuming front FoV
        beam.fit.felv_e : added : Elevation angle error assuming front FoV
        beam.fit.belv : added : Elevation angle assuming rear FoV
        beam.fit.belv_e : added : Elevation angle error assuming front FoV
        beam.fit.vheight : added : virtual height of ionosphere in km
        beam.fit.vheight_e : added : error in virtual height (km)
        beam.fit.fvheight : added : virtual height assuming front FoV
        beam.fit.fvheight_e : added : error in virtual height assuming front FoV
        beam.fit.bvheight : added : virtual height assuming rear FoV
        beam.fit.bvheight_e : added : error in virtual height assuming rear FoV
        beam.fit.hop : added : Hop assuming the assigned origin FoV
        beam.fit.fhop : added : Hop assuming the front FoV
        beam.fit.bhop : added : Hop assuming the rear FoV
        beam.fit.region : added : Region assuming the assigned origin FoV
        beam.fit.fregion : added : Region assuming the front FoV
        beam.fit.bregion : added : Region assuming the rear FoV
        beam.fit.fovflg : added : Flag indicating origin FoV (1=front, -1=back,
                                  0=indeterminate)
        beam.fit.fovpast : added : Flag indicating past FoV assignments
        beam.fit.gflg : updated : Flag indicating backscatter type
                                  (1=ground, 0=ionospheric, -1=indeterminate)
        beam.prm.tdiff : added : tdiff used in elevation (microsec)
        beam.prm.tdiff_e : added : tdiff error (microsec)
    """
    import davitpy.pydarn.sdio as sdio
    import davitpy.pydarn.radar as pyrad

    max_std = 3.0 # This is the maximum standard deviation in degrees.
    max_score = 3.0 # This is the maximum z-score.  z = (x - mean(X)) / std(X)
    fov_frac = 2.0 / 3.0
    fov = {1:"front", -1:"back"}
    near_rg = -1

    #----------------------------------
    # Test input
    if(not ((isinstance(scan, list) or isinstance(scan, np.ndarray)) and
            len(scan) > 0 and len(scan) <= hard.maxbeam and
            isinstance(scan[0], sdio.radDataTypes.beamData))
       and not isinstance(scan, sdio.radDataTypes.radDataPtr)):
        estr = 'need a list of beams or a radar data pointer with [1-'
        estr = '{:s}{:d}] beams: length={:d}'.format(estr, hard.maxbeam,
                                                     len(scan))
        logging.error(estr)
        return None

    if isinstance(min_pnts, float):
        min_pnts = int(min_pnts)
    if not isinstance(min_pnts, int) or min_pnts < 0:
        logging.error('unknown point minimum [{:}]'.format(min_pnts))
        return None

    if not isinstance(region_hmin, dict) or min(region_hmin.values()) < 0.0:
        estr = 'unknown minimum virtual heights [{:}]'.format(region_hmin)
        logging.error(estr)
        return None

    if not isinstance(region_hmax, dict):
        estr = 'unknown maximum virtual heights [{:}]'.format(region_hmax)
        logging.error(estr)
        return None

    if((not isinstance(rg_box, list) and not isinstance(rg_box, np.ndarray))
       or min(rg_box) < 1.0):
        logging.error('bad FoV range gate box[{:}]'.format(rg_box))
        return None

    if((not isinstance(vh_box, list) and not isinstance(vh_box, np.ndarray))
       or min(vh_box) < 0.0):
        logging.error('bad FoV virtual height box [{:}]'.format(vh_box))
        return None

    #-------------------------------------------------------------------------
    # Loading the beams into the output list, updating the distance,
    # groundscatter flag, virtual height, and propogation path
    beams = np.empty(shape=(hard.maxbeam,), dtype='O')
    elvs = {"front":[list() for bi in range(hard.maxbeam)],
            "back":[list() for bi in range(hard.maxbeam)]}
    elv_errs = {"front":[list() for bi in range(hard.maxbeam)],
                "back":[list() for bi in range(hard.maxbeam)]}
    vheights = {"front":[list() for bi in range(hard.maxbeam)],
                "back":[list() for bi in range(hard.maxbeam)]}
    vherrs = {"front":[list() for bi in range(hard.maxbeam)],
              "back":[list() for bi in range(hard.maxbeam)]}
    hops = {"front":[list() for bi in range(hard.maxbeam)],
            "back":[list() for bi in range(hard.maxbeam)]}
    regions = {"front":[list() for bi in range(hard.maxbeam)],
               "back":[list() for bi in range(hard.maxbeam)]}
    bnum = 0
    snum = 0

    while scan is not None:
        # Load beams from scan, accounting for different input types
        if isinstance(scan, list) or isinstance(scan, np.ndarray):
            if snum < len(scan):
                beams[bnum] = scan[snum]
                snum += 1
            else:
                scan = None
        else:
            try:
                beams[bnum] = scan.readRec()
            except:
                estr = "{:s} INFO: empty data pointer".format(rn)
                logging.info(estr)
                scan = None

        bnum += 1
        # If a new beam was loaded, update the beam
        if bnum > len(beams):
            bnum = len(beams)
        elif beams[bnum-1] is None:
            bnum -= 1
        else:
            # Update the beam parameters
            if tdiff is None:
                beams[bnum-1].prm.tdiff = None
            else:
                args = [beams[bnum-1].stid, beams[bnum-1].time,
                        beams[bnum-1].prm.tfreq]
                args.extend(tdiff_args)
                beams[bnum-1].prm.tdiff = tdiff(*args)

            if tdiff_e is None:
                beams[bnum-1].prm.tdiff_e = None
            else:
                args = [beams[bnum-1].stid, beams[bnum-1].time,
                        beams[bnum-1].prm.tfreq]
                args.extend(tdiff_e_args)
                beams[bnum-1].prm.tdiff_e = tdiff_e(*args)

            # Update the beam fit values
            (beams[bnum-1], e, eerr, vh, verr, hh, rr,
             nhard) = update_beam_fit(beams[bnum-1], hard=hard,
                                      region_hmax=region_hmax,
                                      region_hmin=region_hmin, max_hop=max_hop,
                                      ptest=ptest, strict_gs=strict_gs,
                                      bmaz_e=bmaz_e, boresite_e=boresite_e,
                                      ix_e=ix_e, iy_e=iy_e, iz_e=iz_e)

            if e is None or nhard is None:
                beams[bnum-1] = None
                bnum -= 1
            else:
                if near_rg < 0:
                    near_rg = ((500.0 / (5.0e-10 * scicon.c) -
                                beams[bnum-1].prm.lagfr)
                               / beams[bnum-1].prm.smsep)

                for ff in e.keys():
                    elvs[ff][bnum-1] = e[ff]
                    elv_errs[ff][bnum-1] = eerr[ff]
                    vheights[ff][bnum-1] = vh[ff]
                    vherrs[ff][bnum-1] = verr[ff]
                    hops[ff][bnum-1] = hh[ff]
                    regions[ff][bnum-1] = rr[ff]
    if bnum == 0:
        logging.error("unable to update any beams in this scan")
        return None

    if bnum < len(beams):
        beams.resize(bnum)

    #-------------------------------------------------------------------------
    # To determine the FoV, evaluate the elevation variations across all beams 
    # for a range gate and virtual height band, considering each propagation
    # path (region and hop) seperately.
    min_inc = 0.5 * min(rg_box)
    min_rg = int(min_inc)
    max_rg = hard.maxgate if hard.maxgate < max(rg_max) else max(rg_max)
    max_rg = int(np.ceil(max_rg - min_inc))
    fovbelong = [[{"out":0, "in":0, "mix":0} for r in beams[bi].fit.slist]
                 for bi in range(bnum)]
    fovpast = [[0 for r in beams[bi].fit.slist] for bi in range(bnum)]
    fovflg = [[0 for r in beams[bi].fit.slist] for bi in range(bnum)]
    fovstd = [[100.0 + max_std for r in beams[bi].fit.slist]
              for bi in range(bnum)]
    fovslope = [[0.01 for r in beams[bi].fit.slist] for bi in range(bnum)]
    fovscore = [[max_score + 100.0 for r in beams[bi].fit.slist]
                for bi in range(bnum)]

    for r in np.arange(min_rg, max_rg + 1):
        rgnum = 0
        rgelv = {"front":list(), "back":list()}
        rgvh = {"front":list(), "back":list()}
        rghop = {"front":list(), "back":list()}
        rgreg = {"front":list(), "back":list()}
        rgbi = list()
        rgsi = list()
        rgrg = list()
        ilim = 0
        while ilim < len(rg_max) and r >= rg_max[ilim]:
            ilim += 1

        if ilim >= len(rg_max):
            estr = "range gate [{:d}] is above the allowed maximum [".format(r)
            logging.info("{:s}{:d}]".format(estr, rg_max[-1]))
            continue

        width = np.floor(0.5 * rg_box[ilim])
        rmin = r - int(width)
        rmin = rmin if rmin >= 0 else 0
        rmax = int(r + int(width) + (rg_box[ilim] % 2.0))
        rmax = (rmax if rmax <= hard.maxgate else
                (hard.maxgate if hard.maxgate < max(rg_max) else max(rg_max)))

        # For each beam, load the data for this range gate window
        for bi in range(bnum):
            b = beams[bi]
            for ir in np.arange(rmin, rmax):
                try:
                    si = b.fit.slist.index(ir)
                except:
                    si = -1

                # Only load data if an elevation has been calculated for
                # at least one field-of-view
                if si >= 0 and (not np.isnan(elvs["front"][bi][si]) or
                                not np.isnan(elvs["back"][bi][si])):
                    # Save the data for determining FoV if this value falls
                    # within the desired range
                    if ir >= rmin and ir < rmax:
                        rgbi.append(bi)
                        rgsi.append(si)
                        rgrg.append(ir)

                        goodpath = False
                        for ff in fov.values():
                            rgelv[ff].append(elvs[ff][bi][si])
                            rgvh[ff].append(vheights[ff][bi][si])
                            rghop[ff].append(hops[ff][bi][si])
                            rgreg[ff].append(regions[ff][bi][si])
                            if(not np.isnan(hops[ff][bi][si]) and
                               len(regions[ff][bi][si]) == 1):
                                goodpath = True

                        if goodpath:
                            rgnum += 1

        if rgnum < min_pnts:
            continue

        rgbi = np.array(rgbi)
        rgsi = np.array(rgsi)
        rgrg = np.array(rgrg)
        rgpath = set(["{:.1f}{:s}".format(rghop[ff][ii], reg)
                      for ii,reg in enumerate(rgreg[ff])
                      if len(reg) == 1 and not np.isnan(rghop[ff][ii])
                      for ff in fov.values()])

        for ff in fov.values():
            rgelv[ff] = np.array(rgelv[ff])
            rgvh[ff] = np.array(rgvh[ff])

        # Determine the standard deviation of the elevation for the observations
        # at each virtual height at this range gate window and hop.
        for pp in rgpath:
            hop = float(pp[0:3])
            reg = pp[3:4]

            # Seperate this propagation path into virtual height groups and
            # test the linear regression of the elevation angles
            for ff in fov.keys():
                itest = [it for it,fhop in enumerate(rghop[fov[ff]])
                         if fhop == hop and rgreg[fov[ff]][it] == reg]

                if len(itest) < min_pnts:
                    estr = "insufficient points to determine virtual height "
                    estr = "{:s}limits in the {:s} field-".format(estr, fov[ff])
                    estr = "{:s}of-view for propagation path [".format(estr)
                    estr = "{:s}{:s}] at range gate [{:d}]".format(estr, pp, r)
                    logging.info(estr)
                else:
                    # Establish the virtual height windows
                    vmins, vmaxs = select_alt_groups(rgrg[itest],
                                                     rgvh[fov[ff]][itest],
                                                     region_hmin[reg],
                                                     region_hmax[reg],
                                                     vh_box[ilim], min_pnts)

                    for iv,vmin in enumerate(vmins):
                        # Select the data for this height range
                        velv = list()
                        vbm = list()
                        vrg = list()
                        vih = list()
                        for ih,vh in enumerate(rgvh[fov[ff]][itest]):
                            if(not np.isnan(vh) and vh >= vmin and
                               vh < vmaxs[iv]):
                                velv.append(rgelv[fov[ff]][itest][ih])
                                vbm.append(rgbi[itest][ih])
                                vrg.append(rgrg[itest][ih])
                                vih.append(ih)

                        # See if there are enough beams at this height
                        if len(list(set(vbm))) < min_pnts:
                            estr = "insufficient beams to evaluate "
                            estr = "{:s}{:s} field-of-".format(estr, fov[ff])
                            estr = "{:s}view between [{:.0f}".format(estr, vmin)
                            estr = "{:s}-{:.0f} km] at ".format(estr, vmaxs[iv])
                            estr = "{:s}range gate {:d}".format(estr, r)
                            logging.info(estr)
                        else:
                            # Initialize evaluation statistics to bad values
                            line_std = max_std + 100.0
                            line_dev = [max_std + 100.0 for ee in velv]

                            # Get the linear regression of the elevation
                            # angles as a function of range gate.  The slope
                            # of this line must be flat or negative.
                            # Aliasing will cause positive jumps, but these
                            # should not be present in all boxes, allowing
                            # data to be assigned at times when the aliasing
                            # jump is not present.  A more robust method
                            # (such as RANSAC or Theil-Sen) was not used
                            # since the number of points available are small
                            try:
                                ecoeff = stats.linregress(vrg, velv)
                            except:
                                # If there are not enough points to
                                # perform a linear regression, assume a flat
                                # slope with an intercept given by the mean
                                ecoeff = [0.0, np.nanmean(velv)]

                            if not np.isnan(ecoeff[0]) and ecoeff[0] <= 0.0:
                                lval = np.array([ecoeff[1] + ecoeff[0]
                                                 * rr for rr in vrg])
                                ldev = lval - np.array(velv)
                                lstd = np.nanstd(ldev)
                                lscore = [abs(ss) for ss in stats.zscore(ldev)]

                                # Use the current and past z-scores to
                                # determine whether or not each point is
                                # well characterized by the linear
                                # regression
                                if lstd <= max_std:
                                    for ih,bi in enumerate(vbm):
                                        si = rgsi[itest][vih[ih]]

                                        if(lscore[ih] <= max_score and
                                           lstd <= max_std and
                                           lscore[ih] < fovscore[bi][si]
                                           and lstd <= fovstd[bi][si]):
                                            # If the FoV is changing, record
                                            # that this point also met the
                                            # criteria for the other Fov
                                            if fovflg[bi][si] != ff:
                                                fovpast[bi][si] = fovflg[bi][si]

                                            # Replace if the FoV criteria are
                                            # better, regardless of the FoV
                                            fovflg[bi][si] = ff
                                            fovstd[bi][si] = lstd
                                            fovslope[bi][si] = ecoeff[0]
                                            fovscore[bi][si] = lscore[ih]

    #--------------------------------------------------------------------------
    # Assign FoV to points that have realistic elevation angles in only one
    # FoV.  Also evaluate points that don't have FoV flags due to insufficient
    # data across the range gates.  Evaluate elevation spread using a (possibly)
    # expanded range gate window
    inc_rg_box = 3.0
    for bi in range(bnum):
        if step < 3:
            estr = "not testing backscatter unassigned after performing scan"
            logging.info("{:s}evaluation".format(estr))
            break

        lelv = {"front":np.array(elvs["front"][bi]),
                "back":np.array(elvs["back"][bi])}
        lvh = {"front":np.array(vheights["front"][bi]),
               "back":np.array(vheights["back"][bi])}
        for si,ifov in enumerate(fovflg[bi]):
            if np.isnan(lelv['front'][si]) and np.isnan(lelv['back'][si]):
                continue

            if ifov == 0:
                rg = beams[bi].fit.slist[si]
                # If this point is unassigned, there is only one realistic
                # elevation, and aliasing is unlikely, assign the FoV with the
                # realistic elevation

                if(np.isnan(lelv['front'][si])
                   and not np.isnan(lelv['back'][si]) and rg < near_rg):
                    fovflg[bi][si] = -1
                    fovstd[bi][si] = 0.0
                    fovslope[bi][si] = 0.0
                    fovscore[bi][si] = 0.0
                elif(not np.isnan(lelv['front'][si])
                     and np.isnan(lelv['back'][si]) and rg < near_rg):
                    fovflg[bi][si] = 1
                    fovstd[bi][si] = 0.0
                    fovslope[bi][si] = 0.0
                    fovscore[bi][si] = 0.0
                else:
                    if step < 4:
                        estr = "not assigning backscatter by testing the single"
                        logging.info("{:s} beam variations".format(estr))
                        continue

                    # Examine the surrounding observations along the beam using
                    # an extended range gate window
                    #
                    # Differentiate by hop
                    ilim = 0

                    while(ilim < len(rg_max) and rg >= rg_max[ilim]):
                        ilim += 1

                    if ilim >= len(rg_max):
                        estr = "no guidelines provided for range gate "
                        logging.info("{:s}[{:d}]".format(estr, rg))
                        continue

                    rg_half = (0.5 * (rg_box[ilim] + inc_rg_box))
                    irg_half = int(np.floor(rg_half))
                    min_si = si - irg_half if si >= irg_half else 0
                    max_si = (si + irg_half if si + irg_half < hard.maxgate
                              else (hard.maxgate - 1
                                    if hard.maxgate < max(rg_max)
                                    else max(rg_max) - 1))

                    # Load the front and back elevations for this range gate
                    # and within the extended range gate window
                    for ff in fov.keys():
                        ihop = hops[fov[ff]][bi][si]
                        ireg = regions[fov[ff]][bi][si]
                        test_rg = beams[bi].fit.slist[min_si:max_si]
                        test_si = list()
                        ecoeff = list()
                        lstd = max_std + 100.0
                        lscore = max_score + 100.0

                        if not np.isnan(ihop) and len(ireg) == 1:
                            for ri,r in enumerate(test_rg):
                                rsi = min_si + ri
                                if(hops[fov[ff]][bi][rsi] == ihop and
                                   regions[fov[ff]][bi][rsi] == ireg and
                                   abs(rg - beams[bi].fit.slist[rsi])
                                   <= rg_half):
                                    test_si.append(rsi)

                        if len(test_si) < min_pnts:
                            # If there are not enough points to perform a
                            # comparison continue without assigning a FoV flag
                            if not np.isnan(ihop) and len(ireg) == 1:
                                estr = "not enough points to do single-beam "
                                estr = "{:s}test for the ".format(estr)
                                estr = "{:s}{:s} field-of".format(estr, fov[ff])
                                estr = "{:s}-view for hop [".format(estr)
                                estr = "{:s}{:.1f}{:s}".format(estr, ihop, ireg)
                                estr = "{:s}] beam [{:d}] ".format(estr, bi)
                                estr = "{:s}range gate [{:d}]".format(estr, rg)
                                logging.info(estr)
                        else:
                            test_rg = np.array(beams[bi].fit.slist)[test_si]
                            ri = test_si.index(si)

                            try:
                                ecoeff = stats.linregress(test_rg, \
                                                         lelv[fov[ff]][test_si])
                            except:
                                ecoeff = [0.0,
                                          np.nanmean(lelv[fov[ff]][test_si])]

                            if ecoeff[0] <= 0.0:
                                lval = np.array([ecoeff[1] + ecoeff[0] * rr
                                                 for rr in test_rg])
                                ldev = lval - np.array(lelv[fov[ff]][test_si])
                                lstd = np.nanstd(ldev)
                                lscore = [abs(ss) for ss in stats.zscore(ldev)]

                                # Evaluate the standard deviations and the FoV
                                # of the surrounding points to determine the
                                # FoV for this point
                                if lstd <= max_std:
                                    for ih,ti in enumerate(test_si):
                                        if(lscore[ih] <= max_score and
                                           lstd <= max_std and
                                           lscore[ih] < fovscore[bi][si]
                                           and lstd <= fovstd[bi][si]):
                                            # If the FoV is changing, record
                                            # that this point also met the
                                            # criteria for the other Fov
                                            if fovflg[bi][si] != ff:
                                                fovpast[bi][si] = fovflg[bi][si]

                                            # Replace if this new FoV
                                            # criteria are better, regardless
                                            # of whether or not the FoV changes
                                            fovflg[bi][si] = ff
                                            fovstd[bi][si] = lstd
                                            fovslope[bi][si] = ecoeff[0]
                                            fovscore[bi][si] = lscore[ih]

    #--------------------------------------------------------------------------
    # Evaluate the FoV flags, removing points that are surrounded by data
    # assigned to the opposite FoV.
    for r in np.arange(min_rg, max_rg + 1):
        if step < 5:
            estr = "not testing backscatter assignments with azimuthal "
            logging.info("{:s}continuity".format(estr))
            break

        # Initialize the hop-dependent data
        sihop = {ih:list() for ih in np.arange(0.5, max_hop + 0.5, 0.5)}
        bihop = {ih:list() for ih in np.arange(0.5, max_hop + 0.5, 0.5)}
        fovhop = {ih:list() for ih in np.arange(0.5, max_hop + 0.5, 0.5)}
        reghop = {ih:list() for ih in np.arange(0.5, max_hop + 0.5, 0.5)}

        min_range = hard.maxgate
        max_range = 0
        ilim = 0

        # Calculate the range gate limits
        while ilim < len(rg_max) and r >= rg_max[ilim]:
            ilim += 1

        width = np.floor(0.5 * (rg_box[ilim] + inc_rg_box))
        rm = r - int(width)
        rmin = rm if rm >= 0 else 0
        if rmin < min_range:
            min_range = rmin
        rm = r + int(width + rg_box[ilim] % 2.0)
        rmax = rm if rm <= hard.maxgate else hard.maxgate + 1
        if rmax > max_range:
            max_range = rmax

        # For each beam in the maximum possible range gate window, gather the
        # range gate, FoV flag, beam index, and range gate index for each hop
        for bi in range(bnum):
            b = beams[bi]
            for ir in np.arange(min_range, max_range):
                try:
                    si = b.fit.slist.index(ir)
                except:
                    si = -1

                # Save the data if a FoV flag has been found and the range
                # gate limits are appropriate for the hop
                if si >= 0 and fovflg[bi][si] != 0:
                    ihop = hops[fov[fovflg[bi][si]]][bi][si]
                    ireg = regions[fov[fovflg[bi][si]]][bi][si]
                    if(len(ireg) == 1 and not np.isnan(ihop) and ihop <= max_hop
                       and ir >= rmin and ir < rmax):
                        bihop[ihop].append(bi)
                        sihop[ihop].append(si)
                        fovhop[ihop].append(fovflg[bi][si])
                        reghop[ihop].append(ireg)

        # Determine the fraction of each points in the front and back Fov for
        # azimuthally constraints (beam limits) added to the previous limits.
        # If there are an overwhelming number of points in one FoV, remove
        # all FoV flags from the points in the other Fov.
        for ihop in fovhop.keys():
            for ireg in set(reghop[ihop]):
                rind = [ii for ii,rr in enumerate(reghop[ihop]) if rr == ireg]
                # If there are sufficient points, evaluate the data at this hop
                if len(rind) > min_pnts:
                    # Evaluate the data in an azimuthal box
                    for bi in set(np.array(bihop[ihop])[rind]):
                        # Determine the azimuthal limits
                        bmnum = beams[bi].bmnum
                        bwidth = int(min_pnts * 0.75)
                        bmin = bmnum - bwidth if bmnum >= min_pnts else 0
                        if bmnum <= hard.maxbeam - bwidth:
                            bmax = bmnum + bwidth
                        else:
                            bmax = hard.maxbeam

                        ibeam = [ii for ii in rind
                                 if(beams[bihop[ihop][ii]].bmnum >= bmin and
                                    beams[bihop[ihop][ii]].bmnum < bmax)]

                        bad_fov = 0
                        good_fov = False
                        if len(ibeam) > min_pnts:
                            # Sum the points in this box
                            fn = sum([1 for ff in np.array(fovhop[ihop])[ibeam]
                                      if ff == 1])
                            bn = sum([1 for ff in np.array(fovhop[ihop])[ibeam]
                                      if ff == -1])
                        else:
                            fn = 0
                            bn = 0

                        if fn + bn > 0:
                            ffrac = float(fn) / float(fn + bn)
                            if ffrac >= fov_frac and bn > 0:
                                bad_fov = -1
                                good_fov = True
                            elif (1.0 - ffrac) >= fov_frac and fn > 0:
                                bad_fov = 1
                                good_fov = True

                        # Tag all points whose FoV are or are not consistent
                        # with the observed structure at this hop
                        for ff,ifov in enumerate(np.array(fovhop[ihop])[ibeam]):
                            ii = ibeam[ff]
                            si = sihop[ihop][ii]
                            ci = bihop[ihop][ii]
                            if good_fov:
                                if ifov != bad_fov:
                                    # This point is associated with a structure
                                    # that is predominantly the same FoV
                                    fovbelong[ci][si]["in"] += 1
                                else:
                                    # If this point is not associated with a
                                    # structure that is predominately the same
                                    # FoV and this is not the only FoV capable
                                    # of producing a realistic elevation angle,
                                    # flag this point as an outlier
                                    ir = beams[ci].fit.slist[si]
                                    if(not (np.isnan(elvs[fov[-ifov]][ci][si])
                                            and ir < near_rg)):
                                        fovbelong[ci][si]["out"] += 1
                            else:
                                fovbelong[ci][si]["mix"] += 1

    # If any points have been flagged as outliers, remove or change their FoV
    for bi in range(bnum):
        # Break this loop if no continuity tests are desired
        if step < 5:
            break

        for si,bdict in enumerate(fovbelong[bi]):
            if bdict["out"] > 0 and bdict["in"] < bdict["out"] + bdict["mix"]:
                # This point is an outlier in a structure with the opposite FoV.
                # If this point fit the criteria for the other FoV in the past,
                # assign that FoV.  Otherwise remove any FoV assignment.
                if bdict['out'] > bdict['mix'] and bdict['out'] > bdict['in']:
                    fovflg[bi][si] = fovpast[bi][si]
                else:
                    fovflg[bi][si] = 0
                fovpast[bi][si] = 0

                estr = "field-of-view is not consistent with the observed "
                estr = "{:s}structure at hop [{:.1f}".format(estr, ihop)
                estr = "{:s}{:s}] beam [".format(estr, ireg)
                estr = "{:s}{:d}] range gate [".format(estr, beams[bi].bmnum)
                estr = "{:s}{:d}]".format(estr, beams[bi].fit.slist[si])
                logging.info(estr)

    #--------------------------------------------------------------------------
    # Assign the appropriate virtual heights and elevation angles to each
    # point based on their FoV.  Also assign initial regions based on virtual
    # height
    for bi in range(bnum):
        snum = len(beams[bi].fit.slist)
        beams[bi].fit.region = ["" for si in range(snum)]
        beams[bi].fit.hop = [np.nan for si in range(snum)]
        beams[bi].fit.vheight = [np.nan for si in range(snum)]
        beams[bi].fit.vheight_e = [np.nan for si in range(snum)]
        beams[bi].fit.fovelv = [np.nan for si in range(snum)]
        beams[bi].fit.fovelv_e = [np.nan for si in range(snum)]
        beams[bi].fit.fovflg = fovflg[bi]

        for si,ifov in enumerate(beams[bi].fit.fovflg):
            if ifov == 0 or np.isnan(ifov):
                # Default to front FoV if none was found
                beams[bi].fit.fovelv[si] = elvs["front"][bi][si]
                beams[bi].fit.vheight[si] = vheights["front"][bi][si]
                beams[bi].fit.hop[si] = hops["front"][bi][si]
                beams[bi].fit.region[si] = regions["front"][bi][si]
            else:
                # Assign the appropriate FoV
                beams[bi].fit.region[si] = regions[fov[ifov]][bi][si]
                beams[bi].fit.hop[si] = hops[fov[ifov]][bi][si]
                beams[bi].fit.vheight[si] = vheights[fov[ifov]][bi][si]
                beams[bi].fit.vheight_e[si] = vherrs[fov[ifov]][bi][si]
                beams[bi].fit.fovelv_e[si] = elv_errs[fov[ifov]][bi][si]
                beams[bi].fit.fovelv[si] = elvs[fov[ifov]][bi][si]
        # Additional values returned for use in analysis and UT continuity test
        beams[bi].fit.felv = elvs["front"][bi]
        beams[bi].fit.felv_e = elv_errs["front"][bi]
        beams[bi].fit.belv = elvs["back"][bi]
        beams[bi].fit.belv_e = elv_errs["back"][bi]
        beams[bi].fit.fvheight = vheights["front"][bi]
        beams[bi].fit.fvheight_e = vherrs["front"][bi]
        beams[bi].fit.bvheight = vheights["back"][bi]
        beams[bi].fit.bvheight_e = vherrs["back"][bi]
        beams[bi].fit.fhop = hops["front"][bi]
        beams[bi].fit.bhop = hops["back"][bi]
        beams[bi].fit.fregion = regions["front"][bi]
        beams[bi].fit.bregion = regions["back"][bi]
        beams[bi].fit.pastfov = fovpast[bi]

    return beams

#-------------------------------------------------------------------------
def update_beam_fit(beam, hard=None,
                    region_hmax={"D":115.0,"E":150.0,"F":900.0},
                    region_hmin={"D":75.0,"E":115.0,"F":150.0}, max_hop=3.0,
                    ptest=True, strict_gs=False, bmaz_e=0.0, boresite_e=0.0,
                    ix_e=0.0, iy_e=0.0, iz_e=0.0):
    """Update the beam.fit and beam.prm class, updating and adding attributes
    needed for common data analysis.

    Currently the earth radius error and slant distance error have no update
    option through this routine and are identically zero.

    Parameters
    ------------
    beam : (class `sdio.radDataTypes.beamData`)
       Radar data for a specific beam
    hard : (class `pydarn.radar.radStruct.site` or NoneType)
       Hardware information for this radar.  Will load if not supplied.
       (default=None)
    region_hmax : (dict)
        Maximum virtual heights allowed in each ionospheric layer.
        (default={"D":115.0,"E":150.0,"F":400.0})
    region_hmin : (dict)
        Minimum virtual heights allowed in each ionospheric layer.
        (default={"D":75.0,"E":115.0,"F":150.0})
    max_hop : (float)
        The maximum allowable hop to be considered physical. (default=2.0)
    ptest : (boolian)
        Perform test to see if propagation modes are realistic? (default=True)
    strict_gs : (boolian)
        Remove indeterminately flagged backscatter (default=False)
    bmaz_e : (float)
        Error in beam azimuth in degrees (default=0.0)
    boresite_e : (float)
        Error in the boresite location in degrees (default=0.0)
    ix_e : (float)
        Error in the interferometer x coordinate in meters (default=0.0)
    iy_e : (float)
        Error in the interferometer y coordinate in meters (default=0.0)
    iz_e : (float)
        Error in the interferometer z coordinate in meters (default=0.0)

    Returns
    ---------
    return beam, elvs, elv_errs, vheights, vherrs, hops, regions, hard

    beam : (class beamData)
        Updated beamDAta class object.  The beam as the following additional
        or adjusted attributes:
        beam.fit.gflg : updated : Flag indicating backscatter type
                                  (1=ground, 0=ionospheric, -1=indeterminate)
        beam.prm.tdiff : possibly updated : tdiff used in elevation (microsec)
        beam.prm.tdiff_e : possibly updated : tdiff error (microsec)
    elvs : (dict)
        Elevation angles for the front "front" and rear "back" FoV
    elv_errs : (dict)
        Elevation angle errors for the front "front" and rear "back" FoV.
        There is currently no method for calculating these errors from the
        fit data, so np.nan will be returned in all cases.
    vheights : (dict)
        Virtual heights for the front "front" and rear "back" FoV
    vherrs : (dict)
        Virtual height errors for the front "front" and rear "back" FoV.
        There is currently no method for calculating these errors from the
        fit data, so np.nan will be returned in all cases.
    hops : (dict)
        Hops for the front "front" and rear "back" FoV
    regions : (dict)
        Ionospheric regions for the front "front" and rear "back" FoV
    hard : (class `pydarn.radar.radStruct.site`)
        Radar hardware data for this scan
    """
    import davitpy.pydarn.sdio as sdio
    import davitpy.pydarn.radar as pyrad
    import davitpy.utils.geoPack as geo
    import davitpy.pydarn.proc.fov.calc_elevation as ce
    import davitpy.pydarn.proc.fov.calc_height as ch

    #----------------------------------
    # Test input
    if not isinstance(region_hmin, dict) or min(region_hmin.values()) < 0.0:
        estr = 'unknown minimum virtual heights [{:}]'.format(region_hmin)
        logging.error(estr)
        return beam, None, None, None, None, None, None, None

    if not isinstance(region_hmax, dict):
        estr = 'unknown maximum virtual heights [{:}]'.format(region_hmax)
        logging.error(estr)
        return beam, None, None, None, None, None, None, None
 
    if isinstance(max_hop, int):
        max_hop = float(max_hop)
    if not isinstance(max_hop, float) or max_hop < 0.5:
        logging.error('maximum hop must be a float greater than 0.5')
        return beam, None, None, None, None, None, None, None

    if beam is None or beam.fit.slist is None or len(beam.fit.slist) <= 0:
        logging.warning("no fit data in beam at {:}".format(beam.time))
        return beam, None, None, None, None, None, None, None

    #-----------------------------------
    # Initialize FoV dependent values
    slist = getattr(beam.fit, "slist")
    elvs_aliased = {"front":[np.nan for s in slist],
                    "back":[np.nan for s in slist]}
    elva_errs = {"front":[np.nan for s in slist],
                 "back":[np.nan for s in slist]}
    elvs = {"front":[np.nan for s in slist], "back":[np.nan for s in slist]}
    elv_errs = {"front":[np.nan for s in slist], "back":[np.nan for s in slist]}
    vheights = {"front":[np.nan for s in slist], "back":[np.nan for s in slist]}
    vheights_aliased = {"front":[np.nan for s in slist],
                        "back":[np.nan for s in slist]}
    vheighta_errs = {"front":[np.nan for s in slist],
                     "back":[np.nan for s in slist]}
    vherrs = {"front":[np.nan for s in slist], "back":[np.nan for s in slist]}
    hops = {"front":[0.5 for s in slist], "back":[0.5 for s in slist]}
    regions = {"front":["" for s in slist], "back":["" for s in slist]}

    # Initialize local constants
    vmin = min(region_hmin.values())
    vmax = max(region_hmax.values())

    #------------------------------------------------------------------------
    # Load the radar hardware data and calculate hardware specific variables,
    # if it hasn't been done already
    if hard is None:
        try:
            hard = pyrad.site(radId=beam.stid, dt=beam.time)
        except:
            estr = "unable to load hardware data for radar "
            estr = "{:s}{:d} at {:}".format(estr, beam.stid, beam.time)
            logging.warning(estr)
            return beam, elvs, elv_errs, vheights, vherrs, None, None, None

    # Use the geodetic/geocentric conversion to get the terrestrial radius at
    # the radar location (same in both coordinate systems)
    (lat, lon, radius) = geo.geodToGeoc(hard.geolat, hard.geolon, False)

    # Calculate the 0.5 hop distance and initialize the hop list
    dlist = calc_distance(beam)
    dist = {'front':np.array(dlist), "back":np.array(dlist)}
    # Update the groundscatter flag (both distances are the same)
    gflg = select_beam_groundscatter(beam, dist['front'], max_rg=hard.maxgate)

    for i,g in enumerate(beam.fit.gflg):
        if g == 1:
            try:
                gflg.index(i)

                # If this is groundscatter, update the distance and the hop
                hops['front'][i] = 1.0
                hops['back'][i] = 1.0
                dist['front'][i] *= 0.5
                dist['back'][i] *= 0.5
            except:
                # This point was found not to be groundscatter.  It is probably
                # slow moving ionospheric backscatter, so treat it like
                # ionospheric backscatter but change the flag to let the user
                # know that it was not flagged by the initial ionospheric
                # backscatter test
                beam.fit.gflg[i] = -1

                if strict_gs:
                    hops['front'][i] = np.nan
                    hops['back'][i] = np.nan
                    dist['front'][i] = np.nan
                    dist['back'][i] = np.nan

        # Remove backscatter with negative power estimates
        if beam.fit.p_l[i] < 0.0 or beam.fit.p_s[i] < 0.0:
            hops['front'][i] = np.nan
            hops['back'][i] = np.nan
            dist['front'][i] = np.nan
            dist['back'][i] = np.nan

    # Calculate the elevation angles for the front and rear FoV, after
    # initializing the beam parameters with the supplied tdiff
    if not hasattr(beam.prm, "tdiff") or beam.prm.tdiff is None:
        beam.prm.tdiff = hard.tdiff

    if not hasattr(beam.prm, "tdiff_e") or beam.prm.tdiff_e is None:
        beam.prm.tdiff_e = np.nan

    for ff in ["front", "back"]:
        # Calculate the elevation
        try:
            (elvs[ff], elv_errs[ff], pamb,
             hard) = ce.calc_elv_w_err(beam, hard=hard, bmaz_e=bmaz_e,
                                       boresite_e=boresite_e, ix_e=ix_e,
                                       iy_e=iy_e, iz_e=iz_e,
                                       tdiff=beam.prm.tdiff,
                                       tdiff_e=beam.prm.tdiff_e, fov=ff)
            (elvs_aliased[ff], elva_errs[ff], pamb,
             hard) = ce.calc_elv_w_err(beam, hard=hard, bmaz_e=bmaz_e,
                                       boresite_e=boresite_e, ix_e=ix_e,
                                       iy_e=iy_e, iz_e=iz_e,
                                       tdiff=beam.prm.tdiff, alias=1.0, fov=ff)
        except:
            estr = "can't get elevation for beam {:d} at {:}".format(beam.bmnum,
                                                                     beam.time)
            logging.info(estr)
            elvs[ff] = None

        if elvs[ff] is not None:
            # Get the virtual height and virtual height error
            vheights[ff], vherrs[ff] = \
                ch.calc_virtual_height_w_err(beam, radius, elv=elvs[ff],
                                             elv_e=elv_errs[ff], dist=dist[ff],
                                             dist_e=[0.0 for dd in dist[ff]],
                                             dist_units="km")
            vheights_aliased[ff], vheighta_errs[ff] = \
                ch.calc_virtual_height_w_err(beam, radius, elv=elvs_aliased[ff],
                                             elv_e=elva_errs[ff], dist=dist[ff],
                                             dist_e=[0.0 for dd in dist[ff]],
                                             dist_units="km")

            # Test the virtual height
            for i,vh in enumerate(vheights[ff]):
                if not np.isnan(vh) and vh < vmin:
                    # This height is too low.  Replace it with a value corrected
                    # with a 2 pi alias or remove it from consideration for
                    # this FoV
                    if vheights_aliased[ff][i] < vmin:
                        elvs[ff][i] = elvs_aliased[ff][i]
                        elv_errs[ff][i] = elva_errs[ff][i]
                        vheights[ff][i] = vheights_aliased[ff][i]
                        vherrs[ff][i] = vheighta_errs[ff][i]
                    else:
                        elvs[ff][i] = np.nan
                        vheights[ff][i] = np.nan
                    vh = vheights[ff][i]
                vhe = vherrs[ff][i]

                if not np.isnan(vh):
                    hop = hops[ff][i]
                    dd = dlist[i] * 0.5 / hop
                    ghop = True
                    while vh > vmax and hop <= max_hop:
                        # This height is too high.  Increase the hop
                        # number to acheive a realistic value
                        hop += 1.0
                        dd = dlist[i] * 0.5 / hop
                        vout = ch.calc_virtual_height_w_err(beam, radius, \
                                    elv=[elvs[ff][i]], elv_e=[elv_errs[ff][i]],\
                                    dist=[dd], dist_e=[0.0], dist_units="km")
                        vh = vout[0][0]
                        vhe = vout[1][0]

                    # Test the distance and hop to ensure that this
                    # mode is realistic
                    if ptest:
                        ghop = test_propagation(hop, vh, dd,
                                                region_hmax=region_hmax,
                                                region_hmin=region_hmin)

                    if not ghop:
                        # If this is not a valid propagation path, attempt to
                        # use the elevation angle with a 2pi alias added
                        ea = elvs_aliased[ff][i]
                        ee = elva_errs[ff][i]
                        vh = vheights_aliased[ff][i]
                        vhe = vheighta_errs[ff][i]
                        hop = 1.0 if beam.fit.gflg[i] == 1 else 0.5
                        dd = dlist[i] * 0.5 / hop
                        while vh > vmax and hop <= max_hop:
                            # This height is too high.  Increase the hop
                            # number to acheive a realistic value
                            hop += 1.0
                            dd = dlist[i] * 0.5 / hop
                            vout = ch.calc_virtual_height_w_err(beam, radius, \
                                                                elv=[ea],
                                                                elv_e=[ee], \
                                    dist=[dd], dist_e=[0.0], dist_units="km")
                            vh = vout[0][0]
                            vhe = vout[1][0]
                        
                        if vh >= vmin:
                            ghop = test_propagation(hop, vh, dd,
                                                    region_hmax=region_hmax,
                                                    region_hmin=region_hmin)
                    else:
                        ea = elvs[ff][i]
                        ee = elv_errs[ff][i]

                    if hop <= max_hop and ghop:
                        # Update the lists
                        hops[ff][i] = hop
                        dist[ff][i] = dd
                        vheights[ff][i] = vh
                        vherrs[ff][i] = vhe
                        elvs[ff][i] = ea
                        elv_errs[ff][i] = ee
                        regions[ff][i] = assign_region(vh,
                                                       region_hmax=region_hmax,
                                                       region_hmin=region_hmin)
                    else:
                        # Unable to calculate a realistic virtual
                        # height within a sane number of hops, even accounting
                        # for possible aliasing
                        hops[ff][i] = np.nan
                        elvs[ff][i] = np.nan
                        vheights[ff][i] = np.nan
        else:
            hops[ff] = [np.nan for r in slist]
            elvs[ff] = [np.nan for r in slist]
            vheights[ff] = [np.nan for r in slist]

    return beam, elvs, elv_errs, vheights, vherrs, hops, regions, hard

#---------------------------------------------------------------------------
def update_backscatter(rad_bms, min_pnts=3,
                       region_hmax={"D":115.0,"E":150.0,"F":900.0},
                       region_hmin={"D":75.0,"E":115.0,"F":150.0},
                       rg_box=[2,5,10,20], vh_box=[50.0,50.0,50.0,150.0],
                       max_rg=[5,25,40,76], max_hop=3.0,
                       ut_box=dt.timedelta(minutes=20.0), tdiff=None,
                       tdiff_args=list(), tdiff_e=None, tdiff_e_args=list(),
                       ptest=True, strict_gs=False, bmaz_e=0.0, boresite_e=0.0,
                       ix_e=0.0, iy_e=0.0, iz_e=0.0, step=6):
    """Updates the propagation path, elevation, backscatter type, and origin
    field-of-view (FoV) for all backscatter observations in each beam.  Scans
    of data are used to determine the origin field-of-view (FoV), but a full
    scan is not necessary, but if the number of beams is less than the specified
    minimum, a less rigerous evaluation method is used.

    Parameters
    -------------
    rad_bms : (list or class `pydarn.sdio.radDataTypes.radDataPtr`)
        A list of or pointer to beamData class objects
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
    max_hop : (list of floats)
        Maximum hop that the corresponding rg_box and vh_box values applies
        to.  (default=3.0)
    ut_box : (class `dt.timedelta`)
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
    strict_gs : (boolian)
        Remove indeterminately flagged backscatter (default=False)
    bmaz_e : (float)
        Error in beam azimuth in degrees (default=0.0)
    boresite_e : (float)
        Error in the boresite location in degrees (default=0.0)
    ix_e : (float)
        Error in the interferometer x coordinate in meters (default=0.0)
    iy_e : (float)
        Error in the interferometer y coordinate in meters (default=0.0)
    iz_e : (float)
        Error in the interferometer z coordinate in meters (default=0.0)
    step : (int)
        Integer denoting the number of processing steps to perform.  This should
        always be set to 6 (or greater) unless one wishes to reproduce the
        demonstration plots in Burrell et al (2015). (default=6)  The step
        numbers coincide with those indicated in the paper:
        1 or 2: Examine the elevation structure across each scan
        3: Add assignments for points with realistic heights in only one FoV
        4: Add assignments using single-beam elevation angle variations
        5 or more: Test assignements for consistency along the scan.

    Returns
    ---------
    beams : (list)
        A dictionary of updated beamData class objects.  The dictionary keys
        correspond to the beam numbers, and contain np.arrays of beams sorted
        by UT with the following additional/updated attributes

        beam.fit.fovelv : added : Accounts for adjusted tdiff and origin FoV
        beam.fit.fovelv_e : added : elevation error
        beam.fit.felv : added : Elevation angle assuming front FoV
        beam.fit.felv_e : added : Elevation angle error assuming front FoV
        beam.fit.belv : added : Elevation angle assuming rear FoV
        beam.fit.belv_e : added : Elevation angle error assuming front FoV
        beam.fit.vheight : added : virtual height of ionosphere in km
        beam.fit.vheight_e : added : error in virtual height (km)
        beam.fit.fvheight : added : virtual height assuming front FoV
        beam.fit.fvheight_e : added : error in virtual height assuming front FoV
        beam.fit.bvheight : added : virtual height assuming rear FoV
        beam.fit.bvheight_e : added : error in virtual height assuming rear FoV
        beam.fit.hop : added : Hop assuming the assigned origin FoV
        beam.fit.fhop : added : Hop assuming the front FoV
        beam.fit.bhop : added : Hop assuming the rear FoV
        beam.fit.region : added : Region assuming the assigned origin FoV
        beam.fit.fregion : added : Region assuming the front FoV
        beam.fit.bregion : added : Region assuming the rear FoV
        beam.fit.fovflg : added : Flag indicating origin FoV (1=front, -1=back,
                                  0=indeterminate)
        beam.fit.pastfov : added : Flag indicating past FoV assignments
        beam.fit.gflg : updated : Flag indicating backscatter type
                                  (1=ground, 0=ionospheric, -1=indeterminate)
        beam.prm.tdiff : added : tdiff used in elevation (microsec)
        beam.prm.tdiff_e : possibly added : tdiff error (microsec)

    If the input is incorrect, exits with an exception
    """
    import davitpy.pydarn.sdio as sdio
    import davitpy.pydarn.radar as pyrad

    #----------------------------------
    # Test input
    assert(((isinstance(rad_bms, list) or isinstance(rad_bms, np.ndarray)) and
            isinstance(rad_bms[0], sdio.radDataTypes.beamData)) or
            isinstance(rad_bms, sdio.radDataTypes.radDataPtr)), \
        logging.error('need a list/array of beams or a radar data pointer')
    if isinstance(min_pnts, float):
        min_pnts = int(min_pnts)
    assert isinstance(min_pnts, int) and min_pnts >= 0, \
        logging.error('unknown point minimum [{:}]'.format(min_pnts))
    assert isinstance(region_hmin, dict) and min(region_hmin.values()) >= 0.0, \
        logging.error("unknown minimum h' [{:}]".format(region_hmin))
    assert isinstance(region_hmax, dict), \
        logging.error("unknown maximum h' [{:}]".format(region_hmax))
    assert((isinstance(rg_box, list) or isinstance(rg_box, np.ndarray))
           and min(rg_box) >= 1.0), \
        logging.error('range gate box is too small [{:}]'.format(rg_box))
    assert((isinstance(vh_box, list) or isinstance(vh_box, np.ndarray))
            and min(vh_box) >= 0.0), \
        logging.error('virtual height box is too small [{:}]'.format(vh_box))
    assert((isinstance(max_rg, list) or isinstance(max_rg, np.ndarray))
           and min(max_rg) >= 0), \
        logging.error('max range gate box is too small [{:}]'.format(max_rg))
    if isinstance(max_hop, int):
        max_hop = float(max_hop)
    assert isinstance(max_hop, float) and max_hop >= 0.5, \
        logging.error('hop limits are unrealistic [{:}]'.format(max_hop))
    assert isinstance(ut_box, dt.timedelta) and ut_box.total_seconds() > 0.0, \
        logging.error('UT box must be a positive datetime.timdelta object')
    if isinstance(step, float):
        step = int(step)
    assert isinstance(step, int), logging.error('step flag must be an int')

    #-----------------------------------------------------------------------
    # Cycle through all the beams
    snum = 0
    num = 0
    bm, num = get_beam(rad_bms, num)
    max_del_beam = 3
    have_scan = False

    # Load the hardware data for the first time
    try:
        hard = pyrad.site(radId=bm.stid, dt=bm.time)
    except:
        logging.error("no data available in input rad structure")
        return None

    #----------------------------------------------------------------
    # Cycle through the data, updating the beams one scan at a time
    scan = np.empty(shape=(hard.maxbeam,), dtype=type(bm))
    beams = list()

    while bm is not None:
        # Load the beam into the current scan if the scan is empty or if
        # the current beam is within a specified period of time considering
        # the difference in beams
        if snum == 0:
            bm.scan_time = bm.time
            scan[snum] = bm
            snum += 1
            bm_sign = 0
        else:
            del_time = (bm.time - scan[snum-1].time).total_seconds()
            del_beam = bm.bmnum - scan[snum-1].bmnum
            time_inc = bm.prm.inttsc + bm.prm.inttus * 1.0e-6

            if(del_beam != 0 and bm.cp == scan[0].cp and
               del_time <= 3.0 * abs(del_beam) * time_inc and
               abs(del_beam) <= max_del_beam):
                if bm_sign == 0 or bm_sign == np.sign(del_beam):
                    bm_sign = np.sign(del_beam)
                    bm.scan_time = scan[0].time
                    scan[snum] = bm
                    snum += 1
                else:
                    have_scan = True
            else:
                have_scan = True

            #-----------------------------------------------------------------
            # If a scan has been loaded, update the backscatter data in the
            # beams and load the current beam as the first element of a new scan
            if have_scan:
                if snum >= min_pnts:
                    st = scan[0].time
                    b = update_bs_w_scan(scan[0:snum], hard, min_pnts=min_pnts,
                                         region_hmax=region_hmax,
                                         region_hmin=region_hmin,
                                         rg_box=rg_box, vh_box=vh_box,
                                         rg_max=max_rg, max_hop=max_hop,
                                         tdiff=tdiff, tdiff_args=tdiff_args,
                                         tdiff_e=tdiff_e,
                                         tdiff_e_args=tdiff_e_args, ptest=ptest,
                                         strict_gs=strict_gs, bmaz_e=bmaz_e,
                                         boresite_e=boresite_e, ix_e=ix_e,
                                         iy_e=iy_e, iz_e=iz_e, step=step)

                    if b is not None:
                        beams.extend(list(b))
                    else:
                        logging.info("unable to update scan at {:}".format(st))

                bm.scan_time = bm.time
                scan[0] = bm
                snum = 1
                bm_sign = 0
                have_scan = False

        # Cycle to next beam
        bm, num = get_beam(rad_bms, num)

    #---------------------------------------------------------------------
    # Once the scans have been loaded, beam-UT tests of the FoV flags can
    # be performed
    inc_rg_box = 3
    beam_dict = beam_ut_struct_test(beams, frg_box=np.array(rg_box)+inc_rg_box,
                                    max_rg=max_rg, ut_box=ut_box,
                                    reg_attr="region", hop_attr="hop",
                                    fov_attr="fovflg", step=step)

    return(beam_dict)

def beam_ut_struct_test(rad_bms, min_frac=.10, frg_box=[5,8,13,23],
                        max_rg=[5,25,40,76], ut_box=dt.timedelta(minutes=20.0),
                        reg_attr="region", hop_attr="hop", fov_attr="fovflg",
                        restrict_attr=[], restrict_lim=[], step=6):
    """Routine to test for field-of-view (FoV) and structure continuity in UT
    across each beam. Hop (or groundscatter flag) will be used to seperate
    structure types. 

    Parameters
    -----------
    rad_bms : (list or class `sdio.radDataTypes.radDataPtr`)
        List of or pointer to beam data
    min_frac : (float)
        Minimum fraction of possible backscatter points needed in the RG/UT
        box to perform the FoV calculation (default=.1)
    frg_box : (list, np.array)
        Total width of range gate box to examine for backscatter FoV
        continuity.  (default=[5,8,13,23])
    ut_box : (class `dt.timedelta`)
        Total width of universal time box to examine for backscatter FoV
        continuity. (default=20.0 minutes)
    reg_attr : (string)
        beam.fit attribute name to seperate different ionospheric regions.
        Can discard by entering nothing. (default="region")
    hop_attr : (string)
        beam.fit attribute name to seperate different structure types.  Designed
        to use either the groundscatter flag or the hop data. (default="hop")
    fov_attr : (string)
        beam.fit attribute name of the FoV flag
    restrict_attr : (list)
        List containing strings with attribute names.  Used to restrict the
        consideration further, such as by virtual height or slant path distance
        from the radar to the first ionospheric reflection point.  An empty list
        means no additional restrictions are desired. (default=[])
    restrict_lim : (list)
        List containing two-element lists with the minimum and maximum values
        of the restriction limits for the attributes contained in restrict_attr.
        (default=[])
    step : (int)
        Integer denoting the number of processing steps to perform.  This should
        always be set to 6 (or greater) unless one wishes to reproduce the
        demonstration plots in Burrell et al (2015). (default=6)  The step
        numbers coincide with those indicated in the paper:
        1-5: Examine the elevation structure and consistency along the scan
        6: Test for temporal consistency

    Returns
    ----------
    beams : (dict)
        Dictionary containing lists of beams with updated FoV flags seperated
        by beam number.  The beam numbers are the dictionary keys
    """
    import davitpy.pydarn.sdio as sdio
    import davitpy.pydarn.radar as pyrad
    fov_frac = 2.0 / 3.0
    near_rg = -1

    #----------------------------
    # Initialize the output
    beams = dict()

    #----------------------------------
    # Test input
    if(not isinstance(rad_bms, list) and
       not isinstance(rad_bms, sdio.radDataTypes.radDataPtr)):
        logging.error('need a list of beams or a radar data pointer')
        return beams

    if(isinstance(rad_bms, list) and
       (len(rad_bms) <= 0 or not isinstance(rad_bms[0],
                                            sdio.radDataTypes.beamData))):
        logging.error('list must contain at least one beam')
        return beams

    if isinstance(min_frac, int):
        min_frac = float(min_frac)
    if not isinstance(min_frac, float) or min_frac <= 0.0 or min_frac > 1.0:
        estr = 'unrealistic minimum FoV fraction [{:}]'.format(min_frac)
        logging.error(estr)
        return beams

    if((not isinstance(frg_box, list) and not isinstance(frg_box, np.ndarray))
       or len(frg_box) <= 0):
        estr = 'unrealistic FoV range gate box [{:}]'.format(frg_box)
        logging.error(estr)
        return beams

    if((not isinstance(max_rg, list) and not isinstance(max_rg, np.ndarray))
       or len(max_rg) <= 0):
        estr = 'unrealistic maximum range gate box [{:}]'.format(max_rg)
        logging.error(estr)
        return beams

    if not isinstance(ut_box, dt.timedelta) or ut_box.total_seconds() <= 0.0:
        logging.error('unrealistic UT box [{:}]'.format(ut_box))
        return beams

    if not isinstance(restrict_attr, list):
        logging.error('provide more restricting attributes in a list')
        return beams

    if not isinstance(restrict_lim, list):
        logging.error('provide more restricting limits in a list')
        return beams

    if isinstance(step, float):
        step = int(step)
    if not isinstance(step, int):
        logging.error('unrealistic step flag [{:}]'.format(step))
        return beams

    if not isinstance(reg_attr, str) or len(reg_attr) <= 0:
        logging.error('badly formated region attribute [{:}]'.format(reg_attr))
        return beams

    if not isinstance(hop_attr, str) or len(reg_attr) <= 0:
        logging.error('badly formated hop attribute [{:}]'.format(hop_attr))
        return beams

    if not isinstance(fov_attr, str) or len(reg_attr) <= 0:
        estr = 'badly formated FoV flag attribute [{:}]'.format(fov_attr)
        logging.error(estr)
        return beams

    #-----------------------------------------------------------------------
    # Load the first beam and initialize limits
    num = 0
    bm, num = get_beam(rad_bms, num)
    rhalf = [int(r * 0.5) for r in frg_box]

    try:
        hard = pyrad.site(radId=bm.stid, dt=bm.time)
    except:
        logging.error("no data available in input rad structure")
        return(beams)

    while bm is not None:
        bnum = bm.bmnum

        if near_rg < 0:
            near_rg = ((500.0 / (5.0e-10 * scicon.c) - bm.prm.lagfr)
                       / bm.prm.smsep)

        # Load the beams into the output dictionary
        if beams.has_key(bnum):
            beams[bnum].append(bm)
        else:
            beams[bnum] = [bm]

        # Cycle to the next beam
        bm, num = get_beam(rad_bms, num)

    #-----------------------------------------------------------------------
    # Test the step flag and see if the temporal continuity test should be
    # performed
    if step < 6:
        estr = "not testing backscatter assignments with temporal continuity"
        logging.info(estr)
        return(beams)

    #-----------------------------------------------------------------------
    # Cycle through all the beams, updating the FoV flag and structure flag
    # once enough data has been loaded
    for bnum in beams.keys():
        bis = 0
        fovbelong = [[{"out":0, "in":0, "mix":0}
                      for j in beams[bnum][i].fit.slist]
                     for i in np.arange(0, len(beams[bnum]))]
        fovpast = [[j for j in beams[bnum][i].fit.pastfov]
                   for i in np.arange(0, len(beams[bnum]))]
        for i in np.arange(0, len(beams[bnum])):
            # See if there is enough data at this beam to begin the evaluation
            while beams[bnum][i].time - beams[bnum][bis].time >= ut_box:
                # Check the common program of each of the beams.  For a UT
                # comparision, the cp must be the same for all beams
                bicp = [bis + j for j,b in enumerate(beams[bnum][bis:i])
                        if(b.cp == beams[bnum][bis].cp and
                           b.time - beams[bnum][bis].time < ut_box)]

                # Test to see if there is enough data to fill the time window
                if beams[bnum][i].time - beams[bnum][bis].time < ut_box:
                    break

                # Get the range gate, FoV flag, hop, beam index, and range
                # gate index for all backscatter points at these beams
                rgates = list()
                fovflg = list()
                onefov = list()
                hops = list()
                regions = list()
                bi = list()
                ri = list()
                rdata = dict()
                for rattr in restrict_attr:
                    rdata[rattr] = list()

                for bb in bicp:
                    b = beams[bnum][bb]

                    # Load data from the beam, if it exists
                    if(b.fit is not None and hasattr(b.fit, "slist") and
                       hasattr(b.fit, fov_attr) and hasattr(b.fit, hop_attr)):
                        slist = getattr(b.fit, "slist")
                        rgates.extend(slist)
                        bi.extend([bb for j in slist])
                        ri.extend([j for j,r in enumerate(slist)])
                        fflg = getattr(b.fit, fov_attr)
                        fovflg.extend(fflg)
                        otherelv = [b.fit.felv[oe] if ff == -1 else
                                    b.fit.belv[oe] for oe,ff in enumerate(fflg)]
                        onefov.extend([np.isnan(oe) if slist[j] < near_rg
                                       else False
                                       for j,oe in enumerate(otherelv)])
                        hops.extend(getattr(b.fit, hop_attr))
                        if len(reg_attr) > 0 and hasattr(b.fit, reg_attr):
                            regions.extend(getattr(b.fit, reg_attr))

                        for j,rattr in enumerate(restrict_attr):
                            if hasattr(b.fit, rattr):
                                rdata[rattr].extend(getattr(b.fit, rattr))
                            else:
                                rdata[rattr].extend([restrict_lim[j][0]
                                                     for r in slist])

                if len(rgates) > 0:
                    # Cycle through range gate boxes
                    range_min = np.nanmin(rgates)
                    range_max = np.nanmax(rgates)
                    if range_max > max(max_rg):
                        range_max = max(max_rg)

                    rgates = np.array(rgates)
                    fovflg = np.array(fovflg)
                    onefov = np.array(onefov)

                    # Combine hop and region data (if available), to allow
                    # a comprehensive division by propagation path
                    if len(regions) == len(hops):
                        chops = ["{:.1f}{:s}".format(hops[ihop], reg)
                                 if not np.isnan(hops[ihop]) and len(reg) > 0
                                 else np.nan for ihop,reg in enumerate(regions)]
                    else:
                        chops = hops

                    for rattr in restrict_attr:
                        rdata[rattr] = np.array(rdata[rattr])

                    for r in np.arange(range_min, range_max + 1):
                        # Select the indexes for this range gate box
                        ilim = 0
                        while ilim < len(max_rg) and r >= max_rg[ilim]:
                            ilim += 1

                        rmin = r - rhalf[ilim]
                        rmax = r + rhalf[ilim]

                        # If the box size is even, then the testing
                        # conditions will put too many points in the box
                        # unless the size is reduced.  Effectively sets:
                        # jr = np.where(rgates[ir] < rmax)[0]
                        if frg_box[ilim] % 2 == 0:
                            rmax -= 1

                        # Now that we know how big our window is, we can
                        # determine the maximum number of points
                        max_pnts = float(len(bicp) * frg_box[ilim])
                        ir = np.where(rgates >= rmin)[0]
                        jr = np.where(rgates[ir] <= rmax)[0]

                        # Find the hop numbers to consider
                        shop = set([chops[ihop] for ihop in ir[jr]
                                    if isinstance(chops[ihop], str) or
                                    not np.isnan(chops[ihop])])

                        for ihop in shop:
                            hr = [ih for ih in ir[jr] if chops[ih] == ihop]

                            # Test any additional restrictions
                            if float(len(hr)) / max_pnts >= min_frac:
                                for j,rattr in enumerate(restrict_attr):
                                    if len(restrict_lim[j]) == 2:
                                        hk = [hr[k] for k,rd in
                                              enumerate(rdata[rattr][hr])
                                              if(rd >= restrict_lim[j][0]
                                                 and rd < restrict_lim[j][1])]
                                        hr = hk

                                    # Quit testing if there aren't enough
                                    # points to perform the UT structure
                                    # evaluation
                                    if float(len(hr)) / max_pnts < min_frac:
                                        break

                            # Evaluate the temporal FoV structures
                            if float(len(hr)) / max_pnts < min_frac:
                                # There are not enough points in this range
                                # gate and UT box to evaluate the
                                # backscatter structures at this hop
                                estr = "unable to evaluate beam ["
                                estr = "{:s}{:d}] at [".format(estr, bnum)
                                estr = "{:s}{:}".format(estr,
                                                        beams[bnum][bis].time)
                                estr = "{:s}] gate [{:d}], ".format(estr, r)
                                estr = "{:s}insufficient ".format(estr)
                                estr = "{:s}backscatter [".format(estr)
                                estr = "{:s}{:d} < ".format(estr, len(hr))
                                estr = "{:s}{:.0f}".format(estr, max_pnts
                                                           * min_frac)
                                estr = "{:s}] at hop [{:s}]".format(estr, ihop)
                                logging.info(estr)
                            elif float(len(hr)) / max_pnts > 1.0:
                                estr = "maximum number of points exceeded for "
                                estr = "{:s}beam [{:d}] ".format(estr, bnum)
                                estr = "{:s}between range gates ".format(estr)
                                estr = "{:s}[{:d}-{:d}".format(estr, rmin, rmax)
                                estr = "{:s}] at [{:}".format(estr, \
                                                        beams[bnum][bis].time)
                                estr = "{:s} to {:}]".format(estr, \
                                                    beams[bnum][max(bicp)].time)
                                estr = "{:s}: {:d} > ".format(estr, len(hr))
                                estr = "{:s}{:f}".format(estr, max_pnts)
                                logging.error(estr)
                            else:
                                # Get the number of backscatter observations
                                # in each field-of-view
                                rr = dict()
                                rr[1] = np.where(fovflg[hr] == 1)[0]
                                rr[-1] = np.where(fovflg[hr] == -1)[0]
                                fn = float(len(rr[1]))
                                bn = float(len(rr[-1]))
                                tn = fn + bn
                                ffrac = fn / tn if tn > 0.0 else -1.0

                                bad_fov = 0
                                good_fov = False
                                if(ffrac > 0.0 and ffrac >= fov_frac and
                                   bn > 0.0):
                                    good_fov = True
                                    bad_fov = -1
                                elif(ffrac >= 0.0 and 1.0-ffrac >= fov_frac
                                     and fn > 0.0):
                                    good_fov = True
                                    bad_fov = 1

                                # Tag the FoV for being consistent or not and
                                # mixed or not, unless this backscatter point
                                # only as one valid FoV
                                if good_fov:
                                    for irr in rr[bad_fov]:
                                        if not onefov[hr[irr]]:
                                            zz = bi[hr[irr]]
                                            yy = ri[hr[irr]]
                                            fovbelong[zz][yy]['out'] += 1

                                    for irr in rr[-bad_fov]:
                                        zz = bi[hr[irr]]
                                        yy = ri[hr[irr]]
                                        fovbelong[zz][yy]['in'] += 1
                                else:
                                    for ih in hr:
                                        if abs(fovflg[ih]) == 1:
                                            zz = bi[ih]
                                            yy = ri[ih]
                                            fovbelong[zz][yy]['mix'] += 1

                del rgates, fovflg, hops, bi, ri
                bis += 1

        # Update the fovflags
        for i in np.arange(0, len(beams[bnum])):
            for j,bdict in enumerate(fovbelong[i]):
                if(bdict["out"] > 0 and
                   bdict["in"] < bdict["out"] + bdict["mix"]):
                    # Update the FoV flag and the structure flag, since a
                    # structure cannot be set without a FoV
                    if(bdict['out'] > bdict['mix'] and
                       bdict['out'] > bdict['in']):
                        beams[bnum][i].fit.fovflg[j] = fovpast[i][j]
                    else:
                        beams[bnum][i].fit.fovflg[j] = 0

                    if fovpast[i][j] != 0:
                        if fovpast[i][j] == -1:
                            nelv = beams[bnum][i].fit.belv[j]
                            nelve = beams[bnum][i].fit.belv_e[j]
                            nheight = beams[bnum][i].fit.bvheight[j]
                            nheighte = beams[bnum][i].fit.bvheight_e[j]
                            nhop = beams[bnum][i].fit.bhop[j]
                            nreg = beams[bnum][i].fit.bregion[j]
                        else:
                            nelv = beams[bnum][i].fit.felv[j]
                            nelve = beams[bnum][i].fit.felv_e[j]
                            nheight = beams[bnum][i].fit.fvheight[j]
                            nheighte = beams[bnum][i].fit.fvheight_e[j]
                            nhop = beams[bnum][i].fit.fhop[j]
                            nreg = beams[bnum][i].fit.fregion[j]

                        beams[bnum][i].fit.fovelv[j] = nelv
                        beams[bnum][i].fit.fovelv_e[j] = nelve
                        beams[bnum][i].fit.vheight[j] = nheight
                        beams[bnum][i].fit.vheight_e[j] = nheighte
                        beams[bnum][i].fit.hop[j] = nhop
                        beams[bnum][i].fit.region[j] = nreg
                        fovpast[i][j] = 0

    return(beams)
