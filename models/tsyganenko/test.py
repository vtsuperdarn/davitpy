#!bin/env python

import numpy as np
from models import tsyganenko
from utils import geoPack, Re

IYEAR = 2000
IDAY = 1
IHOUR = 12
MIN = 0
ISEC = 0

VXGSE = -400.  #  GSE COMPONENTS OF SOLAR WIND VELOCITY VECTOR; THIS PARTICULAR CHOICE 
VYGSE =   0.  #   IS MADE IN ORDER TO MAKE THE GSW SYSTEM IDENTICAL TO THE STANDARD GSM 
VZGSE =   0. 
LMAX = 500 
RLIM = 60. 
R0 = 1. 
L= 100. 
DSMAX = .01
ERR = .000001
DIR = 1

tsyganenko.recalc_08(IYEAR,IDAY,IHOUR,MIN,ISEC,VXGSE,VYGSE,VZGSE)

lat = 50.
lon = 0.
alt = 0.

print lat, lon, 1.
r,theta,phi, xgeo, ygeo, zgeo = tsyganenko.sphcar_08(1., np.radians(90.-lat), np.radians(lon), 0., 0., 0., 1)

XFGEO,YFGEO,ZFGEO,XGSW,YGSW,ZGSW  = tsyganenko.geogsw_08(xgeo, ygeo, zgeo,0,0,0,1) 
#print ' X,Y,Z [GSW] = ',XGSW,YGSW,ZGSW

PARMOD = np.zeros(10)
PARMOD[0:4] = [2, -8, -2, -5]
#XF,YF,ZF,XX,YY,ZZ,Ll = tsyganenko.trace_08(XGSW,YGSW,ZGSW,1.,1.0,0.001, 
    #RLIM,R0,0,PARMOD,tsyganenko.t96_01,tsyganenko.igrf_gsw_08,LMAX) 
XF,YF,ZF,XX,YY,ZZ,Ll = tsyganenko.trace_08(XGSW,YGSW,ZGSW,DIR,DSMAX,ERR, 
    RLIM,R0,0,PARMOD,'T96_01','IGRF_GSW_08',LMAX) 

print ' XF,YF,ZF = ',XF,YF,ZF 

XFGEO,YFGEO,ZFGEO,XGSW,YGSW,ZGSW  = tsyganenko.geogsw_08(0,0,0,XF,YF,ZF,-1) 

print ' XF,YF,ZF [GEO] = ',XFGEO,YFGEO,ZFGEO, np.sqrt( XFGEO**2 + YFGEO**2 + ZFGEO**2 )

gcR, gdcolat, gdlon, xgeo, ygeo, zgeo = tsyganenko.sphcar_08(0., 0., 0., XFGEO,YFGEO,ZFGEO, -1)
#print gcR, gdcolat, gdlon
print 90.-np.degrees(gdcolat), np.degrees(gdlon), gcR

#print XX,YY,ZZ