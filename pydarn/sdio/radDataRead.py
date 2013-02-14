"""
.. module:: radDataRead
   :synopsis: A module for reading radar data

.. moduleauthor:: AJ, 20130110

************************************
**Module**: pydarn.sdio.radDataRead
************************************

**Functions**:
	* :func:`radDataOpen`
	* :func:`radDataReadRec`
"""

def radDataOpen(sTime,rad,eTime=None,channel=None,bmnum=None,cp=None,fileType='fitex',filtered=False, src=None,fileName=None,custType='fitex'):
	"""A function to establish a pipeline through which we can read radar data.  first it tries the mongodb, then it tries to find local files, and lastly it sftp's over to the VT data server.

	**Args**:
		* **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the beginning time for which you want data
		* **rad** (str): the 3-letter radar code for which you want data
		* **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): the last time that you want data for.  if this is set to None, it will be set to 1 day after sTime.  default = None
		* **[channel]** (str): the 1-letter code for what channel you want data from, eg 'a','b',...  if this is set to None, data from ALL channels will be read. default = None
		* **[bmnum]** (int): the beam number which you want data for.  If this is set to None, data from all beams will be read. default = None
		* **[cp]** (int): the control program which you want data for.  If this is set to None, data from all cp's will be read.  default = None
		* **[fileType]** (str):  The type of data you want to read.  valid inputs are: 'fitex','fitacf','lmfit','rawacf','iqdat'.   if you choose a fit file format and the specified one isn't found, we will search for one of the others.  Beware: if you ask for rawacf/iq data, these files are large and the data transfer might take a long time.  default = 'fitex'
		* **[filtered]** (boolean): a boolean specifying whether you want the fit data to be boxcar filtered.  ONLY VALID FOR FIT.  default = False
		* **[src]** (str): the source of the data.  valid inputs are 'mongo' 'local' 'sftp'.  if this is set to None, it will try all possibilites sequentially.  default = None
		* **[fileName]** (str): the name of a specific file which you want to open.  default=None
		* **[custType]** (str): if fileName is specified, the filetype of the file.  default='fitex'
	**Returns**:
		* **myPtr** (:class:`radDataTypes.radDataPtr`): a radDataPtr object which contains a link to the data to be read.  this can then be passed to radDataReadRec in order to actually read the data.
		
	**Example**:
		::
		
			import datetime as dt
			myPtr = radDataOpen(dt.datetime(2011,1,1),'bks',eTime=dt.datetime(2011,1,1,2),channel='a', bmnum=7,cp=153,fileType='fitex',filtered=False, src=None):
		
	Written by AJ 20130110
	"""
	import subprocess as sub, paramiko as p, re, string
	import datetime as dt, os, pydarn.sdio, glob
	from pydarn.sdio import radDataPtr
	from pydarn.radar import network
	from utils.timeUtils import datetimeToEpoch
	
	#check inputs
	assert(isinstance(sTime,dt.datetime)), \
		'error, sTime must be datetime object'
	assert(isinstance(rad,str) and len(rad) == 3), \
		'error, rad must be a 3 char string'
	assert(eTime == None or isinstance(eTime,dt.datetime)), \
		'error, eTime must be datetime object or None'
	assert(channel == None or (isinstance(channel,str) and len(channel) == 1)), \
		'error, channel must be None or a 1-letter string'
	assert(bmnum == None or isinstance(bmnum,int)), \
		'error, bmnum must be an int or None'
	assert(cp == None or isinstance(cp,int)), \
		'error, cp must be an int or None'
	assert(fileType == 'rawacf' or fileType == 'fitacf' or \
		fileType == 'fitex' or fileType == 'lmfit' or fileType == 'iqdat'), \
		'error, fileType must be one of: rawacf,fitacf,fitex,lmfit,iqdat'
	assert(fileName == None or isinstance(fileName,str)), \
		'error, fileName must be None or a string'
	assert(isinstance(filtered,bool)), \
		'error, filtered must be True of False'
	assert(src == None or src == 'mongo' or src == 'local' or src == 'sftp'), \
		'error, src must be one of None,local,mongo,sftp'
		
	if(eTime == None):
		eTime = sTime+dt.timedelta(days=1)
		
	#create a datapointer object
	myPtr = radDataPtr(sTime=sTime,eTime=eTime,stid=int(network().getRadarByCode(rad).id),channel=channel,bmnum=bmnum,cp=cp)
	
	filelist = []
	if(fileType == 'fitex'): arr = ['fitex','fitacf','lmfit']
	elif(fileType == 'fitacf'): arr = ['fitacf','fitex','lmfit']
	elif(fileType == 'lmfit'): arr = ['lmfit','fitex','fitacf']
	else: arr = [fileType]
	#move back a little in time because files often start at 2 mins after the hour
	sTime = sTime-dt.timedelta(minutes=4)
	#a temporary directory to store a temporary file
	tmpDir = '/tmp/fit/'
	d = os.path.dirname(tmpDir)
	if not os.path.exists(d):
		os.makedirs(d)

	#FIRST, check if a specific filename was given
	if(fileName != None):
		try:
			if(not os.path.isfile(fileName)):
				print 'problem reading',fileName,':file does not exist'
				return None
			outname = tmpDir+str(int(datetimeToEpoch(dt.datetime.now())))
			if(string.find(fileName,'.bz2') != -1):
				outname = string.replace(fileName,'.bz2','')
				print 'bunzip2 -c '+fileName+' > '+outname+'\n'
				os.system('bunzip2 -c '+fileName+' > '+outname)
			elif(string.find(fileName,'.gz') != -1):
				outname = string.replace(fileName,'.gz','')
				print 'gunzip -c '+fileName+' > '+outname+'\n'
				os.system('gunzip -c '+fileName+' > '+outname)
			else:
				os.system('cp '+fileName+' '+outname)
				print 'cp '+fileName+' '+outname
			filelist.append(outname)
			myPtr.fType,myPtr.dType = custType,'dmap'
		except Exception, e:
			print e
			print 'problem reading file',fileName
			return None
	#Next, LOOK LOCALLY FOR FILES
	if((src == None or src == 'local') and fileName == None):
		try:
			for ftype in arr:
				print '\nLooking locally for',ftype,'files'
				#deal with UAF naming convention
				fnames = ['??.??.???.'+ftype+'.*']
				if(channel == None): fnames.append('??.??.???.a.*')
				else: fnames.append('??.??.???.'+channel+'.*')
				for form in fnames:
					#iterate through all of the hours in the request
					#ie, iterate through all possible file names
					ctime = sTime.replace(minute=0)
					if(ctime.hour % 2 == 1): ctime = ctime.replace(hour=ctime.hour-1)
					while ctime <= eTime:
						#directory on the data server
						##################################################################
						### IF YOU ARE A USER NOT AT VT, YOU PROBABLY HAVE TO CHANGE THIS
						### TO MATCH YOUR DIRECTORY STRUCTURE
						##################################################################
						myDir = '/sd-data/'+ctime.strftime("%Y")+'/'+ftype+'/'+rad+'/'
						hrStr = ctime.strftime("%H")
						dateStr = ctime.strftime("%Y%m%d")
						#iterate through all of the files which begin in this hour
						for filename in glob.glob(myDir+dateStr+'.'+hrStr+form):
							outname = string.replace(filename,myDir,tmpDir)
							#unzip the compressed file
							if(string.find(filename,'.bz2') != -1):
								outname = string.replace(outname,'.bz2','')
								print 'bunzip2 -c '+filename+' > '+outname+'\n'
								os.system('bunzip2 -c '+filename+' > '+outname)
							else:
								outname = string.replace(outname,'.gz','')
								print 'gunzip -c '+filename+' > '+outname+'\n'
								os.system('gunzip -c '+filename+' > '+outname)
							
							filelist.append(outname)
						##################################################################
						### END SECTION YOU WILL HAVE TO CHANGE
						##################################################################
						ctime = ctime+dt.timedelta(hours=1)
					if(len(filelist) > 0):
						print 'found',ftype,'data in local files'
						myPtr.fType,myPtr.dType = ftype,'dmap'
						break
				if(len(filelist) > 0): break
				else:
					print  'could not find',ftype,'data in local files'
		except Exception, e:
			print e
			print 'problem reading local data, perhaps you are not at VT?'
			print 'you probably have to edit radDataRead.py'
			print 'I will try to read from other sources'
			src=None
				
	#NEXT, CHECK IF THE DATA EXISTS IN THE DATABASE
	if((src == None or src == 'mongo') and len(filelist) == 0 and fileName == None):
		for ftype in arr:
			print '\nLooking on mongodb for',ftype,'data'
			myPtr.ptr = pydarn.sdio.readFromDb(sTime=myPtr.sTime, eTime=myPtr.eTime, stid=myPtr.stid, \
									channel=myPtr.channel, bmnum=myPtr.bmnum, cp=myPtr.cp, \
									fileType=fileType,exactFlg=False)
			if(myPtr.ptr != None): 
				print 'found',ftype,'data on mongodb'
				myPtr.dType,myPtr.fType = 'mongo',ftype
				break
			else:
				print  'could not find',ftype,'data on mongodb'
				
	#finally, check the VT sftp server if we have not yet found files
	if((src == None or src == 'sftp') and myPtr.ptr == None and len(filelist) == 0 and fileName == None):
		for ftype in arr:
			print '\nLooking on the remote SFTP server for',ftype,'files'
			try:
				#deal with UAF naming convention
				fnames = ['..........'+ftype]
				if(channel == None): fnames.append('..\...\....\.a\.')
				else: fnames.append('..........'+channel+'.'+ftype)
				for form in fnames:
					#create a transport object for use in sftp-ing
					transport = p.Transport((os.environ['VTDB'], 22))
					transport.connect(username=os.environ['DBREADUSER'],password=os.environ['DBREADPASS'])
					sftp = p.SFTPClient.from_transport(transport)
					
					#iterate through all of the hours in the request
					#ie, iterate through all possible file names
					ctime = sTime.replace(minute=0)
					if(ctime.hour % 2 == 1): ctime = ctime.replace(hour=ctime.hour-1)
					oldyr = ''
					while ctime <= eTime:
						#directory on the data server
						myDir = '/data/'+ctime.strftime("%Y")+'/'+ftype+'/'+rad+'/'
						hrStr = ctime.strftime("%H")
						dateStr = ctime.strftime("%Y%m%d")
						if(ctime.strftime("%Y") != oldyr):
							#get a list of all the files in the directory
							allFiles = sftp.listdir(myDir)
							oldyr = ctime.strftime("%Y")
						#create a regular expression to find files of this day, at this hour
						regex = re.compile(dateStr+'.'+hrStr+form)
						#go thorugh all the files in the directory
						for aFile in allFiles:
							#if we have a file match between a file and our regex
							if(regex.match(aFile)): 
								print 'copying file '+myDir+aFile+' to '+tmpDir+aFile
								filename = tmpDir+aFile
								#download the file via sftp
								sftp.get(myDir+aFile,filename)
								#unzip the compressed file
								if(string.find(filename,'.bz2') != -1):
									outname = string.replace(filename,'.bz2','')
									print 'bunzip2 -c '+filename+' > '+outname+'\n'
									os.system('bunzip2 -c '+filename+' > '+outname)
								elif(string.find(filename,'.gz') != -1):
									outname = string.replace(filename,'.gz','')
									print 'gunzip -c '+filename+' > '+outname+'\n'
									os.system('gunzip -c '+filename+' > '+outname)
								else:
									print 'It seems we have downloaded an uncompressed file :/'
									print 'Strange things might happen from here on out...'
									
								filelist.append(outname)
							
						ctime = ctime+dt.timedelta(hours=1)
					if(len(filelist) > 0):
						print 'found',ftype,'data on sftp server'
						myPtr.fType,myPtr.dType = ftype,'dmap'
						break
				if(len(filelist) > 0): break
				else:
					print  'could not find',ftype,'data on sftp server'
			except Exception,e:
				print e
				print 'problem reading from sftp server'
				
	#check if we have found files
	if(len(filelist) != 0):
		#concatenate the files into a single file
		print 'Concatenating all the files in to one'
		tmpName = tmpDir+str(int(datetimeToEpoch(dt.datetime.now())))+'.'+rad+'.'+fileType
		print 'cat '+string.join(filelist)+' > '+tmpName
		os.system('cat '+string.join(filelist)+' > '+tmpName)
		for filename in filelist:
			print 'rm '+filename
			os.system('rm '+filename)
			
		#filter(if desired) and open the file
		if(not filtered): myPtr.ptr = open(tmpName,'r')
		else:
			print 'fitexfilter '+tmpName+' > '+tmpName+'f'
			os.system('fitexfilter '+tmpName+' > '+tmpName+'f')
			os.system('rm '+tmpName)
			myPtr.ptr = open(tmpName+'f','r')
			
	if(myPtr.ptr != None): 
		if(myPtr.dType == None): myPtr.dType = 'dmap'
		return myPtr
	else:
		print '\nSorry, we could not find any data for you :('
		return None
	
