import os,datetime,glob,math,shutil,string,time,pydarn,numpy,utils
from utils.timeUtils import *
from pydarn.sdio.radDataTypes import *
"""
*******************************
MODULE: pydarn.sdio.radDataRead
*******************************

This module contains the following functions:

  dmapOpen

  radDataReadRec

	dmapRead
	
	radDataRead
	
	parseDmap
	
*******************************
"""

	
def radDataOpen(dateStr,rad,time=[0,2400],fileType='fitex',filter=0, src=None):
	"""
	*******************************

	PACKAGE: pydarn.sdio.radDataRead

	FUNCTION: dmapOpen(dateStr,rad,time=[0,2400],fileType='fitex',filter=0):

	PURPOSE: opens a datamap file for reading.  This needs to be called if
	you plan to use radDataReadRec

	INPUTS:
		dateStr: the date of the file to open
		radar: the radar file to open
		[time]: the time duration we plan on reading, this is needed because
			separate files will have to be concatenated.  default = [0,2400]
		[fileType]: the type of file to read, valid inputs are 'fitex', 
			'fitacf', 'lmfit', and 'rawacf'
		[filter]: whether to apply a 3x3x3 boxcar filter to the data

	OUTPUTS:
		f: the opened dmap file
		
	EXAMPLES:
		myFIle = dmapOpen('20110101','bks',time=[259,1430])
		
	Written by AJ 20120928

	"""
	import subprocess as sub
	#get the year of the file
	myDate = utils.yyyymmddToDate(dateStr)
	#we need to get the start and end hours of the request
	#because of how the files are named
	hr1,hr2 = int(math.floor(time[0]/100./2.)*2),int(math.floor(time[1]/100./2.)*2)
	min1 = int(time[0]-int(math.floor(time[0]/100.)*100))
	stime = myDate.replace(hour=hr1,minute=min1)
	if(hr2 == 24):
		etime = myDate+datetime.timedelta(days=1)
	else:
		etime = myDate.replace(hour=hr2)
	
	#FIRST, CHECK IF THE DATA EXISTS IN THE DATABASE
	if(src == None or src == 'db'):
		readFromDb(startTime=stime, endTime=etime, stid=None, channel=None, bmnum=None, cp=None, fileType='fitex',exactFlg=False)

	
	#move back a little in time because files often start at 2 mins
	#after the hour
	stime = myDate.replace(hour=hr1,minute=min1)
	stime = stime-datetime.timedelta(minutes=4)
	
	
	#a temporary directory to store a temporary file
	tmpDir = '/tmp/fit/'
	d = os.path.dirname(tmpDir)
	if not os.path.exists(d):
		os.makedirs(d)

	#iterate through all of the hours in the request
	#ie, iterate through all possible file names
	filelist=[]
	ctime = stime.replace(minute=0)
	if(ctime.hour % 2 == 1): ctime = ctime.replace(hour=ctime.hour-1)
	while ctime <= etime:
		#directory on the data server
		myDir = '/sd-data/'+ctime.strftime("%Y")+'/'+fileType+'/'+rad+'/'
		hrStr = ctime.strftime("%H")
		dateStr = ctime.strftime("%Y%m%d")
		#iterate through all of the files which begin in this hour
		for filename in glob.glob(myDir+dateStr+'.'+hrStr+'*'):
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
			
		ctime = ctime+datetime.timedelta(hours=1)
		
	#check that these is data available
	if(len(filelist) == 0): return None
	
	#concatenate the files into a single file
	tmpName = tmpDir+str(int(datetimeToEpoch(datetime.datetime.now())))+'.'+rad+'.'+fileType
	print 'cat '+string.join(filelist)+' > '+tmpName
	#os.system('cat '+string.join(filelist)+' > '+tmpName)
	subp = sub.Popen(['cat '+string.join(filelist)+' > '+tmpName],shell=True,stdout=sub.PIPE)
	print subp.communicate()[0]
	subp.wait
	#print output
	#delete the individual files
	for filename in filelist:
		print 'rm'+filename 
		os.system('rm '+filename)
		
	#filter(if desired) and open the file
	if(filter == 0): f = open(tmpName,'r')
	else:
		print 'fitexfilter '+tmpName+' > '+tmpName+'f'
		os.system('fitexfilter '+tmpName+' > '+tmpName+'f')
		os.system('rm '+tmpName)
		f = open(tmpName+'f','r')
		
	
	#return the file object
	return f
	
