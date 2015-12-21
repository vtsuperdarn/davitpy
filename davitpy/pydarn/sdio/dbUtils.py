"""
.. module:: dbUtils
   :synopsis: the classes needed for manipulating the mongodb
   
.. moduleauthor:: AJ, 20130108
*********************
**Module**: pydarn.sdio.dbUtils
*********************
**Functions**:
  * :func:`getServerConn`
  * :func:`getDbConn`
  * :func:`getDataConn`
  * :func:`updateDbDict`
  * :func:`readFromDb`
  * :func:`mapDbFit`
"""

import davitpy
from pymongo import MongoClient
from davitpy.pydarn.sdio import *
from davitpy.pydarn.sdio.radDataTypes import *
import datetime, os


def getServerConn(username=davitpy.rcParams['SDBREADUSER'],
                  password=davitpy.rcParams['SDBREADPASS'],
                  dbAddress=davitpy.rcParams['SDDB']):
  """
  **PACKAGE**: pydarn.sdio.dbUtils
  **FUNCTION**: getServerConn([username],[password])
  **PURPOSE**: gets a connection to the mongodb server.  This is the
    most basic connection.  In order to actually access data, this
    connection must be used to get a database connection which can
    in turn be used to get a data connection.

  **NOTE**: mongodb hierarchy goes SERVER->DATABASE->COLLECTION

  **INPUTS**:
    **[username]**: the username to connect with.  
     default is the read-only user defined in davitpyrc
    **[password]**: the password corresponding to the user username.
     default is defined in davitpyrc
    **[dbAddress]**: the address of the database to be accessed,
     eg sd-work9.ece.vt.edu:27017.  Default is defined in davitpyrc

  **OUTPUTS**:
    **sConn**: a connection to the mongodb server
 
  **EXAMPLES**:
    sConn = getServerConn(username='auser',password='apass',\
                         dbAddress='sd-work9.ece.vt.edu:27017')
   
  Written by AJ 20130108
  """
  
  #get a server connection
  try:
    sConn = MongoClient('mongodb://'+username+':'+password+'@'+dbAddress)
  #check for error
  except Exception,e:
    print e
    print 'problem getting connection to server',dbAddress
    sConn = None
    
  #return connection for good, none for bad
  return sConn
  
def getDbConn(username=davitpy.rcParams['SDBREADUSER'],
              password=davitpy.rcParams['SDBREADPASS'],
              dbAddress=davitpy.rcParams['SDDB'], dbName='radData'):
  """
  **PACKAGE**: pydarn.sdio.dbUtils
  **FUNCTION**: getDbConn([username],[password],[dbAddress],[dbName])
  **PURPOSE**: gets a connection to the database 'dbname'. on the
    mongodb server This is the middle-tier connection.  In order 
    to actually access data, this connection must be used to get 
    a data connection.
 
  **NOTE**: mongodb hierarchy goes SERVER->DATABASE->COLLECTION
 
  **INPUTS**:
    **[username]**: the username to connect with.  
      default is the read-only user defined in davitpyrc
    **[password]**: the password corresponding to the user username.
      default is defined in davitpyrc
    **[dbAddress]**: the address of the database to be accessed,
      eg sd-work9.ece.vt.edu:27017.  Default is defined in davitpyrc
    **[dbName]**: the name of the database to connect to.
      default is 'radData', where fit data is stored
 
  **OUTPUTS**:
    **dbConn**: a connection to the database
  
  **EXAMPLES**:
    dbConn = getDbConn(username='auser',password='apass',\
                        dbAddress='sd-work9.ece.vt.edu:27017',dbname='aDb')
    
  Written by AJ 20130108
  """
  
  #get a connection to the server
  sConn = getServerConn(username=username,password=password,dbAddress=dbAddress)
  #if we have a good server connection
  if(sConn != None):
    #connect to the database
    try: dbConn = getattr(sConn, dbName)
    #if we didn't get a database connection
    except:
      print 'error connecting to database ',dbName
      dbConn = None
    #return connection for good, None for bad
    return dbConn
  #if we didn't get a server connection
  else: return None
    
  
