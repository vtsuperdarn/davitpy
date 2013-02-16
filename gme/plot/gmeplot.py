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

"""
*******************************
MODULE: gme.plot.gmeplot
*******************************

This module contains the following functions:

  plotAe
  
  plotDst
*******************************
"""

import pydarn,numpy,math,matplotlib,calendar,datetime,utils,pylab
import matplotlib.pyplot as plot
import matplotlib.lines as lines
from matplotlib.ticker import MultipleLocator
from matplotlib.collections import PolyCollection
from utils.timeUtils import *
from pydarn.sdio import *


def plotAe(myFig,aeList,parameter=['ae'],sTime=None,eTime=None,ylim=None,pos=None):
	"""
	*******************************

	PACKAGE: gme.plot.gmeplot

	FUNCTION: plotAe(myFig,aeList,parameter='ae',sTime=None,eTime=None,ylim=None,pos=None)

	PURPOSE: plots AE/AL/AU/AO indices at panel pos

	INPUTS:
		myFig: the MPL figure we are plotting on
                aeList: aeList data returned from ae.readAe()
                [parameter]: List of AE parameters to plot. Valid values are
                  ['ae','al','au','ao']
                [sTime]: datetime.datetime object for start of plotting.  If not given, earliest data availble from aeList is used.
                [eTime]: datetime.datetime object for end of plotting.  If not given, latest data availble from aeList is used.
                [ylim]: Y-Axis limits
		[pos]: position of the panel

	OUTPUTS:
		NONE
		
	EXAMPLES:
			
	Written by Nathaniel Frissell 20130216

	"""
		
	ax = myFig.add_axes(pos)
#	ax.yaxis.tick_left()
#	ax.yaxis.set_tick_params(direction='out')
#	ax.set_ylim(bottom=10,top=16)
#	ax.yaxis.set_minor_locator(MultipleLocator())
#	ax.yaxis.set_tick_params(direction='out',which='minor')
#	
#	for f in freq:
#		if(f > 16): f = 16
#		if(f < 10): f = 10
#		
#	ax.plot_date(matplotlib.dates.date2num(times), freq, fmt='k-', \
#	tz=None, xdate=True, ydate=False,markersize=2)
#	
#	loc,lab = plot.xticks()
#	plot.xticks(loc,(' '))
#	#customize yticks
#	plot.yticks([10,16],(' '))
#	
#	xmin,xmax = matplotlib.dates.date2num(times[0]),matplotlib.dates.date2num(times[len(times)-1])
#	xrng = (xmax-xmin)
#	inter = int(round(xrng/6.*86400.))
#	inter2 = int(round(xrng/24.*86400.))
#	#format the x axis
#	ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
#	ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))
#	plot.xticks(size=9)
#	
#	plot.figtext(pos[0]-.01,pos[1],'10',ha='right',va='bottom',size=8)
#	plot.figtext(pos[0]-.01,pos[1]+pos[3]-.003,'16',ha='right',va='top',size=8)
#	plot.figtext(pos[0]-.07,pos[1]+pos[3]/2.,'Freq',ha='center',va='center',size=9,rotation='vertical')
#	plot.figtext(pos[0]-.05,pos[1]+pos[3]/2.,'[MHz]',ha='center',va='center',size=7,rotation='vertical')
#	l=lines.Line2D([pos[0]-.04,pos[0]-.04], [pos[1]+.01,pos[1]+pos[3]-.01], \
#	transform=myFig.transFigure,clip_on=False,ls='-',color='k',lw=1.5)                              
#	ax.add_line(l)
