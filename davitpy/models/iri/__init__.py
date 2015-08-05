# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.iri
*********************

**Modules**:
    * :mod:`iri`: fortran subroutines 
    
*******************************
"""

def iri_sub(jf,jmag,alati,along,iyyyy,mmdd,dhour,heibeg,heiend,heistp,oarr,data_file_path):

    try:
        from iri import iri_sub
    except Exception as e:
        print __file__+' -> models.iri.iri_sub: ', e

    if data_file_path is None:
      from davitpy import rcParams
      data_file_path = rcParams['DAVITPY_PATH']

    return iri_sub(jf,jmag,alati,along,iyyyy,mmdd,dhour,heibeg,heiend,heistp,oarr,data_file_path)
