"""
.. module:: radDataTypes
   :synopsis: the classes needed for reading, writing, and storing radar data
.. moduleauthor:: AJ, 20130108
*********************
**Module**: pydarn.sdio.radDataTypes
*********************
**Classes**:
	* :class:`radDataPtr`
	* :class:`baseData`
	* :class:`beamData`
	* :class:`prmData`
	* :class:`fitData`
	* :class:`rawData`
	* :class:`iqData`
"""


from utils import twoWayDict
alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

#we need to use this cipher in order to shorten variable names on the DB
#this allows us to save space as well as reduce transfer time
cipher=twoWayDict({'cp':'c','stid':'s','time':'t','bmnum':'b','channel':'ch','exflg':'ef','lmflg':'lf','acflg':'af','fitex':'ex','fitacf':'fa','lmfit':'lm','rawacf':'r','iqdat':'iq','prm':'p','nave':'n','lagfr':'l','smsep':'s','bmazm':'ba','scan':'sc','rxrise':'rx','inttsc':'is','inttus':'iu','mpinc':'mi','mppul':'mp','mplgs':'ms','mplgexs':'mx','nrang':'nr','frang':'fr','rsep':'rs','xcf':'x','tfreq':'tf','ifmode':'if','ptab':'pt','ltab':'lt','noisemean':'nm','noisesky':'ns','noisesearch':'nc','pwr0':'p0','slist':'sl','npnts':'np','nlag':'nl','qflg':'q','gflg':'g','p_l':'pl','p_l_e':'ple','p_s':'ps','p_s_e':'pse','v':'v','v_e':'ve','w_l':'wl','w_l_e':'wle','w_s':'ws','w_s_e':'wse','phi0':'i0','phi0_e':'i0e','elv':'e','acfd':'ad','xcfd':'xd','rawflg':'rf','iqflg':'iqf','seqnum':'sq','chnnum':'cm','smpnum':'sp','btnum':'bt','tatten':'ta','tnoise':'tn','toff':'to','tsze':'ts','tbadtr':'tbr','badtr':'br','mainData':'md','intData':'id','skpnum':'sk'})

refArr = twoWayDict({'exflg':'fitex','acflg':'fitacf','lmflg':'lmfit','rawflg':'rawacf','iqflg':'iqdat'})

class radDataPtr():
	"""A class which contains a pipeline to a data source
	
	**Attrs**:
		* **ptr** (file or mongodb query object): the data pointer (different depending on mongodo or dmap)
		* **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): start time of the request
		* **eTime** (`datetime <http://tinyurl.com/bl352yx>`_): end time of the request
		* **stid** (int): station id of the request
		* **channel** (str): channel of the request
		* **bmnum** (int): beam number of the request
		* **cp** (int): control prog id of the request
		* **dType** (str): the data type, 'mongo' or 'dmap'
		* **fType** (str): the file type, 'fitacf', 'rawacf', 'iqdat', 'fitex', 'lmfit'
	**Methods**:
		* Nothing.
		
	Written by AJ 20130108
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
		
	def __repr__(self):
		myStr = 'radDataPtr\n'
		for key,var in self.__dict__.iteritems():
			myStr += key+' = '+str(var)+'\n'
		return myStr

class baseData():
	"""a base class for the radar data types.  This allows for single definition of common routines
	
	**ATTRS**:
		* Nothing.
	**METHODS**:
		* :func:`dbDictToObj`: converts a mongodb dictionary to a baseData object
		* :func:`toDbDict`: converts a baseData object to a mongodb dictionaty
		* :func:`updateValsFromDict`: converts a dict from a dmap file to baseData
		
	Written by AJ 20130108
	"""
	
	def dbDictToObj(self,aDict):
		"""This method is used to parse a dictionary of radar data from the mongodb into a :class:`baseData` object.  
		
		.. note::
			In general, users will not need to use this.
			
		**Args**: 
			* **aDict** (dict): the dictionary from the mongodb
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myBaseData.dbDictToObj(mongoDbDict)
			
		written by AJ, 20130123
		"""
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
			
	def toDbDict(self):
		"""This method is used to convert a :class:`baseData` object into a mongodb radData data dictionary.  
		
		.. note::
			In general, users will not need to worry about this.
			
		**Args**: 
			* Nothing.
		**Returns**:
			* **aDict** (dict): a dictionary in the correct format for writing to the radData mongodb
		**Example**:
			::
			
				mongoDbDict = aBaseDataObj.todbDict()
			
		written by AJ, 20130123
		"""
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
		"""A function to to fill a radar params structure with the data in a dictionary that is returned from the reading of a dmap file
		
		.. note::
			In general, users will not need to us this.
			
		**Args**:
			* **aDict (dict):** the dictionary containing the radar data
		**Returns**
			* nothing.
			
		Written by AJ 20121130
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
					
	#def __repr__(self):
		#myStr = ''
		#for key,var in self.__dict__.iteritems():
			#if(isinstance(var,baseData) and key != 'parent'):
				#print key
				#myStr += key+'\n'
				#myStr += str(var)
			#else:
				#myStr += key+' = '+str(var)+'\n'
		#return myStr

