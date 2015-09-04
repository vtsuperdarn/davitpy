"""
*********************
**Module**: models.aacgm
*********************
"""
try:
    from aacgm import mltFromEpoch
except Exception, e:
    print __file__+' -> aacgm: ', e

try:
    from aacgm import mltFromYmdhms
except Exception, e:
    print __file__+' -> aacgm: ', e

try:
    from aacgm import mltFromYrsec
except Exception, e:
    print __file__+' -> aacgm: ', e


def aacgmConv(in_lat,in_lon,height,year,flg,coeff_prefix=None): 

  from davitpy import rcParams
  from davitpy import models
  from aacgm import direct_aacgmConv

  if coeff_prefix is None:
    coeff_prefix = rcParams['AACGM_DAVITPY_DAT_PREFIX']

  return direct_aacgmConv(in_lat,in_lon,height,year,flg,coeff_prefix)

def aacgmConvArr(in_lat_list,in_lon_list,height_list,year,flg,coeff_prefix=None): 

  from davitpy import rcParams
  from davitpy import models
  from aacgm import direct_aacgmConvArr

  if coeff_prefix is None:
    coeff_prefix = rcParams['AACGM_DAVITPY_DAT_PREFIX']

  return direct_aacgmConvArr(in_lat_list,in_lon_list,height_list,year,flg,coeff_prefix)


