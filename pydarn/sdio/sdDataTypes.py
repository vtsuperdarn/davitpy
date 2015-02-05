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
    
    **Public Attrs**:
      * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): start time of the request
      * **eTime** (`datetime <http://tinyurl.com/bl352yx>`_): end time of the request
      * **hemi** (str): station id of the request
      * **fType** (str): the file type, 'grid', 'map'
      * **recordIndex** (dict): look up dictionary for file offsets for scan times
  
    **Private Attrs**:
      * **ptr** (file or mongodb query object): the data pointer (different depending on mongodo or dmap)
      * **fd** (int): the file descriptor 
      * **filename** (str): name of the file opened
      * **nocache** (bool):  do not use cached files, regenerate tmp files 
      * **src** (str):  local or sftp 
  
    **Methods**:
      * **open** 
      * **close** 
      * **createIndex** : Index the offsets for all records and scan boundaries
      * **offsetSeek** : Seek file to requested byte offset, checking to make sure it in the record index
      * **offsetTell** : Current byte offset
      * **rewind** : rewind file back to the beginning 
      * **readRec** : read record at current file offset
      * **readScan** : read scan associated with current record
      * **readAll**  : read all records
      
    Written by AJ 20130607
    """
    def __init__(self,sTime=None,hemi=None,eTime=None, src=None,fileName=None, \
                  fileType=None,noCache=False,verbose=False,local_dirfmt=None, \
                  local_fnamefmt=None,local_dict=None,remote_dirfmt=None,  \
                  remote_fnamefmt=None,remote_dict=None, remote_site=None, \
                  username=None, password=None, port=None,tmpdir=None):

        from pydarn.sdio import sdDataPtr
        from utils.timeUtils import datetimeToEpoch
        import datetime as dt
        import os,glob,string
        from pydarn.radar import network
        import utils
        from pydarn.sdio.fetchUtils import fetch_local_files, fetch_remote_files
    
        self.sTime = sTime
        self.eTime = eTime
        self.hemi = hemi
        self.fType = fileType
        self.dType = None
        self.recordIndex = None
        self.__filename = fileName 
        self.__nocache  = noCache
        self.__src = src
        self.__fd = None
        self.__ptr =  None

        #check inputs
        assert(isinstance(self.sTime,dt.datetime)), \
          'error, sTime must be datetime object'
        assert(hemi is not None), \
          "error, hemi must not be None"
        assert(self.eTime == None or isinstance(self.eTime,dt.datetime)), \
          'error, eTime must be datetime object or None'
        assert(fileType == 'grd' or fileType == 'grdex' or \
          fileType == 'map' or fileType == 'mapex'), \
          "error, fileType must be one of: 'grd','grdex','map','mapex'"
        assert(fileName == None or isinstance(fileName,str)), \
          'error, fileName must be None or a string'
        assert(src == None or src == 'local' or src == 'sftp'), \
          'error, src must be one of None,local,sftp'
    
        if self.eTime == None: self.eTime = self.sTime+dt.timedelta(days=1)
    
        filelist = []
        if fileType == 'grd': arr = ['grd','grdex']
        elif fileType == 'grdex': arr = ['grdex','grd']
        elif fileType == 'map': arr = ['map','mapex']
        elif fileType == 'mapex': arr = ['mapex','map']
        else: arr = [fileType]
    
        #a temporary directory to store a temporary file
        tmpDir = '/tmp/sd/'
        d = os.path.dirname(tmpDir)
        if not os.path.exists(d):
            os.makedirs(d)
  
        cached = False
  
        #FIRST, check if a specific filename was given
        if fileName != None:
            try:
                if(not os.path.isfile(fileName)):
                    print 'problem reading',fileName,':file does not exist'
                    return None
                outname = tmpDir+str(int(datetimeToEpoch(dt.datetime.now())))
                if(string.find(fileName,'.bz2') != -1):
                    outname = string.replace(fileName,'.bz2','')
                    print 'bunzip2 -c '+fileName+' > '+outname+'\n'
                    os.system('bunzip2 -c '+fileName+' > '+outname)
                elif(string.find(fileName,'.gz') != -1):
                    outname = string.replace(fileName,'.gz','')
                    print 'gunzip -c '+fileName+' > '+outname+'\n'
                    os.system('gunzip -c '+fileName+' > '+outname)
                else:
                    os.system('cp '+fileName+' '+outname)
                    print 'cp '+fileName+' '+outname
                filelist.append(outname)
    
            except Exception, e:
                print e
                print 'problem reading file',fileName
                return None

        #Next, check for a cached file
        if fileName == None and not noCache:
            try:
                if not cached:
                    for f in glob.glob("%s????????.??????.????????.??????.%s.%s" % (tmpDir,hemi,fileType)):
                        try:
                            ff = string.replace(f,tmpDir,'')
                            #check time span of file
                            t1 = dt.datetime(int(ff[0:4]),int(ff[4:6]),int(ff[6:8]),int(ff[9:11]),int(ff[11:13]),int(ff[13:15]))
                            t2 = dt.datetime(int(ff[16:20]),int(ff[20:22]),int(ff[22:24]),int(ff[25:27]),int(ff[27:29]),int(ff[29:31]))
                            #check if file covers our timespan
                            if t1 <= self.sTime and t2 >= self.eTime:
                                cached = True
                                filelist.append(f)
                                print 'Found cached file: %s' % f
                                break
                        except Exception,e:
                            print e
            except Exception,e:
                print e
  
        #Next, LOOK LOCALLY FOR FILES
        if not cached and (src == None or src == 'local') and fileName == None:
            try:
                for ftype in arr:
                    print "\nLooking locally for %s files with hemi: %s" % (ftype,hemi)
                    #If the following aren't already, in the near future
                    #they will be assigned by a configuration dictionary 
                    #much like matplotlib's rcsetup.py (matplotlibrc)
    
                    if local_dirfmt is None:
                        try:
                            local_dirfmt = os.environ['DAVIT_SD_LOCAL_DIRFORMAT']
                        except:
                            local_dirfmt = '/sd-data/{year}/{ftype}/{hemi}/'
                            print 'Environment variable DAVIT_SD_LOCAL_DIRFORMAT not set, using default:',local_dirfmt
    
                    if local_dict is None:
                        local_dict = {'hemi':hemi, 'ftype':ftype}
                    if ('ftype' in local_dict.keys()):
                        local_dict['ftype'] = ftype
                    if local_fnamefmt is None:
                        try:
                            local_fnamefmt = os.environ['DAVIT_SD_LOCAL_FNAMEFMT'].split(',')
                        except:
                            local_fnamefmt = ['{date}.{hemi}.{ftype}']
                            print 'Environment variable DAVIT_SD_LOCAL_FNAMEFMT not set, using default:',local_fnamefmt
                    
                    outdir = tmpDir
    
    
                    #fetch the local files
                    temp = fetch_local_files(self.sTime, self.eTime, local_dirfmt, local_dict, outdir, \
                    local_fnamefmt, verbose=verbose)

                    # check to see if the files actually have data between stime and etime
                    valid = self.__validate_fetched(temp,self.sTime,self.eTime)
                    filelist = [x[0] for x in zip(temp,valid) if x[1]]
                    invalid_files = [x[0] for x in zip(temp,valid) if not x[1]]

                    if len(invalid_files) > 0:
                        for f in invalid_files:
                            print 'removing invalid file: ' + f
                            os.system('rm ' + f)

                    # If we have valid files then continue
                    if(len(filelist) > 0):
                        print 'found',ftype,'data in local files'
                        self.fType,self.dType = ftype,'dmap'
                        fileType = ftype
                        break
    
                    else:
                        print  'could not find',ftype,'data in local files'
    
            except Exception, e:
                print e
                print 'There was a problem reading local data, perhaps you are not at VT?'
                print 'Will attempt fetching data from remote.'
                src=None
              
        #finally, check the VT sftp server if we have not yet found files
        if (src == None or src == 'sftp') and self.__ptr == None and len(filelist) == 0 and fileName == None:
            for ftype in arr:
                print '\nLooking on the remote SFTP server for',ftype,'files'
                try:
                    
                    #If the following aren't already, in the near future
                    #they will be assigned by a configuration dictionary 
                    #much like matplotlib's rcsetup.py (matplotlibrc)
    
                    if remote_site is None:
                        try:
                            remote_site = os.environ['DB']
                        except:
                            remote_site = 'sd-data.ece.vt.edu'
                            print 'Environment variable DB not set, using default:',remote_site
                    if username is None:
                        try:
                            username = os.environ['DBREADUSER']
                        except:
                            username = 'sd_dbread'
                            print 'Environment variable DBREADUSER not set, using default:',username
                    if password is None:
                        try:
                            password = os.environ['DBREADPASS']
                        except:
                            password = '5d'
                            print 'Environment variable DBREADPASS not set, using default:',password
                    if remote_dirfmt is None:
                        try:
                            remote_dirfmt = os.environ['DAVIT_SD_REMOTE_DIRFORMAT']
                        except:
                            remote_dirfmt = 'data/{year}/{ftype}/{hemi}/'
                            print 'Environment variable DAVIT_SD_REMOTE_DIRFORMAT not set, using default:',remote_dirfmt
                    if remote_dict is None:
                        remote_dict = {'ftype':ftype, 'hemi':hemi}
                    if ('ftype' in remote_dict.keys()):
                        remote_dict['ftype'] = ftype
                    if remote_fnamefmt is None:
                        try:
                            remote_fnamefmt = os.environ['DAVIT_SD_REMOTE_FNAMEFMT'].split(',')
                        except:
                            remote_fnamefmt = ['{date}.{hemi}.{ftype}']
                            print 'Environment variable DAVIT_SD_REMOTE_FNAMEFMT not set, using default:',remote_fnamefmt
                    if port is None:
                        try:
                            port = os.environ['DB_PORT']
                        except:
                            port = '22'
                            print 'Environment variable DB_PORT not set, using default:',port

                    outdir = tmpDir

                    #Now fetch the files
                    temp = fetch_remote_files(self.sTime, self.eTime, 'sftp', remote_site, \
                        remote_dirfmt, remote_dict, outdir, remote_fnamefmt, username=username, \
                        password=password, port=port, verbose=verbose)

                    # check to see if the files actually have data between stime and etime
                    valid = self.__validate_fetched(temp,self.sTime,self.eTime)
                    filelist = [x[0] for x in zip(temp,valid) if x[1]]
                    invalid_files = [x[0] for x in zip(temp,valid) if not x[1]]

                    if len(invalid_files) > 0:
                        for f in invalid_files:
                            print 'removing invalid file: ' + f
                            os.system('rm ' + f)

                    # If we have valid files then continue
                    if len(filelist) > 0 :
                        print 'found',ftype,'data on sftp server'
                        self.fType,self.dType = ftype,'dmap'
                        fileType = ftype
                        break
    
                    else:
                        print  'could not find',ftype,'data on sftp server'
    
                except Exception,e:
                    print e
                    print 'problem reading from sftp server'
        #check if we have found files
        if len(filelist) != 0:
            #concatenate the files into a single file
            if not cached:
                print 'Concatenating all the files in to one'
                #choose a temp file name with time span info for cacheing
                tmpName = '%s%s.%s.%s.%s.%s.%s' % (tmpDir, \
                  self.sTime.strftime("%Y%m%d"),self.sTime.strftime("%H%M%S"), \
                  self.eTime.strftime("%Y%m%d"),self.eTime.strftime("%H%M%S"),hemi,fileType)
                print 'cat '+string.join(filelist)+' > '+tmpName
                os.system('cat '+string.join(filelist)+' > '+tmpName)
                for filename in filelist:
                    print 'rm '+filename
                    os.system('rm '+filename)
            else:
                tmpName = filelist[0]
                self.fType = fileType
                self.dType = 'dmap'

            self.__filename=tmpName
            self.open()

        if(self.__ptr != None):
            if(self.dType == None): self.dType = 'dmap'
        else:
            print '\nSorry, we could not find any data for you :('

  
    def __repr__(self):
        myStr = 'sdDataPtr\n'
        for key,var in self.__dict__.iteritems():
            myStr += key+' = '+str(var)+'\n'
        return myStr

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def next(self):
        beam=self.readRec()
        if beam is None:
            raise StopIteration
        else:
            return beam

    def open(self):
        """open the associated dmap filename."""
        import os
        self.__fd = os.open(self.__filename,os.O_RDONLY)
        self.__ptr = os.fdopen(self.__fd)

    def createIndex(self):
        import datetime as dt
        from pydarn.dmapio import getDmapOffset,readDmapRec,setDmapOffset
        recordDict={}
        starting_offset=self.offsetTell()
        #rewind back to start of file
        self.rewind()
        while(1):
            #read the next record from the dmap file
            offset= getDmapOffset(self.__fd)
            dfile = readDmapRec(self.__fd)
            if(dfile is None):
                #if we dont have valid data, clean up, get out
                print '\nreached end of data'
                break
            else:
                try:
                    dtime = dt.datetime(dfile['start.year'],dfile['start.month'],dfile['start.day'], \
                                 dfile['start.hour'],dfile['start.minute'],int(dfile['start.second']))
                    dfile['time'] = (dtime - dt.datetime(1970, 1, 1)).total_seconds()
                except Exception,e:
                    print e
                    print 'problem reading time from file, returning None'
                    break

                if(dt.datetime.utcfromtimestamp(dfile['time']) >= self.sTime and \
                  dt.datetime.utcfromtimestamp(dfile['time']) <= self.eTime) : 
                    rectime = dt.datetime.utcfromtimestamp(dfile['time'])
                    recordDict[rectime]=offset
        #reset back to before building the index 
        self.recordIndex=recordDict
        self.offsetSeek(starting_offset)
        return recordDict
  
    def offsetSeek(self,offset,force=False):
        """jump to dmap record at supplied byte offset.
           Require offset to be in record index list unless forced. 
        """
        from pydarn.dmapio import setDmapOffset,getDmapOffset 
        if force:
          return setDmapOffset(self.__fd,offset)
        else:
          if self.recordIndex is None:        
            self.createIndex()
          if offset in self.recordIndex.values():
            return setDmapOffset(self.__fd,offset)
          else:
            return getDmapOffset(self.__fd)
  
    def offsetTell(self):
        """jump to dmap record at supplied byte offset. 
        """
        from pydarn.dmapio import getDmapOffset
        return getDmapOffset(self.__fd)
  
    def rewind(self):
        """jump to beginning of dmap file."""
        from pydarn.dmapio import setDmapOffset 
        return setDmapOffset(self.__fd,0)
  
    def readRec(self):
       """A function to read a single record of radar data from a :class:`pydarn.sdio.radDataTypes.radDataPtr` object
       **Returns**:
       * **myBeam** (:class:`pydarn.sdio.radDataTypes.beamData`): an object filled with the data we are after.  *will return None when finished reading*
       """
       from pydarn.sdio.sdDataTypes import sdDataPtr, gridData, mapData, alpha
       import pydarn
       import datetime as dt
  
       #check input
       if(self.__ptr == None):
           print 'error, your pointer does not point to any data'
           return None
       if self.__ptr.closed:
           print 'error, your file pointer is closed'
           return None
  
       #do this until we reach the requested start time
       #and have a parameter match
       while(1):
           offset = pydarn.dmapio.getDmapOffset(self.__fd)
           dfile = pydarn.dmapio.readDmapRec(self.__fd)
           #check for valid data
           try:
               dtime = dt.datetime(dfile['start.year'],dfile['start.month'],dfile['start.day'], \
                        dfile['start.hour'],dfile['start.minute'],int(dfile['start.second']))
               dfile['time'] = (dtime - dt.datetime(1970, 1, 1)).total_seconds()
           except Exception,e:
               print e
               print 'problem reading time from file, returning None'
               break

           if dfile == None or dt.datetime.utcfromtimestamp(dfile['time']) > self.eTime:
               #if we dont have valid data, clean up, get out
               print '\nreached end of data'
               #self.close()
               return None
           #check that we're in the time window, and that we have a 
           #match for the desired params
  
           if(dt.datetime.utcfromtimestamp(dfile['time']) >= self.sTime and \
                 dt.datetime.utcfromtimestamp(dfile['time']) <= self.eTime ):
               #fill the beamdata object
               #Check the file type
               if self.fType == 'grd' or self.fType == 'grdex':
                   myData = gridData(dataDict=dfile)
               elif self.fType == 'map' or self.fType == 'mapex':
                   myData = mapData(dataDict=dfile)
               else:
                   print 'error, unrecognized file type'
                   return None
               myData.recordDict=dfile
               myData.fType = self.fType
               myData.fPtr = self
               myData.offset = offset
  
               return myData
  
    def close(self):
        """close associated dmap file."""
        import os

        if self.__ptr is not None:
            self.__ptr.close()
            self.__fd=None

    def __validate_fetched(self,filelist,stime,etime):
        """ This function checks if the files in filelist contain data
        for the start and end times (stime,etime) requested by a user.

        **Args**:
            * **filelist** (list):
            * **stime** (datetime.datetime):
            * **etime** (datetime.datetime):

        **Returns**:
            * List of booleans. True if a file contains data in the time
            range (stime,etime)
        """

        # This method will need some modification for it to work with
        # file formats that are NOT DMAP (i.e. HDF5). Namely, the dmapio
        # specific code will need to be modified (readDmapRec).

        import datetime as dt
        import numpy as np
        from pydarn.dmapio import readDmapRec

        valid = []

        for f in filelist:
            print 'Checking file: ' + f
            stimes = []
            etimes = []

            # Open the file and create a file pointer
            self.__filename = f
            self.open()

            # Iterate through the file and grab the start time for beam
            # integration and calculate the end time from intt.sc and intt.us
            while(1):
                #read the next record from the dmap file
                dfile = readDmapRec(self.__fd)
                if(dfile is None):
                    break
                else:
                    temp = dt.datetime(int(dfile['start.year']),int(dfile['start.month']),
                                       int(dfile['start.day']),int(dfile['start.hour']),
                                       int(dfile['start.minute']),int(dfile['start.second']))
                    stimes.append(temp)
                    temp = dt.datetime(int(dfile['end.year']),int(dfile['end.month']),
                                       int(dfile['end.day']),int(dfile['end.hour']),
                                       int(dfile['end.minute']),int(dfile['end.second']))
                    etimes.append(temp)
            # Close the file and clean up
            self.close()
            self.__ptr = None

            inds = np.where((np.array(stimes) >= stime) & (np.array(stimes) <= etime))
            inde = np.where((np.array(etimes) >= stime) & (np.array(etimes) <= etime))
            if (np.size(inds) > 0) or (np.size(inde) > 0):
                valid.append(True)
            else:
                valid.append(False)

        return valid

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

#TESTING CODE
if __name__=="__main__":
  import os
  import datetime
  import hashlib
  try:
      tmpDir=os.environ['DAVIT_TMPDIR']
  except:
      tmpDir = '/tmp/sd/'

  hemi='north'
  channel=None
  fileType='mapex'
  sTime=datetime.datetime(2012,7,10)
  eTime=datetime.datetime(2012,7,11,2)
  expected_filename="20120710.000000.20120711.020000.north.mapex"
  expected_path=os.path.join(tmpDir,expected_filename)
  expected_filesize=32975826
  expected_md5sum="1b0e78cb339e875cc17f82e240ef360f"
  print "Expected File:",expected_path

  print "\nRunning sftp grab example for sdDataPtr."
  print "Environment variables used:"
  print "  DB:", os.environ['DB']
  print "  DB_PORT:",os.environ['DB_PORT']
  print "  DBREADUSER:", os.environ['DBREADUSER']
  print "  DBREADPASS:", os.environ['DBREADPASS']
  print "  DAVIT_SD_REMOTE_DIRFORMAT:", os.environ['DAVIT_SD_REMOTE_DIRFORMAT']
  print "  DAVIT_SD_REMOTE_FNAMEFMT:", os.environ['DAVIT_SD_REMOTE_FNAMEFMT']
  print "  DAVIT_TMPDIR:", os.environ['DAVIT_TMPDIR']
  src='sftp'
  if os.path.isfile(expected_path):
    os.remove(expected_path)
  VTptr = sdDataPtr(sTime,hemi,eTime=eTime,fileType='mapex',src=src,noCache=True)
  if os.path.isfile(expected_path):
    statinfo = os.stat(expected_path)
    print "Actual File Size:  ", statinfo.st_size
    print "Expected File Size:", expected_filesize 
    md5sum=hashlib.md5(open(expected_path).read()).hexdigest()
    print "Actual Md5sum:  ",md5sum
    print "Expected Md5sum:",expected_md5sum
    if expected_md5sum!=md5sum:
      print "Error: Cached dmap file has unexpected md5sum."
  else:
    print "Error: Failed to create expected cache file"
  print "Let's read two records from the remote sftp server:"
  try:
    ptr=VTptr
    myData  = ptr.readRec()
    print myData.recordDict['time']
    myData  = ptr.readRec()
    print myData.recordDict['time']
    print "Close pointer"
    ptr.close()
    print "reopen pointer"
    ptr.open()
    print "Should now be back at beginning:"
    myData  = ptr.readRec()
    print myData.recordDict['time']
    print "What is the current offset:"
    print ptr.offsetTell()
    print "Try to seek to offset 4, shouldn't work:"
    print ptr.offsetSeek(4)
    print "What is the current offset:"
    print ptr.offsetTell()

  except:
    print "record read failed for some reason"

  ptr.close()
  del VTptr

  print "\nRunning local grab example for sdDataPtr."
  print "Environment variables used:"
  print "  DAVIT_SD_LOCAL_DIRFORMAT:", os.environ['DAVIT_SD_LOCAL_DIRFORMAT']
  print "  DAVIT_SD_LOCAL_FNAMEFMT:", os.environ['DAVIT_SD_LOCAL_FNAMEFMT']
  print "  DAVIT_TMPDIR:", os.environ['DAVIT_TMPDIR']

  src='local'
  if os.path.isfile(expected_path):
    os.remove(expected_path)
  localptr = sdDataPtr(sTime,hemi,eTime=eTime,src=src,fileType='mapex',noCache=True)
  if os.path.isfile(expected_path):
    statinfo = os.stat(expected_path)
    print "Actual File Size:  ", statinfo.st_size
    print "Expected File Size:", expected_filesize 
    md5sum=hashlib.md5(open(expected_path).read()).hexdigest()
    print "Actual Md5sum:  ",md5sum
    print "Expected Md5sum:",expected_md5sum
    if expected_md5sum!=md5sum:
      print "Error: Cached dmap file has unexpected md5sum."
  else:
    print "Error: Failed to create expected cache file"
  print "Let's read two records:"
  try:
    ptr=localptr
    myData  = ptr.readRec()
    print myData.recordDict['time']
    myData  = ptr.readRec()
    print myData.recordDict['time']
    print "Close pointer"
    ptr.close()
    print "reopen pointer"
    ptr.open()
    print "Should now be back at beginning:"
    myData  = ptr.readRec()
    print myData.recordDict['time']
  except:
    print "record read failed for some reason"
  ptr.close()
  
  del localptr

