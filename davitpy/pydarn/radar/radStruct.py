# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
Module
------
pydarn.radar.radStruct
   Load and browse radar information

Classes
-------
pydarn.radar.radStruct.network
    radar.dat and hdw.dat information from all the radars
pydarn.radar.radStruct.radar
    radar.dat and hdw.dat information
pydarn.radar.radStruct.site
    hdw.dat information

Moduleauthor
------------
Sebastien

"""
import logging


class network(object):
    """ This class stores information from all radars according to their
    hdw.dat and radar.dat files.  This information is read from the
    radar.sqlite files provided with the pydarn module.

    Attributes
    ----------
    nradar : int
        number of radars in class
    radars : list
        list of :class:`radar` objects

    Methods
    -------
    network.getRadarById
    network.getRadarByName
    network.getRadarByCode
    network.getRadarsByPosition
    network.getAllCodes

    Example
    -------
        obj = pydarn.radar.network()

    Note
    ----
        To add your own radar information to this class you can use the
        :func:`radInfoIO.radarRead` and the :func:`radInfoIO.hdwRead`. Then,
        manually append the output of these functions to this object.

    written by Sebastien, 2012-08

    """
    def __init__(self):
        import sqlite3 as lite
        import os
        import davitpy

        self.radars = []
        # Get DB name
        try:
            rad_path = davitpy.rcParams['DAVIT_TMPDIR']
        except:
            try:
                rad_path = os.environ['HOME']
            except:
                rad_path = os.path.dirname(os.path.abspath(__file__))
        dbname = os.path.join(rad_path, '.radars.sqlite')

        if not os.path.isfile(dbname):
            logging.error("%s not found", dbname)
            return

        with lite.connect(dbname) as conn:
            cur = conn.cursor()
            cur.execute("select count() from rad")
            self.nradar = cur.fetchone()[0]
            cur.execute("select id from rad")
            rows = cur.fetchall()

        for row in rows:
            self.radars.append(radar())
            self.radars[-1].fillFromSqlite(dbname, row[0])

    def __len__(self):
        """Object length (number of radars)

        Belongs to
        ----------
        class : network

        Parameters
        ----------
        None

        Returns
        -------
        number of radars : int

        Example
        -------
            len(obj)

        written by Sebastien, 2012-08

        """
        return self.nradar

    def __str__(self):
        """Object string representation

        Belongs to
        ----------
        class : network

        Parameters
        ----------
        None

        Returns
        -------
        a string : str

        Example
        -------
            print(obj)

        written by Sebastien, 2012-08

        """
        outstring = "Network information object: \
                \n\tTotal radars: {:d}".format(self.nradar)
        for irad in range(self.nradar):
            if self.radars[irad].status == 1:
                status = 'active'
            elif self.radars[irad].status == -1:
                status = 'offline'
            elif self.radars[irad].status == 0:
                status = 'planned'
            else:
                status = '{}'.format(self.radars[irad].status)
            hemi = 'South' if self.radars[
                irad].sites[0].geolat < 0 else 'North'
            outstring += '\n\t\t({}) - [{}][{}] {} ({})'\
                .format(hemi, self.radars[irad].id,
                        self.radars[irad].code[0],
                        self.radars[irad].name, status)
        return outstring

    def getRadarById(self, id):
        """Get a specific radar from its ID

        Belongs to
        ----------
        class : network

        Parameters
        ----------
        id : int
            radar ID

        Returns
        -------
        radar : radar class object

        Example
        -------
            # To get the Blackstone radar by its ID
            radar = obj.getRadarById(33)

        written by Sebastien, 2012-08

        """
        radar = self.getRadarBy(id, by='id')
        return radar

    def getRadarByName(self, name):
        """Get a specific radar from its name

        Belongs to
        ----------
        class : network

        Parameters
        ----------
        name : str
            radar full name

        Returns
        -------
        radar : radar class object

        Example
        -------
            # To get the Blackstone radar by its name
            radar = obj.getRadarById('Blackstone')

        written by Sebastien, 2012-08

        """
        radar = self.getRadarBy(name, by='name')
        return radar

    def getRadarByCode(self, code):
        """Get a specific radar from its 3-letter code

        Belongs to
        ----------
        class : network

        Parameters
        ----------
        code : str
            radar 3-letter code

        Returns
        -------
        radar : radar class object

        Example
        -------
            # To get the Blackstone radar by its code
            radar = obj.getRadarById('bks')

        written by Sebastien, 2012-08

        """
        radar = self.getRadarBy(code, by='code')
        return radar

    def getRadarBy(self, radN, by):
        """Get a specific radar from its name/code/id
        This method is the underlying function behing getRadarByCode,
        getRadarByName and getRadarById

        Belongs to
        ----------
        class : network

        Parameters
        ----------
        radN : str/int
            radar identifier (either code, name or id)
        by : str
            look-up method: 'code', 'name', 'id'

        Returns
        -------
        radar : radar class object

        written by Sebastien, 2012-08

        """
        found = False
        for irad in xrange(self.nradar):
            if by.lower() == 'code':
                for ic in xrange(self.radars[irad].cnum):
                    if self.radars[irad].code[ic].lower() == radN.lower():
                        found = True
                        return self.radars[irad]
                        break
            elif by.lower() == 'name':
                if self.radars[irad].name.lower() == radN.lower():
                    found = True
                    return self.radars[irad]
                    break
            elif by.lower() == 'id':
                if self.radars[irad].id == radN:
                    found = True
                    return self.radars[irad]
                    break
            else:
                logging.error('getRadarBy: invalid method by {}'.format(by))
                break
        if not found:
            logging.error(
                'getRadarBy: could not find radar {}: {}'.format(by, radN))
            return found

    def getRadarsByPosition(self, lat, lon, alt, distMax=4000., datetime=None):
        """Get a list of radars able to see a given point on Earth

        Belongs to
        ----------
        class : network

        Parameters
        ----------
        lat
            latitude of given point in geographic coordinates
        lon
            longitude of given point in geographic coordinates
        alt
            altitude of point above the Earth's surface in km
        distMax
            maximum distance of given point from radar
        datetime : Optional[datetime.datetime object]
            python datetime object (defaults to today)

        Returns
        -------
        dict
            A dictionnary with keys:
            radars : a list of radar objects (:class:`radar`)
            dist: a list of distance from radar to given point (1 perradar)
            beam: a list of beams (1 per radar) seeing the given point

        Example
        -------
            radars = obj.getRadarsByPosition(67., 134., 300.)

        written by Sebastien, 2012-08

        """
        from datetime import datetime as dt
        from davitpy.utils import geoPack as geo
        import numpy as np

        if not datetime:
            datetime = dt.utcnow()

        found = False
        out = {'radars': [], 'dist': [], 'beam': []}

        for irad in xrange(self.nradar):
            site = self.radars[irad].getSiteByDate(datetime)
            # Skip if radar inactive at date
            if (not site) and (self.radars[irad].status != 1):
                continue
            if not (self.radars[irad].stTime <= datetime <=
                    self.radars[irad].edTime):
                        continue
            # Skip if radar in other hemisphere
            if site.geolat * lat < 0.:
                continue
            dist_pnt = geo.calcDistPnt(site.geolat, site.geolon, site.alt,
                                       distLat=lat, distLon=lon, distAlt=300.)
            # Skip if radar too far
            if dist_pnt['dist'] > distMax:
                continue
            # minAz = (site.boresite % 360.)-abs(site.bmsep)*site.maxbeam/2
            # maxAz = (site.boresite % 360.)+abs(site.bmsep)*site.maxbeam/2
            ext_fov = abs(site.bmsep) * site.maxbeam / 2
            pt_bo = [np.cos(np.radians(site.boresite)),
                     np.sin(np.radians(site.boresite))]
            pt_az = [np.cos(np.radians(dist_pnt['az'])),
                     np.sin(np.radians(dist_pnt['az']))]
            delt_az = np.degrees(np.arccos(np.dot(pt_bo, pt_az)))
            # Skip if out of azimuth range
            if not abs(delt_az) <= ext_fov:
                continue
            if np.sign(np.cross(pt_bo, pt_az)) >= 0:
                beam = int(site.maxbeam / 2 + round(delt_az / site.bmsep) - 1)
            else:
                beam = int(site.maxbeam / 2 - round(delt_az / site.bmsep))
            # Update output
            found = True
            out['radars'].append(self.radars[irad])
            out['dist'].append(dist_pnt['dist'])
            out['beam'].append(beam)

        if found:
            return out
        else:
            return found

    def getAllCodes(self, datetime=None, hemi=None):
        """Get a list of all active radar codes

        Belongs to
        ----------
        class : network

        Parameters
        ----------
        datetime : Optional[python datetime object]
            defaults to today
        hemi : Optional[str]
            'north' or 'south', defaults to both

        Returns
        -------
        codes : list
            A list of 3-letter codes

        written by Sebastien, 2012-08

        """
        from datetime import datetime as dt

        if not datetime:
            datetime = dt.utcnow()

        codes = []
        for irad in xrange(self.nradar):
            tcod = self.radars[irad].getSiteByDate(datetime)
            if((tcod) and (self.radars[irad].status == 1) and
               (self.radars[irad].stTime <= datetime <=
                    self.radars[irad].edTime)):
                if((hemi is None) or
                   (hemi.lower() == 'south' and tcod.geolat < 0) or
                   (hemi.lower() == 'north' and tcod.geolat >= 0)):
                    codes.append(self.radars[irad].code[0])

        return codes


# *************************************************************
class radar(object):

    """ Reads radar.dat file and hdw.dat for a given radar and fills a radar
    structure

    Parameters
    ----------
    code : Optional[str]
        3-letter radar code
    radId : Optional[int]
        radar ID

    Note
    ----
        you should provide either **code** OR **radId**, not both

    Attributes
    ----------
    id : int
        radar ID
    status : int
        radar status (active, inactive or planned)
    cnum : int
        number of code names (usually 2, a 3-letter and 1-letter)
    code : Optional[list]
        list of radar codes (usually 2, a 3-letter and 1-letter)
    name : str
        radar name
    operator : str
        PI institution
    hdwfname : str
        hdw.dat file name
    stTime : datetime.datetime
        date of first lights
    edTime : datetime.datetime
        last day of operations
    snum : int
        number of site objects (i.e. number of updates to the hdw.dat)
    sites : list
        list of :class:`site` objects

    Methods
    -------
    radar.fillFromSqlite
    radar.getSiteByDate

    Example
    -------
        obj = pydarn.radar.radar()

    written by Sebastien, 2012-08

    """
    # __slots__ = ('id', 'status', 'cnum', 'code', 'name', 'operator',
    #              'hdwfname', 'stTime', 'edTime', 'snum', 'site')

    def __init__(self, code=None, radId=None):
        import sqlite3 as lite
        import pickle
        import os
        import davitpy

        self.id = 0
        self.status = 0
        self.cnum = 0
        self.code = []
        self.name = u''
        self.operator = u''
        self.hdwfname = u''
        self.stTime = 0.0
        self.edTime = 0.0
        self.snum = 0
        self.sites = [site()]

        # If a radar is requested...
        if code or radId:
            try:
                rad_path = davitpy.rcParams['DAVIT_TMPDIR']
            except:
                try:
                    rad_path = os.environ['HOME']
                except:
                    rad_path = os.path.dirname(os.path.abspath(__file__))
            dbname = os.path.join(rad_path, '.radars.sqlite')

            if not os.path.isfile(dbname):
                logging.error("%s not found", dbname)
                return

            # if the radar code was provided, look for corresponding id
            if code:
                with lite.connect(dbname) as conn:
                    cur = conn.cursor()
                    cur.execute('SELECT id,code FROM rad')
                    rows = cur.fetchall()
                for row in rows:
                    if code in pickle.loads(row[1].encode('ascii')):
                        radId = row[0]

            self.fillFromSqlite(dbname, radId)

    def fillFromSqlite(self, dbname, radId):
        """fill radar structure from sqlite DB

        Belongs to
        ----------
        class : radar

        Parameters
        ----------
        dbname : str
            sqlite database path/name
        radID : int
            radar ID

        Returns
        -------
        None

        written by Sebastien, 2013-02

        """
        import sqlite3 as lite
        import pickle
        import os

        if not os.path.isfile(dbname):
            logging.error("%s not found", dbname)
            return

        with lite.connect(dbname, detect_types=lite.PARSE_DECLTYPES) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM rad WHERE id=?', (radId,))

            row = cur.fetchone()
            if not row:
                logging.error('Radar not found in DB: {}'.format(radId))
                return

            self.id = row[0]
            self.cnum = row[1]
            self.code = pickle.loads(row[2].encode('ascii'))
            self.name = row[3]
            self.operator = row[4]
            self.hdwfname = row[5]
            self.status = row[6]
            self.stTime = row[7]
            self.edTime = row[8]
            self.snum = row[9]
            for ist in range(self.snum):
                self.sites[ist].fillFromSqlite(dbname, radId, ind=ist)
                self.sites.append(site())
            del self.sites[-1]

    def __len__(self):
        """Object length (number of site updates)"""
        return self.snum

    def __str__(self):
        """Object string representation

        Belongs to
        ----------
        class : radar

        Parameters
        ----------
        None

        Returns
        -------
        a string : str

        Example
        -------
            print(obj)

        written by Sebastien, 2012-08

        """
        outstring = 'id: {0} \
                    \nstatus: {1} \
                    \ncnum: {2} \
                    \ncode: {3} \
                    \nname: {4} \
                    \noperator: {5} \
                    \nhdwfname: {6} \
                    \nstTime: {7} \
                    \nedTime: {8} \
                    \nsnum: {9} \
                    \nsites: {10} elements'.format(self.id, self.status,
                                                   self.cnum,
                                                   [c for c in self.code],
                                                   self.name, self.operator,
                                                   self.hdwfname,
                                                   self.stTime.date(),
                                                   self.edTime.date(),
                                                   self.snum, len(self.sites))
        return outstring

    def getSiteByDate(self, datetime):
        """Get a specific radar site at a given date

        Belongs to
        ----------
        class : radar

        Parameters
        ----------
        datetime : datetime.datetime

        Returns
        -------
        site : site class object

        Example
        -------
            # To get the Blackstone radar configuration today
            site = obj.getSiteByDate(datetime.datetime.utcnow())

        written by Sebastien, 2012-08

        """
        found = False
        for isit in range(self.snum):
            if self.sites[isit].tval == -1:
                found = True
                return self.sites[isit]
                break
            elif self.sites[isit].tval >= datetime:
                found = True
                return self.sites[isit]
        if not found:
            estr = 'getSiteByDate: could not get SITE for date '
            logging.error('{:s}{}'.format(estr, datetime))
            return found


# *************************************************************
class site(object):

    """Reads hdw.dat for a given radar and fills a SITE structure

    Parameters
    ----------
    radId : Optional[int]
        radar ID
    code : Optional[str]
        3-letter radar code
    dt : Optional[datetime.datetime]
        date and time of radar configurationation

    Note
    ----
        you should provide either **code** OR **radId**, not both

    Attributes
    ---------
    tval : datetime.datetime
        last date and time operating with these parameters
    geolat : float
        main array latitude [deg]
    geolon : float
        main array longitude [deg]
    alt : float
        main array altitude [km]
    boresite : float
        boresight azimuth [deg]
    bmsep : float
        beam separation [deg]
    vdir : int
        velocity sign
    atten : float
        Analog Rx attenuator step [dB]
    tdiff : float
        Propagation time from interferometer array antenna to
        phasing matrix [us]
    phidiff : float
        phase sign for interferometric calculations
    interfer : list
        Interferometer offset [x, y, z]
    recrise : float
        Analog Rx rise time [us]
    maxatten : int
        maximum number of analog attenuation stages
    maxgate : int
        maximum number of range gates (assuming 45km gates)
    maxbeam : int
        maximum number of beams

    Methods
    -------
    site.fillFromSqlite
    site.beamToAzim
    site.azimToBeam

    Example
    -------
        obj = pydarn.radar.site()

    written by Sebastien, 2012-08

    """

    def __init__(self, radId=None, code=None, dt=None):
        import sqlite3 as lite
        import pickle
        import os
        import davitpy
        import datetime

        # Lets do some type checks on the input
        if not isinstance(radId, int) and radId is not None:
            vtype = type(radId)
            logging.error('radId must be an integer, type found is %s', vtype)
            return

        if not isinstance(code, str) and code is not None:
            vtype = type(code)
            logging.error('code must be a string, type found is %s', vtype)
            return

        if code is not None and radId is not None:
            logging.warning('Both code and radId have been set, where only'
                            ' one should be set.')
            logging.warning('Using code %s', code)

        if dt is not None and not isinstance(dt, datetime.datetime):
            vtype = type(dt)
            logging.error('dt must be a datetime object, type found'
                          ' is %s', vtype)
            return

        self.tval = 0.0
        self.geolat = 0.0
        self.geolon = 0.0
        self.alt = 0.0
        self.boresite = 0.0
        self.bmsep = 0.0
        self.vdir = 0
        self.atten = 0.0
        self.tdiff = 0.0
        self.phidiff = 0.0
        self.interfer = [0.0, 0.0, 0.0]
        self.recrise = 0.0
        self.maxatten = 0
        self.maxgate = 0
        self.maxbeam = 0
        if radId or code:
            try:
                rad_path = davitpy.rcParams['DAVIT_TMPDIR']
            except:
                try:
                    rad_path = os.environ['HOME']
                except:
                    rad_path = os.path.dirname(os.path.abspath(__file__))
            dbname = os.path.join(rad_path, '.radars.sqlite')

            if not os.path.isfile(dbname):
                logging.error("%s not found", dbname)
                return

            # if the radar code was provided, look for corresponding id
            if code:
                with lite.connect(dbname) as conn:
                    cur = conn.cursor()
                    cur.execute('SELECT id,code FROM rad')
                    rows = cur.fetchall()
                for row in rows:
                    if code in pickle.loads(row[1].encode('ascii')):
                        radId = row[0]

            self.fillFromSqlite(dbname, radId, dt=dt)

    def fillFromSqlite(self, dbname, radId, ind=-1, dt=None):
        """fill site structure from sqlite databse

        Belongs to
        ----------
        class : site

        Parameters
        ----------
        dbname : str
            sqlite database path/name
        radID : int
            radar ID
        ind : int
            site index; defaults to most recent configuration
        dt : Optional[datetime.datetime]

        Returns
        -------
        None

        written by Sebastien, 2013-02

        """
        import sqlite3 as lite
        import pickle
        import os

        if not os.path.isfile(dbname):
            logging.error("%s not found", dbname)
            return

        with lite.connect(dbname, detect_types=lite.PARSE_DECLTYPES) as conn:
            cur = conn.cursor()
            command = 'SELECT * FROM hdw WHERE id=? '
            if dt:
                command = '{:s}and tval>=? ORDER BY tval ASC'.format(command)
                cur.execute(command, (radId, dt))
                row = cur.fetchone()
            else:
                command = '{:s}ORDER BY tval ASC'.format(command)
                cur.execute(command, (radId,))
                row = cur.fetchall()[ind]

            self.id = row[0]
            self.tval = row[1]
            self.geolat = row[2]
            self.geolon = row[3]
            self.alt = row[4]
            self.boresite = row[5]
            self.bmsep = row[6]
            self.vdir = row[7]
            self.tdiff = row[8]
            self.phidiff = row[9]
            self.recrise = row[10]
            self.atten = row[11]
            self.maxatten = row[12]
            self.maxgate = row[13]
            self.maxbeam = row[14]
            self.interfer = pickle.loads(row[15].encode('ascii'))

    def __len__(self):
        """Object length"""
        return 1

    def __str__(self):
        """Object string representation"""
        outstring = 'tval: {0} \
                    \ngeolat: {1:5.2f} \
                    \ngeolon: {2:5.2f} \
                    \nalt: {3:6.2f} \
                    \nboresite: {4:5.2f} \
                    \nbmsep: {5:5.2f} \
                    \nvdir: {6} \
                    \natten: {7:5.2f} \
                    \ntdiff: {8:6.4f} \
                    \nphidiff: {9:3.1f} \
                    \ninterfer: [{10:5.2f}, {11:5.2f}, {12:5.2f}] \
                    \nrecrise: {13:5.3f} \
                    \nmaxatten: {14} \
                    \nmaxgate: {15} \
                    \nmaxbeam: {16}'.format(self.tval, self.geolat,
                                            self.geolon, self.alt,
                                            self.boresite, self.bmsep,
                                            self.vdir, self.atten, self.tdiff,
                                            self.phidiff, self.interfer[0],
                                            self.interfer[1], self.interfer[2],
                                            self.recrise, self.maxatten,
                                            self.maxgate, self.maxbeam)
        return outstring

    def beamToAzim(self, beam, fov_dir='front'):
        ''' Get azimuth of given beam

        Parameters
        ----------
        beam : int
            beam number

        Returns
        -------
        azim : float
            beam azimuth

        '''
        phi = ((self.maxbeam - 1) / 2. - beam) * self.bmsep

        if fov_dir is 'back':
            phi = 180.0 - phi

        return self.boresite - phi

    def azimToBeam(self, azim):
        ''' Get azimuth of given beam.  Return a negative beam number (offset by
        one instead of zero) if the azimuth corresponds to the back lobe.
        Return np.nan if the azimuth is not covered by any beam.

        Parameters
        ----------
        azim : float
            beam azimuth [deg. East]

        Returns
        -------
        beam : int
            beam number

        '''
        import numpy as np

        # Assume the azimuth comes from the front lobe
        phi = np.radians(azim - self.boresite)
        delta = np.degrees(np.arctan2(np.sin(phi), np.cos(phi)))
        beam = np.round(delta / self.bmsep + (self.maxbeam - 1) / 2.)

        if beam < 0.0 or beam > self.maxbeam:
            # This azimuth lies outside the front lobe
            phi = np.radians(self.boresite - azim - 180.0)
            delta = np.degrees(np.arctan2(np.sin(phi), np.cos(phi)))
            beam = np.round(delta / self.bmsep + (self.maxbeam - 1) / 2.)

            # Seperate back lobe azimuths from azimuths outside of either
            # field-of-view
            if beam >= 0 and beam < self.maxbeam:
                beam = -np.int_(beam + 1)
            else:
                beam = np.nan
        else:
            beam = np.int_(beam)

        return beam
