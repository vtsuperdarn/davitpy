# sat module __init__.py
"""
sat
****
This subpackage contains various fucntions to read and write sattelite data

This includes the following modules:
	* **poes**
"""

try: import poes
except Exception, e: print e
try: from poes import *
except Exception, e: print e