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


# *************************************************************
def updateHdf5():
	"""
update local radar.hdf5 from remote SQL database. Currently, the remote 
database is housed on the VT servers.
	"""
	import os
	import sys
	import sqlalchemy as sqla
	import h5py

	# Date format
	dtfmt = '%Y-%m-%d %H:%M:%S'
	# Remove file (if it exists)
	rad_path = os.path.abspath( __file__.split('radInfoIO.py')[0] )

	try:
		engine = sqla.create_engine("postgresql://sd_dbread:@sd-data.ece.vt.edu:5432/radarInfo?sslmode=require")
		meta = sqla.MetaData(engine)

		radartb = sqla.Table("radars", meta, autoload=True)
		hdwtb = sqla.Table("hdw", meta, autoload=True)

		radarsSel = radartb.select().execute().fetchall()
		hdwSel = hdwtb.select().execute().fetchall()
	except:
		print 'Could not connect to remote DB, using local files for radar.dat and hdw.dat'
		return False


	try:
		# Remove file first (because!)
		try:
			os.remove(rad_path+'/radars.hdf5')
		except OSError:
			pass
		# Open file
		f = h5py.File(rad_path+'/radars.hdf5','w')

		# Write RADAR info
		radar_grp = f.create_group("radar")
		radar_grp.create_dataset(name='id', data=[rad['id'] for rad in radarsSel], maxshape=(None,))
		radar_grp.create_dataset(name='cnum', data=[rad['cnum'] for rad in radarsSel], maxshape=(None,))
		radar_grp.create_dataset(name='code', data=[[str(c) for c in rad['code']] for rad in radarsSel], maxshape=(None,None))
		radar_grp.create_dataset(name='name', data=[str(rad['name']) for rad in radarsSel], maxshape=(None,))
		radar_grp.create_dataset(name='operator', data=[str(rad['operator']) for rad in radarsSel], maxshape=(None,))
		radar_grp.create_dataset(name='hdwfname', data=[str(rad['hdwfname']) for rad in radarsSel], maxshape=(None,))
		radar_grp.create_dataset(name='status', data=[rad['status'] for rad in radarsSel], maxshape=(None,))
		radar_grp.create_dataset(name='stTime', data=[rad['stTime'].strftime(dtfmt) for rad in radarsSel], maxshape=(None,))
		radar_grp.create_dataset(name='edTime', data=[rad['edTime'].strftime(dtfmt) for rad in radarsSel], maxshape=(None,))
		radar_grp.create_dataset(name='snum', data=[rad['snum'] for rad in radarsSel], maxshape=(None,))

		# Write HDW info
		hdw_grp = f.create_group("hdw")
		hdw_grp.create_dataset(name='id', data=[site['id'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='tval', 
		    data=['{}-{}-{} {}:{}:{}'.format(site['tval'].year,site['tval'].month,site['tval'].day,
		                                     site['tval'].hour,site['tval'].minute,site['tval'].second) for site in hdwSel], 
		    maxshape=(None,))
		hdw_grp.create_dataset(name='geolat', data=[site['geolat'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='geolon', data=[site['geolon'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='alt', data=[site['alt'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='boresite', data=[site['boresite'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='bmsep', data=[site['bmsep'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='vdir', data=[site['vdir'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='atten', data=[site['atten'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='tdiff', data=[site['tdiff'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='phidiff', data=[site['phidiff'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='recrise', data=[site['recrise'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='maxatten', data=[site['maxatten'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='maxgate', data=[site['maxgate'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='maxbeam', data=[site['maxbeam'] for site in hdwSel], maxshape=(None,))
		hdw_grp.create_dataset(name='interfer', data=[site['interfer'] for site in hdwSel], maxshape=(None,None))

		# Close file
		f.close()
		print 'Updated radar information [HDF5 file]'
	except:
		print 'Problem updating HDF5 file: ', sys.exc_info()[0]
		return False

	return True

