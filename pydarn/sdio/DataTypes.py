# Copyright (C) 2014 Ashton Reimer
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
.. module:: DataTypes
   :synopsis: the parent class needed for reading data (dmap, hdf5)
.. moduleauthor:: Ashton, 20140822, generalized from radDataTypes.py by Jef Spaleta

*********************
**Module**: pydarn.sdio.DataTypes
*********************

**Classes**:
  * :class:`pydarn.sdio.DataTypes.DataPtr`

"""


from utils import twoWayDict
alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m', \
          'n','o','p','q','r','s','t','u','v','w','x','y','z']

def DataPtr(dataType,*kwargs):

    if dataType=='dmap':
        return dmapFile(dataType)


class ParentPtr(object):
    """A generalized data pointer class which contains general methods for reading 
       various data file (dmap, hdf5, etc.) types into SuperDARN data types (fit, raw, iqdat, map, etc.).
    
    **Public Attrs**:
      * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): start time of the request
      * **eTime** (`datetime <http://tinyurl.com/bl352yx>`_): end time of the request
      * **fType** (str): the file type, 'fitacf', 'rawacf', 'iqdat', 'fitex', 'lmfit'
      * **dType** (str): the file data type, 'dmap','hdf5'
      * **recordIndex** (dict): look up dictionary for file offsets for all records 
      * **scanStartIndex** (dict): look up dictionary for file offsets for scan start records
    **Private Attrs**:
      * **ptr** (file): the data pointer (different depending dmap or hdf5)
      * **fd** (int): the file descriptor 
      * **filename** (str): the name of the currently open file

    **Methods**:
      * **open** 
      * **close** 
      * **createIndex** : Index the offsets for all records and scan boundaries
      * **offsetSeek** : Seek file to requested byte offset, checking to make sure it in the record index
      * **offsetTell** : Current byte offset
      * **rewind** : rewind file back to the beginning 
      * **read** : read record at current file offset in to a dictionary
     
    Written by ASR 20140822
    """
    def __init__(self,sTime=None,eTime=None,fileType=None, src=None,fileName=None,noCache=False,dataType=None):

        import pydarn

        dataTypeList = ['dmap']    

        assert(dataType in dataTypeList), \
            "Error, dataType not supported. Supported data types: "+str(dataTypeList)

        self.sTime = sTime
        self.eTime = eTime
        self.fType = fileType
        self.dType = dataType
        self.recordIndex = None
        self.scanStartIndex = None
        self.__filename = fileName 
        self.__fd = None
        self.__ptr =  None



class dmapFile(ParentPtr):

    """A class containing the methods for reading dmap data files into 
       SuperDARN data types (fit, raw, iqdat, map, etc.).
    
    **Public Attrs**:
      * **members** (list): list of strings naming the user defined methods of this class

    **Methods**:
      * **open** 
      * **close** 
      * **createIndex** : Index the offsets for all records and scan boundaries
      * **offsetSeek** : Seek file to requested byte offset, checking to make sure it in the record index
      * **offsetTell** : Current byte offset
      * **rewind** : rewind file back to the beginning 
      * **read** : read record at current file offset in to a dictionary
     
    Written by ASR 20140822
    """

    def __init__(self,dataType,*kwargs):
        #self.members=['__del__','__iter__','next','open', \
        #              'createIndex','offsetSeek','offsetTell', \
        #              'rewind','read','close']

        super(dmapFile,self).__init__(dataType=dataType,*kwargs)


    def __del__(self):
        self.close() 

    def __iter__(self):
        return self

    def next(self):
        data=self.readRec()
        if data is None:
            raise StopIteration
        else:
            return data

    def open(self):
        """open the associated filename."""
        import os
        self.__fd = os.open(self.__filename,os.O_RDONLY)
        self.__ptr = os.fdopen(self.__fd)

    def createIndex(self):
        """
           Create dictionary of offsets as a function of timestamp.
  
        """

        # This method will have to do different things depending 
        # on self.dType (for future other data file support ie. hdf5)

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
        """
           Jump to dmap record at supplied byte offset.
           Require offset to be in record index list unless forced. 
        """

        # This method will have to do different things depending 
        # on self.dType (for future other data file support ie. hdf5)

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
        """
           Jump to dmap record at supplied byte offset. 

        """

        # This method will have to do different things depending 
        # on self.dType (for future other data file support ie. hdf5)

        from pydarn.dmapio import getDmapOffset
        return getDmapOffset(self.__fd)

    def rewind(self):
        """
           Jump to beginning of dmap file.
        """

        # This method will have to do different things depending 
        # on self.dType (for future other data file support ie. hdf5)
        from pydarn.dmapio import setDmapOffset 
        return setDmapOffset(self.__fd,0)

    def read(self):
       """
          A function to read a single record of data from a dmap file.

       **Returns**:
       * **dfile** (dict): a dictionary with the data in the dmap record.  *will return None when finished reading*

       """

       # This method will have to do different things depending 
       # on self.dType (for future other data file support ie. hdf5)

       import pydarn, datetime as dt

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
           if dfile == None or dt.datetime.utcfromtimestamp(dfile['time']) > self.eTime:
               #if we dont have valid data, clean up, get out
               print '\nreached end of data'
               return None

           #check that we're in the time window
           if (dt.datetime.utcfromtimestamp(dfile['time']) >= self.sTime and \
               dt.datetime.utcfromtimestamp(dfile['time']) <= self.eTime):
               return dfile

    def close(self):
        """
           Close the associated file.
        """
        import os
        if self.__ptr is not None:
            self.__ptr.close()
            self.__fd=None



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
  eTime=datetime.datetime(2012,11,1,4,0)
  expected_filename="20121101.000000.20121101.040000.fhe.fitacf"
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
  print "  DAVIT_REMOTE_TIMEINC:", os.environ['DAVIT_REMOTE_TIMEINC']
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
  print "  DAVIT_LOCAL_TIMEINC:", os.environ['DAVIT_LOCAL_TIMEINC']
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

