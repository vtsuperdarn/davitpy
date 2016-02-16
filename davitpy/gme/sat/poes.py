# -*- coding: utf-8 -*-
# Copyright (C) 2014  VT SuperDARN Lab
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
"""poes module

A module for reading, writing, and storing poes data

Module Author:: AJ, 20130129

Classes
----------------------------
poesRec     poes data record
----------------------------

Functions
------------------------------------------
readPoes        reading poes data
readPoesFtp     get poes data via ftp
mapPoesMongo    populate database from ftp
overlayPoesTed  map poes ted data
------------------------------------------

"""
from davitpy.gme.base.gmeBase import gmeData
import logging

class poesRec(gmeData):
  """a class to represent a record of poes data.

  Extends class gmeBase.gmeData.  Insight on the class members can
  be obtained from the NOAA NGDC site
  <ftp://satdat.ngdc.noaa.gov/sem/poes/data/readme.txt>.  Note that
  Poes data is available from 1998-present day (or whatever the
  latest NOAA has uploaded is).  **The data are the 16-second
  averages**

  Parameters
  ----------
  ftpLine : Optional[str]
      an ASCII line from the FTP server. if this is provided, the
      object is initialized from it.  header must be provided in
      conjunction with this.  default=None
  header : Optional[str]
      the header from the ASCII FTP file.  default=None
  dbDict : Optional[dict]
      a dictionary read from the mongodb.  if this is provided,
      the object is initialized from it.  default = None
  satnum : Optional[int]
      the satellite nuber.  default=None

  Attributes
  ----------
  time : datetime
      an object identifying which time these data are for
  info : str
      information about where the data come from.  *Please be
      courteous and give credit to data providers when credit is due.*
  dataSet : str
      the name of the data set
  satnum : ind
      the noaa satellite number
  sslat : float
      Geographic Latitude of sub-satellite point, degrees
  sslon : float
      Geographic Longitude of sub-satellite point, degrees
  folat : float
      Geographic Latitude of foot-of-field-line, degrees
  folon : float
      Geographic Longitude of foot-of-field-line, degrees
  lval : float
      L-value
  mlt : float
      Magnetic local time of foot-of-field-line, degrees
  pas0 : float
      MEPED-0 pitch angle at satellite, degrees
  pas90 : float
      MEPED-90 pitch angle at satellite, degrees
  mep0e1 : float
      MEPED-0 > 30 keV electrons, counts/sec
  mep0e2 : float
      MEPED-0 > 100 keV electrons, counts/sec
  mep0e3 : float
      MEPED-0 > 300 keV electrons, counts/sec
  mep0p1 : float
      MEPED-0 30 keV to 80 keV protons, counts/sec
  mep0p2 : float
      MEPED-0 80 keV to 240 keV protons, counts/sec
  mep0p3 : float
      240 kev to 800 keV protons, counts/sec
  mep0p4 : float
      MEPED-0 800 keV to 2500 keV protons, counts/sec
  mep0p5 : float
      MEPED-0 2500 keV to 6900 keV protons, counts/sec
  mep0p6 : float
      MEPED-0 > 6900 keV protons, counts/sec,
  mep90e1 : float
      MEPED-90 > 30 keV electrons, counts/sec,
  mep90e2 : float
      MEPED-90 > 100 keV electrons, counts/sec
  mep90e3 : float
      MEPED-90 > 300 keV electrons, counts/sec
  mep90p1 : float
      MEPED-90 30 keV to 80 keV protons, counts/sec
  mep90p2 : float
      MEPED-90 80 keV to 240 keV protons, counts/sec
  mep90p3 : float
      MEPED-90 240 kev to 800 keV protons, counts/sec,
  mep90p4 : float
      MEPED-90 800 keV to 2500 keV protons, counts/sec
  mep90p5 : float
      MEPED-90 2500 keV to 6900 keV protons, counts/sec
  mep90p6 : float
      MEPED-90 > 6900 keV protons, counts/sec
  mepomp6 : float
      MEPED omni-directional > 16 MeV protons, counts/sec
  mepomp7 : float
      MEPED omni-directional > 36 Mev protons, counts/sec
  mepomp8 : float
      MEPED omni-directional > 70 MeV protons, counts/sec
  mepomp9 : float
      MEPED omni-directional >= 140 MeV protons
  ted : float
      TED, Total Energy Detector Average, ergs/cm2/sec
  echar : float
      TED characteristic energy of electrons, eV
  pchar : float
      TED characteristic energy of protons, eV
  econtr : float
      TED electron contribution, Electron Energy/Total Energy

  Notes
  -----
  If any of the members have a value of None, this means that they could not
  be read for that specific time

  Belongs to class omniRec

  Methods
  -------
  parseFtp

  Example
  -------
      emptyPoesObj = gme.sat.poesRec()

  or

      myPoesObj = poesRec(ftpLine=aftpLine)

    
  written by AJ, 20130131

  """

  def parseFtp(self,line, header):
    """This method is used to convert a line of poes data read from
    the NOAA NGDC FTP site into a :class:`poesRec` object.

    Parameters
    ----------
    line : str
        the ASCII line from the FTP server
    header :

    Returns
    -------
    Nothing.

    Notes
    -----
    In general, users will not need to worry about this.

    Belongs to class poesRec

    Example
    -------
        myPoesObj.parseFtp(ftpLine)

    written by AJ, 20130131

    """
    import datetime as dt
    
    #split the line into cols
    cols = line.split()
    head = header.split()
    self.time = dt.datetime(int(cols[0]), int(cols[1]), int(cols[2]), int(cols[3]),int(cols[4]), \
                            int(float(cols[5])),int(round((float(cols[5])-int(float(cols[5])))*1e6)))
    
    for key in self.__dict__.iterkeys():
      if(key == 'dataSet' or key == 'info' or key == 'satnum' or key == 'time'): continue
      try: ind = head.index(key)
      except Exception,e:
        logging.exception(e)
        logging.exception('problem setting attribute' + key)
      #check for a good value
      if(float(cols[ind]) != -999.): setattr(self,key,float(cols[ind]))

  
  def __init__(self, ftpLine=None, dbDict=None, satnum=None, header=None):
    """the intialization fucntion for a class omniRec object.  

    written by AJ, 20130131

    """
    # note about where data came from
    self.dataSet = 'Poes'
    self.info = 'These data were downloaded from NASA SPDF.  *Please be courteous and give credit to data providers when credit is due.*'
    self.satnum = satnum
    self.sslat = None
    self.sslon = None
    self.folat = None
    self.folon = None
    self.lval = None
    self.mlt = None
    self.pas0 = None
    self.pas90 = None
    self.mep0e1 = None
    self.mep0e2 = None
    self.mep0e3 = None
    self.mep0p1 = None
    self.mep0p2 = None
    self.mep0p3 = None
    self.mep0p4 = None
    self.mep0p5 = None
    self.mep0p6 = None
    self.mep90e1 = None
    self.mep90e2 = None
    self.mep90e3 = None
    self.mep90p1 = None
    self.mep90p2 = None
    self.mep90p3 = None
    self.mep90p4 = None
    self.mep90p5 = None
    self.mep90p6 = None
    self.mepomp6 = None
    self.mepomp7 = None
    self.mepomp8 = None
    self.mepomp9 = None
    self.ted = None
    self.echar = None
    self.pchar = None
    self.econtr = None
    
    #if we're initializing from an object, do it!
    if(ftpLine != None): self.parseFtp(ftpLine,header)
    if(dbDict != None): self.parseDb(dbDict)
    
