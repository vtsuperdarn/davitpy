from sqlalchemy import *
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relation, sessionmaker
from pydarn.sdio import *
import numpy

alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

Base = declarative_base()

class Beam(Base):
	"""
	*******************************
	PACKAGE: pydarn.sdio.sdDbClasses

	CLASS: Beam

	PURPOSE: represent radar data for Alchemy ORM

	DECLARATION: 
		mybeam = Beam(radarPrm,[proctype])

	MEMBERS:
		see pydarn.sdio.radDataTypes

	Written by AJ 20121130
	"""
	
	__tablename__ = "beam"

	beam_id = Column(Integer, primary_key=True, unique=True)
	cp = Column(Integer, primary_key=True)
	stid = Column(Integer, primary_key=True)
	time = Column(DateTime, primary_key=True)
	channel= Column(String, primary_key=True)
	bmnum = Column(Integer, primary_key=True)
	proctype = Column(String, primary_key=True)
	
	def __init__(self, myPrm, proctype='fitex2'):
		if(myPrm.has_key('cp')): self.cp = myPrm['cp']
		else: self.cp = -1
		if(myPrm.has_key('stid')): self.stid = myPrm['stid']
		else: self.stid = -1
		if(myPrm.has_key('time')): self.time = myPrm['time']
		else: self.time = -1
		if(myPrm.has_key('bmnum')): self.bmnum = myPrm['bmnum']
		else: self.bmnum = -1
		if(myPrm.has_key('channel')): 
			if(myPrm['channel'] < 2): self.channel = 'a'
			else: self.channel = alpha[myPrm['channel']-1]
		else: self.channel = 'a'
		self.proctype = proctype
    
	def __repr__(self):
		return "<Beam('%d','%d', '%d', '%f','%d', '%s')>" % (self.beam_id, self.cp, self.stid, self.time, self.bmnum, self.channel)
		

class Prm(Base):
	"""
	*******************************
	PACKAGE: pydarn.sdio.sdDbClasses

	CLASS: Prm

	PURPOSE: represent radar data for Alchemy ORM

	DECLARATION: 
		myprm = Prm(radarPrm)

	MEMBERS:
		see pydarn.sdio.radDataTypes

	Written by AJ 20121130

	"""
	
	#create the sql table
	__tablename__ = "prm"
	prm_id = Column(Integer, primary_key=True)
	beam_id = Column(Integer, ForeignKey('beam.beam_id'))
	smsep = Column(Integer)
	noisesearch = Column(Float)
	nave = Column(Integer)
	lagfr = Column(Integer)
	smsep = Column(Integer)
	noisesearch = Column(Float)
	noisemean = Column(Float)
	noisesky = Column(Float)
	bmazm = Column(Float)
	scan = Column(Integer)
	rxrise = Column(Integer)
	inttsc = Column(Integer)
	inttus = Column(Integer)
	mpinc = Column(Integer)
	mppul = Column(Integer)
	mplgs = Column(Integer)
	mplgexs = Column(Integer)
	nrang = Column(Integer)
	frang = Column(Integer)
	rsep = Column(Integer)
	xcf = Column(Integer)
	tfreq	 = Column(Integer)
	ifmode = Column(Integer)
	ptab = Column(pg.ARRAY(Integer))
	ltab = Column(pg.ARRAY(Integer))

	# creates a bidirectional relationship
	beam = relation(Beam, backref=backref('prm'), uselist=False)

	#initialize the struct
	def __init__(self, myPrm):
		self.nave = -1
		self.lagfr = -1
		self.smsep = -1
		self.bmazm = -1
		self.scan = -1
		self.rxrise = -1
		self.inttsc = -1
		self.inttus = -1
		self.mpinc = -1
		self.mppul = -1
		self.mplgs = -1
		self.mplgexs = -1
		self.nrang = -1
		self.frang = -1
		self.rsep = -1
		self.xcf = -1
		self.tfreq = -1
		self.ifmode = -1
		self.ptab = []
		self.ltab = []
		self.noisemean = -1
		self.noisesky = -1
		self.noisesearch = -1
		self.updateVals(myPrm)
		
	#printing representation
	def __repr__(self):
		return "<prm('%d', '%d')>" % (self.smsep, self.noisesearch)
		
	def updateVals(self, myPrm):
		for attr, value in self.__dict__.iteritems():
			
			if(myPrm.has_key(attr)):
				if(isinstance(myPrm[attr],int) or isinstance(myPrm[attr],list)\
					 or isinstance(myPrm[attr],float)): 
						setattr(self,attr,myPrm[attr])
				else: setattr(self,attr,myPrm[attr].tolist())
			elif(attr == 'noisesearch'): self.noisesearch = myPrm['noise.search']
			elif(attr == 'noisemean'): self.noisemean = myPrm['noise.mean']
			elif(attr == 'noisesky'): self.noisesky = myPrm['noise.sky']
			elif(attr == 'inttus'): self.noisemean = myPrm['intt.us']
			elif(attr == 'inttsc'): self.noisesky = myPrm['intt.sc']


