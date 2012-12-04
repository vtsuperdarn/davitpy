from sqlalchemy import *
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, CHAR
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relationship, sessionmaker
from pydarn.sdio import *
import numpy, pydarn, datetime
Base = declarative_base()

alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

class radData(dict):
	"""
	*******************************
	CLASS pydarn.io.radData

	a dictionary class containing a time sequence of
	radar data in beam structures
	
	KEYS:
		[datetime1, datetime2, ...]
	VALUES:
		[beam1, beam2, ...]
		
	EXAMPLES:
	
	DECLARATION: 
		myData = pydarn.io.radData()
		
	ACCESS:
		myData[datetime] = beam
	
	Written by AJ 20120808
	*******************************
	"""
	
	def __init__(self):
		self._dict = {}
		self.times = []
		self.nrecs = 0
		
	def getTimes(self):
		"""
		*******************************
		FUNCTION radData.getTimes():
		
		returns a sorted list of the datetime keys belonging
		to a radData object
		
		BELONGS TO: class pydarn.io.radData

		INPUTS:
			NONE
		OUTPUTS:
			k: a sorted list of datetime keys for a radData obect
			
		EXAMPLE:
			timelist = myRadData.getTimes()
			
		Written by AJ 20120808
		*******************************
		"""
	
		k = self.keys()
		k.sort()
		return k
		
	def getBeam(self,bmnum):
		"""
		*******************************
		FUNCTION radData.getBeam(bmnum):
		
		returns a radData object containing only data from a specified beam
		
		BELONGS TO: class pydarn.io.radData

		INPUTS:
			bmnum: the desired beam number
		OUTPUTS:
			myData: a new radData structure containing only beams of bmnum
			
		EXAMPLE:
			myRadarData = inRadData.getBeam(7)
			
		Written by AJ 20120811
		*******************************
		"""

		assert(isinstance(bmnum,int)),"bmnum must be integer"
		
		myData = pydarn.sdio.radData()
		
		for k in self.iterkeys():
			if(self[k].prm.bmnum == bmnum):
				myData[k] = self[k]
			
		myData.times = myData.getTimes()
		myData.nrecs = len(myData.times)
		myData.ftype = self.ftype
		
		return myData
		
		
	def getChannel(self,chn):
		"""
		*******************************
		FUNCTION radData.getChannel(bmnum):
		
		returns a radData object containing only data from a specified channel
		
		BELONGS TO: class pydarn.io.radData

		INPUTS:
			chn: the desired channel letter, e.g. 'a'
		OUTPUTS:
			myData: a new radData structure containing only data from channel chn
			
		EXAMPLE:
			myRadarData = inRadData.getChannel('a')
			
		Written by AJ 20120814
		*******************************
		"""
		
		assert(isinstance(chn,str)),"channel must be character"
		
		myData = pydarn.io.radData()
		
		for k in self.iterkeys():
			if(self[k].prm.channel == 0 and chn == 'a'):
				myData[k] = self[k]
			elif(alpha[self[k].prm.channel-1] == chn):
				myData[k] = self[k]
				
		myData.times = myData.getTimes()
		myData.nrecs = len(myData.times)
		myData.ftype = self.ftype
		return myData  
		
