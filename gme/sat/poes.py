"""
.. module:: poes
   :synopsis: A module for reading, writing, and storing poes Data

.. moduleauthor:: AJ, 20130129

*********************
**Module**: gme.sat.poes
*********************
**Classes**:
	* :class:`poesRec`
**Functions**:
	* :func:`readPoes`
	* :func:`readPoesFtp`
	* :func:`mapPoesMongo`
"""

import gme
class poesRec(gme.base.gmeBase.gmeData):
	"""a class to represent a record of poes data.  Extends :class:`gmeBase.gmeData`.  Insight on the class members can be obtained from `the NOAA NGDC site <ftp://satdat.ngdc.noaa.gov/sem/poes/data/readme.txt>`_.  Note that Poes data is available from 1998-present day (or whatever the latest NOAA has uploaded is).  **The data are the 16-second averages**
	
	**Members**: 
		* **time** (`datetime <http://tinyurl.com/bl352yx>`_): an object identifying which time these data are for
		* **info** (str): information about where the data come from.  *Please be courteous and give credit to data providers when credit is due.*
		* **dataSet** (str): the name of the data set
		* **satnum** (ind): the noaa satellite number
		* **sslat** (float): Geographic Latitude of sub-satellite point, degrees
		* **sslon** (float): Geographic Longitude of sub-satellite point, degrees
		* **folat** (float): Geographic Latitude of foot-of-field-line, degrees
		* **folon** (float): Geographic Longitude of foot-of-field-line, degrees
		* **lval** (float): L-value
		* **mlt** (float): Magnetic local time of foot-of-field-line, degrees
		* **pas0** (float): MEPED-0 pitch angle at satellite, degrees
		* **pas90** (float): MEPED-90 pitch angle at satellite, degrees
		* **mep0e1** (float): MEPED-0 > 30 keV electrons, counts/sec
		* **mep0e2** (float): MEPED-0 > 100 keV electrons, counts/sec
		* **mep0e3** (float): MEPED-0 > 300 keV electrons, counts/sec
		* **mep0p1** (float):MEPED-0 30 keV to 80 keV protons, counts/sec
		* **mep0p2** (float): MEPED-0 80 keV to 240 keV protons, counts/sec
		* **mep0p3** (float): 240 kev to 800 keV protons, counts/sec
		* **mep0p4** (float): MEPED-0 800 keV to 2500 keV protons, counts/sec
		* **mep0p5** (float): MEPED-0 2500 keV to 6900 keV protons, counts/sec
		* **mep0p6** (float): MEPED-0 > 6900 keV protons, counts/sec,
		* **mep90e1** (float): MEPED-90 > 30 keV electrons, counts/sec,
		* **mep90e2** (float): MEPED-90 > 100 keV electrons, counts/sec
		* **mep90e3** (float): MEPED-90 > 300 keV electrons, counts/sec
		* **mep90p1** (float): MEPED-90 30 keV to 80 keV protons, counts/sec
		* **mep90p2** (float): MEPED-90 80 keV to 240 keV protons, counts/sec
		* **mep90p3** (float): MEPED-90 240 kev to 800 keV protons, counts/sec,
		* **mep90p4** (float): MEPED-90 800 keV to 2500 keV protons, counts/sec
		* **mep90p5** (float): MEPED-90 2500 keV to 6900 keV protons, counts/sec
		* **mep90p6** (float):MEPED-90 > 6900 keV protons, counts/sec
		* **mepomp6** (float): MEPED omni-directional > 16 MeV protons, counts/sec
		* **mepomp7** (float): MEPED omni-directional > 36 Mev protons, counts/sec
		* **mepomp8** (float): MEPED omni-directional > 70 MeV protons, counts/sec
		* **mepomp9** (float): MEPED omni-directional >= 140 MeV protons
		* **ted** (float): TED, Total Energy Detector Average, ergs/cm2/sec
		* **echar** (float): TED characteristic energy of electrons, eV
		* **pchar** (float): TED characteristic energy of protons, eV
		* **econtr** (float): TED electron contribution, Electron Energy/Total Energy
		
		
	.. note::
		If any of the members have a value of None, this means that they could not be read for that specific time
   
	**Methods**:
		* :func:`parseFtp`
	**Example**:
		::
		
			emptyPoesObj = gme.sat.poesRec()
		
	written by AJ, 20130131
	"""
	
	def parseFtp(self,line, header):
		"""This method is used to convert a line of poes data read from the NOAA NGDC FTP site into a :class:`poesRec` object.
		
		.. note::
			In general, users will not need to worry about this.
		
		**Belongs to**: :class:`poesRec`
		
		**Args**: 
			* **line** (str): the ASCII line from the FTP server
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myPoesObj.parseFtp(ftpLine)
			
		written by AJ, 20130131
		"""
		import datetime as dt
		
		#split the line into cols
		cols = line.split()
		head = header.split()
		self.time = dt.datetime(int(cols[0]), int(cols[1]), int(cols[2]), int(cols[3]),int(cols[4]), \
														int(float(cols[5])),int(round((float(cols[5])-int(float(cols[5])))*1e6)))
		
		for key in self.__dict__.iterkeys():
			if(key == 'dataSet' or key == 'info' or key == 'satnum' or key == 'time'): continue
			try: ind = head.index(key)
			except Exception,e:
				print e
				print 'problem setting attribute',key
			#check for a good value
			if(cols[ind] != -999.): setattr(self,key,float(cols[ind]))
	
	def __init__(self, ftpLine=None, dbDict=None, satnum=None, header=None):
		"""the intialization fucntion for a :class:`omniRec` object.  
		
		.. note::
			In general, users will not need to worry about this.
		
		**Belongs to**: :class:`omniRec`
		
		**Args**: 
			* [**ftpLine**] (str): an ASCII line from the FTP server. if this is provided, the object is initialized from it.  header must be provided in conjunction with this.  default=None
			* [**header**] (str): the header from the ASCII FTP file.  default=None
			* [**dbDict**] (dict): a dictionary read from the mongodb.  if this is provided, the object is initialized from it.  default = None
			* [**satnum**] (int): the satellite nuber.  default=None
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myPoesObj = poesRec(ftpLine=aftpLine)
			
		written by AJ, 20130131
		"""
		#note about where data came from
		self.dataSet = 'Poes'
		self.info = 'These data were downloaded from NASA SPDF.  *Please be courteous and give credit to data providers when credit is due.*'
		self.satnum = satnum
		self.sslat = None
		self.sslon = None
		self.folat = None
		self.folon = None
		self.lval = None
		self.mlt = None
		self.pas0 = None
		self.pas90 = None
		self.mep0e1 = None
		self.mep0e2 = None
		self.mep0e3 = None
		self.mep0p1 = None
		self.mep0p2 = None
		self.mep0p3 = None
		self.mep0p4 = None
		self.mep0p5 = None
		self.mep0p6 = None
		self.mep90e1 = None
		self.mep90e2 = None
		self.mep90e3 = None
		self.mep90p1 = None
		self.mep90p2 = None
		self.mep90p3 = None
		self.mep90p4 = None
		self.mep90p5 = None
		self.mep90p6 = None
		self.mepomp6 = None
		self.mepomp7 = None
		self.mepomp8 = None
		self.mepomp9 = None
		self.ted = None
		self.echar = None
		self.pchar = None
		self.econtr = None
		
		#if we're initializing from an object, do it!
		if(ftpLine != None): self.parseFtp(ftpLine,header)
		if(dbDict != None): self.parseDb(dbDict)
		
