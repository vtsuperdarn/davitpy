from pydarn.pydmap import DMapFile, timespan, dt2ts, ts2dt
import os,datetime,glob,math,shutil,string,time

def radDataRead(dateStr,rad,times=[0,2400],fileType=0):
	import math,glob,os,shutil,string,time

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
	
	
	hr1 = times[0]/100.
	hr2 = times[1]/100.
	
	hr1 = int(math.floor(hr1/2.)*2)
	hr2 = int(math.floor(hr2/2.)*2)
	
	tmpDir = '/tmp/fit/'
	d = os.path.dirname(tmpDir)
	if not os.path.exists(d):
		os.makedirs(d)
	
	tmpName = tmpDir+str(int(time.time()))+'.'+ext
	
	for i in range(hr1,hr2+1):
		if(i < 10):
			hrStr = '0'+str(i)
		else:
			hrStr = str(i)
		
		for filename in glob.glob(myDir+dateStr+'.'+hrStr+'*'):
			print 'copying '+filename
			os.system('cp '+filename+' '+tmpDir)
			filename = string.replace(filename,myDir,tmpDir)
			print 'unzipping '+filename
			if(string.find(filename,'.bz2') != -1):
				os.system('bunzip2 '+filename)
				filename = string.replace(filename,'.bz2','')
			else:
				os.system('gunzip '+filename)
				filename = string.replace(filename,'.bz2','')
				
			print 'concatenating '+filename
			print 'cat '+filename+' >> '+tmpName
			os.system('cat '+filename+' >> '+tmpName)
			print 'deleting '+filename
			os.system('rm '+filename)
			
			
	#delete the temporary fit file
	os.system('rm'+tmpName)