class beamData(Base):
	"""
|	*******************************
|	CLASS pydarn.sdio.beamData
|
|	a class to contain the data from a radar beam sounding
|	
|	ATTRS:
|		cp -- radar control program id number
|		stid -- radar station id number
|		time -- timestamp of beam sounding
|		channel -- radar operating channel
|		bmnum -- beam number
|		prm -- radar operating params
|		fit[] -- a list radar fit data (list for fitex, fitex2, lmfit)
|		raw -- radar rawacf data
|		iq -- radar iqdat data
|	
|		** = not implemented yet
|
|	DECLARATION: 
|		myBeam = pydarn.sdio.radBeam()
|		
|	
|	Written by AJ 20121130
|	*******************************
	"""
	
	#SQL table name
	__tablename__ = "beam"
	
	#SQL columns in beam table
	beam_id = Column(Integer, primary_key=True, unique=True)
	cp = Column(SmallInteger, primary_key=True)
	stid = Column(SmallInteger, primary_key=True)
	time = Column(DateTime, primary_key=True)
	channel= Column(CHAR, primary_key=True)
	bmnum = Column(SmallInteger, primary_key=True)
	
	#children in SQL table
	prm = relationship("prmData", uselist=False, backref="beam")
	allfits = relationship("fitData", backref="beam")
	
	#when we are ready to implement these on the db
	raw = relationship("rawData", uselist=False, backref="beam")
	#iq = relationship("iqData", uselist=False, backref="beam")
	
	def __init__(self, beamDict=None, myBeam=None, proctype=None):
		#initialize the attr values
		self.cp = -1
		self.stid = -1
		self.time = datetime.datetime(2001,1,1)
		self.bmnum = -1
		self.channel = 'a'
		self.fit = fitData()
		self.raw=rawData()
		
		#if we are intializing from an object, do that
		if(beamDict != None): self.updateValsFromDict(beamDict)
		if(myBeam != None): self.updateVals(myBeam)
		
	def updateValsFromDict(self, beamDict):
		"""
	|	*******************************
	|	FUNCTION updateValsFromDict
	|
	|	BELONGS TO: pydarn.sdio.radDataTypes.beamData
	|
	|	this is creAted mainly to fill a radar beam structure 
	|		with the data in a dictionary that is returned from the
	|		reading of a dmap file
	|	
	|	INPUTS:
	|		beamDict -- the dictionary containing the radar data
	|
	|	OUTPUTS: 
	|		None
	|	
	|	Written by AJ 20121130
	|	*******************************
		"""
		
		if(beamDict.has_key('channel')): 
			if(beamDict['channel'] < 2): self.channel = 'a'
			else: self.channel = alpha[beamDict['channel']-1]
		else: self.channel = 'a'
			
		#itterate through the attributes
		for attr, value in self.__dict__.iteritems():
			#this is an alchemy attribute
			if(attr == '_sa_instance_state' or attr == 'channel'): continue
			#check for time attribute
			if(attr == 'time'):
				#convert from epoch to datetime
				if(beamDict.has_key(attr)): 
					setattr(self,attr,datetime.datetime.utcfromtimestamp(beamDict[attr]))
				continue
			#any other attribute, copy the value
			try: setattr(self,attr,beamDict[attr])
			except: 
				if(isinstance(value,int)):
					(setattr(self,attr,-1))
					
	def updateVals(self, myBeam):
		"""
	|	*******************************
	|	FUNCTION updateVals
	|
	|	BELONGS TO: pydarn.sdio.radDataTypes.beamData
	|
	|	this is created mainly to deep copy a radar beam stricutre
	|	
	|	INPUTS:
	|		myBeam -- the object containing the radar data
	|
	|	OUTPUTS: 
	|		None
	|		
	|	
	|	Written by AJ 20121130
	|	*******************************
			"""
		#iterate through the attributes
		for attr, value in self.__dict__.iteritems():
			#this is an alchemy attribute
			if(attr == '_sa_instance_state' or attr == 'beam_id'): continue
			#copy the attribute value
			try: setattr(self,attr,object.__getattribute__(myBeam, attr))
			except: setattr(self,attr,-1)
			
	def __repr__(self):
		return "<Beam("+str(self.time)+", '%d', '%d','%d', '%s')>" % (self.cp, self.stid, self.bmnum, self.channel)
		
