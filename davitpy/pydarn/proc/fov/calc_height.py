#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# calc_virtual_height.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Routines to calculate the height and its error.
#-----------------------------------------------------------------------------
"""calc_virtual_height

Routines to calculate the height and its error

Functions
------------------------------------------------------------------------------
calc_virtual_height        calculate virtual height
calc_virtual_height_w_err  calculate virtual height with error
------------------------------------------------------------------------------

Author: Angeline G. Burrell (AGB)
Date: February 9, 2016
Inst: University of Leicester (UoL)
"""

# Import python packages
import numpy as np
from scipy import constants as scicon
import logging

#---------------------------------------------------------------------------
def calc_virtual_height(beam, radius, elv=list(), elv_attr="elv", dist=list(),
                        dist_attr="slist", dist_units=None):
    """Calculate the virtual height for a specified backscatter distance and
    elevation angle.

    Parameters
    -----------
    beam : (class `pydarn.sdio.radDataTypes.beamData`)
        Data for a single radar and beam along all range gates at a given time
    radius : (float)
        Earth radius in km
    elv : (list or numpy.array())
        List containing elevation in degrees, or nothing to load the
        elevation from the beam (default=list())
    elv_attr : (string)
        Name of beam attribute containing the elevation (default="elv")
    dist : (list or numpy.array())
        List containing the slant distance from the radar to the reflection
        location of the backscatter, or nothing to load the distance from the
        beam. (default=list())
    dist_attr : (str)
        Name of beam attribute containing the slant distance.  Be aware that if
        the default is used, all heights returned will be for .5 hop propogation
        paths.  (default="slist")
    dist_units : (string or NoneType)
        Units of the slant distance to backscatter location data.  May supply
        "km", "m", or None.  None indicates that the distance is in range gate
        bins. (default=None)
    
    Returns
    --------
    height : (numpy.array)
        An array of floats of the same size as the myBeam.fit.slist list,
        containing the virtual height for each range gate or NaN if a virtual
        height could not be calculated

    Notes
    --------
    Specifying a single earth radius introduces additional error into the
    resulting heights.  If the terrestrial radius at the radar location is used,
    this error is on the order of 0.01-0.1 km (much smaller than the difference
    between the real and virtual height).
    """
    import davitpy.pydarn.sdio as sdio

    #---------------------------------
    # Check the input
    if not isinstance(beam, sdio.radDataTypes.beamData):
        logging.error('the beam must be a beamData class')
        return None

    if not isinstance(radius, float):
        logging.error('the radius must be a float')
        return None

    #---------------------------------
    # Load elevation
    if len(elv) == 0 or (len(dist) > 0 and len(elv) != len(dist)):
        try:
            elv = getattr(beam.fit, elv_attr)

            if elv is None:
                logging.error('no elevation available')
                return None
        except:
            logging.error('no elevation attribute [{:s}]'.format(elv_attr))
            return None

    #---------------------------------
    # Load the slant range/distance
    if len(dist) == 0 or len(dist) != len(elv):
        try:
            dist = getattr(beam.fit, dist_attr)

            if dist is None:
                logging.error('no range/distance data available')
                return None

            if len(dist) != len(elv):
                logging.error('different number of range and elevation points')
                return None
        except:
            logging.error('no range attribute [{:s}]'.format(dist_attr))
            return None

    if len(dist) == 0 or len(elv) == 0 or len(elv) != len(dist):
        logging.error("unable to load matching elevation and distance lists")
        return None

    #---------------------------------------------------------------------
    # Ensure that the range/distance (and error) are in km
    if dist_units is None:
        # Convert from range gates to km
        dist = list(5.0e-10 * scicon.c * (np.array(dist) * beam.prm.smsep
                                          + beam.prm.lagfr))
    elif dist_units is "m":
        # Convert from meters to km
        dist = [d / 1000.0 for d in dist]
    elif dist_units is not "km":
        logging.error('unknown range unit [{:s}]'.format(dist_units))
        return None

    #-----------------------------------------------------------------------
    # Cycle through the beams and elevations, calculating the virtual height
    height = np.empty(shape=(len(dist),), dtype=float) * np.nan

    for i,d in enumerate(dist):
        if not np.isnan(elv[i]):
            # Calculate height by assuming a spherical earth and solving the
            # law of cosines for an obtuse triangle with sides radius,
            # radius + height, and distance, where the angle between the side of
            # length distance and radius + height is equal to 90 deg - elevation
            hsqrt = np.sqrt(d**2 + radius**2 + 2.0 * d * radius
                            * np.sin(np.radians(elv[i])))
            height[i] = hsqrt - radius

    return height

