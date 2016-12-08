# -*- coding: utf-8 -*-
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
"""Kp module
   
A module for reading, writing, and storing kp Data

Classes
------------------------
kpDay   a day of Kp data
------------------------

Functions
-------------------------------------------------------
readKp      read/fetch Kp data from various sources
readKpFtp   read Kp data from ftp server
mapKpMongo  read data from server and store to database
-------------------------------------------------------

Module author:: AJ, 20130123

"""
from davitpy.gme.base.gmeBase import gmeData
import logging


class kpDay(gmeData):
    """a class to represent a day of kp data. Extends class gme.base.gmeBase.gmeData.
    Insight on the class members can be obtained from the NOAA FTP site:
    ftp://ftp.ngdc.noaa.gov/STP/GEOMAGNETIC_DATA/INDICES/KP_AP/kp_ap.fmt
    
    Parameters
    ---------- 
    ftpLine : Optional[str]
        an ASCII line from the FTP server, must be provided in conjunction with
        year.  if this is provided, the object is initialized from it.  default=None
    year : Optional[int]
        the year which the data are from.  this is needed because the FTP server
        uses only 2 digits for their year.  default=None
    dbDict : Optional[dict]
        a dictionary read from the mongodb.  if this is provided, the object is
        initialized from it.  default=None

    Attributes
    ----------
    time : datetime
        an object identifying which day these data are for
    kp : list
        a list of the 8 3-hour kp values fora single day.  The values are in string
        form, e.g. '3-', '7+', etc.
    kpSum : int
        the sum of the 8 3-hour kp averages
    ap : list
        a list of the 8 3-hour ap values fora single day.
    apMean : int
        the mean of the 8 3-hour ap averages
    sunspot : int
        the international sunspot number
    info : str
        information about where the data come from.  *Please be courteous and give
        credit to data providers when credit is due.*

    Notes
    -----
    If any of the members have a value of None, this means that they could not be read for that specific date
   
    Methods
    -------
    parseDb
    toDbDict
    parseFtp

    Example
    -------
        emptyKpObj = gme.ind.kpDay()

    or

        myKpDayObj = kpDay(ftpLine=aftpLine,year=2009)
        
    written by AJ, 20130123

    """
    def parseFtp(self,line,yr):
        """This method is used to convert a line of kp data read from the GFZ-Potsdam
        FTP site into a :class:`kpDay` object.  In general, users will not need
        to worry about this.
        
        Parameters
        ----------
        line : str
            the ASCII line from the FTP server
        yr : int
            the year which the data are from.  this is needed because the FTP server
            uses only 2 digits for their year.  y2k much?

        Returns
        -------
        Nothing.

        Notes
        -----
        Belongs to class gme.ind.kp.kpDay
        
        Example
        -------
            myKpDayObj.parseFtp(ftpLine,2009)
            
        written by AJ, 20130123

        """
        import datetime as dt
        
        self.time = dt.datetime(yr,int(line[2:4]),int(line[4:6]))
        for i in range(8):
            #store the kp vals
            num = line[12+i*2:12+i*2+1]
            mod = line[13+i*2:13+i*2+1]
            if(num == ' '): num = '0'
            if(mod == '0'): self.kp.append(num)
            elif(mod == '7'): self.kp.append(str(int(num)+1)+'-')
            elif(mod == '3'): self.kp.append(num+'+')
            else: self.kp.append('?')
            #store the ap vals
            self.ap.append(int(line[31+i*3:31+i*3+3]))
        try: self.kpSum = int(line[28:31])
        except: logging.exception('problem assigning kpSum')
        try: self.apMean = int(line[55:58])
        except: logging.exception('problem assigning apMean')
        try: self.sunspot = int(line[62:65])
        except: logging.exception('problem assigning sunspot')

        
    def __init__(self, ftpLine=None, year=None, dbDict=None):
        """the intialization fucntion for a :class:`gme.ind.kp.kpDay` object.  In general, users will not need to worry about this.
            
        written by AJ, 20130123

        """
        #initialize the data
        #note about where data came from
        self.info = 'These data were downloaded from the GFZ-Potsdam.  *Please be courteous and give credit to data providers when credit is due.*'
        self.kp = []
        self.ap = []
        self.time = None
        self.kpSum = None
        self.apMean = None
        self.sunspot = None
        
        if(ftpLine != None and year != None): self.parseFtp(ftpLine,year)
        
        if(dbDict != None): self.parseDb(dbDict)


    def __repr__(self):
        import datetime as dt
        myStr = 'Kp record FROM: '+str(self.time)+'\n'
        for key,var in self.__dict__.iteritems():
            myStr += key+' = '+str(var)+'\n'
        return myStr

        
