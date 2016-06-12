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

"""Dst module

A module for reading, writing, and storing dst Data

Classes
-------------------------
dstRec  a dst data record
-------------------------

Functions
---------------------------------------
readDst     read dst data from database
readDstWeb  read dst data from website
mapDstMongo store dst data to database
---------------------------------------

Moduleauthor:: AJ, 20130131

"""
from davitpy.gme.base.gmeBase import gmeData
import logging

class dstRec(gmeData):
    """a class to represent a record of dst data.  Extends class
    gme.base.gmeBase.gmeData. Note that Dst data is available from
    1980-present day (or whatever the latest WDC has uploaded is).  **The
    data are 1-hour values**.  Information about dst can be found here:
    http://wdc.kugi.kyoto-u.ac.jp/dstdir/dst2/onDstindex.html
        
    Parameters
    ----------
    webLine : Optional[str]
        an ASCII line from the datafile from WDC. if this is provided, the
        object is initialized from it.  default=None
    dbDict : Optional[dict]
        a dictionary read from the mongodb.  if this is provided, the
        object is initialized from it.  default = None

    Attributes
    ----------
    time : datetime
        an object identifying which time these data are for
    dataSet : str
        a string dicating the dataset this is from
    info : str
        information about where the data come from.  *Please be courteous
        and give credit to data providers when credit is due.*
    dst : float
        the actual dst value

    Notes
    -----
    If any of the members have a value of None, this means that they
    could not be read for that specific time
   
    In general, users will not need to worry about this.
        
    Methods
    -------
    parseWeb

    Example
    -------
        emptyDstObj = gme.ind.dstRec()

    or

        myDstObj = dstRec(webLine=awebLine)
        
    written by AJ, 20130131
    """
    

    def parseWeb(self,line):
        """This method is used to convert a line of dst data from the WDC to a dstRec object
        
        Parameters
        ----------
        line : str
            the ASCII line from the WDC data file

        Returns
        -------
        Nothing

        Notes
        -----
        In general, users will not need to worry about this.
        
        Belongs to class gme.ind.dst.dstRec
        
        Example
        -------
            myDstObj.parseWeb(webLine)
            
        written by AJ, 20130131

        """
        import datetime as dt
        cols = line.split()
        self.time = dt.datetime(int(cols[0][0:4]),int(cols[0][5:7]),int(cols[0][8:10]), \
                                                            int(cols[1][0:2]),int(cols[1][3:5]),int(cols[1][6:8]))
        if(float(cols[3]) != 99999.0): self.dst = float(cols[3])
        
    def __init__(self, webLine=None, dbDict=None):
        """the intialization fucntion for a :class:`gme.ind.dst.dstRec` object.  
        
        written by AJ, 20130131

        """
        #note about where data came from
        self.dataSet = 'Dst'
        self.time = None
        self.info = 'These data were downloaded from WDC For Geomagnetism, Kyoto.  *Please be courteous and give credit to data providers when credit is due.*'
        self.dst = None
        
        #if we're initializing from an object, do it!
        if(webLine != None): self.parseWeb(webLine)
        if(dbDict != None): self.parseDb(dbDict)
        
def readDst(sTime=None,eTime=None,dst=None):
    """This function reads dst data from the mongodb.
    
    Parameters
    ----------
    sTime : Optional[datetime]
        the earliest time you want data for, default=None
    eTime : Optional[datetime]
        the latest time you want data for.  if this is None, end Time will be
        1 day after sTime.  default = None
    dst : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with dst values in the range [a,b] will be
        returned.  default = None

    Returns
    -------
    dstList : list
        if data is found, a list of class gme.ind.dst.dstRec objects matching
        the input parameters is returned.  If no data is found, None is
        returned.

    Example
    -------
        import datetime as dt
        dstList = gme.ind.readDst(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),dst=[-50,50])
        
    written by AJ, 20130131

    """
    import datetime as dt
    import davitpy.pydarn.sdio.dbUtils as db
    
    #check all the inputs for validity
    assert(sTime == None or isinstance(sTime,dt.datetime)), logging.error(
        'sTime must be a datetime object')
    assert(eTime == None or isinstance(eTime,dt.datetime)), logging.error(
        'eTime must be either None or a datetime object')
    assert(dst == None or (isinstance(dst,list) and \
        isinstance(dst[0],(int,float)) and isinstance(dst[1],(int,float)))), \
        logging.error('dst must None or a list of 2 numbers')
        
    if(eTime == None and sTime != None): eTime = sTime+dt.timedelta(days=1)
    qryList = []
    #if arguments are provided, query for those
    if(sTime != None): qryList.append({'time':{'$gte':sTime}})
    if(eTime != None): qryList.append({'time':{'$lte':eTime}})
    if(dst != None): 
        qryList.append({'dst':{'$gte':min(dst)}})
        qryList.append({'dst':{'$lte':max(dst)}})
            
    #construct the final query definition
    qryDict = {'$and': qryList}
    #connect to the database
    dstData = db.getDataConn(dbName='gme',collName='dst')
    
    #do the query
    if(qryList != []): qry = dstData.find(qryDict)
    else: qry = dstData.find()
    if(qry.count() > 0):
        dstList = []
        for rec in qry.sort('time'):
            dstList.append(dstRec(dbDict=rec))
        logging.info('\nreturning a list with ' + str(len(dstList)) + ' records of dst data')
        return dstList
    #if we didn't find anything on the mongodb
    else:
        logging.info('\ncould not find requested data in the mongodb')
        return None

            
