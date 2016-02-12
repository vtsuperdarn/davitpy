# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: gme.isr
*********************
This module handles Incoherent Scatter Radar data.

This includes the following submodules:
    * **mho**: Millstone Hill Observatory data

"""
import logging

try: from mho import *
except Exception, e:
    logging.exception(__file__+' -> gme.isr.mho: ' + e)