def radDataReadRec(myPtr):
	"""A function to read a single record of radar data from a :class:`radDataTypes.radDataPtr` object
	
	.. note::
		to use this, you must first create a :class:`radDataTypes.radDataPtr` object with :func:`radDataOpen` 

	**Args**:
		* **myPtr** (:class:`radDataTypes.radDataPtr`): contains the pipeline to the data we are after
	**Returns**:
		* **myBeam** (:class:`radDataTypes.beamData`): an object filled with the data we are after.  *will return None when finished reading*
		
	**Example**:
		::
		
			import datetime as dt
			myPtr = radDataOpen(dt.datetime(2011,1,1),'bks',eTime=dt.datetime(2011,1,1,2),channel='a', bmnum=7,cp=153,fileType='fitex',filtered=False, src=None):
			myBeam = radDataReadRec(myPtr)
		
	Written by AJ 20130110
	"""
	from pydarn.sdio import radDataPtr, beamData, fitData, prmData, \
		rawData, iqData, refArr, alpha
	import pydarn, datetime as dt
	from pydarn.sdio.radDataTypes import cipher
	
	#check input
	assert(isinstance(myPtr,radDataPtr)),\
		'error, input must be of type radDataPtr'
	if(myPtr.ptr == None):
		print 'error, your pointer does not point to any data'
		return None
	
	myBeam = beamData()
	
	#do this until we reach the requested start time
	#and have a parameter match
	while(1):
		#check for a mongodb query object
		if(myPtr.dType == 'mongo'):
			#get the next record from the database
			rec = next(myPtr.ptr,None)
			#check for valid data
			if(rec == None or rec[cipher['time']] > myPtr.eTime):
				#if we dont have valid data, clean up, get out
				print '\nreached end of data'
				try: myPtr.ptr.collection.database.connection.disconnect()
				except: pass
				return None
			#check that we're in the time window, and that we have a 
			#match for out params
			if(rec[cipher['time']] >= myPtr.sTime and rec[cipher['time']] <= myPtr.eTime and \
					(myPtr.stid == None or myPtr.stid == rec[cipher['stid']]) and
					(myPtr.channel == None or myPtr.channel == rec[cipher['channel']]) and
					(myPtr.bmnum == None or myPtr.bmnum == rec[cipher['bmnum']]) and
					(myPtr.cp == None or myPtr.cp == rec[cipher['cp']])):
				#fill the beamData object
				myBeam.dbDictToObj(rec)
				myBeam.fType = myPtr.fType
				setattr(myBeam,refArr[myPtr.fType],1)
				if(myPtr.fType == 'fitex' or myPtr.fType == 'fitex' or myPtr.fType == 'lmfit'):
					if(myBeam.fit.slist == None): myBeam.fit.slist = []
				return myBeam
		#check if we're reading from a dmap file
		elif(myPtr.dType == 'dmap'):
			#read the next record from the dmap file
			dfile = pydarn.dmapio.readDmapRec(myPtr.ptr)
			#check for valid data
			if(dfile == None or dt.datetime.utcfromtimestamp(dfile['time']) > myPtr.eTime):
				#if we dont have valid data, clean up, get out
				print '\nreached end of data'
				myPtr.ptr.close()
				return None
			#check that we're in the time window, and that we have a 
			#match for the desired params
			if(dfile['channel'] < 2): channel = 'a'
			else: channel = alpha[dfile['channel']-1]
			if(dt.datetime.utcfromtimestamp(dfile['time']) >= myPtr.sTime and \
					dt.datetime.utcfromtimestamp(dfile['time']) <= myPtr.eTime and \
					(myPtr.stid == None or myPtr.stid == dfile['stid']) and
					(myPtr.channel == None or myPtr.channel == channel) and
					(myPtr.bmnum == None or myPtr.bmnum == dfile['bmnum']) and
					(myPtr.cp == None or myPtr.cp == dfile['cp'])):
				#fill the beamdata object
				myBeam.updateValsFromDict(dfile)
				myBeam.fit.updateValsFromDict(dfile)
				myBeam.prm.updateValsFromDict(dfile)
				myBeam.rawacf.updateValsFromDict(dfile)
				myBeam.iqdat.updateValsFromDict(dfile)
				myBeam.fType = myPtr.fType
				setattr(myBeam,refArr[myPtr.fType],1)
				if(myPtr.fType == 'fitex' or myPtr.fType == 'fitex' or myPtr.fType == 'lmfit'):
					setattr(myBeam,myPtr.fType,myBeam.fit)
					if(myBeam.fit.slist == None): myBeam.fit.slist = []
				return myBeam
		else: 
			print 'error, unrecognized data type'
			return None
			
