# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
Subpackage
----------
pydarn.radar
    This subpackage contains various radar information/routines for DaViT-py

Modules
-------
pydarn.radar.radFov
    radar fields-of-view calculations
pydarn.radar.radInfo
    radar information
pydarn.radar.radUtils
    misc. radar parameters (cpid...)

Submodules
-----------
tdiff
    Contains routines to estimate the hardware tdiff value for a specified
    radar and frequency band

"""

import logging

try:
    from radFov import *
except Exception as e:
    logging.exception(__file__+' -> pydarn.radar.radFov: ', str(e))

try:
    from radUtils import *
except Exception as e:
    logging.exception(__file__+' -> pydarn.radar.radUtils: ', str(e))

try:
    from radInfoIo import *
except Exception as e:
    logging.exception(__file__+' -> pydarn.radar.radInfoIo: ', str(e))

try:
    from radStruct import *
except Exception as e:
    logging.exception(__file__+' -> pydarn.radar.radStruct: ', str(e))

try:
    import tdiff
except Exception, e:
    logging.exception('problem importing tdiff: ' + str(e))


####################################
# Update local HDF5
####################################
import os.path
import time
import davitpy
try:
    dirn = davitpy.rcParams['DAVIT_TMPDIR']
    d = os.path.dirname(dirn)
    if not os.path.exists(d):
        os.makedirs(d)
except:
    dirn = os.environ['HOME']
filn = os.path.join(dirn, '.radars.sqlite')
ctime = time.time()
# Update if not there or unreadable
# Update if too old
try:
    mtime = os.path.getmtime(filn)
except OSError:
    mtime = 0
finally:
    # DavitPy stores hdw.dat information in a local SQLite file.
    # If that SQLite file does not exist or is more than 1 week old, go
    # update it from an upstream source.
    if ctime > mtime + 86400*7:
        _ = updateRadars()
