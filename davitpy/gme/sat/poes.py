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
"""A module for reading, writing, and storing Polar Orbiting Environmental
Satellites (POES) data

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
    """a class to represent a record of POES data.

    Parameters
    ----------
    ftpLine : (str]
      an ASCII line from the FTP server. if this is provided, the
      object is initialized from it.  header must be provided in
      conjunction with this.  default=None
    header : (str]
      the header from the ASCII FTP file.  default=None
    dbDict : (dict]
      a dictionary read from the mongodb.  if this is provided,
      the object is initialized from it.  default = None
    satnum : (int]
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

    Extends class gmeBase.gmeData.  Insight on the class members can
    be obtained from the NOAA NGDC site:
    <ftp://satdat.ngdc.noaa.gov/sem/poes/data/readme.txt>. 
    Note that POES data are available from 1998-present day (or whatever the
    latest NOAA has uploaded is).  **The data are the 16-second averages**

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

    def parseFtp(self, line, header):
        """This method is used to convert a line of poes data read from
        the NOAA NGDC FTP site into a :class:`poesRec` object.

        Parameters
        ----------
        line : (str)
            the ASCII line from the FTP server
        header : (str)
            The header, used to set the attribute key

        Returns
        -------
        Void

        Example
        -------
        myPoesObj.parseFtp(ftpLine)

        written by AJ, 20130131
        """
        import datetime as dt

        # split the line into cols
        cols = line.split()
        head = header.split()

        # Set the time
        sec = int(np.floor(float(cols[5])))
        self.time = dt.datetime(int(cols[0]), int(cols[1]), int(cols[2]),
                                int(cols[3]), int(cols[4]), sec,
                                int(round((float(cols[5]) - sec) * 1e6)))

        for key in self.__dict__.iterkeys():
            if(key == 'dataSet' or key == 'info' or key == 'satnum' or
               key == 'time'):
                continue
            try:
                ind = head.index(key)
            except Exception,e:
                logging.exception(e)
                logging.exception('problem setting attribute' + key)

            # check for a good value
            if(float(cols[ind]) != -999.0):
                setattr(self, key, float(cols[ind]))
  
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
        if(ftpLine != None):
            self.parseFtp(ftpLine, header)
        if(dbDict != None):
            self.parseDb(dbDict)
    
