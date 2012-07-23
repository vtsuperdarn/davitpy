# pydarn/radar/radNetwork.py
"""
*******************************
		radNetwork
*******************************
This module contains the following class:
	Network
		radar.dat and hdw.dat information from all the radars
	radar
		radar.dat info and placeholders for hdw.dat information
	site
		hdw.dat information
		
This module contains the following functions
	hdwRead
		reads hdw.dat files
	radarRead
		reads radar.dat

Created by Sebastien
*******************************
"""

# *************************************************************
class Network:
	"""
This class stores information from all radars according to their hdw.dat and radar.dat
	"""
	def __init__(self):
		self = []
			

# *************************************************************
class radar:
	"""
Reads radar.dat file and hdw.dat for a given radar and fills a radar structure
	"""
	#__slots__ = ('id', 'status', 'cnum', 'code', 'name', 'operator', 'hdwfname', 'st_time', 'ed_time', 'snum', 'site')
	def __init__(self):
		tsite = site()
		self.id = 0
		self.status = 0
		self.cnum = 0
		self.code = []
		self.name = ''
		self.operator = ''
		self.hdwfname = ''
		self.st_time = 0.0
		self.ed_time = 0.0
		self.snum = 0
		self.site = []
		for isit in range(32):
			self.site.append(tsite)
	
	def load(self, name='', id=-1, code=''):
		""" Method of RADAR object
load(name=name, id=id, code=code)

Fills the radar object with information from the radar specified by either its name, id or 3-letter code
		"""
		# First, load info from radar.dat file
		radarF = radarRead()
		for irad in range( len(radarF['id']) ):
			if (radarF['id'][irad] == id or radarF['name'][irad] == name or radarF['code'][irad][0] == code):
				self.id = radarF['id'][irad]
				self.status = radarF['status'][irad]
				self.st_time = radarF['st_time'][irad]
				self.ed_time = radarF['ed_time'][irad]
				self.name = radarF['name'][irad]
				self.operator = radarF['operator'][irad]
				self.hdwfname = radarF['hdwfname'][irad]
				self.code = radarF['code'][irad]
		# Then, load info from hdw.dat file
			

# *************************************************************
class site:
	"""
Reads hdw.dat for a given radar and fills a SITE structure
	"""
	#__slots__ = ('tval', 'geolat', 'geolon', 'alt', 'boresite', 'bmsep', 'vdir', 'atten', 'tdif', 'phidiff', 'interfer', 'recrise', 'maxatten', 'maxrange', 'maxbeam')
	def __init__(self):
		self.tval = 0.0
		self.geolat = 0.0
		self.geolon = 0.0
		self.alt = 0.0
		self.boresite = 0.0
		self.bmsep = 0.0
		self.vdir = 0
		self.atten = 0.0
		self.tdiff = 0.0
		self.phidiff = 0
		self.interfer = [0.0, 0.0, 0.0]
		self.recrise = 0.0
		self.maxatten = 0
		self.maxrange = 0
		self.maxbeam = 0
		

# *************************************************************
def radarRead():
	"""
radarRead()

Reads radar.dat file
	"""
	import shlex
	import os
	from datetime import datetime
	from utils import parse_date
	
	# Read file
	try:
		file_net = open(os.environ['RSTPATH']+'/tables/superdarn/radar.dat', 'r')
		data = file_net.readlines()
		file_net.close()
		err = 0
	except:
		print 'radarRead: cannot read '+os.environ['RSTPATH']+'/tables/superdarn/radar.dat'
		err = -1
		return {}
	
	# Initialize placeholder dictionary of lists
	radarF = {}
	radarF['id'] = []
	radarF['status'] = []
	radarF['st_time'] = []
	radarF['ed_time'] = []
	radarF['name'] = []
	radarF['operator'] = []
	radarF['hdwfname'] = []
	radarF['code'] = []
	# Fill dictionary with each radar.dat lines
	for ldat in data:
		ldat = shlex.split(ldat)
		radarF['id'].append( int(ldat[0]) )
		radarF['status'].append( int(ldat[1]) )
		tmpDate = parseDate( int(ldat[2]) )
		radarF['st_time'].append( datetime(tmpDate[0], tmpDate[1], tmpDate[2]) )
		tmpDate = parseDate( int(ldat[3]) )
		radarF['ed_time'].append( datetime(tmpDate[0], tmpDate[1], tmpDate[2]) )
		radarF['name'].append( ldat[4] )
		radarF['operator'].append( ldat[5] )
		radarF['hdwfname'].append( ldat[6] )
		radarF['code'].append( ldat[7:] )
	
	# Return			
	return radarF


# *************************************************************
def hdwRead(fname):
	"""
hdwRead(name=name, id=id, code=code)

Reads hdw.dat files for given radar specified by its hdw.dat file name (path excluded)
	"""
	import os
	import shlex
	from datetime import datetime
	from utils import timeYrsecToDate
	
	# Read hardware file FNAME
	try:
		file_hdw = open(os.environ['RSTPATH']+'/tables/superdarn/hdw/'+fname, 'r')
		data = file_hdw.readlines()
		file_hdw.close()
	except:
		print 'hdwRead: cannot read '+os.environ['RSTPATH']+'/tables/superdarn/hdw/'+fname
		return {}
	
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
	siteF['maxrange'] = []
	siteF['maxbeam'] = []
	# Read line by line, ignoring comments
	for ldat in data:
		if ldat[0] == '#': continue
		ldat = shlex.split(ldat)
		siteF['tval'].append( timeYrsecToDate( int(ldat[1]), int(ldat[2]) ) )
		siteF['geolat'].append( float(ldat[3]) )
		siteF['geolon'].append( float(ldat[4]) )
		siteF['alt'].append( float(ldat[5]) )
		siteF['boresite'].append( float(ldat[6]) )
		siteF['bmsep'].append( float(ldat[7]) )
		siteF['vdir'].append( int(ldat[8]) )
		siteF['atten'].append( float(ldat[9]) )
		siteF['tdiff'].append( float(ldat[10]) )
		siteF['phidiff'].append( int(ldat[11]) )
		siteF['interfer'].append( [float(ldat[12]), float(ldat[13]), float(ldat[14])] )
		siteF['recrise'].append( float(ldat[15]) )
		siteF['maxatten'].append( int(ldat[16]) )
		siteF['maxrange'].append( int(ldat[17]) )
		siteF['maxbeam'].append( int(ldat[18]) )
		
		
		
	# Return
	return siteF
	