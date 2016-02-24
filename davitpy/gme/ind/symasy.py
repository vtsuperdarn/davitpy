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
"""symasy module

A module for reading, writing, and storing symasy Data

Classes
---------------------------------
symAsyRec   a SYM/ASY data record
---------------------------------

Functions
---------------------------------------------------------------
readSymAsy      read sym/asy data from database
readSymAsyWeb   read sym/asy data from website
mapSymAsyMongo  read sym/asy from website and store to database
---------------------------------------------------------------

Module author: AJ, 20130131

"""
from davitpy.gme.base.gmeBase import gmeData
import logging

class symAsyRec(gmeData):
    """a class to represent a record of sym/asy data.  Extends class
    gme.base.gmeBase.gmeData. Note that sym/asym data is available from 1980-present
    day (or whatever the latest WDC has uploaded is).  **The data are 1-minute
    values.**  More info on sym/asy can be found here:
    http://wdc.kugi.kyoto-u.ac.jp/aeasy/asy.pdf
        
    Parameters
    ----------
    webLine : Optional[str]
        an ASCII line from the datafile from WDC. if this is provided, the object
        is initialized from it.  default=None
    dbDict : Optional[dict]
        a dictionary read from the mongodb.  if this is provided, the object is
        initialized from it.  default = None

    Attributes
    ----------
    time : datetime
        an object identifying which time these data are for
    dataSet : str
        a string indicating the dataset this is from
    info : str
        information about where the data come from.  *Please be courteous and
        give credit to data providers when credit is due.*
    symh : float
        the symh value
    symd : float
        the symd value
    asyh : float
        the asyh value
    asyd : float
        the asyd value

    Methods
    -------
    parseWeb

    Notes
    -----
    If any of the members have a value of None, this means that
    they could not be read for that specific time
   
    Example
    -------
        emptySymAsyObj = gme.ind.symAsyRec()

    or

        myDstObj = symAsyRec(webLine=awebLine)

    written by AJ, 20130131

    """
    def parseWeb(self,line):
        """This method is used to convert a line of sym/asy data from
        the WDC to a symAsyRec object
        
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
        
        Belongs to class gme.ind.symasy.symAsyRec

        Example
        -------
            mysymAsyObj.parseWeb(webLine)
            
        written by AJ, 20130131

        """
        import datetime as dt
        cols = line.split()
        self.time = dt.datetime(int(cols[0][0:4]),int(cols[0][5:7]),int(cols[0][8:10]), \
                                                            int(cols[1][0:2]),int(cols[1][3:5]),int(cols[1][6:8]))
        if(float(cols[3]) != 99999.0): self.asyd = float(cols[3])
        if(float(cols[4]) != 99999.0): self.asyh = float(cols[4])
        if(float(cols[5]) != 99999.0): self.symd = float(cols[5])
        if(float(cols[6]) != 99999.0): self.symh = float(cols[6])

        
    def __init__(self, webLine=None, dbDict=None):
        #note about where data came from
        self.dataSet = 'Sym/Asy'
        self.time = None
        self.info = 'These data were downloaded from WDC For Geomagnetism, Kyoto.  *Please be courteous and give credit to data providers when credit is due.*'
        #the indices
        self.symh = None
        self.symd = None
        self.asyh = None
        self.asyd = None
        
        #if we're initializing from an object, do it!
        if(webLine != None): self.parseWeb(webLine)
        if(dbDict != None): self.parseDb(dbDict)

        
def readSymAsy(sTime=None,eTime=None,symh=None,symd=None,asyh=None,asyd=None):
    """This function reads sym/asy data from the mongodb.
    
    Parameters
    ----------
    sTime : Optional[datetime]
        the earliest time you want data for, default=None
    eTime : Optional[datetime]
        the latest time you want data for.  if this is None, end Time will
        be 1 day after sTime.  default = None
    symh : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with symh values in the range [a,b] will be
        returned.  default = None
    symd : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with symd values in the range [a,b] will be
        returned.  default = None
    asyh : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with asyh values in the range [a,b] will be
        returned.  default = None
    asyd : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with asyd values in the range [a,b] will be
        returned.  default = None

    Returns
    -------
    symList : list
        if data is found, a list of class gme.ind.symasy.symAsyRec objects
        matching the input parameters is returned.  If no data is found,
        None is returned.

    Example
    -------
        import datetime as dt
        symList = gme.ind.readSymAsy(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),symh=[5,50],asyd=[-10,0])
        
    written by AJ, 20130131

    """
    import datetime as dt
    import davitpy.pydarn.sdio.dbUtils as db
    
    #check all the inputs for validity
    assert(sTime == None or isinstance(sTime,dt.datetime)), \
        logging.error('sTime must be a datetime object')
    assert(eTime == None or isinstance(eTime,dt.datetime)), \
        logging.error('eTime must be either None or a datetime object')
    var = locals()
    for name in ['symh','symd','asyh','asyd']:
        assert(var[name] == None or (isinstance(var[name],list) and \
            isinstance(var[name][0],(int,float)) and isinstance(var[name][1],(int,float)))), \
            logging.error(name + ' must None or a list of 2 numbers')
            
    if(eTime == None and sTime != None): eTime = sTime+dt.timedelta(days=1)
    qryList = []
    #if arguments are provided, query for those
    if(sTime != None): qryList.append({'time':{'$gte':sTime}})
    if(eTime != None): qryList.append({'time':{'$lte':eTime}})
    var = locals()
    for name in ['symh','symd','asyh','asyd']:
        if(var[name] != None): 
            qryList.append({name:{'$gte':min(var[name])}})
            qryList.append({name:{'$lte':max(var[name])}})
            
    #construct the final query definition
    qryDict = {'$and': qryList}
    #connect to the database
    symData = db.getDataConn(dbName='gme',collName='symasy')
    
    #do the query
    if(qryList != []): qry = symData.find(qryDict)
    else: qry = symData.find()
    if(qry.count() > 0):
        symList = []
        for rec in qry.sort('time'):
            symList.append(symAsyRec(dbDict=rec))
        logging.info('\nreturning a list with' + len(symList) + 'records of sym/asy data')
        return symList
    #if we didn't find anything on the mongodb
    else:
        logging.info('\ncould not find requested data in the mongodb')
        return None