def readPoes(sTime,eTime=None,satnum=None,folat=None,folon=None,ted=None,echar=None,pchar=None):
  """This function reads poes data.

  First, it will try to get it from the mongodb, and if it can't find it, it will
  look on the NOAA NGDC FTP server using :func:`readPoesFtp`.  The data are
  16-second averages

  Parameters
  ----------
  sTime : datetime or None
    the earliest time you want data for
  eTime : Optional[datetime or None]
    the latest time you want data for.  if this is None, end Time will be 1
    day after sTime.  default = None
  satnum : Optional[int]
    the satellite you want data for.  eg 17 for noaa17.  if this is None, data
    for all satellites will be returned.  default = None
  folat : Optional[list or None]
    if this is not None, it must be a 2-element list of numbers, [a,b].  In
    this case, only data with bx values in the range [a,b] will be returned.
    default = None
  folon : Optional[list or None]
    if this is not None, it must be a 2-element list of numbers, [a,b].  In
    this case, only data with bye values in the range [a,b] will be returned.
    default = None
  ted : Optional[list or None]
    if this is not None, it must be a 2-element list of numbers, [a,b].  In
    this case, only data with bze values in the range [a,b] will be returned.
    default = None
  echar : Optional[list or None]
    if this is not None, it must be a 2-element list of numbers, [a,b].  In
    this case, only data with bym values in the range [a,b] will be returned.
    default = None
  pchar : Optional[list or None]
    if this is not None, it must be a 2-element list of numbers, [a,b].  In
    this case, only data with bzm values in the range [a,b] will be returned.
    default = None
    
  Returns
  -------
  poesList : list or None
    if data is found, a list of class poesRec objects matching the input
    parameters is returned.  If no data is found, None is returned.

  Example
  -------
      import datetime as dt
      poesList = gme.sat.readPoes(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),folat=[60,80])
    
  written by AJ, 20130131

  """
  import datetime as dt
  import davitpy.pydarn.sdio.dbUtils as db

  # check all the inputs for validity
  assert(isinstance(sTime,dt.datetime)), logging.error(
    'sTime must be a datetime object')
  assert(eTime == None or isinstance(eTime,dt.datetime)), logging.error(
    'eTime must be either None or a datetime object')
  assert(satnum == None or isinstance(satnum,int)), logging.error('satnum must be an int')
  var = locals()
  for name in ['folat','folon','ted','echar','pchar']:
    assert(var[name] == None or (isinstance(var[name],list) and \
      isinstance(var[name][0],(int,float)) and \
      isinstance(var[name][1],(int,float)))), logging.error(
      name + ' must None or a list of 2 numbers')

  if(eTime == None): eTime = sTime+dt.timedelta(days=1)
  qryList = []
  # if arguments are provided, query for those
  qryList.append({'time':{'$gte':sTime}})
  if(eTime != None): qryList.append({'time':{'$lte':eTime}})
  if(satnum != None): qryList.append({'satnum':satnum})
  var = locals()
  for name in ['folat','folon','ted','echar','pchar']:
    if(var[name] != None): 
      qryList.append({name:{'$gte':min(var[name])}})
      qryList.append({name:{'$lte':max(var[name])}})

  # construct the final query definition
  qryDict = {'$and': qryList}
  # connect to the database
  poesData = db.getDataConn(dbName='gme',collName='poes')

  # do the query
  if(qryList != []): qry = poesData.find(qryDict)
  else: qry = poesData.find()
  if(qry.count() > 0):
    poesList = []
    for rec in qry.sort('time'):
      poesList.append(poesRec(dbDict=rec))
    logging.info('nreturning a list with '+ len(poesList) + ' records of poes data')
    return poesList
  # if we didn't find anything on the mongodb
  else:
    logging.info('could not find requested data in the mongodb')
    return None
    # print 'we will look on the ftp server, but your conditions will be (mostly) ignored'
    
    ## read from ftp server
    # poesList = readPoesFtp(sTime, eTime)
    
    # if(poesList != None):
      # print '\nreturning a list with',len(poesList),'recs of poes data'
      # return poesList
    # else:
      # print '\n no data found on FTP server, returning None...'
      # return None


