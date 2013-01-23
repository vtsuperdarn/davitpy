def readOmniFromWeb(sTime,eTime=None,res=1):
	
	from ftplib import FTP
	
	#connect to the server
	ftp = FTP('spdf.gsfc.nasa.gov')