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

This module contains the following objects
	* **updateHdf5**
		update local radar.hdf5 from remote SQL database

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
	"""
update local radar.hdf5 from remote SQL database. Currently, the remote 
database is housed on the VT servers.
	"""

	def __init__(self):
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
		# SQL server
		self.sql_user = 'sd_dbread'
		self.sql_host = 'sd-data.ece.vt.edu'
		self.sql_port = 5432

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

		# Try to connect to DB
		conn = self.sqlConnect()
		# If it worked, try to update HDF5 file
		if conn: self.h5Update()


	def sqlConnect(self):
		'''
Try to establish a connection to remote sql database
		'''
		import sqlalchemy as sqla
		import sys

		try:
			engine = sqla.create_engine("postgresql://{}:@{}:{}/radarInfo?sslmode=require".\
										format(self.sql_user,
											self.sql_host, 
											self.sql_port))
			meta = sqla.MetaData(engine)

			tbSel = lambda tbName: sqla.Table(tbName, meta, autoload=True).select().execute().fetchall()

			self.sql_select = {'rad': tbSel("radars"), 'hdw': tbSel("hdw"), 'inf': tbSel("info")}
			return True
		except:
			print 'Could not connect to remote DB: ', sys.exc_info()[0]
			return False


	def h5Init(self):
		'''
Initialize HDF5 file (only if file does not already exists)
		'''
		import h5py, os

		fname = os.path.join(self.h5_path, self.h5_file)
		try:
			with open(fname,'r+') as f: pass
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
		'''
Update HDF5 file with provided SQL selections (if possible).
		'''
		import h5py, os, sys

		isInit = self.h5Init()
		if not isInit: return False

		fname = os.path.join(self.h5_path, self.h5_file)

		arr_rad = self.__sqlaToArr(self.sql_select['rad'], self.dtype_rad)
		arr_hdw = self.__sqlaToArr(self.sql_select['hdw'], self.dtype_hdw)
		arr_inf = self.__sqlaToArr(self.sql_select['inf'], self.dtype_info)

		try:
			f = h5py.File(fname,'r+')

			# Update each dataset
			self.__h5UpdateDset(f['radar'], arr_rad, 'id')
			self.__h5UpdateDset(f['hdw'], arr_hdw, 'id')
			self.__h5UpdateDset(f['metadata'], arr_inf, 'var')

			# Close file
			f.close()
			print 'Updated radar information [HDF5 file]'
		except:
			print 'Problem updating HDF5 file: ', sys.exc_info()[0]
			return False

		return True


	def __h5UpdateDset(self, dset, arr, key):
		'''
Update dataset (scan existing rows and update if necessary)
		'''
		from numpy import where

		for row in arr:
			inds = where( dset[:,key]==row[key] )
			# Try to overwrite if exist, else grow the dataset and insert
			try:
				dset[inds[0][0]] = row
			except IndexError:
				dset.resize((dset.shape[0]+1,))
				dset[dset.shape[0]-1] = row


	def __sqlaToArr(self, sel, dtype=None):
		'''
Create a compound array out of SQLAlchemy row objects.
This is used to write in HDF5 datasets.
		'''
		import numpy

		arr = numpy.empty(len(sel), dtype=dtype)
		for ir,row in enumerate(sel):
			for k,v in row.items():
				try:
					arr[ir][k] = v
				except (ValueError, TypeError):
					arr[ir][k][:] = v
		return arr

