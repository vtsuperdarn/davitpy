# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: pydarn.radar
*********************
This subpackage contains various radar information/routines for DaViT-py

**Modules**:
    * :mod:`pydarn.radar.radFov`: radar fields-of-view calculations
    * :mod:`pydarn.radar.radInfo`: radar information
    * :mod:`pydarn.radar.radUtils`: misc. radar parameters (cpid...)
"""

try:
    from radFov import *
except Exception as e:
    print __file__+' -> pydarn.radar.radFov: ', e

try:
    from radUtils import *
except Exception as e:
    print __file__+' -> pydarn.radar.radUtils: ', e

try:
    from radInfoIo import *
except Exception as e:
    print __file__+' -> pydarn.radar.radInfoIo: ', e

try:
    from radStruct import *
except Exception as e:
    print __file__+' -> pydarn.radar.radStruct: ', e


####################################
# Update local HDF5
####################################
import os.path, time
dirn = os.path.abspath( __file__.split('__init__.py')[0] )
filn = os.path.join(dirn, 'radars.hdf5')
ctime = time.time()
# Update if not there or unreadable
# Update if too old
try:
    mtime = os.path.getmtime(filn)
except OSError:
    mtime = 0
finally:
    if ctime > mtime + 86400*7:
        _ = updateHdf5()
