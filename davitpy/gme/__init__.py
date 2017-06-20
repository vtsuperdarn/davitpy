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

# Overall module for gme (Geo Magnetic Environment)
"""gme module

Module with libraries for dealing with Geo-Magnetic Environment (gme)

Modules
--------------------------------------------
base        basic things for the gme package
ind         indices data
isr         incoherent scatter radar data
plotting    plotting for gme data
sat         satellite data
--------------------------------------------

"""
from __future__ import absolute_import
import logging


try: 
    from . import base
except Exception as e: 
    logging.exception(__file__ + ' -> gme.base: ' + str(e))

try: 
    from . import ind
except Exception as e: 
    logging.exception(__file__ + ' -> gme.ind: ' + str(e))

try: 
    from . import sat
except Exception as e: 
    logging.exception(__file__ + ' -> gme.sat: ' + str(e))

try: 
    from . import plotting
except Exception as e: 
    logging.exception(__file__ + ' -> gme.plot: ' + str(e))

try: 
    from . import isr
except Exception as e:
    logging.exception(__file__ + ' -> isr: ' + str(e))
