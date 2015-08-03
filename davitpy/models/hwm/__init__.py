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


def checkhwm07(data_file_path=None):

    try:
        from checkhwm07 import checkhwm07
    except Exception as e:
        print __file__+' -> models.hwm.checkhwm07: ', e

    if data_file_path is None:
        from davitpy import rcParams
        data_file_path = rcParams['DAVITPY_PATH']

    return checkhwm07(data_file_path)


def hwm07(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,data_file_path=None):

    try:
        from hwm07 import hwm07
    except Exception as e:
        print __file__+' -> models.hwm.hwm07: ', e

    if data_file_path is None:
        from davitpy import rcParams
        data_file_path = rcParams['DAVITPY_PATH']

    return hwm07(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,data_file_path)

