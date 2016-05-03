# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
sat
---
This subpackage contains various fucntions to read and write sattelite data

Modules
------------------------------------------
goes    NOAA's GOES satellites
poes    NOAA/EUMETSAT's POES satellites
rbsp    NASA's Van Allen probes (ex. RBSP)
------------------------------------------

"""
import logging

try: from goes import *
except Exception, e:
    logging.exception(__file__ + ' -> gme.sat.goes: ' + str(e))

try: from poes import *
except Exception, e:
    logging.exception(__file__ + ' -> gme.sat.poes: ' + str(e))

try: from rbsp import *
except Exception, e:
    logging.exception(__file__+' -> gme.sat.rbsp: ' + str(e))
