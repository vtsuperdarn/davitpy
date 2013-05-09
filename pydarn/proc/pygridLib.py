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

.. note::
      Some of these functions are used to make pygrid files.  This assumes that the environment variable DATADIR is set.  If DATADIR is not set, files will be written to the current working directory

.. moduleauthor:: AJ, 20130410
*********************
**Module**: pydarn.proc.pygridLib
*********************
**Classes**:
  * :func:`pydarn.proc.pygridLib.makePygridBatch`
  * :func:`pydarn.proc.pygridLib.mergePygrid`
  * :func:`pydarn.proc.pygridLib.makePygrid`
  * :func:`pydarn.proc.pygridLib.drawPygridMap`
  * :class:`pydarn.proc.pygridLib.pygrid`
  * :class:`pydarn.proc.pygridLib.latcell`
  * :class:`pydarn.proc.pygridLib.pygridCell`
  * :class:`pydarn.proc.pygridLib.mergeVec`
  * :class:`pydarn.proc.pygridLib.pygridVec`
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
    
  ddir = os.environ.get('DATADIR')
  if ddir == None: ddir = os.getcwd()
  baseDir = ddir+'/pygrid'
  codes = pydarn.radar.network().getAllCodes(hemi=hemi)
  myFiles,fileNames = [],[]
  for c in codes:
    fileName = locatePygridFile(sTime.strftime("%Y%m%d"),c)
    if fileName == None : continue

    print 'opening: '+fileName
    ff = openPygrid(fileName,'r')
    if ff != None:
      fileNames.append(fileName)
      myFiles.append(ff)
    else: 
      continue
    
  
  if myFiles == []: return
  
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
    

def makePygrid(sTime,rad,eTime=None,fileType='fitex',interval=60,vb=0,filtered=True, fileName=None, vmax=2000.):
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

  ddir = os.environ.get('DATADIR')
  if ddir == None: ddir = os.getcwd()
  d = ddir+'/pygrid/'+rad
  if not os.path.exists(d):
    os.makedirs(d)
  fileName = d+'/'+sTime.strftime("%Y%m%d")+'.'+rad+'.pygrid.mlt.hdf5'
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
        # myFov = pydarn.radar.radFov.fov(site=site,rsep=myBeam.prm.rsep,\
        #   ngates=ngates+1,nbeams=site.maxbeam)
        myFova = pydarn.radar.radFov.fov(site=site,rsep=myBeam.prm.rsep,\
          ngates=ngates+1, model=None, altitude=300.,coords='mag')

        #create a 2D list to hold coords of RB cells
        coordsList = [[None]*ngates for _ in range(site.maxbeam)]
        #generate new coordsList
        for ii in range(site.maxbeam):
          for jj in range(ngates):
            arr1=[myFova.latCenter[ii][jj],myFova.lonCenter[ii][jj],300]
            arr2=[myFova.latCenter[ii][jj+1],myFova.lonCenter[ii][jj+1],300]
            azm = greatCircleAzm(arr1[0],arr1[1],arr2[0],arr2[1])
            coordsList[ii][jj] = [arr1[0],arr1[1],azm]
        oldCpid = myBeam.cp
        
      #are we in the target time interval?
      if(cTime < t <= bndT): 
        #enter the radar data into the grid
        g.enterData(myBeam,coordsList,vmax=vmax)
        
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
  # if(os.path.exists(fileName+'.bz2')): os.system('rm '+fileName+'.bz2')
  # os.system('bzip2 '+fileName)
      
  
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
  """a class defining a single grid cell
    
  **Members**:
    * **bl** (list of floats): bottom left corner in [mlat,mlon]
    * **tl** (list of floats): bottom left corner in [mlat,mlon]
    * **tr** (list of floats): top right corner in [mlat,mlon]
    * **br** (list of floats): bottom right corner in [mlat,mlon]
    * **center** (list of floats): the center coordinate pair in [mlat,mlon]
    * **nVecs** (int): the number of gridded vectors in this cell
    * **vecs** (list of :class:`pydarn.proc.pygridLib.pygridVec`): a list to hold the pygridVec objects
  
  **Examples**:
    ::

      myCell = pydarn.proc.pygridLib.pygridCell(botLat,topLat,leftLon,rightLon)

  Written by AJ 20120907
  """
  
  def __init__(self,lat1,lat2,mlon1,mlon2,n):
    import math
    
    #define the 4 corners of the cell
    self.bl = [lat1,mlon1]
    self.tl = [lat2,mlon1]
    self.tr = [lat2,mlon2]
    self.br = [lat1,mlon2]
    
    self.index = int(math.floor(lat1))*500+n
    
    #check for a wrap around midnight (causes issues with mean) and then
    #calculate the center point of the cell
    if(mlon2 < mlon1): self.center = [(lat1+lat2)/2.,((24.+mlon1+mlon2)/2.)%24.]
    else: self.center = [(lat1+lat2)/2.,(mlon1+mlon2)/2.]
    
    #initialize number of grid vectors in this cell and the list to hold them
    self.nVecs = 0
    self.allVecs = []
    self.nAvg = 0
    self.avgVecs = []
    self.mrgVec = None
    
    
