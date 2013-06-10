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
.. module:: sdDataTypes
   :synopsis: the classes needed for reading, writing, and storing processed radar data (grid, map)
.. moduleauthor:: AJ, 20130108
*********************
**Module**: pydarn.sdio.sdDataTypes
*********************
**Classes**:
  * :class:`pydarn.sdio.sdDataTypes.sdDataPtr`
  * :class:`pydarn.sdio.sdDataTypes.sdBaseData`
  * :class:`pydarn.sdio.sdDataTypes.gridData`
  * :class:`pydarn.sdio.sdDataTypes.mapData`
"""


from utils import twoWayDict
alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m', \
          'n','o','p','q','r','s','t','u','v','w','x','y','z']

class sdDataPtr():
  """A class which contains a pipeline to a data source
  
  **Attrs**:
    * **ptr** (file or mongodb query object): the file pointer
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): start time of the request
    * **eTime** (`datetime <http://tinyurl.com/bl352yx>`_): end time of the request
    * **hemi** (str): station id of the request
    * **fType** (str): the file type, 'grid', 'map'
  **Methods**:
    * Nothing.
    
  Written by AJ 20130607
  """
  def __init__(self,ptr=None,sTime=None,eTime=None,hemi=None,fType=None):
    self.ptr = ptr
    self.sTime = sTime
    self.eTime = eTime
    self.hemi = hemi
    self.fType = None
    
  def __repr__(self):
    myStr = 'sdDataPtr\n'
    for key,var in self.__dict__.iteritems():
      myStr += key+' = '+str(var)+'\n'
    return myStr

class sdBaseData():
  """a base class for the porocessed SD data types.  This allows for single definition of common routines
  
  **ATTRS**:
    * Nothing.
  **METHODS**:
    * :func:`updateValsFromDict`: converts a dict from a dmap file to baseData
    
  Written by AJ 20130607
  """
  
  def updateValsFromDict(self, aDict):
    """A function to to fill an sdBaseData object with the data in a dictionary that is returned from the reading of a dmap file
    
    .. note::
      In general, users will not need to use this.
      
    **Args**:
      * **aDict (dict):** the dictionary containing the radar data
    **Returns**
      * Nothing.
      
    Written by AJ 20121130
    """
    
    import datetime as dt
    syr,smo,sdy,shr,smt,ssc = 1,1,1,1,1,1
    eyr,emo,edy,ehr,emt,esc = 1,1,1,1,1,1

    for key,val in aDict.iteritems():
      if key == 'start.year': syr = aDict['start.year']
      elif key == 'start.month': smo = aDict['start.month']
      elif key == 'start.day': sdy = aDict['start.day']
      elif key == 'start.hour': shr = aDict['start.hour']
      elif key == 'start.minute': smt = aDict['start.minute']
      elif key == 'start.second': ssc = int(aDict['start.second'])
      elif key == 'end.year': eyr = aDict['end.year']
      elif key == 'end.month': emo = aDict['end.month']
      elif key == 'end.day': edy = aDict['end.day']
      elif key == 'end.hour': ehr = aDict['end.hour']
      elif key == 'end.minute': emt = aDict['end.minute']
      elif key == 'end.second': esc = int(aDict['end.second'])

      elif 'vector.' in key:
        if isinstance(self,sdVector):
          name = key.replace('vector.','')
          name = name.replace('.','')
          if hasattr(self, name): setattr(self,name,val)

      elif 'model.' in key:
        if isinstance(self,sdModel):
          name = key.replace('model.','')
          name = name.replace('.','')
          if hasattr(self, name): setattr(self,name,val)

      elif '+' in key:
        name = key.replace('+','p')
        if hasattr(self, name): setattr(self,name,val)

      else:
        name = key.replace('.','')
        if hasattr(self, name):
          setattr(self,name,val)

    if isinstance(self,gridData) or isinstance(self,mapData):
      self.sTime = dt.datetime(syr,smo,sdy,shr,smt,ssc)
      self.eTime = dt.datetime(eyr,emo,edy,ehr,emt,esc)

  def __repr__(self):
    myStr = ''
    for key,val in self.__dict__.iteritems():
      myStr += str(key)+' = '+str(val)+'\n'
    return myStr

class gridData(sdBaseData):
  """ a class to contain a record of gridded data, extends :class:`pydarn.sdio.sdDataTypes.sdBaseData`
  
  **Attrs**:
    * **chnnum** (int): number of channels?
  
  **Example**: 
    ::
    
      myGrid = pydarn.sdio.gridData()
    
  Written by AJ 20130607
  """

  #initialize the struct
  def __init__(self, dataDict=None):
    self.sTime = None
    self.eTime = None
    self.stid = None
    self.channel = None
    self.nvec = None
    self.freq = None
    self.programid = None
    self.noisemean = None
    self.noisesd = None
    self.gsct = None
    self.vmin = None
    self.vmax = None
    self.pmin = None
    self.pmax = None
    self.wmin = None
    self.wmax = None
    self.vemin = None
    self.vemax = None
    self.vector = sdVector(dataDict=dataDict)

    if dataDict != None:
      self.updateValsFromDict(dataDict)

class mapData(sdBaseData):
  """ a class to contain a record of map potential data, extends :class:`pydarn.sdio.sdDataTypes.sdBaseData`
  
  **Attrs**:
    * **chnnum** (int): number of channels?
  
  **Example**: 
    ::
    
      myMap = pydarn.sdio.mapData()
    
  Written by AJ 20130607
  """

  #initialize the struct
  def __init__(self, dataDict=None):
    self.sTime = None
    self.eTime = None
    self.dopinglevel = None
    self.modelwt = None
    self.errorwt = None
    self.IMFflag = None
    self.IMFdelay = None
    self.IMFBx = None
    self.IMFBy = None
    self.IMFBz = None
    self.modelangle = None
    self.modellevel = None
    self.hemi = None
    self.fitorder = None
    self.latmin = None
    self.chisqr = None
    self.chisqrdat = None
    self.rmserr = None
    self.lonshft = None
    self.latshft = None
    self.mltstart = None
    self.mltend = None
    self.mltav = None
    self.potdrop = None
    self.potdroperr = None
    self.potmax = None
    self.potmaxerr = None
    self.potmin = None
    self.potminerr = None
    self.grid = gridData(dataDict=dataDict)

    self.N = None
    self.Np1 = None
    self.Np2 = None
    self.Np3 = None
    self.model = sdModel(dataDict=dataDict)

    if(dataDict != None): 
      self.updateValsFromDict(dataDict)
        
class sdVector(sdBaseData):
  """ a class to contain vector records of gridded data, extends :class:`pydarn.sdio.sdDataTypes.sdBaseData`
  
  **Attrs**:
    * **chnnum** (int): number of channels?
  
  **Example**: 
    ::
    
      myGrid = pydarn.sdio.gridData()
    
  Written by AJ 20130607
  """

  #initialize the struct
  def __init__(self, dataDict=None):
    self.mlat = None
    self.mlon = None
    self.kvect = None
    self.stid = None
    self.channel = None
    self.index = None
    self.velmedian = None
    self.velsd = None
    self.pwrmedian = None
    self.pwrsd = None
    self.wdtmedian = None
    self.wdtsd = None

    if(dataDict != None):
      self.updateValsFromDict(dataDict)

class sdModel(sdBaseData):
  """ a class to contain model records of map poential data, extends :class:`pydarn.sdio.sdDataTypes.sdBaseData`
  
  **Attrs**:
    * **chnnum** (int): number of channels?
  
  **Example**: 
    ::
    
      myGrid = pydarn.sdio.gridData()
    
  Written by AJ 20130607
  """

  #initialize the struct
  def __init__(self, dataDict=None):
    self.mlat = None
    self.kvect = None
    self.velmedian = None
    self.boundarymlat = None
    self.boundarymlon = None

    if(dataDict != None): self.updateValsFromDict(dataDict)