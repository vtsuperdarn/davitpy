# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.aacgm
*********************
"""
try:
    from aacgmlib import *
except Exception, e:
    print __file__+' -> aacgmlib: ', e
