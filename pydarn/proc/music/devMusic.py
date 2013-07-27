# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# Radar data read functions
# ==
# ***
# 
# In this notebook, we will explore how to read radar data. The necessary routines are in `pydarn.sdio`

# <codecell>

############################################
# This code adds davitpy to your python path
# Eventually, this won't be necessary
import sys
sys.path.append('/davitpy')
############################################

# <codecell>

import matplotlib
matplotlib.use('Agg')

import pydarn.sdio
import datetime
import numpy as np

# <codecell>

import pydarn.proc.music as music

from matplotlib import pyplot as plt


outdir = '/data/pymusic/'
figsize = (20,10)

# <codecell>

#the first routine we will call is radDataOpen, which
#establishes a data piepeline.  we will now set up the args.

#sTime is the time we want to start reading (reqd input)
sTime = datetime.datetime(2010,11,19,12,0)
print sTime

#rad is the 3-letter radar code for the radar we want (reqd input)
rad='bks'

#NOTE:the rest of the inputs are optional
#eTime is the end time we want to read until
eTime = datetime.datetime(2010,11,19,16,0)
print eTime

#channel is the radar channel we want data from, eg 'a'
#by default this is None, which will read data from all channels
channel='a'

#cp is the control program id number which we want data from
#by default, this is set to None which reads data from all cpids
cp=None

#fileType specifies the type of data we want.  valid inputs are
#'fitex','fitacf','lmfit','rawacf'.  by default this is 'fitex'
#if a fit type is requested but not found, the code will automatically
#look for other fit types
fileType='fitacf'

#filter is a boolean indicating whether to boxcar filter the data.
#this is onyl valid for fit types, and wont work on mongo data
filtered=False

#src is a string indicating the desired data source.  valid
#inputs are 'mongo','local','sftp'.  by default this is set to
#None which will sequentially try all sources
src=None

################################################################################
# Okay, now lets get the data connection
myPtr = pydarn.sdio.radDataOpen(sTime,rad,eTime=eTime,channel=channel,cp=cp,fileType=fileType,filtered=filtered, src=src)
dataObj_IS  = music.musicArray(myPtr,fovModel='IS')

myPtr = pydarn.sdio.radDataOpen(sTime,rad,eTime=eTime,channel=channel,cp=cp,fileType=fileType,filtered=filtered, src=src)
dataObj     = music.musicArray(myPtr,fovModel='GS')

#pydarn.plotting.musicPlot.musicFan(dataObj,time=datetime.datetime(2010,11,19,13))
music.defineLimits(dataObj,rangeLimits=[200,800])
#music.defineLimits(dataObj,gateLimits=[13,33])
#music.defineLimits(dataObj,beamLimits=[5,12])
#music.defineLimits(dataObj,timeLimits=[datetime.datetime(2010,11,19,13,30),datetime.datetime(2010,11,19,14,30)])
music.applyLimits(dataObj)

music.beamInterpolation(dataObj)
#music.beamInterpolation(dataObj,limits=[15,45],units='gate')

music.determine_relative_position(dataObj)


time = datetime.datetime(2010,11,19,13)
pydarn.plotting.musicPlot.plotRelativeRanges(dataObj,time=time)

#fig = plt.figure(figsize=figsize)
#pydarn.plotting.musicPlot.multiPlot(dataObj,fig=fig)
#fig.savefig(outdir+'/multiplot.png')

fig = plt.figure(figsize=figsize)
ax  = fig.add_subplot(121)
pydarn.plotting.musicPlot.musicFan(dataObj   ,time=datetime.datetime(2010,11,19,13),plotZeros=True,dataSet='originalFit',axis=ax)
ax  = fig.add_subplot(122)
pydarn.plotting.musicPlot.musicFan(dataObj_IS,time=datetime.datetime(2010,11,19,13),plotZeros=True,dataSet='originalFit',axis=ax)
fig.savefig(outdir+'/range_comparison.png')
#
#fig = plt.figure(figsize=figsize)
#ax  = fig.add_subplot(121)
#pydarn.plotting.musicPlot.musicFan(dataObj,time=datetime.datetime(2010,11,19,13),plotZeros=True,dataSet='originalFit',axis=ax)
#ax  = fig.add_subplot(122)
#pydarn.plotting.musicPlot.musicFan(dataObj,time=datetime.datetime(2010,11,19,13),plotZeros=True,axis=ax)
#fig.savefig(outdir+'/beam_interp.png')

#plt.show()
