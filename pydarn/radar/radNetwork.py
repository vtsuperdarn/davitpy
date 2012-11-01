# pydarn/radar/radNetwork.py
"""
*******************************
		radNetwork
*******************************
This module contains the following class:
	* **network**
		radar.dat and hdw.dat information from all the radars
	* **radar**
		placeholder for radar.dat and hdw.dat information
	* **site**
		placeholder for hdw.dat information
		
This module contains the following functions
	* **hdwRead**
		reads hdw.dat files
	* **radarRead**
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
		if not radarF: 
			print 'network(object): No radars found in radar.dat'
		self.nradar = len(radarF['id'])
		for irad in range( self.nradar ):
			tRadar = radar()
			tRadar.id = radarF['id'][irad]
			tRadar.status = radarF['status'][irad]
			tRadar.cnum = radarF['cnum'][irad]
			tRadar.stTime = radarF['stTime'][irad]
			tRadar.edTime = radarF['edTime'][irad]
			tRadar.name = radarF['name'][irad]
			tRadar.operator = radarF['operator'][irad]
			tRadar.hdwfname = radarF['hdwfname'][irad]
			tRadar.code = radarF['code'][irad]
			# Then, load info from hdw.dat file
			siteF = hdwRead(tRadar.hdwfname)
			if not siteF: continue
			tsnum = 0
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
				tRadar.site[isit].maxgate = siteF['maxgate'][isit]
				tRadar.site[isit].maxbeam = siteF['maxbeam'][isit]
				tsnum += 1
			tRadar.snum = tsnum
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
			hemi = 'South' if self.info[iRad].site[0].geolat < 0 else 'North'
			outstring += '\n\t\t({}) - [{:d}][{}] {} ({})'.format(hemi, 
																self.info[iRad].id, 
																self.info[iRad].code[0], 
																self.info[iRad].name, 
																status)
		return outstring
		
	def getRadarById(self, id):
		"""
Get a specific radar from its ID
		"""
		radar = self.getRadarBy(id, by='id')
		return radar
		
	def getRadarByName(self, name):
		"""
Get a specific radar from its name
		"""
		radar = self.getRadarBy(name, by='name')
		return radar
		
	def getRadarByCode(self, code):
		"""
Get a specific radar from its 3-letter code
		"""
		radar = self.getRadarBy(code, by='code')
		return radar
		
	def getRadarBy(self, radN, by):
		"""Get a specific radar from its name/code/id
This method is the underlying function behing getRadarByCode, getRadarByName and getRadarById

**INPUTS**:
	* **radN**: radar identifier (either code, name or id)
	* **by**: look-up method: 'code', 'name', 'id'

**OUTPUTS**:
	* A radar object

		"""
		found = False
		for iRad in xrange( self.nradar ):
			if by.lower() == 'code':
				for ic in xrange(self.info[iRad].cnum):
					if self.info[iRad].code[ic].lower() == radN.lower():
						found = True
						return self.info[iRad]
						break
			elif by.lower() == 'name':
				if self.info[iRad].name.lower() == radN.lower():
					found = True
					return self.info[iRad]
					break
			elif by.lower() == 'id':
				if self.info[iRad].id == radN:
					found = True
					return self.info[iRad]
					break
			else:
				print 'getRadarBy: invalid method by {}'.format(by)
				break
		if not found:
			print 'getRadarBy: could not find radar {}: {}'.format(by, radN)
			return found
		
	def getRadarsByPosition(self, lat, lon, alt, distMax=4000., datetime=None):
		"""Get a list of radars able to see a given point 

**INPUTS**:
	* **lat**: latitude of given point in geographic coordinates
	* **lon**: longitude of given point in geographic coordinates
	* **alt**: altitude of point above the Earth's surface in km
	* **[distMax]**: maximum distance of given point from radar
	* **[datetime]**: python datetime object
