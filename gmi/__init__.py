# Overall module for gmi (Geo Magnetic Indices)
"""
*******************************
            GMI
*******************************
Module with libraries for dealing with gmi

This includes the following submodules:
	kp
	
	ampere

	omni

*******************************
"""

try: import kp
except Exception,e: print e

try: from kp import *
except Exception,e: print e

try: import ampere
except Exception,e: print e

try: import omni
except Exception,e: print e

try: from omni import *
except Exception,e: print e
