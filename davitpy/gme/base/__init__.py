# -*- coding: utf-8 -*-
# base module __init__.py
"""
base
----

This subpackage contains various fucntions to read and write Kp index
DEV: functions/modules/classes with a * have not been developed yet

Modules
-----------------------------------------
fillGmedb   create and populate databases
gmeBase     base class for gme data
-----------------------------------------

"""
import logging

try: import gmeBase
except Exception,e: logging.exception(e)

try: from gmeBase import *
except Exception,e: logging.exception(e)

try: import fillGmedb
except Exception,e: logging.exception(e)

try: from fillGmedb import *
except Exception,e: logging.exception(e)
