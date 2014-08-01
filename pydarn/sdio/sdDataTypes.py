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
    self.fd = None 

  def close(self):
    import os
    if self.ptr is not None:
      self.ptr.close()
      self.fd=None
 
 
  def __repr__(self):
    myStr = 'sdDataPtr\n'
    for key,var in self.__dict__.iteritems():
      myStr += key+' = '+str(var)+'\n'
    return myStr

  def __del__(self):
    self.close()

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
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): start time of the record
    * **eTime** (`datetime <http://tinyurl.com/bl352yx>`_): end time of the record
    * **stid** (list): a list of the station IDs in the record, by radar
    * **nvec** (list): a list of the number of vectors in the record, by radar
    * **freq** (list): a list of the transmit frequencies, in kHz, by radar
    * **programid** (list): a list of the program IDs, by radar
    * **noisemean** (list): a list of the mean noise level, by radar
    * **noisesd** (list): a list of the standard deviation of noise level, by radar
    * **gsct** (list): a list of flags indicating whether ground scatter was excluded from the gridding, by radar
    * **vmin** (list): a list of minimum allowed Doppler velocity, by radar
    * **vmax** (list): a list of the maximum allowed Doppler velocity, by radar
    * **pmin** (list): a list of the minimum allowed power level, by radar
    * **pmax** (list): a list of the maximum allowed power level, by radar
    * **wmin** (list): a list of the minimum allowed spectral width, by radar
    * **wmax** (list): a list of the maximum allowed spectral width, by radar
    * **vemin** (list): a list of the minimum allowed velocity error, by radar
    * **vemax** (list): a list of the maximum allowed velocity error, by radar
    * **vector** (:class:`pydarn.sdio.sdDataTypes.sdVector`): an object containing all of the vector.* elements from the file
  
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

  .. note::
    I don't know what `alot <http://4.bp.blogspot.com/_D_Z-D2tzi14/S8TRIo4br3I/AAAAAAAACv4/Zh7_GcMlRKo/s400/ALOT.png>`_ of these attributes mean.  If you do, please add them in.

  **Attrs**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): start time of the record
    * **eTime** (`datetime <http://tinyurl.com/bl352yx>`_): end time of the record
    * **dopinglevel** (int): 
    * **modelwt** (int): 
    * **errorwt** (int): 
    * **IMFflag** (int): 
    * **IMFdelay** (int): 
    * **IMFBx** (float): the Bx component of the IMF
    * **IMFBy** (float): the By component of the IMF
    * **IMFBz** (float): the Bz component of the IMF
    * **modelangle** (string): 
    * **modellevel** (string): 
    * **hemi** (int): the hemisphere, 1=north, 2=south?
    * **fitorder** (int): the order of the spherical harmonic fit
    * **latmin** (float): the minimum latitude in the spherical harmonic fit
    * **chisqr** (double): 
    * **chisqrdat** (double): 
    * **rmserr** (double): an object containing all of the vector.* elements from the file
    * **lonshft** (double): 
    * **latshft** (double): 
    * **mltstart** (double): 
    * **mltend** (double): 
    * **mltav** (double): 
    * **potdrop** (double): the cross polar cap potential, in volts
    * **potdroperr** (int): the error in the cross polar cap potential 
    * **potmax** (double): 
    * **potmaxerr** (double): 
    * **potmin** (double): 
    * **potminerr** (double): 
    * **grid** (:class:`pydarn.sdio.sdDataTypes.gridData`): an object to hold all of the grid data in the record 
    * **N** (list): 
    * **Np1** (list): 
    * **Np2** (list): 
    * **Np3** (list): 
    * **model** (:class:`pydarn.sdio.sdDataTypes.sdModel`): an object to hold the model.* data in the record
  
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
    * **mlat** (list): the magnetic longitude of the grid cells
    * **mlon** (list): the magnetic longitude of the grid cells
    * **kvect** (list): the kvectors of the vectors in the grid cells
    * **stid** (int): the station ID of the radar which made the measurement of the vector in the grid cell
    * **channel** (int): the channel of the radar which made the measurement of the vector in the grid cell
    * **index** (int): 
    * **velmedian** (int): the median velocity of the vector
    * **velsd** (float): the standard deviation of the velocity of the vector
    * **pwrmedian** (float): the median power of the vector
    * **pwrsd** (float): the standard devation of the power of the vector
    * **wdtmedian** (string): the median spectral width of the vector
    * **wdtsd** (string): the standard devation on the spectral width of the vector
  
  **Example**: 
    ::
    
      myVec = pydarn.sdio.sdVector()
    
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

  .. note::
    I don't know what `alot <http://4.bp.blogspot.com/_D_Z-D2tzi14/S8TRIo4br3I/AAAAAAAACv4/Zh7_GcMlRKo/s400/ALOT.png>`_ of these attributes mean.  If you do, please add them in.

  **Attrs**:
    * **mlat** (list): 
    * **kvect** (list): 
    * **velmedian** (list): 
    * **boundarymlat** (int): 
    * **boundarymlon** (int):

  **Example**: 
    ::
    
      myMod = pydarn.sdio.sdModel()
    
  Written by AJ 20130607
  """

  #initialize the struct
  def __init__(self, dataDict=None):
    self.mlat = None
    self.mlon = None
    self.kvect = None
    self.velmedian = None
    self.boundarymlat = None
    self.boundarymlon = None

    if(dataDict != None): self.updateValsFromDict(dataDict)