def readDstWeb(sTime,eTime=None):
    """This function reads dst data from the WDC kyoto website
    
    Parameters
    ----------
    sTime : datetime
        the earliest time you want data for
    eTime : Optional[datetime]
        the latest time you want data for.  if this is None, eTime will
        be equal to sTime.  default = None

    Notes
    -----
    You should not use this. Use the general function readDst instead.
    
    Example
    -------
        import datetime as dt
        dstList = gme.ind.readDstWeb(dt.datetime(2011,1,1,1,50),eTime=dt.datetime(2011,1,1,10,0))
        
    written by AJ, 20130131

    """
    import datetime as dt
    import mechanize
    
    assert(isinstance(sTime,dt.datetime)),logging.error('sTime must be a datetime object')
    if(eTime == None): eTime = sTime
    assert(isinstance(eTime,dt.datetime)),logging.error('eTime must be a datetime object')
    assert(eTime >= sTime), logging.error('eTime < eTime')
    
    sCent = sTime.year/100
    sTens = (sTime.year - sCent*100)/10
    sYear = sTime.year-sCent*100-sTens*10
    sMonth = sTime.strftime("%m")
    eCent = eTime.year/100
    eTens = (eTime.year - eCent*100)/10
    eYear = eTime.year-eCent*100-eTens*10
    eMonth = eTime.strftime("%m")
    
    br = mechanize.Browser()
    br.set_handle_robots(False)   # no robots
    br.set_handle_refresh(False)  # can sometimes hang without this
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.open('http://wdc.kugi.kyoto-u.ac.jp/dstae/index.html')
    
    br.form = list(br.forms())[0]
    
    #fill out the page fields
    br.form.find_control('SCent').value = [str(sCent)]
    br.form.find_control('STens').value = [str(sTens)]
    br.form.find_control('SYear').value = [str(sYear)]
    br.form.find_control('SMonth').value = [sMonth]
    br.form.find_control('ECent').value = [str(eCent)]
    br.form.find_control('ETens').value = [str(eTens)]
    br.form.find_control('EYear').value = [str(eYear)]
    br.form.find_control('EMonth').value = [eMonth]
    
    br.form.find_control('Output').value = ['DST']
    br.form.find_control('Out format').value = ['IAGA2002']
    br.form.find_control('Email').value = "vt.sd.sw@gmail.com"
    
    response = br.submit()
    
    #get the data
    lines = response.readlines()

    dstList = []
    for l in lines:
        #check for headers
        if(l[0] == ' ' or l[0:4] == 'DATE'): continue
        cols=l.split()
        try: dstList.append(dstRec(webLine=l))
        except Exception,e:
            logging.exception(e)
            logging.exception('problemm assigning initializing dst object')
        
    if(dstList != []): return dstList
    else: return None


def mapDstMongo(sYear,eYear=None):
    """This function reads dst data from wdc and puts it in mongodb
    
    Parameters
    ----------
    sYear : int
        the year to begin mapping data
    eYear : Optional[int]
        the end year for mapping data.  if this is None,
        eYear will be sYear

    Returns
    -------
    Nothing

    Notes
    -----
    In general, nobody except the database admins will need to use this function
    
    Example
    -------
        gme.ind.mapDstMongo(1997)
        
    written by AJ, 20130123

    """
    import davitpy.pydarn.sdio.dbUtils as db
    from davitpy import rcParams
    import datetime as dt
    
    #check inputs
    assert(isinstance(sYear,int)), logging.error('sYear must be int')
    if(eYear == None): eYear=sYear
    assert(isinstance(eYear,int)), logging.error('sYear must be None or int')
    assert(eYear >= sYear), logging.error('end year greater than start year')
    
    #get data connection
    mongoData = db.getDataConn(username=rcParams['DBWRITEUSER'],password=rcParams['DBWRITEPASS'],\
                                dbAddress=rcParams['SDDB'],dbName='gme',collName='dst')
    
    #set up all of the indices
    mongoData.ensure_index('time')
    mongoData.ensure_index('dst')
    
    for yr in range(sYear,eYear+1):
        #1 year at a time, to not fill up RAM
        templist = readDstWeb(dt.datetime(yr,1,1),dt.datetime(yr,12,31))
        for rec in templist:
            #check if a duplicate record exists
            qry = mongoData.find({'time':rec.time})
            logging.debug(rec.time)
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
                logging.warning('strange, there is more than 1 DST record for ' + rec.time)
        del templist
