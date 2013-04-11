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
.. module:: pygridLib
   :synopsis: the classes and functions used for pygrid files

.. moduleauthor:: AJ, 20130410
*********************
**Module**: pydarn.proc.pygridLib
*********************
**Classes**:
  * :func:`makePygridBatch`
  * :func:`mergePygrid`
  * :func:`makePygrid`
  * :func:`drawPygridMap`
  * :class:`pygrid`
  * :class:`latcell`
  * :class:`pygridCell`
  * :class:`mergeVec`
  * :class:`pygridVec`
"""


from pydarn.sdio.pygridIo import *
from pydarn.sdio.radDataRead import *
from utils.timeUtils import *
from utils.geoPack import *

def makePygridBatch(sTime,eTime=None,hemi='both',interval=120,merge=1,vb=0,filter=1):
  """ performs makePygrid for a range of dates on several radars

  **Args**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the start time
    * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): the end time.  If this equals None, eDateStr is assigned the value of sDateStr.  default = None
    * **[hemi]** (str): the hemispheres for which to do the gridding, allowable values are 'north', 'south', and 'both'.  default = 'both'
    * **[interval]** (int): the gridding interval in seconds, default = 120
    * **[merge]** (int): a flag indicating whether to merge the gridded data or not.  default: 1
    * **[vb]** (int): a flag for verbose output.  default = 0
  **Returns**:
    * Nothing.
    
  **Example**:
    ::
      
      import datetime as dt
      pydarn.proc.makePygridBatch(dt.datetime(2011,1,1))
    
  Written by AJ 20120925
  """
  
  import datetime as dt,pydarn
  #check for valie date input
  assert(isinstance(sTime,dt.datetime)),\
    'error, sTime must be a datetime object'
  if(eTime == None): eTime = sTime+dt.timedelta(days=1)
  else:
    assert(isinstance(eTime,dt.datetime)),\
      'error, eTime must be None or a datetime object'
  #check for valid hemi input
  if(hemi != None):
    assert(hemi == 'north' or hemi == 'south' or hemi == 'both'),\
      "error, acceptable values for hemi are 'north', 'south', or 'both'"
    #get 3 letter radar codes
    if(hemi == 'both'):
      rads = pydarn.radar.network().getAllCodes()
    else:
      rads = pydarn.radar.network().getAllCodes(hemi=hemi)
    #iterate from start to end date
    cDate = dt.datetime(sTime.year,sTime.month,sTime.day)
    while(cDate <= dt.datetime(eTime.year,eTime.month,eTime.day)):
      #iterate through the radars
      for r in rads:
        if(vb == 1): print r, cDate
        ##make the pygrid files
        #if(dt.datetime(sTime.year,sTime.month,sTime.day) < dt.datetime(eTime.year,eTime.month,eTime.day)):
          #makePygrid(sTime,r,eTime=eTime,vb=vb,interval=interval,filter=filter)
        #else: 
          #makePygrid(sTime,r,eTime=eTime,vb=vb,interval=interval,filter=filter)
      #merge the pygrid files if desired
      if(merge == 1):
        if(hemi == 'both'):
          mergePygrid(cDate,hemi='north',vb=vb,interval=interval)
          mergePygrid(cDate,hemi='south',vb=vb,interval=interval)
        else:
          mergePygrid(cDate,hemi=hemi,vb=vb,interval=interval)
      #increment current datetime by 1 day
      cDate += dt.timedelta(days=1)
  
  
def mergePygrid(sTime,eTime=None,hemi='north',interval=120,vb=0):
  """reads several grid files, combines them, and merges vectors where possible.

  **Args**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the start time.
    * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): the end time.  If this is None, it will be set to 1 day after sTime.  default = None
    * **[hemi]** (str): the hemisphere you wish to work on.  valid inputs are 'north' and 'south'.  default = 'north'
    * **[interval]** (int): the time interval at which to do the merging in seconds; default = 120
  **Returns**:
    * **Nothing**

  **Example**:
    ::
      
      import datetime as dt
      pydarn.proc.mergePygrid(dt.datetime(2011,1,1),hemi='south')
    
    
  Written by AJ 20120807
  """
  import datetime as dt,pydarn,os,string,math
  
  #convert date string, start time, end time to datetime
  if(eTime == None): eTime = sTime + dt.timedelta(days=1)
    
  baseDir = os.environ['DATADIR']+'/pygrid'
  codes = pydarn.radar.network().getAllCodes(hemi=hemi)
  myFiles,fileNames = [],[]
  for c in codes:
    fileName = locatePygridFile(sTime.strftime("%Y%m%d"),c)
    if(fileName == None): continue
    print 'opening: '+fileName
    fileNames.append(fileName)
    myFiles.append(openPygrid(fileName,'r'))
    
  
  if(myFiles == []): return
  
  d = baseDir+'/'+hemi
  if not os.path.exists(d):
    os.makedirs(d)
  outName = d+'/'+sTime.strftime("%Y%m%d")+'.'+hemi+'.pygrid.hdf5'
  outFile = openPygrid(outName,'w')
  
  g = pygrid()
  cTime = sTime
  #until we reach the designated end time
  while cTime < eTime:
    #boundary time
    bndT = cTime+dt.timedelta(seconds=interval)
    #remove vectors from the grid object
    g.delVecs()
    #verbose option
    if(vb==1): print cTime
    for f in myFiles:
      readPygridRec(f,g,datetimeToEpoch(cTime),datetimeToEpoch(bndT))
      
    if(g.nVecs > 0):
      g.sTime = cTime
      g.eTime = bndT
      g.mergeVecs()
      g.nVecs = 0
      for l in g.lats:
        for c in l.cells:
          c.allVecs = [];
          c.nVecs = 0;
      writePygridRec(outFile,g)
    
    #reassign the current time we are at
    cTime = bndT
  
  #close the files
  closePygrid(outFile)
  for f in myFiles: closePygrid(f)
  
  for f in fileNames:
    print 'zipping: '+f
    os.system('bzip2 '+f)
    

def makePygrid(sTime,rad,eTime=None,fileType='fitex',interval=60,vb=0,filtered=True, fileName=None):
  """a function to read in fitted radar data and put it into a geospatial grid
  
  **INPUTS**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the start time do want to grid
    * **rad** (str): the 3 letter radar code, e.g. 'bks'
    * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): the last time that you want data for.  if this is set to None, it will be set to 1 day after sTime.  default = None
    * **[fileType]** (str): 'fitex', 'fitacf', or 'lmfit'; default = 'fitex'
    * **[interval]** (int): the time interval at which to do the gridding in seconds; default = 60
    * **[filtered] (bool)**: True to boxcar filter, False for normal data; default = True
    
  **Returns**:
    * Nothing.

  **Example**:
    ::
    
      import datetime as dt
      pydarn.proc.makePygrid(dt.datetime(2011,1,1),'bks')

    
  Written by AJ 20120807

  """
  import pydarn,math,datetime as dt,models.aacgm as aacgm,os

  
  if eTime == None: eTime = sTime+dt.timedelta(days=1)
  
  #read the radar data
  myFile = radDataOpen(sTime,rad,eTime=eTime,fileType=fileType,filtered=filtered,fileName=fileName)
  if myFile == None: 
    print 'could not find data requested, returning None'
    return None
  
  #get a radar site object
  site = pydarn.radar.network().getRadarByCode(rad).getSiteByDate(sTime)

  #a list for all the grid objects
  myGrids = []
  #create a pygrid object
  g = pygrid()
  #initialize start time
  cTime = sTime
  lastInd = 0
  

  
  oldCpid = -999999999999999
  myBeam = radDataReadRec(myFile)
  if myBeam == None:
    print 'no data available'
    return None

  d = os.environ['DATADIR']+'/pygrid/'+rad
  if not os.path.exists(d):
    os.makedirs(d)
  fileName = d+'/'+sTime.strftime("%Y%m%d")+'.'+rad+'.pygrid.hdf5'
  #open a pygrid file
  gFile = openPygrid(fileName,'w')
  
  #until we reach the designated end time
  while cTime < eTime:
    if myBeam == None : break
    
    #boundary time
    bndT = cTime+dt.timedelta(seconds=interval)
    #remove vectors from the grid object
    g.delVecs()
    #verbose option
    if(vb==1): print cTime
    #iterate through the radar data
    while(myBeam.time < bndT):
      
      #current time of radar data
      t = myBeam.time
      
      #check for a control program change
      if(myBeam.cp != oldCpid and myBeam.channel == 'a'):
        #get possibly new ngates
        ngates = max([site.maxgate,myBeam.prm.nrang])
        #gereate a new FOV
        myFov = pydarn.radar.radFov.fov(site=site,rsep=myBeam.prm.rsep,\
          ngates=ngates+1,nbeams=site.maxbeam)
        myFova = pydarn.radar.radFov.fov(site=site,rsep=myBeam.prm.rsep,\
          ngates=ngates+1, model=None, altitude=300.)

        #create a 2D list to hold coords of RB cells
        coordsList = [[None]*ngates for _ in range(site.maxbeam)]
        #generate new coordsList
        for ii in range(site.maxbeam):
          for jj in range(ngates):
            arr1=aacgm.aacgmConv(myFov.latCenter[ii][jj],myFov.lonCenter[ii][jj],300,0)
            arr2=aacgm.aacgmConv(myFov.latCenter[ii][jj+1],myFov.lonCenter[ii][jj+1],300,0)
            arr3=aacgm.aacgmConv(myFova.latCenter[ii][jj],myFova.lonCenter[ii][jj],300,0)
            arr4=aacgm.aacgmConv(myFova.latCenter[ii][jj+1],myFova.lonCenter[ii][jj+1],300,0)
            azm = greatCircleAzm(arr3[0],arr3[1],arr4[0],arr4[1])
            coordsList[ii][jj] = [arr1[0],arr1[1],azm]
        oldCpid = myBeam.cp
        
      #are we in the target time interval?
      if(cTime < t <= bndT): 
        #enter the radar data into the grid
        g.enterData(myBeam,coordsList)
        
      #read the next record
      myBeam = radDataReadRec(myFile)
      
      if(myBeam == None): break

    #if we have > 0 gridded vector
    if(g.nVecs > 0):
      #record some information
      g.sTime = cTime
      g.eTime = bndT
      #average is LOS vectors
      g.averageVecs()
      #write to the hdf5 file
      writePygridRec(gFile,g)
      
    #reassign the current time we are at
    cTime = bndT
    
    
  closePygrid(gFile)
  if(os.path.exists(fileName+'.bz2')): os.system('rm '+fileName+'.bz2')
  os.system('bzip2 '+fileName)
      
  
class pygridVec(object):
  """a class defining a single gridded vector
    
  **ATTRS**:
    * **v** : Doppler velocity
    * **w_l** : spectral width
    * **p_l** : power
    * **stid** : station id number
    * **time** : time of the measurement
    * **bmnum** : beam number of the measurement
    * **rng** : range gate of the measurement
    * **azm** : azimuth of the measurement
  **METHODS**:
    * Nothing.

  **Example**:
    ::
    
      myVel = pydarn.proc.pygridLib.pygridVec(v,w_l,p_l,stid,time,bmnum,rng,azm):

  Written by AJ 20120907

  """
  
  def __init__(self,v,w_l,p_l,stid,time,bmnum,rng,azm):
    
    #initialize all the values, pretty self-explanatory
    self.v = v
    self.w_l = w_l
    self.p_l = p_l
    self.stid = stid
    self.time = time
    self.azm = azm
    self.bmnum = bmnum
    self.rng = rng
    
    
class mergeVec:
  """a class defining a single merged vector
  
  DECLARATION: 
    myVel = pydarn.proc.pygridLib.pygridVec(v,w_l,p_l,stid,time,bmnum,rng,azm):
    
  **Attrs**:
    * **v**: Doppler velocity
    * **w_l**: spectral width
    * **p_l**: power
    * **stids**: station id list
    * **azm**: azimuth of the measurement
  **METHODS**
    * Nothing.

  **Example**:
    ::
    
      myVel = pydarn.proc.pygridLib.pygridVec(v,w_l,p_l,stid,time,bmnum,rng,azm):
      
  Written by AJ 20120918

  """
  
  def __init__(self,v,w_l,p_l,stid1,stid2,azm):
    
    #initialize all the values, pretty self-explanatory
    self.v = v
    self.w_l = w_l
    self.p_l = p_l
    self.stids = [stid1,stid2]
    self.azm = azm
    
    
class pygridCell:
  """

  PACKAGE: pydarn.proc.pygridLib
  
  CLASS: pygridCell
  
  PURPOSE: a class defining a single grid cell

  DECLARATION: 
    myCell = pydarn.proc.pygridLib.pygridCell(botLat,topLat,leftLon,rightLon)
    
  MEMBERS:
    bl : bottom left corner in [lat,mlt]
    tl : bottom left corner in [lat,mlt]
    tr : top right corner in [lat,mlt]
    br : bottom right corner in [lat,mlt]
    center : the center coordinate pair in [lat,mlt]
    nVecs : the number of gridded vectors in this cell
    vecs : a list to hold the pygridVec objects
    
  Written by AJ 20120907

  """
  
  def __init__(self,lat1,lat2,mlt1,mlt2,n):
    import math
    
    #define the 4 corners of the cell
    self.bl = [lat1,mlt1]
    self.tl = [lat2,mlt1]
    self.tr = [lat2,mlt2]
    self.br = [lat1,mlt2]
    
    self.index = int(math.floor(lat1))*500+n
    
    #check for a wrap around midnight (causes issues with mean) and then
    #calculate the center point of the cell
    if(mlt2 < mlt1): self.center = [(lat1+lat2)/2.,(24.-mlt1+mlt2)/2.]
    else: self.center = [(lat1+lat2)/2.,(mlt1+mlt2)/2.]
    
    #initialize number of grid vectors in this cell and the list to hold them
    self.nVecs = 0
    self.allVecs = []
    self.nAvg = 0
    self.avgVecs = []
    self.mrgVec = None
    
    
class latCell:
  """

  PACKAGE: pydarn.proc.pygridLib
  
  CLASS: latCell
  
  PURPOSE: a class to hold the information for a single latitude
    for a geospatial grid
  
  DECLARATION: 
    myLat = pydarn.proc.pygridLib.latCell()
    
  MEMBERS:
    nCells : the number of pygridCells contained in this latCell
    botLat : the lower latitude limit of thsi cell
    topLat : the upper latitude limit of this cell
    delLon : the step size (in degrees) in longitude for this
      latCell
    cells : a list of the pygridCell objects
    
  Written by AJ 20120907

  """
  
  def __init__(self,lat):
    import math,models.aacgm as aacgm
    #calculate number of pygridCells, defined in Ruohoniemi and Baker
    self.nCells = int(round(360.*math.sin(math.radians(90.-lat))))
    #bottom latitude boundary of this latCell
    self.botLat = lat
    #latitude step size of this cell
    self.delMlt = 24./self.nCells
    #top latitude boundary of this cell
    self.topLat = lat+1
    #list for pygridCell objects
    self.cells = []
    
    #iterate over all longitudinal cells
    for i in range(0,self.nCells):
      #calculate left and right mlt boundaries for this pygridCell
      mlt1=i*24./self.nCells
      mlt2=(i+1)*24./self.nCells
      #create a new pygridCell object and append it to the list
      self.cells.append(pygridCell(self.botLat,self.topLat,mlt1,mlt2,i))
    
    
class pygrid(object):
  """

  PACKAGE: pydarn.proc.pygridLib
  
  CLASS: pygrid
  
  PURPOSE:the top level class for defining a geospatial grid for 
    velocity gridding

  DECLARATION: 
    myGrid = pygrid()
    
  MEMBERS:
    lats: a list of latCell objects
    nLats: an integer number equal to the number of
      items in the lats list
    delLat: the spacing between latCell objects
    nVecs: the number of gridded vectors in the pygrid object
    
  Written by AJ 20120907

  """
  
  def __init__(self):
    import math 
    
    self.nVecs = 0
    self.nAvg = 0
    self.nMrg = 0
    self.lats = []
    self.nLats = 90
    
    #latitude step size
    self.delLat = 90./self.nLats
    
    self.sTime = None
    self.eTime = None
    
    #for all the latitude steps
    for i in range(0,self.nLats):
      #create a new latCell object and append it to the list
      l = latCell(float(i)*self.delLat)
      self.lats.append(l)
      
  def delVecs(self):
    """

    PACKAGE: pydarn.proc.pygridLib
    
    FUNCTION: pygrid.delVecs():
    
    BELONGS TO: CLASS: pydarn.proc.pygridLib.pygrid
    
    PURPOSE: delete all vectors from a pygrid object
    
    INPUTS:
      None
      
    OUTPUTS:
      None
      
    EXAMPLE:
      myGrid.delVecs()
      
    Written by AJ 20120911

    """
    self.nVecs = 0
    self.nAvg = 0
    self.nMrg = 0
    
    for l in self.lats:
      for c in l.cells:
        c.allVecs = []
        c.nVecs = 0
        c.avgVecs = []
        c.nAvg = 0
        c.mrgVec = None
      
  def mergeVecs(self):
    """
    
    PACKAGE: pydarn.proc.pygridLib
    
    FUNCTION: pygrid.mergeVecs():
    
    BELONGS TO: CLASS: pydarn.proc.pygridLib.pygrid

    go through all grid cells and average the vectors in 
    cells with more than 1 vector

    INPUTS:
      None
      
    OUTPUTS:
      None
      
    EXAMPLE:
      myGrid.averageVecs()
      
    Written by AJ 20120917

    """
    
    import numpy as np
    import math
    from numpy import linalg as la
    
    for l in self.lats:
      for c in l.cells:
        if(c.nAvg > 1):
          v1,v2 = c.avgVecs[0],c.avgVecs[1]
          a1,a2 = math.radians(v1.azm),math.radians(v2.azm)
          if(abs(a2-a1) < math.radians(20)): continue
          
          arr = np.array([[math.cos(a1),math.sin(a1)],[math.cos(a2),math.sin(a2)]])
          inv = la.inv(arr)
          
          v_n = inv[0][0]*v1.v+inv[0][1]*v2.v
          v_e = inv[1][0]*v1.v+inv[1][1]*v2.v
          
          vel = math.sqrt(v_n*v_n + v_e*v_e)
          azm = math.degrees(math.atan2(v_e,v_n))
          
          
          c.mrgVec = mergeVec(vel,np.average(np.array([v1.w_l,v2.w_l])),\
          np.average(np.array([v1.p_l,v2.p_l])),v1.stid,v2.stid,azm)
          
          self.nMrg += 1

          
  def averageVecs(self):
    """
    
    PACKAGE: pydarn.proc.pygridLibLib
    
    FUNCTION: pygrid.averageVecs():
    
    BELONGS TO: CLASS: pydarn.proc.pygridLibLib.pygrid
    
    PURPOSE: go through all grid cells and average the vectors in 
    cells with more than 1 vector
    
    INPUTS:
      None
      
    OUTPUTS:
      None
      
    EXAMPLE:
      myGrid.averageVecs()
      
    Written by AJ 20120917

    """
    import numpy,math
    
    for l in self.lats:
      for c in l.cells:
        if(c.nVecs > 0):
          ve,vn,a,w,p = [],[],[],[],[]
          # tmpVe = [[]*1 for _ in range(50)]
          # tmpVn = [[]*1 for _ in range(50)]
          # tmpA = [[]*1 for _ in range(50)]
          # tmpW,tmpP = [],[]
          for v in c.allVecs:
            ve.append(v.v*math.sin(math.radians(v.azm)))
            vn.append(v.v*math.cos(math.radians(v.azm)))
            a.append(v.azm)
            w.append(v.w_l)
            p.append(v.p_l)
            # tmpVe[v.bmnum].append(v.v*math.sin(math.radians(v.azm)))
            # tmpVn[v.bmnum].append(v.v*math.sin(math.radians(v.azm)))
            # tmpA[v.bmnum].append(v.azm)
            # tmpW.append(v.w_l)
            # tmpP.append(v.p_l)
          # v,a = [],[]
          # for i in range(50):
          #   if(tmpV[i] != []):
          #     v.append(numpy.mean(numpy.array(tmpV[i])))
          #     a.append(numpy.mean(numpy.array(tmpA[i])))
          azm = math.atan2(numpy.median(ve),numpy.median(vn))
          vel = math.sqrt(numpy.median(ve)**2+numpy.median(vn)**2)
          c.avgVecs.append(pygridVec(vel,numpy.median(w),numpy.median(p),c.allVecs[0].stid,c.allVecs[0].time,-1,-1,azm))
          self.nAvg += 1
          c.nAvg += 1

        
  def enterData(self,myData,coordsList):
    """
    
    PACKAGE: pydarn.proc.pygridLib
    
    FUNCTION pygrid.enterData():
    
    BELONGS TO: CLASS: pydarn.proc.pygridLib.pygrid
    
    PURPOSE: inserts radar fitacf data into a pygrid object
    
    INPUTS:
      myData: a pydarn.io.radDataTypes.beam object
      coordsList: a 2D list containing the coords [lat,lon,azm] 
        corresponding to range-beam cells
        
    OUTPUTS:
      None
      
    EXAMPLE:
      myGrid.enterData(myBeam,myCoords)
      
    Written by AJ 20120911

    """
    import math,models.aacgm as aacgm,time
    
    #go through all scatter points on this beam
    for i in range(len(myData.fit.slist)):
      
      #check for good ionospheric scatter
      if(myData.fit.gflg[i] == 0 or myData.fit.gflg[i] == 2 and myData.fit.v[i] != 0.0):
        
        #range gate number
        rng = myData.fit.slist[i]
        #get coords of r-b cell
        myPos = coordsList[myData.bmnum][rng]
        #latitudinal index
        latInd = int(math.floor(myPos[0]/self.delLat))
        
        #convert coords to mlt
        mlt1 = aacgm.mltFromEpoch(datetimeToEpoch(myData.time),myPos[1])
        
        #print myData['fit']['v'][i],myPos[2]
        #compensate for neg. direction is away from radar
        if(myData.fit.v[i] > 0.): azm = (myPos[2]+180+360)%360
        else: azm = (myPos[2]+360)%360
        #print abs(myData['fit']['v'][i]),azm
        #print ""
        #longitudinal index
        lonInd = int(math.floor(mlt1/self.lats[latInd].delMlt))
        
        #create a pygridVec object and append it to the list of pygridCells
        self.lats[latInd].cells[lonInd].allVecs.append(pygridVec(abs(myData.fit.v[i]),myData.fit.w_l[i],\
        myData.fit.p_l[i],myData.stid,myData.time,myData.bmnum,rng,azm))
        
        #increment number of vectors in grid cell and pygrid object
        self.lats[latInd].cells[lonInd].nVecs += 1
        self.nVecs += 1
      
      
