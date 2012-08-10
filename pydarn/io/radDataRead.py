import os,datetime,glob,math,shutil,string,time,pydarn

def radDataRead(dateStr,rad,times=[0,2400],fileType=0):
	import math,glob,os,shutil,string,time
	import pydarn.pydmap
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
	print filelist
			#add the file to a temporary file
			#print 'concatenating '+filename
			#print 'cat '+filename+' >> '+tmpName
			#os.system('cat '+filename+' >> '+tmpName)
			
			#remove the single file
			#print 'deleting '+filename
			#os.system('rm '+filename)
			#print ''
		
	dfile = pydarn.pydmap.DMapFile(files=filelist,format='d')
	
	for filename in filelist:
		os.system('rm '+filename)
		
	
	myRadData = pydarn.io.radData()
	
	ftimes = dfile.times
	
	stime = datetime.datetime(int(dateStr[0:4]),int(dateStr[4:6]),int(dateStr[6:8]),int(math.floor(times[0]/100.)),int((times[0]/100.-math.floor(times[0]/100.))*100))
	etime = datetime.datetime(int(dateStr[0:4]),int(dateStr[4:6]),int(dateStr[6:8]),int(math.floor(times[1]/100.)),int((times[1]/100.-math.floor(times[1]/100.))*100))

	for t in ftimes:
		if(t >= stime and t <= etime):
			print stime,t,etime
			myBeam = pydarn.io.beam()
		
			myPrmData = parsePrm(dfile[t])
			myBeam['prm'] = myPrmData
			myRadData[t] = myBeam
		
	return myRadData

	
def parsePrm(rec):
	
	myPrmData = pydarn.io.prmData()
	
	for k in myPrmData.iterkeys():
		if(rec.has_key(k)):
			myPrmData[k] = rec[k]
	
	return myPrmData
	
