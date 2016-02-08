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
pydarn.sdio.fitexfilter
-------------------------------------
Filter fitexfiles natively in python

Functions
----------
combBeams
fitFilter
doFilter

Classes
--------
Gate : A class to hold limited fitted and interferometer values for a single
       radar, time, beam, and range gate


Notes
---------
This is very SLOW.   We recommend using the c version which is folded into
the sdio function radDataRead.radDataOpen
"""

import numpy as np
import datetime as dt
from davitpy import utils
import logging

class Gate(object):
    """A class to represent a single range gate
  
    Parameters
    ------------
    v : (float)
        velocity in m/s
    w_l : (float)
        spectral width in m/s
    p_l :(float)
        power in dB
    elv : (float)
        elevation angle in degrees
    phi0 : (float)
        phase difference between front and back array in degrees

    written by AJ, 20130402
    """

    def __init__(self, fit, i):
        self.v = fit.v[i]
        self.w_l = fit.w_l[i]
        self.p_l = fit.p_l[i]
        self.pwr0 = fit.pwr0[i]
        self.elv = None if fit.elv is None else fit.elv[i]
        self.phi0 = None if fit.phi0 is None else fit.phi0[i]

def combBeams(scan):
    """This function combines all repeated beams within a scan into a
    single beam with medians for the velocity, elevation, phase lag, and
    exponentially fitted power and spectral width.

    Parameters
    -----------
    scan : (list or sdio.scanData object)
        A list of beams in a scan

    Returns
    --------
    outscan (sdio.scanData object)
        The averaged scan

    written by AJ, 20130402
    """
    from davitpy import pydarn
    outscan = []
    # sort the scan by beam number
    sorted(scan, key=lambda beam: beam.bmnum)

    # see if any beam number repeat
    bcnt = np.zeros(50)
    for b in scan:
        bcnt[b.bmnum] += 1.

    # save any single beams:
    for b in scan:
        if bcnt[b.bmnum] == 1:
            outscan.append(b)

    # average any repeat beams
    for i in range(len(bcnt)):
        beams = []
        # check for more than one
        if bcnt[i] > 1:
            beam = pydarn.sdio.beamData()
            for b in scan:
                # append it to beams list
                if b.bmnum == i:
                    beams.append(b)

            nrang = max(beams, key= lambda x:x.prm.nrang)

            # initialize a new beam object
            beam.copyData(beams[0])
            for key,val in beam.fit.__dict__.iteritems(): 
                setattr(beam.fit, key, [])
            beam.prm.nrang = nrang

            for j in range(nrang):
                cnt = 0.0
                pos = float(bcnt[i])
                for b in beams:
                    if j in b.fit.slist:
                        cnt += 1.
                if cnt / pos > .5:
                    beam.fit.slist.append(j)
                    beam.fit.qflg = 1
                    for key in beam.fit.__dict__.iterkeys():
                        if key == 'qflg' or key == 'gflg' or key == 'slist':
                            continue
                        arr = []
                        for b in beams:
                            if j in b.fit.slist:
                                ind = b.fit.slist.index(j)
                                arr.append(getattr(b.fit, key)[ind])
                        setattr(beam.fit, key, np.median(arr))
            outscan.append(beam)

    sorted(outscan, key=lambda beam: beam.bmnum)

    return outscan

def fitFilter(infile, outfile, thresh=0.4):
    """This function applies a boxcar filter to a fitacf file.  Currently
    hardwired to load Blackstone on 1-5-2010.  The fix to this is stored in
    0.5-release_fitexFilter_change branch in aburrell's fork.

    Parameters
    ------------
    infile : (str)
        The name of the input fitacf-format file
    outfile : (str)
        The name of the output file
    thresh : (float)
        The filter threshold for turning on a R-B cell.  (default=0.4)

    Returns
    ---------
    Void

    Note
    -----
    This is VERY slow

    written by AJ, 20130402
    """
    from davitpy import pydarn
    inp = pydarn.sdio.radDataOpen(dt.datetime(2010,5,1), 'bks', fileName=infile)

    outp = open(outfile, 'w')

    scans = [None, None, None]

    sc = pydarn.sdio.radDataReadScan(inp)
    scans[1] = sc

    sc = pydarn.sdio.radDataReadScan(inp)
    scans[2] = sc

    while sc != None:
        tsc = doFilter(scans, thresh=thresh)

        for b in tsc:
            logging.info("processing: {:}".format(b))
            pydarn.dmapio.writeFitRec(b, utils.datetimeToEpoch(b.time), outp)

        sc = pydarn.sdio.radDataReadScan(inp)
        scans[0] = scans[1]
        scans[1] = scans[2]
        scans[2] = sc

    tsc = doFilter(scans, thresh=thresh)
    logging.info("current at time: {:}".format(tsc.time))

    for b in tsc:
        pydarn.dmapio.writeFitRec(b, utils.datetimeToEpoch(b.time), outp)

    outp.close()
    return

def doFilter(scans, thresh=.4):
    """This function applies a boxcar filter to consecutive scans

    Note
    -----
    This is VERY slow.

    Parameters
    -----------
    scans : (list)
        a list of 3 consecutive scans, sorted by time.
    thresh : (float)
        The filter threshold for turning on a R-B cell.  (default=0.4)

    Returns
    --------
    outscan : (list or radDataTypes.scanData object)
        The filtered scan

    written by AJ, 20130402
    """
    from davitpy import pydarn

    scans = []
    for s in scans:
        if s == None:
            scans.append(None)
        else:
            scans.append(combBeams(s))

    outscan = pydarn.sdio.scanData()

    # define the weigths array
    w = [[[0.0 for i in range(3)] for j in range(3)] for k in range(3)]
    for i in range(0,3):
        for j in range(0,3):
            for k in range(0,3):
                tplus = 1 if k == 0 else 0
                rplus = 1 if i == 0 else 0
                bmplus = 1 if j == 0 else 0
                centplus = 1 if i == 0 and j == 0 and k == 0 else 0

                w[(i+1)%3][(j+1)%3][(k+1)%3] = 1+tplus+rplus+bmplus+centplus

    for b in scans[1]:
        bmnum = b.bmnum
        # make a new beam
        beam = pydarn.sdio.beamData()
        beam.copyData(b)
        for key,val in beam.fit.__dict__.iteritems(): 
            setattr(beam.fit,key,[])

        for r in range(0,b.prm.nrang):
            # boxcar to hold the gates
            box = [[[None for j in range(3)] for k in range(3)]
                   for n in range(3)]

            # iterate through time
            for j in range(0,3):
                # iterate through beam
                for k in range(-1,2):
                    # iterate through gate
                    for n in range(-1,2):
                        # get the scan we are working on
                        s = scans[j]
                        if s == None:
                            continue

                        # get the beam we are working on
                        tbm = None
                        for bm in s:
                            if bm.bmnum == bmnum + k:
                                tbm = bm
                        if tbm == None:
                            continue

                        # check if target gate number is in the beam
                        if r+n in tbm.fit.slist:
                            ind = tbm.fit.slist.index(r + n)
                            box[j][k+1][n+1] = Gate(tbm.fit, ind)
                        else:
                            box[j][k+1][n+1] = 0

            pts = 0.0
            tot = 0.0
            v = list()
            w_l = list()
            p_l = list()
            elv = list()
            phi0 = list()
            pwr0 = list()
            # iterate through time
            for j in range(0,3):
                # iterate through beam
                for k in range(0,3):
                    # iterate through gate
                    for n in range(0,3):
                        bx = box[j][k][n]
                        if bx == None:
                            continue
                        wt = w[j][k][n]
                        tot += wt
                        if bx != 0:
                            pts += wt
                            for m in range(0, wt):
                                v.append(bx.v)
                                pwr0.append(bx.pwr0)
                                w_l.append(bx.w_l)
                                p_l.append(bx.p_l)
                                if bx.elv:
                                    elv.append(bx.elv)
                                if bx.phi0:
                                    phi0.append(bx.phi0)

            # check if we meet the threshold
            if pts / tot >= thresh:
                beam.fit.slist.append(r)
                beam.fit.qflg.append(1)
                beam.fit.v.append(np.median(v))
                beam.fit.w_l.append(np.median(w_l))
                beam.fit.p_l.append(np.median(p_l))
                beam.fit.pwr0.append(np.median(pwr0))
                if len(elv) > 0:
                    beam.fit.elv.append(np.median(elv))
                if len(phi0) > 0:
                    beam.fit.phi0.append(np.median(phi0))

                # Re-evaluate the groundscatter flag
                gflg = 0 if np.median(w_l) > -3.0 * np.median(v) + 90.0 else 1
                beam.fit.gflg.append(gflg)

        outscan.append(beam)

    return outscan
















