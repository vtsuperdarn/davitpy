"""
*********************
**Module**: pydarn.radar
*********************
This subpackage contains various radar information/routines for DaViT-py

**Classes**:
	* :class:`network`: radar.dat and hdw.dat information from all the radars
	* :class:`radar`: radar.dat and hdw.dat information
	* :class:`site`: hdw.dat information
"""

from radFov import *
from radUtils import *
from radInfoIO import *

# Update local HDF5
_ = updateHdf5()


# *************************************************************
class network(object):
	"""This class stores information from all radars according to their hdw.dat and radar.dat
	This information is read from the radar.hdf5 files provided with the pydarn module.
	
	**Members**: 
		* **nradar** (int): number of radars in class
		* **radars** (list): list of :class:`radar` objects
	**Methods**:
		* :func:`getRadarById`
		* :func:`getRadarByName`
		* :func:`getRadarByCode`
		* :func:`getRadarsByPosition`
		* :func:`getAllCodes`
	**Example**:
		::

			obj = pydarn.radar.network()

	.. note:: To add your own radar information to this class you can use the :func:`radInfoIO.radarRead` and the :func:`radInfoIO.hdwRead`. Then, manually append the output of these functions to this object.

	written by Sebastien, 2012-08
	"""

	def __init__(self):
		"""Default class constructor
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **None**
		**Returns**:
			* **network** (obj)
					
		written by Sebastien, 2012-08
		"""
		import h5py

		# Date format
		dtfmt = "%Y-%m-%d %H:%M:%S"

		self.radars = []
		# Open file
		rad_path = __file__.split('__init__.py')[0]
		f = h5py.File(rad_path+'/radars.hdf5','r')
		radarF = f['/radar']
		siteF = f['/hdw']
		self.nradar = len(radarF['id'])
		for irad in range( self.nradar ):
			self.radars.append(radar())
			self.radars[irad].fillFromHdf5(radarF['id'][irad], radarF, siteF)
		f.close()
			
	def __len__(self):
		"""Object length (number of radars)
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **None**
		**Returns**:
			* **number of radars** (int)
		**Example**:
			::

				len(obj)
					
		written by Sebastien, 2012-08
		"""
		return self.nradar
	
	def __str__(self):
		"""Object string representation
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **None**
		**Returns**:
			* **a string** (str)
		**Example**:
			::

				print(obj)
					
		written by Sebastien, 2012-08
		"""
		outstring = "Network information object: \
				\n\tTotal radars: {:d}".format(self.nradar)
		for iRad in range( self.nradar ):
			if self.radars[iRad].status == 1:
				status = 'active'
			elif self.radars[iRad].status == -1:
				status = 'offline'
			elif self.radars[iRad].status == 0:
				status = 'planned'
			else:
				status = '{}'.format(self.radars[iRad].status)
			hemi = 'South' if self.radars[iRad].sites[0].geolat < 0 else 'North'
			outstring += '\n\t\t({}) - [{}][{}] {} ({})'.format(hemi, 
																self.radars[iRad].id, 
																self.radars[iRad].code[0], 
																self.radars[iRad].name, 
																status)
		return outstring
		
	def getRadarById(self, id):
		"""Get a specific radar from its ID
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **id** (int): radar ID
		**Returns**:
			* **radar** (:class:`radar`)
		**Example**:
			::

				# To get the Blackstone radar by its ID
				radar = obj.getRadarById(33)
					
		written by Sebastien, 2012-08
		"""
		radar = self.getRadarBy(id, by='id')
		return radar
		
	def getRadarByName(self, name):
		"""Get a specific radar from its name
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **name** (str): radar full name
		**Returns**:
			* **radar** (:class:`radar`)
		**Example**:
			::

				# To get the Blackstone radar by its name
				radar = obj.getRadarById('Blackstone')
					
		written by Sebastien, 2012-08
		"""
		radar = self.getRadarBy(name, by='name')
		return radar
		
	def getRadarByCode(self, code):
		"""Get a specific radar from its 3-letter code
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **code** (str): radar 3-letter code
		**Returns**:
			* **radar** (:class:`radar`)
		**Example**:
			::

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
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **radN** (str/int): radar identifier (either code, name or id)
			* **by** (str): look-up method: 'code', 'name', 'id'
		**Returns**:
			* **radar** (:class:`radar`)
					
		written by Sebastien, 2012-08
		"""
		found = False
		for iRad in xrange( self.nradar ):
			if by.lower() == 'code':
				for ic in xrange(self.radars[iRad].cnum):
					if self.radars[iRad].code[ic].lower() == radN.lower():
						found = True
						return self.radars[iRad]
						break
			elif by.lower() == 'name':
				if self.radars[iRad].name.lower() == radN.lower():
					found = True
					return self.radars[iRad]
					break
			elif by.lower() == 'id':
				if self.radars[iRad].id == radN:
					found = True
					return self.radars[iRad]
					break
			else:
				print 'getRadarBy: invalid method by {}'.format(by)
				break
		if not found:
			print 'getRadarBy: could not find radar {}: {}'.format(by, radN)
			return found
		
	def getRadarsByPosition(self, lat, lon, alt, distMax=4000., datetime=None):
		"""Get a list of radars able to see a given point on Earth
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **lat**: latitude of given point in geographic coordinates
			* **lon**: longitude of given point in geographic coordinates
			* **alt**: altitude of point above the Earth's surface in km
			* **[distMax]**: maximum distance of given point from radar
			* **[datetime]**: python datetime object (defaults to today)
		**Returns**:
			* A dictionnary with keys:
				* 'radars': a list of radar objects (:class:`radar`)
				* 'dist': a list of distance from radar to given point (1 per radar)
				* 'beam': a list of beams (1 per radar) seeing the given point
		**Example**:
			::

				radars = obj.getRadarsByPosition(67., 134., 300.)
					
		written by Sebastien, 2012-08
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
			site = self.radars[iRad].getSiteByDate(datetime)
			# Skip if radar inactive at date
			if (not site) and (self.radars[iRad].status != 1): continue
			if not (self.radars[iRad].stTime <= datetime <= self.radars[iRad].edTime): continue
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
			out['radars'].append(self.radars[iRad])
			out['dist'].append(distPnt['dist'])
			out['beam'].append(beam)

		if found: return out
		else: return found
		
	def getAllCodes(self, datetime=None, hemi=None):
		"""Get a list of all active radar codes
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **[datetime]**: python datetime object (defaults to today)
			* **[hemi]**: 'north' or 'south' defaults to both
		**Returns**:
			* **codes** (list): A list of 3-letter codes
					
		written by Sebastien, 2012-08
		"""
		from datetime import datetime as dt
		
		if not datetime: datetime = dt.utcnow()
		
		codes = []
		for iRad in xrange( self.nradar ):
			tcod = self.radars[iRad].getSiteByDate(datetime)
			if (tcod) and (self.radars[iRad].status == 1) \
			and (self.radars[iRad].stTime <= datetime <= self.radars[iRad].edTime):
				if (hemi == None) or \
				(hemi.lower() == 'south' and tcod.geolat < 0) or \
				(hemi.lower() == 'north' and tcod.geolat >= 0): 
					codes.append(self.radars[iRad].code[0])
		
		return codes



# *************************************************************
class radar(object):
	"""Reads radar.dat file and hdw.dat for a given radar and fills a radar structure
	
	**Members**: 
		* **id** (int): radar ID
		* **status** (int): radar status (active, inactive or planned)
		* **cnum** (int): number of code names (usually 2, a 3-letter and 1-letter)
		* **code** (list): list of radar codes (usually 2, a 3-letter and 1-letter)
		* **name** (str): radar name
		* **operator** (str): PI institution
		* **hdwfname** (str): hdw.dat file name
		* **stTime** (datetime.datetime): date of first lights
		* **edTime** (datetime.datetime): last day of operations
		* **snum** (int): number of site objects (i.e. number of updates to the hdw.dat)
		* **sites** (list): list of :class:`site` objects
	**Methods**:
		* :func:`getSiteByDate`
	**Example**:
		::

			obj = pydarn.radar.radar()

	written by Sebastien, 2012-08
	"""
	#__slots__ = ('id', 'status', 'cnum', 'code', 'name', 'operator', 'hdwfname', 'stTime', 'edTime', 'snum', 'site')
	def __init__(self, code=None, radId=None):
		"""Default class constructor
		If no argument is passed, the object is initialized to 0
		
		**Belongs to**: :class:`radar`
		
		**Args**: 
			* [**code**] (str): 3-letter radar code
			* [**radId**] (int): radar ID
		**Returns**:
			* **radar** (:class:`radar`)

		.. note:: you should provide either **code** OR **radId**, not both
					
		written by Sebastien, 2012-08
		"""
		import h5py
		from numpy import where

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
		self.sites = [site()]

		# If a radar is requested...
		if code or radId:
			rad_path = __file__.split('__init__.py')[0]
			f = h5py.File(rad_path+'/radars.hdf5','r')
			radarF = f['/radar']
			siteF = f['/hdw']
			if code: radId = radarF['id'][ where( radarF['code'][:] == code )[0][0] ]
			self.fillFromHdf5(radId, radarF, siteF)
			f.close()

	def fillFromHdf5(self, radId, dset, siteDset):
		"""fill radar structure from hdf5 dataset
		
		**Belongs to**: :class:`radar`
		
		**Args**: 
			* **radID** (int): radar ID
			* **dset** (h5py.dset): hdf5 radar dataset
			* **sitedset** (h5py.dset): hdf5 site dataset
		**Returns**:
			* **None**
					
		written by Sebastien, 2013-02
		"""
		from datetime import datetime
		from numpy import where

		# Date format
		dtfmt = "%Y-%m-%d %H:%M:%S"

		irad = where( dset['id'][:] == radId )[0][0]
		self.id = dset['id'][irad]
		self.status = dset['status'][irad]
		self.cnum = dset['cnum'][irad]
		self.stTime = datetime.strptime(dset['stTime'][irad], dtfmt)
		self.edTime = datetime.strptime(dset['edTime'][irad], dtfmt)
		self.name = dset['name'][irad]
		self.operator = dset['operator'][irad]
		self.hdwfname = dset['hdwfname'][irad]
		self.code = dset['code'][irad]
		siteInds = where( siteDset['id'][:] == radId )[0]
		if siteInds == []: return
		tsnum = 0
		for ist,isit in enumerate(siteInds):
			self.sites[ist].fillFromHdf5(radId, siteDset, ind=ist)
			tsnum += 1
			self.sites.append(site())
		del self.sites[tsnum]
		self.snum = tsnum
			
	def __len__(self):
		""" Object length (number of site updates)
		"""
		return self.snum
	
	def __str__(self):
		"""Object string representation
		
		**Belongs to**: :class:`radar`
		
		**Args**: 
			* **None**
		**Returns**:
			* **a string** (str)
		**Example**:
			::

				print(obj)
					
		written by Sebastien, 2012-08
		"""
		outstring = 'id: {0} \
					\nstatus: {1} \
					\ncnum: {2} \
					\ncode: [{3}] \
					\nname: {4} \
					\noperator: {5} \
					\nhdwfname: {6} \
					\nstTime: {7} \
					\nedTime: {8} \
					\nsnum: {9} \
					\nsites: {10} elements'.format(self.id, \
										self.status, \
										self.cnum, \
										[c for c in self.code], \
										self.name, \
										self.operator, \
										self.hdwfname, \
										self.stTime.date(), \
										self.edTime.date(), \
										self.snum, \
										len(self.sites))
		return outstring
		
	def getSiteByDate(self, datetime):
		"""Get a specific radar site at a given date
		
		**Belongs to**: :class:`network`
		
		**Args**: 
			* **datetime** (datetime.datetime)
		**Returns**:
			* **site** (:class:`site`)
		**Example**:
			::

				# To get the Blackstone radar configuration today
				site = obj.getSiteByDate(datetime.datetime.utcnow())
					
		written by Sebastien, 2012-08
		"""
		found = False
		for iSit in range( self.snum ):
			if self.sites[iSit].tval == -1:
				found = True
				return self.sites[iSit]
				break
			elif self.sites[iSit].tval >= datetime:
				found = True
				return self.sites[iSit]
		if not found:
			print 'getSiteByDate: could not get SITE for date {}'.format(datetime)
			return found
		


# *************************************************************
class site(object):
	"""Reads hdw.dat for a given radar and fills a SITE structure
	
	**Members**: 
		* **tval** (datetime.datetime): last date and time operating with these parameters
		* **geolat** (float): main array latitude [deg]
		* **geolon** (float): main array longitude [deg]
		* **alt** (float): main array altitude [km]
		* **boresite** (float): boresight azimuth [deg]
		* **bmsep** (float): beam separation [deg]
		* **vdir** (int): velocity sign
		* **atten** (float): Analog Rx attenuator step [dB]
		* **tdiff** (float): Propagation time from interferometer array antenna to phasing matrix [us]
		* **phidiff** (float): phase sign for interferometric calculations
		* **interfer** (list): Interferometer offset [x, y, z]
		* **recrise** (float): Analog Rx rise time [us]
		* **maxatten** (int): maximum number of analog attenuation stages
		* **maxgate** (int): maximum number of range gates (assuming 45km gates)
		* **maxbeam** (int): maximum number of beams
	**Example**:
		::

			obj = pydarn.radar.site()

	written by Sebastien, 2012-08
	"""

	def __init__(self, radId=None, code=None, dt=None):
		"""Default class constructor
		
		**Belongs to**: :class:`site`
		
		**Args**: 
			* [**radId**] (int): radar ID
			* [**code**] (str): 3-letter radar code
			* [**dt**] (datetime.datetime): date and time of radar configurationation
		**Returns**:
			* **site** (:class:`site`)

		.. note:: you should provide either **code** OR **radId**, not both
					
		written by Sebastien, 2012-08
		"""
		import h5py
		from numpy import where

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
			rad_path = __file__.split('__init__.py')[0]
			f = h5py.File(rad_path+'/radars.hdf5','r')
			siteF = f['/hdw']
			if code: radId = f['/radar']['id'][ where( f['/radar']['code'][:] == code )[0][0] ]
			self.fillFromHdf5(radId, siteF, dt=dt)
			f.close()

	def fillFromHdf5(self, radId, dset, ind=-1, dt=None):
		"""fill site structure from hdf5 dataset
		
		**Belongs to**: :class:`site`
		
		**Args**: 
			* **radID** (int): radar ID
			* **dset** (h5py.dset): hdf5 dataset
			* [**ind**] (int): site index; defaults to most recent configuration
			* [**dt**] (datetime.datetime)
		**Returns**:
			* **None**
					
		written by Sebastien, 2013-02
		"""
		from datetime import datetime
		from numpy import where

		# Date format
		dtfmt = "%Y-%m-%d %H:%M:%S"

		# Find the data index
		siteInds = where( dset['id'][:] == radId )[0]
		# Adjust index if negative
		if ind < 0: ind = len(siteInds) + ind
		# Get index
		if siteInds == []: return
		if dt:
			for ist,isit in enumerate(siteInds):
				tval = datetime.strptime(dset['tval'][isit], dtfmt)
				if tval < dt: 
					continue
				else:
					ind = isit 
					break
		else:
			ind = siteInds[ind]

		self.tval = datetime.strptime(dset['tval'][ind], dtfmt)
		self.geolat = dset['geolat'][ind]
		self.geolon = dset['geolon'][ind]
		self.alt = dset['alt'][ind]
		self.boresite = dset['boresite'][ind]
		self.bmsep = dset['bmsep'][ind]
		self.vdir = dset['vdir'][ind]
		self.atten = dset['atten'][ind]
		self.tdiff = dset['tdiff'][ind]
		self.phidiff = dset['phidiff'][ind]
		self.interfer = dset['interfer'][ind]
		self.recrise = dset['recrise'][ind]
		self.maxatten = dset['maxatten'][ind]
		self.maxgate = dset['maxgate'][ind]
		self.maxbeam = dset['maxbeam'][ind]
			
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


