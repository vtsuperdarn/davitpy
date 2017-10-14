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
from __future__ import absolute_import
import logging

try:
    from . import tsyganenko
except Exception as e:
    logging.exception(__file__ + ' -> models.tsyganenko: ' + str(e))

try:
    from . import igrf
except Exception as e:
    logging.exception(__file__ + ' -> models.igrf: ' + str(e))

try:
    from . import aacgm
except Exception as e:
    logging.exception(__file__ + ' -> models.aacgm: ' + str(e))

try:
    from . import iri
except Exception as e:
    logging.exception(__file__ + ' -> models.iri: ' + str(e))

try:
    from . import msis
except Exception as e:
    logging.exception(__file__ + ' -> models.msis: ' + str(e))

try:
    from . import hwm
except Exception as e:
    logging.exception(__file__ + ' -> models.hwm: ' + str(e))

try:
    from . import raydarn
except Exception as e:
    logging.exception(__file__ + ' -> models.raydarn: ' + str(e))