def readPoesFtp(sTime,eTime=None):
  """This function reads poes data from the NOAA NGDC server via
     anonymous FTP connection.
  
  Parameters
  ----------
  sTime : datetime
    the earliest time you want data for
  eTime : Optional[datetime]
    the latest time you want data for.  if this is None, eTime will be equal
    1 day after sTime.  default = None

  Returns
  -------
  poesList : list or None
    if data is found, a list of :class:`poesRec` objects matching the input
    parameters is returned.  If no data is found, None is returned.

  Notes
  -----
  You should not use this. Use the general function :func:`readPoes` instead.

  Example
  -------
      import datetime as dt
      poesList = gme.sat.readpoesFtp(dt.datetime(2011,1,1,1,50),eTime=dt.datetime(2011,1,1,10,0))
    
  written by AJ, 20130128

  """
  from ftplib import FTP
  import datetime as dt

  assert(isinstance(sTime,dt.datetime)), logging.error(
    'sTime must be datetime')
  if(eTime == None): eTime=sTime+dt.timedelta(days=1)
  assert(isinstance(eTime,dt.datetime)), logging.error(
    'eTime must be datetime')
  assert(eTime >= sTime), logging.error(
    'end time greater than start time')

  # connect to the server
  try: ftp = FTP('satdat.ngdc.noaa.gov')  
  except Exception,e:
    logging.exception(e)
    logging.exception('problem connecting to NOAA server')
    return None

  # login as anonymous
  try: l=ftp.login()
  except Exception,e:
    logging.exception(e)
    logging.exception('problem logging in to NOAA server')
    return None

  myPoes = []
  # get the poes data
  myTime = dt.datetime(sTime.year,sTime.month,sTime.day)
  while(myTime <= eTime):
    # go to the data directory
    try: ftp.cwd('/sem/poes/data/avg/txt/'+str(myTime.year))
    except Exception,e:
      logging.exception(e)
      logging.exception('error getting to data directory')
      return None

    # list directory contents
    dirlist = ftp.nlst()
    for dire in dirlist:
      # check for satellite directory
      if(dire.find('noaa') == -1): continue
      satnum = dire.replace('noaa','')
      # chege to file directory
      ftp.cwd('/sem/poes/data/avg/txt/'+str(myTime.year)+'/'+dire)
      fname = 'poes_n'+satnum+'_'+myTime.strftime("%Y%m%d")+'.txt'
      logging.info('poes: RETR ' + fname)
      # list to hold the lines
      lines = []
      # get the data
      try: ftp.retrlines('RETR '+fname,lines.append)
      except Exception,e:
        logging.exception(e)
        logging.exception('error retrieving' + fname)

      # convert the ascii lines into a list of poesRec objects
      # skip first (header) line
      for line in lines[1:]:
        cols = line.split()
        t = dt.datetime(int(cols[0]), int(cols[1]), int(cols[2]), int(cols[3]),int(cols[4]))
        if(sTime <= t <= eTime):
          myPoes.append(poesRec(ftpLine=line,satnum=int(satnum),header=lines[0]))

    # increment myTime
    myTime += dt.timedelta(days=1)

  if(len(myPoes) > 0): return myPoes
  else: return None


