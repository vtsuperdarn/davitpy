# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models
*********************

**Modules**:
    * :mod:`models.aacgm`: corrected geomagnetic model
    * :mod:`models.tsyganenko`: T96
    * :mod:`models.iri`: International Reference Ionosphere 2012
    * :mod:`models.igrf`: International Geomagnetic Reference Field 2011
    * :mod:`models.msis`: Neutral atmosphere model (NRLMSISE-00)
    * :mod:`models.raydarn`: SuperDARN ray tracing code coupled with IRI

"""
try:
    import tsyganenko
except Exception, e:
    print __file__+' -> models.tsyganenko: ', e

try:
    import igrf
except Exception, e:
    print __file__+' -> models.igrf: ', e

try:
    import aacgm
except Exception, e:
    print __file__+' -> models.aacgm: ', e

try:
    import iri
except Exception, e:
    print __file__+' -> models.iri: ', e

try:
    import msis
except Exception, e:
    print __file__+' -> models.msis: ', e

try:
    import hwm
except Exception, e:
    print __file__+' -> models.hwm: ', e

try:
    import raydarn
except Exception, e:
    print __file__+' -> models.raydarn: ', e

