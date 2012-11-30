from sqlalchemy import *
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relation, sessionmaker
from pydarn.sdio import *
from dbTestClasses import *

def createDb():
	# create a connection to a sqlite database
	# turn echo on to see the auto-generated SQL
	db = create_engine('postgresql://ajpg:ajpg@sd-data.ece.vt.edu/raddata',echo=False)
	# get a handle on the table object
	beams_table = Beam.__table__
	# get a handle on the metadata
	metadata = Base.metadata
	metadata.create_all(db)


def mapDb():
	
	from sqlalchemy.sql import and_
	
	db = create_engine('postgresql://ajpg:ajpg@sd-data.ece.vt.edu/raddata',echo=False)
	meta = MetaData(db)
	
	Session = sessionmaker(bind=db)
	session = Session()

	beams = Table('beam', meta, autoload=True)
	
	#open the file
	myFile = dmapOpen('20080309','bks',time=[10,20])
	
	assert(myFile != None),'error, no data available for the requested time/radar/filetype combination'
	myBeam = radDataReadRec(myFile)
	assert(myBeam != None),'error, no data available for the requested time/radar/filetype combination'
	
	while(myBeam != None):
		
		if(myBeam['prm'].has_key('channel')):
			if(myBeam['prm']['channel'] < 2): chn = 'a'
			else: chn = alpha[myBeam['prm']['channel']-1]
		else: chn = 'a'
		
		sql = session.query(Beam, Prm, Fit)
		
		sql = sql.filter(and_(Beam.cp==myBeam['prm']['cp'], Beam.stid==myBeam['prm']['stid'],\
											Beam.time==myBeam['prm']['time'], Beam.channel==chn,\
											Beam.bmnum==myBeam['prm']['bmnum']))
		sql = sql.filter(Prm.beam_id == Beam.beam_id)
		sql = sql.filter(Fit.beam_id == Beam.beam_id)
		
		if(len(sql.all()) == 0):
			tempBeam = Beam(myBeam['prm'])
			tempBeam.prm = [Prm(myBeam['prm'])]
			tempBeam.fit = [Fit(myBeam['fit'])]
			session.add(tempBeam)
		else:
			sql.all()[0][1].updateVals(myBeam['prm'])
			sql.all()[0][2].updateVals(myBeam['fit'])
			
		
		myBeam = radDataReadRec(myFile)
	
	print 'start commit'
	session.commit()
	myFile.close()