def mapPoesMongo(sYear,eYear=None):
  """This function reads poes data from the NOAA NGDC FTP server via anonymous
  FTP connection and maps it to the mongodb.  

  Parameters
  ----------
  sYear : int
    the year to begin mapping data
  eYear : Optional[int or None]
    the end year for mapping data.  if this is None, eYear will be sYear

  Returns
  -------
  Nothing.

  Notes
  -----
  In general, nobody except the database admins will need to use this function
  
  Example
  -------
      gme.sat.mapPoesMongo(2004)
    
  written by AJ, 20130131

  """
  import davitpy.pydarn.sdio.dbUtils as db
  from davitpy import rcParams
  import datetime as dt

  # check inputs
  assert(isinstance(sYear,int)), logging.error('sYear must be int')
  if(eYear == None): eYear=sYear
  assert(isinstance(eYear,int)), logging.error('sYear must be None or int')
  assert(eYear >= sYear), logging.error('end year greater than start year')

  # get data connection
  mongoData = db.getDataConn(username=rcParams['DBWRITEUSER'],password=rcParams['DBWRITEPASS'],\
                dbAddress=rcParams['SDDB'],dbName='gme',collName='poes')

  # set up all of the indices
  mongoData.ensure_index('time')
  mongoData.ensure_index('satnum')
  mongoData.ensure_index('folat')
  mongoData.ensure_index('folon')
  mongoData.ensure_index('ted')
  mongoData.ensure_index('echar')
  mongoData.ensure_index('pchar')

  # read the poes data from the FTP server
  myTime = dt.datetime(sYear,1,1)
  while(myTime < dt.datetime(eYear+1,1,1)):
    # 10 day at a time, to not fill up RAM
    templist = readPoesFtp(myTime,myTime+dt.timedelta(days=10))
    if(templist == None): continue
    for rec in templist:
      # check if a duplicate record exists
      qry = mongoData.find({'$and':[{'time':rec.time},{'satnum':rec.satnum}]})
      print rec.time, rec.satnum
      tempRec = rec.toDbDict()
      cnt = qry.count()
      # if this is a new record, insert it
      if(cnt == 0): mongoData.insert(tempRec)
      # if this is an existing record, update it
      elif(cnt == 1):
        logging.debug('found one!!')
        dbDict = qry.next()
        temp = dbDict['_id']
        dbDict = tempRec
        dbDict['_id'] = temp
        mongoData.save(dbDict)
      else:
        logging.info('strange, there is more than 1 record for ' + rec.time)
    del templist
    myTime += dt.timedelta(days=10)