def readKp(sTime=None,eTime=None,kpMin=None,apMin=None,kpSum=None,apMean=None,sunspot=None):
    """This function reads kp data.  First, it will try to get it from the mongodb,
    and if it can't find it, it will look on the GFZ ftp server using 
    gme.ind.kp.readKpFtp
    
    Parameters
    ----------
    sTime : Optional[datetime]
        the earliest time you want data for.  if this is None, start time will
        be the earliest record found.  default=None
    eTime : Optional[datetime]
        the latest time you want data for.  if this is None, end Time will be
        latest record found.  default=None
    kpMin : Optional[int]
        specify this to only return data from dates with a 3-hour kp value of
        minimum kpMin.  if this is none, it will be ignored.  default=None
    apMin : Optional[int]
        specify this to only return data from dates with a 3-hour ap value of
        minimum apMin.  if this is none, it will be ignored.  default=None
    kpSum : Optional[list]
        this must be a 2 element list of integers.  if this is specified,
        only dates with kpSum values in the range [a,b] will be returned.  if
        this is None, it will be ignored.  default=None
    apMean : Optional[list]
        this must be a 2 element list of integers.  if this is specified, only
        dates with apMean values in the range [a,b] will be returned.  if this
        is None, it will be ignored.  default=None
    sunspot : Optionl[list]
        this must be a 2 element list of integers.  if this is specified, only
        dates with sunspot values in the range [a,b] will be returned.  if
        this is None, it will be ignored.  default=None

    Returns
    -------
    kpList : list
        if data is found, a list of class gme.ind.kp.kpDay objects matching
        the input parameters is returned.  If not data is found, None is
        returned.

    Example
    -------
        import datetime as dt
        kpList = gme.ind.readKp(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),kpMin=2,apMin=1,kpSum=[0,10],apMean=[0,50],sunspot=[6,100])
        
    written by AJ, 20130123

    """
    import datetime as dt
    import davitpy.pydarn.sdio.dbUtils as db
    
    #check all the inputs for validity
    assert(sTime == None or isinstance(sTime,dt.datetime)), \
        logging.error('sTime must be either None or a datetime object')
    assert(eTime == None or isinstance(eTime,dt.datetime)), \
        logging.error('eTime must be either None or a datetime object')
    assert(kpMin == None or isinstance(kpMin,int)), \
        logging.error('kpMin must be either None or an int')
    assert(apMin == None or isinstance(apMin,int)), \
        logging.error('apMin must be either None or an int')
    assert(kpSum == None or (isinstance(kpSum,list) and len(kpSum) == 2 and \
        isinstance(kpSum[0], int) and isinstance(kpSum[1], int))), \
        logging.error('kpSum must be either None or a 2 element list')
    assert(apMean == None or (isinstance(apMean,list) and len(apMean) == 2and \
        isinstance(apMean[0], int) and isinstance(apMean[1], int))), \
        logging.error('apMean must be either None or a 2 element list')
    assert(sunspot == None or (isinstance(sunspot,list) and len(sunspot) == 2and \
        isinstance(sunspot[0], int) and isinstance(sunspot[1], int))), \
        logging.error('sunspot must be either None or a 2 element list')
    
    qryList = []
    #if arguments are provided, query for those
    if(sTime != None): qryList.append({'time':{'$gte':sTime}})
    if(eTime != None): qryList.append({'time':{'$lte':eTime}})
    if(kpMin != None): qryList.append({'kp':{'$gte':kpMin}})
    if(apMin != None): qryList.append({'ap':{'$gte':kpMin}})
    if(kpSum != None): qryList.append({'kpSum':{'$gte':min(kpSum)}})
    if(kpSum != None): qryList.append({'kpSum':{'$lte':max(kpSum)}})
    if(apMean != None): qryList.append({'apMean':{'$gte':min(apMean)}})
    if(apMean != None): qryList.append({'apMean':{'$lte':max(apMean)}})
    if(sunspot != None): qryList.append({'sunspot':{'$gte':min(sunspot)}})
    if(sunspot != None): qryList.append({'sunspot':{'$lte':max(sunspot)}})
    
    #construct the final query definition
    qryDict = {'$and': qryList}
    
    #connect to the database
    kpData = db.getDataConn(dbName='gme',collName='kp')
    
    #do the query
    if(qryList != []): qry = kpData.find(qryDict)
    else: qry = kpData.find()
    if(qry.count() > 0):
        kpList = []
        for rec in qry.sort('time'):
            kpList.append(kpDay(dbDict=rec))
        logging.info('\nreturning a list with',len(kpList),'days of kp data')
        return kpList
    #if we didn't find anything ont he mongodb
    else:
        logging.warning('\ncould not find requested data in the mongodb')
        logging.warning('we will look on the ftp server, but your conditions will be (mostly) ignored')
        
        if(sTime == None):
            logging.info('start time for search set to 1980...')
            sTime = dt.datetime(1980,1,1)
        
        kpList = []
        if(eTime == None): eTime = dt.now()
        for yr in range(sTime.year,eTime.year+1):
            tmpList = readKpFtp(dt.datetime(yr,1,1), eTime=dt.datetime(yr,12,31))
            if(tmpList == None): continue
            for x in tmpList:
                kpList.append(x)
                
        if(kpList != []):
            logging.info('\nreturning a list with ' + str(len(kpList)) + ' days of kp data')
            return kpList
        else:
            logging.info('\n no data found on FTP server, returning None...')
            return None
    
