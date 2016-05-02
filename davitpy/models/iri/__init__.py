# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""International Reference Ionosphere

Modules
---------------------------
iri     fortran subroutines
---------------------------
    
"""
import logging


def iri_sub(jf, jmag, alati, along, iyyyy, mmdd, dhour, heibeg, heiend,
            heistp, oarr, data_file_path=None):
    """

    Parameters
    ----------
    jf :

    jmag :

    alati :

    along :

    iyyyy :

    mmdd :

    dhour :

    heibeg :

    heiend :

    heistp :

    oarr :

    data_file_path : Optional[str]
        Path to davitpy installation. Default is to use rcParams' 'DAVITPY_PATH'

    """
    try:
        from iri import iri_sub
    except Exception as e:
        logging.exception(__file__ + ' -> models.iri.iri_sub: ' + str(e))

    if data_file_path is None:
        from davitpy import rcParams
        data_file_path = rcParams['DAVITPY_PATH']

    return iri_sub(jf, jmag, alati, along, iyyyy, mmdd, dhour, heibeg,
                   heiend, heistp, oarr, data_file_path)