def readPoes(sTime,eTime=None,satnum=None,folat=None,folon=None,ted=None,echar=None,pchar=None):
	"""This function reads poes data.  First, it will try to get it from the mongodb, and if it can't find it, it will look on the NOAA NGDC FTP server using :func:`readPoesFtp`.  The data are 16-second averages

	**Args**: 
		* **sTime** (`datetime <http://tinyurl.com/bl352yx>`_ or None): the earliest time you want data for
		* [**eTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the latest time you want data for.  if this is None, end Time will be 1 day after sTime.  default = None
		* [**satnum**] (int): the satellite you want data for.  eg 17 for noaa17.  if this is None, data for all satellites will be returned.  default = None
		* [**satnum**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with bx values in the range [a,b] will be returned.  default = None
		* [**folat**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with bx values in the range [a,b] will be returned.  default = None
		* [**folon**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with bye values in the range [a,b] will be returned.  default = None
		* [**ted**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with bze values in the range [a,b] will be returned.  default = None
		* [**echar**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with bym values in the range [a,b] will be returned.  default = None
		* [**pchar**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with bzm values in the range [a,b] will be returned.  default = None
		
	**Returns**:
		* **poesList** (list or None): if data is found, a list of :class:`poesRec` objects matching the input parameters is returned.  If no data is found, None is returned.
	**Example**:
		::
		
			import datetime as dt
			poesList = gme.sat.readPoes(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),folat=[60,80])
		
	written by AJ, 20130131
	"""
	
	import datetime as dt
	import pydarn.sdio.dbUtils as db
	
	#check all the inputs for validity
	assert(isinstance(sTime,dt.datetime)), \
		'error, sTime must be a datetime object'
	assert(eTime == None or isinstance(eTime,dt.datetime)), \
		'error, eTime must be either None or a datetime object'
	assert(satnum == None or isinstance(satnum,int)), 'error, satnum must be an int'
	var = locals()
	for name in ['folat','folon','ted','echar','pchar']:
		assert(var[name] == None or (isinstance(var[name],list) and \
			isinstance(var[name][0],(int,float)) and isinstance(var[name][1],(int,float)))), \
			'error,'+name+' must None or a list of 2 numbers'
		
	if(eTime == None): eTime = sTime+dt.timedelta(days=1)
	qryList = []
	#if arguments are provided, query for those
	qryList.append({'time':{'$gte':sTime}})
	if(eTime != None): qryList.append({'time':{'$lte':eTime}})
	if(satnum != None): qryList.append({'satnum':satnum})
	var = locals()
	for name in ['folat','folon','ted','echar','pchar']:
		if(var[name] != None): 
			qryList.append({name:{'$gte':min(var[name])}})
			qryList.append({name:{'$lte':max(var[name])}})
			
	#construct the final query definition
	qryDict = {'$and': qryList}
	#connect to the database
	poesData = db.getDataConn(dbName='gme',collName='poes')
	
	#do the query
	if(qryList != []): qry = poesData.find(qryDict)
	else: qry = poesData.find()
	if(qry.count() > 0):
		poesList = []
		for rec in qry.sort('time'):
			poesList.append(poesRec(dbDict=rec))
		print '\nreturning a list with',len(poesList),'records of poes data'
		return poesList
	#if we didn't find anything on the mongodb
	else:
		print '\ncould not find requested data in the mongodb'
		print 'we will look on the ftp server, but your conditions will be (mostly) ignored'
		
		#read from ftp server
		poesList = readPoesFtp(sTime, eTime)
		
		if(poesList != None):
			print '\nreturning a list with',len(poesList),'recs of poes data'
			return poesList
		else:
			print '\n no data found on FTP server, returning None...'
			return None
			
