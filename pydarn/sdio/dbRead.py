from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relation, sessionmaker
from pydarn.sdio import *

def openDbConnection(username,password):
	
	try:
		db = create_engine('postgresql://'+username+':'+password+'@sd-data.ece.vt.edu:5432/raddata',echo=False)
		#db = create_engine('postgresql://'+username+':'+password+'@localhost/mydb',echo=False)
		meta = MetaData(db)
		Session = sessionmaker(bind=db)
		session = Session()
		return meta,session
	except: 
		print 'error connecting to database'
		return None,None

	
def makeQuery(session, startTime, endTime=None, cp=None, stid=None, channel=None, bmnum=None, exactFlg=False):
	
	from sqlalchemy.sql import and_, or_
	import datetime as dt

	try:
		if(endTime == None): endTime = dt.datetime(2999,1,1)
				
		qry = session.query(beamData)
		qry = qry.filter(and_(or_(beamData.cp==cp, cp==None), or_(beamData.stid==stid, stid==None),
													or_(beamData.channel==channel, channel==None), 
													or_(beamData.bmnum==bmnum, bmnum==None)))
													
		if(exactFlg):
			qry = qry.filter(beamData.time==startTime)
		else:
			qry = qry.filter(and_(beamData.time >= startTime, beamData.time <= endTime))

		return qry
	except:
		print 'error constructing query'
		return None
	
def readFromDb(startTime, endTime=None, stid=None, channel=None, bmnum=None, cp=None, fileType=None):
	
	meta,session = openDbConnection('sd_dbread','')
	if(meta == None): return None
	
	qry = makeQuery(session, startTime, endTime=endTime, stid=stid, channel=channel, bmnum=bmnum, cp=cp)
	if(qry == None):
		return None
		
	#try:
	nRecs = qry.count()
	if(nRecs == 0):
		print 'no matching records found in database, will look in files'
		return None
	return qry.all()
		
	#except:
		#print 'error reading from database'
		#return None
	
	
	
