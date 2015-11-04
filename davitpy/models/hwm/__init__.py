# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.hwm
*********************

**Modules**:
    * :mod:`hwm14`: fortran subroutines
  
*********************
"""

def checkhwm14(path=None):

    try:
        from checkhwm14 import checkhwm14
    except Exception as e:
        print __file__+' -> models.hwm.checkhwm14: ', e

    if path is None:
        from davitpy import rcParams
        path = rcParams['DAVITPY_PATH']

    return checkhwm14(path)

def hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,path=None):

    try:
        from hwm14 import hwm14
    except Exception as e:
        print __file__+' -> models.hwm.hwm14: ', e

    if path is None:
        from davitpy import rcParams
        try:
            path = "{:s}/davitpy/models/hwm/".format(rcParams['DAVITPY_PATH'])
        except Exception as e:
            print __file__+' -> models.hwm.hwm14: ', e

    return hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,path)

import hwm_input
