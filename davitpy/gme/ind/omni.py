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
"""OMNI module

A module for reading, writing, and storing OMNI data

Classes
--------------------------
omniRec a omni data record
--------------------------

Functions
------------------------------------------------------
readOmni        read/fetch omni data in various ways
readOmniFtp     read omni data from NASA server
mapOmniMongo    read omni data and store into database
------------------------------------------------------

Module author: AJ, 20130128

"""
from davitpy.gme.base.gmeBase import gmeData
import logging

class omniRec(gmeData):
    """a class to represent a record of omni data.  Extends class gmeBase.gmeData.
    Insight on the class members can be obtained from the NASA SPDF site:
    ftp://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/hroformat.txt.  Note that
    Omni data is available from 1995-present day (or whatever the latest NASA has
    uploaded is), in 1 and 5 minute resolution.

    .. warning::
        AE,AL,AU,SYM/H,SYM/D,ASYM/H,and ASYM/D are included in the omni files and
        thus are read into this class.  I cannot verify the quality of these
        indices distributed with Omni data.  For quality assurance on these
        indices, use the functions in the gme.mag.indices module.

    Parameters
    ----------
    ftpLine : Optional[str]
        an ASCII line from the FTP server. if this is provided, the object is
        initialized from it.  default=None
    dbDict : Optional[dict]
        a dictionary read from the mongodb.  if this is provided, the object
        is initialized from it.  default = None
    res : Optional[int]
        the time resolution of the data.  default=None
    
    Attributes
    ----------
    time : datetime
        an object identifying which time these data are for
    dataSet : str
        the name of the data set
    res : int
        the time resolution of the data, in minutes
    timeshift : int
        timeshift from ACE to bowshock
    bMagAvg : float
        average IMF B magnitude, nT
    bx : float
        IMF Bx, nT
    bye : float
        IMF By (GSE), nT
    bze : float
        IMF Bz (GSE), nT
    bym : float
        IMF By (GSM), nT
    bzm : float
        IMF Bz (GSM), nT
    flowSpeed : float
        plasma flow speed, km/s
    vxe : float
        velocity in x direction (GSE), km/s
    vye : float
        velocity in y direction (GSE), km/s
    vze : float
        velocity in z direction (GSE), km/s
    np : float
        proton density, n/cc
    temp : float
        temperature in K
    pDyn : float
        Flow pressure nPa
    e : float
        Electric field, mV/m
    beta : float
        Plasma Beta
    machNum : float
        Alfven mach number
    ae : float
        AE index, nT
    al : float
        AL index, nT
    au : float
        AU index, nT
    symd : float
        SYM/D index, nT
    symh : float
        SYM/H index, nT
    asyd : float
        ASY/D index, nT
    asyh : float
        ASY/H index, nT
    info : str
        information about where the data come from.  *Please be courteous and
        give credit to data providers when credit is due.*
        
    Methods
    -------
    parseFtp

    Notes
    -----
    If any of the members have a value of None, this means that they could
    not be read for that specific time

    Example
    -------
        emptyOmniObj = gme.ind.omniRec()

    or

        myOmniObj = omniRec(ftpLine=aftpLine)
        
    written by AJ, 20130128

    """
    def parseFtp(self,line):
        """This method is used to convert a line of omni data read from the
        NASA SPDF FTP site into a :class:`omniRec` object.
        
        Parameters
        ----------
        line : str
            the ASCII line from the FTP server

        Returns
        -------
        Nothing

        Notes
        -----
        In general, users will not need to worry about this.
        
        Belongs to class omniRec
        
        Example
        -------
            myOmniObj.parseFtp(ftpLine)
            
        written by AJ, 20130123

        """
        import datetime as dt
        
        #a dict to map from the column number in the line to attribute name
        mappingdict = {9:'timeshift',13:'bMagAvg',14:'bx',15:'bye',16:'bze',17:'bym', \
                                        18:'bzm',21:'flowSpeed',22:'vxe',23:'vye',24:'vze',25:'np', \
                                        26:'temp',27:'pDyn',28:'e',29:'beta',30:'machNum',37:'ae', \
                                        38:'al',39:'au',40:'symd',41:'symh',42:'asyd',43:'asyh'}
                                        
        #split the line into cols
        cols = line.split()
        self.time = dt.datetime(int(cols[0]), 1, 1, int(cols[2]),int(cols[3])) + \
                                    dt.timedelta(days=(int(cols[1])-1))
                                    
        #go through the columns and assign the attribute values 
        for i in range(9,len(cols)):
            if(not mappingdict.has_key(i)): continue
            temp = cols[i]
            temp = temp.replace('.','')
            temp = temp.replace('9','')
            if(temp == ''): continue
            try: setattr(self,mappingdict[i],float(cols[i]))
            except Exception,e:
                logging.exception(e)
                logging.exception('problem assigning value to' + mappingdict[i])
            
    def __init__(self, ftpLine=None, res=None, dbDict=None):
        #initialize the attributes
        #note about where data came from
        self.dataSet = 'Omni'
        self.info = 'These data were downloaded from NASA SPDF.  *Please be courteous and give credit to data providers when credit is due.*'
        self.res = res
        self.timeshift = None
        self.bMagAvg = None
        self.bx = None
        self.bye = None
        self.bze = None
        self.bym = None
        self.bzm = None
        self.flowSpeed = None
        self.vxe = None
        self.vye = None
        self.vze = None
        self.np = None
        self.temp = None
        self.pDyn = None
        self.e = None
        self.beta = None
        self.machNum = None
        self.ae = None
        self.al = None
        self.au = None
        self.symd = None
        self.symh = None
        self.asyd = None
        self.asyh = None
        #if we're initializing from an object, do it!
        if(ftpLine != None): self.parseFtp(ftpLine)
        if(dbDict != None): self.parseDb(dbDict)
    
