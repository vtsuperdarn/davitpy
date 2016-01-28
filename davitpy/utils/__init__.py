# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
utils
-----

This subpackage contains various utilities for DaViT-py

Modules
--------------------------------------
plotUtils   Basic plotting tools 
geoPack     geographic transformations
timeUtils   date/time manipulations 
calcSun     solar position calculator
coordUtils  coordinate system tools
--------------------------------------

Attributes
----------
Re : float
    Mean Earth radius in kilometers
RePol : float
    Polar Earth radius in kilometers
ReEqu : float
    Equatorial Earth radisu in kilometers


"""

import logging

try:
    from plotUtils import *
except Exception, e:
    logging.exception(__file__ + ' -> utils.plotUtils: ' + e)

try:
    from geoPack import *
except Exception, e:
    logging.exception(__file__ + ' -> utils.geoPack: ' + e)

try:
    from timeUtils import *
except Exception, e:
    logging.exception(__file__ + ' -> utils.timeUtils: ' + e)

try:
    from calcSun import *
except Exception, e:
    logging.exception(__file__ + ' -> utils.calcSun: ' + e)

try:
    from coordUtils import *
except Exception, e:
    logging.exception(__file__ + ' -> utils.coordUtils: ' + e)


# Define a few general-use constants

Re = 6371.0
RePol = 6378.1370
ReEqu = 6356.7523

class twoWayDict(dict):
    """Thanks to Sasha Chedygov on stackoverflow for this idea

    Note
    ----
    The initialization function was added on here
        
    """
    def __init__(self,initDict={}):
        for key,val in initDict.iteritems():
            self[key] = val
            self[val] = key

    def __len__(self):
        return dict.__len__(self) / 2
		
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

