"""
.. module:: ae
   :synopsis: A module for reading, writing, and storing ae Data

.. moduleauthor:: AJ, 20130131

*********************
**Module**: gme.ind.ae
*********************
**Classes**:
	* :class:`aeRec`
**Functions**:
	* :func:`readAe`
	* :func:`readAeWeb`
	* :func:`mapAeMongo`
"""

import gme
class aeRec(gme.base.gmeBase.gmeData):
	"""a class to represent a record of ae data.  Extends :class:`gmeBase.gmeData` . Note that Ae data is available from 1980-present day (or whatever the latest WDC has uploaded is).  **The data are 1-minute values**.  Information about dst can be found `here <http://wdc.kugi.kyoto-u.ac.jp/aedir/ae2/onAEindex.html>`_
		
	**Members**: 
		* **time** (`datetime <http://tinyurl.com/bl352yx>`_): an object identifying which time these data are for
		* **dataSet** (:class:`dst.dstRec`)): a string dicating the dataset this is from
		* **info** (str): information about where the data come from.  *Please be courteous and give credit to data providers when credit is due.*
		* **ae** (float): auroral electrojet
		* **au** (float): auroral upper
		* **ae** (float): auroral lower
		* **ao** (float): mean of al and au
	.. note::
		If any of the members have a value of None, this means that they could not be read for that specific time
   
	**Methods**:
		* :func:`parseWeb`
	**Example**:
		::
		
			emptyAeObj = gme.ind.aeRec()
		
	written by AJ, 20130131
	"""
	
	def parseWeb(self,line):
		"""This method is used to convert a line of ae data from the WDC to a aeRec object
		
		.. note::
			In general, users will not need to worry about this.
		
		**Belongs to**: :class:`aeRec`
		
		**Args**: 
			* **line** (str): the ASCII line from the WDC data file
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myAeObj.parseWeb(webLine)
			
		written by AJ, 20130131
		"""
		import datetime as dt
		cols = line.split()
		self.time = dt.datetime(int(cols[0][0:4]),int(cols[0][5:7]),int(cols[0][8:10]), \
															int(cols[1][0:2]),int(cols[1][3:5]),int(cols[1][6:8]))
		if(float(cols[3]) != 99999.0): self.ae = float(cols[3])
		if(float(cols[4]) != 99999.0): self.au = float(cols[4])
		if(float(cols[5]) != 99999.0): self.al = float(cols[5])
		if(float(cols[6]) != 99999.0): self.ao = float(cols[6])
		
	def __init__(self, webLine=None, dbDict=None):
		"""the intialization fucntion for a :class:`aeRec` object.  
		
		.. note::
			In general, users will not need to worry about this.
		
		**Belongs to**: :class:`aeRec`
		
		**Args**: 
			* [**webLine**] (str): an ASCII line from the datafile from WDC. if this is provided, the object is initialized from it.  default=None
			* [**dbDict**] (dict): a dictionary read from the mongodb.  if this is provided, the object is initialized from it.  default = None
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myAeObj = aeRec(webLine=awebLine)
			
		written by AJ, 20130131
		"""
		#note about where data came from
		self.dataSet = 'AE'
		self.time = None
		self.info = 'These data were downloaded from WDC For Geomagnetism, Kyoto.  *Please be courteous and give credit to data providers when credit is due.*'
		self.ae = None
		self.au = None
		self.al = None
		self.ao = None
		
		#if we're initializing from an object, do it!
		if(webLine != None): self.parseWeb(webLine)
		if(dbDict != None): self.parseDb(dbDict)
		
