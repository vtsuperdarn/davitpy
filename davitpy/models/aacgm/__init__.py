# -*- coding: utf-8 -*-
"""models.aacgm

Functions
------------
aacgmConv
aacgmConvArr
------------

"""
import logging

try:
    from aacgm import mltFromEpoch
except Exception, e:
    logging.exception(__file__ + ' -> aacgm: ' + str(e))

try:
    from aacgm import mltFromYmdhms
except Exception, e:
    logging.exception(__file__ + ' -> aacgm: ' + str(e))

try:
    from aacgm import mltFromYrsec
except Exception, e:
    logging.exception(__file__ + ' -> aacgm: ' + str(e))


def aacgmConv(in_lat, in_lon, height, year, flg, coeff_prefix=None):
    """
    Parameters
    ----------
    in_lat : float

    in_lon : float

    height : float

    year : int

    flg :

    coeff_prefix : Optional[str]
        location for aacgm coefficient files. Default (none) is to use
        rcParams['AACGM_DAVITPY_DAT_PREFEX']

    Returns
    -------
    direct_aacgmConv()

    """
    from davitpy import rcParams
    from davitpy import models
    from aacgm import direct_aacgmConv

    if coeff_prefix is None:
        coeff_prefix = rcParams['AACGM_DAVITPY_DAT_PREFIX']

    return direct_aacgmConv(in_lat, in_lon, height, year, flg, coeff_prefix)


def aacgmConvArr(in_lat_list, in_lon_list, height_list, year, flg,
                 coeff_prefix=None):
    """
    Parameters
    ----------
    in_lat_list : list

    in_lon_list : list

    height_list : list

    year :

    flg :

    coeff_prefix : Optional[str]
        location for aacgm coefficient files. Default (none) is to use
        rcParams['AACGM_DAVITPY_DAT_PREFEX']

    Returns
    -------
    direct_aacgmConvArr()

    """
    from davitpy import rcParams
    from davitpy import models
    from aacgm import direct_aacgmConvArr

    if coeff_prefix is None:
        coeff_prefix = rcParams['AACGM_DAVITPY_DAT_PREFIX']

    return direct_aacgmConvArr(in_lat_list, in_lon_list, height_list,
                               year, flg, coeff_prefix)
