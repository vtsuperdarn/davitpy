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

# Plot module __init__.py
"""
*******************************
            PLOT
*******************************
This subpackage contains various plotting routines for DaViT-py

This includes the following function(s):
	*rti
		rti data plots
	*scan
		scan data plots
	*freq
		frequency plot
	*noise
		noise plot
	
This includes the following module(s):
	*map
		empty maps in polar projections with the following function(s):
			*overlay_radar
			*overlay_fov
			*overlay_terminator
			*overlay_daynight

*******************************
"""

from rti import *
from plotUtils import *
from map import *
from printRec import *
from fan import *
from pygridPlot import *
import pygridPlot