def readOmni(sTime,eTime=None,res=5,bx=None,bye=None,bze=None,bym=None,bzm=None,pDyn=None,ae=None,symh=None):
    """This function reads omni data.  First, it will try to get it from the
    mongodb, and if it can't find it, it will look on the NASA SPDF FTP
    server using readOmniFtp
    
    Parameters
    ----------
    sTime : datetime
        the earliest time you want data for
    eTime : Optional[datetime]
        the latest time you want data for.  if this is None, end Time will
        be 1 day after sTime.  default = None
    res : Optional[int]
        the time reolution of data desired.  This can be either 1
        or 5. default = 5
    bx : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with bx values in the range [a,b] will be
        returned.  default = None
    bx : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with bx values in the range [a,b] will be
        returned.  default = None
    bye : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with bye values in the range [a,b] will be
        returned.  default = None
    bze : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with bze values in the range [a,b] will be
        returned.  default = None
    bym : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with bym values in the range [a,b] will be
        returned.  default = None
    bzm : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with bzm values in the range [a,b] will be
        returned.  default = None
    pDyn : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with pDyn values in the range [a,b] will be
        returned.  default = None
    ae : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with ae values in the range [a,b] will be
        returned.  default = None
    symh : Optional[list]
        if this is not None, it must be a 2-element list of numbers, [a,b].
        In this case, only data with symh values in the range [a,b] will be
        returned.  default = None

    Returns
    -------
    omniList : list
        if data is found, a list of class omniRec objects matching the
        input parameters is returned.  If no data is found, None is
        returned.

    Example
    -------
        import datetime as dt
        omniList = gme.ind.readOmni(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),bx=[0,5.5],bye=[-1,3.5],bze=[-10,0],ae=[0,56.3])
        
    written by AJ, 20130128

    """
    import datetime as dt
    import davitpy.pydarn.sdio.dbUtils as db
    
    #check all the inputs for validity
    assert(isinstance(sTime,dt.datetime)), \
        logging.error('sTime must be a datetime object')
    assert(eTime == None or isinstance(eTime,dt.datetime)), \
        logging.error('eTime must be either None or a datetime object')
    assert(res==5 or res == 1), logging.error('res must be either 1 or 5')
    var = locals()
    for name in ['bx','bye','bze','bym','bzm','pDyn','ae','symh']:
        assert(var[name] == None or (isinstance(var[name],list) and \
            isinstance(var[name][0],(int,float)) and isinstance(var[name][1],(int,float)))), \
            logging.error(name + ' must None or a list of 2 numbers')

    if(eTime == None): eTime = sTime+dt.timedelta(days=1)
    qryList = []
    #if arguments are provided, query for those
    qryList.append({'time':{'$gte':sTime}})
    qryList.append({'res':res})
    if(eTime != None): qryList.append({'time':{'$lte':eTime}})
    var = locals()
    for name in ['bx','bye','bze','bym','bzm','pDyn','ae','symh']:
        if(var[name] != None): 
            qryList.append({name:{'$gte':min(var[name])}})
            qryList.append({name:{'$lte':max(var[name])}})
            
    #construct the final query definition
    qryDict = {'$and': qryList}
    #connect to the database
    omniData = db.getDataConn(dbName='gme',collName='omni')
    
    #do the query
    if(qryList != []): qry = omniData.find(qryDict)
    else: qry = omniData.find()
    if(qry.count() > 0):
        omniList = []
        for rec in qry.sort('time'):
            omniList.append(omniRec(dbDict=rec))
        logging.info('\nreturning a list with ' + str(len(omniList)) + ' records of omni data')
        return omniList
    #if we didn't find anything on the mongodb
    else:
        logging.info('\ncould not find requested data in the mongodb')
        logging.info('we will look on the ftp server, but your conditions will be (mostly) ignored')
        
        #read from ftp server
        omniList = readOmniFtp(sTime, eTime)
        
        if(omniList != None):
            logging.info('\nreturning a list with ' + str(len(omniList)) + ' recs of omni data')
            return omniList
        else:
            logging.info('\n no data found on FTP server, returning None...')
            return None

            