class beamData(baseData):
	"""a class to contain the data from a radar beam sounding, extends class :class:`baseData`
	
	**Attrs**:
		* **cp** (int): radar control program id number
		* **stid** (int): radar station id number
		* **time** (`datetime <http://tinyurl.com/bl352yx>`_): timestamp of beam sounding
		* **channel** (str): radar operating channel, eg 'a', 'b', ...
		* **bmnum** (int): beam number
		* **prm** (:class:`prmData`): operating params
		* **fit** (:class:`fitData`): fitted params
		* **rawacf** (:class:`rawData`): rawacf data
		* **iqdat** (:class:`iqData`): iqdat data
		* **fitex** (:class:`fitData`): fitted params from fitex file.  this is useful for mongodb interface.  Users can ignore this, just use at the fit attribute.
		* **fitacf** (:class:`fitData`): fitted params from fitacf file.  this is useful for mongodb interface.  Users can ignore this, just use at the fit attribute.
		* **lmfit** (:class:`fitData`): fitted params from lmfit file.  this is useful for mongodb interface.  Users can ignore this, just use at the fit attribute.
		* **exflg** (int): a flag indicating the presence of fitex data. this is useful for database operation, can enerally be ignored by users
		* **acflg** (int): a flag indicating the presence of acflg data. this is useful for database operation, can generally be ignored by users
		* **lmflg** (int): a flag indicating the presence of lmfit data. this is useful for database operation, can generally be ignored by users
		* **rawflg** (int): a flag indicating the presence of rawacf data. this is useful for database operation, can generally be ignored by users
		* **iqflg** (int): a flag indicating the presence of iqdat data. this is useful for database operation, can generally be ignored by users
		* **fType** (str): the file type, 'fitacf', 'rawacf', 'iqdat', 'fitex', 'lmfit'

	**Example**: 
		::
		
			myBeam = pydarn.sdio.radBeam()
		
	Written by AJ 20121130
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
		import datetime as dt
		myStr = 'Beam record FROM: '+str(self.time)+'\n'
		for key,var in self.__dict__.iteritems():
			myStr += key+' = '+str(var)+'\n'
		return myStr
		
class prmData(baseData):
	"""A class to represent radar operating parameters, extends :class:`baseData`

	**Attrs**:
		* **nave**  (int): number of averages
		* **lagfr**  (int): lag to first range in us
		* **smsep**  (int): sample separation in us
		* **bmazm**  (float): beam azimuth
		* **scan**  (int): new scan flag
		* **rxrise**  (int): receiver rise time
		* **inttsc**  (int): integeration time (sec)
		* **inttus**  (int): integration time (us)
		* **mpinc**  (int): multi pulse increment (tau, basic lag time) in us
		* **mppul**  (int): number of pulses
		* **mplgs**  (int): number of lags
		* **mplgexs**  (int): number of lags (tauscan)
		* **nrang**  (int): number of range gates
		* **frang**  (int): first range gate (km)
		* **rsep**  (int): range gate separation in km
		* **xcf**  (int): xcf flag
		* **tfreq**  (int): transmit freq in kHz
		* **ifmode**  (int): if mode flag
		* **ptab**  (mppul length list): pulse table
		* **ltab**  (mplgs x 2 length list): lag table
		* **noisemean**  (float): mean noise level
		* **noisesky**  (float): sky noise level
		* **noisesearch**  (float): freq search noise level

	Written by AJ 20121130
	"""

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
	"""a class to contain the fitted params of a radar beam sounding, extends :class:`baseData`
	
	**Attrs**:
		* **pwr0**  (prm.nrang length list): lag 0 power
		* **slist**  (npnts length list): list of range gates with backscatter
		* **npnts** (int): number of range gates with scatter
		* **nlag**  (npnts length list): number of good lags
		* **qflg**  (npnts length list): quality flag
		* **gflg**  (npnts length list): ground scatter flag
		* **p_l**  (npnts length list): lambda power
		* **p_l_e**  (npnts length list): lambda power error
		* **p_s**  (npnts length list): sigma power
		* **p_s_e**  (npnts length list): sigma power error
		* **v**  (npnts length list): velocity
		* **v_e**  (npnts length list): velocity error
		* **w_l**  (npnts length list): lambda spectral width
		* **w_l_e**  (npnts length list): lambda width error
		* **w_s**  (npnts length list): sigma spectral width
		* **w_s_e**  (npnts length list): sigma width error
		* **phi0**  (npnts length list): phi 0
		* **phi0_e**  (npnts length list): phi 0 error
		* **elv**  (npnts length list): elevation angle
	
	**Example**: 
		::
		
			myFit = pydarn.sdio.fitData()
		
	Written by AJ 20121130
	"""

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
	"""a class to contain the rawacf data from a radar beam sounding, extends :class:`baseData`
	
	**Attrs**:
		* **acfd** (nrang x mplgs x 2 length list): acf data
		* **xcfd** (nrang x mplgs x 2 length list): xcf data
	
	**Example**: 
		::
		
			myRaw = pydarn.sdio.rawData()
		
	Written by AJ 20130125
	"""

	#initialize the struct
	def __init__(self, rawDict=None, parent=None):
		self.acfd = []			#acf data
		self.xcfd = []			#xcf data
		self.parent = parent #reference to parent beam
		
		if(rawDict != None): self.updateValsFromDict(rawDict)
		
class iqData(baseData):
	""" a class to contain the iq data from a radar beam sounding, extends :class:`baseData`
	
	.. warning::
		I'm not sure what all of the attributes mean.  if somebody knows what these are, please help!

	**Attrs**:
		* **chnnum** (int): number of channels?
		* **smpnum** (int): number of samples per pulse sequence
		* **skpnum** (int): number of samples to skip at the beginning of a pulse sequence?
		* **seqnum** (int): number of pulse sequences
		* **tbadtr** (? length list): time of bad tr samples?
		* **tval** (? length list): ?
		* **atten** (? length list): ?
		* **noise** (? length list): ?
		* **offset** (? length list): ?
		* **size** (? length list): ?
		* **badtr** (? length list): bad tr samples?
		* **mainData** (seqnum x smpnum x 2 length list): the actual iq samples (main array)
		* **intData** (seqnum x smpnum x 2 length list): the actual iq samples (interferometer)
	
	**Example**: 
		::
		
			myIq = pydarn.sdio.iqData()
		
	Written by AJ 20130116
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
        
