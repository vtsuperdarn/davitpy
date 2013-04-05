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


# Update local HDF5
_ = updateHdf5()
