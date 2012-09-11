import os,datetime,glob,math,shutil,string,time,pydarn,numpy,utils

def dmapRead(dateStr,rad,times,fileType,filter=0):
	"""
	*******************************
	
	dmapRead(dateStr,rad,times,fileType):
	
	parses a user's input arguments and then reads
	the content of a data map file using the library
	pdymap provided by Jef Spaleta

	INPUTS:
		dateStr : a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		[times]: the range of times for which the file should be read
		[fileType]: 0 for fitex, 1 for fitacf, 2 for lmfit, 3 for rawacf
		[filter]: 1 to boxcar filter, 0 for raw data
	OUTPUTS:
		dfile: the contents of the datamap file(s) in a pydmap object
		
	Written by AJ 20120807
	*******************************
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
		print 'cat '+' '.join(filelist)+' > '+tmpName
		os.system('cat '+' '.join(filelist)+' > '+tmpName)
		print 'fitexfilter '+tmpName+' > '+tmpName+'.f'
		os.system('fitexfilter '+tmpName+' > '+tmpName+'.f')
		
		dfile = pydarn.dmapio.readDmap(1,[tmpName+'.f'])
	
	for filename in filelist:
		os.system('rm '+filename)
		
	return dfile

def radDataRead(dateStr,rad,time=[0,2400],fileType='fitex',vb=0,beam=-1,filter=0):
	"""
	*******************************
	
	radDataRead(dateStr,rad,[time],[fileType],[vb],[beam]):
	
	reads radar data (fitacf or rawacf) for a given period

	INPUTS:
		dateStr : a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		[times]: the range of times for which the file should be read,
			in SIMPLIFIED [hhmm,hhmm] format, eg [29,156], 
			instead of [0029,0156]
			note that an end time of 2400 will read to the end of the file
			default = [0,2400]
		[fileType]: one of ['fitex','fitacf','lmfit','rawacf']
			default = 'fitex'
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
	dfile = dmapRead(dateStr,rad,time,fileType,filter=filter)
	print 'done read'
	
	#create radData object
	myRadData = pydarn.io.radData()
	
	
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
			myBeam = pydarn.io.beam()
		
			#parse the parameters
			myPrmData = parseDmap(dfile[epochT],pydarn.io.prmData())
			myBeam['prm'] = myPrmData
			myBeam['prm']['time'] = dateT
			
			#parse the fit data
			if(fileType == 'fitex' or fileType == 'fitacf' or fileType == 'lmfit'):
				myFitData = parseDmap(dfile[epochT],pydarn.io.fitData())
				myBeam['fit'] = myFitData
			
			#parse the raw data
			if(fileType == 'rawacf'):
				myRawData = parseDmap(dfile[epochT],pydarn.io.rawData())
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
	
	parseDmap(myRec,myData):
	
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
	for k in myData.iterkeys():
		if(myRec.has_key(k)):
			if(isinstance(myRec[k],list)):
				myData[k] = numpy.array(myRec[k])
			else:
				myData[k] = myRec[k]
	
	return myData
	
	