def radDataReadRec(myFile,vb=0,beam=-1,channel=None):
	"""
|	*******************************
|	PACKAGE: pydarn.sdio.radDataRead
|
|	FUNCTION: radDataReadRec(myFile,vb=0)
|
|	PURPOSE: reads a single record from a dmap file
|	NOTE: to use this, you must first open the file with dmapopen
|
|	INPUTS:
|		myFile: the file object we are reading from.  This object must be
|			created using the dmapOpen() function.
|		[vb]: flag to indicate verbose output.  default = 0
|		[beam]: read only records from this beam, a value of -1 will read
|			all beams.  default = -1
|		[channel]: read only records from this channel.  a value of None
|			will read all channels.  Default = None
|	OUTPUTS:
|		myBeam: a radar beam object containign keys of 'prm','fit','raw'
|		
|	EXAMPLES:
|		myBeam = radDataReadRec(myFile)
|		
|	Written by AJ 20120928
	"""
	import string
	#read the datamap file
	redo = 1
	while(redo == 1):
		redo = 0
		dfile = pydarn.dmapio.readDmapRec(myFile)
		if(dfile == None):
			del dfile 
			return None
		if(beam != -1 and dfile['bmnum'] != beam): 
			del dfile
			redo = 1
		elif(channel != None):
			if((channel == 'a' and (dfile['channel'] != 0 and dfile['channel'] != 1)) and \
					dfile['channel']-1 != alpha.index(channel)): redo = 1
	
	keys = dfile.keys()
	for k in keys:
		dfile[string.replace(k,'.','')] = dfile[k]
		
	fileName, fileExtension = os.path.splitext(myFile.name)
	#if(fileExtension == 'fitex'): fileExtension = 'fitex2'
	
	#verbose output
	if(vb):
		print datetime.datetime.utcfromtimestamp(dfile['time'])
		
	#create a beam object
	myBeam = pydarn.sdio.beamData(beamDict=dfile)
	
	#parse the parameters
	myBeam.prm = pydarn.sdio.prmData(prmDict=dfile)

	if(fileExtension[1:] == 'fitex' or fileExtension[1:] == 'lmfit' or fileExtension[1:] == 'fitacf'):
		#parse the fit data
		setattr(myBeam,fileExtension[1:],pydarn.sdio.fitData(fitDict=dfile))
		myBeam.fit = getattr(myBeam,fileExtension[1:])
		myBeam.fit.proctype = fileExtension[1:]
		if(fileExtension[1:] == 'fitex'): myBeam.exflg = 1
		elif(fileExtension[1:] == 'lmfit'): myBeam.lmflg = 1
		elif(fileExtension[1:] == 'fitacf'): myBeam.acflg = 1
	elif(fileExtension[1:] == 'rawacf'):
		myBeam.raw = pydarn.sdio.rawData(rawDict=dfile)
		
	del dfile
	return myBeam
	
def radDataOpen(dateStr,rad,time=[0,2400],fileType='fitex',vb=0,beam=-1,filter=0):
	"""
	*******************************

	PACKAGE: pydarn.sdio.radDataRead

	FUNCTION: radDataRead(dateStr,rad,time=[0,2400],fileType='fitex',vb=0,beam=-1,filter=0)

	PURPOSE: reads a large chunk of data at once from a dmap file into
		a radData object

	INPUTS:
		dateStr : a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		[time]: the range of times for which the file should be read,
			default = [0,2400]
		[fileType]: the file type to open.  Valid inputs are 'fitex', 'fitacf',
			'lmfit', and 'rawacf'
		[filter]: 1 to boxcar filter, 0 for raw data.  default = 0
		[vb]: flag for verbose output, default = 0
		[beam]: option idicating to only read records from a single beam.  if this
			is set to -1, all records are read.  default = -1

	OUTPUTS:
		myRadData: a radData object containging the chunck of data
		
	EXAMPLES:
		myData = radDataRead('20110101','bks')
		
	Written by AJ 20120928

	"""
	import string
	#read the datamap file
	redo = 1
	while(redo == 1):
		redo = 0
		dfile = pydarn.dmapio.readDmapRec(myFile)
		if(dfile == None):
			del dfile 
			return None
		if(beam != -1 and dfile['bmnum'] != beam): 
			del dfile
			redo = 1
		elif(channel != None):
			if((channel == 'a' and (dfile['channel'] != 0 and dfile['channel'] != 1)) and \
					dfile['channel']-1 != alpha.index(channel)): redo = 1
	
	keys = dfile.keys()
	for k in keys:
		dfile[string.replace(k,'.','')] = dfile[k]
		
	fileName, fileExtension = os.path.splitext(myFile.name)
	#if(fileExtension == 'fitex'): fileExtension = 'fitex2'
	
	#verbose output
	if(vb):
		print datetime.datetime.utcfromtimestamp(dfile['time'])
		
	#create a beam object
	myBeam = pydarn.sdio.beamData(beamDict=dfile)
	
	#parse the parameters
	myBeam.prm = pydarn.sdio.prmData(prmDict=dfile)

	if(fileExtension[1:] == 'fitex' or fileExtension[1:] == 'lmfit' or fileExtension[1:] == 'fitacf'):
		#parse the fit data
		setattr(myBeam,fileExtension[1:],pydarn.sdio.fitData(fitDict=dfile))
		myBeam.fit = getattr(myBeam,fileExtension[1:])
		myBeam.fit.proctype = fileExtension[1:]
		if(fileExtension[1:] == 'fitex'): myBeam.exflg = 1
		elif(fileExtension[1:] == 'lmfit'): myBeam.lmflg = 1
		elif(fileExtension[1:] == 'fitacf'): myBeam.acflg = 1
	elif(fileExtension[1:] == 'rawacf'):
		myBeam.raw = pydarn.sdio.rawData(rawDict=dfile)
		
	del dfile
	return myBeam

