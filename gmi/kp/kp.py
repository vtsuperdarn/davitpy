"""
*******************************
A class to contain a day of Kp data

Created by AJ

*******************************
"""

class kpDay:
	def parseFtp(self,line,yr):
		import datetime as dt
		
		self.date = dt.datetime(yr,int(line[2:4]),int(line[4:6]))
		self.kp = []
		self.ap = []
		for i in range(8):
			#store the kp vals
			num = line[12+i*2:12+i*2+1]
			mod = line[13+i*2:13+i*2+1]
			if(num == ' '): num = '0'
			if(mod == '0'): self.kp.append(num)
			elif(mod == '7'): self.kp.append(str(int(num)+1)+'-')
			elif(mod == '3'): self.kp.append(num+'+')
			else: self.kp.append('?')
			#store the ap vals
			self.ap.append(int(line[31+i*3:31+i*3+3]))
		self.sunspot = int(line[62:65])
		self.f107 = float(line[65:70])
		
	def __init__(self, ftpLine=None, year=None):
		#note about where data came from
		self.note = 'This data was downloaded from the GFZ-Potsdam'
		
		if(ftpLine != None and year != None): 
			self.parseFtp(ftpLine,year)
		
		
def readKpFtp(sTime, eTime=None):
	from ftplib import FTP
	import datetime as dt
	
	sTime.replace(hour=0,minute=0,second=0,microsecond=0)
	if(eTime == None): eTime=sTime
	assert(eTime >= sTime), 'error, end time greater than start time'
	if(eTime.year > sTime.year):
		print 'you asked to read across a year bound'
		print "we can't do this, so we will read until the end of the year"
		eTime = dt.datetime(sTime.year,12,31)
		print 'eTime =',eTime
	eTime.replace(hour=0,minute=0,second=0,microsecond=0)
	
	#connect to the server
	try: ftp = FTP('ftp.gfz-potsdam.de')
	except Exception,e:
		print e
		print 'problem connecting to GFZ-Potsdam server'
		
	#login as anonymous
	try: l=ftp.login()
	except Exception,e:
		print e
		print 'problem logging in to GFZ-potsdam server'
	
	#go to the kp directory
	try: ftp.cwd('/pub/home/obs/kp-ap/wdc')
	except Exception,e:
		print e
		print 'error getting to data directory'
	
	#list to hold the lines
	lines = []
	#get the data
	print 'RETR kp'+str(sTime.year)+'.wdc'
	ftp.retrlines('RETR kp'+str(sTime.year)+'.wdc',lines.append)

	myKp = []
	for l in lines:
		if(sTime <= dt.datetime(sTime.year,int(l[2:4]),int(l[4:6])) <= eTime):
			myKp.append(kpDay(ftpLine=l,year=sTime.year))
		
	return lines