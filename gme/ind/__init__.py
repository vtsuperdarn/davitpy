# ind module __init__.py
"""
ind
****
This subpackage contains various fucntions to read and write Geomagnetic Indices

This includes the following modules:

	* **kp**
	* **omni**
"""

try: import kp
except Exception, e: print e
try: from kp import *
except Exception, e: print e

try: import omni
except Exception, e: print e
try: from omni import *
except Exception, e: print e


try: import dst
except Exception, e: print e
try: from dst import *
except Exception, e: print e

try: import ae
except Exception, e: print e
try: from ae import *
except Exception, e: print e

try: import symasy
except Exception, e: print e
try: from symasy import *
except Exception, e: print e