import pydarn
import numpy as np

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
      for f in myBeam.fit: f = []
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
  
def fitFilter(scans,thresh=.4):

  myScans = []
  for s in scans:
    if s == None:
      myScans.append(None)
    else:
      myScans.append(combBeams(s))

  for b in myScans[1]:
    for i in range(b.fit.slist)
      box = [[[None for i in range(3)] for j in range(3)] for k in range(3)]



