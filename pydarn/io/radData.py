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
		self['radar.revision.major'] = -9999999
		self['radar.revision.minor'] = -9999999
		self['origin.code'] = -9999999
		self['origin.time'] = -9999999
		self['origin.command'] = -9999999
		self['cp'] = -9999999
		self['stid'] = -9999999
		self['time'] = -9999999
		self['txpow'] = -9999999
		self['nave'] = -9999999
		self['atten'] = -9999999
		self['lagfr'] = -9999999
		self['smsep'] = -9999999
		self['ercod'] = -9999999
		self['stat.agc'] = -9999999
		self['stat.lopwr'] = -9999999
		self['noise.search'] = -9999999
		self['noise.mean'] = -9999999
		self['noise.sky'] = -9999999
		self['noise.lag0'] = -9999999
		self['noise.vel'] = -9999999
		self['channel'] = -9999999
		self['bmnum'] = -9999999
		self['bmazm'] = -9999999
		self['scan'] = -9999999
		self['offset'] = -9999999
		self['rxrise'] = -9999999
		self['intt.sc'] = -9999999
		self['intt.us'] = -9999999
		self['txpl'] = -9999999
		self['mpinc'] = -9999999
		self['mppul'] = -9999999
		self['mplgs'] = -9999999
		self['mplgexs'] = -9999999
		self['nrang'] = -9999999
		self['frang'] = -9999999
		self['rsep'] = -9999999
		self['xcf'] = -9999999
		self['tfreq'] = -9999999
		self['mxpwr'] = -9999999
		self['lvmax'] = -9999999
		self['ifmode'] = -9999999
		self['combf'] = -9999999
		self['fitacf.revision.major'] = -9999999
		self['fitacf.revision.minor'] = -9999999
		self['ptab'] = -9999999
		self['ltab'] = -9999999
		
    
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
		self['pwr0'] = -9999999
		self['slist'] = -9999999
		self['nlag'] = -9999999
		self['qflg'] = -9999999
		self['gflg'] = -9999999
		self['p_l'] = -9999999
		self['p_l_e'] = -9999999
		self['p_s'] = -9999999
		self['p_s_e'] = -9999999
		self['v'] = -9999999
		self['v_e'] = -9999999
		self['w_l'] = -9999999
		self['w_l_e'] = -9999999
		self['sd_l'] = -9999999
		self['sd_s'] = -9999999
		self['sd_phi'] = -9999999
		self['x_qflg'] = -9999999
		self['x_gflg'] = -9999999
		self['x_p_l'] = -9999999
		self['x_p_l_e'] = -9999999
		self['x_p_s'] = -9999999
		self['x_p_s_e'] = -9999999
		self['x_v'] = -9999999
		self['x_v_e'] = -9999999
		self['x_w_l'] = -9999999
		self['x_w_l_e'] = -9999999
		self['x_w_s'] = -9999999
		self['x_w_s_e'] = -9999999
		self['phi0'] = -9999999
		self['phi0_e'] = -9999999
		self['elv'] = -9999999
		self['elv_low'] = -9999999
		self['elv_high'] = -9999999
		self['x_sd_l'] = -9999999
		self['x_sd_s'] = -9999999
		self['x_sd_phi'] = -9999999
		
        
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
        