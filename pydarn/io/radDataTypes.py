import pydarn 

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
		myData = prm.io.radData()
		
	ACCESS:
		myData[datetime] = beam
	
	Written by AJ 20120808
	*******************************
	"""
	
	def __init__(self):
		self._dict = {}
		self.times = []
		self.nrecs = 0
		self.ftype = 'no data'
		
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
		
		myData = pydarn.io.radData()
		
		for k in self.iterkeys():
			if(self[k]['prm']['bmnum'] == bmnum):
				myData[k] = self[k]
			
		myData.times = myData.getTimes()
		myData.nrecs = len(myData.times)
		return myData
      
class beam(dict):
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

class prmData(dict):
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
		#self['radar.revision.major'] = []
		#self['radar.revision.minor'] = []
		#self['origin.code'] = []
		#self['origin.time'] = []
		self['origin.command'] = []		#command used to generate file	
		self['cp'] = []								#control prog id
		self['stid'] = []							#station id
		self['time'] = []							#time of beam sounding
		#self['txpow'] = []
		self['nave'] = []							#number of averages
		#self['atten'] = []
		self['lagfr'] = []						#lag to first range in us
		self['smsep'] = []						#sample separation in us
		#self['ercod'] = []
		#self['stat.agc'] = []
		#self['stat.lopwr'] = []
		self['noise.search'] = []			#clear freq search noise
		self['noise.mean'] = []				#avg of 10 quietest range gates
		self['noise.sky'] = []				#noise used for power calculation
		self['noise.lag0'] = []				#?
		self['noise.vel'] = []				#?
		self['channel'] = []					#channel
		self['bmnum'] = []						#beam number
		self['bmazm'] = []						#beam azimuth
		self['scan'] = []							#new scan flag
		#self['offset'] = []
		self['rxrise'] = []						#rec. rise time
		self['intt.sc'] = []					#integration time in s
		self['intt.us'] = []					#integration time in us
		#self['txpl'] = []
		self['mpinc'] = []						#basic lag time in us
		self['mppul'] = []						#number of pulses
		self['mplgs'] = []						#number of lags
		self['mplgexs'] = []					#number of tauscan lags
		self['nrang'] = []						#number of range gates
		self['frang'] = []						#distance to first range gate in km
		self['rsep'] = []							#range gate separation in km
		self['xcf'] = []							#xcf flag
		self['tfreq'] = []						#tansmit frequency
		#self['mxpwr'] = []
		#self['lvmax'] = []
		self['ifmode'] = []						#ifmode flag
		#self['combf'] = []
		#self['fitacf.revision.major'] = []
		#self['fitacf.revision.minor'] = []
		self['ptab'] = []							#pulse table
		self['ltab'] = []							#lag table
		
    
class fitData(dict):
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
		self['npnts'] = []						#number of gates w/ scatter
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
		#self['x_p_l'] = []
		#self['x_p_l_e'] = []
		#self['x_p_s'] = []
		#self['x_p_s_e'] = []
		#self['x_v'] = []
		#self['x_v_e'] = []
		#self['x_w_l'] = []
		#self['x_w_l_e'] = []
		#self['x_w_s'] = []
		#self['x_w_s_e'] = []
		self['phi0'] = []							#phase shift from main to inter. array
		self['phi0_e'] = []						#error on phase shift estimate
		self['elv'] = []							#elevation angle
		self['elv_low'] = []
		self['elv_high'] = []
		#self['x_sd_l'] = []
		#self['x_sd_s'] = []
		#self['x_sd_phi'] = []
		
        
class rawData(dict):
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

        