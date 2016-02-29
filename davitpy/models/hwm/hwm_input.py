#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# hwm_input.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Routines to make it easier to provide input to HWM in python
#-----------------------------------------------------------------------------
"""
hwm_input

Author: Angeline G. Burrell (AGB)
Date: September 16, 2015
Inst: University of Leicester (UoL)

Comments
----------
Routines to make it easier to provide input to HWM in python

Contains
----------
format_hwm_input
datetime_to_utsec
datetime_to_iydsec
datetime_to_slt
"""

# Import python packages
import datetime as dt
import logging

def format_hwm_input(time, alt, lat, lon, ap=-1, path=None):
    """ Take input using keywords and return a set with correctly formatted
    input for HWM14

    Parameters
    -------------
    time : datetime.datetime
        UT as a datetime object
    alt : float
        Altitude in km (lower limit at 0 km)
    lat : float
        Geographic latitude in degrees North
    lon : float
        Geographic longitude in degrees East
    ap : Optional[float]
        Ap index or -1 to produce undisturbed winds (default=-1.0)
    path : Optional[str or NoneType]
        Path to HWM data files

    Returns
    -----------
    hwm_set : set or NoneType
        Set containing used and unused inputs
        (iyd,sec,alt,lat,lon,slt,f107a,f107,ap,w)
    """
    iyd = datetime_to_iyd(time)
    sec = datetime_to_utsec(time)

    # The first element of this array is not used
    ap = [0.0, ap]

    # Define the path if it was not provided
    if path is None:
        from davitpy import rcParams
        try:
            path = "{:s}/davitpy/models/hwm/".format(rcParams['DAVITPY_PATH'])
        except Exception as e:
            logging.exception(e)
            return None

    # These inputs are not used
    stl = datetime_to_slt(time, lon)
    f107a = 100.0
    f107 = 100.0

    # This is the input
    hwm_set = (iyd, sec, alt, lat, lon, stl, f107a, f107, ap, path)

    return hwm_set

def datetime_to_utsec(time):
    """ Calculate seconds of day from datetime

    Parameters
    -----------
    time : datetime.datetime
        datetime object

    Returns
    ----------
    sec_of_day : float
        Seconds of day
    """

    sec_of_day = (time.hour * 3600.0 + time.minute * 60.0 + time.second
                  + time.microsecond * 1.0e-6)
    return sec_of_day

def datetime_to_iyd(time):
    """ Convert datetime to iyd input needed for hwm

    Parameters
    ------------
    time : datetime.datetime
        datetime object

    Returns
    ----------
    iyd : int
        integer combining year and day of year (YYDDD)
    """

    ttuple = time.timetuple()
    iyd = ttuple.tm_yday + (ttuple.tm_year
                            - int(ttuple.tm_year / 100) * 100) * 1000

    return iyd

def datetime_to_slt(time, glon):
    """ Compute local time from date and longitude.

    Parameters:
    ------------
    time : datetime.datetime
        datetime objects
    glon : float
        geographic longitude in degrees.

    Output:
    --------
    lt : float
        Local time in hours
    """
    lt = datetime_to_utsec(time) / 3600.0 + glon / 15.0

    # Adjust to ensure that 0.0 <= lt < 24.0
    lt = lt if lt >= 0.0 else lt + 24.0
    lt = lt if lt < 24.0 else lt - 24.0

    return(lt)