class prmData(Base):
	"""
|	*******************************
|	PACKAGE: pydarn.sdio.radDataTypes
|
|	CLASS: radPrm
|
|	PURPOSE: represent radar operating parameters
|
|	DECLARATION: 
|		myprm = Prm(radarPrm)
|
|	ATTRS:
|		nave  --				number of averages
|		lagfr  --				lag to first range in us
|		smsep  --				sample separation in us
|		bmazm  --				beam azimuth
|		scan  --				new scan flag
|		rxrise  --			receiver rise time
|		inttsc  --			integeration time (sec)
|		inttus  --			integration time (us)
|		mpinc  --				multi pulse increment (tau, basic lag time) in us
|		mppul  --				number of pulses
|		mplgs  --				number of lags
|		mplgexs  --			number of lags (tauscan)
|		nrang  --				number of range gates
|		frang  --				first range gate (km)
|		rsep  --				range gate separation in km
|		xcf  --					xcf flag
|		tfreq  --				transmit freq in kHz
|		ifmode  --			if mode flag
|		ptab  -- 				pulse table
|		ltab  -- 				lag table
|		noisemean  --		mean noise level
|		noisesky  --		sky noise level
|		noisesearch  --	freq search noise level
|
|	Written by AJ 20121130
|	"""
	
	#SQL table name
	__tablename__ = "prm"
	
	#SQL columns
	prm_id = Column(Integer, primary_key=True)
	beam_id = Column(Integer, ForeignKey('beam.beam_id'))
	smsep = Column(SmallInteger)
	noisesearch = Column(Float)
	nave = Column(SmallInteger)
	lagfr = Column(SmallInteger)
	smsep = Column(SmallInteger)
	noisesearch = Column(Float)
	noisemean = Column(Float)
	noisesky = Column(Float)
	bmazm = Column(Float)
	scan = Column(SmallInteger)
	rxrise = Column(SmallInteger)
	inttsc = Column(SmallInteger)
	inttus = Column(Integer)
	mpinc = Column(SmallInteger)
	mppul = Column(SmallInteger)
	mplgs = Column(SmallInteger)
	mplgexs = Column(SmallInteger)
	nrang = Column(SmallInteger)
	frang = Column(SmallInteger)
	rsep = Column(SmallInteger)
	xcf = Column(SmallInteger)
	tfreq	 = Column(SmallInteger)
	ifmode = Column(SmallInteger)
	ptab = Column(pg.ARRAY(SmallInteger))
	ltab = Column(pg.ARRAY(SmallInteger))


	#initialize the struct
	def __init__(self, prmDict=None, myPrm=None):
		#set default values
		self.nave = -1				#number of averages
		self.lagfr = -1				#lag to first range in us
		self.smsep = -1				#sample separation in us
		self.bmazm = -1				#beam azimuth
		self.scan = -1				#new scan flag
		self.rxrise = -1			#receiver rise time
		self.inttsc = -1			#integeration time (sec)
		self.inttus = -1			#integration time (us)
		self.mpinc = -1				#multi pulse increment (tau, basic lag time) in us
		self.mppul = -1				#number of pulses
		self.mplgs = -1				#number of lags
		self.mplgexs = -1			#number of lags (tauscan)
		self.nrang = -1				#number of range gates
		self.frang = -1				#first range gate (km)
		self.rsep = -1				#range gate separation in km
		self.xcf = -1					#xcf flag
		self.tfreq = -1				#transmit freq in kHz
		self.ifmode = -1			#if mode flag
		self.ptab = []				#pulse table
		self.ltab = []				#lag table
		self.noisemean = -1		#mean noise level
		self.noisesky = -1		#sky noise level
		self.noisesearch = -1#freq search noise level
		
		#if we are copying a structure, do that
		if(prmDict != None): self.updateValsFromDict(prmDict)
		if(myPrm != None): self.updateVals(myPrm)
		
	def updateValsFromDict(self, prmDict):
		"""
	|	*******************************
	|	FUNCTION updateValsFromDict
	|
	|	BELONGS TO: pydarn.sdio.radDataTypes.prmData
	|
	|	this is created mainly to fill a radar params structure 
	|		with the data in a dictionary that is returned from the
	|		reading of a dmap file
	|	
	|	INPUTS:
	|		prmDict -- the dictionary containing the radar data
	|
	|	OUTPUTS: 
	|		None
	|	
	|	Written by AJ 20121130
	|	*******************************
		"""
		#iterate through prmData's attributes
		for attr, value in self.__dict__.iteritems():
			#check for special attributes
			if(attr == '_sa_instance_state' or attr == 'beam_id' or attr == 'prm_id'): continue
			#try to copy the value
			try: setattr(self,attr,prmDict[attr])
			except:
				#check for attibutes we need to rename
				if(attr == 'noisesearch'):
					try: self.noisesearch = prmDict['noise.search']
					except: pass
				elif(attr == 'noisemean'):
					try: self.noisemean = prmDict['noise.mean']
					except: pass
				elif(attr == 'noisesky'):
					try: self.noisesky = prmDict['noise.sky']
					except: pass
				elif(attr == 'inttus'):
					try: self.inttus = prmDict['intt.us']
					except: pass
				elif(attr == 'inttsc'): 
					try: self.inttsc = prmDict['intt.sc']
					except: pass
				#else put in a default value
				elif(isinstance(value,list)): setattr(self,attr,[])
				else: setattr(self,attr,-1)
		
	def updateVals(self, myPrm):
		"""
	|	*******************************
	|	FUNCTION updateVals
	|
	|	BELONGS TO: pydarn.sdio.radDataTypes.prmData
	|
	|	this is created mainly to deep copy a radar prmData stricutre
	|	
	|	INPUTS:
	|		myPrm -- the object containing the radar data
	|
	|	OUTPUTS: 
	|		None
	|		
	|	Written by AJ 20121130
	|	*******************************
		"""
		for attr, value in self.__dict__.iteritems():
			if(attr == '_sa_instance_state' or attr == 'beam_id' or attr == 'prm_id'): continue
			try: 
				setattr(self,attr,object.__getattribute__(myPrm, attr))
			except:
				if(isinstance(value,list)): setattr(self,attr,[])
				elif(isinstance(value,String)): setattr(self,attr,'')
				else: setattr(self,attr,-1)

