# pydarn/radar/radNetwork.py
"""
*******************************
		radNetwork
*******************************
This module contains the following class:
	network
		radar.dat and hdw.dat information from all the radars
	radar
		placeholder for radar.dat and hdw.dat information
	site
		placeholder for hdw.dat information
		
This module contains the following functions
	hdwRead
		reads hdw.dat files
	radarRead
		reads radar.dat

Created by Sebastien
*******************************
"""

# *************************************************************
class network(object):
	"""
This class stores information from all radars according to their hdw.dat and radar.dat
	"""
	def __init__(self):
		"""
Creates NETWORK object
		"""
		self.info = []
		# First, load info from radar.dat file
		radarF = radarRead()
		self.nradar = len(radarF['id'])
		for irad in range( self.nradar ):
			tRadar = radar()
			tRadar.id = radarF['id'][irad]
			tRadar.status = radarF['status'][irad]
			tRadar.st_time = radarF['st_time'][irad]
			tRadar.ed_time = radarF['ed_time'][irad]
			tRadar.name = radarF['name'][irad]
			tRadar.operator = radarF['operator'][irad]
			tRadar.hdwfname = radarF['hdwfname'][irad]
			tRadar.code = radarF['code'][irad]
			# Then, load info from hdw.dat file
			siteF = hdwRead(tRadar.hdwfname)
			for isit in range( len(siteF['tval']) ):
				tRadar.site[isit].tval = siteF['tval'][isit]
				tRadar.site[isit].geolat = siteF['geolat'][isit]
				tRadar.site[isit].geolon = siteF['geolon'][isit]
				tRadar.site[isit].alt = siteF['alt'][isit]
				tRadar.site[isit].boresite = siteF['boresite'][isit]
				tRadar.site[isit].bmsep = siteF['bmsep'][isit]
				tRadar.site[isit].vdir = siteF['vdir'][isit]
				tRadar.site[isit].atten = siteF['atten'][isit]
				tRadar.site[isit].tdiff = siteF['tdiff'][isit]
				tRadar.site[isit].phidiff = siteF['phidiff'][isit]
				tRadar.site[isit].interfer = siteF['interfer'][isit]
				tRadar.site[isit].recrise = siteF['recrise'][isit]
				tRadar.site[isit].maxatten = siteF['maxatten'][isit]
				tRadar.site[isit].maxrange = siteF['maxrange'][isit]
				tRadar.site[isit].maxbeam = siteF['maxbeam'][isit]
			self.info.append(tRadar)
			
	def __len__(self):
		"""
Object length (number of radars)
		"""
		return self.nradar
	
	def __str__(self):
		"""
Object string representation
		"""
		outstring = "Network information object: \
				\n\tTotal radars: {:d}".format(self.nradar)
		for iRad in range( self.nradar ):
			if self.info[iRad].status == 1:
				status = 'active'
			elif self.info[iRad].status == -1:
				status = 'offline'
			elif self.info[iRad].status == 0:
				status = 'planned'
			else:
				status = '{}'.format(self.info[iRad].status)
			outstring += '\n\t\t[{:d}] {} ({})'.format(self.info[iRad].id, self.info[iRad].name, status)
		return outstring
		
	def getRadarById(self, id):
		"""
Get a specific radar from its ID
		"""
		for iRad in range( self.nradar ):
			if self.info[iRad].id == id:
				return self.info[iRad]
				break
		
	def getRadarByName(self, name):
		"""
Get a specific radar from its name
		"""
		for iRad in range( self.nradar ):
			if self.info[iRad].name.lower() == name.lower():
				return self.info[iRad]
				break
		
	def getRadarByCode(self, code):
		"""
Get a specific radar from its 3-letter code
		"""
		for iRad in range( self.nradar ):
			if self.info[iRad].code[0].lower() == code.lower():
				return self.info[iRad]
				break
			

# *************************************************************
class radar(network):
	"""
Reads radar.dat file and hdw.dat for a given radar and fills a radar structure
	"""
	__maxSites = 32
	#__slots__ = ('id', 'status', 'cnum', 'code', 'name', 'operator', 'hdwfname', 'st_time', 'ed_time', 'snum', 'site')
	def __init__(self):
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
		for isit in range(self.__maxSites):
			tsite = site()
			self.site.append(tsite)
			
	def __len__(self):
		"""
Object length
		"""
		return 1
	
	def __str__(self):
		"""
Object string representation
		"""
		outstring = 'id: {0:d} \
					\nstatus: {1:d} \
					\ncnum: {2:d} \
					\ncode: {3} \
					\nname: {4} \
					\noperator: {5} \
					\nhdwfname: {6} \
					\nst_time: {7} \
					\ned_time: {8} \
					\nsnum: {9:d} \
					\nsite: {10:d} elements'.format(self.id, \
										self.status, \
										self.cnum, \
										self.code[0], \
										self.name, \
										self.operator, \
										self.hdwfname, \
										self.st_time.date(), \
										self.ed_time.date(), \
										self.snum, \
										len(self.site))
		return outstring
		
	def getSiteByDate(self, date):
		"""
Get a specific radar site at a given date
		"""
		for iSit in range( self.__maxSites ):
			if self.site[iSit].tval == -1:
				return self.site[iSit]
				break
			if self.site[iSit].tval >= date:
				if iSit > 0: 
					return self.site[iSit-1]
				else:
					return self.site[iSit]
				break
		


# *************************************************************
class site(radar):
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
			
	def __len__(self):
		"""
Object length
		"""
		return 1
	
	def __str__(self):
		"""
Object string representation
		"""
		outstring = 'tval: {0} \
					\ngeolat: {1:5.2f} \
					\ngeolon: {2:5.2f} \
					\nalt: {3:6.2f} \
					\nboresite: {4:5.2f} \
					\nbmsep: {5:5.2f} \
					\nvdir: {6:3.1f} \
					\natten: {7:5.2f} \
					\ntdiff: {8:6.4f} \
					\nphidiff: {9:3.1f} \
					\ninterfer: [{10:5.2f}, {11:5.2f}, {12:5.2f}] \
					\nrecrise: {13:5.3f} \
					\nmaxatten: {14:d} \
					\nmaxrange: {15:d} \
					\nmaxbeam: {16:d}'.format(self.tval, \
											self.geolat, \
											self.geolon, \
											self.alt, \
											self.boresite, \
											self.bmsep, \
											self.vdir, \
											self.atten, \
											self.tdiff, \
											self.phidiff, \
											self.interfer[0], self.interfer[1], self.interfer[2], \
											self.recrise, \
											self.maxatten, \
											self.maxrange, \
											self.maxbeam)
		return outstring
		

# *************************************************************
def radarRead():
	"""radarRead()
Reads radar.dat file
	"""
	import shlex
	import os
	from datetime import datetime
	from utils import parseDate
	
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
	"""hdwRead(name=name, id=id, code=code)
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
		siteF['phidiff'].append( int(ldat[11]) )
		siteF['interfer'].append( [float(ldat[12]), float(ldat[13]), float(ldat[14])] )
		siteF['recrise'].append( float(ldat[15]) )
		siteF['maxatten'].append( int(ldat[16]) )
		siteF['maxrange'].append( int(ldat[17]) )
		siteF['maxbeam'].append( int(ldat[18]) )
		
	# Return
	return siteF
	