def readKpFtp(sTime, eTime=None):
    """This function reads kp data from the GFZ Potsdam FTP server via anonymous
    FTP connection.  This cannot read across year boundaries.
    
    Parameters
    ----------
    sTime : datetime
        the earliest time you want data for
    eTime : Optional[datetime]
        the latest time you want data for.  if this is None, eTime will be the
        end of the year of sTime.  default=None

    Returns
    -------
    kpList : list
        if data is found, a list of class gme.ind.kp.kpDay objects matching the
        input parameters is returned.  If not data is found, None is returned.
        default=None

    Notes
    -----
    You should not be using this function.  use readKp instead.

    Example
    -------
        import datetime as dt
        kpList = gme.ind.readKpFtp(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1))
            
    written by AJ, 20130123

    """
    from ftplib import FTP
    import datetime as dt
    
    sTime.replace(hour=0,minute=0,second=0,microsecond=0)
    if(eTime == None): eTime=sTime
    assert(eTime >= sTime), logging.error('end time greater than start time')
    if(eTime.year > sTime.year):
        logging.warning('you asked to read across a year bound')
        logging.warning("we can't do this, so we will read until the end of the year")
        eTime = dt.datetime(sTime.year,12,31)
        logging.warning('eTime = ' + eTime)
    eTime.replace(hour=0,minute=0,second=0,microsecond=0)
    
    #connect to the server
    try: ftp = FTP('ftp.gfz-potsdam.de')
    except Exception,e:
        logging.exception(e)
        logging.exception('problem connecting to GFZ-Potsdam server')
        
    #login as anonymous
    try: l=ftp.login()
    except Exception,e:
        logging.exception(e)
        logging.exception('problem logging in to GFZ-potsdam server')
    
    #go to the kp directory
    try: ftp.cwd('/pub/home/obs/kp-ap/wdc')
    except Exception,e:
        logging.exception(e)
        logging.exception('error getting to data directory')
    
    #list to hold the lines
    lines = []
    #get the data
    logging.debug('RETR kp' + str(sTime.year) + '.wdc')
    try:    ftp.retrlines('RETR kp'+str(sTime.year)+'.wdc',lines.append)
    except Exception,e:
        logging.exception(e)
        logging.exception('couldnt retrieve kp file')
    
    #convert the ascii lines into a list of kpDay objects
    myKp = []
    if(len(lines) > 0):
        for l in lines:
            if(sTime <= dt.datetime(sTime.year,int(l[2:4]),int(l[4:6])) <= eTime):
                myKp.append(kpDay(ftpLine=l,year=sTime.year))
            
        return myKp
    else:
        return None

    
def mapKpMongo(sYear,eYear=None):
    """This function reads kp data from the GFZ Potsdam FTP server via anonymous FTP
    connection and maps it to the mongodb.  
    
    Parameters
    ----------
    sYear : int
        the year to begin mapping data
    eYear : Optional[int]
        the end year for mapping data.  if this is None, eYear will
        be sYear.  default=None

    Returns
    -------
    Nothing.

    Notes
    -----
    In general, nobody except the database admins will need to use this function
    
    Example
    -------
        gme.ind.mapKpMongo(1985,eTime=1986)
        
    written by AJ, 20130123

    """
    import davitpy.pydarn.sdio.dbUtils as db
    from davitpy import rcParams
    import datetime as dt
    
    if(eYear == None): eYear=sYear
    assert(eYear >= sYear), logging.error('end year greater than start year')
    
    mongoData = db.getDataConn(username=rcParams['DBWRITEUSER'],password=rcParams['DBWRITEPASS'],\
                                dbAddress=rcParams['SDDB'],dbName='gme',collName='kp')
    
    #set up all of the indices
    mongoData.ensure_index('time')
    mongoData.ensure_index('kp')
    mongoData.ensure_index('ap')
    mongoData.ensure_index('kpSum')
    mongoData.ensure_index('apMean')
    mongoData.ensure_index('sunspot')
    
    #read the kp data from the FTP server
    datalist = []
    for yr in range(sYear,eYear+1):
        templist = readKpFtp(dt.datetime(yr,1,1), dt.datetime(yr+1,1,1))
        if(templist == None): continue
        for rec in templist:
            #check if a duplicate record exists
            qry = mongoData.find({'time':rec.time})
            tempRec = rec.toDbDict()
            cnt = qry.count()
            #if this is a new record, insert it
            if(cnt == 0): mongoData.insert(tempRec)
            #if this is an existing record, update it
            elif(cnt == 1):
                logging.debug('foundone!!')
                dbDict = qry.next()
                temp = dbDict['_id']
                dbDict = tempRec
                dbDict['_id'] = temp
                mongoData.save(dbDict)
            else:
                logging.warning('strange, there is more than 1 record for' + rec.time)