**OUTPUTS**:
	* A dictionnary with keys:
		* 'radars': a list of radar objects
		* 'dist': a list of distance from radar to given point (1 per radar)
		* 'beam': a list of beams (1 per radar) seeing the given point

		"""
		from datetime import datetime as dt
		from utils import geoPack as geo
		
		if not datetime: datetime = dt.utcnow()

		found = False
		out = {'radars': [], 
				'dist': [], 
				'beam': []}
		for iRad in xrange( self.nradar ):
			site = self.info[iRad].getSiteByDate(datetime)
			# Skip if radar inactive at date
			if (not site) and (self.info[iRad].status != 1): continue
			if not (self.info[iRad].stTime <= datetime <= self.info[iRad].edTime): continue
			# Skip if radar in other hemisphere
			if site.geolat*lat < 0.: continue
			distPnt = geo.calcDistPnt(site.geolat, site.geolon, site.alt, 
							distLat=lat, distLon=lon, distAlt=300.)
			# Skip if radar too far
			if distPnt['dist'] > distMax: continue
			minAz = site.boresite-site.bmsep*site.maxbeam/2
			maxAz = site.boresite+site.bmsep*site.maxbeam/2
			# Skip if out of azimuth range
			if not minAz <= distPnt['az'] <= maxAz: continue
			beam = int( site.maxbeam/2 + round( (distPnt['az']-site.boresite)/site.bmsep ) )
			# Update output
			found = True
			out['radars'].append(self.info[iRad])
			out['dist'].append(distPnt['dist'])
			out['beam'].append(beam)

		if found: return out
		else: return found
		
	def getAllCodes(self, datetime=None, hemi=None):
		"""
Get a list of all active radar codes
		"""
		from datetime import datetime as dt
		
		if not datetime: datetime = dt.utcnow()
		
		codes = []
		for iRad in xrange( self.nradar ):
			tcod = self.info[iRad].getSiteByDate(datetime)
			if (tcod) and (self.info[iRad].status == 1) \
			and (self.info[iRad].stTime <= datetime <= self.info[iRad].edTime):
				if (hemi == None) or \
				(hemi.lower() == 'south' and tcod.geolat < 0) or \
				(hemi.lower() == 'north' and tcod.geolat >= 0): 
					codes.append(self.info[iRad].code[0])
				
		
		return codes
			

# *************************************************************
class radar(network):
	"""
Reads radar.dat file and hdw.dat for a given radar and fills a radar structure
	"""
	__maxSites__ = 32
	#__slots__ = ('id', 'status', 'cnum', 'code', 'name', 'operator', 'hdwfname', 'stTime', 'edTime', 'snum', 'site')
	def __init__(self):
		self.id = 0
		self.status = 0
		self.cnum = 0
		self.code = []
		self.name = ''
		self.operator = ''
		self.hdwfname = ''
		self.stTime = 0.0
		self.edTime = 0.0
		self.snum = 0
		self.site = []
		for isit in range(self.__maxSites__):
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
					\nstTime: {7} \
					\nedTime: {8} \
					\nsnum: {9:d} \
					\nsite: {10:d} elements'.format(self.id, \
										self.status, \
										self.cnum, \
										self.code[0], \
										self.name, \
										self.operator, \
										self.hdwfname, \
										self.stTime.date(), \
										self.edTime.date(), \
										self.snum, \
										len(self.site))
		return outstring
		
	def getSiteByDate(self, datetime):
		"""
Get a specific radar site at a given date (as a python datetime object)
		"""
		found = False
		for iSit in range( self.__maxSites__ ):
			if self.site[iSit].tval == -1:
				found = True
				return self.site[iSit]
				break
			elif self.site[iSit].tval >= datetime:
				found = True
				return self.site[iSit]
		if not found:
			print 'getSiteByDate: could not get SITE for date {}'.format(datetime)
			return found
		


# *************************************************************
class site(radar):
	"""
Reads hdw.dat for a given radar and fills a SITE structure
	"""
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
		self.phidiff = 0.0
		self.interfer = [0.0, 0.0, 0.0]
		self.recrise = 0.0
		self.maxatten = 0
		self.maxgate = 0
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
					\nmaxgate: {15:d} \
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
											self.maxgate, \
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
		file_hdw = open(os.environ['SD_HDWPATH']+'/'+fname, 'r')
		data = file_hdw.readlines()
		file_hdw.close()
	except:
		print 'hdwRead: cannot read '+os.environ['SD_HDWPATH']+'/'+fname
		return None
	
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
	