from pymongo import MongoClient
from pydarn.sdio import *
import pydarn, datetime

	
def readFromDb(startTime=None, endTime=None, stid=None, channel=None, bmnum=None, cp=None, fileType='fitex',exactFlg=False):
	

	import datetime as dt

	t = dt.datetime.now()
	
	qryList = []
	
	#******************************************
	### Construct the query from the arguments
	#******************************************
	
	#if a start time is not provided, use a default
	if(startTime == None): startTime = dt.datetime(2011,1,1)
	#if we want only a single exact time (useful for filling/updating database)
	if(exactFlg): qryList.append({"time": startTime})
	else:
		#if endtime is not provided, use a default
		if(endTime == None): endTime = startTime+dt.timedelta(hours=1)
		#query for time later than start time and less than end time
		qryList.append({"time": {"$lt": endTime}})
		qryList.append({"time": {"$gt": startTime}})
		
	#if other arguments are provided, query for those
	if(stid != None): qryList.append({"stid": stid})
	if(channel != None): qryList.append({"channel": channel})
	if(bmnum != None): qryList.append({"bmnum": bmnum})
	if(cp != None): qryList.append({"cp": cp})
	
	#establish a connection to the server
	conn = MongoClient('mongodb://sd_dbread:5d@sd-work9.ece.vt.edu:27017')
	#connect to the database
	db=conn.radData
	#get the collection of beams
	beams=db.beams
	
	#some arrays for dealing with data types
	if(fileType == 'fitex'): arr = ['exflg','acflg','lmflg']
	elif(fileType == 'fitacf'): arr = ['acflg','exflg','lmflg']
	elif(fileType == 'lmfit'): arr = ['lmflg','exflg','acflg']
	elif(fileType == 'rawacf'): arr = ['rawflg']
	elif(fileType == 'iqdat'): arr = ['iqflg']
	refArr = {'exflg':'fitex','acflg':'fitacf','lmflg':'lmfit','rawflg':'rawacf','iqflg':'iqdat'}
	
	for ftype in arr:
		print 'checking for',refArr[ftype],'in the database'
		#if there is already a file type flag in the query, remove it
		try: qryList.remove({ftype:1})
		except: pass
		
		#append the current file type to the query
		qryList.append({ftype:1})
		#construct the final query definition
		qryDict = {'$and': qryList}
		
		#make a dictionary telling which data types NOT to get,
		#eg dont get rawacf, iqdat, fitacf, lmfit for fitex request
		exDict = {}
		for key,val in refArr.iteritems():
			if(key != ftype): exDict[val] = 0
			
		#do the actual query
		qry = beams.find(qryDict,exDict)
		#check if we have any results
		count = qry.count()
		#if we have data, exit the loop
		if(count > 0):
			break
		#otherwise, try with a different data type
		else:
			print 'could not find',refArr[ftype],'in the database'
	
	#check if we actually had data
	if(count == 0): 
		print 'could not find data in the database, checking for dmap files'
		return None
		
	x=[]
	
	for s in qry:
		x.append(s)
		
	print dt.datetime.now() - t
	return x,qry
		
		
	
	
	
