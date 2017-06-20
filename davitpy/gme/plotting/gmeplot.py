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
"""gme plotting module

A module for reading, writing, and storing kp Data

Functions
----------------------------------
plotGME     plot ground indicies
plotOMNI    plot solar wind params
----------------------------------

Module Author: Nathaniel Frissell

"""
import logging


def __get_iterable(x):
  if isinstance(x, str):
    return [x]
  else:
    return x


def plotGME(gmiList,parameter=None,sTime=None,eTime=None,ymin=None,ymax=None,
            NoX=False,NoY=False,NoCredit=False,NoLegend=False,legendSize=None):
  """Plot ground magnetic indicies, including AE, SYMH, ASYMH, and DST.

  Parameters
  ----------
  gmiList : gmiList object
        returned from ae.readAe(), symAsy.readSymAsy(), or dst.readDst()
  parameter : Optional[list]
        List of parameters to plot. Valid values are: 
            aeList:     ['ae', 'al', 'au', 'ao'] (Defaults to 'ae')
            symAsyList: ['symh', 'symd', 'asymh', 'asymd'] (Defaults to 'symh')
            dstList:    ['dst']
  sTime : Optional[datetime.datetime]
        Start of plotting.  If not given, earliest data availble from aeList is used.
  eTime : Optional[datetime.datetime]
        End of plotting.  If not given, latest data availble from aeList is used.
  ymin : Optional[ ]
        Y-Axis minimum limit
  ymax : Optional[ ]
        Y-Axis maximum limit
  NoX : Optional[bool]
        Suppress X-Axis Titles and Ticks
  NoY : Optional[bool]
        Suppress Y-Axis Titles and Ticks
  NoCredit : Optional[bool]
        Suppress printing source of data on plot
  NoLegend : Optional[bool]
        Suppress a legend if more than one parameter is plotted
  legendSize : Optional[ ]
        Character size of the legend

  Returns
  -------
  Nothing.

  Notes
  -----
  If a matplotlib figure currently exists, it will be modified by this routine.  If not, a
  new one will be created.

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


def plotOmni(omniList,parameter=None,sTime=None,eTime=None,ymin=None,
             ymax=None,yLabel=False,NoX=False,NoY=False,NoCredit=False):
  """OMNI solar wind parameters, including interplanetary magnetic field and solar wind velocity.

  Parameters
  ----------
  omniList : omniList
        object returned from ind.readOmni()
  parameter : Optional[list]
        List of parameters to plot. Valid values are: 
            omniList:     ['ae', 'al', 'au', 'bx', 'bye', 'bze', 'bym', 'bzm', 'vxe', 'vye', 'vze',
                           'symh', 'symd', 'asyh', 'asyd', 'np', 'e', 'pdyn', 'temp', 'beta',
                           'bmagavg', 'machnum', 'flowspeed'] (Defaults to 'bzm')
  sTime : Optional[datetime.datetime]
        Start of plotting.  If not given, earliest data availble from omniList is used.
  eTime : Optional[datetime.datetime]
        End of plotting.  If not given, latest data availble from omniList is used.
  ymin : Optional[ ]
        Y-Axis minimum limit
  ymax : Optional[ ]
        Y-Axis maximum limit
  yLabel : Optional[bool]
        Custom Y-Axis Title
  NoX : Optional[bool]
        Suppress X-Axis Titles and Ticks
  NoY : Optional[bool]
        Suppress Y-Axis Titles and Ticks
  NoCredit : Optional[bool]
        Suppress printing source of data on plot

  Returns
  -------
  Nothing.

  Notes
  -----
  If a matplotlib figure currently exists, it will be modified by this routine.  If not, a new one will be created.

  Written by Evan Thomas 20131001

  """
  import matplotlib.pyplot as mp
  import matplotlib.dates as md
        
  times = [omniList[x].time for x in range(len(omniList))]
  dataSet = (omniList[0]).dataSet
  if dataSet == 'Omni':
    ae    = [omniList[x].ae   for x in range(len(omniList))]
    al    = [omniList[x].al   for x in range(len(omniList))]
    au    = [omniList[x].au   for x in range(len(omniList))]
    bx    = [omniList[x].bx   for x in range(len(omniList))]
    bye   = [omniList[x].bye  for x in range(len(omniList))]
    bze   = [omniList[x].bze  for x in range(len(omniList))]
    bym   = [omniList[x].bym  for x in range(len(omniList))]
    bzm   = [omniList[x].bzm  for x in range(len(omniList))]
    vxe   = [omniList[x].vxe  for x in range(len(omniList))]
    vye   = [omniList[x].vye  for x in range(len(omniList))]
    vze   = [omniList[x].vze  for x in range(len(omniList))]
    symh  = [omniList[x].symh for x in range(len(omniList))]
    symd  = [omniList[x].symd for x in range(len(omniList))]
    asyh  = [omniList[x].asyh for x in range(len(omniList))]
    asyd  = [omniList[x].asyd for x in range(len(omniList))]
    np    = [omniList[x].np   for x in range(len(omniList))]
    e     = [omniList[x].e    for x in range(len(omniList))]
    pdyn  = [omniList[x].pDyn for x in range(len(omniList))]
    temp  = [omniList[x].temp for x in range(len(omniList))]
    beta  = [omniList[x].beta for x in range(len(omniList))]
    bmagavg = [omniList[x].bMagAvg  for x in range(len(omniList))]
    machnum = [omniList[x].machNum for x in range(len(omniList))]
    flowspeed = [omniList[x].flowSpeed for x in range(len(omniList))]
    data  = {'ae':ae, 'al':al, 'au':au, 'bx':bx, 'bye':bye, 'bze':bze, 'bym':bym, 'bzm':bzm, 'vxe':vxe, 'vye':vye, 'vze':vze
	     , 'symh':symh, 'symd':symd, 'asyh':asyh, 'asyd':asyd, 'np':np, 'e':e, 'pdyn':pdyn, 'temp':temp, 'beta':beta
	     , 'bmagavg':bmagavg, 'machnum':machnum, 'flowspeed':flowspeed}
    if parameter == None: parameter = 'bzm'
  
  assert(not isinstance(parameter,list)), logging.error("parameter must not be a list, eg 'bzm'")
  
  parameter = __get_iterable(parameter)
  
  figure = mp.gcf()
  if figure == None: figure = mp.figure()
  
  for param in parameter:
    if data.has_key(param.lower()) == False: logging.info(param.lower())
    if data.has_key(param.lower()) == False: continue
    mp.plot(times,data[param.lower()],label=param.upper())
  
  mp.ylim(ymin,ymax)
  mp.xlim(sTime,eTime)

  ax = mp.gca()

  if NoY == False:
    if yLabel == False:
      ylabel = (parameter[0]).upper() + ' [nT]'
      if(parameter[0] == 'ae'): ylabel = 'AE [nT]'
      if(parameter[0] == 'al'): ylabel = 'AL [nT]'
      if(parameter[0] == 'au'): ylabel = 'AU [nT]'
      if(parameter[0] == 'bx'): ylabel = 'Bx [nT]'
      if(parameter[0] == 'bye'): ylabel = 'By GSE [nT]'
      if(parameter[0] == 'bze'): ylabel = 'Bz GSE [nT]'
      if(parameter[0] == 'bym'): ylabel = 'By GSM [nT]'
      if(parameter[0] == 'bzm'): ylabel = 'Bz GSM [nT]'
      if(parameter[0] == 'vxe'): ylabel = 'Vx GSE [km/s]'
      if(parameter[0] == 'vye'): ylabel = 'Vy GSE [km/s]'
      if(parameter[0] == 'vze'): ylabel = 'Vz GSE [km/s]'
      if(parameter[0] == 'symh'): ylabel = 'SymH [nT]'
      if(parameter[0] == 'symd'): ylabel = 'SymD [nT]'
      if(parameter[0] == 'asyh'): ylabel = 'AsyH [nT]'
      if(parameter[0] == 'asyd'): ylabel = 'AsyD [nT]'
      if(parameter[0] == 'np'): ylabel = r'n [cm$^{-3}$]'
      if(parameter[0] == 'e'): ylabel = 'E [mV/m]'
      if(parameter[0] == 'pdyn'): ylabel = 'Pdyn [nPa]'
      if(parameter[0] == 'temp'): ylabel = 'T [K]'
      if(parameter[0] == 'beta'): ylabel = 'beta'
      if(parameter[0] == 'bmagavg'): ylabel = 'Average |B| [nT]'
      if(parameter[0] == 'machnum'): ylabel = 'Alfven mach number'
      if(parameter[0] == 'flowspeed'): ylabel = 'Flow Speed [km/s]'
    else:
      ylabel = yLabel
    mp.ylabel(ylabel)
  else:
    ax.set_yticklabels([]) 
  
  if NoX == False:
    ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
    mp.xlabel('Time [UT]')
    figure.autofmt_xdate()
  else:
    ax.set_xticklabels([]) 
  
  minVal = min( x for x in data[parameter[0]] if x is not None)
  if minVal < 0:
    mp.axhline(y=0, color='k', linestyle='dashed')
    
  if NoCredit == False:
    s = 'Source: NASA SPDF'
    xpos = 0.01
    ypos = 0.91
    ax.annotate(s,xy=(xpos,ypos),xycoords="axes fraction",horizontalalignment="left",fontsize='x-small')
