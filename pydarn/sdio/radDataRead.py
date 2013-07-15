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
.. module:: radDataRead
   :synopsis: A module for reading radar data (iqdat, raw, fit)

.. moduleauthor:: AJ, 20130110

************************************
**Module**: pydarn.sdio.radDataRead
************************************

**Functions**:
  * :func:`pydarn.sdio.radDataRead.radDataOpen`
  * :func:`pydarn.sdio.radDataRead.radDataReadRec`
  * :func:`pydarn.sdio.radDataRead.radDataReadScan`
  * :func:`pydarn.sdio.radDataRead.radDataReadAll`
"""

def radDataOpen(sTime,rad,eTime=None,channel=None,bmnum=None,cp=None, \
                fileType='fitex',filtered=False, src=None,fileName=None, \
                custType='fitex',noCache=False):

  """A function to establish a pipeline through which we can read radar data.  first it tries the mongodb, then it tries to find local files, and lastly it sftp's over to the VT data server.

  **Args**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the beginning time for which you want data
    * **rad** (str): the 3-letter radar code for which you want data
    * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): the last time that you want data for.  if this is set to None, it will be set to 1 day after sTime.  default = None
    * **[channel]** (str): the 1-letter code for what channel you want data from, eg 'a','b',...  if this is set to None, data from ALL channels will be read. default = None
    * **[bmnum]** (int): the beam number which you want data for.  If this is set to None, data from all beams will be read. default = None
    * **[cp]** (int): the control program which you want data for.  If this is set to None, data from all cp's will be read.  default = None
    * **[fileType]** (str):  The type of data you want to read.  valid inputs are: 'fitex','fitacf','lmfit','rawacf','iqdat'.   if you choose a fit file format and the specified one isn't found, we will search for one of the others.  Beware: if you ask for rawacf/iq data, these files are large and the data transfer might take a long time.  default = 'fitex'
    * **[filtered]** (boolean): a boolean specifying whether you want the fit data to be boxcar filtered.  ONLY VALID FOR FIT.  default = False
    * **[src]** (str): the source of the data.  valid inputs are 'local' 'sftp'.  if this is set to None, it will try all possibilites sequentially.  default = None
    * **[fileName]** (str): the name of a specific file which you want to open.  default=None
    * **[custType]** (str): if fileName is specified, the filetype of the file.  default='fitex'
    * **[noCache]** (boolean): flag to indicate that you do not want to check first for cached files.  default = False.
  **Returns**:
    * **myPtr** (:class:`pydarn.sdio.radDataTypes.radDataPtr`): a radDataPtr object which contains a link to the data to be read.  this can then be passed to radDataReadRec in order to actually read the data.
    
  **Example**:
    ::
    
      import datetime as dt
      from pydarn.sdio import radDataOpen
      myPtr = radDataOpen(dt.datetime(2011,1,1),'sas',eTime=dt.datetime(2011,1,2),fileType='fitacf',filtered=False, src=None):

  **Note**:
    * The above example reads in only 1 day of data. If eTime=dt.datetime(2011,1,1,0,0,1) then 2 days would be read in.

  Written by AJ 20130110
  Modified by Ashton 20130710
  """
  import paramiko as p
  import re
  import string
  import datetime as dt, os, pydarn.sdio, glob
  from pydarn.sdio import radDataPtr
  from pydarn.radar import network
  from utils.timeUtils import datetimeToEpoch
  
  #check inputs
  assert(isinstance(sTime,dt.datetime)), \
    'error, sTime must be datetime object'
  assert(isinstance(rad,str) and len(rad) == 3), \
    'error, rad must be a 3 char string'
  assert(eTime == None or isinstance(eTime,dt.datetime)), \
    'error, eTime must be datetime object or None'
  assert(channel == None or (isinstance(channel,str) and len(channel) == 1)), \
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

  #Since ISAS stores an entire day worth of data in one file, eTime=sTime + 1 day specifies one day of data
  if(eTime == None):
    eTime = sTime+dt.timedelta(days=1)
  else:
    if sTime < eTime:
  #So then if eTime is specified, need to round it up to the nearest whole day
      if dt.datetime.strptime(eTime.strftime("%Y%m%d"),"%Y%m%d") < eTime:
        eTime=dt.datetime.strptime(eTime.strftime("%Y%m%d"),"%Y%m%d")+dt.timedelta(days=1)
    else:
      assert(1==2),'sTime must be less than eTime!'
  #And for sTime we need to round it down to the nearest whole day
  sTime=dt.datetime.strptime(sTime.strftime("%Y%m%d"),"%Y%m%d")
    
  #create a datapointer object
  myPtr = radDataPtr(sTime=sTime,eTime=eTime,stid=int(network().getRadarByCode(rad).id), 
                      channel=channel,bmnum=bmnum,cp=cp)
  
  filelist = []
  if(fileType == 'fitex'): arr = ['fitex','fitacf','lmfit']
  elif(fileType == 'fitacf'): arr = ['fitacf','fitex','lmfit']
  elif(fileType == 'lmfit'): arr = ['lmfit','fitex','fitacf']
  else: arr = [fileType]

  #move back a little in time because files often start at 2 mins after the hour
#  sTime = sTime-dt.timedelta(minutes=4)
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
      if filtered:
        #for f in glob.glob("%s????????.??????.????????.??????.%s.%sf" % (tmpDir,rad,fileType)):
	for f in glob.glob("%s????????.????????.%s.%sf" % (tmpDir,rad,fileType)):
          try:
            ff = string.replace(f,tmpDir,'')
            #check time span of file
 #           t1 = dt.datetime(int(ff[0:4]),int(ff[4:6]),int(ff[6:8]),int(ff[9:11]),int(ff[11:13]),int(ff[13:15]))
            t1 = dt.datetime(int(ff[0:4]),int(ff[4:6]),int(ff[6:8]),)
            t2 = dt.datetime(int(ff[10:14]),int(ff[14:16]),int(ff[16:18]))
#            t2 = dt.datetime(int(ff[16:20]),int(ff[20:22]),int(ff[22:24]),int(ff[25:27]),int(ff[27:29]),int(ff[29:31]))
           #check if file covers our timespan
            if t1 <= sTime and t2 >= eTime:
              cached = True
              filelist.append(f)
              print 'Found cached file: %s' % f
              break
          except Exception,e:
            print e
      if not cached:
        for f in glob.glob("%s????????.????????.%s.%s" % (tmpDir,rad,fileType)):
          try:
            ff = string.replace(f,tmpDir,'')
            #check time span of file
            t1 = dt.datetime(int(ff[0:4]),int(ff[4:6]),int(ff[6:8]))
            t2 = dt.datetime(int(ff[9:13]),int(ff[13:15]),int(ff[15:17]))
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
#THIS HAS NOT BEEN EDITED FOR THE ISAS GROUP AT UofS. IF DAVITPY IS TO BE PUT ON CHAPMAN, THIS WILL HAVE
#TO BE LOOKED AT. FOR NOW, CONDITIONAL EDITED TO SKIP.
  if 1==2:# not cached and (src == None or src == 'local') and fileName == None:
    try:
      for ftype in arr:
        print '\nLooking locally for',ftype,'files'
        #deal with UAF naming convention
        fnames = ['??.??.???.'+ftype+'.*']
        if(channel == None): fnames.append('??.??.???.a.*')
        else: fnames.append('??.??.???.'+channel+'.*')
        for form in fnames:
          #iterate through all of the hours in the request
          #ie, iterate through all possible file names
          ctime = sTime.replace(minute=0)
          if(ctime.hour % 2 == 1): ctime = ctime.replace(hour=ctime.hour-1)
          while ctime <= eTime:
            #directory on the data server
            ##################################################################
            ### IF YOU ARE A USER NOT AT VT, YOU PROBABLY HAVE TO CHANGE THIS
            ### TO MATCH YOUR DIRECTORY STRUCTURE
            ##################################################################
            myDir = '/sd_data/'+ctime.strftime("%Y")+'/'+ctime.strftime("%m")+'/'
            hrStr = ctime.strftime("%H")
            dateStr = ctime.strftime("%Y%m%d")
            #iterate through all of the files which begin in this hour
            for filename in glob.glob(myDir+dateStr+'.'+hrStr+form):
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
              t1 = dt.datetime(int(ff[0:4]),int(ff[4:6]),int(ff[6:8]),int(ff[9:11]),int(ff[11:13]),int(ff[14:16]))
              if fileSt == None or t1 < fileSt: fileSt = t1

            ##################################################################
            ### END SECTION YOU WILL HAVE TO CHANGE
            ##################################################################
            ctime = ctime+dt.timedelta(hours=1)
          if(len(filelist) > 0):
            print 'found',ftype,'data in local files'
            myPtr.fType,myPtr.dType = ftype,'dmap'
            fileType = ftype
            break
        if(len(filelist) > 0): break
        else:
          print  'could not find',ftype,'data in local files'
    except Exception, e:
      print e
      print 'problem reading local data, perhaps you are not at VT?'
      print 'you probably have to edit radDataRead.py'
      print 'I will try to read from other sources'
      src=None
#END OF NOT EDITED        



  #finally, check the chapman sftp server if we have not yet found files
  if (src == None or src == 'sftp') and myPtr.ptr == None and len(filelist) == 0 and fileName == None:
    for ftype in arr:
      print '\nLooking on the remote SFTP server for',ftype,'files'
      try:
        #deal with UofS naming convention
        fnames = ['.C0.'+rad+'.'+ftype]
        if(channel == None): fnames.append('..\...\....\.a\.')
        else: fnames.append('..........'+channel+'.'+ftype)
        for form in fnames:
          #create a transport object for use in sftp-ing
          transport = p.Transport((os.environ['ISASDB'], 22))
          transport.connect(username=os.environ['DBREADUSER'],password=os.environ['DBREADPASS'])
          sftp = p.SFTPClient.from_transport(transport)
          
          #iterate through all of the hours in the request
          #ie, iterate through all possible file names
          ctime = sTime
          oldyr = ''
          while ctime < eTime:
            #directory on the data server
            myDir = 'fitcon/'+ctime.strftime("%Y")+'/'+ctime.strftime("%m")+'/'
            dateStr = ctime.strftime("%Y%m%d")
            if(ctime.strftime("%Y") != oldyr):
              #get a list of all the files in the directory
              allFiles = sftp.listdir(myDir)
              oldyr = ctime.strftime("%Y")
            #create a regular expression to find files of this day, at this hour
            regex = re.compile(dateStr+form)
            #go thorugh all the files in the directory
            for aFile in allFiles:
              #if we have a file match between a file and our regex
              if(regex.match(aFile)): 
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
                t1 = dt.datetime(int(ff[0:4]),int(ff[4:6]),int(ff[6:8]))
                if fileSt == None or t1 < fileSt: fileSt = t1

            ctime = ctime+dt.timedelta(days=1)
          if len(filelist) > 0 :
            print 'found',ftype,'data on sftp server'
            myPtr.fType,myPtr.dType = ftype,'dmap'
            fileType = ftype
            break
        if len(filelist) > 0 : break
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
      tmpName = '%s%s.%s.%s.%s' % (tmpDir, \
                fileSt.strftime("%Y%m%d"), \
                eTime.strftime("%Y%m%d"),rad,fileType)
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
    if(not filtered): 
      myPtr.ptr = open(tmpName,'r')
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
        myPtr.ptr = open(fTmpName,'r')
      except Exception,e:
        print 'problem opening file'
        print e
        return None
  if(myPtr.ptr != None): 
    if(myPtr.dType == None): myPtr.dType = 'dmap'
    return myPtr
  else:
    print '\nSorry, we could not find any data for you :('
    return None
  
def radDataReadRec(myPtr):
  """A function to read a single record of radar data from a :class:`pydarn.sdio.radDataTypes.radDataPtr` object
  
  .. note::
    to use this, you must first create a :class:`pydarn.sdio.radDataTypes.radDataPtr` object with :func:`radDataOpen` 

  **Args**:
    * **myPtr** (:class:`pydarn.sdio.radDataTypes.radDataPtr`): contains the pipeline to the data we are after
  **Returns**:
    * **myBeam** (:class:`pydarn.sdio.radDataTypes.beamData`): an object filled with the data we are after.  *will return None when finished reading*
    
  **Example**:
    ::
    
      import datetime as dt
      myPtr = radDataOpen(dt.datetime(2011,1,1),'bks',eTime=dt.datetime(2011,1,1,2),channel='a', bmnum=7,cp=153,fileType='fitex',filtered=False, src=None):
      myBeam = radDataReadRec(myPtr)
    
  Written by AJ 20130110
  """

  from pydarn.sdio.radDataTypes import radDataPtr, beamData, \
    fitData, prmData, rawData, iqData, alpha
  import pydarn, datetime as dt
  
  #check input
  assert(isinstance(myPtr,radDataPtr)),\
    'error, input must be of type radDataPtr'
  if(myPtr.ptr == None):
    print 'error, your pointer does not point to any data'
    return None
  if myPtr.ptr.closed:
    print 'error, your file pointer is closed'
    return None
  
  myBeam = beamData()
  
  #do this until we reach the requested start time
  #and have a parameter match
  while(1):
    dfile = pydarn.dmapio.readDmapRec(myPtr.ptr)
    #check for valid data
    if dfile == None or dt.datetime.utcfromtimestamp(dfile['time']) > myPtr.eTime:
      #if we dont have valid data, clean up, get out
      print '\nreached end of data'
      myPtr.ptr.close()
      return None
    #check that we're in the time window, and that we have a 
    #match for the desired params
    if dfile['channel'] < 2: channel = 'a'
    else: channel = alpha[dfile['channel']-1]
    if(dt.datetime.utcfromtimestamp(dfile['time']) >= myPtr.sTime and \
        dt.datetime.utcfromtimestamp(dfile['time']) <= myPtr.eTime and \
        (myPtr.stid == None or dfile['stid'] == 0 or myPtr.stid == dfile['stid']) and
        (myPtr.channel == None or myPtr.channel == channel) and
        (myPtr.bmnum == None or myPtr.bmnum == dfile['bmnum']) and
        (myPtr.cp == None or myPtr.cp == dfile['cp'])):
      #fill the beamdata object
      myBeam.updateValsFromDict(dfile)
      myBeam.fit.updateValsFromDict(dfile)
      myBeam.prm.updateValsFromDict(dfile)
      myBeam.rawacf.updateValsFromDict(dfile)
      myBeam.iqdat.updateValsFromDict(dfile)
      myBeam.fType = myPtr.fType
      if(myPtr.fType == 'fitacf' or myPtr.fType == 'fitex' or myPtr.fType == 'lmfit'):
        if myBeam.fit.slist == None: 
          myBeam.fit.slist = []
      return myBeam
      
def radDataReadScan(myPtr):
  """A function to read a full scan of data from a :class:`pydarn.sdio.radDataTypes.radDataPtr` object
  
  .. note::
    to use this, you must first create a :class:`pydarn.sdio.radDataTypes.radDataPtr` object with :func:`radDataOpen`
    
  .. note::
    This will ignore any bmnum request.  Also, if no channel was specified in radDataOpen, it will only read channel 'a'

  **Args**:
    * **myPtr** (:class:`pydarn.sdio.radDataTypes.radDataPtr`): contains the pipeline to the data we are after
  **Returns**:
    * **myScan** (:class:`pydarn.sdio.radDataTypes.scanData`): an object filled with the data we are after.  *will return None when finished reading*
    
  **Example**:
    ::
    
      import datetime as dt
      myPtr = radDataOpen(dt.datetime(2011,1,1),'bks',eTime=dt.datetime(2011,1,1,2),channel='a', bmnum=7,cp=153,fileType='fitex',filtered=False, src=None):
      myBeam = radDataReadScan(myPtr)
    
  Written by AJ 20130110
  """
  from pydarn.sdio import radDataPtr, beamData, fitData, prmData, \
    rawData, iqData, alpha, scanData
  import pydarn, datetime as dt
  
  #check input
  assert(isinstance(myPtr,radDataPtr)),\
    'error, input must be of type radDataPtr'
  if(myPtr.ptr == None):
    print 'error, your pointer does not point to any data'
    return None
  if myPtr.ptr.closed:
    print 'error, your file pointer is closed'
    return None
  
  myScan = scanData()
  if myPtr.fBeam != None: myScan.append(myPtr.fBeam)
  else: firstflg = True
  if myPtr.channel == None: tmpchn = 'a'
  else: tmpchn = myPtr.channel
  
  #do this until we reach the requested start time
  #and have a parameter match
  while(1):
      #read the next record from the dmap file
    dfile = pydarn.dmapio.readDmapRec(myPtr.ptr)
    #check for valid data
    if(dfile == None or dt.datetime.utcfromtimestamp(dfile['time']) > myPtr.eTime):
      #if we dont have valid data, clean up, get out
      print '\nreached end of data'
      myPtr.ptr.close()
      return None
    #check that we're in the time window, and that we have a 
    #match for the desired params
    if(dfile['channel'] < 2): channel = 'a'
    else: channel = alpha[dfile['channel']-1]
    if(dt.datetime.utcfromtimestamp(dfile['time']) >= myPtr.sTime and \
        dt.datetime.utcfromtimestamp(dfile['time']) <= myPtr.eTime and \
        (myPtr.stid == None or myPtr.stid == dfile['stid']) and
        (tmpchn == channel) and
        (myPtr.cp == None or myPtr.cp == dfile['cp'])):
      #fill the beamdata object
      myBeam = beamData()
      myBeam.updateValsFromDict(dfile)
      myBeam.fit.updateValsFromDict(dfile)
      myBeam.prm.updateValsFromDict(dfile)
      myBeam.rawacf.updateValsFromDict(dfile)
      myBeam.iqdat.updateValsFromDict(dfile)
      myBeam.fType = myPtr.fType
      if(myPtr.fType == 'fitacf' or myPtr.fType == 'fitex' or myPtr.fType == 'lmfit'):
        if(myBeam.fit.slist == None): 
          myBeam.fit.slist = []
      if(myBeam.prm.scan == 0 or firstflg):
        myScan.append(myBeam)
        firstflg = False
      else:
        myPtr.fBeam = myBeam
        return myScan

def radDataReadAll(myPtr):
  """A function to read a large amount (to the end of the request) of radar data into a list from a :class:`pydarn.sdio.radDataTypes.radDataPtr` object
  
  .. note::
    to use this, you must first create a :class:`pydarn.sdio.radDataTypes.radDataPtr` object with :func:`radDataOpen`

  **Args**:
    * **myPtr** (:class:`pydarn.sdio.radDataTypes.radDataPtr`): contains the pipeline to the data we are after
  **Returns**:
    * **myList** (list): a list filled with :class:`pydarn.sdio.radDataTypes.scanData` objects holding the data we are after.  *will return None if nothing is found*
    
  **Example**:
    ::
    
      import datetime as dt
      myPtr = radDataOpen(dt.datetime(2011,1,1),'bks',eTime=dt.datetime(2011,1,1,2),channel='a', bmnum=7,cp=153,fileType='fitex',filtered=False, src=None):
      myList = radDataReadAll(myPtr)
    
  Written by AJ 20130606
  """
  from pydarn.sdio import radDataPtr, beamData, fitData, prmData, \
    rawData, iqData, alpha, scanData
  import pydarn, datetime as dt
  
  #check input
  if not isinstance(myPtr,radDataPtr):
    'error, input must be of type radDataPtr'
    return None
  if myPtr.ptr == None:
    print 'error, your pointer does not point to any data'
    return None
  if myPtr.ptr.closed:
    print 'error, your file pointer is closed'
    return None
  
  myScan = scanData()
  if(myPtr.fBeam != None): myScan.append(myPtr.fBeam)
  else: firstflg = True
  if(myPtr.channel == None): tmpchn = 'a'
  else: tmpchn = myPtr.channel
  
  #do this until we reach the requested start time
  #and have a parameter match
  while(1):
      #read the next record from the dmap file
    dfile = pydarn.dmapio.readDmapRec(myPtr.ptr)
    #check for valid data
    if(dfile == None or dt.datetime.utcfromtimestamp(dfile['time']) > myPtr.eTime):
      #if we dont have valid data, clean up, get out
      print '\nreached end of data'
      myPtr.ptr.close()
      return None
    #check that we're in the time window, and that we have a 
    #match for the desired params
    if(dfile['channel'] < 2): channel = 'a'
    else: channel = alpha[dfile['channel']-1]
    if(dt.datetime.utcfromtimestamp(dfile['time']) >= myPtr.sTime and \
        dt.datetime.utcfromtimestamp(dfile['time']) <= myPtr.eTime and \
        (myPtr.stid == None or myPtr.stid == dfile['stid']) and
        (tmpchn == channel) and
        (myPtr.cp == None or myPtr.cp == dfile['cp'])):
      #fill the beamdata object
      myBeam = beamData()
      myBeam.updateValsFromDict(dfile)
      myBeam.fit.updateValsFromDict(dfile)
      myBeam.prm.updateValsFromDict(dfile)
      myBeam.rawacf.updateValsFromDict(dfile)
      myBeam.iqdat.updateValsFromDict(dfile)
      myBeam.fType = myPtr.fType
      if(myPtr.fType == 'fitacf' or myPtr.fType == 'fitex' or myPtr.fType == 'lmfit'):
        if(myBeam.fit.slist == None): myBeam.fit.slist = []
      if(myBeam.prm.scan == 0 or firstflg):
        myScan.append(myBeam)
        firstflg = False
      else:
        myPtr.fBeam = myBeam
        return myScan

