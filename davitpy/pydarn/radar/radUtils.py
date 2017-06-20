# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
Module
------
pydarn.radar.radUtils

Functions
---------
getCpName
    get the name of a control program from cp id number
getParamDict
    Get information about a parameter, including units,
    default ranges, and axis labels.

"""
import logging

def getCpName(cpid):
    """Get the name of a control program from cp id number

    Parameters
    ----------
    cpid : int
        the control prog. id number

    Returns
    -------
    cpName : str
        the name of a control program

    Example
    -------
        s = getCpName(3310)

    written by AJ, 2012-08

    """
    from math import fabs

    assert(isinstance(cpid, int) or isinstance(cpid, float)), \
        logging.error('error, cpid must be a number')
    if(fabs(cpid) == 26003):
        return 'stereoscan (b)'
    if(fabs(cpid) == 153):
        return 'stereoscan (a)'
    if(fabs(cpid) == 3310):
        return 'themis-tauscan'
    if(fabs(cpid) == 3300):
        return 'themisscan'
    if(fabs(cpid) == 150):
        return 'katscan'
    if(fabs(cpid) == 151):
        return 'katscan -fast'
    if(fabs(cpid) == 503):
        return 'tauscan'
    if(fabs(cpid) == 9213):
        return 'pcpscan'
    if(fabs(cpid) == 1):
        return 'normalscan'
    if(fabs(cpid) == 210):
        return 'rbsp-tau'
    if(fabs(cpid) == 3501):
        return 'twofsound'
    if(fabs(cpid) == 1200):
        return 'icescan'
    else:
        return ''

def getParamDict(param):
    """Get information about a parameter, including units, default ranges,
    and axis labels.

    Parameters
    ----------
    param : str
        name of parameter

    Returns
    -------
    paramDict : str
        dictionary containing information about the chosen parameter

    Example
    -------
        paramDict = getParamDict('w_l')

    written by Nathaniel Frissell, 2013-07

    """
    import numpy as np

    # Create empty dictionary.
    paramDict = {}

    if param == 'p_l' or param == 'power':
        paramDict['param'] = 'power'
        paramDict['label'] = r'$\lambda$ Power'
        paramDict['unit'] = 'dB'
        paramDict['range'] = (0, 30)
    elif param == 'p_s':
        paramDict['param'] = 'power'
        paramDict['label'] = r'$\sigma$ Power'
        paramDict['unit'] = 'dB'
        paramDict['range'] = (0, 30)
    elif param == 'v' or param == 'velocity':
        paramDict['param'] = 'velocity'
        paramDict['label'] = 'Velocity'
        paramDict['unit'] = 'm s^{-1}'
        paramDict['range'] = (-500, 500)
    elif param.find('vheight') >= 0:
        paramDict['param'] = 'height'
        paramDict['label'] = "h'"
        paramDict['unit'] = 'km'
        paramDict['range'] = (75.0, 900.0)
    elif param == 'w_l' or param == 'width':
        paramDict['param'] = 'width'
        paramDict['label'] = r'$\lambda$ Spectral Width'
        paramDict['unit'] = 'm s^{-1}'
        paramDict['range'] = (0, 100)
    elif param == 'w_s':
        paramDict['param'] = 'width'
        paramDict['label'] = r'$\sigma$ Spectral Width'
        paramDict['unit'] = 'm s^{-1}'
        paramDict['range'] = (0, 100)
    elif param.find('elv') >= 0:
        paramDict['param'] = 'elevation'
        paramDict['label'] = 'Elevation'
        paramDict['unit'] = 'degrees'
        paramDict['range'] = (10, 30)
    elif param == 'phi0':
        paramDict['param'] = 'phi'
        paramDict['label'] = r'$\phi_0$'
        paramDict['unit'] = 'radians'
        paramDict['range'] = (-np.pi, np.pi)
    return paramDict
