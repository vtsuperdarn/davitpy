# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.iri
*********************

**Modules**:
    * :mod:`iri`: fortran subroutines 
    
*******************************
"""

try:
      from iri import *
except Exception, e:
      print __file__+' -> models.iri.iri: ', e
