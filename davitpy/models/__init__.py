# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""models module

Module with python wrappers to c and fortran codes for various models

Modules
----------------------------------------------------------
aacgm       corrected geomagnetic model
tsyganenko  T96
iri         International Reference Ionosphere 2012
igrf        International Geomagnetic Reference Field 2011
msis        Neutral atmosphere model (NRLMSISE-00)
raydarn     SuperDARN ray tracing code coupled with IRI
----------------------------------------------------------

"""
import logging

try:
    import tsyganenko
except Exception, e:
    logging.exception(__file__ + ' -> models.tsyganenko: ' + str(e))

try:
    import igrf
except Exception, e:
    logging.exception(__file__ + ' -> models.igrf: ' + str(e))

try:
    import aacgm
except Exception, e:
    logging.exception(__file__ + ' -> models.aacgm: ' + str(e))

try:
    import iri
except Exception, e:
    logging.exception(__file__ + ' -> models.iri: ' + str(e))

try:
    import msis
except Exception, e:
    logging.exception(__file__ + ' -> models.msis: ' + str(e))

try:
    import hwm
except Exception, e:
    logging.exception(__file__ + ' -> models.hwm: ' + str(e))

try:
    import raydarn
except Exception, e:
    logging.exception(__file__ + ' -> models.raydarn: ' + str(e))