def getDataConn(username=davitpy.rcParams['SDBREADUSER'],
                password=davitpy.rcParams['SDBREADPASS'],
                dbAddress=davitpy.rcParams['SDDB'], dbName='radData',
                collName='beams'):
  """
  **PACKAGE**: pydarn.sdio.dbUtils
  **FUNCTION**: getDataConn([username],[password],[dbAddress],[dbName],[collName])
  **PURPOSE**: gets a connection to the collection collName on the
    mongodb server. This is the highetst level connection
 
  **NOTE**: mongodb hierarchy goes SERVER->DATABASE->COLLECTION
 
  **INPUTS**:
    **[username]**: the username to connect with.  
      default is the read-only user defined in .bashrc
    **[password]**: the password corresponding to the user username.
      default is defined in .bashrc
    **[dbAddress]**: the address of the database to be accessed,
      eg sd-work9.ece.vt.edu:27017.  Default is defined in .bashrc
    **[dbName]**: the name of the database to connect to.
      default is 'radData', where fit data is stored
    **[collName]**: the name of the collection to connect to.
      default is 'beams', where beam sounding data is stored
 
  **OUTPUTS**:
    **dataConn**: a connection to the database
  
  **EXAMPLES**:
    dataConn = getDbConn(username='auser',password='apass',\
                        dbAddress='sd-work9.ece.vt.edu:27017',\
                        dbName='aDb',collName='acoll')
    
  Written by AJ 20130108
  """
  
  #get a connection to the database
  dbConn = getDbConn(username=username,password=password,dbAddress=dbAddress,dbName=dbName)
  if(dbConn != None):
    #get the collection collName
    try: dataConn = getattr(dbConn, collName)
    except: 
      print 'error getting connection to collection ',collName
      dataConn = None
    return dataConn
  #return None if we didnt get a db connection
  else: return None
  
def updateDbDict(dbDict,dmapDict):
  """
| **PACKAGE**: pydarn.sdio.dbUtils
| **FUNCTION**: updateDbDict(dbDict,dmapDict)
| **PURPOSE**: updates a mongodb dictionary with data
|   from a dmap dictionary
|
| **INPUTS**:
|   **dbDict**: the dictionary for mongodb use
|   **dmapDict**: the dictionary read from the dmap file
|
| **OUTPUTS**:
|   **dbDict**: a n updated dictionary for use int he mongodb database
| 
| **EXAMPLES**:
|   newDbDict = updateDbDict(oldDbDict,dmapDict)
|   
| Written by AJ 20130108
  """
  #iterate through the items in the db dict
  for key,val in dbDict.iteritems():
    #pass over the mongodb _id param
    if(key == '_id'): continue
    #check if the dmap dict has a corresponding key
    if(dmapDict.has_key(cipher[key])):
      #check for a valid different value
      if(val != dmapDict[cipher[key]] and dmapDict[cipher[key]] != None):
        #update the db dictionary value with the new value
        try:
          dbDict[key] = dmapDict[cipher[key]]
        except:
          print 'problem changing value'
  #return the updated dictionary
  return dbDict
  
  
