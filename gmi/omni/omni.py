
class omniRec:
	
	def toDbDict(self):
		dbDict = {}
		for attr, val in self.__dict__.iteritems():
			dbDict[attr] = val
		return dbDict
		
	def parseFtp(self,line):
		import datetime as dt
		
		mappingdict = {9:'timeshift',13:'bMagAvg',14:'bx',15:'bye',16:'bze',17:'bym', \
										18:'bzm',21:'flowSpeed',22:'vxe',23:'vye',24:'vze',25:'np', \
										26:'temp',27:'pDyn',28:'e',29:'beta',30:'machNum',37:'ae', \
										38:'al',39:'au',40:'symd',41:'symh',42:'asyd',43:'asyh'}
										
		cols = line.split()
		self.time = dt.datetime(int(cols[0]), 1, 1, int(cols[2]),int(cols[3])) + \
									dt.timedelta(days=(int(cols[1])-1))
									
		for i in range(9,len(cols)):
			if(not mappingdict.has_key(i)): continue
			temp = cols[i]
			temp = temp.replace('.','')
			temp = temp.replace('9','')
			if(temp == ''): continue
			try: setattr(self,mappingdict[i],float(cols[i]))
			except Exception,e:
				print e
				print 'problem assigning value to',mappingdict[i]
			
	def __init__(self, ftpLine=None, res=None, dbDict=None):
		#note about where data came from
		self.info = 'These data were downloaded from NASA SPDF'
		self.res = res
		self.time = None
		self.timeshift = None
		self.bMagAvg = None
		self.bx = None
		self.bye = None
		self.bze = None
		self.bym = None
		self.bzm = None
		self.flowSpeed = None
		self.vxe = None
		self.vye = None
		self.vze = None
		self.np = None
		self.temp = None
		self.pDyn = None
		self.e = None
		self.beta = None
		self.machNum = None
		self.ae = None
		self.al = None
		self.au = None
		self.symd = None
		self.symh = None
		self.asyd = None
		self.asyh = None
		
		if(ftpLine != None): self.parseFtp(ftpLine)
		
		if(dbDict != None): self.parseDb(dbDict)

def readOmniFtp(sTime,eTime=None,res=1):
	
	from ftplib import FTP
	import datetime as dt
	
	if(eTime == None): eTime=sTime
	assert(eTime >= sTime), 'error, end time greater than start time'
	assert(res == 1 or res == 5), 'error, res must be 1 or 5'
	
	#connect to the server
	try: ftp = FTP('spdf.gsfc.nasa.gov')	
	except Exception,e:
		print e
		print 'problem connecting to SPDF server'
		
	#login as anonymous
	try: l=ftp.login()
	except Exception,e:
		print e
		print 'problem logging in to SPDF server'
	
	#go to the omni directory
	try: ftp.cwd('/pub/data/omni/high_res_omni/')
	except Exception,e:
		print e
		print 'error getting to data directory'
	
	#list to hold the lines
	lines = []
	#get the omni data
	for yr in range(sTime.year,eTime.year+1):
		if(res == 1): fname = 'omni_min'+str(yr)+'.asc'
		else: fname = 'omni_5min'+str(yr)+'.asc'
		print 'RETR '+fname
		ftp.retrlines('RETR '+fname,lines.append)
	
	#convert the ascii lines into a list of omniRec objects
	myOmni = []
	if(len(lines) > 0):
		for l in lines:
			linedate = dt.datetime(int(l[0:4]), 1, 1, int(l[8:11]), int(l[11:14])) + \
									dt.timedelta(int(l[5:8]) - 1)
			if(sTime <= linedate <= eTime):
				myOmni.append(omniRec(ftpLine=l,res=res))
		return myOmni
	else:
		return None
		
def mapOmniMongo(sYear,eYear=None,res=1):

	import pydarn.sdio.dbUtils as db
	import os, datetime as dt
	
	if(eYear == None): eYear=sYear
	assert(eYear >= sYear), 'error, end year greater than start year'
	
	mongoData = db.getDataConn(username=os.environ['DBWRITEUSER'],password=os.environ['DBWRITEPASS'],\
								dbAddress=os.environ['SDDB'],dbName='gmi',collName='omni')
	
	#set up all of the indices
	mongoData.ensure_index('time')
	mongoData.ensure_index('bx')
	mongoData.ensure_index('bye')
	mongoData.ensure_index('bze')
	mongoData.ensure_index('bym')
	mongoData.ensure_index('bzm')
	mongoData.ensure_index('pDyn')
		
	#read the omni data from the FTP server
	templist = readOmniFtp(dt.datetime(sYear,1,1), dt.datetime(eYear,12,31),res=res)
	for rec in templist:
		#check if a duplicate record exists
		qry = mongoData.find({'$and':[{'time':rec.time},{'res':rec.res}]})
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
			print 'strange, there is more than 1 record for',rec.time
	
	