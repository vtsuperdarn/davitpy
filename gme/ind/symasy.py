"""
.. module:: symasy
   :synopsis: A module for reading, writing, and storing symasy Data

.. moduleauthor:: AJ, 20130131

*********************
**Module**: gme.ind.symasy
*********************
**Classes**:
	* :class:`symAsyRec`
**Functions**:
	* :func:`readSymAsy`
	* :func:`readSymAsyWeb`
	* :func:`mapSymAsyMongo`
"""

import gme
class symAsyRec(gme.base.gmeBase.gmeData):
	"""a class to represent a record of sym/asy data.  Extends :class:`gmeBase.gmeData`. Note that sym/asym data is available from 1980-present day (or whatever the latest WDC has uploaded is).  **The data are 1-minute values.**  More info on sym/asy can be found `here <http://wdc.kugi.kyoto-u.ac.jp/aeasy/asy.pdf>`_
		
	**Members**: 
		* **time** (`datetime <http://tinyurl.com/bl352yx>`_): an object identifying which time these data are for
		* **dataSet** (str): a string indicating the dataset this is from
		* **info** (str): information about where the data come from.  *Please be courteous and give credit to data providers when credit is due.*
		* **symh** (float): the symh value
		* **symd** (float): the symd value
		* **asyh** (float): the asyh value
		* **asyd** (float): the asyd value
	.. note::
		If any of the members have a value of None, this means that they could not be read for that specific time
   
	**Methods**:
		* :func:`parseWeb`
	**Example**:
		::
		
			emptySymAsyObj = gme.ind.symAsyRec()
		
	written by AJ, 20130131
	"""
	
	def parseWeb(self,line):
		"""This method is used to convert a line of sym/asy data from the WDC to a symAsyRec object
		
		.. note::
			In general, users will not need to worry about this.
		
		**Belongs to**: :class:`symAsyRec`
		
		**Args**: 
			* **line** (str): the ASCII line from the WDC data file
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				mysymAsyObj.parseWeb(webLine)
			
		written by AJ, 20130131
		"""
		import datetime as dt
		cols = line.split()
		self.time = dt.datetime(int(cols[0][0:4]),int(cols[0][5:7]),int(cols[0][8:10]), \
															int(cols[1][0:2]),int(cols[1][3:5]),int(cols[1][6:8]))
		if(float(cols[3]) != 99999.0): self.asyd = float(cols[3])
		if(float(cols[4]) != 99999.0): self.asyh = float(cols[4])
		if(float(cols[5]) != 99999.0): self.symd = float(cols[5])
		if(float(cols[6]) != 99999.0): self.symh = float(cols[6])
		
	def __init__(self, webLine=None, dbDict=None):
		"""the intialization fucntion for a :class:`symAsyRec` object.  
		
		.. note::
			In general, users will not need to worry about this.
		
		**Belongs to**: :class:`symAsyRec`
		
		**Args**: 
			* [**webLine**] (str): an ASCII line from the datafile from WDC. if this is provided, the object is initialized from it.  default=None
			* [**dbDict**] (dict): a dictionary read from the mongodb.  if this is provided, the object is initialized from it.  default = None
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myDstObj = symAsyRec(webLine=awebLine)
			
		written by AJ, 20130131
		"""
		
		#note about where data came from
		self.dataSet = 'Sym/Asy'
		self.time = None
		self.info = 'These data were downloaded from WDC For Geomagnetism, Kyoto.  *Please be courteous and give credit to data providers when credit is due.*'
		#the indices
		self.symh = None
		self.symd = None
		self.asyh = None
		self.asyd = None
		
		#if we're initializing from an object, do it!
		if(webLine != None): self.parseWeb(webLine)
		if(dbDict != None): self.parseDb(dbDict)
		
def readSymAsy(sTime=None,eTime=None,symh=None,symd=None,asyh=None,asyd=None):
	"""This function reads sym/asy data from the mongodb.
	
	**Args**: 
		* [**sTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the earliest time you want data for, default=None
		* [**eTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the latest time you want data for.  if this is None, end Time will be 1 day after sTime.  default = None
		* [**symh**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with symh values in the range [a,b] will be returned.  default = None
		* [**symd**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with symd values in the range [a,b] will be returned.  default = None
		* [**asyh**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with asyh values in the range [a,b] will be returned.  default = None
		* [**asyd**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with asyd values in the range [a,b] will be returned.  default = None
	**Returns**:
		* **symList** (list or None): if data is found, a list of :class:`symAsyRec` objects matching the input parameters is returned.  If no data is found, None is returned.
	**Example**:
		::
		
			import datetime as dt
			symList = gme.ind.readSymAsy(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),symh=[5,50],asyd=[-10,0])
		
	written by AJ, 20130131
	"""
	import datetime as dt
	import pydarn.sdio.dbUtils as db
	
	#check all the inputs for validity
	assert(sTime == None or isinstance(sTime,dt.datetime)), \
		'error, sTime must be a datetime object'
	assert(eTime == None or isinstance(eTime,dt.datetime)), \
		'error, eTime must be either None or a datetime object'
	var = locals()
	for name in ['symh','symd','asyh','asyd']:
		assert(var[name] == None or (isinstance(var[name],list) and \
			isinstance(var[name][0],(int,float)) and isinstance(var[name][1],(int,float)))), \
			'error,'+name+' must None or a list of 2 numbers'
			
	if(eTime == None and sTime != None): eTime = sTime+dt.timedelta(days=1)
	qryList = []
	#if arguments are provided, query for those
	if(sTime != None): qryList.append({'time':{'$gte':sTime}})
	if(eTime != None): qryList.append({'time':{'$lte':eTime}})
	var = locals()
	for name in ['symh','symd','asyh','asyd']:
		if(var[name] != None): 
			qryList.append({name:{'$gte':min(var[name])}})
			qryList.append({name:{'$lte':max(var[name])}})
			
	#construct the final query definition
	qryDict = {'$and': qryList}
	#connect to the database
	symData = db.getDataConn(dbName='gme',collName='symasy')
	
	#do the query
	if(qryList != []): qry = symData.find(qryDict)
	else: qry = symData.find()
	if(qry.count() > 0):
		symList = []
		for rec in qry.sort('time'):
			symList.append(symAsyRec(dbDict=rec))
		print '\nreturning a list with',len(symList),'records of sym/asy data'
		return symList
	#if we didn't find anything on the mongodb
	else:
		print '\ncould not find requested data in the mongodb'
		return None
			
