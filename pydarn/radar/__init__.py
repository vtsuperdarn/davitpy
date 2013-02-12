# Radar module __init__.py
"""
*******************************
            RADAR
*******************************
This subpackage contains various radar information/routines for DaViT-py
DEV: functions/modules/classes with a * have not been developed yet

This includes the following object(s):
	* **network**
		radar.dat and hdw.dat information from all the radars
	* **radar**
		radar.dat and hdw.dat information
	* **site**
		hdw.dat information
	* **fov**
		field-of-view information


*******************************
"""

from radFov import *
from radUtils import *
from radInfoIO import *

# Update local HDF5
_ = updateHdf5()


# *************************************************************
class network(object):
	"""
This class stores information from all radars according to their hdw.dat and radar.dat

Created by Sebastien - Aug. 2012
	"""
	def __init__(self):
		"""
Creates NETWORK object
		"""
		import h5py
		from datetime import datetime
		from numpy import where

		# Date format
		dtfmt = "%Y-%m-%d %H:%M:%S"

		self.info = []
		# Open file
		rad_path = __file__.split('__init__.py')[0]
		f = h5py.File(rad_path+'/radars.hdf5','r')
		radarF = f['/radar']
		self.nradar = len(radarF['id'])
		for irad in range( self.nradar ):
			tRadar = radar()
			tRadar.id = radarF['id'][irad]
			tRadar.status = radarF['status'][irad]
			tRadar.cnum = radarF['cnum'][irad]
			tRadar.stTime = datetime.strptime(radarF['stTime'][irad], dtfmt)
			tRadar.edTime = datetime.strptime(radarF['edTime'][irad], dtfmt)
			tRadar.name = radarF['name'][irad]
			tRadar.operator = radarF['operator'][irad]
			tRadar.hdwfname = radarF['hdwfname'][irad]
			tRadar.code = radarF['code'][irad]
			siteF = f['/hdw']
			siteInds = where( siteF['id'][:] == tRadar.id )[0]
			if siteInds == []: continue
			tsnum = 0
			for ist,isit in enumerate(siteInds):
				tRadar.site[ist].tval = datetime.strptime(siteF['tval'][isit], dtfmt)
				tRadar.site[ist].geolat = siteF['geolat'][isit]
				tRadar.site[ist].geolon = siteF['geolon'][isit]
				tRadar.site[ist].alt = siteF['alt'][isit]
				tRadar.site[ist].boresite = siteF['boresite'][isit]
				tRadar.site[ist].bmsep = siteF['bmsep'][isit]
				tRadar.site[ist].vdir = siteF['vdir'][isit]
				tRadar.site[ist].atten = siteF['atten'][isit]
				tRadar.site[ist].tdiff = siteF['tdiff'][isit]
				tRadar.site[ist].phidiff = siteF['phidiff'][isit]
				tRadar.site[ist].interfer = siteF['interfer'][isit]
				tRadar.site[ist].recrise = siteF['recrise'][isit]
				tRadar.site[ist].maxatten = siteF['maxatten'][isit]
				tRadar.site[ist].maxgate = siteF['maxgate'][isit]
				tRadar.site[ist].maxbeam = siteF['maxbeam'][isit]
				tsnum += 1
			tRadar.snum = tsnum
			self.info.append(tRadar)
		f.close()
			
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
			outstring += '\n\t\t({}) - [{}][{}] {} ({})'.format(hemi, 
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
		from numpy import sin, cos, arccos, dot, cross, sign
		from math import radians, degrees
		
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
			# minAz = (site.boresite % 360.)-abs(site.bmsep)*site.maxbeam/2
			# maxAz = (site.boresite % 360.)+abs(site.bmsep)*site.maxbeam/2
			extFov = abs(site.bmsep)*site.maxbeam/2
			ptBo = [cos(radians(site.boresite)), sin(radians(site.boresite))]
			ptAz = [cos(radians(distPnt['az'])), sin(radians(distPnt['az']))]
			deltAz = degrees( arccos( dot(ptBo, ptAz) ) )
			# Skip if out of azimuth range
			if not abs(deltAz) <= extFov: continue
			if sign(cross(ptBo, ptAz)) >= 0:
				beam = int( site.maxbeam/2 + round( deltAz/site.bmsep ) - 1 )
			else:
				beam = int( site.maxbeam/2 - round( deltAz/site.bmsep ) )
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

Created by Sebastien - Aug. 2012
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
					\nsite: {10} elements'.format(self.id, \
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


Created by Sebastien - Aug. 2012
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
					\nvdir: {6} \
					\natten: {7:5.2f} \
					\ntdiff: {8:6.4f} \
					\nphidiff: {9:3.1f} \
					\ninterfer: [{10:5.2f}, {11:5.2f}, {12:5.2f}] \
					\nrecrise: {13:5.3f} \
					\nmaxatten: {14} \
					\nmaxgate: {15} \
					\nmaxbeam: {16}'.format(self.tval, \
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


