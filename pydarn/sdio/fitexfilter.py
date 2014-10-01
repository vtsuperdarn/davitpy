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
*************************************
**Module**: pydarn.sdio.fitexfilter
*************************************
Filter fitexfiles natively in python

.. warning::
  This is very SLOW.  We are currently working on this.  We recommend using the c version which is folded into :func:`pydarn.sdio.radDataRead.radDataOpen` 
**Functions**:
  * :func:`pydarn.sdio.fitexfilter.combBeams`
  * :func:`pydarn.sdio.fitexfilter.fitFilter`
  * :func:`pydarn.sdio.fitexfilter.doFilter`
**Classes**:
  * :class:`pydarn.sdio.fitexfilter.Gate`
"""

import pydarn
import numpy as np
import datetime as dt
import utils

import logging
logger = logging.getLogger(__name__)


class Gate(object):
  """A class to represent a single range gate
    
  **Attrs**: 
    * **v** (float): velocity
    * **w_l** (float): spectral width
    * **p_l** (float): power
    * **elv** (float): elevation angle
    * **phi0** (float): phase difference between front and back array

  written by AJ, 20130402
  """
  def __init__(self,fit,i):
    self.v = fit.v[i]
    self.w_l = fit.w_l[i]
    self.p_l = fit.p_l[i]
    self.pwr0 = fit.pwr0[i]
    if fit.elv != None: self.elv = fit.elv[i]
    else: self.elv = None
    if fit.phi0 != None: self.phi0 = fit.phi0[i]
    else: self.phi0 = None

def combBeams(scan):
  """This function combines all repeated beams within a scan into an averaged beam
    
  **Args**: 
    * **scan** (:class:`sdio.scanData`): the scan to be combined
  **Returns**:
    * **outScan** (:class:`sdio.scanData`): the combined scan
  **Example**:
    ::
    
      combBeams(myScan)
    
  written by AJ, 20130402
  """
  outScan = []
  #sort the scan by beam number
  sorted(scan, key=lambda beam: beam.bmnum)

  #see if any beam number repeat
  bcnt = np.zeros(50)
  for b in scan:
    bcnt[b.bmnum] += 1.

  #save any single beams:
  for b in scan:
    if bcnt[b.bmnum] == 1:
      outScan.append(b)

  #average any repeat beams
  for i in range(len(bcnt)):
    beams = []
    #check for more than one
    if bcnt[i] > 1:
      myBeam = pydarn.sdio.beamData()
      for b in scan:
        #append it to beams list
        if b.bmnum == i: beams.append(b)

      nrang = max(beams,key= lambda x:x.prm.nrang)

      #initialize a new beam object
      myBeam.copyData(beams[0])
      for key,val in myBeam.fit.__dict__.iteritems(): 
        setattr(myBeam.fit,key,[])
      myBeam.prm.nrang = nrang

      for j in range(nrang):
        cnt,pos = 0.,float(bcnt[i])
        for b in beams:
          if j in b.fit.slist: cnt += 1.
        if cnt/pos > .5:
          myBeam.fit.slist.append(j)
          myBeam.fit.qflg = 1
          for key in myBeam.fit.__dict__.iterkeys():
            if key == 'qflg' or key == 'gflg' or key == 'slist':
              continue
            arr = []
            for b in beams:
              if j in b.fit.slist:
                ind = b.fit.slist.index(j)
                arr.append(getattr(b.fit, key)[ind])
            setattr(myBeam.fit,key,np.median(arr))
      outScan.append(myBeam)

  sorted(outScan, key=lambda beam: beam.bmnum)

  return outScan


def fitFilter(inFile,outFile,thresh=0.4,vb=False):
  """This function applies a boxcar filter to a fitacf file
    
  .. warning::
    This is **VERY** slow.  We are currently working on improving this.

  **Args**: 
    * **infile** (str): the name of the input fitacf-format file
    * **outfile** (str): the name of the output file
    * **[thresh]** (float): the filter threshold for turning on a R-B cell.  default = 0.4
    * **[vb]** (boolean): a flag indicating verbose output.  default = False
  **Returns**:
    * Nothing.

  **Example**:
    ::
    
      pydarn.sdio.fitexfilter.fitFilter('input.fitacf','output.fitacf',thresh=0.5,vb=True)
    
  written by AJ, 20130402
  """
  inp = pydarn.sdio.radDataOpen(dt.datetime(2010,5,1),'bks',fileName=inFile)

  outp = open(outFile,'w')

  scans = [None, None, None]

  sc = pydarn.sdio.radDataReadScan(inp)
  scans[1] = sc

  sc = pydarn.sdio.radDataReadScan(inp)
  scans[2] = sc

  while sc != None:

    tsc = doFilter(scans,thresh=thresh)

    for b in tsc:
      logger.info(b)
      pydarn.dmapio.writeFitRec(b,utils.datetimeToEpoch(b.time),outp)

    sc = pydarn.sdio.radDataReadScan(inp)
    
    scans[0] = scans[1]
    scans[1] = scans[2]
    scans[2] = sc

  tsc = doFilter(scans,thresh=thresh)
  logger.info(tsc.time)
  for b in tsc:
    pydarn.dmapio.writeFitRec(b,utils.datetimeToEpoch(b.time),outp)

  outp.close()


def doFilter(scans,thresh=.4):
  """This function applies a boxcar filter to consecutive scans
    
  .. warning::
    This is **VERY** slow.  We are currently working on improving this.

  **Args**: 
    * **scans** (list): a list of 3 consecutive scans in time.
    * **[thresh]** (float): the filter threshold for turning on a R-B cell.  default = 0.4
  **Returns**:
    * outScan** (:class:`pydarn.sdio.radDataTypes.scanData`): the filtered scan

  **Example**:
    ::
    
      filtScan = pydarn.sdio.fitexfilter.doFilter(scanList,thresh=0.5)
    
  written by AJ, 20130402
  """
  myScans = []
  for s in scans:
    if s == None:
      myScans.append(None)
    else:
      myScans.append(combBeams(s))

  outScan = pydarn.sdio.scanData()

  #define the weigths array
  w = [[[0. for i in range(3)] for j in range(3)] for k in range(3)]
  for i in range(0,3):
    for j in range(0,3):
      for k in range(0,3):
        if k == 0: tplus = 1
        else: tplus = 0
        if i == 0: rplus = 1
        else: rplus = 0
        if j == 0: bmplus = 1
        else: bmplus = 0
        if i == 0 and j == 0 and k == 0: centplus = 1
        else: centplus = 0

        w[(i+1)%3][(j+1)%3][(k+1)%3] = 1+tplus+rplus+bmplus+centplus



  for b in myScans[1]:
    bmnum = b.bmnum
    #make a new beam
    myBeam = pydarn.sdio.beamData()
    myBeam.copyData(b)
    for key,val in myBeam.fit.__dict__.iteritems(): 
      setattr(myBeam.fit,key,[])

    for r in range(0,b.prm.nrang):

      #boxcar to hold the gates
      box = [[[None for j in range(3)] for k in range(3)] for n in range(3)]

      #iterate through time
      for j in range(0,3):
        #iterate through beam
        for k in range(-1,2):
          #iterate through gate
          for n in range(-1,2):

            #get the scan we are working on
            s = myScans[j]
            if s == None: continue

            #get the beam we are working on
            tbm = None
            for bm in s:
              if bm.bmnum == bmnum + k: tbm = bm
            if tbm == None: continue

            #check if target gate number is in the beam
            if r+n in tbm.fit.slist:
              ind = tbm.fit.slist.index(r+n)
              box[j][k+1][n+1] = Gate(tbm.fit,ind)
            else: box[j][k+1][n+1] = 0

      pts,tot=0.,0.
      v,w_l,p_l,elv,phi0,pwr0 = [],[],[],[],[],[]
      #iterate through time
      for j in range(0,3):
        #iterate through beam
        for k in range(0,3):
          #iterate through gate
          for n in range(0,3):
            bx = box[j][k][n]
            if bx == None: continue
            wt = w[j][k][n]
            tot += wt
            if bx != 0:
              pts += wt
              for m in range(0,wt):
                v.append(bx.v)
                pwr0.append(bx.pwr0)
                w_l.append(bx.w_l)
                p_l.append(bx.p_l)
                if bx.elv: elv.append(bx.elv)
                if bx.phi0: phi0.append(bx.phi0)

      #check if we meet the threshold
      if pts/tot >= thresh:
        myBeam.fit.slist.append(r)
        myBeam.fit.qflg.append(1)
        myBeam.fit.v.append(np.median(v))
        myBeam.fit.w_l.append(np.median(w_l))
        myBeam.fit.p_l.append(np.median(p_l))
        myBeam.fit.pwr0.append(np.median(pwr0))
        if elv != []: myBeam.fit.elv.append(np.median(elv))
        if phi0 != []: myBeam.fit.phi0.append(np.median(phi0))
        if np.median(w_l) > -3.*np.median(v)+90.:
          myBeam.fit.gflg.append(0)
        else: myBeam.fit.gflg.append(1)

    outScan.append(myBeam)

  return outScan
















