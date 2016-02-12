# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: gme.plotting
*********************
This subpackage contains various plotting routines for geomagnetic environment data.

**Modules**:
	* :mod:`gme.plotting.gmeplot`

*******************************
"""
import logging

try: from gmeplot import *
except Exception, e: 
  logging.exception('problem importing gme.plotting.gmeplot: ' + e)
