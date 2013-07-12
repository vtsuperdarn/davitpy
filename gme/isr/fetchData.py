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
userFullname = 'Sebastien de Larquier'
userEmail = 'sdelarquier@vt.edu'
userAffiliation = 'Virginia Tech'

#####################################################
#####################################################
class fetchData(object):
	"""Read Millstone Hill data, either locally if it can be found, or directly from Madrigal

	**Args**:
		* **expDate** (datetime.datetime): experiment date
		* **[endDate]** (datetime.datetime): end date/time to look for experiment files on Madrigal
		* **[listOfParams]** (str): a string containing a list of parameters to download
		* **[dataPath]** (str): path where the local data should be read/saved
		* **[fileExt]** (str): file extension (i.e., 'g.002'). If None is provided, it will just look for the most recent available one
		* **userFullname** (str): required to download data from Madrigal (no registration needed)
		* **userEmail** (str): required to download data from Madrigal (no registration needed)
		* **userAffiliation** (str): required to download data from Madrigal (no registration needed)
		* **instId** (int): required to specify instrument to download data for. See list of Instrument IDs.
		* **sriFile** (str): path and filename of SRI International hdf5 file to import

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
		* **EISCAT combined IS Radars**: 70
		* **EISCAT Kiruna UHF Receiver**: 71
		* **EISCAT Tromso UHF Receiver**: 72
		* **EISCAT Sodankyla UHF Receiver**: 73
		* **EISCAT Tromso VHF IS Receiver**: 74
		* **Sondestrum IS Radar**: 80
		* **Resolute Bay North IS Radar**: 91
		* **EISCAT Svalbard IS Radar**: 95



	**HDF5 Example**:
		::

			# Get data for November 17-18, 2010
			import datetime as dt
			userFullname = 'Sebastien de Larquier'
			userEmail = 'sdelarquier@vt.edu'
			userAffiliation = 'Virginia Tech'
			date = dt.datetime(2010,11,17,20)
			edate = dt.datetime(2010,11,18,13)
			instId = 30
			filePath = fetchData( date, endDate=edate, 
				 getHdf5=True
				 userFullname=userFullname, 
				 userEmail=userEmail, 
				 userAffiliation=userAffiliation,
				 instId=instId )
	**isPrint Example**:
		::

			# Get data for November 17-18, 2010
			import datetime as dt
			userFullname = 'Sebastien de Larquier'
			userEmail = 'sdelarquier@vt.edu'
			userAffiliation = 'Virginia Tech'
			date = dt.datetime(2010,11,17,20)
			edate = dt.datetime(2010,11,18,13)
			instId = 30
			listOfParams='YEAR,MONTH,DAY,HOUR,MIN,SEC,GDALT,GDLAT,GDLON,NE'
			filePath = fetchData( date, endDate=edate, 
				 listOfParams=listOfParams
				 userFullname=userFullname, 
				 userEmail=userEmail, 
				 userAffiliation=userAffiliation,
				 instId=instId )
				
	Adapted by Ashton Reimer 2013-07
	from code by Sebastien de Larquier, 2013-03
	"""
	def __init__(self, expDate, endDate=None, listOfParams=None,getHdf5=None,
		dataPath=None, fileExt=None, instId=None, sriFile=None, 
		userFullname=None, userEmail=None, userAffiliation=None):

		self.expDate = expDate
		self.endDate = endDate
		self.dataPath = dataPath
		self.fileExt = fileExt
		self.instId = instId

		if None in [userFullname, userEmail, userAffiliation, instId]:
			print 'Error: Please provide userFullname, userEmail, userAffiliation, and instId.'
			return





		if getHdf5:
			self.getHdf5=True
			filePath = self.getDataMadHdf5( userFullname, userEmail, userAffiliation)
		else:
			self.getIsPrint=True
			filePath = self.getDataMadIsPrint(listOfParams, userFullname, userEmail, userAffiliation)

		self.filePath = filePath

	def getDataMadHdf5(self, userFullname, userEmail, userAffiliation):
		"""Look for the desired ISR data on Madrigal and download hdf5 file
		
		**Belongs to**: :class:`fetchData`

		**Returns**:
			* **filePath**: the path and name of the data file
		"""
		import madrigalWeb.madrigalWeb
		import os, numpy, datetime
		from matplotlib.dates import date2num, epoch2num, num2date

		madrigalUrl = 'http://cedar.openmadrigal.org'
		madData = madrigalWeb.madrigalWeb.MadrigalData(madrigalUrl)

		#Instrument ID
		instId = self.instId

		# Start and end date/time
		sdate = self.expDate
		fdate = self.endDate if self.endDate else sdate + datetime.timedelta(days=1)

		# Get experiment list
		expList = madData.getExperiments(instId, 
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
			userFullname, userEmail, userAffiliation, 
			format="hdf5")
		ext='.hdf5'

		filePath = os.path.join( self.dataPath,
			os.path.split(thisFilename)[1]+ext )

		return filePath

	def getDataMadIsPrint(self, listOfParams, userFullname, userEmail, userAffiliation):
		"""Look for the desired ISR data on Madrigal and download it with isPrint
		
		**Belongs to**: :class:`fetchData`

		**Returns**:
			* **filePath**: the path and name of the data file
		"""
		import madrigalWeb.madrigalWeb
		import os, pickle, numpy, datetime
		from matplotlib.dates import date2num, epoch2num, num2date

		madrigalUrl = 'http://cedar.openmadrigal.org'
		madData = madrigalWeb.madrigalWeb.MadrigalData(madrigalUrl)

		#Instrument ID
		instId = self.instId

		# Start and end date/time
		sdate = self.expDate
		fdate = self.endDate if self.endDate else sdate + datetime.timedelta(days=1)

		# Get experiment list
		expList = madData.getExperiments(instId, 
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

		# Use isPrint to get data then pickle it

		if not listOfParams:
			params=madData.getExperimentFileParameters(thisFilename)
			listofparams=",".join([t.mnemonic for t in params])

		# Now get the data
		res = madData.isprint(thisFilename, 
			listOfParams,'', userFullname, userEmail, userAffiliation)

		rows = res.split("\n") 
		if not self.dataPath: self.dataPath=''
		self.fileExt = ( os.path.split(thisFilename)[1] )[-1]
		self.res=res                
		self.rows=rows
		self.thisFilename=thisFilename	

		#Now that we have the data, create a dictionary of it
		params=listOfParams.split(",")
		data={}
		for p in params:
			data[p]=numpy.array([])
		for r in rows:
			if r=='': continue
			dat=r.split()
			j=0
			for p in params:
				if dat[j]=='missing': dat[j]=numpy.nan
				data[p]=numpy.concatenate((data[p],[float(dat[j])]))
				j=j+1

		ext='.p'
		filePath = os.path.join( self.dataPath,
			os.path.split(thisFilename)[1]+ext )


		#Then save the dictionary to a file using pickle if necessary
		pickle.dump(data,open(filePath,'wb'))

		return filePath