def overlayPoesTed( baseMapObj, axisHandle, startTime, endTime = None, coords = 'geo', \
                    hemi = 1, folat = [45., 90.], satNum = None, param='ted', scMin=-3.,scMax=0.5) :
  """This function overlays POES TED data onto a map object.

  Parameters
  ----------
  baseMapObj : datetime or None
    the map object you want data to be overlayed on.
  axisHandle : datetime or None
    the Axis Handle used.
  startTime : datetime or None
    the starttime you want data for. If endTime is not given overlays data from
    satellites with in +/- 45 min of the startTime
  endTime : Optional[datetime or None]
    the latest time you want data for.  if this is None, data from satellites
    with in +/- 45 min of the startTime is overlayed.  default = None
  satnum : Optional[int]
    the satellite you want data for.  eg 17 for noaa17.  if this is None, data
    for all satellites will be returned.  default = None
  coords : Optional[str]
    Coordinates of the map object on which you want data to be overlayed on,
    'geo', 'mag', 'mlt'. Default 'geo'
  hemi : Optional[list or None]
    Hemisphere of the map object on which you want data to be overlayed on.
    Value is 1 for northern hemisphere and -1 for the southern hemisphere. Default 1
  folat : Optional[list or None]
    if this is not None, it must be a 2-element list of numbers, [a,b].  In this
    case, only data with latitude values in the range [a,b] will be returned.  default = None
  param : Optional[str]
    the name of the poes parameter to be plotted.  default='ted'

  Returns
  -------
  btpltpoes :
    POES TED data is overlayed on the map object. If no data is found, None is returned.

  Example
  -------
      import datetime as dt
      poesList = gme.sat.overlayPoesTed(MapObj, sTime=dt.datetime(2011,3,4,4))

  written by Bharat Kunduri, 20130216

  """
  import utils
  import matplotlib as mp
  import datetime
  import numpy
  import matplotlib.pyplot as plt
  import gme.sat.poes as Poes
  import math
  import models
  import matplotlib.cm as cm
  from scipy import optimize  


  # check all the inputs for validity
  assert(isinstance(startTime,datetime.datetime)), logging.error(
    'sTime must be a datetime object')
  assert(endTime == None or isinstance(endTime,datetime.datetime)), \
    logging.error('eTime must be either None or a datetime object')

  var = locals()

  assert(var['satNum'] == None or (isinstance(var['satNum'],list) )), \
    logging.error('satNum must None or a list of satellite (integer) numbers')

  if satNum != None :
    assert( len(satNum) <= 5 ), \
    logging.error('there are only 5 POES satellites in operation (atleast when I wrote this code)')

  assert(var['folat'] == None or (isinstance(var['folat'],list) and \
    isinstance(var['folat'][0],(int,float)) and isinstance(var['folat'][1],(int,float)))), \
    logging.error('folat must None or a list of 2 numbers')

  # Check the hemisphere and get the appropriate folat
  folat = [ math.fabs( folat[0] ) * hemi, math.fabs( folat[1] ) * hemi ]

  # Check if the endTime is given in which case the user wants a specific time interval to search for
  # If not we'll give him the best available passes for the selected start time...
  if ( endTime != None ) :
    timeRange = numpy.array( [ startTime, endTime ] )
  else :
    timeRange = None

  pltTimeInterval = numpy.array( datetime.timedelta( minutes = 45 ) )

  # check if the timeRange is set... if not set the timeRange to +/- pltTimeInterval of the startTime
  if timeRange == None:
    timeRange = numpy.array( [ startTime - pltTimeInterval, startTime + pltTimeInterval ] )

  # SatNums - currently operational POES satellites are 15, 16, 17, 18, 19
  if satNum == None:
    satNum = [None]
  # If any particular satellite number is not chosen by user loop through all the available one's 

  satNum = numpy.array( satNum ) # I like numpy arrays better that's why I'm converting the satNum list to a numpy array

  latPoesAll = [[] for j in range(len(satNum))]
  lonPoesAll = [[] for j in range(len(satNum))]
  tedPoesAll = [[] for j in range(len(satNum))]
  timePoesAll = [[] for j in range(len(satNum))]
  lenDataAll = [[] for j in range(len(satNum))]

  goodFlg=False

  for sN in range(len(satNum)) :

    if(satNum[sN] != None):
      currPoesList = Poes.readPoes(timeRange[0], eTime = timeRange[1], satnum = int(satNum[sN]), folat = folat)
    else:
      currPoesList = Poes.readPoes(timeRange[0], eTime = timeRange[1], satnum = satNum[sN], folat = folat)

    # Check if the data is loaded...
    if currPoesList == None :
      logging.warning('No data found')
      continue
      #return None

    else:
      goodFlg=True
    # Loop through the list and store the data into arrays    
    lenDataAll.append(len(currPoesList))

    for l in currPoesList :
      # Store our data in arrays
      try:
        tedPoesAll[sN].append(math.log10(getattr(l,param)))
        if coords == 'mag' or coords == 'mlt':
          lat,lon,_ = models.aacgm.aacgmConv(l.folat,l.folon, 0., l.time.year, 0)
          latPoesAll[sN].append(lat)
          if coords == 'mag':
            lonPoesAll[sN].append(lon)
          else:
            lonPoesAll[sN].append(models.aacgm.mltFromEpoch(utils.timeUtils.datetimeToEpoch(l.time),lon)*360./24.)
        else:
          latPoesAll[sN].append(l.folat)
          lonPoesAll[sN].append(l.folon)

        timePoesAll[sN].append(l.time)
      except Exception,e:
        logging.exception(e)
        logging.exception('could not get parameter for time' + l.time)

  if(not goodFlg): return None

  latPoesAll = numpy.array( latPoesAll ) 
  lonPoesAll = numpy.array( lonPoesAll )
  tedPoesAll = numpy.array( tedPoesAll )
  timePoesAll = numpy.array( timePoesAll )
  lenDataAll = numpy.array( lenDataAll )

  poesTicks = [ -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5 ]

  # get the axis of the figure...
  ax = axisHandle

  for nn in range( len(satNum) ) :

    x, y = baseMapObj(lonPoesAll[nn], latPoesAll[nn])
    bpltpoes = baseMapObj.scatter(x,y,c=tedPoesAll[nn], vmin=scMin, vmax=scMax, alpha = 0.7, cmap=cm.jet, zorder = 7., edgecolor='none')
    timeCurr = timePoesAll[nn]
    for aa in range( len(latPoesAll[nn]) ) :
      if aa % 10 == 0:
        str_curr = str(timeCurr[aa].hour)+':'+str(timeCurr[aa].minute)
        ax.annotate( str_curr, xy =( x[aa], y[aa] ), size = 5, zorder = 6. )

  # cbar = plt.colorbar(bpltpoes, ticks = poesTicks, orientation='horizontal')
  # cbar.ax.set_xticklabels(poesTicks)
  # cbar.set_label(r"Total Log Energy Flux [ergs cm$^{-2}$ s$^{-1}$]")
  return bpltpoes


