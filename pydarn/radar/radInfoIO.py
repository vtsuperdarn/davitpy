"""
*******************************
pydarn.radar.radInfoIO
*******************************
Input/Output for radar information (location, boresight, interferometer position...) is 
read from a local SQLlite database (radar.db). The functions in this module provide tools 
to populate/update said database (from hdw.dat and radar.dat files), or simply read hdw.dat 
and radar.dat files. It also provide a function to manually update the local radar.db database 
using the remote SQL database (requires an active internet connection).

This module contains the following functions
	* **hdwRead**
		reads hdw.dat files
	* **radarRead**
		reads radar.dat
	* **hdwToSqlLite**
		update radar.db with content of hdw.dat file
	* **radarToSqlLite**
		update radar.db with content of radar.dat file
	* **updateDb**
		update local radar.db from remote SQL database

Created by Sebastien

*******************************
"""
		

# *************************************************************
def radarRead(path=None):
	"""
Reads radar.dat file
(path defaults to RST environment variable SD_RADAR)
	"""
	import shlex
	import os
	from datetime import datetime
	from utils import parseDate
	
	# Read file
	try:
		file_net = open(os.environ['SD_RADAR'], 'r')
		data = file_net.readlines()
		file_net.close()
		err = 0
	except:
		print 'radarRead: cannot read '+os.environ['SD_RADAR']
		err = -1
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
	"""
Reads hdw.dat files for given radar specified by its hdw.dat file name 
(path defaults to RST environment variable SD_HDWPATH)
	"""
	import os
	import shlex
	from datetime import datetime
	from utils import timeYrsecToDate
	
	# Read hardware file FNAME
	try:
		file_hdw = open(os.environ['SD_HDWPATH']+'/'+fname, 'r')
		data = file_hdw.readlines()
		file_hdw.close()
	except IOError as errTmp:
		print 'hdwRead: cannot read '+os.environ['SD_HDWPATH']+'/'+fname+': {}'.format(errTmp.strerror)
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


def hdwToSqlLite(fname, path=None):
	"""
Reads hdw.dat files for given radar specified by its hdw.dat file name and path
and write its information to the local sqllite database.
(path defaults to RST environment variable SD_HDWPATH)
	"""
	pass


def radarToSqlLite(path=None):
	"""
Reads radar.dat file given its path (including file name) and writes its content 
to the local sqllite database. 
(path defaults to RST environment variable SD_RADAR)
	"""
	pass


def updateDb():
	"""
update local radar.db from remote SQL database. Currently, the remote 
database is housed on the VT servers.
	"""
	pass