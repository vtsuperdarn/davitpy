import os,datetime as dt,glob,math,shutil,string,time,pydarn,numpy,utils
from utils.timeUtils import *
from pydarn.sdio import *
from pydarn.radar import *
"""
|*******************************
|MODULE: pydarn.sdio.radDataRead
|*******************************
|
|This module contains the following functions:
|
|	radDataOpen
|  
|	radDataReadRec  
|	
|*******************************
"""

def radDataOpen(sTime,rad,eTime=None,channel=None,bmnum=None,cp=None,fileType='fitex',filter=False, src=None):
	"""
|	*******************************
|	**PACKAGE**: pydarn.sdio.radDataRead
|
|	**FUNCTION**: radDataOpen(sTime,rad,[eTime=None],[channel=None],
|														[bmnum=None],[cp=None],[fileType='fitex'],
|														[filter=FALSE], [src=None]):
|
|	**PURPOSE**: establishes a pipeline through which 
|		we can read radar data.  first it tries the mongodb,
|		then it tries to find local files, and lastly it 
|		sftp's over to the VT data server.
|
|	**INPUTS**:
|		**sTime**: a datetime object specifying the beginning time
|			for which you want data
|		**rad**: the 3-letter radar code for which you want data
|		**[eTime]**: a dateTime object specifying the last time that
|			you want data for.  if this is set to None, it will be 
|			set to 1 day after sTime.  default = None
|		**[channel]**: the 1-letter code for what channel you want
|			data from, eg 'a','b',...  if this is set to None,
|			data from ALL channels will be read. default = None
|		**[bmnum]**: the beam number which you want data for.  If
|			this is set to None, data from all beams will be read.
|			default = None
|		**[cp]**: the control program which you want data for.  If this is
|			set to None, data from all cp's will be read.  default = None
|		**[fileType]**:  The type of data you want to read.  valid inputs
|			are: 'fitex','fitacf','lmfit','rawacf' ('iqdat' coming in the
|			future).  if you choose a fit file format and the specified one
|			isn't found, we will search for one of the others.  Beware:
|			if you ask for rawacf data, these files are large and the data
|			transfer might take a long time.  default = 'fitex'
|		**[filter]**: a boolean specifying whether you want the fit data to
|			be boxcar filtered.  ONLY VALID FOR FIT.  default = False
|		**[src]**: the source of the data.  valid inputs are 'mongo'
|			'local' 'sftp'.  if this is set to None, it will try all
|			possibilites sequentially.  default = None
|	**OUTPUTS**:
|		**myPtr**: a radDataPtr object which contains a link to the data
|			to be read.  this can then be passed to radDataReadRec
|			in order to actually read the data.
|		
|	**EXAMPLES**:
|		myPtr = radDataOpen(aDatetime,'bks',eTime=anotherDatetime,channel='a',
|												bmnum=7,cp=153,fileType='fitex',filter=False, src=None):
|		
|	Written by AJ 20130110
	"""
	import subprocess as sub, paramiko as p, re
	
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
		fileType == 'fitex' or fileType == 'lmfit'), \
		'error, fileType must be one of: rawacf,fitacf,fitex,lmfit'
	assert(isinstance(filter,bool)), \
		'error, filter must be True of False'
	assert(src == None or src == 'mongo' or src == 'local' or src == 'sftp'), \
		'error, src must be one of None,local,mongo,sftp'
		
	if(eTime == None):
		eTime = sTime+dt.timedelta(days=1)
		
	#create a datapoint object
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

	#FIRST, LOOK LOCALLY FOR FILES
	if(src == None or src == 'local'):
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
				
	#NEXT, CHECK IF THE DATA EXISTS IN THE DATABASE
	if((src == None or src == 'mongo') and len(filelist) == 0):
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
	if((src == None or src == 'sftp') and myPtr.ptr == None and len(filelist) == 0):
		for ftype in arr:
			print '\nLooking on the remote SFTP server for',ftype,'files'
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
					#go thorugh all the fiels in the directory
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
				
	#check if we have found files
	if(len(filelist) != 0):
		#concatenate the files into a single file
		print 'Concatenating all the files in to one'
		tmpName = tmpDir+str(int(datetimeToEpoch(dt.datetime.now())))+'.'+rad+'.'+fileType
		print 'cat '+string.join(filelist)+' > '+tmpName
		os.system('cat '+string.join(filelist)+' > '+tmpName)
		for filename in filelist:
			print 'rm'+filename
			os.system('rm '+filename)
			
		#filter(if desired) and open the file
		if(~filter): myPtr.ptr = open(tmpName,'r')
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
	"""
|	*******************************
|	**PACKAGE**: pydarn.sdio.radDataRead
|
|	**FUNCTION**: radDataReadRec(myPtr)
|
|	**PURPOSE**: reads a single record of radar data
|	**NOTE**: to use this, you must first open a connection with radDataOpen 
|
|	**INPUTS**:
|		**myPtr**: a pydarn.sdio.radDataTypes.radDataPtr object.  this
|			contains the connection to the data we are after
|	**OUTPUTS**:
|		**myBeam**: a pydarn.sdio.radDataTypes.beamData object, filled
|			with the data we are after
|		**NOTE**: will return None when finished reading
|		
|	EXAMPLES:
|		myBeam = radDataReadRec(myPtr)
|		
|	Written by AJ 20130110
	"""
	
	#check input
	assert(isinstance(myPtr,radDataPtr)),\
		'error, input must be of type radDataPtr'
	
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
				#myBeam.iqdat.updateValsFromDict(dfile)
				myBeam.fType = myPtr.fType
				setattr(myBeam,refArr[myPtr.fType],1)
				if(myPtr.fType == 'fitex' or myPtr.fType == 'fitex' or myPtr.fType == 'lmfit'):
					setattr(myBeam,myPtr.fType,myBeam.fit)
				return myBeam
		else: 
			print 'error, unrecognized data type'
			return None
			