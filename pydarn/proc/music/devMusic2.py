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

import pickle

outdir = '/data/pymusic/'
figsize = (20,10)


dataObj = pickle.load(open('dataObj.p','rb'))

fig = plt.figure(figsize=figsize)
ax  = fig.add_subplot(111)
pydarn.plotting.musicPlot.musicFan(dataObj,dataSet='filtered',plotZeros=True,axis=ax,scale=(-1.,1.))
fig.savefig(outdir+'/filteredDataFan.png')

fig = plt.figure(figsize=figsize)
ax  = fig.add_subplot(111)
pydarn.plotting.musicPlot.musicRTI(dataObj,dataSet='filtered',plotZeros=True,axis=ax,scale=(-1,1))
fig.savefig(outdir+'/filteredDataRTI.png')

fig = plt.figure(figsize=figsize)
pydarn.plotting.musicPlot.plotKarr(dataObj,fig=fig)
fig.savefig(outdir+'/karr.png')
