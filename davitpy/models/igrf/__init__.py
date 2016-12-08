# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""International Geomagnetic Reference Field 2011

Basic plotting tools for IGRF

Modules
---------------------------
igrf    fortran subroutines
---------------------------

"""
import logging

try:
    from igrf import *
except Exception, e:
    logging.exception(__file__ + ' -> igrf: ' + str(e))
