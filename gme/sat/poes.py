"""
.. module:: poes
   :synopsis: A module for reading, writing, and storing poes Data

.. moduleauthor:: AJ, 20130129

*********************
**Module**: gmi.sat.poes
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
	"""a class to represent a record of poes data.  Extends gmeData.  Insight on the class members can be obtained from `the NOAA NGDC site <ftp://satdat.ngdc.noaa.gov/sem/poes/data/readme.txt>`_.  Note that Poes data is available from 1998-present day (or whatever the latest NOAA has uploaded is).
	"""
	
	def parseFtp(self,line, header):
		import datetime as dt
		
		#split the line into cols
		cols = line.split()
		head = header.split()
		
		##print line
		#print cols
		self.time = dt.datetime(int(cols[0]), int(cols[1]), int(cols[2]), int(cols[3]),int(cols[4]))
		
		for key in self.__dict__.iterkeys():
			if(key == 'dataSet' or key == 'info' or key == 'satnum' or key == 'time'): continue
			try: ind = head.index(key)
			except Exception,e:
				print e
				print 'problem setting attribute',key
			#check for a good value
			if(cols[ind] != -999.): setattr(self,key,float(cols[ind]))
	
	def __init__(self, ftpLine=None, dbDict=None, satnum=None, header=None):
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
		
def readPoesFtp(sTime,eTime=None):
	"""This function reads poes data from the NOAA NGDC server via anonymous FTP connection.
	"""
	
	from ftplib import FTP
	import datetime as dt
	
	assert(isinstance(sTime,dt.datetime)),'error, sTime must be datetime'
	if(eTime == None): eTime=sTime
	assert(isinstance(eTime,dt.datetime)),'error, eTime must be datetime'
	assert(eTime >= sTime), 'error, end time greater than start time'
	
	#connect to the server
	try: ftp = FTP('satdat.ngdc.noaa.gov')	
	except Exception,e:
		print e
		print 'problem connecting to SPDF server'
		return None
		
	#login as anonymous
	try: l=ftp.login()
	except Exception,e:
		print e
		print 'problem logging in to SPDF server'
		return None
		
	myPoes = []
	#get the poes data
	myTime = sTime
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
			print 'RETR '+fname
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
				myPoes.append(poesRec(ftpLine=line,satnum=int(satnum),header=lines[0]))
				
		#increment myTime
		myTime += dt.timedelta(days=1)
	
	if(len(myPoes) > 0): return myPoes
	else: return None
	

def mapPoesMongo(sYear,eYear=None):
	import pydarn.sdio.dbUtils as db
	import os, datetime as dt
	
	#check inputs
	assert(isinstance(sYear,int)),'error, sYear must be int'
	if(eYear == None): eYear=sYear
	assert(isinstance(eYear,int)),'error, sYear must be None or int'
	assert(eYear >= sYear), 'error, end year greater than start year'
	
	#get data connection
	mongoData = db.getDataConn(username=os.environ['DBWRITEUSER'],password=os.environ['DBWRITEPASS'],\
								dbAddress=os.environ['SDDB'],dbName='gmi',collName='poes')
	
	#set up all of the indices
	mongoData.ensure_index('time')
	mongoData.ensure_index('ssnum')
	mongoData.ensure_index('folat')
	mongoData.ensure_index('folon')
	mongoData.ensure_index('ted')
	mongoData.ensure_index('echar')
	mongoData.ensure_index('pchar')
		
	#read the poes data from the FTP server
	for yr in range(sYear,eYear+1):
		templist = readPoesFtp(dt.datetime(yr,1,1), dt.datetime(yr,12,31,23,59,59,99999))
		for rec in templist:
			#check if a duplicate record exists
			qry = mongoData.find({'$and':[{'time':rec.time},{'satnum':rec.satnum}]})
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
		del templist
	
	