def readAe(sTime=None,eTime=None,ae=None,al=None,au=None,ao=None):
	"""This function reads ae data from the mongodb.  **The data are 1-minute values**
	
	**Args**: 
		* [**sTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the earliest time you want data for, default=None
		* [**eTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the latest time you want data for.  if this is None, end Time will be 1 day after sTime.  default = None
		* [**ae**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with ae values in the range [a,b] will be returned.  default = None
		* [**al**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with al values in the range [a,b] will be returned.  default = None
		* [**au**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with au values in the range [a,b] will be returned.  default = None
		* [**ao**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with ao values in the range [a,b] will be returned.  default = None
	**Returns**:
		* **aeList** (list or None): if data is found, a list of :class:`aeRec` objects matching the input parameters is returned.  If no data is found, None is returned.
	**Example**:
		::
		
			import datetime as dt
			aeList = gme.ind.readAe(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),ao=[-50,50])
		
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
	for name in ['ae','al','au','ao']:
		assert(var[name] == None or (isinstance(var[name],list) and \
			isinstance(var[name][0],(int,float)) and isinstance(var[name][1],(int,float)))), \
			'error,'+name+' must None or a list of 2 numbers'
			
	if(eTime == None and sTime != None): eTime = sTime+dt.timedelta(days=1)
	qryList = []
	#if arguments are provided, query for those
	if(sTime != None): qryList.append({'time':{'$gte':sTime}})
	if(eTime != None): qryList.append({'time':{'$lte':eTime}})
	var = locals()
	for name in ['ae','al','au','ao']:
		if(var[name] != None): 
			qryList.append({name:{'$gte':min(var[name])}})
			qryList.append({name:{'$lte':max(var[name])}})
			
	#construct the final query definition
	qryDict = {'$and': qryList}
	#connect to the database
	aeData = db.getDataConn(dbName='gme',collName='ae')
	
	#do the query
	if(qryList != []): qry = aeData.find(qryDict)
	else: qry = aeData.find()
	if(qry.count() > 0):
		aeList = []
		for rec in qry.sort('time'):
			aeList.append(aeRec(dbDict=rec))
		print '\nreturning a list with',len(aeList),'records of ae data'
		return aeList
	#if we didn't find anything on the mongodb
	else:
		print '\ncould not find requested data in the mongodb'
		return None
			
def readAeWeb(sTime,eTime=None):
	"""This function reads ae data from the WDC kyoto website
	
	.. warning::
		You should not use this. Use the general function :func:`readAe` instead.
	
	**Args**: 
		* **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the earliest time you want data for
		* [**eTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the latest time you want data for.  if this is None, eTime will be equal to sTime.  default = None
	**Example**:
		::
		
			import datetime as dt
			aeList = gme.ind.readAeWeb(dt.datetime(2011,1,1,1,50),eTime=dt.datetime(2011,1,1,10,0))
		
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
	br.form.find_control('Output').value = ['AE']
	br.form.find_control('Out format').value = ['IAGA2002']
	br.form.find_control('Email').value = "vt.sd.sw@gmail.com"
	
	response = br.submit()
	
	lines = response.readlines()

	aeList = []
	for l in lines:
		#check for headers
		if(l[0] == ' ' or l[0:4] == 'DATE'): continue
		cols=l.split()
		try: aeList.append(aeRec(webLine=l))
		except Exception,e:
			print e
			print 'problemm initializing ae object'
		
	if(aeList != []): return aeList
	else: return None

def mapAeMongo(sYear,eYear=None):
	"""This function reads ae data from wdc and puts it in mongodb
	
	.. warning::
		In general, nobody except the database admins will need to use this function
	
	**Args**: 
		* **sYear** (int): the year to begin mapping data
		* [**eYear**] (int or None): the end year for mapping data.  if this is None, eYear will be sYear
	**Returns**:
		* Nothing.
	**Example**:
		::
		
			gme.ind.mapAeMongo(1997)
		
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
								dbAddress=os.environ['SDDB'],dbName='gme',collName='ae')
	
	#set up all of the indices
	mongoData.ensure_index('time')
	mongoData.ensure_index('ae')
	mongoData.ensure_index('al')
	mongoData.ensure_index('au')
	mongoData.ensure_index('ao')
	
	for yr in range(sYear,eYear+1):
		#1 day at a time, to not fill up RAM
		templist = readAeWeb(dt.datetime(yr,1,1),dt.datetime(yr,1,1)+dt.timedelta(days=366))
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
				print 'strange, there is more than 1 AE record for',rec.time
		del templist
	

	