def readPoes(stime, eTime=None, satnum=None, folat=None, folon=None, ted=None,
             echar=None, pchar=None):
    """This function reads POES data.

    Parameters
    ----------
    stime : (datetime or None)
        the earliest time you want data for
    eTime : (datetime or None)
        the latest time you want data for.  if this is None, end Time will be 1
        day after stime.  (default=None)
    satnum : (int)
        the satellite you want data for.  eg 17 for noaa17.  if this is None,
        data for all satellites will be returned.  (default=None)
    folat : (list or None)
        if this is not None, it must be a 2-element list of numbers, [a,b].  In
        this case, only data with bx values in the range [a,b] will be returned.
        (default=None)
    folon : (list or None)
        if this is not None, it must be a 2-element list of numbers, [a,b].  In
        this case, only data with bye values in the range [a,b] will be returned
        (default=None)
    ted : (list or None)
        if this is not None, it must be a 2-element list of numbers, [a,b].  In
        this case, only data with bze values in the range [a,b] will be returned
        (default=None)
    echar : (list or None)
        if this is not None, it must be a 2-element list of numbers, [a,b].  In
        this case, only data with bym values in the range [a,b] will be returned
        (default=None)
    pchar : (list or None)
        if this is not None, it must be a 2-element list of numbers, [a,b].  In
        this case, only data with bzm values in the range [a,b] will be returned
        (default=None)

    Returns
    -------
    poesList : (list or None)
        if data is found, a list of class poesRec objects matching the input
        parameters is returned.  If no data is found, None is returned.

    Notes
    --------
    First, it will try to get it from the mongodb, and if it can't find it, it
    will look on the NOAA NGDC FTP server using :func:`readPoesFtp`.  The data
    are 16-second averages

    Example
    -------
        import datetime as dt
        poesList = gme.sat.readPoes(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),folat=[60,80])
    
    written by AJ, 20130131
    """
    import datetime as dt
    import davitpy.pydarn.sdio.dbUtils as db

    # check all the inputs for validity
    assert isinstance(stime, dt.datetime), \
        logging.error('stime must be a datetime object')
    assert eTime == None or isinstance(eTime,dt.datetime), \
        logging.error('eTime must be either None or a datetime object')
    assert satnum == None or isinstance(satnum,int), \
        logging.error('satnum must be an int')
    var = locals()
    for name in ['folat','folon','ted','echar','pchar']:
        assert(var[name] == None or (isinstance(var[name],list) and
                                     isinstance(var[name][0],(int,float)) and
                                     isinstance(var[name][1],(int,float)))), \
        logging.error(name + ' must None or a list of 2 numbers')

    if(eTime == None):
        eTime = stime + dt.timedelta(days=1)
    qryList = []
    # if arguments are provided, query for those
    qryList.append({'time':{'$gte':stime}})
    if(eTime != None):
        qryList.append({'time':{'$lte':eTime}})
    if(satnum != None):
        qryList.append({'satnum':satnum})
    var = locals()
    for name in ['folat','folon','ted','echar','pchar']:
        if(var[name] != None): 
            qryList.append({name:{'$gte':min(var[name])}})
            qryList.append({name:{'$lte':max(var[name])}})

    # construct the final query definition
    qryDict = {'$and': qryList}
    # connect to the database
    poesData = db.getDataConn(dbName='gme', collName='poes')

    # do the query
    qry = poesData.find(qryDict) if qryList != [] else poesData.find()
    if(qry.count() > 0):
        poesList = []
        for rec in qry.sort('time'):
            poesList.append(poesRec(dbDict=rec))
        logging.info('nreturning a list with '+ len(poesList) +
                     ' records of poes data')
        return poesList

    # if we didn't find anything on the mongodb
    else:
        logging.info('could not find requested data in the mongodb')
        return None
        # print 'we will look on the ftp server, but your conditions will be
        # (mostly) ignored'

        ## read from ftp server
        # poesList = readPoesFtp(stime, eTime)

        # if(poesList != None):
        # print '\nreturning a list with',len(poesList),'recs of poes data'
        # return poesList
        # else:
        # print '\n no data found on FTP server, returning None...'
        # return None

def readPoesFtp(stime, eTime=None):
    """This function reads poes data from the NOAA NGDC server via
    anonymous FTP connection.  It should not be used.

    Parameters
    ----------
    stime : (datetime)
        the earliest time you want data for
    eTime : (datetime)
        the latest time you want data for.  if this is None, eTime will be equal
        1 day after stime.  default=None

    Returns
    -------
    poesList : (list or None)
        if data is found, a list of :class:`poesRec` objects matching the input
        parameters is returned.  If no data is found, None is returned.

    Notes
    -----
    You should not use this. Use the general function :func:`readPoes` instead.

    written by AJ, 20130128
    """
    from ftplib import FTP
    import datetime as dt

    assert isinstance(stime, dt.datetime), \
        logging.error('stime must be datetime')
    if(eTime == None):
        eTime = stime + dt.timedelta(days=1)
    assert isinstance(eTime, dt.datetime), \
        logging.error('eTime must be datetime')
    assert eTime >= stime, logging.error('end time greater than start time')

    # connect to the server
    try:
        ftp = FTP('satdat.ngdc.noaa.gov')  
    except Exception,e:
        logging.exception(e)
        logging.exception('problem connecting to NOAA server')
        return None

    # login as anonymous
    try:
        l = ftp.login()
    except Exception,e:
        logging.exception(e)
        logging.exception('problem logging in to NOAA server')
        return None

    my_poes = []
    # get the poes data
    my_time = dt.datetime(stime.year, stime.month, stime.day)
    while my_time <= eTime:
        # go to the data directory
        try:
            ftp.cwd('/sem/poes/data/avg/txt/'+str(my_time.year))
        except Exception,e:
            logging.exception(e)
            logging.exception('error getting to data directory')
            return None

        # list directory contents
        dirlist = ftp.nlst()
        for dire in dirlist:
            # check for satellite directory
            if(dire.find('noaa') == -1):
                continue
            satnum = dire.replace('noaa','')
            # chege to file directory
            ftp.cwd('/sem/poes/data/avg/txt/'+str(my_time.year)+'/'+dire)
            fname = 'poes_n'+satnum+'_'+my_time.strftime("%Y%m%d")+'.txt'
            logging.info('poes: RETR ' + fname)
            # list to hold the lines
            lines = []
            # get the data
            try:
                ftp.retrlines('RETR '+fname,lines.append)
            except Exception,e:
                logging.exception(e)
                logging.exception('error retrieving' + fname)

            # convert the ascii lines into a list of poesRec objects
            # skip first (header) line
            for line in lines[1:]:
                cols = line.split()
                t = dt.datetime(int(cols[0]), int(cols[1]), int(cols[2]),
                                int(cols[3]), int(cols[4]))
                if(stime <= t <= eTime):
                    my_poes.append(poesRec(ftpLine=line, satnum=int(satnum),
                                           header=lines[0]))

        # increment my_time
        my_time += dt.timedelta(days=1)

    if(len(my_poes) > 0):
        return my_poes
    else:
        return None

