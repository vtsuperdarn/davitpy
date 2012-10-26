# IGRF module __init__.py
"""
*******************************
MODULE: models.igrf
*******************************

This module contains the following functions:

  igrf11
       INPUTS:
           - ITYPE:
               - 1 - geodetic (shape of Earth is approximated by a spheroid)
               - 2 - geocentric (shape of Earth is approximated by a sphere)
           - DATE: date in years A.D. (ignored if IOPT=2)
           - ALT: altitude or radial distance in km (depending on ITYPE)
           - XLTI,XLTF,XLTD: latitude (initial, final, increment) in decimal degrees
           - XLNI,XLNF,XLND: longitude (initial, final, increment) in decimal degrees
           - IFL: value for MF/SV flag:
               - 0 for main field (MF)
               - 1 for secular variation (SV)
               - 2 for both
       OUTPUTS:
           - aLat is the latitude of each point
           - aLon is the longitude of each point
           - D is declination in degrees (+ve east)
           - I is inclination in degrees (+ve down)
           - H is horizontal intensity in nT
           - X is north component in nT
           - Y is east component in nT
           - Z is vertical component in nT (+ve down)
           - F is total intensity in nT

  igrf11syn
  
  ddecdm
  
  dmddec
  
Written by Sebastien 20120926
    
*******************************
"""

from igrf import *