def readOmniFtp(sTime,eTime=None,res=5):
    """This function reads omni data from the NASA SPDF server via anonymous
    FTP connection.
    
    .. warning::
        You should not use this. Use the general function :func:`readOmni` instead.
    
    Parameters
    ----------
    sTime : datetime
        the earliest time you want data for
    eTime : Optional[datetime]
        the latest time you want data for.  if this is None, eTime will be
        equal to sTime.  default = None
    res : Optional[int]
        the time resolution of the data you want.  Must be either 1 or 5.
        default=5

    Returns
    -------
    omniList : list
        if data is found, a list of class omniRec objects matching the input
        parameters is returned.  If no data is found, None is returned.

    Example
    -------
        import datetime as dt
        omniList = gme.ind.readOmniFtp(dt.datetime(2011,1,1,1,50),eTime=dt.datetime(2011,1,1,10,0),res=5)
        
    written by AJ, 20130128

    """
    from ftplib import FTP
    import datetime as dt
    
    assert(isinstance(sTime,dt.datetime)), logging.error('sTime must be datetime')
    if(eTime == None): eTime=sTime
    assert(isinstance(eTime,dt.datetime)), logging.error('eTime must be datetime')
    assert(eTime >= sTime), logging.error('end time greater than start time')
    assert(res == 1 or res == 5), logging.error('res must be 1 or 5')
    
    #connect to the server
    try: ftp = FTP('spdf.gsfc.nasa.gov')    
    except Exception,e:
        logging.exception(e)
        logging.exception('problem connecting to SPDF server')
        
    #login as anonymous
    try: l=ftp.login()
    except Exception,e:
        logging.exception(e)
        logging.exception('problem logging in to SPDF server')
    
    #go to the omni directory
    try: ftp.cwd('/pub/data/omni/high_res_omni/')
    except Exception,e:
        logging.exception(e)
        logging.exception('error getting to data directory')
    
    #list to hold the lines
    lines = []
    #get the omni data
    for yr in range(sTime.year,eTime.year+1):
        if(res == 1): fname = 'omni_min'+str(yr)+'.asc'
        else: fname = 'omni_5min'+str(yr)+'.asc'
        logging.info('omni: RETR ' + fname)
        try: ftp.retrlines('RETR '+fname,lines.append)
        except Exception,e:
            logging.exception(e)
            logging.exception('error retrieving' + fname)
    
    #convert the ascii lines into a list of omniRec objects
    myOmni = []
    if(len(lines) > 0):
        for l in lines:
            linedate = dt.datetime(int(l[0:4]), 1, 1, int(l[8:11]), int(l[11:14])) + \
                                    dt.timedelta(int(l[5:8]) - 1)
            if(sTime <= linedate <= eTime):
                myOmni.append(omniRec(ftpLine=l,res=res))
            if(linedate > eTime): break
        return myOmni
    else:
        return None
        
def mapOmniMongo(sYear,eYear=None,res=5):
    """This function reads omni data from the NASA SPDF FTP server via
    anonymous FTP connection and maps it to the mongodb.  
    
    .. warning::
        In general, nobody except the database admins will need to use this function
    
    Parameters
    ----------
    sYear : int
        the year to begin mapping data
    eYear : Optional[int]
        the end year for mapping data.  if this is None, eYear will be sYear
    res : Optional[int]
        the time resolution for mapping data.  Can be either 1 or 5.  default=5

    Returns
    -------
    Nothing

    Example
    -------
        gme.ind.mapOmniMongo(1997,res=1)
        
    written by AJ, 20130123

    """
    import davitpy.pydarn.sdio.dbUtils as db
    from davitpy import rcParams
    import datetime as dt
    
    #check inputs
    assert(res == 1 or res == 5), logging.error('res must be either 1 or 5')
    assert(isinstance(sYear,int)), logging.error('sYear must be int')
    if(eYear == None): eYear=sYear
    assert(isinstance(eYear,int)), logging.error('sYear must be None or int')
    assert(eYear >= sYear), logging.error('end year greater than start year')
    
    #get data connection
    mongoData = db.getDataConn(username=rcParams['DBWRITEUSER'],password=rcParams['DBWRITEPASS'],\
                                dbAddress=rcParams['SDDB'],dbName='gme',collName='omni')
    
    #set up all of the indices
    mongoData.ensure_index('time')
    mongoData.ensure_index('res')
    mongoData.ensure_index('bx')
    mongoData.ensure_index('bye')
    mongoData.ensure_index('bze')
    mongoData.ensure_index('bym')
    mongoData.ensure_index('bzm')
    mongoData.ensure_index('pDyn')
    mongoData.ensure_index('ae')
    mongoData.ensure_index('symh')
        
    #read the omni data from the FTP server
    for yr in range(sYear,eYear+1):
        for mon in range(1,13):
            templist = readOmniFtp(dt.datetime(yr,mon,1),dt.datetime(yr,mon,1)+dt.timedelta(days=31),res=res)
            if(templist == None): continue
            for rec in templist:
                #check if a duplicate record exists
                qry = mongoData.find({'$and':[{'time':rec.time},{'res':rec.res}]})
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
                    logging.warning('strange, there is more than 1 record for' + rec.time)
