# -*- coding: utf-8 -*-
"""models.aacgm

Functions
------------
------------

"""
import logging

try:
    from wrapper import convert_latlon, convert_str_to_bit, get_aacgm_coord
    from wrapper import convert_latlon_arr, get_aacgm_coord_arr
except Exception, e:
    logging.exception(__file__ + ' -> aacgm: ' + str(e))

try:
    from aacgm import convert
except Exception, e:
    logging.exception(__file__ + ' -> aacgm: ' + str(e))

try:
    from aacgm import set_datetime
except Exception, e:
    logging.exception(__file__ + ' -> aacgm: ' + str(e))

try:
    from aacgm import mlt_convert
except Exception, e:
    logging.exception(__file__ + ' -> aacgm: ' + str(e))

try:
    from aacgm import mlt_convert_yrsec
except Exception, e:
    logging.exception(__file__ + ' -> aacgm: ' + str(e))

try:
    from aacgm import G2A, A2G, TRACE, ALLOWTRACE, BADIDEA, GEOCENTRIC
except Exception, e:
    logging.exception(__file__ + ' -> aacgm: ' + str(e))