#---------------------------------------------------------------------------
def calc_virtual_height_w_err(beam, radius, radius_e=0.0, elv=list(),
                              elv_attr="elv", elv_e=list(), elv_e_attr="elv_e",
                              dist=list(), dist_attr="slist", dist_e=list(),
                              dist_e_attr="slist_e", dist_units=None):
    """Calculate the virtual height and error for a specified backscatter
    distance and elevation angle.

    Parameters
    -----------
    beam : (class `pydarn.sdio.radDataTypes.beamData`)
        Data for a single radar and beam along all range gates at a given time
    radius : (float)
        Earth radius in km
    radius_e : (float)
        Earth radius error in km (default=0.0)
    elv : (list or numpy.array())
        List containing elevation in degrees, or nothing to load the
        elevation from the beam (default=list())
    elv_attr : (string)
        Name of beam attribute containing the elevation (default="elv")
    elv_e : (list or numpy.array())
        List containing elevation error in degrees, or nothing to load the
        elevation from the beam (default=list())
    elv_e_attr : (string)
        Name of beam attribute containing the elevation error (default="elv_e")
    dist : (list or numpy.array())
        List containing the slant distance from the radar to the reflection
        location of the backscatter, or nothing to load the distance from the
        beam. (default=list())
    dist_attr : (str)
        Name of beam attribute containing the slant distance.  Be aware that if
        the default is used, all heights returned will be for .5 hop propogation
        paths.  (default="slist")
    dist_e : (list or numpy.array())
        List containing the error in slant distance from the radar to the
        reflection location of the backscatter, or nothing to load the distance
        error from the beam. (default=list())
    dist_e_attr : (str)
        Name of beam attribute containing the error in slant distance.  Be aware
        that if the default is used, all height errors returned will be for .5
        hop propogation paths.  (default="dist_e")
    dist_units : (string or NoneType)
        Units of the slant distance to backscatter location data and errors.
        May supply "km", "m", or None.  None indicates that the distance is in
        range gate bins. You cannot supply the distance and distance error in
        different unites.  (default=None)
    
    Returns
    --------
    height : (numpy.array)
        An array of floats of the same size as the myBeam.fit.slist list,
        containing the virtual heights for each range gate or NaN if the
        virtual height could not be calculated
    height_err : (numpy.array)
        An array of floats of the same size as the myBeam.fit.slist list,
        containing the virtual height error for each range gate or NaN if an
        error could not be calculated

    Notes
    --------
    Specifying a single earth radius introduces additional error into the
    resulting heights.  If the terrestrial radius at the radar location is used,
    this error is on the order of 0.01-0.1 km (much smaller than the difference
    between the real and virtual height). This error can be included by using
    the radius_e input parameter.
    """
    import davitpy.pydarn.sdio as sdio

    #---------------------------------
    # Check the input
    if not isinstance(beam, sdio.radDataTypes.beamData):
        logging.error('the beam must be a beamData class')
        return None

    if not isinstance(radius, float):
        logging.error('the radius must be a float')
        return None

    #---------------------------------
    # Load elevation
    if len(elv) == 0 or (len(dist) > 0 and len(elv) != len(dist)):
        try:
            elv = getattr(beam.fit, elv_attr)

            if elv is None:
                logging.error('no elevation available')
                return None
        except:
            logging.error('no elevation attribute [{:s}]'.format(elv_attr))
            return None

    #---------------------------------
    # Load elevation error
    if len(elv_e) == 0 or (len(elv) > 0 and len(elv_e) != len(elv)):
        try:
            elv_e = getattr(beam.fit, elv_e_attr)

            if elv_e is None:
                logging.error('no elevation available')
                return None
        except:
            estr = 'no elevation error attribute [{:s}]'.format(elv_e_attr)
            logging.info(estr)
            elv_e = [0.0 for e in elv]

    #---------------------------------
    # Load the slant range/distance
    if len(dist) == 0 or len(dist) != len(elv):
        try:
            dist = getattr(beam.fit, dist_attr)

            if dist is None:
                logging.error('no range/distance data available')
                return None

            if len(dist) != len(elv):
                logging.error('different number of range and elevation points')
                return None
        except:
            logging.error('no range attribute [{:s}]'.format(dist_attr))
            return None

    if len(dist) == 0 or len(elv) == 0 or len(elv) != len(dist):
        logging.error("unable to load matching elevation and distance lists")
        return None

    #--------------------------------------
    # Load the slant range/distance error
    if len(dist_e) == 0 or len(dist_e) != len(dist):
        try:
            dist_e = getattr(beam.fit, dist_e_attr)

            if dist_e is None:
                logging.error('no range/distance errors available')
                return None

            if len(dist_e) != len(dist):
                logging.error('different number of distance points and errors')
                return None
        except:
            logging.info('no range error attribute [{:s}]'.format(dist_e_attr))
            dist_e = [0.0 for d in dist]

    #---------------------------------------------------------------------
    # Ensure that the range/distance (and error) are in km
    if dist_units is None:
        # Convert from range gates to km
        dist = list(5.0e-10 * scicon.c * (np.array(dist) * beam.prm.smsep
                                          + beam.prm.lagfr))
        dist_e = list(5.0e-10 * scicon.c * np.array(dist_e) * beam.prm.smsep)
    elif dist_units is "m":
        # Convert from meters to km
        dist = [d / 1000.0 for d in dist]
        dist_e = [d / 1000.0 for d in dist_e]
    elif dist_units is not "km":
        logging.error('unknown range unit [{:s}]'.format(dist_units))
        return None

    #-----------------------------------------------------------------------
    # Cycle through the beams and elevations, calculating the virtual height
    height = np.empty(shape=(len(dist),), dtype=float) * np.nan
    height_err = np.empty(shape=(len(dist),), dtype=float) * np.nan

    for i,d in enumerate(dist):
        if not np.isnan(elv[i]):
            # Calculate height by assuming a spherical earth and solving the
            # law of cosines for an obtuse triangle with sides radius,
            # radius + height, and distance, where the angle between the side of
            # length distance and radius + height is equal to 90 deg - elevation
            sin_elv = np.sin(np.radians(elv[i]))
            hsqrt = np.sqrt(d**2 + radius**2 + 2.0 * d * radius * sin_elv)
            height[i] = hsqrt - radius

            # Now that the height has been calculated, find the error
            term_elv = 0.0
            if not np.isnan(elv_e[i]) or elv_e[i] > 0.0:
                temp = d * radius * np.cos(np.radians(elv[i])) / hsqrt
                term_elv = (elv_e[i] * temp)**2

            term_rad = 0.0
            if not np.isnan(radius_e) or radius_e > 0.0:
                temp = (radius + d * sin_elv) / hsqrt - 1.0
                term_rad = (radius_e * temp)**2

            term_d = 0.0
            if not np.isnan(dist_e[i]) or dist_e[i] > 0.0:
                temp = (d + radius * sin_elv) / hsqrt
                term_d = (dist_e[i] * temp)**2

            height_err[i] = np.sqrt(term_rad + term_d + term_elv)

    return height, height_err