class fitData(Base):
	"""
|	*******************************
|	CLASS pydarn.sdio.fitData
|
|	a class to contain the fit data from a radar beam sounding
|	
|	ATTRS:
|		proctype -- 	fitting processing type
|		pwr0  --			lag 0 power
|		slist  --			list of range gates with backscatter
|		npnts --			number of range gates with scatter
|		nlag  --			number of good lags
|		qflg  --			quality flag
|		gflg  --			ground scatter flag
|		p_l  --				lambda power
|		p_l_e  --			lambda power error
|		p_s  --				sigma power
|		p_s_e  --			sigma power error
|		v  --					velocity
|		v_e  --				velocity error
|		w_l  --				lambda spectral width
|		w_l_e  --			lambda width error
|		w_s  --				sigma spectral width
|		w_s_e  --			sigma width error
|		phi0  --			phi 0
|		phi0_e  --		phi 0 error
|		elv  --				elevation angle
|	
|	DECLARATION: 
|		myFit = pydarn.sdio.fitData()
|		
|	Written by AJ 20121130
|	*******************************
|	"""

	
	#create the sql table
	__tablename__ = "allfits"
	
	#create the SQL columns
	fit_id = Column(Integer, primary_key=True)
	proctype = Column(String, primary_key=True)
	beam_id = Column(Integer, ForeignKey('beam.beam_id'))
	pwr0 = Column(pg.ARRAY(Float))
	slist = Column(pg.ARRAY(SmallInteger))
	npnts = Column(SmallInteger)
	nlag = Column(pg.ARRAY(SmallInteger))
	qflg = Column(pg.ARRAY(SmallInteger))
	gflg = Column(pg.ARRAY(SmallInteger))
	p_l = Column(pg.ARRAY(Float))
	p_l_e	 = Column(pg.ARRAY(Float))
	p_s = Column(pg.ARRAY(Float))
	p_s_e	 = Column(pg.ARRAY(Float))
	v = Column(pg.ARRAY(Float))
	v_e	 = 	Column(pg.ARRAY(Float))
	w_l	 = 	Column(pg.ARRAY(Float))
	w_l_e	 = 	Column(pg.ARRAY(Float))
	w_s	 = 	Column(pg.ARRAY(Float))
	w_s_e	 = 	Column(pg.ARRAY(Float))
	phi0	 = 	Column(pg.ARRAY(Float))
	phi0_e = 		Column(pg.ARRAY(Float))
	elv	 = 	Column(pg.ARRAY(Float))


	#initialize the struct
	def __init__(self, fitDict=None, myFit=None):
		self.proctype = 'null'	#processing type
		self.pwr0 = []			#lag 0 power
		self.slist = []			# list of range gates with backscatter
		self.npnts = 0			#number of range gates with scatter
		self.nlag = []			#number of good lags
		self.qflg = []			#quality flag
		self.gflg = []			#ground scatter flag
		self.p_l = []				#lambda power
		self.p_l_e = []			#lambda power error
		self.p_s = []				#sigma power
		self.p_s_e = []			#sigma power error
		self.v = []					#velocity
		self.v_e = []				#velocity error
		self.w_l = []				#lambda spectral width
		self.w_l_e = []			#lambda width error
		self.w_s = []				#sigma spectral width
		self.w_s_e = []			#sigma width error
		self.phi0 = []			#phi 0
		self.phi0_e = []		#phi 0 error
		self.elv = []				#elevation angle
		
		if(fitDict != None): self.updateValsFromDict(fitDict)
		if(myFit != None): self.updateVals(myFit)
		
	def updateValsFromDict(self, fitDict):
		"""
	|	*******************************
	|	FUNCTION updateValsFromDict
	|
	|	BELONGS TO: pydarn.sdio.radDataTypes.fitData
	|
	|	this is created mainly to fill a radar fit structure 
	|		with the data in a dictionary that is returned from the
	|		reading of a dmap file
	|	
	|	INPUTS:
	|		prmDict -- the dictionary containing the radar data
	|
	|	OUTPUTS: 
	|		None
	|	
	|	Written by AJ 20121130
	|	*******************************
		"""
		for attr, value in self.__dict__.iteritems():
			if(attr == '_sa_instance_state' or attr == 'beam_id' or attr == 'fit_id'): continue
			try:
				setattr(self,attr,fitDict[attr])
			except:
				if(isinstance(value,int)): setattr(self,attr,0)
				elif(isinstance(value,list)): setattr(self,attr,[])
				
	def updateVals(self, myFit):
		for attr, value in self.__dict__.iteritems():
			if(attr == '_sa_instance_state' or attr == 'beam_id' or attr == 'fit_id'): continue
			try: setattr(self,attr,object.__getattribute__(myFit, attr))
			except:
				if(isinstance(value,list)): setattr(self,attr,[])
				elif(isinstance(value,String)): setattr(self,attr,'')
				else: setattr(self,attr,-1)
				
