# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
.. module:: radInfoIo
   :synopsis: read/write radar information
.. moduleauthor:: Sebastien
*********************
**Module**: pydarn.radar.radInfoIo
*********************
Input/Output for radar information (location, boresight, interferometer
position...) is read from a local dblite database (radar.db). The functions
in this module provide tools to populate/update said database (from hdw.dat
and radar.dat files), or simply read hdw.dat and radar.dat files. It also
provide a function to manually update the local radar.db database using the
remote db database (requires an active internet connection).

**Classes**:
        * :class:`pydarn.radar.radInfoIo.updateRadars`
**Functions**:
        * :func:`pydarn.radar.radInfoIo.hdwRead`: reads hdw.dat files
        * :func:`pydarn.radar.radInfoIo.radarRead`: reads radar.dat file
"""


# *************************************************************
def radarRead(path=None):
    """Reads radar.dat file

    **Args***
        * [**path**] (str): path to radar.dat file; defaults to RST
                     environment variable SD_RADAR
        **Returns**:
        * A dictionary with keys matching the radar.dat variables
          each containing values of length #radars.

        **Example**:
                ::

            radars = pydarn.radar.radarRead()

    Written by Sebastien, 2012-09
    """
    import shlex
    import os
    from datetime import datetime
    from davitpy.utils import parseDate

    # Read file
    if path:
        pathOpen = os.path.join(path, 'radar.dat')
    else:
        pathOpen = os.getenv('SD_RADAR')

    try:
        file_net = open(pathOpen, 'r')
        data = file_net.readlines()
        file_net.close()
    except:
        print('radarRead: cannot read {}'.format(pathOpen))
        print('')
        txt = 'You may be getting this error because your computer ' \
              'cannot contact an appropriate internet server to get ' \
              'the latest radar.dat information.  You can can use a ' \
              'local file instead by setting the SD_RADAR environment ' \
              'variable to the location of a local copy of radar.dat.'
        print(txt)
        print('')
        txt = 'Example, you might add a similar line to your .bashrc:'
        print(txt)
        txt = 'export SD_RADAR=/home/username/tables/radar.dat'
        print(txt)
        print('')
        txt = 'Also, make sure your SD_HDWPATH also points to the location ' \
              'of your hdw.dat files.'
        print(txt)
        txt = 'You can get the latest hdw.dat files from ' \
              'https://github.com/vtsuperdarn/hdw.dat'
        print(txt)
        txt = 'Example, you might add a similar line to your .bashrc:'
        print(txt)
        txt = 'export SD_HDWPATH=/home/username/tables/hdw.dat/'
        print(txt)
        print('')
        return None

    # Initialize placeholder dictionary of lists
    radarF = {}
    radarF['id'] = []
    radarF['status'] = []
    radarF['stTime'] = []
    radarF['edTime'] = []
    radarF['name'] = []
    radarF['operator'] = []
    radarF['hdwfname'] = []
    radarF['code'] = []
    radarF['cnum'] = []
    # Fill dictionary with each radar.dat lines
    for ldat in data:
        ldat = shlex.split(ldat)
        if len(ldat) == 0: continue
        radarF['id'].append(int(ldat[0]))
        radarF['status'].append(int(ldat[1]))
        tmpDate = parseDate(int(ldat[2]))
        radarF['stTime'].append(datetime(tmpDate[0], tmpDate[1], tmpDate[2]))
        tmpDate = parseDate(int(ldat[3]))
        radarF['edTime'].append(datetime(tmpDate[0], tmpDate[1], tmpDate[2]))
        radarF['name'].append(ldat[4])
        radarF['operator'].append(ldat[5])
        radarF['hdwfname'].append(ldat[6])
        radarF['code'].append(ldat[7:])
        radarF['cnum'].append(len(ldat[7:]))

    # Return
    return radarF


# *************************************************************
def hdwRead(fname, path=None):
    """Reads hdw.dat files for given radar specified by its hdw.dat file name

    **Args**:
        * **fname** (str): hdw.dat file name
        * [**path**] (str): path to hdw.dat file; defaults to RST environment
                     variable SD_HDWPATH
    **Returns**:
        * A dictionary with keys matching the hdw.dat variables each
          containing values of length #site updates.

    **Example**:
        ::

            hdw = pydarn.radar.hdwRead('hdw.dat.bks')

    Written by Sebastien, 2012-09
    """
    import os
    import sys
    import shlex
    from datetime import datetime
    from davitpy.utils import timeYrsecToDate

    # Read hardware file FNAME
    # Read file
    if path:
        pathOpen = os.path.join(path, fname)
    else:
        pathOpen = os.getenv('SD_RADAR')
        pathOpen = os.path.join(str(os.getenv('SD_HDWPATH')), fname)

    try:
        file_hdw = open(pathOpen, 'r')
        data = file_hdw.readlines()
        file_hdw.close()
    except:
        print('hdwRead: cannot read {}'.format(pathOpen))
        print('')
        txt = 'You may be getting this error because your computer cannot ' \
              'contact an appropriate internet server to get the latest ' \
              'hdw.dat information.  You can can use a local file instead ' \
              'by setting the SD_HDWPATH environment variable to the ' \
              'location of the local hdw.dat path.'
        print(txt)
        txt = 'You can get the latest hdw.dat files from ' \
              'https://github.com/vtsuperdarn/hdw.dat'
        print(txt)
        print('')
        txt = 'Example, you might add a similar line to your .bashrc:'
        print(txt)
        txt = 'export SD_HDWPATH=/home/username/tables/hdw.dat/'
        print(txt)
        print('')
        return

    # Site placeholder
    siteF = {}
    siteF['tval'] = []
    siteF['geolat'] = []
    siteF['geolon'] = []
    siteF['alt'] = []
    siteF['boresite'] = []
    siteF['bmsep'] = []
    siteF['vdir'] = []
    siteF['atten'] = []
    siteF['tdiff'] = []
    siteF['phidiff'] = []
    siteF['interfer'] = []
    siteF['recrise'] = []
    siteF['maxatten'] = []
    siteF['maxgate'] = []
    siteF['maxbeam'] = []
    # Read line by line, ignoring comments
    for ldat in data:
        ldat = shlex.split(ldat)
        if len(ldat) == 0: continue
        if ldat[0] == '#': continue
        if int(ldat[1]) == 2999:
            siteF['tval'].append(-1)
        else:
            siteF['tval'].append(timeYrsecToDate(int(ldat[2]), int(ldat[1])))
        siteF['geolat'].append(float(ldat[3]))
        siteF['geolon'].append(float(ldat[4]))
        siteF['alt'].append(float(ldat[5]))
        siteF['boresite'].append(float(ldat[6]))
        siteF['bmsep'].append(float(ldat[7]))
        siteF['vdir'].append(float(ldat[8]))
        siteF['atten'].append(float(ldat[9]))
        siteF['tdiff'].append(float(ldat[10]))
        siteF['phidiff'].append(float(ldat[11]))
        siteF['interfer'].append([float(ldat[12]), float(ldat[13]),
                                 float(ldat[14])])
        siteF['recrise'].append(float(ldat[15]))
        siteF['maxatten'].append(int(ldat[16]))
        siteF['maxgate'].append(int(ldat[17]))
        siteF['maxbeam'].append(int(ldat[18]))

    # Return
    return siteF


# *************************************************************
class updateRadars(object):
    """Update local radar.sqlite from remote db database, or from local files
       if the database cannot be reached.  Currently, the remote database is
       housed on the VT servers.

    **Members**:
        * **sql_path** (str): path to sqlite file
        * **sql_file** (str): sqlite file name
    **Methods**:
        * :func:`updateRadars.sqlInit`
        * :func:`updateRadars.sqlUpdate`
        * :func:`updateRadars.dbConnect`

    **Example**:
        ::

            obj = pydarn.radar.updateRadars()

    Written by Sebastien, 2013-05
    """

    def __init__(self):
        """Default class constructor

        **Belongs to**: :class:`updateRadars`

        **Args**:
            * **None**
        **Returns**:
            * **updateRadars** (obj)
        """

        import os
        import sys
        from datetime import datetime
        from numpy import dtype
        import sqlite3 as lite
        import davitpy

        # Date format
        dtfmt = '%Y-%m-%d %H:%M:%S'
        dttest = datetime.utcnow().strftime(dtfmt)
        # File path
        try:
            self.sql_path = davitpy.rcParams['DAVIT_TMPDIR']
        except:
            try:  self.sql_path = os.environ['HOME']
            except: self.sql_path = os.path.dirname(os.path.abspath(__file__))
        self.sql_file = '.radars.sqlite'
        # MongoDB server
        self.db_name = 'radarInfo'
        try:
            self.db_user = davitpy.rcParams['DBREADUSER']
        except KeyError:
            self.db_user = ""
        try:
            self.db_pswd = davitpy.rcParams['DBREADPASS']
        except KeyError:
            self.db_pswd = ""
        try:
            self.db_host = davitpy.rcParams['SDDB']
        except KeyError:
            self.db_host = ""

        # Declare custom data types
        self.dtype_rad = ["id INT",
                          "cnum INT",
                          "code BLOB",
                          "name TEXT",
                          "operator TEXT",
                          "hdwfname TEXT",
                          "status INT",
                          "stTime TIMESTAMP",
                          "edTime TIMESTAMP",
                          "snum INT"]
        self.dtype_hdw = ["id INT",
                          "tval TIMESTAMP",
                          "geolat REAL",
                          "geolon REAL",
                          "alt REAL",
                          "boresite REAL",
                          "bmsep REAL",
                          "vdir INT",
                          "tdiff REAL",
                          "phidiff REAL",
                          "recrise REAL",
                          "atten REAL",
                          "maxatten REAL",
                          "maxgate INT",
                          "maxbeam INT",
                          "interfer BLOB"]
        self.dtype_inf = ["var TEXT",
                          "description TEXT"]

        isUp = self.sqlUpdate()

        if isUp:
            print "Radars information has been updated."

    def dbConnect(self):
        """Try to establish a connection to remote db database

        **Belongs to**: :class:`updateRadars`

        **Args**:
            * **None**
        **Returns**:
            * **isConnected** (bool): True if the connection was successfull
        """
        from pymongo import MongoClient
        import sys

        uri = 'mongodb://{0}:{1}@{2}/{3}'.format(self.db_user, self.db_pswd,
                                                 self.db_host, self.db_name)

        try:
            conn = MongoClient(uri)
            dba = conn[self.db_name]
        except:
            print 'Could not connect to remote DB: ', sys.exc_info()[0]
            dba = False

        if dba:
            try:
                colSel = lambda colName: dba[colName].find()

                self.db_select = {'rad': colSel("radars"),
                                  'hdw': colSel("hdw"),
                                  'inf': colSel("metadata")}
                return True
            except:
                print 'Could not get data from remote DB: ', sys.exc_info()[0]
                print('Could not update .radars.sqlite file with hdw.dat info')
                return False
        else:
            result = self.__readFromFiles()
            if not result:
                print('Could not update .radars.sqlite file with hdw.dat info')
            return result

    def sqlInit(self):
        """Initialize sqlite file (only if file does not already exists)

        **Belongs to**: :class:`updateRadars`

        **Args**:
            * **None**
        **Returns**:
            * **isConnected** (bool): True if sqlite file already exists or was
                              successfully created
        """
        import sqlite3 as lite
        import os

        fname = os.path.join(self.sql_path, self.sql_file)
        try:
            with lite.connect(fname) as conn: pass
            return True
        except lite.Error, e:
            print "sqlInit() Error %s: %s" % (e.args[0], fname)
            return False

    def sqlUpdate(self):
        """Update sqlite file with provided db selections (if possible).

        **Belongs to**: :class:`updateRadars`

        **Args**:
            * **None**
        **Returns**:
            * **isConnected** (bool): True if sqlite file update
                              was successfull
        """
        import os
        import sys
        import sqlite3 as lite

        # Try to connect to DB
        conn = self.dbConnect()
        if not conn: return False

        # Try to open sqlite file
        isInit = self.sqlInit()
        if not isInit: return False

        # Format BD output for sqlite input
        arr_rad = self.__makeInsDict(self.db_select['rad'], self.dtype_rad)
        arr_hdw = self.__makeInsDict(self.db_select['hdw'], self.dtype_hdw)
        arr_inf = self.__makeInsDict(self.db_select['inf'], self.dtype_inf)

        fname = os.path.join(self.sql_path, self.sql_file)

        with lite.connect(fname, detect_types=lite.PARSE_DECLTYPES) as conn:
            cur = conn.cursor()

            # Drop tables if they exists
            cur.execute("DROP TABLE IF EXISTS rad")
            cur.execute("DROP TABLE IF EXISTS hdw")
            cur.execute("DROP TABLE IF EXISTS inf")

            # Create new tables
            cur.execute("CREATE TABLE rad (%s)" % ', '.join(self.dtype_rad))
            cur.execute("CREATE TABLE hdw (%s)" % ', '.join(self.dtype_hdw))
            cur.execute("CREATE TABLE inf (%s)" % ', '.join(self.dtype_inf))

            cur.executemany("INSERT INTO rad VALUES(%s)" % ', '.join(['?'] *
                            len(self.dtype_rad)), arr_rad)
            cur.executemany("INSERT INTO hdw VALUES(%s)" % ', '.join(['?'] *
                            len(self.dtype_hdw)), arr_hdw)
            cur.executemany("INSERT INTO inf VALUES(%s)" % ', '.join(['?'] *
                            len(self.dtype_inf)), arr_inf)

        return True

    def __makeInsDict(self, sel, dtype):
        """Handles BLOB datatype for arrays before insertion into sqlite DB.
        This method is hidden and used internatlly by :func:`sqlUpdate`.

        **Belongs to**: :class:`updateRadars`

        **Args**:
            * **sel** (pymongo Ptr)
            * [**dtype**] (str): a list of 'name TYPE' pairsto be inserted into
                          sqlite DB
        **Returns**:
            * **arr** a list of lists of DB entries
        """
        import pickle

        arr = []
        for ir, row in enumerate(sel):
            entry = []
            for typ in dtype:
                k, d = typ.split()
                if d == 'BLOB':
                    v = pickle.dumps(row[k])
                else:
                    v = row[k]
                entry.append(v)
            arr.append(entry)

        return arr

    def __readFromFiles(self):
        """Read hdw.dat and radar.dat into a select-like dictionary from local files
        """
        from datetime import datetime

        # Build radar and hdw dictionaries
        radars = []
        hdw = []
        radarF = radarRead()
        if radarF is None: return False

        nradar = len(radarF['id'])
        for irad in xrange(nradar):
            radars.append({"id": radarF['id'][irad],
                           "cnum": radarF['cnum'][irad],
                           "code": radarF['code'][irad],
                           "name": radarF['name'][irad],
                           "operator": radarF['operator'][irad],
                           "hdwfname": radarF['hdwfname'][irad],
                           "status": radarF['status'][irad],
                           "stTime": radarF['stTime'][irad],
                           "edTime": radarF['edTime'][irad],
                           "snum": 0})
            siteF = hdwRead(radarF['hdwfname'][irad])
            if not siteF: continue
            tsnum = 0
            for isit in xrange(len(siteF['tval'])):
                if siteF['tval'][isit] == 0: continue
                tval = datetime(3000, 1, 1) if siteF['tval'][isit] == -1 else siteF['tval'][isit]
                hdw.append({"id": radarF['id'][irad],
                            "tval": tval,
                            "geolat": siteF['geolat'][isit],
                            "geolon": siteF['geolon'][isit],
                            "alt": siteF['alt'][isit],
                            "boresite": siteF['boresite'][isit],
                            "bmsep": siteF['bmsep'][isit],
                            "vdir": siteF['vdir'][isit],
                            "tdiff": siteF['tdiff'][isit],
                            "phidiff": siteF['phidiff'][isit],
                            "recrise": siteF['recrise'][isit],
                            "atten": siteF['atten'][isit],
                            "maxatten": siteF['maxatten'][isit],
                            "maxgate": siteF['maxgate'][isit],
                            "maxbeam": siteF['maxbeam'][isit],
                            "interfer": siteF['interfer'][isit]})
                tsnum += 1
            radars[-1]["snum"] = tsnum

        self.db_select = {'rad': radars, 'hdw': hdw,
                          'inf': [{"var": '', "description": ''}]}

        return True
