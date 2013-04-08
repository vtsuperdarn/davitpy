# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.igrf
*********************
Basic plotting tools

**Modules**:
  * :mod:`models.igrf`: fortran subroutines

"""

try:
    from igrf import *
except Exception, e:
    print __file__+' -> igrf: ', e
