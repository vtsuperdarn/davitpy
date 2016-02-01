"""
.. module:: dbUtils
   :synopsis: the classes needed for manipulating the mongodb
   
.. moduleauthor:: AJ, 20130108

pydarn.sdio.dbUtils
--------------------

Functions
------------
getServerConn
getDbConn
getDataConn
updateDbDict
readFromDb
mapDbFit
"""

import logging
import datetime as dt
import os
from pymongo import MongoClient
import davitpy

def getServerConn(username=davitpy.rcParams['SDBREADUSER'],
                  password=davitpy.rcParams['SDBREADPASS'],
                  dbaddress=davitpy.rcParams['SDDB']):
    """Gets a connection to the mongodb server.  This is the most basic
    connection.  In order to actually access data, this connection must be used
    to get a database connection which can in turn be used to get a data
    connection.

    Example
    --------
    ::
    sconn = getServerConn(username='auser',password='apass', \
                          dbaddress='sd-work9.ece.vt.edu:27017')

    Parameters
    ------------
    username : (str)
        The username to connect with.  Default is the read-only user defined in
        davitpyrc (default=davitpy.rcParams['SDBREADUSER'])
    password : (str)
        The password corresponding to the user username. The default is defined
        in davitpyrc (default=davitpy.rcParams['SDBREADPASS'])
    dbaddress : (str)
        The address of the database to be accessed.  Default is defined in
        davitpyrc.  (default=davitpy.rcParams['SDDB'])

    Returns
    --------
    sconn : (dict/NoneType)
        A connection to the mongodb server.  None if unable to connect.

    Notes
    --------
    mongodb hierarchy goes SERVER->DATABASE->COLLECTION

    Written by AJ 20130108
    """

    # get a server connection, checking for any errors
    try:
        sconn = MongoClient('mongodb://'+username+':'+password+'@'+dbaddress)
    except Exception,e:
        logging.error(e)
        logging.error('problem connecting to server {}'.format(dbaddress))
        sconn = None
    
    # return connection for good, none for bad
    return sconn

def getDbConn(username=davitpy.rcParams['SDBREADUSER'],
              password=davitpy.rcParams['SDBREADPASS'],
              dbaddress=davitpy.rcParams['SDDB'], dbname='radData'):
    """ Gets a connection to the database 'dbname'. on the mongodb server.
    This is the middle-tier connection.  In order to actually access data, this
    connection must be used to get a data connection.
 
    Examples
    ----------
    dbConn = getDbConn(username='auser',password='apass',\
                       dbaddress='sd-work9.ece.vt.edu:27017',dbname='aDb')

    Parameters
    -----------
    username : (str)
        The username to connect with.  Default is the read-only user defined in
        davitpyrc. (default=davitpy.rcParams['SDBREADUSER'])
    password : (str/bool)
        The password corresponding to the user username.  Default is defined in
        davitpyrc.  If the boolian 'True' is specified, an interactive prompt
        will be used obtain the password.
        (default=davitpy.rcParams['SDBREADPASS'])
    dbaddress : (str)
        The address of the database to be accessed, eg
        'sd-work9.ece.vt.edu:27017'.  Default is defined in davitpyrc.
        (default=davitpy.rcParams['SDDB'])
    dbname : (str)
        The name of the database to connect to. Default is 'radData', where fit
        data is stored. (default='radData')

    Returns
    --------
    dbconn : (dict/NoneType)
        A connection to the database, or None if a connection could not be
        established.

    Notes
    -------
    Mongodb hierarchy goes SERVER->DATABASE->COLLECTION

    Written by AJ 20130108
    """
    # Initialize the database connection
    dbconn = None

    # get a connection to the server
    sconn = getServerConn(username=username, password=password,
                          dbaddress=dbaddress)
    # if we have a good server connection
    if(sconn != None):
        # connect to the database, testing for errors
        try:
            dbConn = getattr(sconn, dbname)
        except:
            logging.error('error connecting to database {}'.format(dbname))

    # return connection for good, None for bad
    return dbconn

def getDataConn(username=davitpy.rcParams['SDBREADUSER'],
                password=davitpy.rcParams['SDBREADPASS'],
                dbaddress=davitpy.rcParams['SDDB'], dbname='radData',
                collname='beams'):
    """Gets a connection to the collection collname on the mongodb server. This
    is the highetst level connection.
 
    Examples
    ----------
    dataconn = getDbConn(username='auser',password='apass',\
                         dbaddress='sd-work9.ece.vt.edu:27017',\
                         dbname='aDb',collname='acoll')

    Parameters
    -----------
    username : (str)
        The username to connect with.  Default is the read-only user defined in
        rcParams.  (default=davitpy.rcParams['SDBREADUSER'])
    password : (str/bool)
        The password corresponding to the user username.  The default password
        is defined in rcParams.  If the boolian 'True' is used, an interactive
        plot will be used.  (default=davitpy.rcParams['SDBREADPASS'])
    dbaddress : (str)
        The address of the database to be accessed, eg
        'sd-work9.ece.vt.edu:27017'.  Default is defined in rcParams.
        (default=davitpy.rcParams['SDDB'])
    dbname : (str)
        The name of the database to connect to. (default='radData')
    collname : (str)
        The name of the collection to connect to. (default='beams')
 
    Returns
    --------
    dataconn : (/NoneType)
        A connection to the database, or None if no connection could be made.
 
    Notes
    ------
    mongodb hierarchy goes SERVER->DATABASE->COLLECTION

    Written by AJ 20130108
    """
    # Initialize data connection
    dataconn = None

    # get a connection to the database
    dbconn = getDbConn(username=username, password=password,
                       dbaddress=dbaddress, dbname=dbname)

    if(dbconn != None):
        # get the collection collname
        try:
            dataconn = getattr(dbconn, collname)
        except:
            logging.error("can't connect to collection {}".format(collname))

    return dataconn