class rawData(Base):
	"""
|	*******************************
|	CLASS pydarn.sdio.rawData
|
|	a class to contain the fit data from a radar beam sounding
|	
|	ATTRS:
|		acf -- 	acf data
|		xcf -- xcf data
|	
|	DECLARATION: 
|		myRaw = pydarn.sdio.rawData()
|		
|	Written by AJ 20121130
|	*******************************
|	"""

	
	#create the sql table
	__tablename__ = "raw"
	
	#create the SQL columns
	raw_id = Column(Integer, primary_key=True)
	beam_id = Column(Integer, ForeignKey('beam.beam_id'))
	acfd = Column(pg.ARRAY(Float))
	xcfd = Column(pg.ARRAY(Float))
	
	#initialize the struct
	def __init__(self, rawDict=None, myRaw=None):
		self.acfd = []			#lag 0 power
		self.xcfd = []			# list of range gates with backscatter
		
		if(rawDict != None): self.updateValsFromDict(rawDict)
		if(myRaw != None): self.updateVals(myRaw)
		
	def updateValsFromDict(self, rawDict):
		"""
	|	*******************************
	|	FUNCTION updateValsFromDict
	|
	|	BELONGS TO: pydarn.sdio.radDataTypes.rawData
	|
	|	this is created mainly to fill a radar raw structure 
	|		with the data in a dictionary that is returned from the
	|		reading of a dmap file
	|	
	|	INPUTS:
	|		rawDict -- the dictionary containing the radar data
	|
	|	OUTPUTS: 
	|		None
	|	
	|	Written by AJ 20121130
	|	*******************************
		"""
		for attr, value in self.__dict__.iteritems():
			if(attr == '_sa_instance_state' or attr == 'beam_id' or attr == 'raw_id'): continue
			try:
				setattr(self,attr,rawDict[attr])
			except:
				if(isinstance(value,int)): setattr(self,attr,0)
				elif(isinstance(value,list)): setattr(self,attr,[])
				
	def updateVals(self, myRaw):
		for attr, value in self.__dict__.iteritems():
			if(attr == '_sa_instance_state' or attr == 'beam_id' or attr == 'raw_id'): continue
			try: setattr(self,attr,object.__getattribute__(myRaw, attr))
			except:
				if(isinstance(value,list)): setattr(self,attr,[])
				elif(isinstance(value,String)): setattr(self,attr,'')
				else: setattr(self,attr,-1)
				
