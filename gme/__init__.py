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
"""
*********************
**Module**: gme
*********************
Module with libraries for dealing with Geo-Magnetic Environment (gme)

This includes the following submodules:
	* **base**: basic things for the gme package
	* **ind**: indices; ie anything that isn't satellite data
	* **sat**: satellite data
    * **rbsp**: rbsp footpoints
"""

try: import base
except Exception,e: 
    print __file__+' -> gme.base: ', e

try: import ind
except Exception,e: 
    print __file__+' -> gme.ind: ', e

try: import sat
except Exception,e: 
    print __file__+' -> gme.sat: ', e

#try: import ampere
#except Exception,e: 
#    print __file__+' -> gme.ampere: ', e

try: import plotting
except Exception,e: 
    print __file__+' -> gme.plot: ', e

try: import isr
except Exception, e:
    print __file__+' -> isr: ', e
