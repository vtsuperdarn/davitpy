# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.hwm
*********************

**Modules**:
    * :mod:`hwm07`: fortran subroutines
  
*********************
"""

try:
    from hwm07 import *
except Exception as e:
    print __file__+' -> models.hwm.hwm07: ', e
