# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""Horizontal wind model module

Modules
---------------------------
hwm14   fortran subroutines
---------------------------
  
"""
import logging

def hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,path=None):
    """

    Parameters
    ----------
    iyd :

    sec :

    alt :

    glat :

    glon :

    stl :

    f107a :

    f107 :

    ap :

    path : Optional[str]
        location for davitpy installation.  Default is rcParams' 'DAVITPY_PATH'
        value.

    """
    try:
        from hwm14 import hwm14
    except Exception as e:
        logging.exception(__file__ + ' -> models.hwm.hwm14: ' + str(e))

    if path is None:
        from davitpy import rcParams
        try:
            path = "{:s}/davitpy/models/hwm/".format(rcParams['DAVITPY_PATH'])
        except Exception as e:
            logging.exception(__file__ + ' -> models.hwm.hwm14: ' + str(e))

    return hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,path)

import hwm_input