def overlayPoesBnd( baseMapObj, axisHandle, startTime, coords = 'geo', hemi = 1, equBnd = True, polBnd = False ) :
  """Overlay POES data

  This function reads POES TED data with in +/- 45min of the given time, fits the
  auroral oval boundaries and overlays them on a map object. The poleward
  boundary is not accurate all the times due to lesser number of satellite passes
  identifying it.

  Parameters
  ----------
  baseMapObj : datetime or None
    the map object you want data to be overlayed on.
  axisHandle : datetime or None
    the Axis Handle used.
  startTime : datetime or None
    the starttime you want data for. If endTime is not given overlays data from satellites with in +/- 45 min of the startTime
  coords : Optional[list or None]
    Coordinates of the map object on which you want data to be overlayed on. Default 'geo'
  hemi : Optional[list or None]
    Hemisphere of the map object on which you want data to be overlayed on. Value is 1 for northern hemisphere and -1 for the southern hemisphere.Default 1
  equBnd : Optional[list or None]
    If this is True the equatorward auroral oval boundary fit from the TED data is overlayed on the map object. Default True
  polBnd : Optional[list or None]
    If this is True the poleward auroral oval boundary fit from the TED data is overlayed on the map object. Default False
    
  Returns
  -------
  Nothing

  Example
  -------
      import datetime as dt
      poesList = gme.sat.overlayPoesTed(MapObj, sTime=dt.datetime(2011,3,4,4))

  written by Bharat Kunduri, 20130216

  """
  import utils
  import matplotlib as mp
  import datetime
  import numpy
  import matplotlib.pyplot as plt
  import gme.sat.poes as Poes
  import math
  import matplotlib.cm as cm
  from scipy import optimize
  import models

  # check all the inputs for validity
  assert(isinstance(startTime,datetime.datetime)), logging.error(
    'sTime must be a datetime object')

  # Check the hemisphere and get the appropriate folat
  folat = [ 45. * hemi, 90. * hemi ]

  # Get the time range we choose +/- 45 minutes....
  pltTimeInterval = numpy.array( datetime.timedelta( minutes = 45 ) )
  timeRange = numpy.array( [ startTime - pltTimeInterval, startTime + pltTimeInterval ] )

  satNum = [ 15, 16, 17, 18, 19 ]

  # We set the TED cut-off value to -0.75,
  # From observed cases this appeared to do well...
  # though fails sometimes especially during geomagnetically quiet times...
  # However this is version 1.0 and there always is room for improvement
  equBndCutoffVal = -0.75

  # If any particular satellite number is not chosen by user loop through all the available one's 
  satNum = numpy.array( satNum ) # I like numpy arrays better that's why I'm converting the satNum list to a numpy array

  latPoesAll = [[] for j in range(len(satNum))]
  lonPoesAll = [[] for j in range(len(satNum))]
  tedPoesAll = [[] for j in range(len(satNum))]
  timePoesAll = [[] for j in range(len(satNum))]
  lenDataAll = [[] for j in range(len(satNum))]

  for sN in range( len(satNum) ) :
    currPoesList = Poes.readPoes( timeRange[0], eTime = timeRange[1], satnum = int(satNum[sN]), folat = folat )

    # Check if the data is loaded...
    if currPoesList == None :
      logging.warning('No data found')
      continue

    # Loop through the list and store the data into arrays    
    lenDataAll.append( len( currPoesList ) )

    for l in range( lenDataAll[-1] ) :
      # Store our data in arrays if the TED data value is > than the cutoff value
      try:
        x = math.log10(currPoesList[l].ted)
      except:
       continue

      if x > equBndCutoffVal:
        if coords == 'mag' or coords == 'mlt':
          lat,lon,_ = models.aacgm.aacgmConv(currPoesList[l].folat,currPoesList[l].folon, 0., currPoesList[l].time.year, 0)
          latPoesAll[sN].append(lat)
          if coords == 'mag':
            lonPoesAll[sN].append(lon)
          else:
            lonPoesAll[sN].append(models.aacgm.mltFromEpoch(utils.timeUtils.datetimeToEpoch(currPoesList[l].time),lon)*360./24.)
        else:
          latPoesAll[sN].append(currPoesList[l].folat)
          lonPoesAll[sN].append(currPoesList[l].folon)

        # latPoesAll[sN].append( currPoesList[l].folat )
        # lonPoesAll[sN].append( currPoesList[l].folon )
        tedPoesAll[sN].append( math.log10(currPoesList[l].ted) )
        timePoesAll[sN].append( currPoesList[l].time )

  latPoesAll = numpy.array( latPoesAll ) 
  lonPoesAll = numpy.array( lonPoesAll )
  tedPoesAll = numpy.array( tedPoesAll )
  timePoesAll = numpy.array( timePoesAll )
  lenDataAll = numpy.array( lenDataAll )

  # Now to identify the boundaries...
  # Also need to check if the boundary is equatorward or poleward..
  # When satellite is moving from high-lat to low-lat decrease in flux would mean equatorward boundary
  # When satellite is moving from low-lat to high-lat increase in flux would mean equatorward boundary
  # that is what we are trying to check here

  eqBndLats = []
  eqBndLons = []
  poBndLats = []
  poBndLons = []    

  for n1 in range( len(satNum) ) :
    currSatLats = latPoesAll[n1]
    currSatLons = lonPoesAll[n1]
    currSatTeds = tedPoesAll[n1]

    testLatArrLtoh = []
    testLonArrLtoh = []
    testLatArrHtol = []
    testLonArrHtol = []

    testLatArrLtohP = []
    testLonArrLtohP = []
    testLatArrHtolP = []
    testLonArrHtolP = []

    for n2 in range( len(currSatLats)-1 ) :

      # Check if the satellite is moving form low-lat to high-lat or otherwise

      if ( math.fabs( currSatLats[n2] ) < math.fabs( currSatLats[n2+1] ) ) :

        if ( currSatTeds[n2] < currSatTeds[n2+1] ) :
          testLatArrLtoh.append( currSatLats[n2] )
          testLonArrLtoh.append( currSatLons[n2] )

        if ( currSatTeds[n2] > currSatTeds[n2+1] ) :
          testLatArrLtohP.append( currSatLats[n2] )
          testLonArrLtohP.append( currSatLons[n2] )

      if ( math.fabs( currSatLats[n2] ) > math.fabs( currSatLats[n2+1] ) ) :
        if ( currSatTeds[n2] > currSatTeds[n2+1] ) :
          testLatArrHtol.append( currSatLats[n2] )
          testLonArrHtol.append( currSatLons[n2] )

        if ( currSatTeds[n2] < currSatTeds[n2+1] ) :
          testLatArrHtolP.append( currSatLats[n2] )
          testLonArrHtolP.append( currSatLons[n2] )

    # I do this to find the index of the min lat...
    if ( testLatArrLtoh != [] ) :
      testLatArrLtoh = numpy.array( testLatArrLtoh )
      testLonArrLtoh = numpy.array( testLonArrLtoh )
      VarEqLat1 = testLatArrLtoh[ numpy.where( testLatArrLtoh == min(testLatArrLtoh) ) ]
      VarEqLon1 = testLonArrLtoh[ numpy.where( testLatArrLtoh == min(testLatArrLtoh) ) ]
      eqBndLats.append( VarEqLat1[0] )
      eqBndLons.append( VarEqLon1[0] )

    if ( testLatArrHtol != [] ) :
      testLatArrHtol = numpy.array( testLatArrHtol )
      testLonArrHtol = numpy.array( testLonArrHtol )
      VarEqLat2 = testLatArrHtol[ numpy.where( testLatArrHtol == min(testLatArrHtol) ) ]
      VarEqLon2 = testLonArrHtol[ numpy.where( testLatArrHtol == min(testLatArrHtol) ) ]
      eqBndLats.append( VarEqLat2[0] )
      eqBndLons.append( VarEqLon2[0] )

    if ( testLatArrLtohP != [] ) :
      testLatArrLtohP = numpy.array( testLatArrLtohP )
      testLonArrLtohP = numpy.array( testLonArrLtohP )
      VarEqLatP1 = testLatArrLtohP[ numpy.where( testLatArrLtohP == min(testLatArrLtohP) ) ]
      VarEqLonP1 = testLonArrLtohP[ numpy.where( testLatArrLtohP == min(testLatArrLtohP) ) ]
      if VarEqLatP1[0] > 64. :
        poBndLats.append( VarEqLatP1[0] )
        poBndLons.append( VarEqLonP1[0] )

    if ( testLatArrHtolP != [] ) :
      testLatArrHtolP = numpy.array( testLatArrHtolP )
      testLonArrHtolP = numpy.array( testLonArrHtolP )
      VarEqLatP2 = testLatArrHtolP[ numpy.where( testLatArrHtolP == min(testLatArrHtolP) ) ]
      VarEqLonP2 = testLonArrHtolP[ numpy.where( testLatArrHtolP == min(testLatArrHtolP) ) ]
      if VarEqLatP2[0] > 64 :
        poBndLats.append( VarEqLatP2[0] )
        poBndLons.append( VarEqLonP2[0] )

  eqBndLats = numpy.array( eqBndLats )
  eqBndLons = numpy.array( eqBndLons )
  poBndLats = numpy.array( poBndLats )
  poBndLons = numpy.array( poBndLons )

  # get the axis Handle used
  ax = axisHandle

  # Now we do the fitting part...
  fitfunc = lambda p, x: p[0] + p[1]*numpy.cos(2*math.pi*(x/360.)+p[2]) # Target function
  errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function

  # Initial guess for the parameters
  # Equatorward boundary
  p0Equ = [ 1., 1., 1.]
  p1Equ, successEqu = optimize.leastsq(errfunc, p0Equ[:], args=(eqBndLons, eqBndLats))  
  if polBnd == True :
    p0Pol = [ 1., 1., 1.]
    p1Pol, successPol = optimize.leastsq(errfunc, p0Pol[:], args=(poBndLons, poBndLats))   

  allPlotLons = numpy.linspace(0., 360., 25.)
  allPlotLons[-1] = 0.
  eqPlotLats = []
  if polBnd == True :
    poPlotLats = []
  for xx in allPlotLons :
    if equBnd == True :
      eqPlotLats.append( p1Equ[0] + p1Equ[1]*numpy.cos(2*math.pi*(xx/360.)+p1Equ[2] ) )
    if polBnd == True :
      poPlotLats.append( p1Pol[0] + p1Pol[1]*numpy.cos(2*math.pi*(xx/360.)+p1Pol[2] ) )

  xEqu, yEqu = baseMapObj(allPlotLons, eqPlotLats)
  bpltpoes = baseMapObj.plot( xEqu,yEqu, zorder = 7., color = 'b' )

  if polBnd == True :
    xPol, yPol = baseMapObj(allPlotLons, poPlotLats)
    bpltpoes = baseMapObj.plot( xPol,yPol, zorder = 7., color = 'r' )