def readSymAsyWeb(sTime,eTime=None):
	"""This function reads sym/asy data from the WDC kyoto website
	
	.. warning::
		You should not use this. Use the general function :func:`readSymAsy` instead.
	
	**Args**: 
		* **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the earliest time you want data for
		* [**eTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the latest time you want data for.  if this is None, eTime will be equal 1 day after sTime.  This must not be more than 366 days after sTime.  default = None
	**Example**:
		::
		
			import datetime as dt
			symList = gme.ind.readSymAsyWeb(dt.datetime(2011,1,1),eTime=dt.datetime(2011,1,5))
		
	written by AJ, 20130131
	"""
	
	
	import datetime as dt
	import mechanize
	
	assert(isinstance(sTime,dt.datetime)),'error, sTime must be a datetime object'
	if(eTime == None): eTime = sTime+dt.timedelta(days=1)
	assert(isinstance(eTime,dt.datetime)),'error, eTime must be a datetime object'
	assert(eTime >= sTime), 'error, eTime < eTime'
	delt = eTime-sTime
	assert(delt.days <= 366), 'error, cant read more than 366 days'
	
	tens = (sTime.year)/10
	year = sTime.year-tens*10
	month = sTime.strftime("%m")
	dtens = sTime.day/10
	day = sTime.day-dtens*10
	htens = sTime.hour/10
	hour = sTime.hour-htens*10
	ddtens = delt.days/10
	dday = delt.days - ddtens*10
	br = mechanize.Browser()
	br.set_handle_robots(False)   # no robots
	br.set_handle_refresh(False)  # can sometimes hang without this
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
	br.open('http://wdc.kugi.kyoto-u.ac.jp/aeasy/index.html')
	
	br.form = list(br.forms())[0]
	
	#fill out the fields
	br.form.find_control('Tens').value = [str(tens)]
	br.form.find_control('Year').value = [str(year)]
	br.form.find_control('Month').value = [str(month)]
	br.form.find_control('Day_Tens').value = [str(dtens)]
	br.form.find_control('Days').value = [str(day)]
	br.form.find_control('Hour_Tens').value = [str(htens)]
	br.form.find_control('Hour').value = [str(hour)]
	if(ddtens < 9): ddtens = '0'+str(ddtens)
	br.form.find_control('Dur_Day_Tens').value = [str(ddtens)]
	br.form.find_control('Dur_Day').value = [str(dday)]
	br.form.find_control('Output').value = ['ASY']
	br.form.find_control('Out format').value = ['IAGA2002']
	br.form.find_control('Email').value = "vt.sd.sw@gmail.com"
	
	response = br.submit()
	
	#get the data file
	lines = response.readlines()

	symList = []
	for l in lines:
		#check for headers
		if(l[0] == ' ' or l[0:4] == 'DATE'): continue
		cols=l.split()
		try: symList.append(symAsyRec(webLine=l))
		except Exception,e:
			print e
			print 'problem initializing symAsy object'
		
	if(symList != []): return symList
	else: return None

def mapSymAsyMongo(sYear,eYear=None):
	"""This function reads sym/asy data from wdc and puts it in mongodb
	
	.. warning::
		In general, nobody except the database admins will need to use this function
	
	**Args**: 
		* **sYear** (int): the year to begin mapping data
		* [**eYear**] (int or None): the end year for mapping data.  if this is None, eYear will be sYear
	**Returns**:
		* Nothing.
	**Example**:
		::
		
			gme.ind.mapSymAsyMongo(2001)
		
	written by AJ, 20130123
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
								dbAddress=os.environ['SDDB'],dbName='gme',collName='symasy')
	
	#set up all of the indices
	mongoData.ensure_index('time')
	mongoData.ensure_index('symh')
	mongoData.ensure_index('symd')
	mongoData.ensure_index('asyh')
	mongoData.ensure_index('asyd')
	
	for yr in range(sYear,eYear+1):
		#1 day at a time, to not fill up RAM
		templist = readSymAsyWeb(dt.datetime(yr,1,1),dt.datetime(yr,1,1)+dt.timedelta(days=366))
		if(templist == None): continue
		for rec in templist:
			#check if a duplicate record exists
			qry = mongoData.find({'time':rec.time})
			print rec.time
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
				print 'strange, there is more than 1 Sym/Asy record for',rec.time
		del templist
	

	