from utils import twoWayDict
alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

#we need to use this cipher in order to shorten variable names on the DB
#this allows us to save space as well as reduce transfer time
cipher=twoWayDict({'cp':'c','stid':'s','time':'t','bmnum':'b','channel':'ch','exflg':'ef','lmflg':'lf','acflg':'af','fitex':'ex','fitacf':'fa','lmfit':'lm','rawacf':'r','iqdat':'iq','prm':'p','nave':'n','lagfr':'l','smsep':'s','bmazm':'ba','scan':'sc','rxrise':'rx','inttsc':'is','inttus':'iu','mpinc':'mi','mppul':'mp','mplgs':'ms','mplgexs':'mx','nrang':'nr','frang':'fr','rsep':'rs','xcf':'x','tfreq':'tf','ifmode':'if','ptab':'pt','ltab':'lt','noisemean':'nm','noisesky':'ns','noisesearch':'nc','pwr0':'p0','slist':'sl','npnts':'np','nlag':'nl','qflg':'q','gflg':'g','p_l':'pl','p_l_e':'ple','p_s':'ps','p_s_e':'pse','v':'v','v_e':'ve','w_l':'wl','w_l_e':'wle','w_s':'ws','w_s_e':'wse','phi0':'i0','phi0_e':'i0e','elv':'e','acfd':'ad','xcfd':'xd','rawflg':'rf','iqflg':'iqf','seqnum':'sq','chnnum':'cm','smpnum':'sp','btnum':'bt','tatten':'ta','tnoise':'tn','toff':'to','tsze':'ts','tbadtr':'tbr','badtr':'br','mainData':'md','intData':'id','skpnum':'sk'})

refArr = twoWayDict({'exflg':'fitex','acflg':'fitacf','lmflg':'lmfit','rawflg':'rawacf','iqflg':'iqdat'})

class radDataPtr():
	"""
|	*******************************
|
|	**CLASS**: pydarn.sdio.radDataPtr
|	**PURPOSE**: a class which contains a pipeline to a data source
|	
|	**ATTRS**:
|		ptr: the data pointer (different depending on mongodo or dmap)
|		sTime: start time of the request
|		eTime: end time of the request
|		stid: station id of the request
|		channel: channel of the request
|		bmnum: beam number of the request
|		cp: control prog id of the request
|		dType: the data type, 'mongo' or 'dmap'
|		fType: the file type, 'fitacf', 'rawacf', 'iqdat', 'fitex', 'lmfit'
|	
|	**METHODS**:
|		NONE
|		
|	Written by AJ 20130108
|	*******************************
	"""
	def __init__(self,ptr=None,sTime=None,eTime=None,stid=None,channel=None,bmnum=None,cp=None):
		self.ptr = ptr
		self.sTime = sTime
		self.eTime = eTime
		self.stid = stid
		self.channel = channel
		self.bmnum = bmnum
		self.cp = cp
		self.dType = None
		self.fType = None

