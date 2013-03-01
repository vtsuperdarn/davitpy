# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models
*********************

**Modules**:
    * :mod:`aacgm`: corrected geomagnetic model
    * :mod:`tsyganenko`: T96
    * :mod:`iri`: International Reference Ionosphere 2012
    * :mod:`igrf`: International Geomagnetic Reference Field 2011
    * :mod:`msis`: Neutral atmosphere model (NRLMSISE-00)
    * :mod:`raydarn`: SuperDARN ray tracing code coupled with IRI

"""
try:
    import tsyganenko
except Exception, e:
    print __file__+' -> tsyganenko: ', e

try:
    import igrf
except Exception, e:
    print __file__+' -> igrf: ', e

try:
    import aacgm
except Exception, e:
    print __file__+' -> aacgm: ', e

try:
    import iri
except Exception, e:
    print __file__+' -> iri: ', e

try:
    import msis
except Exception, e:
    print __file__+' -> msis: ', e

try:
    import hwm
except Exception, e:
    print __file__+' -> hwm: ', e

