import os,datetime,glob,math,shutil,string,time,pydarn,numpy,utils
from utils.timeUtils import *
from pydarn.sdio.radDataTypes import *
import pydarn.sdio.radDataTypes
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

	
def dmapOpen(dateStr,rad,time=[0,2400],fileType='fitex',filter=0):
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
	
	#get the year of the file
	myDate = utils.yyyymmddToDate(dateStr)
	
	#we need to get the start and end hours of the request
	#becasue of how the files are named
	hr1,hr2 = int(math.floor(time[0]/100./2.)*2),int(math.floor(time[1]/100./2.)*2)
	min1 = int(time[0]-int(math.floor(time[0]/100.)*100))
	#move back a little in time because files often start at 2 mins
	#after the hour
	stime = myDate.replace(hour=hr1,minute=min1)
	stime = stime-datetime.timedelta(minutes=4)
	if(hr2 == 24):
		etime = myDate+datetime.timedelta(days=1)
	else:
		etime = myDate.replace(hour=hr2)

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
	tmpName = tmpDir+str(int(datetimeToEpoch(datetime.datetime.now())))+'.'+fileType
	print 'cat '+string.join(filelist)+' > '+tmpName
	os.system('cat '+string.join(filelist)+' > '+tmpName)

	#delete the individual files
	for filename in filelist: os.system('rm '+filename)
		
	#filter(if desired) and open the file
	if(filter == 0): f = open(tmpName,'r')
	else:
		print 'fitexfilter '+tmpName+' > '+tmpName+'.f'
		os.system('fitexfilter '+tmpName+' > '+tmpName+'.f')
		os.system('rm '+tmpName)
		f = open(tmpName+'.f','r')
		
	#return the file object
	return f
	
def radDataReadRec(myFile,vb=0,beam=-1,channel=None):
	"""
	*******************************

	PACKAGE: pydarn.sdio.radDataRead

	FUNCTION: radDataReadRec(myFile,vb=0)

	PURPOSE: reads a single record from a dmap file

	INPUTS:
		myFile: the file object we are reading from.  This object must be
			created using the dmapOpen() function.
		[vb]: flag to indicate verbose output.  default = 0
		[beam]: read only records from this beam, a value of -1 will read
			all beams.  default = -1
		[channel]: read only records from this channel.  a value of None
			will read all channels.  Default = None

	OUTPUTS:
		myBeam: a radar beam object containign keys of 'prm','fit','raw'
		
	EXAMPLES:
		myBeam = radDataReadRec(myFile)
		
	Written by AJ 20120928

	"""
	
	#read the datamap file
	redo = 1
	while(redo == 1):
		redo = 0
		dfile = pydarn.dmapio.readDmapRec(myFile)
		if(dfile == None): return None
		if(beam != -1 and dfile[dfile.keys()[0]]['bmnum'] != beam): redo = 1
		elif(channel != None):
			if((channel == 'a' and (dfile[dfile.keys()[0]]['channel'] != 0 and dfile[dfile.keys()[0]]['channel'] != 1)) or \
			(channel == 'b' and dfile[dfile.keys()[0]]['channel'] != 2) or \
			(channel == 'c' and dfile[dfile.keys()[0]]['channel'] != 3) or \
			(channel == 'd' and dfile[dfile.keys()[0]]['channel'] != 4)): redo = 1


	#iterate through the available times from the file
	epochT = dfile.keys()[0]

	dateT = datetime.datetime.utcfromtimestamp(epochT)

	#verbose output
	if(vb):
		print dateT

	#create a beam object
	myBeam = pydarn.sdio.radDataTypes.beam()

	#parse the parameters
	myPrmData = parseDmap(dfile[epochT],prmData())
	myBeam['prm'] = myPrmData
	myBeam['prm']['time'] = dateT
	
	#parse the fit data
	myFitData = parseDmap(dfile[epochT],fitData())
	myBeam['fit'] = myFitData

	#parse the raw data
	myRawData = parseDmap(dfile[epochT],rawData())
	myBeam['raw'] = myRawData

	return myBeam
	
