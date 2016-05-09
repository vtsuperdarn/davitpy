# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
pydarn.plotting
---------------

This subpackage contains various plotting routines for DaViT-py

Modules
-------------------------------------------------------------------
acfPlot         ACF and XCF data
fan             fan and field of view data
iqPlot          IQ voltage data
mapOverlay      overlay information on maps
musicPlot       data created with the pydarn.proc.music module
plotMapGrid     gridded velocities, convection and contour plotting
printRec        print radar data records to plain text
rti             range-time-intensity data
-------------------------------------------------------------------

"""


import logging

try:
    from rti import *
except Exception, e:
    logging.exception('problem importing rti: ' + str(e))

try:
    from acfPlot import *
except Exception, e:
    logging.exception('problem importing acfPlot: ' + str(e))

try:
    from iqPlot import *
except Exception, e:
    logging.exception('problem importing iqPlot: ' + str(e))

try:
    from fan import *
except Exception, e:
    logging.exception('problem importing fan: ' + str(e))

try:
    from mapOverlay import *
except Exception, e:
    logging.exception('problem importing mapOverlay: ' + str(e))

try:
    from printRec import *
except Exception, e:
    logging.exception('problem importing printRec: ' + str(e))

try:
    from plotMapGrd import *
except Exception, e:
    logging.exception(__file__ + ' -> utils.plotMapGrd: ' + str(e))

try:
    from musicPlot import *
except Exception, e:
    logging.exception('problem importing musicPlot: ' + str(e))
