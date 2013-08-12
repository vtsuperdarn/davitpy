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
.. module:: gmeplot
   :synopsis: A module for reading, writing, and storing kp Data
.. moduleauthor:: Nathaniel Frissell
*********************
**Module**: gme.plotting.gmeplot
*********************
  * :func:`gme.plotting.plotGME`
"""

def __get_iterable(x):
  if isinstance(x, str):
    return [x]
  else:
    return x


def plotGME(gmiList,parameter=None,sTime=None,eTime=None,ymin=None,ymax=None,NoX=False,NoY=False,NoCredit=False,NoLegend=False,legendSize=None):
  """plot ground magnetic indicies, including AE, SYMH, ASYMH, and DST.

  **Args**:
    * **gmiList**: gmiList object returned from ae.readAe(), symAsy.readSymAsy(), or dst.readDst()
    * **[parameter]**: List of parameters to plot. Valid values are: 

      * aeList:     ['ae', 'al', 'au', 'ao'] (Defaults to 'ae')
      * symAsyList: ['symh', 'symd', 'asymh', 'asymd'] (Defaults to 'symh')
      * dstList:    ['dst']

    * **[sTime]**: datetime.datetime object for start of plotting.  If not given, earliest data availble from aeList is used.
    * **[eTime]**: datetime.datetime object for end of plotting.  If not given, latest data availble from aeList is used.
    * **[ymin]**: Y-Axis minimum limit
    * **[ymax]**: Y-Axis maximum limit
    * **[NoX]**:  Suppress X-Axis Titles and Ticks
    * **[NoY]**:  Suppress Y-Axis Titles and Ticks
    * **[NoCredit]**: Suppress printing source of data on plot
    * **[NoLegend]**: Suppress a legend if more than one parameter is plotted
    * **[legendSize]**: Character size of the legend

  **Returns**:
    * Nothing.

  .. note::
    If a matplotlib figure currently exists, it will be modified by this routine.  If not, a new one will be created.

  Written by Nathaniel Frissell 20130216
  """
  #import pydarn,numpy,math,matplotlib,calendar,datetime,utils,pylab
  import matplotlib.pyplot as mp
  import matplotlib.dates as md
        
  times = [gmiList[x].time for x in range(len(gmiList))]
  dataSet = (gmiList[0]).dataSet
  if dataSet == 'AE':
    ae    = [gmiList[x].ae   for x in range(len(gmiList))]
    al    = [gmiList[x].al   for x in range(len(gmiList))]
    au    = [gmiList[x].au   for x in range(len(gmiList))]
    ao    = [gmiList[x].ao   for x in range(len(gmiList))]
    data  = {'ae': ae,'al':al,'au':au,'ao':ao}
    if parameter == None: parameter = ['ae']
  elif dataSet == 'Sym/Asy':
    symh  = [gmiList[x].symh for x in range(len(gmiList))]
    symd  = [gmiList[x].symd for x in range(len(gmiList))]
    asyh  = [gmiList[x].asyh for x in range(len(gmiList))]
    asyd  = [gmiList[x].asyd for x in range(len(gmiList))]
    data  = {'symh':symh, 'symd':symd, 'asyh':asyh, 'asyd': asyd}
    if parameter == None: parameter = ['symh']
  elif dataSet == 'Dst':
    dst   = [gmiList[x].dst  for x in range(len(gmiList))]
    data  = {'dst':dst}
    if parameter == None: parameter = ['dst']

  parameter = __get_iterable(parameter)

  figure = mp.gcf()
  if figure == None: figure = mp.figure()

  for param in parameter:
    if data.has_key(param.lower()) == False: continue
    mp.plot(times,data[param.lower()],label=param.upper())

  mp.ylim(ymin,ymax)
  mp.xlim(sTime,eTime)

  ax = mp.gca()

  if NoY == False:
    if len(parameter) == 1:
      ylabel = (parameter[0]).upper() + ' [nT]'
    else:
      ylabel = ','.join([x.upper() for x in parameter]) + ' [nT]'
      if NoLegend == False: ax.legend(prop={'size':legendSize})
    mp.ylabel(ylabel)
  else:
    ax.set_yticklabels([]) 

  if NoX == False:
    ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
    mp.xlabel('Time [UT]')
    figure.autofmt_xdate()
  else:
    ax.set_xticklabels([]) 

  if NoCredit == False:
    s = 'Source: Kyoto WDC'
    xpos = 0.01
    ypos = 0.91
    ax.annotate(s,xy=(xpos,ypos),xycoords="axes fraction",horizontalalignment="left",fontsize='x-small')
