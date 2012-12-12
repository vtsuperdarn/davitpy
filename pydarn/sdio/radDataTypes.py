from sqlalchemy import *
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, CHAR
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relationship, sessionmaker
from pydarn.sdio import *
import numpy, pydarn, datetime
alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

class baseData():
	
	def dictToObj(self,aDict):
		for key, val in aDict.iteritems():
			#if the value is a dictionary, make a recursive call
			if(isinstance(val,dict)): 
				if(key == 'fitex' or key == 'lmfit' or key == 'fitacf'):
					self.fit.dictToObj(val)
				else: getattr(self, key).dictToObj(val)
			#otherwise, copy the value
			else: setattr(self,key,val)
			
	def objToDict(self):
		aDict = {}
		for attr, val in self.__dict__.iteritems():
			#if the value is a class, recursively convert to dict
			if(isinstance(val,baseData)): aDict[attr] = val.objToDict()
			#otherwise, copy the value
			else: aDict[attr] = val
		return aDict
			
	def updateValsFromDict(self, aDict):
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
		
		import datetime as dt
		
		#iterate through prmData's attributes
		for attr, value in self.__dict__.iteritems():
			#check for special params
			if(attr == 'time'):
				#convert from epoch to datetime
				if(aDict.has_key(attr) and isinstance(aDict[attr], float)): 
					setattr(self,attr,dt.datetime.utcfromtimestamp(aDict[attr]))
				continue
			elif(attr == 'channel'):
				if(aDict.has_key('channel')): 
					if(isinstance(aDict.has_key('channel'), int)):
						if(aDict['channel'] < 2): self.channel = 'a'
						else: self.channel = alpha[aDict['channel']-1]
					else: self.channel = aDict['channel']
				else: self.channel = 'a'
				continue
			try:
				setattr(self,attr,aDict[attr])
			except:
				#else put in a default value
				setattr(self,attr,None)

class beamData(baseData):
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
	def __init__(self, beamDict=None, myBeam=None, proctype=None):
		#initialize the attr values
		self.cp = None
		self.stid = None
		self.time = None
		self.bmnum = None
		self.channel = None
		self.exflg = None
		self.lmflg = None
		self.acflg = None
		self.fitex=None
		self.fitacf=None
		self.lmfit=None
		self.fit = None
		self.raw = None
		self.prm = None
		
		#if we are intializing from an object, do that
		if(beamDict != None): self.updateValsFromDict(beamDict)
		#if(myBeam != None): self.updateVals(myBeam)
			
	def __repr__(self):
		return "<Beam("+str(self.time)+", '%d', '%d','%d', '%s')>" % (self.cp, self.stid, self.bmnum, self.channel)
		
class prmData(baseData):
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

	#initialize the struct
	def __init__(self, prmDict=None, myPrm=None):
		#set default values
		self.nave = None				#number of averages
		self.lagfr = None				#lag to first range in us
		self.smsep = None				#sample separation in us
		self.bmazm = None				#beam azimuth
		self.scan = None				#new scan flag
		self.rxrise = None			#receiver rise time
		self.inttsc = None			#integeration time (sec)
		self.inttus = None			#integration time (us)
		self.mpinc = None				#multi pulse increment (tau, basic lag time) in us
		self.mppul = None				#number of pulses
		self.mplgs = None				#number of lags
		self.mplgexs = None			#number of lags (tauscan)
		self.nrang = None				#number of range gates
		self.frang = None				#first range gate (km)
		self.rsep = None				#range gate separation in km
		self.xcf = None					#xcf flag
		self.tfreq = None				#transmit freq in kHz
		self.ifmode = None			#if mode flag
		self.ptab = None				#pulse table
		self.ltab = None				#lag table
		self.noisemean = None		#mean noise level
		self.noisesky = None		#sky noise level
		self.noisesearch = None#freq search noise level
		
		#if we are copying a structure, do that
		if(prmDict != None): self.updateValsFromDict(prmDict)
		#if(myPrm != None): self.updateVals(myPrm)

class fitData(baseData):
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


	#initialize the struct
	def __init__(self, fitDict=None, myFit=None):
		self.proctype = None	#processing type
		self.pwr0 = None			#lag 0 power
		self.slist = None			# list of range gates with backscatter
		self.npnts = None			#number of range gates with scatter
		self.nlag = None			#number of good lags
		self.qflg = None			#quality flag
		self.gflg = None			#ground scatter flag
		self.p_l = None				#lambda power
		self.p_l_e = None			#lambda power error
		self.p_s = None				#sigma power
		self.p_s_e = None			#sigma power error
		self.v = None					#velocity
		self.v_e = None				#velocity error
		self.w_l = None				#lambda spectral width
		self.w_l_e = None			#lambda width error
		self.w_s = None				#sigma spectral width
		self.w_s_e = None			#sigma width error
		self.phi0 = None			#phi 0
		self.phi0_e = None		#phi 0 error
		self.elv = None				#elevation angle
		
		if(fitDict != None): self.updateValsFromDict(fitDict)
		#if(myFit != None): self.updateVals(myFit)
				
class rawData(baseData):
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
	acfd = Column(pg.ARRAY(Float(precision=4)))
	xcfd = Column(pg.ARRAY(Float(precision=4)))
	
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
		

        