class beamD(dict):
	"""
	*******************************
	CLASS pydarn.io.beam

	a dictionary class containing a pydarn.io.prm class 
	and either a pydarn.io.fit or pydarn.io.raw class
	
	KEYS:
		['prm','fit','raw']
	VALUES:
		[prmData,fitData, rawData]
	
	EXAMPLES:
	
	DECLARATION: 
		myBeam = pydarn.io.beam()
		
	ACCESS:
		myBeam['prm'] = prmData
	
	Written by AJ 20120808
	*******************************
	"""
	def __init__(self):
		self._dict = {}

class prmDataD(dict):
	"""
	*******************************
	CLASS pydarn.io.prmData

	a dictionary class containing radar operating parameter data
	
	KEYS:
		['cp','tfreq', ...]
	VALUES:
		[CP ID, T Freq, ...]
	
	EXAMPLES:
	
	DECLARATION: 
		myPrm = pydarn.io.prmData()
		
	ACCESS:
		myPrm['tfreq'] = tfreq
	
	Written by AJ 20120808
	*******************************
	"""
	def __init__(self):
		self._dict = {}
		self['radar.revision.major'] = []
		self['radar.revision.minor'] = []
		self['origin.code'] = []
		self['origin.time'] = []
		self['origin.command'] = []		#command used to generate file	
		self['cp'] = []								#control prog id
		self['stid'] = []							#station id
		self['time'] = []							#time of beam sounding
		self['txpow'] = []
		self['nave'] = []							#number of averages
		self['atten'] = []
		self['lagfr'] = []						#lag to first range in us
		self['smsep'] = []						#sample separation in us
		self['ercod'] = []
		self['stat.agc'] = []
		self['stat.lopwr'] = []
		self['noise.search'] = []			#clear freq search noise
		self['noise.mean'] = []				#avg of 10 quietest range gates
		self['noise.sky'] = []				#noise used for power calculation
		self['noise.lag0'] = []				#?
		self['noise.vel'] = []				#?
		self['channel'] = []					#channel
		self['bmnum'] = []						#beam number
		self['bmazm'] = []						#beam azimuth
		self['scan'] = []							#new scan flag
		self['offset'] = []
		self['rxrise'] = []						#rec. rise time
		self['intt.sc'] = []					#integration time in s
		self['intt.us'] = []					#integration time in us
		self['txpl'] = []
		self['mpinc'] = []						#basic lag time in us
		self['mppul'] = []						#number of pulses
		self['mplgs'] = []						#number of lags
		self['mplgexs'] = []					#number of tauscan lags
		self['nrang'] = []						#number of range gates
		self['frang'] = []						#distance to first range gate in km
		self['rsep'] = []							#range gate separation in km
		self['xcf'] = []							#xcf flag
		self['tfreq'] = []						#tansmit frequency
		self['mxpwr'] = []
		self['lvmax'] = []
		self['ifmode'] = []						#ifmode flag
		self['combf'] = []
		self['fitacf.revision.major'] = []
		self['fitacf.revision.minor'] = []
		self['ptab'] = []							#pulse table
		self['ltab'] = []							#lag table
		