def readFromDb(sTime=None, eTime=None, stid=None, channel=None, bmnum=None, cp=None, fileType='fitex',exactFlg=False):
  """
| **PACKAGE**: pydarn.sdio.dbUtils
| **FUNCTION**: readFromDb([sTime],[eTime],[stid],[channel],[bmnum],[cp],\
|                           [fileType],[exactFlg])
| **PURPOSE**: read some record(s) from the mongodb database
|
| **NOTE**:  I recommend making your query as specific as possible, as this
|   will speed up the read speeds.  The biggest limiting factor is network speed,
|   so be specific.  For even higher performance, consider writing your own
|   mongodb queries
|
| **INPUTS**:
|   **[sTime]**: a datetime object with the time to start reading.
|     if this is None, sTime is defined as 00:00 UT on 1 Jan 2011.
|     default: None
|   **[eTime]**: a datetime object specifying the last record to read.
|     if this is none, the first record after sTime (within 24 hours,
|     provided it exists) will be read.  defualt = None
|   **[stid]**: the station id of the radar we want data for.  if this is
|     None, all available radars will be read.  default = None
|   **[channel]**: the channel letter for which to read data.  if this
|     is None, data from all channels will be read.  default = None
|   **[bmnum]**: the beam number for which to read data.  if this is None,
|     data from all beams will be read.  default = None
|   **[cp]**: the control program for which to read data.  if this is None,
|     data from all control programs will be read.  default = None
|   **[fileType]**: the filetype for which to read data.  valid inputs are:
|     'fitex' [default], 'fitacf', 'lmfit', 'rawacf', 'iqdat'.  if a fit file 
|     type is specified but data is not found, the program will search for another
|     fit type.
|   **[exactFlg]**: a flag to indicate the we only want a record with EXACTLY
|     the params specified (including time, to the ms).  this is useful for
|     updating records.  default = False
|
| **OUTPUTS**:
|   **myData**: a list of pydarn.sdio.beamData objects in chronological order
| 
| **EXAMPLES**:
    >>> myData = readFromDb(sTime=atime,stid=33,channel=None,bmnum=7,cp=153,fileType='fitacf',exactFlg=True)
|   
| Written by AJ 20130108
  """
  import datetime as dt
  import operator

  t = dt.datetime.now()
  
  #a list which will contain our query criteria
  qryList = []
  singFlg = False

  #if a start time is not provided, use a default
  if(sTime == None): sTime = dt.datetime(2011,1,1)
  
  #if we want only a single exact time (useful for filling/updating database)
  if(exactFlg): qryList.append({"time": sTime})
  #otherwise query for a time range
  else:
    #if endtime is not provided, use a 24-hour window
    if(eTime == None): 
      eTime = sTime+dt.timedelta(hours=24)
      singFlg = True
    #query for time later than start time and less than end time
    qryList.append({cipher["time"]: {"$lte": eTime}})
    qryList.append({cipher["time"]: {"$gte": sTime}})
    
  #if other arguments are provided, query for those
  if(stid != None): qryList.append({cipher["stid"]: stid})
  if(channel != None): qryList.append({cipher["channel"]: channel})
  if(bmnum != None): qryList.append({cipher["bmnum"]: bmnum})
  if(cp != None): qryList.append({cipher["cp"]: cp})
  
  #get a data connection for the mongodb database
  beams = getDataConn()
  
  #some arrays for dealing with data types
  if(fileType == 'fitex'): flg = 'exflg'
  elif(fileType == 'fitacf'): flg = 'acflg'
  elif(fileType == 'lmfit'): flg = 'lmflg'
  elif(fileType == 'rawacf'): flg = 'rawflg'
  elif(fileType == 'iqdat'): flg = 'iqflg'
  
  #append the current file type to the query
  qryList.append({cipher[flg]:1})
  #construct the final query definition
  qryDict = {'$and': qryList}
  
  #make a dictionary telling which data types NOT to get,
  #eg dont get rawacf, iqdat, fitacf, lmfit for fitex request
  exDict = {}
  for key,val in refArr.iteritems():
    if(key != flg): exDict[cipher[val]] = 0
    
  #do the actual query
  qry = beams.find(qryDict,exDict)
  #check if we have any results
  try:
    count = qry.count()
  except Exception,e:
    print e
    count = 0
  if(count > 0):
    return qry
  else:
    return None
    