class baseData():
	"""
|	*******************************
|
|	**CLASS**: pydarn.sdio.baseData
|	**PURPOSE**: a base class for the radar data types.  This allows
|		for single definition of common routines
|	
|	**ATTRS**:
|		None
|	
|	**METHODS**:
|		dbDictToObj: converts a mongodb dictionary to a baseData object
|		dictToObj: comverts a dmap dictionary to a baseData object
|		toDbDict(): converts a baseData object to a mongodb dictionaty
|		
|	Written by AJ 20130108
|	*******************************
	"""
	
	def dbDictToObj(self,aDict):
		for key, val in aDict.iteritems():
			if(key == '_id'): continue
			elif(key == 'it'):
				self.inttsc = int(val)
				self.inttus = val-int(val)
			elif(key == 'tt'):
				self.tsc = int(val)
				self.tus = val-int(val)
			#if the value is a dictionary, make a recursive call
			elif(isinstance(val,dict)): 
				if(cipher[key] == 'fitex' or cipher[key] == 'lmfit' or cipher[key] == 'fitacf'):
					self.fit.dictToObj(val)
				else: getattr(self, cipher[key]).dbDictToObj(val)
			#otherwise, copy the value
			else: setattr(self,cipher[key],val)
			
	def dictToObj(self,aDict):
		for key, val in aDict.iteritems():
			#if the value is a dictionary, make a recursive call
			if(isinstance(val,dict)): 
				if(key == 'fitex' or key == 'lmfit' or key == 'fitacf'):
					self.fit.dictToObj(val)
				else: getattr(self, key).dictToObj(val)
			#otherwise, copy the value
			else: setattr(self,key,val)
			
	def toDbDict(self):
		aDict = {}
		for attr, val in self.__dict__.iteritems():
			#check for things we dont want to save
			if(attr=='inttus' or attr=='tus' or attr.rfind('_s') != -1): continue
			elif(attr == 'inttsc'): 
				try: aDict['it'] = self.inttsc + self.inttus*1e-6
				except: aDict['it'] = None
			elif(attr == 'tsc'): 
				try: aDict['tt'] = self.tsc + self.tus*1e-6
				except: aDict['tt'] = None
			#if the value is a class, recursively convert to dict
			elif(isinstance(val,baseData)): aDict[cipher[attr]] = val.toDbDict()
			#otherwise, copy the value
			else: aDict[cipher[attr]] = val
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
	|		aDict -- the dictionary containing the radar data
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
			elif(attr == 'inttus'):
				if(aDict.has_key('intt.us')): 
					self.inttus = aDict['intt.us']
				continue
			elif(attr == 'inttsc'):
				if(aDict.has_key('intt.sc')): 
					self.inttsc = aDict['intt.sc']
				continue
			elif(attr == 'noisesky'):
				if(aDict.has_key('noise.sky')): 
					self.noisesky = aDict['noise.sky']
				continue
			elif(attr == 'noisesearch'):
				if(aDict.has_key('noise.search')): 
					self.noisesearch = aDict['noise.search']
				continue
			elif(attr == 'noisemean'):
				if(aDict.has_key('noise.mean')): 
					self.noisemean = aDict['noise.mean']
				continue
			elif(attr == 'acfd' or attr == 'xcfd'):
				if(aDict.has_key(attr)): 
					setattr(self,attr,[])
					for i in range(self.parent.prm.nrang):
						rec = []
						for j in range(self.parent.prm.mplgs):
							samp = []
							for k in range(2):
								samp.append(aDict[attr][(i*self.parent.prm.mplgs+j)*2+k])
							rec.append(samp)
						getattr(self, attr).append(rec)
				else: setattr(self,attr,[])
				continue
			elif(attr == 'mainData'):
				if(aDict.has_key('data')): 
					if(len(aDict['data']) == aDict['smpnum']*aDict['seqnum']*2*2): fac = 2
					else: fac = 1
					setattr(self,attr,[])
					for i in range(aDict['seqnum']):
						rec = []
						for j in range(aDict['smpnum']):
							samp = []
							for k in range(2):
								samp.append(aDict['data'][(i*fac*aDict['smpnum']+j)*2+k])
							rec.append(samp)
						getattr(self, attr).append(rec)
				else: setattr(self,attr,[])
				continue
			elif(attr == 'intData'):
				if(aDict.has_key('data')): 
					if(len(aDict['data']) == aDict['smpnum']*aDict['seqnum']*2*2): fac = 2
					else: continue
					setattr(self,attr,[])
					for i in range(aDict['seqnum']):
						rec = []
						for j in range(aDict['smpnum']):
							samp = []
							for k in range(2):
								samp.append(aDict['data'][((i*fac+1)*aDict['smpnum']+j)*2+k])
							rec.append(samp)
						getattr(self, attr).append(rec)
				else: setattr(self,attr,[])
				continue
			try:
				setattr(self,attr,aDict[attr])
			except:
				#put in a default value if not another object
				if(not isinstance(getattr(self,attr),baseData)):
					setattr(self,attr,None)