class fitDataD(dict):
	"""
	*******************************
	CLASS pydarn.io.fitData

	a dictionary class containing fitted radar data
	
	EXAMPLES:
	
	DECLARATION: 
		myFit = pydarn.io.fitData()
		
	ACCESS:
		#number of range gates with scatter:
		myFit['npnts']
		#first range gate with scatter
		r = myFit['slist'][0]
		#velocity of range gate r
		v = myFit['v'][0]
	
	Written by AJ 20120808
	*******************************
	"""
	def __init__(self):
		self._dict = {}
		self['pwr0'] = []							#lag 0 power array
		self['slist'] = []						#list of range gates w/ scatter
		self['npnts'] = 0						  #number of gates w/ scatter
		self['nlag'] = []							#number of good lags
		self['qflg'] = []							#quality flag
		self['gflg'] = []							#g scat flag
		self['p_l'] = []							#lambda fit power
		self['p_l_e'] = []						#lambda fit power error
		self['p_s'] = []							#sigma fit power
		self['p_s_e'] = []						#sigma fit power error
		self['v'] = []								#Doppler velocity
		self['v_e'] = []							#velocity error
		self['w_l'] = []							#lambda fit width
		self['w_l_e'] = []						#lambda fit width error
		self['sd_l'] = []							#?
		self['sd_s'] = []							#?
		self['sd_phi'] = []						#?
		self['x_qflg'] = []						#?
		self['x_gflg'] = []						#?
		self['x_p_l'] = []
		self['x_p_l_e'] = []
		self['x_p_s'] = []
		self['x_p_s_e'] = []
		self['x_v'] = []
		self['x_v_e'] = []
		self['x_w_l'] = []
		self['x_w_l_e'] = []
		self['x_w_s'] = []
		self['x_w_s_e'] = []
		self['phi0'] = []							#phase shift from main to inter. array
		self['phi0_e'] = []						#error on phase shift estimate
		self['elv'] = []							#elevation angle
		self['elv_low'] = []
		self['elv_high'] = []
		self['x_sd_l'] = []
		self['x_sd_s'] = []
		self['x_sd_phi'] = []
		
class rawDataD(dict):
	"""
	*******************************
	CLASS pydarn.io.rawData

	a dictionary class containing raw radar data
	
	EXAMPLES:
	
	DECLARATION: 
		myRaw = pydarn.io.rawData()
		
	ACCESS:
			#acf for range gate r
			acf = myRaw['acfd'][r]
			
	Written by AJ 20120808
	*******************************
	"""
	def __init__(self):
		self._dict = {}
		self['slist'] = []						#list of range gates w/ ACFS (should be all nrang)
		self['pwr0'] = []							#lag 0 powers
		self['acfd'] = []							#calculated ACFs
		self['xcfd'] = []							#claculated XCFs

        
