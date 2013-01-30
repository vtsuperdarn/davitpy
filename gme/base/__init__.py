# base module __init__.py
"""
****
base
****
This subpackage contains various fucntions to read and write Kp index
DEV: functions/modules/classes with a * have not been developed yet

This includes the following modules:
	gmeBase

*******************************
"""

try: import gmeBase
except Exception,e: print e

try: from gmeBase import *
except Exception,e: print e

try: import fillGmedb
except Exception,e: print e

try: from fillGmedb import *
except Exception,e: print e
