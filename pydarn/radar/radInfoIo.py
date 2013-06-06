# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: pydarn.radar.radInfoIo
*********************
Input/Output for radar information (location, boresight, interferometer position...) is 
read from a local dblite database (radar.db). The functions in this module provide tools 
to populate/update said database (from hdw.dat and radar.dat files), or simply read hdw.dat 
and radar.dat files. It also provide a function to manually update the local radar.db database 
using the remote db database (requires an active internet connection).

**Classes**:
	* :class:`pydarn.radar.radInfoIo.updateHdf5`
**Functions**:
	* :func:`pydarn.radar.radInfoIo.hdwRead`: reads hdw.dat files
	* :func:`pydarn.radar.radInfoIo.radarRead`: reads radar.dat file
"""
		

# *************************************************************
def radarRead(path=None):
	"""Reads radar.dat file
	
	**Args**: 
		* [**path**] (str): path to radar.dat file; defaults to RST environment variable SD_RADAR
	**Returns**:
		* A dictionary with keys matching the radar.dat variables each containing values of length #radars.
	**Example**:
		::

			radars = pydarn.radar.radarRead()
			
	written by Sebastien, 2012-09
	"""
	import shlex
	import os, sys
	from datetime import datetime
	from utils import parseDate
	
	# Read file
	try:
		if path: pathOpen = os.path.join(path, 'radar.dat')
		else: pathOpen = os.environ['SD_RADAR']
		file_net = open(pathOpen, 'r')
		data = file_net.readlines()
		file_net.close()
	except:
		print 'radarRead: cannot read {}: {}'.format(pathOpen,
													 sys.exc_info()[0])
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
		radarF['id'].append( int(ldat[0]) )
		radarF['status'].append( int(ldat[1]) )
		tmpDate = parseDate( int(ldat[2]) )
		radarF['stTime'].append( datetime(tmpDate[0], tmpDate[1], tmpDate[2]) )
		tmpDate = parseDate( int(ldat[3]) )
		radarF['edTime'].append( datetime(tmpDate[0], tmpDate[1], tmpDate[2]) )
		radarF['name'].append( ldat[4] )
		radarF['operator'].append( ldat[5] )
		radarF['hdwfname'].append( ldat[6] )
		radarF['code'].append( ldat[7:] )
		radarF['cnum'].append( len(ldat[7:]) )
	
	# Return			
	return radarF


# *************************************************************
def hdwRead(fname, path=None):
	"""Reads hdw.dat files for given radar specified by its hdw.dat file name
	
	**Args**: 
		* **fname** (str): hdw.dat file name
		* [**path**] (str): path to hdw.dat file; defaults to RST environment variable SD_HDWPATH
	**Returns**:
		* A dictionary with keys matching the hdw.dat variables each containing values of length #site updates.
	**Example**:
		::

			hdw = pydarn.radar.hdwRead('hdw.dat.bks')
			
	written by Sebastien, 2012-09
	"""
	import os
	import shlex
	from datetime import datetime
	from utils import timeYrsecToDate
	
	# Read hardware file FNAME
	try:
		if path: pathOpen = os.path.join(path, fname)
		else: pathOpen = os.path.join(os.environ['SD_HDWPATH'], fname)
		file_hdw = open(pathOpen, 'r')
		data = file_hdw.readlines()
		file_hdw.close()
	except:
		print 'hdwRead: cannot read {}: {}'.format(pathOpen, 
												   sys.exc_info()[0])
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
			siteF['tval'].append( -1 )
		else:
			siteF['tval'].append( timeYrsecToDate( int(ldat[2]), int(ldat[1]) ) )
		siteF['geolat'].append( float(ldat[3]) )
		siteF['geolon'].append( float(ldat[4]) )
		siteF['alt'].append( float(ldat[5]) )
		siteF['boresite'].append( float(ldat[6]) )
		siteF['bmsep'].append( float(ldat[7]) )
		siteF['vdir'].append( float(ldat[8]) )
		siteF['atten'].append( float(ldat[9]) )
		siteF['tdiff'].append( float(ldat[10]) )
		siteF['phidiff'].append( float(ldat[11]) )
		siteF['interfer'].append( [float(ldat[12]), float(ldat[13]), float(ldat[14])] )
		siteF['recrise'].append( float(ldat[15]) )
		siteF['maxatten'].append( int(ldat[16]) )
		siteF['maxgate'].append( int(ldat[17]) )
		siteF['maxbeam'].append( int(ldat[18]) )
		
	# Return
	return siteF


# *************************************************************
class updateRadars(object):
    """update local radar.sqlite from remote db database. Currently, the remote 
    database is housed on the VT servers.
    
    **Members**: 
        * **sql_path** (str): path to sqlite file
        * **sql_file** (str): sqlite file name
    **Methods**:
        * :func:`sqlInit`
        * :func:`sqlUpdate`
        * :func:`dbConnect`
    **Example**:
        ::

            obj = pydarn.radar.updateRadars()

    written by Sebastien, 2013-05
    """

    def __init__(self):
        """Default class constructor
        
        **Belongs to**: :class:`updateRadars`
        
        **Args**: 
            * **None**
        **Returns**:
            * **updateRadars** (obj)
        """

        import os, sys
        from datetime import datetime
        from numpy import dtype
        import sqlite3 as lite

        # Date format
        dtfmt = '%Y-%m-%d %H:%M:%S'
        dttest = datetime.utcnow().strftime(dtfmt)
        # File path
        self.sql_path = os.path.dirname( os.path.abspath( __file__ ) )
        self.sql_file = 'radars.sqlite'
        # MongoDB server
        self.db_user = os.environ['DBREADUSER']
        self.db_pswd = os.environ['DBREADPASS']
        self.db_host = os.environ['SDDB']
        self.db_name = 'radarInfo'

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

        self.sqlUpdate()


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
        print self.db_user,self.db_pswd,self.db_host,self.db_name
        uri="mongodb://%s:%s@%s/%s"  % (self.db_user, self.db_pswd, self.db_host, self.db_name)
        print uri
        try:
            conn = MongoClient(uri) 
            dba = conn[self.db_name]
        except:
            print 'Could not connect to remote DB: ', sys.exc_info()[0]
            return False

        try:
            colSel = lambda colName: dba[colName].find()

            self.db_select = {'rad': colSel("radars"), 'hdw': colSel("hdw"), 'inf': colSel("metadata")}
            return True
        except:
            print 'Could not get data from remote DB: ', sys.exc_info()[0]
            return False


    def sqlInit(self):
        """Initialize sqlite file (only if file does not already exists)
        
        **Belongs to**: :class:`updateRadars`
        
        **Args**: 
            * **None**
        **Returns**:
            * **isConnected** (bool): True if sqlite file already exists or was sussessfully created
        """
        import sqlite3 as lite
        import os

        fname = os.path.join(self.sql_path, self.sql_file)
        try:
            with lite.connect(fname) as conn: pass
            return True
        except lite.Error, e:
            print "sqlInit() Error %s:" % e.args[0]
            return False


    def sqlUpdate(self):
        """Update sqlite file with provided db selections (if possible).
        
        **Belongs to**: :class:`updateRadars`
        
        **Args**: 
            * **None**
        **Returns**:
            * **isConnected** (bool): True if sqlite file update was successfull
        """
        import os, sys
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

            cur.executemany("INSERT INTO rad VALUES(%s)" % ', '.join(['?']*len(self.dtype_rad)), 
                arr_rad)
            cur.executemany("INSERT INTO hdw VALUES(%s)" % ', '.join(['?']*len(self.dtype_hdw)), 
                arr_hdw)
            cur.executemany("INSERT INTO inf VALUES(%s)" % ', '.join(['?']*len(self.dtype_inf)), 
                arr_inf)

        return True


    def __makeInsDict(self, sel, dtype):
        """Handles BLOB datatype for arrays before insertion into sqlite DB.
        This method is hidden and used internatlly by :func:`sqlUpdate`.
        
        **Belongs to**: :class:`updateRadars`
        
        **Args**: 
            * **sel** (pymongo Ptr)
            * [**dtype**] (str): a list of 'name TYPE' pairsto be inserted into sqlite DB
        **Returns**:
            * **arr** a list of lists of DB entries
        """
        import pickle

        arr = []
        for ir,row in enumerate(sel):
            entry = []
            for typ in dtype:
                k, d = typ.split()
                if d == 'BLOB':
                    v = pickle.dumps(row[k])
                else: 
                    v = row[k]
                entry.append( v )
            arr.append( entry )

        return arr
        