class Fit(Base):
	"""
	*******************************
	PACKAGE: pydarn.sdio.sdDbClasses

	CLASS: Fit

	PURPOSE: represent radar fit data for Alchemy ORM

	DECLARATION: 
		myfit = Fit(radarFit)

	MEMBERS:
		see pydarn.sdio.radDataTypes

	Written by AJ 20121130

	"""
	
	#create the sql table
	__tablename__ = "fit"
	fit_id = Column(Integer, primary_key=True)
	beam_id = Column(Integer, ForeignKey('beam.beam_id'))
	pwr0 = Column(pg.ARRAY(Float))
	slist = Column(pg.ARRAY(Integer))
	npnts = Column(Integer)
	nlag = Column(pg.ARRAY(Integer))
	qflg = Column(pg.ARRAY(Integer))
	gflg = Column(pg.ARRAY(Integer))
	p_l = Column(pg.ARRAY(Float))
	p_l_e	 = Column(pg.ARRAY(Float))
	p_s = Column(pg.ARRAY(Float))
	p_s_e	 = Column(pg.ARRAY(Float))
	v = Column(pg.ARRAY(Float))
	v_e	 = 	Column(pg.ARRAY(Float))
	w_l	 = 	Column(pg.ARRAY(Float))
	w_l_e	 = 	Column(pg.ARRAY(Float))
	sd_l	 = 	Column(pg.ARRAY(Float))
	sd_s	 = 	Column(pg.ARRAY(Float))
	sd_phi	 = 	Column(pg.ARRAY(Float))
	phi0	 = 	Column(pg.ARRAY(Float))
	phi0_e = 		Column(pg.ARRAY(Float))
	elv	 = 	Column(pg.ARRAY(Float))
	elv_low		 = Column(pg.ARRAY(Float))
	elv_high	 = 	Column(pg.ARRAY(Float))
	x_sd_l	 = 	Column(pg.ARRAY(Float))
	x_sd_s	 = 	Column(pg.ARRAY(Float))
	x_sd_phi	 = 	Column(pg.ARRAY(Float))

	# creates a bidirectional relationship
	beam = relation(Beam, backref=backref('fit'), uselist=False)

	#initialize the struct
	def __init__(self, myFit):
		self.pwr0 = []
		self.slist = []
		self.npnts = 0
		self.nlag = []
		self.qflg = []
		self.gflg = []
		self.p_l = []
		self.p_l_e = []
		self.p_s = []
		self.p_s_e = []
		self.v = []
		self.v_e = []
		self.w_l = []
		self.w_l_e = []
		#self.sd_l = []
		#self.sd_s = []
		#self.sd_phi = []
		self.phi0 = []
		self.phi0_e = []
		#self.elv_low = []
		self.elv = []
		#self.elv_high = []
		#self.x_sd_l = []
		#self.x_sd_s = []
		#self.x_sd_phi = []
		
		self.updateVals(myFit)

		
	def updateVals(self, myFit):
		
		for attr, value in self.__dict__.iteritems():
			if(myFit.has_key(attr)):
				if(isinstance(myFit[attr],int) or isinstance(myFit[attr],list)): setattr(self,attr,myFit[attr])
				else: setattr(self,attr,myFit[attr].tolist())
    
		#if(myFit.has_key('pwr0')): self.pwr0 = myFit['pwr0'].tolist()
		#else: self.pwr0 = []
		#if(myFit.has_key('slist')): self.slist = myFit['slist'].tolist()
		#else: self.slist = []
		#if(myFit.has_key('npnts')): self.npnts = myFit['npnts']
		#else: self.npnts = 0
		#if(myFit.has_key('nlag')): self.nlag = myFit['nlag'].tolist()
		#else: self.nlag = []
		#if(myFit.has_key('qflg')): self.qflg = myFit['qflg'].tolist()
		#else: self.qflg = []
		#if(myFit.has_key('gflg')): self.gflg = myFit['gflg'].tolist()
		#else: self.gflg = []
		#if(myFit.has_key('p_l')): self.p_l = myFit['p_l'].tolist()
		#else: self.p_l = []
		#if(myFit.has_key('p_l_e')): self.p_l_e = myFit['p_l_e'].tolist()
		#else: self.p_l_e = []
		#if(myFit.has_key('p_s')): self.p_s = myFit['p_s'].tolist()
		#else: self.p_s = []
		#if(myFit.has_key('p_s_e')): self.p_s_e = myFit['p_s_e'].tolist()
		#else: self.p_s_e = []
		#if(myFit.has_key('v')): self.v = myFit['v'].tolist()
		#else: self.v = []
		#if(myFit.has_key('v_e')): self.v_e = myFit['v_e'].tolist()
		#else: self.v_e = []
		#if(myFit.has_key('w_l')): self.w_l = myFit['w_l'].tolist()
		#else: self.w_l = []
		#if(myFit.has_key('w_l_e')): self.w_l_e = myFit['w_l_e'].tolist()
		#else: self.w_l_e = []
		#if(myFit.has_key('sd_l')): self.sd_l = myFit['sd_l'].tolist()
		#else: self.sd_l = []
		#if(myFit.has_key('sd_s')): self.sd_s = myFit['sd_s'].tolist()
		#else: self.sd_s = []
		#if(myFit.has_key('sd_phi')): self.sd_phi = myFit['sd_phi'].tolist()
		#else: self.sd_phi = []
		#if(myFit.has_key('phi0')): self.phi0 = myFit['phi0'].tolist()
		#else: self.phi0 = []
		#if(myFit.has_key('phi0_e')): self.phi0_e = myFit['phi0_e'].tolist()
		#else: self.phi0_e = []
		#if(myFit.has_key('elv_low')): self.elv_low = myFit['elv_low'].tolist()
		#else: self.elv_low = []
		#if(myFit.has_key('elv')): self.elv = myFit['elv'].tolist()
		#else: self.elv = []
		#if(myFit.has_key('elv_high')): self.elv_high = myFit['elv_high'].tolist()
		#else: self.elv_high = []
		#if(myFit.has_key('x_sd_l')): self.x_sd_l = myFit['x_sd_l']
		#else: self.x_sd_l = []
		#if(myFit.has_key('x_sd_s')): self.x_sd_s = myFit['x_sd_s']
		#else: self.x_sd_s = []
		#if(myFit.has_key('x_sd_phi')): self.x_sd_phi = myFit['x_sd_phi']
		#else: self.x_sd_phi = []
		


		
		
		