def mapPoesMongo(syear, eYear=None):
    """This function reads poes data from the NOAA NGDC FTP server via anonymous
    FTP connection and maps it to the mongodb.  

    Parameters
    ----------
    syear : (int)
        the year to begin mapping data
    eYear : (int or None)
        the end year for mapping data.  if this is None, eYear will be syear

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
    assert isinstance(syear, int), logging.error('syear must be int')
    if eYear == None:
        eYear = syear
    assert isinstance(eYear, int), logging.error('syear must be None or int')
    assert eYear >= syear, logging.error('end year greater than start year')

    # get data connection
    mongo_data = db.getDataConn(username=rcParams['DBWRITEUSER'],
                                password=rcParams['DBWRITEPASS'],
                                dbAddress=rcParams['SDDB'], dbName='gme',
                                collName='poes')

    # set up all of the indices
    mongo_data.ensure_index('time')
    mongo_data.ensure_index('satnum')
    mongo_data.ensure_index('folat')
    mongo_data.ensure_index('folon')
    mongo_data.ensure_index('ted')
    mongo_data.ensure_index('echar')
    mongo_data.ensure_index('pchar')

    # read the poes data from the FTP server
    my_time = dt.datetime(syear, 1, 1)
    while my_time < dt.datetime(eYear+1, 1, 1):
        # 10 day at a time, to not fill up RAM
        templist = readPoesFtp(my_time, my_time+dt.timedelta(days=10))
        if(templist == None):
            continue
        for rec in templist:
            # check if a duplicate record exists
            qry = mongo_data.find({'$and':[{'time':rec.time},
                                          {'satnum':rec.satnum}]})
            logging.info("{:}, {:}".format(rec.time, rec.satnum))
            tempRec = rec.toDbDict()
            cnt = qry.count()
            # if this is a new record, insert it; if it exists, update it
            if cnt == 0:
                mongo_data.insert(tempRec)
            elif cnt == 1:
                logging.debug('found one!!')
                db_dict = qry.next()
                temp = db_dict['_id']
                db_dict = tempRec
                db_dict['_id'] = temp
                mongo_data.save(db_dict)
            else:
                logging.info('strange, there is more than 1 record for '
                             + rec.time)
        del templist
        my_time += dt.timedelta(days=10)

def overlayPoesTed(basemap_obj, ax, start_time, endTime=None,
                   coords='geo', hemi=1, folat=[45.0, 90.0], satNum=None,
                   param='ted', scMin=-3.0,scMax=0.5):
    """This function overlays POES TED data onto a map object.

    Parameters
    ----------
    basemap_obj : (datetime or None)
        the map object you want data to be overlayed on.
    ax : (datetime or None)
        the Axis Handle used.
    start_time : (datetime or None)
        the starttime you want data for. If endTime is not given overlays data
        from satellites with in +/- 45 min of the start_time
    endTime : (datetime or None)
        the latest time you want data for.  if this is None, data from
        satellites within +/- 45 min of the start_time is overlayed.
        (default=None)
    satnum : (int)
        the satellite you want data for.  eg 17 for noaa17.  if this is None,
        data for all satellites will be returned.  default=None
    coords : (str)
        Coordinates of the map object on which you want data to be overlayed on,
        'geo', 'mag', 'mlt'. Default 'geo'
    hemi : (list or None)
        Hemisphere of the map object on which you want data to be overlayed on.
        Value is 1 for northern hemisphere and -1 for the southern hemisphere.
        (default=1)
    folat : (list or None)
        if this is not None, it must be a 2-element list of numbers, [a,b].  In
        this case, only data with latitude values in the range [a,b] will be
        returned.  (default=None)
    param : (str)
        the name of the poes parameter to be plotted.  default='ted'

    Returns
    -------
    btpltpoes :
        POES TED data is overlayed on the map object. If no data is found, None
        is returned.

    Example
    -------
      import datetime as dt
      poesList = gme.sat.overlayPoesTed(MapObj, sTime=dt.datetime(2011,3,4,4))

    written by Bharat Kunduri, 20130216
    """
    import datetime as dt
    import numpy as np
    import math
    import models
    import matplotlib.cm as cm
    from davitpy import rcParams

    igrf_file = rcParams['IGRF_DAVITPY_COEFF_FILE']

    # check all the inputs for validity
    assert isinstance(start_time, dt.datetime), \
        logging.error('stime must be a datetime object')
    assert endTime == None or isinstance(endTime, dt.datetime), \
        logging.error('eTime must be either None or a datetime object')

    var = locals()

    assert var['satNum'] == None or isinstance(var['satNum'], list), \
        logging.error('satNum must None or a list of satellite (int) numbers')

    if satNum != None :
        assert len(satNum) <= 5, \
            logging.error('there are only 5 operational POES satellites (2013)')

    assert var['folat'] == None or (isinstance(var['folat'], list) and
                                    isinstance(var['folat'][0],(int, float)) and
                                    isinstance(var['folat'][1], (int, float))),\
        logging.error('folat must None or a list of 2 numbers')

    # Check the hemisphere and get the appropriate folat
    folat = [math.fabs(folat[0]) * hemi, math.fabs(folat[1]) * hemi]

    # Check if the endTime is given in which case the user wants a specific
    # time interval to search for.  If not we'll give him the best available
    # passes for the selected start time...
    time_range = None if endTime is None else np.array([start_time, endTime])
    plt_time_int = np.array(dt.timedelta(minutes=45))

    # check if the time_range is set... if not set the time_range to +/-
    # plt_time_int of the start_time
    if time_range is None:
        time_range = np.array([start_time - plt_time_int,
                              start_time + plt_time_int])

    # SatNums - currently operational POES satellites are 15, 16, 17, 18, 19
    if satNum is None:
        satNum = [None]
    # If any particular satellite number is not chosen by user loop through all
    # the available one's 

    satNum = np.array(satNum)
    snum_size = len(satNum)
    
    lat_poes_all = [[] for j in range(snum_size)]
    lon_poes_all = [[] for j in range(snum_size)]
    ted_poes_all = [[] for j in range(snum_size)]
    time_poes_all = [[] for j in range(snum_size)]
    len_data_all = [[] for j in range(snum_size)]

    good_flag = False

    for sn in range(snum_size):
        if(satNum[sn] != None):
            curr_poes = readPoes(time_range[0], eTime=time_range[1],
                                 satnum=int(satNum[sn]), folat=folat)
        else:
            curr_poes = readPoes(time_range[0], eTime=time_range[1],
                                 satnum=satNum[sn], folat=folat)

        # Check if the data is loaded...
        if curr_poes == None:
            logging.warning('No data found')
            continue
            #return None
        else:
            good_flag = True

        # Loop through the list and store the data into arrays    
        len_data_all.append(len(curr_poes))

        for l in curr_poes:
            # Store our data in arrays
            try:
                ted_poes_all[sn].append(math.log10(getattr(l, param)))
                if coords == 'mag' or coords == 'mlt':
                    lat, lon,_ = models.aacgm.convert_latlon_arr(l.folat, \
                          l.folon, np.zeros(shape=l.folat.shape), l.time, 'G2A')
                    lat_poes_all[sn].append(lat)
                    if coords == 'mag':
                        lon_poes_all[sn].append(lon)
                    else:
                        mlt = models.aacgm.mlt_convert(l.time.year,
                                                       l.time.month, l.time.day,
                                                       l.time.hour,
                                                       l.time.minute,
                                                       l.time.second, lon,
                                                       igrf_file)
                        lon_poes_all[sn].append(mlt * 360.0 / 24.0)
                else:
                    lat_poes_all[sn].append(l.folat)
                    lon_poes_all[sn].append(l.folon)

                time_poes_all[sn].append(l.time)
            except Exception,e:
                logging.exception(e)
                logging.exception('could not get parameter for time' + l.time)

    if not good_flag:
      return None

    lat_poes_all = np.array(lat_poes_all) 
    lon_poes_all = np.array(lon_poes_all)
    ted_poes_all = np.array(ted_poes_all)
    time_poes_all = np.array(time_poes_all)
    len_data_all = np.array(len_data_all)

    # get the axis of the figure...
    for nn in range(snum_size):
        x, y = basemap_obj(lon_poes_all[nn], lat_poes_all[nn])
        bpltpoes = basemap_obj.scatter(x,y,c=ted_poes_all[nn], vmin=scMin,
                                      vmax=scMax, alpha=0.7, cmap=cm.jet,
                                      zorder=7.0, edgecolor='none')
        timeCurr = time_poes_all[nn]
        for aa in range(len(lat_poes_all[nn])):
            if aa % 10 == 0:
                str_curr = str(timeCurr[aa].hour)+':'+str(timeCurr[aa].minute)
                ax.annotate(str_curr, xy =(x[aa], y[aa]), size=5, zorder=6.0)

    # Old formatting
    #------------------
    # import matplotlib.pyplot as plt
    # poes_ticks = [-3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5]
    # cbar = plt.colorbar(bpltpoes, ticks=poes_ticks, orientation='horizontal')
    # cbar.ax.set_xticklabels(poes_ticks)
    # cbar.set_label(r"Total Log Energy Flux [ergs cm$^{-2}$ s$^{-1}$]")

    return bpltpoes

def overlayPoesBnd(basemap_obj, ax, start_time, coords='geo', hemi=1,
                   equBnd=True, polBnd=False ) :
    """Overlay POES data on a map

    Parameters
    ----------
    basemap_obj : (class 'mpl_toolkits.basemap.Basemap')
        the map object you want data to be overlayed on.
    ax : (class 'matplotlib.axes._subplots.AxesSubplot')
        the Axis Handle used.
    start_time : (datetime)
        the starttime you want data for. If endTime is not given overlays data
        from satellites with in +/- 45 min of the start_time
    coords : (list or None)
        Coordinates of the map object on which you want data to be overlayed on.
        (default='geo')
    hemi : (list or None)
        Hemisphere of the map object on which you want data to be overlayed on.
        Value is 1 for northern hemisphere and -1 for the southern hemisphere.
        (default=1)
    equBnd : (list or None]
        If this is True the equatorward auroral oval boundary fit from the TED
        data is overlayed on the map object. (default=True)
    polBnd : (list or None]
        If this is True the poleward auroral oval boundary fit from the TED
        data is overlayed on the map object. (default=False)

    Returns
    -------
    Nothing

    Notes
    ---------
    This function reads POES TED data with in +/- 45 min of the given time, fits
    the auroral oval boundaries and overlays them on a map object. The poleward
    boundary is not accurate all the times due to lesser number of satellite
    passes identifying it.

    Example
    -------
        import datetime as dt
        poesList = gme.sat.overlayPoesTed(MapObj, sTime=dt.datetime(2011,3,4,4))

    written by Bharat Kunduri, 20130216
    """
    import datetime as dt
    import numpy as np
    import math
    import matplotlib.cm as cm
    from scipy import optimize
    import models
    from davitpy import rcParams

    igrf_file = rcParams['IGRF_DAVITPY_COEFF_FILE']
    
    # check all the inputs for validity
    assert isinstance(start_time, dt.datetime), \
        logging.error('stime must be a datetime object')

    # Check the hemisphere and get the appropriate folat
    folat = [45.0 * hemi, 90.0 * hemi]

    # Get the time range we choose +/- 45 minutes....
    plt_time_int = np.array(dt.timedelta(minutes=45))
    time_range = np.array([start_time-plt_time_int, start_time+plt_time_int])

    # We set the TED cut-off value to -0.75,
    # From observed cases this appeared to do well...
    # though fails sometimes especially during geomagnetically quiet times...
    # However this is version 1.0 and there always is room for improvement
    equBndCutoffVal = -0.75

    # If any particular satellite number is not chosen by user loop through all
    # the available ones.  Writer preferred numpy arrays over lists
    sat_num = np.array([15, 16, 17, 18, 19])
    snum_size = sat_num.shape[0]

    lat_poes_all = [[] for j in range(snum_size)]
    lon_poes_all = [[] for j in range(snum_size)]
    ted_poes_all = [[] for j in range(snum_size)]
    time_poes_all = [[] for j in range(snum_size)]
    len_data_all = [[] for j in range(snum_size)]

    for sn in range(snum_size):
        curr_poes = readPoes(time_range[0], eTime=time_range[1],
                             satnum=int(sat_num[sn]), folat=folat)

        # Check if the data is loaded...
        if curr_poes == None:
            logging.warning('No data found')
            continue

        # Loop through the list and store the data into arrays    
        len_data_all.append(len(curr_poes))

        for l in range(len_data_all[-1]):
            # Store our data in arrays if the TED data value is > than the
            # cutoff value
            try:
                x = math.log10(curr_poes[l].ted)
            except:
                continue

            if x > equBndCutoffVal:
                if coords == 'mag' or coords == 'mlt':
                    lat, lon, _ = models.aacgm.convert_latlon_arr( \
                                    curr_poes[l].folat, curr_poes[l].folon, \
                                    np.zeroes(shape=curr_poes[l].folat.shape), \
                                    curr_poes[l].time.year, 'G2A')
                    lat_poes_all[sn].append(lat)
                    if coords == 'mag':
                        lon_poes_all[sn].append(lon)
                    else:
                        tt = curr_poes[l].time
                        mlt = models.aacgm.mlt_convert(tt.year, tt.month,
                                                       tt.day, tt.hour,
                                                       tt.minute, tt.second,
                                                       lon, igrf_file)
                        lon_poes_all[sn].append(mlt * 360.0 / 24.0)
                else:
                    lat_poes_all[sn].append(curr_poes[l].folat)
                    lon_poes_all[sn].append(curr_poes[l].folon)

                ted_poes_all[sn].append(math.log10(curr_poes[l].ted))
                time_poes_all[sn].append(curr_poes[l].time)

    lat_poes_all = np.array(lat_poes_all)
    lon_poes_all = np.array(lon_poes_all)
    ted_poes_all = np.array(ted_poes_all)
    time_poes_all = np.array(time_poes_all)
    len_data_all = np.array(len_data_all)

    # Now to identify the boundaries...
    # Also need to check if the boundary is equatorward or poleward..
    # When satellite is moving from high-lat to low-lat decrease in flux would
    # mean equatorward boundary.  When satellite is moving from low-lat to
    # high-lat increase in flux would mean equatorward boundary that is what we
    # are trying to check here

    eq_bnd_lats = []
    eq_bnd_lons = []
    po_bnd_lats = []
    po_bnd_lons = []    

    for n1 in range(snum_size):
        curr_sat_lats = lat_poes_all[n1]
        curr_sat_lons = lon_poes_all[n1]
        curr_sat_teds = ted_poes_all[n1]

        test_lat_ltoh = []
        test_lon_ltoh = []
        test_lat_htol = []
        test_lon_htol = []

        test_lat_ltohp = []
        test_lon_ltohp = []
        test_lat_htolp = []
        test_lon_htolp = []

        for n2 in range(len(curr_sat_lats)-1):
            # Check if the satellite is moving from low-lat to high-lat or not
            if math.fabs(curr_sat_lats[n2]) < math.fabs(curr_sat_lats[n2+1]):
                if curr_sat_teds[n2] < curr_sat_teds[n2+1]:
                    test_lat_ltoh.append(curr_sat_lats[n2])
                    test_lon_ltoh.append(curr_sat_lons[n2])

                if curr_sat_teds[n2] > curr_sat_teds[n2+1]:
                    test_lat_ltohp.append(curr_sat_lats[n2])
                    test_lon_ltohp.append(curr_sat_lons[n2])

            if math.fabs(curr_sat_lats[n2]) > math.fabs(curr_sat_lats[n2+1]):
                if curr_sat_teds[n2] > curr_sat_teds[n2+1]:
                    test_lat_htol.append(curr_sat_lats[n2])
                    test_lon_htol.append(curr_sat_lons[n2])

                if curr_sat_teds[n2] < curr_sat_teds[n2+1]:
                    test_lat_htolp.append(curr_sat_lats[n2])
                    test_lon_htolp.append(curr_sat_lons[n2])

        # I do this to find the index of the min lat...
        if test_lat_ltoh != []:
          test_lat_ltoh = np.array(test_lat_ltoh)
          test_lon_ltoh = np.array(test_lon_ltoh)
          var_eq_lat1 = test_lat_ltoh[np.where(test_lat_ltoh ==
                                               min(test_lat_ltoh))]
          var_eq_lon1 = test_lon_ltoh[np.where(test_lat_ltoh ==
                                               min(test_lat_ltoh))]
          eq_bnd_lats.append(var_eq_lat1[0])
          eq_bnd_lons.append(var_eq_lon1[0])

        if test_lat_htol != []:
            test_lat_htol = np.array(test_lat_htol)
            test_lon_htol = np.array(test_lon_htol)
            var_eq_lat2 = test_lat_htol[np.where(test_lat_htol ==
                                                 min(test_lat_htol))]
            var_eq_lon2 = test_lon_htol[np.where(test_lat_htol ==
                                                 min(test_lat_htol))]
            eq_bnd_lats.append(var_eq_lat2[0])
            eq_bnd_lons.append(var_eq_lon2[0])

        if test_lat_ltohp != []:
            test_lat_ltohp = np.array(test_lat_ltohp)
            test_lon_ltohp = np.array(test_lon_ltohp)
            var_eq_latP1 = test_lat_ltohp[np.where(test_lat_ltohp ==
                                                   min(test_lat_ltohp))]
            var_eq_lonP1 = test_lon_ltohp[np.where(test_lat_ltohp ==
                                                   min(test_lat_ltohp))]
            if var_eq_latP1[0] > 64.0:
                po_bnd_lats.append(var_eq_latP1[0])
                po_bnd_lons.append(var_eq_lonP1[0])

        if test_lat_htolp != []:
            test_lat_htolp = np.array(test_lat_htolp)
            test_lon_htolp = np.array(test_lon_htolp)
            var_eq_latP2 = test_lat_htolp[np.where(test_lat_htolp ==
                                                   min(test_lat_htolp))]
            var_eq_lonP2 = test_lon_htolp[np.where(test_lat_htolp ==
                                                   min(test_lat_htolp))]
            if var_eq_latP2[0] > 64:
                po_bnd_lats.append(var_eq_latP2[0])
                po_bnd_lons.append(var_eq_lonP2[0])

    eq_bnd_lats = np.array(eq_bnd_lats)
    eq_bnd_lons = np.array(eq_bnd_lons)
    po_bnd_lats = np.array(po_bnd_lats)
    po_bnd_lons = np.array(po_bnd_lons)

    # Now we do the fitting part.  We start by establishing a target function.
    # The error is the distance to the target function.
    fitfunc = lambda p, x: p[0] + p[1] * np.cos(np.radians(x) + p[2])
    errfunc = lambda p, x, y: fitfunc(p, x) - y

    # Initial guess for the parameters
    # Equatorward boundary
    p0_eq = [1.0, 1.0, 1.0]
    p1_eq, success_eq = optimize.leastsq(errfunc, p0_eq[:], args=(eq_bnd_lons,
                                                                  eq_bnd_lats))
    if pol_bnd == True :
        p0_pol = [ 1., 1., 1.]
        p1_pol, success_pol = optimize.leastsq(errfunc, p0_pol[:],
                                               args=(po_bnd_lons, po_bnd_lats))

    all_plot_lons = np.linspace(0.0, 360.0, 25.0)
    all_plot_lons[-1] = 0.0
    eq_plot_lats = []
    if pol_bnd == True :
        po_plot_lats = []
    for xx in all_plot_lons :
        if equ_bnd == True :
            eq_plot_lats.append(p1_eq[0] + p1_eq[1] * np.cos(np.radians(xx)
                                                             + p1_eq[2]))
        if pol_bnd == True :
            po_plot_lats.append(p1_pol[0] + p1_pol[1]*np.cos(np.radians(xx)
                                                             + p1_pol[2]))

    x_eq, y_eq = basemap_obj(all_plot_lons, eq_plot_lats)
    bpltpoes = basemap_obj.plot(x_eq, y_eq, zorder=7.0, color='b')

    if pol_bnd == True :
        x_pol, y_pol = basemap_obj(all_plot_lons, po_plot_lats)
        bpltpoes = basemap_obj.plot(x_pol, y_pol, zorder=7.0, color='r')

    return
