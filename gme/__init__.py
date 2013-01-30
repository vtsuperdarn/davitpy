# Overall module for gme (Geo Magnetic Environment)
"""
gme
***
Module with libraries for dealing with Geo-Magnetic Environment (gme)

This includes the following submodules:
	* **base**: basic things for the gme package
	* **ind**: indices; ie anything that isn't satellite data
	* **sat**: satellite data
	* **ampere**
"""

try: import base
except Exception,e: print e
try: from base import *
except Exception,e: print e

try: import ind
except Exception,e: print e
try: from ind import *
except Exception,e: print e

try: import sat
except Exception,e: print e
try: from sat import *
except Exception,e: print e


try: import ampere
except Exception,e: print e