def mapDbFit(dateStr, rad, time=[0,2400], fileType='fitex', vb=0):
  """put dmap data into the mongodb database
 
  **NOTE**: this is a write operation, so you must have DBWRITEUSER
    and DBWRITEPASS defined in your ~/.bashrc.  these can be obtained
    from the VT crew, as needed.  most people will not need this capability
 
  **Args**:
    * **dateStr**: the target date in 'yyymmdd' format
    * **rad**: the three letter radar code, e.g. 'bks'
    * **[time]**: the time range to perform the operation in REDUCED
      hhmm format, ie [28,652] instead of [0028,0652].  default = [0,2400]
    * **[fileType]**: the file type for which to perform the operation.
      valid inputs are 'fitex' [default], 'fitacf', 'lmfit', 'rawacf' , 'iqdat'
    * **[vb]**: a flag for verbose output.  default = 0
  **Returns**:
    * Nothing
  
  **Example**:
    ::

      mapDbFit('20110710', 'bks', time=[0,240], fileType='fitacf', vb=1):
    
  Written by AJ 20130108
  """
  from davitpy import utils
  import math
  
  #parse the dateStr into a datetime object
  myDate = utils.yyyymmddToDate(dateStr)
  #we need to get the start and end hours of the request
  #becasue of how the files are named
  hr1,hr2 = int(math.floor(time[0]/100./2.)*2),int(math.floor(time[1]/100./2.)*2)
  min1,min2 = int(time[0]-int(math.floor(time[0]/100.)*100)),int(time[1]-int(math.floor(time[1]/100.)*100))
  #move back a little in time because files often start at 2 mins
  #after the hour
  stime = myDate.replace(hour=hr1,minute=min1)
  stime = stime-datetime.timedelta(minutes=4)
  #endtime boundary condition
  if(hr2 == 24):
    etime = myDate+datetime.timedelta(days=1)
  else:
    etime = myDate.replace(hour=hr2,minute=min2)
    
  #open the dmap file
  myFile = radDataOpen(stime,rad,eTime=etime,fileType=fileType, src='local')
  if(myFile == None):
    print 'error, no data available for the requested time/radar/filetype combination'
    return None
  #read a record
  dmapBeam = radDataReadRec(myFile)
  if(dmapBeam == None):
    print 'error, no data available for the requested time/radar/filetype combination'
    return None
    
  #get a write connection to the db
  try:
    beams = getDataConn(davitpy.rcParams['DBWRITEUSER'],davitpy.rcParams['DBWRITEPASS'])
  except:
    print 'error connecting to database for writing'
    return None
  
  #ensure all necessary indices
  beams.ensure_index(cipher['time'])
  beams.ensure_index(cipher['bmnum'])
  beams.ensure_index(cipher['channel'])
  beams.ensure_index(cipher['stid'])
  beams.ensure_index(cipher['cp'])
  beams.ensure_index(cipher['exflg'])
  beams.ensure_index(cipher['acflg'])
  beams.ensure_index(cipher['lmflg'])
  beams.ensure_index(cipher['iqflg'])
  beams.ensure_index(cipher['rawflg'])
  
  #go until the end of file
  while(dmapBeam != None):
    #check that we're in the time window
    if(dmapBeam.time > etime): break
    if(dmapBeam.time <= etime):
      #check for verbose output
      if(vb): print dmapBeam.time,dmapBeam.stid
      del dmapBeam.fType
      del dmapBeam.fit
      del dmapBeam.rawacf.parent
      #convert the dmap dict to a db dictionary
      dmapDict = dmapBeam.toDbDict()
      
      #perform a query (search for already existent entry
      qry = beams.find({'$and':[{cipher["time"]: dmapBeam.time}, {cipher["bmnum"]: dmapBeam.bmnum}, \
                                {cipher["channel"]: dmapBeam.channel}, {cipher["stid"]: dmapBeam.stid}, \
                                {cipher["cp"]: dmapBeam.cp}]})
      #check for a new entry
      if(qry.count() == 0):
        #inster the data
        beams.insert(dmapDict)
      #if this beam sounding already exists
      else:
        #update the data
        dbDict = qry.next()
        dbDict = updateDbDict(dbDict,dmapDict)
        beams.save(dbDict)
    #read the next record from the dmap file
    dmapBeam = radDataReadRec(myFile)
    
  
  #close the dmap file
  myFile.close()