def dmapRead(dateStr,rad,times,fileType,filter=0):
	"""
	*******************************

	PACKAGE: pydarn.sdio.radDataRead

	FUNCTION: dmapRead(dateStr,rad,times,fileType,filter=0)

	PURPOSE: reads a large chunk of a dmap file

	INPUTS:
		dateStr : a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		times: the range of times for which the file should be read
		fileType: the file type to open.  Valid inputs are 'fitex', 'fitacf',
			'lmfit', and 'rawacf'
		[filter]: 1 to boxcar filter, 0 for raw data.  default = 0

	OUTPUTS:
		dfile: a dictionary containing the contents of a dmap file
		
	EXAMPLES:
		dfile = dmapRead('20110101','bks',[0,2400],'fitex',filter=1)
		
	Written by AJ 20120928

	"""
	
	#get the year of the file
	myDate = utils.yyyymmddToDate(dateStr)
	
	#we need to get the start and end hours of the request
	#becasue of how the files are named
	hr1,hr2 = int(math.floor(times[0]/100./2.)*2),int(math.floor(times[1]/100./2.)*2)
	min1 = int(times[0]-int(math.floor(times[0]/100.)*100))

	stime = myDate.replace(hour=hr1,minute=min1)
	stime = stime-datetime.timedelta(minutes=4)

	if(hr2 == 24):
		etime = myDate+datetime.timedelta(days=1)
	else:
		etime = myDate.replace(hour=hr2)

	#a temporary directory to store a temporary file
	tmpDir = '/tmp/fit/'
	d = os.path.dirname(tmpDir)
	if not os.path.exists(d):
		os.makedirs(d)
	tmpName = tmpDir+str(int(time.time()))+'.'+fileType

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

	if(filter == 0): dfile = pydarn.dmapio.readDmap(len(filelist),filelist)
	else:
		if(len(filelist) > 0):
			print 'cat '+' '.join(filelist)+' > '+tmpName
			os.system('cat '+' '.join(filelist)+' > '+tmpName)
			print 'fitexfilter '+tmpName+' > '+tmpName+'.f'
			os.system('fitexfilter '+tmpName+' > '+tmpName+'.f')
			dfile = pydarn.dmapio.readDmap(1,[tmpName+'.f'])
		else: dfile = pydarn.dmapio.readDmap(len(filelist),filelist)
	
	for filename in filelist:
		os.system('rm '+filename)
		
	return dfile

def radDataRead(dateStr,rad,time=[0,2400],fileType='fitex',vb=0,beam=-1,filter=0):
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
	
	
	#read the datamap file
	dfile = dmapRead(dateStr,rad,time,fileType,filter=filter)
	print 'done read'
	
	#create radData object
	myRadData = radData()
	
	
	#calculate start and end times
	stime = utils.yyyymmddToDate(dateStr).replace(hour=int(math.floor(time[0]/100.)),minute=int((time[0]-int(math.floor(time[0]/100.))*100)))
	
	if(time[1] == 2400):
		etime = utils.yyyymmddToDate(dateStr)+datetime.timedelta(days=1)
	else:
		etime = utils.yyyymmddToDate(dateStr).replace(hour=int(math.floor(time[1]/100.)),minute=int((time[1]-int(math.floor(time[1]/100.))*100)))
		
	#iterate through the available times from the file
	for epochT in dfile.keys():

		dateT = datetime.datetime.utcfromtimestamp(epochT)

		#check that we are in the target time interval
		if(dateT >= stime and dateT <= etime):
			
			#verbose output
			if(vb):
				print dateT
				
			#check the requested beam
			if(beam != -1 and dfile[epochT]['bmnum'] != beam):
				continue
			
			#create a beam object
			myBeam = pydarn.sdio.radDataTypes.beam()
		
			#parse the parameters
			myPrmData = parseDmap(dfile[epochT],prmData())
			myBeam['prm'] = myPrmData
			myBeam['prm']['time'] = dateT
			
			#parse the fit data
			if(fileType == 'fitex' or fileType == 'fitacf' or fileType == 'lmfit'):
				myFitData = parseDmap(dfile[epochT],fitData())
				myBeam['fit'] = myFitData
			
			#parse the raw data
			if(fileType == 'rawacf'):
				myRawData = parseDmap(dfile[epochT],rawData())
				myBeam['raw'] = myRawData
				
			myRadData[dateT] = myBeam
			
	print 'done copy'
	
	myRadData.times = myRadData.getTimes()
	myRadData.nrecs = len(myRadData.times)
	if(myRadData.nrecs > 0):
		myRadData.ftype = fileType
		
	return myRadData


def parseDmap(myRec,myData):
	"""
	*******************************

	PACKAGE: pydarn.sdio.radDataRead

	FUNCTION: parseDmap(myRec,myData)

	PURPOSE: parses a dfile dictionary into a radData structure

	INPUTS:
		myRec: the record from the dmap file
		myData: the radData structure tp be filled

	OUTPUTS:
		myData: the filles radData structure
		
	EXAMPLES:
		myData = parseDmap(dfile,myData)
		
	Written by AJ 20120928

	"""
	for k in myData.iterkeys():
		if(myRec.has_key(k)):
			if(isinstance(myRec[k],list)):
				myData[k] = numpy.array(myRec[k])
			else:
				myData[k] = myRec[k]
	
	return myData
	
	

