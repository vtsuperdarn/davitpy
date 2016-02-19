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
    import fetchUtils
    from fetchUtils import *
except Exception,e:
    logging.critical('{:}\nproblem importing fetchUtils'.format(e))

try:
    import DataTypes
    from DataTypes import *
except Exception,e:
    logging.critical('{:}\nproblem importing DataTypes'.format(e))

try:
    import radDataTypes
    from radDataTypes import *
except Exception,e:
    logging.critical('{:}\nproblem importing radDataTypes'.format(e))

try:
    import radDataRead
    from radDataRead import *
except Exception,e:
    logging.critical('{:}\nproblem importing radDataRead'.format(e))

try:
    import sdDataTypes
    from sdDataTypes import *
except Exception,e:
    logging.critical('{:}\nproblem importing sdDataTypes'.format(e))

try:
    import sdDataRead
    from sdDataRead import *
except Exception,e: 
    logging.critical('{:}\nproblem importing sdDataRead'.format(e))

try:
    import fitexfilter
    from fitexfilter import *
except Exception,e:
    logging.critical('{:}\nproblem importing fitexfilter'.format(e))

try:
    import dbUtils
    from dbUtils import *
except Exception,e: 
    logging.critical('{:}\nproblem importing dbUtils'.format(e))
