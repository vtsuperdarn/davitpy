from datetime import datetime as dt

options = {}
options['timeStep']       = 2.          #;timeStep between scans in Minutes.
options['param']          = 'power'
options['scale']          = [-25, 25]
options['filtered']       = False
options['ajground']       = False
options['scatterflag']    = 1
options['sim']            = 0 
options['keep_lr']        = 0 
options['kx_min']         = 0.05
options['ky_min']         = 0.05
options['coord']          = 'geog'
options['dkx']            = 0.001
options['dky']            = 0.001
options['gl']             = 3
options['test']           = 0
options['nmax']           = 5
options['fir_filter']     = 1
options['zero_padding']   = 1
options['use_all_cells']  = 1
options['fft_range']      = [0., 1.5]
options['fir_scale']      = [-10, 10]

params                    = {}
params['datetime']        = [dt(2010,11,19,9,30), dt(2010,11,19,19,30)]
params['radar']           = 'gbr'
params['channel']         = 'a'
params['bmnum']            = 6
params['drange']          = [500,1000]
params['band']            = [0.3,1.2]
params['kmax']            = 0.05
params['fir_datetime']    = [dt(2010,11,19,14,10), dt(2010,11,19,16,00)]

class music(object):
  def __init__(self):
   self.options = options
   self.params  = params
