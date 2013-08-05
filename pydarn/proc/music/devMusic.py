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
#sTime = datetime.datetime(2010,11,19,11,0)
sTime = datetime.datetime(2011,5,9,8,0)
print sTime

#rad is the 3-letter radar code for the radar we want (reqd input)
#rad='bks'
rad='wal'

#NOTE:the rest of the inputs are optional
#eTime is the end time we want to read until
eTime = datetime.datetime(2011,5,9,19,0)
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
#music.defineLimits(dataObj,rangeLimits=[150,500])
music.defineLimits(dataObj,rangeLimits=[600,1200])
#music.defineLimits(dataObj,gateLimits=[13,33])
#music.defineLimits(dataObj,beamLimits=[5,12])
#music.defineLimits(dataObj,timeLimits=[datetime.datetime(2010,11,19,13,30),datetime.datetime(2010,11,19,14,30)])
#music.applyLimits(dataObj)
dataObj.active.applyLimits()

fig = plt.figure(figsize=figsize)
ax  = fig.add_subplot(121)
pydarn.plotting.musicPlot.musicFan(dataObj   ,plotZeros=True,dataSet='originalFit',axis=ax)
ax  = fig.add_subplot(122)
pydarn.plotting.musicPlot.musicFan(dataObj_IS,plotZeros=True,dataSet='originalFit',axis=ax)
fig.savefig(outdir+'/range_comparison.png')

music.beamInterpolation(dataObj,dataSet='limitsApplied')
#music.beamInterpolation(dataObj,limits=[15,45],units='gate')

fig = plt.figure(figsize=figsize)
ax  = fig.add_subplot(121)
pydarn.plotting.musicPlot.musicFan(dataObj,plotZeros=True,dataSet='originalFit',axis=ax)
ax  = fig.add_subplot(122)
pydarn.plotting.musicPlot.musicFan(dataObj,plotZeros=True,axis=ax)
fig.savefig(outdir+'/beam_interp.png')

music.determineRelativePosition(dataObj)

#time = datetime.datetime(2010,11,19,13)
time = sTime

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.plotRelativeRanges(dataObj,time=time,fig=fig)
fig.savefig(outdir+'/ranges.png')

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.timeSeriesMultiPlot(dataObj,dataSet2='limitsApplied',fig=fig)
fig.savefig(outdir+'/multiplot.png')

music.timeInterpolation(dataObj,timeRes=120)

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.timeSeriesMultiPlot(dataObj,dataSet='timeInterpolated',dataSet2='beamInterpolated',fig=fig)
fig.savefig(outdir+'/timeInterp.png')

#Insert simulated data.
music.simulator(dataObj)
timeOfInt = (datetime.datetime(2011,5,9,11,45),datetime.datetime(2011,5,9,15,15))

fig = plt.figure(figsize=figsize)
ax  = fig.add_subplot(111)
pydarn.plotting.musicPlot.musicFan(dataObj,time=datetime.datetime(2010,11,19,13),plotZeros=True,axis=ax)
fig.savefig(outdir+'/simulatedDataFan.png')

fig = plt.figure(figsize=figsize)
ax  = fig.add_subplot(111)
pydarn.plotting.musicPlot.musicRTI(dataObj,plotZeros=True,axis=ax)
fig.savefig(outdir+'/simulatedDataRTI.png')

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.timeSeriesMultiPlot(dataObj,fig=fig,xlim=timeOfInt)
fig.savefig(outdir+'/simulatedMultiPlot.png')

#filt = music.filter(dataObj, dataSet='active', numtaps=501, cutoff_low=0.0003, cutoff_high=0.0012)
dataObj.active.metadata['timeLimits'] = timeOfInt
dataObj.active.applyLimits()

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.timeSeriesMultiPlot(dataObj,fig=fig)
fig.savefig(outdir+'/filtered.png')

#fig = plt.figure(figsize=figsize)
#ax  = fig.add_subplot(111)
#pydarn.plotting.musicPlot.musicFan(dataObj,plotZeros=True,axis=ax)
#fig.savefig(outdir+'/filteredDataFan.png')
#
#fig = plt.figure(figsize=figsize)
#ax  = fig.add_subplot(111)
#pydarn.plotting.musicPlot.musicRTI(dataObj,plotZeros=True,axis=ax)
#fig.savefig(outdir+'/filteredDataRTI.png')
#
#fig = plt.figure(figsize=figsize)
#filt.plotTransferFunction(fig=fig,xmax=0.004)
#fig.savefig(outdir+'/transferFunction.png')
#
#fig = plt.figure(figsize=figsize)
#filt.plotImpulseResponse(fig=fig)
#fig.savefig(outdir+'/impulseResponse.png')

#dataObj.active.metadata['timeLimits'] = (datetime.datetime(2010,11,19,15,6),datetime.datetime(2010,11,19,16,8))
detrend = music.detrend(dataObj, dataSet='active')

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.timeSeriesMultiPlot(dataObj,fig=fig)
fig.savefig(outdir+'/detrendedData.png')

detrend = music.windowData(dataObj, dataSet='active')
fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.timeSeriesMultiPlot(dataObj,fig=fig)
fig.savefig(outdir+'/windowedData.png')

music.calculateFFT(dataObj)

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.spectrumMultiPlot(dataObj,fig=fig,xlim=(-0.0025,0.0025))
fig.savefig(outdir+'/spectrum.png')

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.spectrumMultiPlot(dataObj,fig=fig,plotType='magnitude',xlim=(0,0.0025))
fig.savefig(outdir+'/magnitude.png')

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.spectrumMultiPlot(dataObj,fig=fig,plotType='phase',xlim=(0,0.0025))
fig.savefig(outdir+'/phase.png')

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.plotFullSpectrum(dataObj,fig=fig,xlim=(0,0.0015))
fig.savefig(outdir+'/fullSpectrum.png')

music.calculateDlm(dataObj)

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.plotDlm(dataObj,fig=fig)
fig.savefig(outdir+'/dlm_abs.png')

music.calculateKarr(dataObj)

import pickle
pickle.dump(dataObj,open('dataObj.p','wb'))

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.plotKarr(dataObj,fig=fig)
fig.savefig(outdir+'/karr.png')


#plt.show()
