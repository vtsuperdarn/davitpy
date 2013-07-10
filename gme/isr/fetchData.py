# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: gme.fetchData
*********************
This module handles fetching Incoherent Scatter Radar data from Madrigal

**Class**:
	* :class:`fetchData`: Fetch Incoherent Scatter Radar data directly from Madrigal

"""

# constants
user_fullname = 'Sebastien de Larquier'
user_email = 'sdelarquier@vt.edu'
user_affiliation = 'Virginia Tech'

#####################################################
#####################################################
class fetchData(object):
	"""Read Millstone Hill data, either locally if it can be found, or directly from Madrigal

	**Args**:
		* **expDate** (datetime.datetime): experiment date
		* **[endDate]** (datetime.datetime): end date/time to look for experiment files on Madrigal
		* **[getMad]** (bool): force download from Madrigal (overwrite any matching local file)
		* **[dataPath]** (str): path where the local data should be read/saved
		* **[fileExt]** (str): file extension (i.e., 'g.002'). If None is provided, it will just look for the most recent available one
		* **user_fullname** (str): required to download data from Madrigal (no registration needed)
		* **user_email** (str): required to download data from Madrigal (no registration needed)
		* **user_affiliation** (str): required to download data from Madrigal (no registration needed)
		* **inst_id** (int): required to specify instrument to download data for. See list of Instrument IDs.

	**Instrument IDs**
		* **Jicamarca**: 10
		* **Jicamarca Bistatic**: 11
		* **Arecibo - Linefeed**: 20
		* **Arecibo - Gregorian**: 21
		* **Arecibo - Velocity Vector**: 22
		* **MU IS radar**: 25
		* **Millstone Hill IS Radar**: 30
		* **Millstone Hill UHF Zenith**: 32
		* **St. Santin IS Radar**: 40
		* **St. Nancay Receiver**: 41
		* **Kharkov Ukraine IS Radar**: 45
		* **Chatanika IS Radar**: 50
		* **ISTP Irkutsk Radar**: 53
		* **Poker Flat IS Radar**: 61
		* **EISCAT combined IS Radars**: 70 (not yet implemented)
		* **EISCAT Kiruna UHF Receiver**: 71
		* **EISCAT Tromso UHF Receiver**: 72
		* **EISCAT Sodankyla UHF Receiver**: 73
		* **EISCAT Tromso VHF IS Receiver**: 74
		* **Sondestrum IS Radar**: 80
		* **Resolute Bay North IS Radar**: 91
		* **EISCAT Svalbard IS Radar**: 95



	**Example**:
		::

			# Get data for November 17-18, 2010
			import datetime as dt
			user_fullname = 'Sebastien de Larquier'
			user_email = 'sdelarquier@vt.edu'
			user_affiliation = 'Virginia Tech'
			date = dt.datetime(2010,11,17,20)
			edate = dt.datetime(2010,11,18,13)
			inst_id = 30
			filePath = fetchData( date, endDate=edate, 
				 user_fullname=user_fullname, 
				 user_email=user_email, 
				 user_affiliation=user_affiliation,
				 inst_id=inst_id )
					
	Adapted by Ashton Reimer 2013-07
	from code by Sebastien de Larquier, 2013-03
	"""
	def __init__(self, expDate, endDate=None, 
		dataPath=None, fileExt=None, inst_id=None, #getMad=False, 
		user_fullname=None, user_email=None, user_affiliation=None):

		self.expDate = expDate
		self.endDate = endDate
		self.dataPath = dataPath
		self.fileExt = fileExt
		self.inst_id = inst_id

		if None in [user_fullname, user_email, user_affiliation, inst_id]:
			print 'Error: Please provide user_fullname, user_email, user_affiliation, and inst_id.'
			return
		filePath = self.getFileMad(user_fullname, user_email, user_affiliation)

		self.filePath = filePath
		


	def getFileMad(self, user_fullname, user_email, user_affiliation):
		"""Look for the desired ISR data on Madrigal
		
		**Belongs to**: :class:`fetchData`

		**Returns**:
			* **filePath**: the path and name of the data file
		"""
		import madrigalWeb.madrigalWeb
		import os, h5py, numpy, datetime
		from matplotlib.dates import date2num, epoch2num, num2date

		madrigalUrl = 'http://cedar.openmadrigal.org'
		madData = madrigalWeb.madrigalWeb.MadrigalData(madrigalUrl)

		#Instrument ID
		inst_id = self.inst_id

		# Start and end date/time
		sdate = self.expDate
		fdate = self.endDate if self.endDate else sdate + datetime.timedelta(days=1)

		# Get experiment list
		expList = madData.getExperiments(inst_id, 
			sdate.year, sdate.month, sdate.day, sdate.hour, 
			sdate.minute, sdate.second, 
			fdate.year, fdate.month, fdate.day, fdate.hour, 
			fdate.minute, fdate.second)
		if not expList: return

		# Try to get the default file
		thisFilename = False
		fileList = madData.getExperimentFiles(expList[0].id)
		for thisFile in fileList:
		    if thisFile.category == 1:
		        thisFilename = thisFile.name
		        break
		if not thisFilename: return

		# Download HDF5 file
		result = madData.downloadFile(thisFilename, 
			os.path.join( self.dataPath,"{}.hdf5"\
			.format(os.path.split(thisFilename)[1]) ), 
			user_fullname, user_email, user_affiliation, 
			format="hdf5")

		# Now add some derived data to the hdf5 file
		res = madData.isprint(thisFilename, 
			'YEAR,MONTH,DAY,HOUR,MIN,SEC,RANGE,GDALT,NE,NEL,MDTYP,GDLAT,GLON',
	 		'', user_fullname, user_email, user_affiliation)

		rows = res.split("\n") 
		filePath = os.path.join( self.dataPath,
			os.path.split(thisFilename)[1]+'.hdf5' )
		self.fileExt = ( os.path.split(thisFilename)[1] )[-1]
		# Add new datasets to hdf5 file
                	
		return filePath

