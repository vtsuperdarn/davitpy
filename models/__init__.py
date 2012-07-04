# Ionospheric and ray tracing models module __init__.py
"""
*******************************
            Models
*******************************
Models module. Contains the following models:
	raydarn: SuperDARN ray tracing code coupled with IRI
	IRI: International Reference Ionosphere 2012
	IGRF: International Geomagnetic Reference Field 2011
	MSIS: Neutral atmosphere model (NRLMSISE-00)
	HWM: Horizontal Wind Model 2007
	COND: conductivity model based on IRI and MSIS

This includes the following submodules:
	rt: ray tracing interface
	iri: iri interface
	igrf: igrf interface
	hwm: hwm interface
	msis: msis interface
	cond: conductivity model interface

*******************************
"""

from models import rt
from models import iri
from models import hwm
from models import msis
from models import cond
from models import igrf