def readPoesFtp(sTime,eTime=None):
	"""This function reads poes data from the NOAA NGDC server via anonymous FTP connection.
	
	.. warning::
		You should not use this. Use the general function :func:`readPoes` instead.
	
	**Args**: 
		* **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the earliest time you want data for
		* [**eTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the latest time you want data for.  if this is None, eTime will be equal 1 day after sTime.  default = None
	**Returns**:
		* **poesList** (list or None): if data is found, a list of :class:`poesRec` objects matching the input parameters is returned.  If no data is found, None is returned.
	**Example**:
		::
		
			import datetime as dt
			poesList = gme.sat.readpoesFtp(dt.datetime(2011,1,1,1,50),eTime=dt.datetime(2011,1,1,10,0))
		
	written by AJ, 20130128
	"""
	
	from ftplib import FTP
	import datetime as dt
	
	assert(isinstance(sTime,dt.datetime)),'error, sTime must be datetime'
	if(eTime == None): eTime=sTime+dt.timedelta(days=1)
	assert(isinstance(eTime,dt.datetime)),'error, eTime must be datetime'
	assert(eTime >= sTime), 'error, end time greater than start time'
	
	#connect to the server
	try: ftp = FTP('satdat.ngdc.noaa.gov')	
	except Exception,e:
		print e
		print 'problem connecting to NOAA server'
		return None
		
	#login as anonymous
	try: l=ftp.login()
	except Exception,e:
		print e
		print 'problem logging in to NOAA server'
		return None
		
	myPoes = []
	#get the poes data
	myTime = dt.datetime(sTime.year,sTime.month,sTime.day)
	while(myTime <= eTime):
		#go to the data directory
		try: ftp.cwd('/sem/poes/data/avg/txt/'+str(myTime.year))
		except Exception,e:
			print e
			print 'error getting to data directory'
			return None
		
		#list directory contents
		dirlist = ftp.nlst()
		for dire in dirlist:
			#check for satellite directory
			if(dire.find('noaa') == -1): continue
			satnum = dire.replace('noaa','')
			#chege to file directory
			ftp.cwd('/sem/poes/data/avg/txt/'+str(myTime.year)+'/'+dire)
			fname = 'poes_n'+satnum+'_'+myTime.strftime("%Y%m%d")+'.txt'
			print 'poes: RETR '+fname
			#list to hold the lines
			lines = []
			#get the data
			try: ftp.retrlines('RETR '+fname,lines.append)
			except Exception,e:
				print e
				print 'error retrieving',fname
				
			#convert the ascii lines into a list of poesRec objects
			#skip first (header) line
			for line in lines[1:]:
				cols = line.split()
				t = dt.datetime(int(cols[0]), int(cols[1]), int(cols[2]), int(cols[3]),int(cols[4]))
				if(sTime <= t <= eTime):
					myPoes.append(poesRec(ftpLine=line,satnum=int(satnum),header=lines[0]))
				
		#increment myTime
		myTime += dt.timedelta(days=1)
	
	if(len(myPoes) > 0): return myPoes
	else: return None
	

