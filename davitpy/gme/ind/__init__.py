# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# ind module __init__.py
"""
ind
---

This subpackage contains various fucntions to read and write Geomagnetic Indices

Modules
----------------------------
ae      AE data
dst     Dst data
kp      Kp data
omni    OMNI data (from ACE)
symasy  SYM/ASY data
----------------------------

"""
import logging

try: import kp
except Exception, e: logging.exception(e)
try: from kp import *
except Exception, e: logging.exception(e)

try: import omni
except Exception, e: logging.exception(e)
try: from omni import *
except Exception, e: logging.exception(e)


try: import dst
except Exception, e: logging.exception(e)
try: from dst import *
except Exception, e: logging.exception(e)

try: import ae
except Exception, e: logging.exception(e)
try: from ae import *
except Exception, e: logging.exception(e)

try: import symasy
except Exception, e: logging.exception(e)
try: from symasy import *
except Exception, e: logging.exception(e)
