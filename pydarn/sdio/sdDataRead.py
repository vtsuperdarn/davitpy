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
.. module:: sdDataRead
   :synopsis: A module for reading processed SD data (grid, map)

.. moduleauthor:: AJ, 20130607

************************************
**Module**: pydarn.sdio.sdDataRead
************************************

**Functions**:
  * :func:`pydarn.sdio.sdDataRead.sdDataOpen`
  * :func:`pydarn.sdio.sdDataRead.sdDataReadRec`
  * :func:`pydarn.sdio.sdDataRead.sdDataReadAll`
"""

def sdDataOpen(sTime,hemi='north',eTime=None,fileType='grdex',src=None,fileName=None, \
                custType='grdex',noCache=False):

  """A function to establish a pipeline through which we can read radar data.  first it tries the mongodb, then it tries to find local files, and lastly it sftp's over to the VT data server.

  **Args**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the beginning time for which you want data
    * **[hemi]** (str): the hemisphere for which you want data, 'north' or 'south'.  default = 'north'
    * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): the last time that you want data for.  if this is set to None, it will be set to 1 day after sTime.  default = None
    * **[fileType]** (str):  The type of data you want to read.  valid inputs are: 'grd','grdex','map','mapex'.  If you choose a file format and the specified one isn't found, we will search for one of the others (eg mapex instead of map). default = 'grdex'.
    * **[src]** (str): the source of the data.  valid inputs are 'local' 'sftp'.  if this is set to None, it will try all possibilites sequentially.  default = None
    * **[fileName]** (str): the name of a specific file which you want to open.  If this is set, we will not look for cached files.  default=None
    * **[custType]** (str): if fileName is specified, the filetype of the file.  default = 'grdex'
    * **[noCache]** (boolean): flag to indicate that you do not want to check first for cached files.  default = False.
  **Returns**:
    * **myPtr** (:class:`pydarn.sdio.sdDataTypes.sdDataPtr`): a sdDataPtr object which contains a link to the data to be read.  this can then be passed to sdDataReadRec in order to actually read the data.
    
  **Example**:
    ::
    
      import datetime as dt
      myPtr = sdDataOpen(dt.datetime(2011,1,1),hemi='north'):
    
  Written by AJ 20130607
  """

  import paramiko as p
  import re
  import string
  import datetime as dt
  import os
  import pydarn.sdio
  import glob
  from pydarn.sdio import sdDataPtr
  from pydarn.radar import network
  from utils.timeUtils import datetimeToEpoch
  
  #check inputs
  assert(isinstance(sTime,dt.datetime)), \
    'error, sTime must be datetime object'
  assert(hemi == 'north' or hemi == 'south'), \
    "error, hemi must be 'north' or 'south'"
  assert(eTime == None or isinstance(eTime,dt.datetime)), \
    'error, eTime must be datetime object or None'
  assert(fileType == 'grd' or fileType == 'grdex' or \
    fileType == 'map' or fileType == 'mapex'), \
    "error, fileType must be one of: 'grd','grdex','map','mapex'"
  assert(fileName == None or isinstance(fileName,str)), \
    'error, fileName must be None or a string'
  assert(src == None or src == 'local' or src == 'sftp'), \
    'error, src must be one of None,local,sftp'
    
  if eTime == None: eTime = sTime+dt.timedelta(days=1)
    
  #create a datapointer object
  myPtr = sdDataPtr(sTime=sTime,eTime=eTime,hemi=hemi)
  
  filelist = []
  if fileType == 'grd': arr = ['grd','grdex']
  elif fileType == 'grdex': arr = ['grdex','grd']
  elif fileType == 'map': arr = ['map','mapex']
  elif fileType == 'mapex': arr = ['mapex','map']
  else: arr = [fileType]

  #move back a little in time because files often start at 2 mins after the hour
  sTime = sTime-dt.timedelta(minutes=4)
  #a temporary directory to store a temporary file
  tmpDir = '/tmp/sd/'
  d = os.path.dirname(tmpDir)
  if not os.path.exists(d):
    os.makedirs(d)

  cached = False
  fileSt = None

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
      myPtr.fType,myPtr.dType = custType,'dmap'
      fileSt = sTime
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
            if t1 <= sTime and t2 >= eTime:
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
        ##################################################################
        ### IF YOU ARE A USER NOT AT VT, YOU PROBABLY HAVE TO CHANGE THIS
        ### TO MATCH YOUR DIRECTORY/FILE STRUCTURE
        ##################################################################
        print '\nLooking locally for',ftype,'files'
        form = '%s.%s.*' % (hemi,ftype)
        #iterate through all of the days in the request
        #ie, iterate through all possible file names
        ctime = sTime
        while ctime <= eTime:
          #directory on the data server
          myDir = '/sd-data/'+ctime.strftime("%Y")+'/'+ftype+'/'+hemi+'/'
          dateStr = ctime.strftime("%Y%m%d")
          #iterate through all of the files which begin in this hour
          for filename in glob.glob(myDir+dateStr+'.'+form):
            outname = string.replace(filename,myDir,tmpDir)
            #unzip the compressed file
            if(string.find(filename,'.bz2') != -1):
              outname = string.replace(outname,'.bz2','')
              print 'bunzip2 -c '+filename+' > '+outname+'\n'
              os.system('bunzip2 -c '+filename+' > '+outname)
            elif(string.find(filename,'.gz') != -1):
              outname = string.replace(outname,'.gz','')
              print 'gunzip -c '+filename+' > '+outname+'\n'
              os.system('gunzip -c '+filename+' > '+outname)
            
            filelist.append(outname)

            #HANDLE CACHEING NAME
            ff = string.replace(outname,tmpDir,'')
            #check the beginning time of the file (for cacheing)
            t1 = dt.datetime(int(ff[0:4]),int(ff[4:6]),int(ff[6:8]),0,0,0)
            if fileSt == None or t1 < fileSt: fileSt = t1

          ctime = ctime+dt.timedelta(days=1)
        if len(filelist) > 0:
          print 'found',ftype,'data in local files'
          myPtr.fType = ftype
          fileType = ftype
          break
        else:
          print  'could not find',ftype,'data in local files'
        ##################################################################
        ### END SECTION YOU WILL HAVE TO CHANGE
        ##################################################################
    except Exception, e:
      print e
      print 'problem reading local data, perhaps you are not at VT?'
      print 'you probably have to edit sdDataRead.py'
      print 'I will try to read from other sources'
      src=None
        
  #finally, check the VT sftp server if we have not yet found files
  if (src == None or src == 'sftp') and myPtr.ptr == None and len(filelist) == 0 and fileName == None:
    for ftype in arr:
      print '\nLooking on the remote SFTP server for',ftype,'files'
      try:
        form = '......'+ftype
        #create a transport object for use in sftp-ing
        transport = p.Transport((os.environ['DB'], 22))
        transport.connect(username=os.environ['DBREADUSER'],password=os.environ['DBREADPASS'])
        sftp = p.SFTPClient.from_transport(transport)
        
        #iterate through all of the hours in the request
        #ie, iterate through all possible file names
        ctime = sTime
        oldyr = ''
        while ctime <= eTime:
          #directory on the data server
          myDir = '/data/'+ctime.strftime("%Y")+'/'+ftype+'/'+hemi+'/'
          dateStr = ctime.strftime("%Y%m%d")
          if ctime.strftime("%Y") != oldyr:
            #get a list of all the files in the directory
            allFiles = sftp.listdir(myDir)
            oldyr = ctime.strftime("%Y")
          #create a regular expression to find files of this day, at this hour
          regex = re.compile(dateStr+'.'+form)
          #go thorugh all the files in the directory
          for aFile in allFiles:
            #if we have a file match between a file and our regex
            if regex.match(aFile): 
              print 'copying file '+myDir+aFile+' to '+tmpDir+aFile
              filename = tmpDir+aFile
              #download the file via sftp
              sftp.get(myDir+aFile,filename)
              #unzip the compressed file
              if(string.find(filename,'.bz2') != -1):
                outname = string.replace(filename,'.bz2','')
                print 'bunzip2 -c '+filename+' > '+outname+'\n'
                os.system('bunzip2 -c '+filename+' > '+outname)
              elif(string.find(filename,'.gz') != -1):
                outname = string.replace(filename,'.gz','')
                print 'gunzip -c '+filename+' > '+outname+'\n'
                os.system('gunzip -c '+filename+' > '+outname)
              else:
                print 'It seems we have downloaded an uncompressed file :/'
                print 'Strange things might happen from here on out...'
                
              filelist.append(outname)

              #HANDLE CACHEING NAME
              ff = string.replace(outname,tmpDir,'')
              #check the beginning time of the file
              t1 = dt.datetime(int(ff[0:4]),int(ff[4:6]),int(ff[6:8]),0,0,0)
              if fileSt == None or t1 < fileSt: fileSt = t1

          ctime = ctime+dt.timedelta(days=1)
        if len(filelist) > 0 :
          print 'found',ftype,'data on sftp server'
          myPtr.fType = ftype
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
                fileSt.strftime("%Y%m%d"),fileSt.strftime("%H%M%S"), \
                eTime.strftime("%Y%m%d"),eTime.strftime("%H%M%S"),hemi,fileType)
      print 'cat '+string.join(filelist)+' > '+tmpName
      os.system('cat '+string.join(filelist)+' > '+tmpName)
      for filename in filelist:
        print 'rm '+filename
        os.system('rm '+filename)
    else:
      tmpName = filelist[0]
      myPtr.fType = fileType
      myPtr.dType = 'dmap'

    #filter(if desired) and open the file
    myPtr.fd = os.open(tmpName,os.O_RDONLY)
    myPtr.ptr = os.fdopen(myPtr.fd)
  if myPtr.ptr != None: 
    return myPtr
  else:
    print '\nSorry, we could not find any data for you :('
    return None
  
def sdDataReadRec(myPtr):
  """A function to read a single record of radar data from a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object
  
  .. note::
    to use this, you must first create a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object with :func:`sdDataOpen` 

  **Args**:
    * **myPtr** (:class:`pydarn.sdio.sdDataTypes.sdDataPtr`): contains the pipeline to the data we are after
  **Returns**:
    * **myData** (:class:`pydarn.sdio.sdDataTypes.gridData` or :class:`pydarn.sdio.sdDataTypes.mapData`): an object filled with the data we are after.  *will return None when finished reading the file*
    
  **Example**:
    ::
    
      import datetime as dt
      myPtr = sdDataOpen(dt.datetime(2011,1,1),'south'):
      myData = sdDataReadRec(myPtr)
    
  Written by AJ 20130610
  """

  from pydarn.sdio.sdDataTypes import sdDataPtr, gridData, mapData, alpha
  import pydarn
  import datetime as dt
  
  #check input
  assert(isinstance(myPtr,sdDataPtr)),\
    'error, input must be of type sdDataPtr'
  if myPtr.ptr == None:
    print 'error, your pointer does not point to any data'
    return None
  if myPtr.ptr.closed:
    print 'error, your file pointer is closed'
    return None
  

  if myPtr.fType == 'grd' or myPtr.fType == 'grdex':
    myData = gridData()
  elif myPtr.fType == 'map' or myPtr.fType == 'mapex':
    myData = mapData()
  else:
    print 'error, unrecognized file type'
    return None

  #do this until we reach the requested start time
  #and have a parameter match
  while(1):
    dfile = pydarn.dmapio.readDmapRec(myPtr.fd)
    #check for valid data
    try:
      dtime = dt.datetime(dfile['start.year'],dfile['start.month'],dfile['start.day'], \
                          dfile['start.hour'],dfile['start.minute'],int(dfile['start.second']))
    except Exception,e:
      print e
      print 'problem reading time from file, returning None'
      return None
    if dfile == None or dtime > myPtr.eTime:
      #if we dont have valid data, clean up, get out
      print '\nreached end of data'
      myPtr.ptr.close()
      return None
    #check that we're in the time window, and that we have a 
    #match for the desired params
    if myPtr.sTime <= dtime <= myPtr.eTime:
      #fill the data object
      if myPtr.fType == 'grd' or myPtr.fType == 'grdex':
        myData = gridData(dataDict=dfile)
      elif myPtr.fType == 'map' or myPtr.fType == 'mapex':
        myData = mapData(dataDict=dfile)
      else:
        print 'error, unrecognized file type'
        return None
      myData.fType = myPtr.fType
      return myData

def sdDataReadAll(myPtr):
  """A function to read a large amount (to the end of the request) of radar data into a list from a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object
  
  .. note::
    to use this, you must first create a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object with :func:`sdDataOpen`

  **Args**:
    * **myPtr** (:class:`pydarn.sdio.sdDataTypes.sdDataPtr`): contains the pipeline to the data we are after
  **Returns**:
    * **myList** (list): a list filled with :class:`pydarn.sdio.sdDataTypes.gridData` or :class:`pydarn.sdio.sdDataTypes.mapData` objects holding the data we are after.  *will return None if nothing is found*
    
  **Example**:
    ::
    
      import datetime as dt
      myPtr = sdDataOpen(dt.datetime(2011,1,1),'bks',eTime=dt.datetime(2011,1,1,2),channel='a', bmnum=7,cp=153,fileType='fitex',filtered=False, src=None):
      myList = sdDataReadAll(myPtr)
    
  Written by AJ 20130606
  """
  from pydarn.sdio.sdDataTypes import sdDataPtr, gridData, mapData, alpha
  import pydarn
  import datetime as dt
  
  #check input
  assert(isinstance(myPtr,sdDataPtr)),\
    'error, input must be of type sdDataPtr'
  if myPtr.ptr == None:
    print 'error, your pointer does not point to any data'
    return None
  if myPtr.ptr.closed:
    print 'error, your file pointer is closed'
    return None
  
  myList = []
  #do this until we reach the requested start time
  #and have a parameter match
  while(1):

    dfile = pydarn.dmapio.readDmapRec(myPtr.fd)
    print "python tell:",myPtr.ptr.tell()
    #check for valid data
    try:
      dtime = dt.datetime(dfile['start.year'],dfile['start.month'],dfile['start.day'], \
                          dfile['start.hour'],dfile['start.minute'],int(dfile['start.second']))
    except Exception,e:
      print e
      print 'problem reading time from file, returning None'
      return None

    if dfile == None or dtime > myPtr.eTime:
      #if we dont have valid data, clean up, get out
      print '\nreached end of data'
      myPtr.ptr.close()
      break
    #check that we're in the time window, and that we have a 
    #match for the desired params
    if myPtr.sTime <= dtime <= myPtr.eTime:
      #fill the beamdata object
      if myPtr.fType == 'grd' or myPtr.fType == 'grdex':
        myData = gridData(dataDict=dfile)
      elif myPtr.fType == 'map' or myPtr.fType == 'mapex':
        myData = mapData(dataDict=dfile)
      else:
        print 'error, unrecognized file type'
        return None
      myData.fType = myPtr.fType
      myList.append(myData)

  if len(myList) > 0:
    print 'returning a list with %d records of data' % len(myList)
    return myList
  else:
    print 'No data found, returning None'
    return None

