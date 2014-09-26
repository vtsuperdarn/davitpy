# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: gme.sat
*********************
This subpackage contains various fucntions to read and write sattelite data

This includes the following modules:
	* **poes**
    * **rbsp**
"""
try: from goes import *
except Exception, e:
    print __file__+' -> gme.sat.goes: ', e

try: from poes import *
except Exception, e:
    print __file__+' -> gme.sat.poes: ', e

try: from rbsp import *
except Exception, e:
    print __file__+' -> gme.sat.rbsp: ', e
