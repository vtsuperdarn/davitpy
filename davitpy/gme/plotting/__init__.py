# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
plotting
--------

This subpackage contains various plotting routines for geomagnetic environment data.

Modules
---------------------------------------------
gmeplot     reading, writing, storing Kp data
---------------------------------------------

"""
import logging

try: from gmeplot import *
except Exception, e: 
  logging.exception('problem importing gme.plotting.gmeplot: ' + str(e))
