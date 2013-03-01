# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.igrf
*********************
Basic plotting tools

**Functions**:
  * :func:`igrf11`: Create empty map

"""

try:
    from igrf import *
except Exception, e:
    print __file__+' -> igrf: ', e