import os,datetime,glob,math,shutil,string,time,pydarn

def dmapRead(dateStr,rad,times,fileType):
	"""
	*******************************
	
	dmapRead():
	
	parses a user's input arguments and then reads
	the content of a data map file using the library
	pdymap provided by Jef Spaleta

	INPUTS:
		dateStr : a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		[times]: the range of times for which the file should be read
		[fileType]: 0 for fitex, 1 for fitacf, 2 for lmfit, 3 for rawacf
	OUTPUTS:
		dfile: the contents of the datamap file(s) in a pydmap object
		
	Written by AJ 20120807
	*******************************
	"""
	
	import math,glob,os,shutil,string,time
	import pydarn

	#get the year of the file
	yrStr = dateStr[0:4]
	
	#check for file extension
	if(fileType == 0):
		ext = 'fitex'
	elif(fileType == 1):
		ext = 'fitacf'
	elif(fileType == 2):
		ext = 'lmfit'
	elif(fileType == 3):
		ext = 'rawacf'
	
	#this needs to be changed when the network is working
	myDir = '/sd-data/'+yrStr+'/'+ext+'/'+rad+'/'
	
	#we need to get the start and end hours of the request
	#becasue of how the files are named
	hr1 = times[0]/100.
	hr2 = times[1]/100.
	hr1 = int(math.floor(hr1/2.)*2)
	hr2 = int(math.floor(hr2/2.)*2)
	
	#a temporary directory to store a temporary file
	tmpDir = '/tmp/fit/'
	d = os.path.dirname(tmpDir)
	if not os.path.exists(d):
		os.makedirs(d)
	tmpName = tmpDir+str(int(time.time()))+'.'+ext

	#iterate through all of the hours in the request
	#ie, iterate through all possible file names
	
	filelist=[]
	for i in range(hr1,hr2+1):
		if(i < 10):
			hrStr = '0'+str(i)
		else:
			hrStr = str(i)

		#iterate through all of the files which begin in this hour
		for filename in glob.glob(myDir+dateStr+'.'+hrStr+'*'):
			#copy the file from sd-data to a local temp directory
			print 'copying '+filename
			os.system('cp '+filename+' '+tmpDir)
			filename = string.replace(filename,myDir,tmpDir)
			
			#unzip the compressed file
			print 'unzipping '+filename
			if(string.find(filename,'.bz2') != -1):
				os.system('bunzip2 '+filename)
				filename = string.replace(filename,'.bz2','')
			else:
				os.system('gunzip '+filename)
				filename = string.replace(filename,'.bz2','')
				
			filelist.append(filename)
			
	tempname = tmpDir+str(int(time.time()))
	
	print 'concatenating '+' '.join(filelist)+' > '+tempname
	os.system('cat '+' '.join(filelist)+' > '+tempname)
	
	for filename in filelist:
		os.system('rm '+filename)
		
	dfile = pydarn.dmapio.readDmap(tempname)
	

		
		
	return dfile

def radDataRead(dateStr,rad,time=[0,2400],fileType=0,vb=0,beam=-1):
	"""
	*******************************
	
	radDataRead():
	
	reads radar data (fitacf or rawacf) for a given period

	INPUTS:
		dateStr : a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		[times]: the range of times for which the file should be read,
			in SIMPLIFIED [hhmm,hhmm] format, eg [29,156], 
			instead of [0029,0156]
			note that an end time of 2400 will read to the end of the file
			default = [0,2400]
		[fileType]: 0 for fitex, 1 for fitacf, 2 for lmfit, 3 for rawacf
			default=0
		[vb]: verbose output, 1=yes, 0=no
			default = 0
		[beam]: beam for which to read data, a value of -1 will
			read all beams (default)
	OUTPUTS:
		myData: a radData object
		
	Written by AJ 20120807
	*******************************
	"""
	
	#read the datamap file
	dfile = dmapRead(dateStr,rad,times=time,fileType=fileType)
	print 'done read'
	
	#create radData object
	myRadData = pydarn.io.radData()
	
	#calculate start and end times
	stime = datetime.datetime(int(dateStr[0:4]),int(dateStr[4:6]),int(dateStr[6:8]), \
	int(math.floor(time[0]/100.)),int((time[0]/100.-math.floor(time[0]/100.))*100))
	if(time[1] == 2400):
		etime = datetime.datetime(int(dateStr[0:4]),int(dateStr[4:6]),int(dateStr[6:8])+1,1,0,0)
	else:
		etime = datetime.datetime(int(dateStr[0:4]),int(dateStr[4:6]),int(dateStr[6:8]), \
		int(math.floor(time[1]/100.)),int((time[1]/100.-math.floor(time[1]/100.))*100))
		
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
			myBeam = pydarn.io.beam()
		
			#parse the parameters
			myPrmData = parseDmap(dfile[epochT],pydarn.io.prmData())
			myBeam['prm'] = myPrmData
			myBeam['prm']['time'] = dateT
			
			#parse the fit data
			if(fileType < 3):
				myFitData = parseDmap(dfile[epochT],pydarn.io.fitData())
				myBeam['fit'] = myFitData
			
			myRadData[dateT] = myBeam
			
	print 'done copy'
	return myRadData


def parseDmap(myRec,myData):
	"""
	*******************************
	
	parseDmap():
	
	parses radar data from a pydmapobject into the proper 
	structure, eg fitData, prmData

	INPUTS:
		myRec: the pydmapobject containing the data record
		myData: the structure to put the data into
	OUTPUTS:
		myData: a data object, e.g. prmData, fitData, rawData
		
	Written by AJ 20120807
	*******************************
	"""
	from numpy import *
	for k in myData.iterkeys():
		if(myRec.has_key(k)):
			if(isinstance(myRec[k],list)):
				myData[k] = array(myRec[k])
			else:
				myData[k] = myRec[k]
	
	return myData
	
	