class latCell:
  """a class to hold the information for a single latitude for a geospatial grid
    
    
  **Members**:
    * **nCells** (int): the number of pygridCells contained in this latCell
    * **botLat** (float): the lower latitude limit of this cell
    * **topLat** (float): the upper latitude limit of this cell
    * **delLon** (float): the step size (in degrees) in longitude for this latCell
    * **cells** (list): a list of the pygridCell objects
    
  **Example:**
    ::

      myLatCell = pydarn.proc.pygridLib.latCell()

  Written by AJ 20120907
  """
  
  def __init__(self,lat):
    import math,models.aacgm as aacgm
    #calculate number of pygridCells, defined in Ruohoniemi and Baker
    self.nCells = int(round(360.*math.sin(math.radians(90.-lat))))
    #bottom latitude boundary of this latCell
    self.botLat = lat
    #latitude step size of this cell
    self.delLon = 24./self.nCells
    #top latitude boundary of this cell
    self.topLat = lat+1
    #list for pygridCell objects
    self.cells = []
    
    #iterate over all longitudinal cells
    for i in range(0,self.nCells):
      #calculate left and right mlon boundaries for this pygridCell
      mlon1=i*24./self.nCells
      mlon2=(i+1)*24./self.nCells
      #create a new pygridCell object and append it to the list
      self.cells.append(pygridCell(self.botLat,self.topLat,mlon1,mlon2,i))
    
    
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
    """method to delete all vectors from a pygrid object

    **Belongs to** :class:`pydarn.proc.pygridLib.pygrid`
    
    **Args**:
      * Nothing.
    **Returns**:
      * Nothing.
      
    **Example**
      ::

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
    """method to go through all grid cells and merge the vectors in cells with more than 1 averaged vector
    
    **Belongs to** :class:`pydarn.proc.pygridLib.pygrid`
    
    **Args**:
      * Nothing.
    **Returns**:
      * Nothing.
      
    **Example**
      ::

        myGrid.mergeVecs()
      
    Written by AJ 20120917
    """
    
    import numpy as np
    import math
    from numpy import linalg as la
    
    #iterate through lats
    for l in self.lats:
      #iterate though cells
      for c in l.cells:
        #see if we have more than 1 average cell
        if(c.nAvg > 1):
          mFlg = False
          #iterate through possible vector combinations
          for i in range(c.nAvg):
            for j in range(i+1,c.nAvg):
              #if we've already merged, don't do anything
              if mFlg: continue

              #get the velocities and azimuths
              v1,v2 = c.avgVecs[i],c.avgVecs[j]
              a1,a2 = math.radians(v1.azm),math.radians(v2.azm)

              #check if the azimuths are too close together
              if(abs(a2-a1) < math.radians(20)): continue
              
              #do a metic inversion to solve simultaneous equations
              arr = np.array([[math.cos(a1),math.sin(a1)],[math.cos(a2),math.sin(a2)]])
              inv = la.inv(arr)
              
              #solve for 2-d vector
              v_n = inv[0][0]*v1.v+inv[0][1]*v2.v
              v_e = inv[1][0]*v1.v+inv[1][1]*v2.v
              vel = math.sqrt(v_n*v_n + v_e*v_e)
              azm = math.degrees(math.atan2(v_e,v_n))
              
              #create the merged vector
              c.mrgVec = mergeVec(vel,np.average(np.array([v1.w_l,v2.w_l])),\
              np.average(np.array([v1.p_l,v2.p_l])),v1.stid,v2.stid,azm)
              self.nMrg += 1
              mFlg = True

          
  def averageVecs(self):
    """method to go through all grid cells and average (actually median) the vectors in cells with more than 1 vector
    
    **Belongs to** :class:`pydarn.proc.pygridLib.pygrid`
    
    **Args**:
      * Nothing.
    **Returns**:
      * Nothing.
      
    **Example**
      ::

        myGrid.averageVecs()
      
    Written by AJ 20120917
    """

    import numpy,math
    
    #iterate over latitudes
    for l in self.lats:
      #iterate over longitudinal cells
      for c in l.cells:
        #check if we have vectors
        if(c.nVecs > 0):
          for i in range(36):
            #empty lists
            ve,vn,a,w,p,vv = [],[],[],[],[],[]
            for v in c.allVecs:
              if int(round(v.azm/10.)%36) == i:
                #append the vector params to the empty lists
                # ve.append(v.v*math.sin(math.radians(v.azm)))
                # vn.append(v.v*math.cos(math.radians(v.azm)))
                vv.append(v.v)
                # a.append(v.azm)
                w.append(v.w_l)
                p.append(v.p_l)

            if vv != []:
              # azm = math.atan2(numpy.median(ve),numpy.median(vn))*180./3.14159
              # vel = math.sqrt(numpy.median(ve)**2+numpy.median(vn)**2)

              #create the average vector
              c.avgVecs.append(pygridVec(numpy.median(vv),numpy.median(w),numpy.median(p),c.allVecs[0].stid, \
                                c.allVecs[0].time,-1,-1,i*10.+5.))
              self.nAvg += 1
              c.nAvg += 1

        
  def enterData(self,myData,coordsList,vmax=2000.):
    """method to insert radar fit data into a pygrid object

    **Belongs to** :class:`pydarn.proc.pygridLib.pygrid`
    
    **Args**:
      * **myData** (:class:`pydarn.sdio.radDataTypes.beamData`): the beam ovject to be insterted into the grid
      * **coordsList** (list of floats): a 2D list containing the coords [lat,lon,azm] corresponding to range-beam cells
    **Returns**:
      * Nothing.
      
    **Example**:
      ::

        myGrid.enterData(myBeam,myCoords)
      
    Written by AJ 20120911
    """
    import math
    import models.aacgm as aacgm
    import time
    
    #go through all scatter points on this beam
    if myData.fit.slist == None: return
    
    for i in range(len(myData.fit.slist)):
      
      #check for good ionospheric scatter
      if myData.fit.gflg[i] == 0 and myData.fit.v[i] != 0.0 and math.fabs(myData.fit.v[i]) < vmax:
        
        #range gate number
        rng = myData.fit.slist[i]
        #get coords of r-b cell
        try: 
          myPos = coordsList[myData.bmnum][rng]
        except:
          continue
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
        lonInd = int(math.floor(mlt1/self.lats[latInd].delLon))
        
        #create a pygridVec object and append it to the list of pygridCells
        self.lats[latInd].cells[lonInd].allVecs.append(pygridVec(abs(myData.fit.v[i]),myData.fit.w_l[i],\
        myData.fit.p_l[i],myData.stid,myData.time,myData.bmnum,rng,azm))
        
        #increment number of vectors in grid cell and pygrid object
        self.lats[latInd].cells[lonInd].nVecs += 1
        self.nVecs += 1
      
      