class beamData(baseData):
	"""
|	*******************************
|	**CLASS**: pydarn.sdio.beamData
|
|	**PURPOSE**: a class to contain the data 
|		from a radar beam sounding
|	
|	**ATTRS**:
|		cp -- radar control program id number
|		stid -- radar station id number
|		time -- timestamp of beam sounding
|		channel -- radar operating channel, eg 'a', 'b', ...
|		bmnum -- beam number
|		prm -- a prmData object with oper. params
|		fit -- a fitData object with the fitted params
|		rawacf -- a rawData object with radar rawacf data
|		iqdat -- radar iqdat data (not yet implemented)
|		exflg -- a flag indicating the presence of fitex data.
|			this is useful for database operation, can
|			generally be ignored by users
|		acflg -- a flag indicating the presence of acflg data.
|			this is useful for database operation, can
|			generally be ignored by users
|		lmflg -- a flag indicating the presence of lmfit data.
|			this is useful for database operation, can
|			generally be ignored by users
|		rawflg -- a flag indicating the presence of rawacf data.
|			this is useful for database operation, can
|			generally be ignored by users
|		iqflg -- a flag indicating the presence of iqdat data.
|			this is useful for database operation, can
|			generally be ignored by users
|		fType: the file type, 'fitacf', 'rawacf', 'iqdat', 'fitex', 'lmfit'
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
		self.rawflg = None
		self.iqflg = None
		self.fitex = None
		self.fitacf = None
		self.lmfit= None
		self.fit = fitData()
		self.rawacf = rawData(parent=self)
		self.prm = prmData()
		self.iqdat = iqData()
		self.fType = None
		
		#if we are intializing from an object, do that
		if(beamDict != None): self.updateValsFromDict(beamDict)
			
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
		self.noisesearch = None	#freq search noise level
		
		#if we are copying a structure, do that
		if(prmDict != None): self.updateValsFromDict(prmDict)

class fitData(baseData):
	"""
|	*******************************
|	**CLASS** pydarn.sdio.fitData
|
|	**PURPOSE** a class to contain the fitted params of
|		a radar beam sounding
|	
|	**ATTRS**:
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
|	**DECLARATION**: 
|		myFit = pydarn.sdio.fitData()
|		
|	Written by AJ 20121130
|	*******************************
|	"""

	#initialize the struct
	def __init__(self, fitDict=None, myFit=None):
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
				
class rawData(baseData):
	"""
|	*******************************
|	**CLASS**: pydarn.sdio.rawData
|
|	**PURPOSE**: a class to contain the rawacf data from a radar beam sounding
|	
|	**ATTRS**:
|		acf -- acf data as a 3-d list.  the size is [nrang][mplgs][2]
|		xcf -- xcf data, same format as acf data
|	
|	**DECLARATION**: 
|		myRaw = pydarn.sdio.rawData()
|		
|	Written by AJ 20121130
|	*******************************
	"""

	#initialize the struct
	def __init__(self, rawDict=None, parent=None):
		self.acfd = []			#acf data
		self.xcfd = []			#xcf data
		self.parent = parent #reference to parent beam
		
		if(rawDict != None): self.updateValsFromDict(rawDict)
		
class iqData(baseData):
	"""
|	*******************************
|	**CLASS**: pydarn.sdio.iqData
|
|	**PURPOSE**: a class to contain the iq data from a radar beam sounding
|	**NOTE**: I'm not sure what all of the attributes mean
|
|	**ATTRS**:
|		chnnum -- number of channels?
|		smpnum -- number of samples per beam sounding
|		skpnum -- number of samples to skip at the 
|			beginning of a pulse sequence?
|		seqnum -- number of pulse sequences
|		tbadtr -- time of bad tr samples?
|		tval -- ?
|		atten -- ?
|		noise -- ?
|		offset -- ?
|		size -- ?
|		badtr -- bad tr samples?
|		mainData -- the actual iq samples (main array)
|			seqnum x smpnum x 2 list
|		intData -- the actual iq samples (interferometer)
|			seqnum x smpnum x 2 list
|	
|	**DECLARATION**: 
|		myIq = pydarn.sdio.iqData()
|		
|	Written by AJ 20130116
|	*******************************
	"""

	#initialize the struct
	def __init__(self, iqDict=None, parent=None):
		self.seqnum = None
		self.chnnum = None
		self.smpnum = None
		self.skpnum = None
		self.btnum = None
		self.tsc = None
		self.tus = None
		self.tatten = None
		self.tnoise = None
		self.toff = None
		self.tsze = None
		self.tbadtr = None
		self.badtr = None
		self.mainData = []
		self.intData = []
		
		if(iqDict != None): self.updateValsFromDict(iqDict)
        
