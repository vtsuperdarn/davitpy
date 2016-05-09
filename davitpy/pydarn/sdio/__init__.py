# I/O module __init__.py
"""
This subpackage contains various input/output routines for DaViTpy

Modules
---------
DataTypes
    defines the general data pointer
radDataTypes
    defines the fundamental radar data types
radDataRead
    contains the functions necessary for reading radar data
sdDataTypes
    defines the map and grid data types
sdDataRead
    contains the functions to read the radar map and grid files
fitexfilter
    Contains filtering routines
dbUtils
    general utilities for database maintenance
fetchUtils
    routines to retrieve data files from local and remote locations
"""
import logging

try:
    from fetchUtils import *
except Exception,e:
    logging.exception(__file__+' -> pydarn.sdio.fetchUtils: ', str(e))

try:
    from DataTypes import *
except Exception,e:
    logging.exception(__file__+' -> pydarn.sdio.DataTypes: ', str(e))

try:
    from radDataTypes import *
except Exception,e:
    logging.exception(__file__+' -> pydarn.sdio.radDataTypes: ', str(e))

try:
    from radDataRead import *
except Exception,e:
    logging.exception(__file__+' -> pydarn.sdio.radDataRead: ', str(e))

try:
    from sdDataTypes import *
except Exception,e:
    logging.exception(__file__+' -> pydarn.sdio.sdDataTypes: ', str(e))

try:
    from sdDataRead import *
except Exception,e: 
    logging.exception(__file__+' -> pydarn.sdio.sdDataRead: ', str(e))

try:
    from fitexfilter import *
except Exception,e:
    logging.exception(__file__+' -> pydarn.sdio.fitexfilter: ', str(e))

try:
    from dbUtils import *
except Exception,e:
    logging.exception(__file__+' -> pydarn.sdio.dbUtils: ', str(e))