def updateDbDict(dbdict, dmapdict):
    """ updates a mongodb dictionary with data from a dmap dictionary

    Examples
    ---------
    newDbDict = updateDbDict(oldDbdict, dmapdict)

    Parameters
    ----------
    dbdict : (dict)
        The dictionary for mongodb use
    dmapdict : (dict)
        The dictionary read from the dmap file

    Returns
    --------
    dbdict : (dict)
        An updated dictionary for use int he mongodb database

    Written by AJ 20130108
    """

    # iterate through the items in the db dict
    for key,val in dbdict.iteritems():
        # pass over the mongodb _id param
        if(key == '_id'):
            continue

        # check if the dmap dict has a corresponding key
        if(dmapdict.has_key(cipher[key])):
            # check for a valid different value
            if(val != dmapdict[cipher[key]] and dmapdict[cipher[key]] != None):
                # update the db dictionary value with the new value
                try:
                    dbdict[key] = dmapdict[cipher[key]]
                except:
                    logging.error('problem changing value')

    # return the updated dictionary
    return dbdict

def readFromDb(sTime=None, eTime=None, stid=None, channel=None, bmnum=None,
               cp=None, fileType='fitex', exactFlg=False):
    """ read some record(s) from the mongodb database

    Examples
    ---------
    my_data = readFromDb(sTime=atime, stid=33, channel=None, bmnum=7, cp=153, \
                         fileType='fitacf', exactFlg=True)

    Parameters
    ----------
    sTime : (datetime/NoneType)
        A datetime object with the time to start reading.  If this is None,
        sTime is defined as 00:00 UT on 1 Jan 2011. (default=None)
    eTime : (datetime/NoneType)
        A datetime object specifying the last record to read. If this is none,
        the first record after sTime (within 24 hours, provided it exists) will
        be read.  (default=None)
    stid : (int/NoneType)
        The station id of the radar we want data for.  If this is None, all
        available radars will be read.  (default=None)
    channel : (str/NoneType)
        The channel letter for which to read data.  If this is None, data from
        all channels will be read.  (default=None)
    bmnum : (int/NoneType)
        The beam number for which to read data.  If this is None, data from all
        beams will be read.  (default=None)
    cp : (int/NoneType)
        The control program for which to read data.  If this is None, data from
        all control programs will be read.  (default=None)
    fileType : (str)
        The filetype for which to read data.  Valid inputs are:
        'fitex', 'fitacf', 'lmfit', 'rawacf', 'iqdat'.  If a fit file type is
        specified but data is not found, the program will search for another
        fit type. (default='fitex')
    exactFlg : (bool)
        A flag to indicate the we only want a record with EXACTLY the params
        specified (including time, to the ms).  This is useful for updating
        records.  (default=False)

    Returns
    --------
    qry : (list/None)
        A list of pydarn.sdio.beamData objects in chronological order.

    Notes
    -------
    I recommend making your query as specific as possible, as this will speed
    up the read speeds.  The biggest limiting factor is network speed, so be
    specific.  For even higher performance, consider writing your own mongodb
    queries.

    Written by AJ 20130108
    """
    t = dt.datetime.now()
  
    # a list which will contain our query criteria
    qry_list = []

    # if a start time is not provided, use a default
    if(sTime == None):
        logging.info('No starting time supplied, defaulting to 1/1/2011')
        sTime = dt.datetime(2011, 1, 1)

    # if we want only a single exact time (useful for filling/updating database)
    if(exactFlg):
        qry_list.append({"time": sTime})
    else:
        # if endtime is not provided, use a 24-hour window
        if(eTime == None): 
            eTime = sTime + dt.timedelta(hours=24)

        # query for time later than start time and less than end time
        qry_list.append({cipher["time"]: {"$lte": eTime}})
        qry_list.append({cipher["time"]: {"$gte": sTime}})

    # if other arguments are provided, query for those
    if(stid != None):
        qry_list.append({cipher["stid"]: stid})
    if(channel != None):
        qry_list.append({cipher["channel"]: channel})
    if(bmnum != None):
        qry_list.append({cipher["bmnum"]: bmnum})
    if(cp != None):
        qry_list.append({cipher["cp"]: cp})

    # get a data connection for the mongodb database
    beams = getDataConn()

    # some arrays for dealing with data types
    if(fileType == 'fitex'):
        flg = 'exflg'
    elif(fileType == 'fitacf'):
        flg = 'acflg'
    elif(fileType == 'lmfit'):
        flg = 'lmflg'
    elif(fileType == 'rawacf'):
        flg = 'rawflg'
    elif(fileType == 'iqdat'):
        flg = 'iqflg'

    # append the current file type to the query
    qry_list.append({cipher[flg]:1})

    # construct the final query definition
    qrydict = {'$and': qry_list}

    # make a dictionary telling which data types NOT to get,
    # eg dont get rawacf, iqdat, fitacf, lmfit for fitex request
    exdict = {}
    for key,val in refArr.iteritems():
        if(key != flg):
            exdict[cipher[val]] = 0

    # do the actual query
    qry = beams.find(qrydict, exdict)

    # check if we have any results
    try:
        count = qry.count()
    except Exception,e:
        logging.error(e)
        qry = None

    return qry


