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
			
		Written by AJ 20120808
		*******************************
		"""
	
		k = self.keys()
		k.sort()
		return k
      
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
		self['origin.command'] = []
		self['cp'] = []
		self['stid'] = []
		self['time'] = []
		#self['txpow'] = []
		self['nave'] = []
		#self['atten'] = []
		self['lagfr'] = []
		self['smsep'] = []
		#self['ercod'] = []
		#self['stat.agc'] = []
		#self['stat.lopwr'] = []
		self['noise.search'] = []
		self['noise.mean'] = []
		self['noise.sky'] = []
		self['noise.lag0'] = []
		self['noise.vel'] = []
		self['channel'] = []
		self['bmnum'] = []
		self['bmazm'] = []
		self['scan'] = []
		#self['offset'] = []
		self['rxrise'] = []
		self['intt.sc'] = []
		self['intt.us'] = []
		#self['txpl'] = []
		self['mpinc'] = []
		self['mppul'] = []
		self['mplgs'] = []
		self['mplgexs'] = []
		self['nrang'] = []
		self['frang'] = []
		self['rsep'] = []
		self['xcf'] = []
		self['tfreq'] = []
		#self['mxpwr'] = []
		#self['lvmax'] = []
		self['ifmode'] = []
		#self['combf'] = []
		#self['fitacf.revision.major'] = []
		#self['fitacf.revision.minor'] = []
		self['ptab'] = []
		self['ltab'] = []
		
    
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
		len(myFit['slist'])
		#first range gate with scatter
		r = myFit['slist'][0]
		#velocity of range gate r
		v = myFit['v'][0]
	
	Written by AJ 20120808
	*******************************
	"""
	def __init__(self):
		self._dict = {}
		self['pwr0'] = []
		self['slist'] = []
		self['npnts'] = []
		self['nlag'] = []
		self['qflg'] = []
		self['gflg'] = []
		self['p_l'] = []
		self['p_l_e'] = []
		self['p_s'] = []
		self['p_s_e'] = []
		self['v'] = []
		self['v_e'] = []
		self['w_l'] = []
		self['w_l_e'] = []
		self['sd_l'] = []
		self['sd_s'] = []
		self['sd_phi'] = []
		self['x_qflg'] = []
		self['x_gflg'] = []
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
		self['phi0'] = []
		self['phi0_e'] = []
		self['elv'] = []
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
	
	Written by AJ 20120808
	*******************************
	"""
	def __init__(self):
		self._dict = {}
        