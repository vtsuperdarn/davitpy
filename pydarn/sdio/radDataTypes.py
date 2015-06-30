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
.. module:: radDataTypes
   :synopsis: the classes needed for reading, writing, and storing fundamental radar data (iq,raw,fit)
.. moduleauthor:: AJ, 20130108
*********************
**Module**: pydarn.sdio.radDataTypes
*********************
**Classes**:
  * :class:`pydarn.sdio.radDataTypes.radDataPtr`
  * :class:`pydarn.sdio.radDataTypes.radBaseData`
  * :class:`pydarn.sdio.radDataTypes.scanData`
  * :class:`pydarn.sdio.radDataTypes.beamData`
  * :class:`pydarn.sdio.radDataTypes.prmData`
  * :class:`pydarn.sdio.radDataTypes.fitData`
  * :class:`pydarn.sdio.radDataTypes.rawData`
  * :class:`pydarn.sdio.radDataTypes.iqData`
"""


from utils import twoWayDict
alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m', \
          'n','o','p','q','r','s','t','u','v','w','x','y','z']


class radDataPtr():
  """A class which contains a pipeline to a data source
  
  **Public Attrs**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): start time of the request
    * **eTime** (`datetime <http://tinyurl.com/bl352yx>`_): end time of the request
    * **stid** (int): station id of the request
    * **channel** (str): the 1-letter code to specify the UAF channel (not stereo), 
                         e.g. 'a','b',... If 'all', ALL channels were obtained. 
                         default = None meaning don't check for UAF named data files
    * **bmnum** (int): beam number of the request
    * **cp** (int): control prog id of the request
    * **fType** (str): the file type, 'fitacf', 'rawacf', 'iqdat', 'fitex', 'lmfit'
    * **fBeam** (:class:`pydarn.sdio.radDataTypes.beamData`): the first beam of the next scan, useful for when reading into scan objects
    * **recordIndex** (dict): look up dictionary for file offsets for all records 
    * **scanStartIndex** (dict): look up dictionary for file offsets for scan start records
  **Private Attrs**:
    * **ptr** (file or mongodb query object): the data pointer (different depending on mongodo or dmap)
    * **fd** (int): the file descriptor 
    * **filtered** (bool): use Filtered datafile 
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
    
  Written by AJ 20130108
  """
  def __init__(self,sTime=None,radcode=None,eTime=None,stid=None,channel=None,bmnum=None,cp=None, \
                fileType=None,filtered=False, src=None,fileName=None,noCache=False,verbose=False, \
                local_dirfmt=None, local_fnamefmt=None, local_dict=None, remote_dirfmt=None,      \
                remote_fnamefmt=None, remote_dict=None,remote_site=None, username=None, port=None,\
                password=None,tmpdir=None):

    import datetime as dt
    import os,glob,string
    from pydarn.radar import network
    import utils
    from pydarn.sdio.fetchUtils import fetch_local_files, fetch_remote_files
    
    self.sTime = sTime
    self.eTime = eTime
    self.stid = stid
    self.channel = channel
    self.bmnum = bmnum
    self.cp = cp
    self.fType = fileType
    self.dType = None
    self.fBeam = None
    self.recordIndex = None
    self.scanStartIndex = None
    self.__filename = fileName 
    self.__filtered = filtered
    self.__nocache  = noCache
    self.__src = src
    self.__fd = None
    self.__ptr =  None

    #check inputs
    assert(isinstance(self.sTime,dt.datetime)), \
      'error, sTime must be datetime object'
    assert(self.eTime == None or isinstance(self.eTime,dt.datetime)), \
      'error, eTime must be datetime object or None'
    assert(self.channel == None or (isinstance(self.channel,str) and len(self.channel) == 1) \
           or (self.channel == 'all')), \
      'error, channel must be None or a 1-letter string'
    assert(bmnum == None or isinstance(bmnum,int)), \
      'error, bmnum must be an int or None'
    assert(cp == None or isinstance(cp,int)), \
      'error, cp must be an int or None'
    assert(fileType == 'rawacf' or fileType == 'fitacf' or \
      fileType == 'fitex' or fileType == 'lmfit' or fileType == 'iqdat'), \
      'error, fileType must be one of: rawacf,fitacf,fitex,lmfit,iqdat'
    assert(fileName == None or isinstance(fileName,str)), \
      'error, fileName must be None or a string'
    assert(isinstance(filtered,bool)), \
      'error, filtered must be True of False'
    assert(src == None or src == 'local' or src == 'sftp'), \
      'error, src must be one of None,local,sftp'

    # If channel is all, then make the channel a wildcard, then it will pull in all UAF channels
    if (self.channel=='all'):
      channel = '.'

    if(self.eTime == None):
      self.eTime = self.sTime+dt.timedelta(days=1)

    filelist = []
    if(fileType == 'fitex'): arr = ['fitex','fitacf','lmfit']
    elif(fileType == 'fitacf'): arr = ['fitacf','fitex','lmfit']
    elif(fileType == 'lmfit'): arr = ['lmfit','fitex','fitacf']
    else: arr = [fileType]

    #a temporary directory to store a temporary file
    if tmpdir is None:
      try:
        tmpDir=os.environ['DAVIT_TMPDIR']
      except:
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
            outname = tmpDir+str(int(utils.datetimeToEpoch(dt.datetime.now())))
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
            self.dType = 'dmap'

        except Exception, e:
            print e
            print 'problem reading file',fileName
            return None
    #Next, check for a cached file
    if fileName == None and not noCache:
        try:
            if (self.channel is None):
                for f in glob.glob("%s????????.??????.????????.??????.%s.%s" % (tmpDir,radcode,fileType)):
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
            else:
                for f in glob.glob("%s????????.??????.????????.??????.%s.%s.%s" % (tmpDir,radcode,self.channel,fileType)):
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
                print "\nLooking locally for %s files with radcode: %s channel: %s" % (ftype,radcode,self.channel)
                #If the following aren't already, in the near future
                #they will be assigned by a configuration dictionary 
                #much like matplotlib's rcsetup.py (matplotlibrc)

                if local_dirfmt is None:
                    try:
                        local_dirfmt = os.environ['DAVIT_LOCAL_DIRFORMAT']
                    except:
                        local_dirfmt = '/sd-data/{year}/{ftype}/{radar}/'
                        print 'Environment variable DAVIT_LOCAL_DIRFORMAT not set, using default:',local_dirfmt

                if local_dict is None:
                    local_dict = {'radar':radcode, 'ftype':ftype, 'channel':channel}
                if ('ftype' in local_dict.keys()):
                    local_dict['ftype'] = ftype

                if local_fnamefmt is None:
                    try:
                        local_fnamefmt = os.environ['DAVIT_LOCAL_FNAMEFMT'].split(',')
                    except:
                        local_fnamefmt = ['{date}.{hour}......{radar}.{ftype}', \
                '{date}.{hour}......{radar}.{channel}.{ftype}']
                        print 'Environment variable DAVIT_LOCAL_FNAMEFMT not set, using default:',local_fnamefmt
                
                outdir = tmpDir

                #check to see if channel was specified and only use fnamefmts with channel in them
                for f,fname in enumerate(local_fnamefmt):
                    if ((channel is not None) and ('channel' not in fname)):
                        local_fnamefmt.pop(f)
                if len(local_fnamefmt) == 0:
                    print "Error, no file name formats containing channel exists!"
                    break

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
                        remote_dirfmt = os.environ['DAVIT_REMOTE_DIRFORMAT']
                    except:
                        remote_dirfmt = 'data/{year}/{ftype}/{radar}/'
                        print 'Environment variable DAVIT_REMOTE_DIRFORMAT not set, using default:',remote_dirfmt
                if remote_dict is None:
                    remote_dict = {'ftype':ftype, 'channel':channel, 'radar':radcode}
                if ('ftype' in remote_dict.keys()):
                    remote_dict['ftype'] = ftype
                if remote_fnamefmt is None:
                    try:
                        remote_fnamefmt = os.environ['DAVIT_REMOTE_FNAMEFMT'].split(',')
                    except:
                        remote_fnamefmt = ['{date}.{hour}......{radar}.{ftype}', \
                                          '{date}.{hour}......{radar}.{channel}.{ftype}']
                        print 'Environment variable DAVIT_REMOTE_FNAMEFMT not set, using default:',remote_fnamefmt
                if port is None:
                    try:
                        port = os.environ['DB_PORT']
                    except:
                        port = '22'
                        print 'Environment variable DB_PORT not set, using default:',port

                outdir = tmpDir

                #check to see if channel was specified and only use fnamefmts with channel in them
                for f,fname in enumerate(remote_fnamefmt):
                    if ((channel is not None) and ('channel' not in fname)):
                        remote_fnamefmt.pop(f)
                if len(remote_fnamefmt) == 0:
                    print "Error, no file name formats containing channel exists!"
                    break

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
            if (self.channel is None):
                tmpName = '%s%s.%s.%s.%s.%s.%s' % (tmpDir, \
                  self.sTime.strftime("%Y%m%d"),self.sTime.strftime("%H%M%S"), \
                  self.eTime.strftime("%Y%m%d"),self.eTime.strftime("%H%M%S"),radcode,fileType)
            else:
                tmpName = '%s%s.%s.%s.%s.%s.%s.%s' % (tmpDir, \
                  self.sTime.strftime("%Y%m%d"),self.sTime.strftime("%H%M%S"), \
                  self.eTime.strftime("%Y%m%d"),self.eTime.strftime("%H%M%S"),radcode,self.channel,fileType)
            print 'cat '+string.join(filelist)+' > '+tmpName
            os.system('cat '+string.join(filelist)+' > '+tmpName)
            for filename in filelist:
                print 'rm '+filename
                os.system('rm '+filename)
        else:
            tmpName = filelist[0]
            self.fType = fileType
            self.dType = 'dmap'

        #filter(if desired) and open the file
        if(not filtered):
            self.__filename=tmpName
            self.open()
        else:
            if not fileType+'f' in tmpName:
                try:
                    fTmpName = tmpName+'f'
                    print 'fitexfilter '+tmpName+' > '+fTmpName
                    os.system('fitexfilter '+tmpName+' > '+fTmpName)
                except Exception,e:
                    print 'problem filtering file, using unfiltered'
                    fTmpName = tmpName
            else:
                fTmpName = tmpName
            try:
                self.__filename=fTmpName
                self.open()
            except Exception,e:
                print 'problem opening file'
                print e
    if(self.__ptr != None):
        if(self.dType == None): self.dType = 'dmap'
    else:
        print '\nSorry, we could not find any data for you :('




  def __repr__(self):
    myStr = 'radDataPtr: \n'
    for key,var in self.__dict__.iteritems():
      if isinstance(var,radBaseData) or isinstance(var,radDataPtr) or  isinstance(var,type({})):
        myStr += '%s = %s \n' % (key,'object')
      else:
        myStr += '%s = %s \n' % (key,var)
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
      scanStartDict={}
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
              if(dt.datetime.utcfromtimestamp(dfile['time']) >= self.sTime and \
                dt.datetime.utcfromtimestamp(dfile['time']) <= self.eTime) : 
                  rectime = dt.datetime.utcfromtimestamp(dfile['time'])
                  recordDict[rectime]=offset
                  if dfile['scan']==1: scanStartDict[rectime]=offset
      #reset back to before building the index 
      self.recordIndex=recordDict
      self.offsetSeek(starting_offset)
      self.scanStartIndex=scanStartDict
      return recordDict,scanStartDict

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

  def readScan(self):
        """A function to read a full scan of data from a :class:`pydarn.sdio.radDataTypes.radDataPtr` object

        .. note
        This will ignore any bmnum request.  Also, if no channel was specified in radDataOpen, it will only read channel 'a'

        **Returns**:
        * **myScan** (:class:`pydarn.sdio.radDataTypes.scanData`): an object filled with the data we are after.  *will return None when finished reading*

        """
        from pydarn.sdio import scanData
        import pydarn
        #Save the radDataPtr's bmnum setting temporarily and set it to None
        orig_beam=self.bmnum
        self.bmnum=None

        if self.__ptr.closed:
            print 'error, your file pointer is closed'
            return None

        myScan = scanData()
        while(1):
            myBeam=self.readRec()
            if myBeam is None: 
                break

            if ((myBeam.prm.scan == 1 and len(myScan) == 0)         # Append a beam if it is the first in a scan AND nothing has been added to the myScan object. 
             or (myBeam.prm.scan == 0 and  len(myScan) > 0) ):      # Append a beam if it is not the first in a scan AND the myScan object has items.
                myScan.append(myBeam)
                offset = pydarn.dmapio.getDmapOffset(self.__fd)
            elif myBeam.prm.scan == 1 and len(myScan) > 0:          # Break out of the loop if we are on to the next scan and rewind the pointer to the previous beam.
                s = pydarn.dmapio.setDmapOffset(self.__fd,offset)
                break 

        if len(myScan) == 0: myScan = None
        self.bmnum=orig_beam
        return myScan

  def readRec(self):
     """A function to read a single record of radar data from a :class:`pydarn.sdio.radDataTypes.radDataPtr` object
     **Returns**:
     * **myBeam** (:class:`pydarn.sdio.radDataTypes.beamData`): an object filled with the data we are after.  *will return None when finished reading*
     """
     from pydarn.sdio.radDataTypes import radDataPtr, beamData, \
     fitData, prmData, rawData, iqData, alpha
     import pydarn, datetime as dt

     #check input
     if(self.__ptr == None):
         print 'error, your pointer does not point to any data'
         return None
     if self.__ptr.closed:
         print 'error, your file pointer is closed'
         return None
     myBeam = beamData()
     #do this until we reach the requested start time
     #and have a parameter match
     while(1):
         offset=pydarn.dmapio.getDmapOffset(self.__fd)
         dfile = pydarn.dmapio.readDmapRec(self.__fd)
         #check for valid data
         if dfile == None or dt.datetime.utcfromtimestamp(dfile['time']) > self.eTime:
             #if we dont have valid data, clean up, get out
             print '\nreached end of data'
             #self.close()
             return None
         #check that we're in the time window, and that we have a 
         #match for the desired params
         #if dfile['channel'] < 2: channel = 'a'  THIS CHECK IS BAD. 'channel' in a dmap file specifies STEREO operation or not.
         #else: channel = alpha[dfile['channel']-1]
         if(dt.datetime.utcfromtimestamp(dfile['time']) >= self.sTime and \
               dt.datetime.utcfromtimestamp(dfile['time']) <= self.eTime and \
               (self.stid == None or self.stid == dfile['stid']) and
               #(self.channel == None or self.channel == channel) and ASR removed because of bad check as above.
               (self.bmnum == None or self.bmnum == dfile['bmnum']) and
               (self.cp == None or self.cp == dfile['cp'])):
             #fill the beamdata object
             myBeam.updateValsFromDict(dfile)
             myBeam.recordDict=dfile
             myBeam.fType = self.fType
             myBeam.fPtr = self
             myBeam.offset = offset
             #file prm object
             myBeam.prm.updateValsFromDict(dfile)
             if myBeam.fType == "rawacf":
                 myBeam.rawacf.updateValsFromDict(dfile)
             if myBeam.fType == "iqdat":
                 myBeam.iqdat.updateValsFromDict(dfile)
             if(myBeam.fType == 'fitacf' or myBeam.fType == 'fitex' or myBeam.fType == 'lmfit'):
                 myBeam.fit.updateValsFromDict(dfile)
             if myBeam.fit.slist == None:
                 myBeam.fit.slist = []
             return myBeam

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

      import os
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
                  temp = dt.datetime.utcfromtimestamp(dfile['time'])
                  stimes.append(temp)
                  sec = dfile['intt.sc'] + dfile['intt.us'] / (10. ** 6)
                  etimes.append(temp + dt.timedelta(seconds=sec))
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

class radBaseData():
  """a base class for the radar data types.  This allows for single definition of common routines
  
  **ATTRS**:
    * Nothing.
  **METHODS**:
    * :func:`updateValsFromDict`: converts a dict from a dmap file to radBaseData
    
  Written by AJ 20130108
  """
  
  def copyData(self,obj):
    """This method is used to recursively copy all of the contents from ont object to self
    
    .. note::
      In general, users will not need to use this.
      
    **Args**: 
      * **obj** (:class:`pydarn.sdio.radDataTypes.radBaseData`): the object to be copied
    **Returns**:
      * Nothing.
    **Example**:
      ::
      
        myradBaseData.copyData(radBaseDataObj)
      
    written by AJ, 20130402
    """
    for key, val in obj.__dict__.iteritems():
      if isinstance(val, radBaseData):
        try: getattr(self, key).copyData(val)
        except: pass
      else:
        setattr(self,key,val)

  def updateValsFromDict(self, aDict):
    """A function to to fill a radar params structure with the data in a dictionary that is returned from the reading of a dmap file
    
    .. note::
      In general, users will not need to us this.
      
    **Args**:
      * **aDict (dict):** the dictionary containing the radar data
    **Returns**
      * nothing.
      
    Written by AJ 20121130
    """
    
    import datetime as dt
    
    #iterate through prmData's attributes
    for attr, value in self.__dict__.iteritems():
      #check for special params
      if(attr == 'time'):
        #convert from epoch to datetime
        if(aDict.has_key(attr) and isinstance(aDict[attr], float)): 
          setattr(self,attr,dt.datetime.utcfromtimestamp(aDict[attr]))
        continue
      elif(attr == 'channel'):
        if(aDict.has_key('channel')):
          self.channel = aDict['channel']
        continue

  # REMOVED BY ASR on 11 SEP 2014
  # the channel attribute in fitted files (fitacf, lmfit, fitex) specifies
  # if the data came from a STEREO radar, so we shouldn't clobber the value
  # from the dmap file.
  #    elif(attr == 'channel'):
  #      if(aDict.has_key('channel')): 
  #        if(isinstance(aDict.has_key('channel'), int)):
  #          if(aDict['channel'] < 2): self.channel = 'a'
  #          else: self.channel = alpha[aDict['channel']-1]
  #        else: self.channel = aDict['channel']
  #      else: self.channel = 'a'
  #      continue

      elif(attr == 'inttus'):
        if(aDict.has_key('intt.us')): 
          self.inttus = aDict['intt.us']
        continue
      elif(attr == 'inttsc'):
        if(aDict.has_key('intt.sc')): 
          self.inttsc = aDict['intt.sc']
        continue
      elif(attr == 'noisesky'):
        if(aDict.has_key('noise.sky')): 
          self.noisesky = aDict['noise.sky']
        continue
      elif(attr == 'noisesearch'):
        if(aDict.has_key('noise.search')): 
          self.noisesearch = aDict['noise.search']
        continue
      elif(attr == 'noisemean'):
        if(aDict.has_key('noise.mean')): 
          self.noisemean = aDict['noise.mean']
        continue
      elif(attr == 'acfd' or attr == 'xcfd'):
        if(aDict.has_key(attr)): 
          setattr(self,attr,[])
          for i in range(self.parent.prm.nrang):
            rec = []
            for j in range(self.parent.prm.mplgs):
              samp = []
              for k in range(2):
                samp.append(aDict[attr][(i*self.parent.prm.mplgs+j)*2+k])
              rec.append(samp)
            getattr(self, attr).append(rec)
        else: setattr(self,attr,[])
        continue
      elif(attr == 'mainData'):
        if(aDict.has_key('data')): 
          if(len(aDict['data']) == aDict['smpnum']*aDict['seqnum']*2*2): fac = 2
          else: fac = 1
          setattr(self,attr,[])
          for i in range(aDict['seqnum']):
            rec = []
            for j in range(aDict['smpnum']):
              samp = []
              for k in range(2):
                samp.append(aDict['data'][(i*fac*aDict['smpnum']+j)*2+k])
              rec.append(samp)
            getattr(self, attr).append(rec)
        else: setattr(self,attr,[])
        continue
      elif(attr == 'intData'):
        if(aDict.has_key('data')): 
          if(len(aDict['data']) == aDict['smpnum']*aDict['seqnum']*2*2): fac = 2
          else: continue
          setattr(self,attr,[])
          for i in range(aDict['seqnum']):
            rec = []
            for j in range(aDict['smpnum']):
              samp = []
              for k in range(2):
                samp.append(aDict['data'][((i*fac+1)*aDict['smpnum']+j)*2+k])
              rec.append(samp)
            getattr(self, attr).append(rec)
        else: setattr(self,attr,[])
        continue
      try:
        setattr(self,attr,aDict[attr])
      except:
        #put in a default value if not another object
        if(not isinstance(getattr(self,attr),radBaseData)):
          setattr(self,attr,None)
          
  #def __repr__(self):
    #myStr = ''
    #for key,var in self.__dict__.iteritems():
      #if(isinstance(var,radBaseData) and key != 'parent'):
        #print key
        #myStr += key+'\n'
        #myStr += str(var)
      #else:
        #myStr += key+' = '+str(var)+'\n'
    #return myStr
    
class scanData(list):
  """a class to contain a radar scan.  Extends list.  Just a list of :class:`pydarn.sdio.radDataTypes.beamData` objects
  
  **Attrs**:
    Nothing.
  **Example**: 
    ::
    
      myBeam = pydarn.sdio.scanData()
    
  Written by AJ 20121130
  """

  def __init__(self):
    pass
  
class beamData(radBaseData):
  """a class to contain the data from a radar beam sounding, extends class :class:`pydarn.sdio.radDataTypes.radBaseData`
  
  **Attrs**:
    * **cp** (int): radar control program id number
    * **stid** (int): radar station id number
    * **time** (`datetime <http://tinyurl.com/bl352yx>`_): timestamp of beam sounding
    * **channel** (str): radar operating channel, eg 'a', 'b', ...
    * **bmnum** (int): beam number
    * **prm** (:class:`pydarn.sdio.radDataTypes.prmData`): operating params
    * **fit** (:class:`pydarn.sdio.radDataTypes.fitData`): fitted params
    * **rawacf** (:class:`pydarn.sdio.radDataTypes.rawData`): rawacf data
    * **iqdat** (:class:`pydarn.sdio.radDataTypes.iqData`): iqdat data
    * **fType** (str): the file type, 'fitacf', 'rawacf', 'iqdat', 'fitex', 'lmfit'

  **Example**: 
    ::
    
      myBeam = pydarn.sdio.radBeam()
    
  Written by AJ 20121130
  """
  def __init__(self, beamDict=None, myBeam=None, proctype=None):
    #initialize the attr values
    self.cp = None
    self.stid = None
    self.time = None
    self.bmnum = None
    self.channel = None
    self.exflg = None
    self.lmflg = None
    self.acflg = None
    self.rawflg = None
    self.iqflg = None
    self.fitex = None
    self.fitacf = None
    self.lmfit= None
    self.fit = fitData()
    self.rawacf = rawData(parent=self)
    self.prm = prmData()
    self.iqdat = iqData()
    self.recordDict = None 
    self.fType = None
    self.offset = None
    self.fPtr = None 
    #if we are intializing from an object, do that
    if(beamDict != None): self.updateValsFromDict(beamDict)
    
  def __repr__(self):
    import datetime as dt
    myStr = 'Beam record FROM: '+str(self.time)+'\n'
    for key,var in self.__dict__.iteritems():
      if isinstance(var,radBaseData) or isinstance(var,radDataPtr) or isinstance(var,type({})):
        myStr += '%s  = %s \n' % (key,'object')
      else:
        myStr += '%s  = %s \n' % (key,var)
    return myStr
    
class prmData(radBaseData):
  """A class to represent radar operating parameters, extends :class:`pydarn.sdio.radDataTypes.radBaseData`

  **Attrs**:
    * **nave**  (int): number of averages
    * **lagfr**  (int): lag to first range in us
    * **smsep**  (int): sample separation in us
    * **bmazm**  (float): beam azimuth
    * **scan**  (int): new scan flag
    * **rxrise**  (int): receiver rise time
    * **inttsc**  (int): integeration time (sec)
    * **inttus**  (int): integration time (us)
    * **mpinc**  (int): multi pulse increment (tau, basic lag time) in us
    * **mppul**  (int): number of pulses
    * **mplgs**  (int): number of lags
    * **mplgexs**  (int): number of lags (tauscan)
    * **nrang**  (int): number of range gates
    * **frang**  (int): first range gate (km)
    * **rsep**  (int): range gate separation in km
    * **xcf**  (int): xcf flag
    * **tfreq**  (int): transmit freq in kHz
    * **txpl**  (int): transmit pulse length in us 
    * **ifmode**  (int): if mode flag
    * **ptab**  (mppul length list): pulse table
    * **ltab**  (mplgs x 2 length list): lag table
    * **noisemean**  (float): mean noise level
    * **noisesky**  (float): sky noise level
    * **noisesearch**  (float): freq search noise level

  Written by AJ 20121130
  """

  #initialize the struct
  def __init__(self, prmDict=None, myPrm=None):
    #set default values
    self.nave = None        #number of averages
    self.lagfr = None       #lag to first range in us
    self.smsep = None       #sample separation in us
    self.bmazm = None       #beam azimuth
    self.scan = None        #new scan flag
    self.rxrise = None      #receiver rise time
    self.inttsc = None      #integeration time (sec)
    self.inttus = None      #integration time (us)
    self.mpinc = None       #multi pulse increment (tau, basic lag time) in us
    self.mppul = None       #number of pulses
    self.mplgs = None       #number of lags
    self.mplgexs = None     #number of lags (tauscan)
    self.nrang = None       #number of range gates
    self.frang = None       #first range gate (km)
    self.rsep = None        #range gate separation in km
    self.xcf = None         #xcf flag
    self.tfreq = None       #transmit freq in kHz
    self.txpl = None       #transmit freq in kHz
    self.ifmode = None      #if mode flag
    self.ptab = None        #pulse table
    self.ltab = None        #lag table
    self.noisemean = None   #mean noise level
    self.noisesky = None    #sky noise level
    self.noisesearch = None #freq search noise level
    
    #if we are copying a structure, do that
    if(prmDict != None): self.updateValsFromDict(prmDict)

  def __repr__(self):
    import datetime as dt
    myStr = 'Prm data: \n'
    for key,var in self.__dict__.iteritems():
      myStr += '%s  = %s \n' % (key,var)
    return myStr

class fitData(radBaseData):
  """a class to contain the fitted params of a radar beam sounding, extends :class:`pydarn.sdio.radDataTypes.radBaseData`
  
  **Attrs**:
    * **pwr0**  (prm.nrang length list): lag 0 power
    * **slist**  (npnts length list): list of range gates with backscatter
    * **npnts** (int): number of range gates with scatter
    * **nlag**  (npnts length list): number of good lags
    * **qflg**  (npnts length list): quality flag
    * **gflg**  (npnts length list): ground scatter flag
    * **p_l**  (npnts length list): lambda power
    * **p_l_e**  (npnts length list): lambda power error
    * **p_s**  (npnts length list): sigma power
    * **p_s_e**  (npnts length list): sigma power error
    * **v**  (npnts length list): velocity
    * **v_e**  (npnts length list): velocity error
    * **w_l**  (npnts length list): lambda spectral width
    * **w_l_e**  (npnts length list): lambda width error
    * **w_s**  (npnts length list): sigma spectral width
    * **w_s_e**  (npnts length list): sigma width error
    * **phi0**  (npnts length list): phi 0
    * **phi0_e**  (npnts length list): phi 0 error
    * **elv**  (npnts length list): elevation angle
  
  **Example**: 
    ::
    
      myFit = pydarn.sdio.fitData()
    
  Written by AJ 20121130
  """

  #initialize the struct
  def __init__(self, fitDict=None, myFit=None):
    self.pwr0 = None      #lag 0 power
    self.slist = None     # list of range gates with backscatter
    self.npnts = None     #number of range gates with scatter
    self.nlag = None      #number of good lags
    self.qflg = None      #quality flag
    self.gflg = None      #ground scatter flag
    self.p_l = None       #lambda power
    self.p_l_e = None     #lambda power error
    self.p_s = None       #sigma power
    self.p_s_e = None     #sigma power error
    self.v = None         #velocity
    self.v_e = None       #velocity error
    self.w_l = None       #lambda spectral width
    self.w_l_e = None     #lambda width error
    self.w_s = None       #sigma spectral width
    self.w_s_e = None     #sigma width error
    self.phi0 = None      #phi 0
    self.phi0_e = None    #phi 0 error
    self.elv = None       #elevation angle
    
    if(fitDict != None): self.updateValsFromDict(fitDict)

  def __repr__(self):
    import datetime as dt
    myStr = 'Fit data: \n'
    for key,var in self.__dict__.iteritems():
      myStr += '%s = %s \n' % (key,var)
    return myStr

class rawData(radBaseData):
  """a class to contain the rawacf data from a radar beam sounding, extends :class:`pydarn.sdio.radDataTypes.radBaseData`
  
  **Attrs**:
    * **pwr0** (nrang length list): acf lag0 pwr 
    * **acfd** (nrang x mplgs x 2 length list): acf data
    * **xcfd** (nrang x mplgs x 2 length list): xcf data
  
  **Example**: 
    ::
    
      myRaw = pydarn.sdio.rawData()
    
  Written by AJ 20130125
  """

  #initialize the struct
  def __init__(self, rawDict=None, parent=None):
    self.pwr0 = []      #acf data
    self.acfd = []      #acf data
    self.xcfd = []      #xcf data
    self.parent = parent #reference to parent beam
    
    if(rawDict != None): self.updateValsFromDict(rawDict)

  def __repr__(self):
    import datetime as dt
    myStr = 'Raw data: \n'
    for key,var in self.__dict__.iteritems():
      myStr += '%s = %s \n' % (key,var)
    return myStr

class iqData(radBaseData):
  """ a class to contain the iq data from a radar beam sounding, extends :class:`pydarn.sdio.radDataTypes.radBaseData`
  
  .. warning::
    I'm not sure what all of the attributes mean.  if somebody knows what these are, please help!

  **Attrs**:
    * **chnnum** (int): number of channels sampled
    * **smpnum** (int): number of samples per pulse sequence
    * **skpnum** (int): number of voltage samples to skip when making acfs
    * **seqnum** (int): number of pulse sequences
    * **tsc** (seqnum length list): seconds component of time past epoch of each pulse sequence
    * **tus** (seqnum length list): micro seconds component of time past epoch of each pulse sequence
    * **tatten** (seqnum length list): attenuator setting for each pulse sequence
    * **tnoise** (seqnum length list): noise value for each pulse sequence
    * **toff** (seqnum length list): offset into the sample buffer for each pulse sequence
    * **tsze** (seqnum length list): number of words stored per pulse sequence
    * **mainData** (seqnum x smpnum x 2 length list): the main array iq complex samples
    * **intData** (seqnum x smpnum x 2 length list): the interferometer iq complex samples
    * **badtr** (? length list): bad tr samples?
    * **tval** (? length list): ?
    * **tbadtr** (? length list): time of bad tr samples?
  
  **Example**: 
    ::
    
      myIq = pydarn.sdio.iqData()
    
  Written by AJ 20130116
  """

  #initialize the struct
  def __init__(self, iqDict=None, parent=None):
    self.seqnum = None
    self.chnnum = None
    self.smpnum = None
    self.skpnum = None
    self.btnum = None
    self.tsc = None
    self.tus = None
    self.tatten = None
    self.tnoise = None
    self.toff = None
    self.tsze = None
    self.tbadtr = None
    self.badtr = None
    self.mainData = []
    self.intData = []
    
    if(iqDict != None): self.updateValsFromDict(iqDict)

  def __repr__(self):
    import datetime as dt
    myStr = 'IQ data: \n'
    for key,var in self.__dict__.iteritems():
      myStr += '%s = %s \n' % (key,var)
    return myStr

if __name__=="__main__":
  import os
  import datetime
  import hashlib
  try:
      tmpDir=os.environ['DAVIT_TMPDIR']
  except:
      tmpDir = '/tmp/sd/'

  rad='fhe'
  channel=None
  fileType='fitacf'
  filtered=False
  sTime=datetime.datetime(2012,11,1,0,0)
  eTime=datetime.datetime(2012,11,1,4,2)
  expected_filename="20121101.000000.20121101.040200.fhe.fitacf"
  expected_path=os.path.join(tmpDir,expected_filename)
  expected_filesize=19377805
  expected_md5sum="cfd48945be0fd5bf82119da9a4a66994"
  print "Expected File:",expected_path

  print "\nRunning sftp grab example for radDataPtr."
  print "Environment variables used:"
  print "  DB:", os.environ['DB']
  print "  DB_PORT:",os.environ['DB_PORT']
  print "  DBREADUSER:", os.environ['DBREADUSER']
  print "  DBREADPASS:", os.environ['DBREADPASS']
  print "  DAVIT_REMOTE_DIRFORMAT:", os.environ['DAVIT_REMOTE_DIRFORMAT']
  print "  DAVIT_REMOTE_FNAMEFMT:", os.environ['DAVIT_REMOTE_FNAMEFMT']
  print "  DAVIT_TMPDIR:", os.environ['DAVIT_TMPDIR']
  src='sftp'
  if os.path.isfile(expected_path):
    os.remove(expected_path)
  VTptr = radDataPtr(sTime,rad,eTime=eTime,channel=channel,bmnum=None,cp=None,fileType=fileType,filtered=filtered, src=src,noCache=True)
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
    beam  = ptr.readRec()
    print beam.time
    beam  = ptr.readRec()
    print beam.time
    print "Close pointer"
    ptr.close()
    print "reopen pointer"
    ptr.open()
    print "Should now be back at beginning:"
    beam  = ptr.readRec()
    print beam.time
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

  print "\nRunning local grab example for radDataPtr."
  print "Environment variables used:"
  print "  DAVIT_LOCAL_DIRFORMAT:", os.environ['DAVIT_LOCAL_DIRFORMAT']
  print "  DAVIT_LOCAL_FNAMEFMT:", os.environ['DAVIT_LOCAL_FNAMEFMT']
  print "  DAVIT_TMPDIR:", os.environ['DAVIT_TMPDIR']

  src='local'
  if os.path.isfile(expected_path):
    os.remove(expected_path)
  localptr = radDataPtr(sTime,rad,eTime=eTime,channel=channel,bmnum=None,cp=None,fileType=fileType,filtered=filtered, src=src,noCache=True)
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
    beam  = ptr.readRec()
    print beam.time
    beam  = ptr.readRec()
    print beam.time
    print "Close pointer"
    ptr.close()
    print "reopen pointer"
    ptr.open()
    print "Should now be back at beginning:"
    beam  = ptr.readRec()
    print beam.time
  except:
    print "record read failed for some reason"
  ptr.close()
  
  del localptr


  print "\nRunning sftp grab example for testing the channel option for channel c"
  rad='kod'
  channel='c'
  fileType='fitex'
  filtered=False
  sTime=datetime.datetime(2014,6,24,0,0)
  eTime=datetime.datetime(2014,6,24,2,2)
  expected_filename="20140624.000000.20140624.020200.kod.c.fitex"
  expected_path=os.path.join(tmpDir,expected_filename)
  expected_filesize=16148989
  expected_md5sum="ae7b4a7c8fea56af9639c39bea1453f2"
  print "Expected File:",expected_path

  print "\nRunning sftp grab example for radDataPtr."
  print "Environment variables used:"
  print "  DB:", os.environ['DB']
  print "  DB_PORT:",os.environ['DB_PORT']
  print "  DBREADUSER:", os.environ['DBREADUSER']
  print "  DBREADPASS:", os.environ['DBREADPASS']
  print "  DAVIT_REMOTE_DIRFORMAT:", os.environ['DAVIT_REMOTE_DIRFORMAT']
  print "  DAVIT_REMOTE_FNAMEFMT:", os.environ['DAVIT_REMOTE_FNAMEFMT']
  print "  DAVIT_TMPDIR:", os.environ['DAVIT_TMPDIR']
  src='sftp'
  if os.path.isfile(expected_path):
    os.remove(expected_path)
  VTptr = radDataPtr(sTime,rad,eTime=eTime,channel=channel,bmnum=None,cp=None,fileType=fileType,filtered=filtered, src=src,noCache=True)
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
    beam  = ptr.readRec()
    print beam.time
    beam  = ptr.readRec()
    print beam.time
    print "Close pointer"
    ptr.close()
    print "reopen pointer"
    ptr.open()
    print "Should now be back at beginning:"
    beam  = ptr.readRec()
    print beam.time
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

  print "\nRunning sftp grab example for testing the channel option for all"
  rad='kod'
  channel='all'
  fileType='fitex'
  filtered=False
  sTime=datetime.datetime(2014,6,24,0,0)
  eTime=datetime.datetime(2014,6,24,2,2)
  expected_filename="20140624.000000.20140624.020200.kod.all.fitex"
  expected_path=os.path.join(tmpDir,expected_filename)
  expected_filesize=31822045
  expected_md5sum="493bd0c937b6135cc608d0518d929077"
  print "Expected File:",expected_path

  print "\nRunning sftp grab example for radDataPtr."
  print "Environment variables used:"
  print "  DB:", os.environ['DB']
  print "  DB_PORT:",os.environ['DB_PORT']
  print "  DBREADUSER:", os.environ['DBREADUSER']
  print "  DBREADPASS:", os.environ['DBREADPASS']
  print "  DAVIT_REMOTE_DIRFORMAT:", os.environ['DAVIT_REMOTE_DIRFORMAT']
  print "  DAVIT_REMOTE_FNAMEFMT:", os.environ['DAVIT_REMOTE_FNAMEFMT']
  print "  DAVIT_TMPDIR:", os.environ['DAVIT_TMPDIR']
  src='sftp'
  if os.path.isfile(expected_path):
    os.remove(expected_path)
  VTptr = radDataPtr(sTime,rad,eTime=eTime,channel=channel,bmnum=None,cp=None,fileType=fileType,filtered=filtered, src=src,noCache=True)
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
    beam  = ptr.readRec()
    print beam.time
    beam  = ptr.readRec()
    print beam.time
    print "Close pointer"
    ptr.close()
    print "reopen pointer"
    ptr.open()
    print "Should now be back at beginning:"
    beam  = ptr.readRec()
    print beam.time
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