def mapDbFit(date_str, rad, time=[0,2400], fileType='fitex'):
    """Put dmap data into the mongodb database

    Example
    -------
    ::
    mapDbFit('20110710', 'bks', time=[0,240], fileType='fitacf')

    Parameters
    ------------
    date_str : (str)
        The target date in 'yyymmdd' format
    rad : (str)
        The three letter radar code, e.g. 'bks'
    time : (list)
        The time range to perform the operation in reduced hhmm format,
        ie [28,652] instead of [0028,0652].  (default=[0,2400])
    fileType : (str)
        The file type for which to perform the operation. Valid inputs are:
        'fitex', 'fitacf', 'lmfit', 'rawacf' , 'iqdat' (default='fitacf')

    Returns
    ---------
    Void

    Note
    ------
    This is a write operation, so you must have DBWRITEUSER and DBWRITEPASS
    defined in rcParams.
 
    Written by AJ 20130108
    """
    from davitpy import utils
    import math
  
    # parse the date_str into a datetime object
    my_date = utils.yyyymmddToDate(date_str)

    # we need to get the start and end hours of the request becasue of how the
    # files are named
    hr1 = 2 * int(math.floor(time[0] / 50.0))
    hr2 = 2 * int(math.floor(time[1] / 50.0))
    print "TEST!", hr1, int(math.floor(time[0] / 100. / 2.)*2)

    min1 = int(time[0] - int(math.floor(time[0] / 100.0) * 100))
    min2 = int(time[1] - int(math.floor(time[1] / 1000.) * 100))

    # move back a little in time because files often start at 2 mins
    # after the hour
    stime = my_date.replace(hour=hr1, minute=min1)
    stime = stime - dt.timedelta(minutes=4)

    # end time boundary condition
    if(hr2 == 24):
        etime = my_date + dt.timedelta(days=1)
    else:
        etime = my_date.replace(hour=hr2, minute=min2)
    
    # open the dmap file
    my_file = radDataOpen(stime, rad, eTime=etime, fileType=fileType,
                          src='local')
    if(my_file == None):
        estr = 'no data available for the requested time ['
        estr = '{:s}{:} to {:}], radar [{:s}], '.format(estr, stime, etime, rad)
        estr = '{:s}and file type [{:s}] combination'.format(estr, fileType)
        logging.error(estr)
        return None

    # read a record
    dmap_beam = radDataReadRec(my_file)
    if(dmap_beam == None):
        estr = 'no data available for the requested time ['
        estr = '{:s}{:} to {:}], radar [{:s}], '.format(estr, stime, etime, rad)
        estr = '{:s}and file type [{:s}] combination'.format(estr, fileType)
        logging.error(estr)
        return None
    
    # get a write connection to the db
    try:
        beams = getDataConn(davitpy.rcParams['DBWRITEUSER'],
                            davitpy.rcParams['DBWRITEPASS'])
    except:
        logging.error('cannot connect to database for writing')
        return None

    # ensure all necessary indices
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

    # go until the end of file
    while(dmap_beam != None):
        # check that we're in the time window
        if(dmap_beam.time > etime):
            break
        if(dmap_beam.time <= etime):
            #check for verbose output
            estr = 'processing time [{:}], radar [{:}]'.format(dmap_beam.time,
                                                               dmap_beam.stid)
            logging.info(estr)
            del dmap_beam.fType
            del dmap_beam.fit
            del dmap_beam.rawacf.parent

            # convert the dmap dict to a db dictionary
            dmapdict = dmap_beam.toDbDict()
      
            # perform a query (search for already existent entry
            qry = beams.find({'$and':[{cipher["time"]: dmap_beam.time},
                                      {cipher["bmnum"]: dmap_beam.bmnum},
                                      {cipher["channel"]: dmap_beam.channel},
                                      {cipher["stid"]: dmap_beam.stid},
                                      {cipher["cp"]: dmap_beam.cp}]})
            # check for a new entry
            if(qry.count() == 0):
                # instert the data
                beams.insert(dmapdict)
            else:
                # update the data
                dbdict = qry.next()
                dbdict = updateDbDict(dbdict, dmapdict)
                beams.save(dbdict)
        # read the next record from the dmap file
        dmap_beam = radDataReadRec(my_file)
  
    # close the dmap file
    my_file.close()