def readSymAsyWeb(sTime,eTime=None):
    """This function reads sym/asy data from the WDC kyoto website
    
    .. warning::
        You should not use this. Use the general function
        gme.ind.symasy.readSymAsy instead.
    
    Parameters
    ----------
    sTime : datetime
        the earliest time you want data for
    eTime : Optional[datetime]
        the latest time you want data for.  if this is None, eTime
        will be equal 1 day after sTime.  This must not be more
        than 366 days after sTime.  default = None

    Example
    -------
        import datetime as dt
        symList = gme.ind.readSymAsyWeb(dt.datetime(2011,1,1),eTime=dt.datetime(2011,1,5))
        
    written by AJ, 20130131

    """
    import datetime as dt
    import mechanize
    
    assert(isinstance(sTime,dt.datetime)), logging.error('sTime must be a datetime object')
    if(eTime == None): eTime = sTime+dt.timedelta(days=1)
    assert(isinstance(eTime,dt.datetime)), logging.error('eTime must be a datetime object')
    assert(eTime >= sTime), logging.error('eTime < eTime')
    delt = eTime-sTime
    assert(delt.days <= 366), logging.error('cant read more than 366 days')
    
    tens = (sTime.year)/10
    year = sTime.year-tens*10
    month = sTime.strftime("%m")
    dtens = sTime.day/10
    day = sTime.day-dtens*10
    htens = sTime.hour/10
    hour = sTime.hour-htens*10
    ddtens = delt.days/10
    dday = delt.days - ddtens*10
    br = mechanize.Browser()
    br.set_handle_robots(False)   # no robots
    br.set_handle_refresh(False)  # can sometimes hang without this
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.open('http://wdc.kugi.kyoto-u.ac.jp/aeasy/index.html')
    
    br.form = list(br.forms())[0]
    
    #fill out the fields
    br.form.find_control('Tens').value = [str(tens)]
    br.form.find_control('Year').value = [str(year)]
    br.form.find_control('Month').value = [str(month)]
    br.form.find_control('Day_Tens').value = [str(dtens)]
    br.form.find_control('Days').value = [str(day)]
    br.form.find_control('Hour_Tens').value = [str(htens)]
    br.form.find_control('Hour').value = [str(hour)]
    if(ddtens < 9): ddtens = '0'+str(ddtens)
    br.form.find_control('Dur_Day_Tens').value = [str(ddtens)]
    br.form.find_control('Dur_Day').value = [str(dday)]
    br.form.find_control('Output').value = ['ASY']
    br.form.find_control('Out format').value = ['IAGA2002']
    br.form.find_control('Email').value = "vt.sd.sw@gmail.com"
    
    response = br.submit()
    
    #get the data file
    lines = response.readlines()

    symList = []
    for l in lines:
        #check for headers
        if(l[0] == ' ' or l[0:4] == 'DATE'): continue
        cols=l.split()
        try: symList.append(symAsyRec(webLine=l))
        except Exception,e:
            logging.exception(e)
            logging.exception('problem initializing symAsy object')
        
    if(symList != []): return symList
    else: return None

def mapSymAsyMongo(sYear,eYear=None):
    """This function reads sym/asy data from wdc and puts it in mongodb
    
    .. warning::
        In general, nobody except the database admins will need to
        use this function
    
    Parameters
    ----------
    sYear : int
        the year to begin mapping data
    eYear : Optional[int]
        the end year for mapping data.  if this is None, eYear
        will be sYear

    Returns
    -------
    Nothing

    Example
    -------
        gme.ind.mapSymAsyMongo(2001)
        
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
                                dbAddress=rcParams['SDDB'],dbName='gme',collName='symasy')
    
    #set up all of the indices
    mongoData.ensure_index('time')
    mongoData.ensure_index('symh')
    mongoData.ensure_index('symd')
    mongoData.ensure_index('asyh')
    mongoData.ensure_index('asyd')
    
    for yr in range(sYear,eYear+1):
        #1 day at a time, to not fill up RAM
        templist = readSymAsyWeb(dt.datetime(yr,1,1),dt.datetime(yr,1,1)+dt.timedelta(days=366))
        if(templist == None): continue
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
                logging.debug('found one!!')
                dbDict = qry.next()
                temp = dbDict['_id']
                dbDict = tempRec
                dbDict['_id'] = temp
                mongoData.save(dbDict)
            else:
                logging.warning('strange, there is more than 1 Sym/Asy record for' + rec.time)
        del templist