def mapPoesMongo(sYear,eYear=None):
	"""This function reads poes data from the NOAA NGDC FTP server via anonymous FTP connection and maps it to the mongodb.  
	
	.. warning::
		In general, nobody except the database admins will need to use this function
	
	**Args**: 
		* **sYear** (int): the year to begin mapping data
		* [**eYear**] (int or None): the end year for mapping data.  if this is None, eYear will be sYear
	**Returns**:
		* Nothing.
	**Example**:
		::
		
			gme.sat.mapPoesMongo(2004)
		
	written by AJ, 20130131
	"""
	import pydarn.sdio.dbUtils as db
	import os, datetime as dt
	
	#check inputs
	assert(isinstance(sYear,int)),'error, sYear must be int'
	if(eYear == None): eYear=sYear
	assert(isinstance(eYear,int)),'error, sYear must be None or int'
	assert(eYear >= sYear), 'error, end year greater than start year'
	
	#get data connection
	mongoData = db.getDataConn(username=os.environ['DBWRITEUSER'],password=os.environ['DBWRITEPASS'],\
								dbAddress=os.environ['SDDB'],dbName='gme',collName='poes')
	
	#set up all of the indices
	mongoData.ensure_index('time')
	mongoData.ensure_index('satnum')
	mongoData.ensure_index('folat')
	mongoData.ensure_index('folon')
	mongoData.ensure_index('ted')
	mongoData.ensure_index('echar')
	mongoData.ensure_index('pchar')
		
	#read the poes data from the FTP server
	myTime = dt.datetime(sYear,1,1)
	while(myTime < dt.datetime(eYear+1,1,1)):
		#10 day at a time, to not fill up RAM
		templist = readPoesFtp(myTime,myTime+dt.timedelta(days=10))
		if(templist == None): continue
		for rec in templist:
			#check if a duplicate record exists
			qry = mongoData.find({'$and':[{'time':rec.time},{'satnum':rec.satnum}]})
			print rec.time, rec.satnum
			tempRec = rec.toDbDict()
			cnt = qry.count()
			#if this is a new record, insert it
			if(cnt == 0): mongoData.insert(tempRec)
			#if this is an existing record, update it
			elif(cnt == 1):
				print 'foundone!!'
				dbDict = qry.next()
				temp = dbDict['_id']
				dbDict = tempRec
				dbDict['_id'] = temp
				mongoData.save(dbDict)
			else:
				print 'strange, there is more than 1 record for',rec.time
		del templist
		myTime += dt.timedelta(days=10)

	