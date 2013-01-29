# Overall module for gmi (Geo Magnetic Indices)
"""
*******************************
            GME
*******************************
Module with libraries for dealing with Geo-Magnetic Environment (gme)

This includes the following submodules:
	* **base**
	* **kp**
	* **ampere**
	* **omni**
	
	

*******************************
"""

try: import base
except Exception,e: print e
try: from base import *
except Exception,e: print e

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

