# Ionospheric and ray tracing models module __init__.py
"""
*******************************
MODULE: models
*******************************

This module contains the following functions:

	raydarn: SuperDARN ray tracing code coupled with IRI
	
	IRI: International Reference Ionosphere 2012
	
	IGRF: International Geomagnetic Reference Field 2011
	
	MSIS: Neutral atmosphere model (NRLMSISE-00)
	
	HWM: Horizontal Wind Model 2007

*******************************
"""
try:
    import tsyganenko
except:
    print __file__+' -> tsyganenko: import error'
try:
    import igrf
except:
    print __file__+' -> igrf: import error'
try:
    import aacgm
except:
    print __file__+' -> aacgm: import error'
try:
    import iri
except:
    print __file__+' -> iri: import error'
try:
    import msis
except:
    print __file__+' -> msis: import error'
