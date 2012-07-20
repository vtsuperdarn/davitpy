class radData(dict):
	def __init__(self):
		self._dict = {}
      
class beam(dict):
	def __init__(self):
		self._dict = {}
		self['prm'] = prmData()
		self['fit'] = fitData()
		self['raw'] = rawData()

class prmData(dict):
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
	def __init__(self):
		self._dict = {}
        
class rawData(dict):
	def __init__(self):
		self._dict = {}
        