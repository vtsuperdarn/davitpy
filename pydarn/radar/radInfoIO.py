"""
*********************
**Module**: pydarn.radar.radInfoIO
*********************
Input/Output for radar information (location, boresight, interferometer position...) is 
read from a local dblite database (radar.db). The functions in this module provide tools 
to populate/update said database (from hdw.dat and radar.dat files), or simply read hdw.dat 
and radar.dat files. It also provide a function to manually update the local radar.db database 
using the remote db database (requires an active internet connection).

**Classes**:
	* :class:`updateHdf5`
**Functions**:
	* :func:`hdwRead`: reads hdw.dat files
	* :func:`radarRead`: reads radar.dat file
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
class updateHdf5(object):
	"""update local radar.hdf5 from remote db database. Currently, the remote 
	database is housed on the VT servers.
	
	**Members**: 
		* **h5_path** (str): path to hdf5 file
		* **h5_file** (str): hdf5 file name
	**Methods**:
		* :func:`h5Init`
		* :func:`h5Update`
		* :func:`dbConnect`
	**Example**:
		::

			obj = pydarn.radar.updateHdf5()

	written by Sebastien, 2012-10
	"""

	def __init__(self):
		"""Default class constructor
		
		**Belongs to**: :class:`updateHdf5`
		
		**Args**: 
			* **None**
		**Returns**:
			* **updateHdf5** (obj)
					
		written by Sebastien, 2012-10
		"""

		import os, sys
		from datetime import datetime
		from numpy import dtype
		import h5py

		# Date format
		dtfmt = '%Y-%m-%d %H:%M:%S'
		dttest = datetime.utcnow().strftime(dtfmt)
		# File path
		self.h5_path = os.path.abspath( __file__.split('radInfoIO.py')[0] )
		self.h5_file = 'radars.hdf5'
		# MongoDB server
		self.db_user = 'sd_dbread'
		self.db_pswd = '5d'
		self.db_host = 'sd-work9.ece.vt.edu'
		self.db_name = 'radarInfo'

		# Declare custom data types
		self.dtype_rad = dtype([('id', 'i'), 
		                         ('cnum', 'i'),
		                         ('code', 'S3', (2,)),
		                         ('name', h5py.new_vlen(str) ), 
		                         ('operator', h5py.new_vlen(str) ), 
		                         ('hdwfname', h5py.new_vlen(str) ), 
		                         ('status', 'i'), 
		                         ('stTime', 'S{}'.format(len(dttest))), 
		                         ('edTime', 'S{}'.format(len(dttest))), 
		                         ('snum', 'i') ])
		self.dtype_hdw = dtype([('id', 'i'), 
		                         ('tval', 'S{}'.format(len(dttest))),
		                         ('geolat', 'float'),
		                         ('geolon', 'float'),
		                         ('alt', 'float'),
		                         ('boresite', 'float'),
		                         ('bmsep', 'float'),
		                         ('vdir', 'i'),
		                         ('tdiff', 'float'),
		                         ('phidiff', 'float'),
		                         ('recrise', 'float'),
		                         ('atten', 'float'),
		                         ('maxatten', 'float'),
		                         ('maxgate', 'i'),
		                         ('maxbeam', 'i'),
		                         ('interfer', 'float', (3,)) ])
		self.dtype_info = dtype([('var', h5py.new_vlen(str)),
		                          ('description', h5py.new_vlen(str)) ])

		self.h5Update()


	def dbConnect(self):
		"""Try to establish a connection to remote db database
		
		**Belongs to**: :class:`updateHdf5`
		
		**Args**: 
			* **None**
		**Returns**:
			* **isConnected** (bool): True if the connection was successfull
					
		written by Sebastien, 2012-10
		"""
		from pymongo import MongoClient
		import sys

		try:
			conn = MongoClient( 'mongodb://{}:{}@{}/{}'.format(self.db_user,
																	   self.db_pswd, 
																	   self.db_host,
																	   self.db_name) )

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


	def h5Init(self):
		"""Initialize HDF5 file (only if file does not already exists)
		
		**Belongs to**: :class:`updateHdf5`
		
		**Args**: 
			* **None**
		**Returns**:
			* **isConnected** (bool): True if hdf5 file already exists or was sussessfully created
					
		written by Sebastien, 2012-10
		"""
		import h5py, os

		fname = os.path.join(self.h5_path, self.h5_file)
		try:
			with open(fname,'r+') as f: pass
			return True
		except IOError:
			try:
				# Open file
				f = h5py.File(fname,'w')

				rad_ds = f.create_dataset('radar', (1,), dtype=self.dtype_rad)
				hdw_ds = f.create_dataset('hdw', (1,), dtype=self.dtype_hdw)
				info_ds = f.create_dataset("metadata", (1,), dtype=self.dtype_info)

				# Close file
				f.close()
				return True
			except IOError:
				print 'Cannot initialize HDF5 file for updates. Changing nothing.'
				return False


	def h5Update(self):
		"""Update HDF5 file with provided db selections (if possible).
		
		**Belongs to**: :class:`updateHdf5`
		
		**Args**: 
			* **None**
		**Returns**:
			* **isConnected** (bool): True if hdf5 file update was successfull
					
		written by Sebastien, 2012-10
		"""
		import h5py, os, sys

		# Try to connect to DB
		conn = self.dbConnect()
		if not conn: return False

		# Try to open hdf5 file
		isInit = self.h5Init()
		if not isInit: return False

		fname = os.path.join(self.h5_path, self.h5_file)

		arr_rad = self.__makeCompArr(self.db_select['rad'], self.dtype_rad)
		arr_hdw = self.__makeCompArr(self.db_select['hdw'], self.dtype_hdw)
		arr_inf = self.__makeCompArr(self.db_select['inf'], self.dtype_info)

		try:
			f = h5py.File(fname,'r+')

			# Update each dataset
			self.__h5UpdateDset(f['radar'], arr_rad, 'id')
			self.__h5UpdateDset(f['hdw'], arr_hdw, 'id')
			self.__h5UpdateDset(f['metadata'], arr_inf, 'var')

			# Close file
			f.close()
			print 'Updated radar information in {}'.format( os.path.join(self.h5_path, self.h5_file) )
		except:
			print 'Problem updating HDF5 file: ', sys.exc_info()[0]
			return False

		return True


	def __h5UpdateDset(self, dset, arr, key):
		"""Update dataset (scan existing rows and update if necessary).
		This method is hidden and used internatlly by :func:`h5Update`.
		
		**Belongs to**: :class:`updateHdf5`
		
		**Args**: 
			* **dset** (hdf5 dataset): an hdf5 dataset from an hdf5 file object
			* **arr** (numpy.dtype): compound array
			* **key** (str): primary key to hdf5 dataset
		**Returns**:
			* **None**
					
		written by Sebastien, 2012-10
		"""
		from numpy import where

		for row in arr:
			inds = where( dset[:,key]==row[key] )
			# Try to overwrite if exist, else grow the dataset and insert
			try:
				dset[inds[0][0]] = row
			except IndexError:
				dset.resize((dset.shape[0]+1,))
				dset[dset.shape[0]-1] = row


	def __makeCompArr(self, sel, dtype=None):
		"""Create a compound array out of db output. This is used to write in HDF5 datasets.
		This method is hidden and used internatlly by :func:`h5Update`.
		
		**Belongs to**: :class:`updateHdf5`
		
		**Args**: 
			* **sel** (pymongo Ptr)
			* [**dtype**] (numpy.dtype): the numpy.dtype of the compound array
		**Returns**:
			* **None**
					
		written by Sebastien, 2012-10
		"""
		import numpy

		arr = numpy.empty(sel.count(), dtype=dtype)
		for ir,row in enumerate(sel):
			for k,v in row.items():
				if k == '_id': continue
				try:
					arr[ir][k] = v
				except (ValueError, TypeError):
					arr[ir][k][:] = v
		return arr

