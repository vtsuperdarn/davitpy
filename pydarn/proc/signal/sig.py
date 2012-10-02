from matplotlib import pyplot as mp
import numpy as np
import scipy as sp

class sig(object):
  def __init__(self, dtv, data, **metadata):
    """Define a vtsd sig object.

    :param dtv: datetime.datetime list
    :param data: raw data
    :param ylabel: Y-Label String for data
    :returns: sig object
    """
    defaults = {}
    defaults['ylabel'] = 'Untitled Y-Axis'
    defaults['xlabel'] = 'Time [UT]'
    defaults['title']  = 'Untitled Plot'

    self.metadata = dict(defaults.items() + metadata.items())

    self.raw = sigStruct(dtv, data, id=0, parent=self)
    self.active = self.raw

class sigStruct(sig):
  def __init__(self, dtv, data, id, parent=0, **metadata):
    self.parent = parent
    """Define a vtsd sigStruct object.

    :param dtv: datetime.datetime list
    :param data: raw data
    :param id: A serial number uniquely identifying this signal in the
    : processing chain.
    :param **metadata: keywords sent to matplot lib, etc.
    :returns: sig object
    """
    self.dtv      = dtv
    self.data     = data
    self.metadata = {}

    self.id = id

    for key in metadata:
      print "%s: %s" % (key, metadata[key])

    for key in metadata:
      self.metadata[key] = metadata[key]

  def plot(self):
    #from matplotlib import pyplot as mp

    #Metadata of "processed" signal overrides defaults.
    metadata = dict(self.parent.metadata.items() + self.metadata.items())

    fig = mp.figure()
    mp.plot(self.dtv,self.data)
    fig.autofmt_xdate()

    if 'dtStart' in metadata:
      mp.xlim(xmin=metadata['dtStart'])
    if 'dtEnd' in metadata:
      mp.xlim(xmax=metadata['dtEnd'])

    if 'xmin' in metadata:
      mp.xlim(xmin=metadata['xmin'])
    if 'xmax' in metadata:
      mp.xlim(xmax=metadata['xmax'])

    if 'ymin' in metadata:
      mp.ylim(ymin=metadata['ymin'])
    if 'ymax' in metadata:
      mp.ylim(ymax=metadata['ymax'])

    mp.xlabel(metadata['xlabel'])
    mp.ylabel(metadata['ylabel'])
    mp.title(metadata['title'])

class bandpass(object):
  def __init__(self,nsamp,f_c,sampRate,window='blackmanharris'):
    """Define a bandpass filter object

    :param nsamp: number of samples the filter will have
    :param f_c: Two-element list of cutoff frequencies
    :param sampRante: Sample rate of filter.  This should match the sample rate of the data being filtered.
    :param window: Type of window the filter should use.  See scipy.signal.firwin() for options.
    :returns: sig object
    """
    f_c = np.array(f_c)
    f_max = 1/(2.*sampRate)
    f_cn = f_c / f_max

    n = nsamp

    #Lowpass filter
    a = sp.signal.firwin(n, cutoff = f_cn[0], window = window)
    #Highpass filter with spectral inversion
    b = - sp.signal.firwin(n, cutoff = f_cn[1], window = window); b[n/2] = b[n/2] + 1
    #Combine into a bandpass filter
    d = - (a+b); d[n/2] = d[n/2] + 1
    
    self.f_c = f_c
    self.sampRate = sampRate
    self.window = window
    self.ir = d
  #These functions are modified from Matti Pastell's Page:
  # http://mpastell.com/2010/01/18/fir-with-scipy/

  #Plot frequency and phase response
  def plotTransferFunction(self,xmin=0,xmax=None,ymin_freq=-150,ymax_freq=5,ymin_phase=None,ymax_phase=None):
      """Plot the frequency and phase response of the filter object.

      :param xmin: Minimum value for x-axis.
      :param xmax: Maximum value for x-axis.
      :param ymin_freq: Minimum value for y-axis for the frequency response plot.
      :param ymax_freq: Maximum value for y-axis for the frequency response plot.
      :param ymin_phase: Minimum value for y-axis for the phase response plot.
      :param ymax_phase: Maximum value for y-axis for the phase response plot.
      """
      w,h = sp.signal.freqz(self.ir,1)
      h_dB = 20 * np.log10(abs(h))
      mp.subplot(211)
      w = w/max(w)
      if self.sampRate != 0:
          maxw = 1./(2.* self.sampRate)
          w = w * maxw
      mp.plot(w,h_dB)

      if xmin is not None: mp.xlim(xmin=xmin)
      if xmax is not None: mp.xlim(xmax=xmax)
      if ymin_freq is not None: mp.ylim(ymin=ymin_freq)
      if ymax_freq is not None: mp.ylim(ymax=ymax_freq)

      mp.ylabel('Magnitude (db)')

      if self.sampRate==0:
                      mp.xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
      else:
                      mp.xlabel(r'Frequency (Hz)')
      mp.title(r'Frequency response')
      mp.subplot(212)
      h_Phase = np.unwrap(np.arctan2(np.imag(h),np.real(h)))
      mp.plot(w,h_Phase)

      if xmin is not None: mp.xlim(xmin=xmin)
      if xmax is not None: mp.xlim(xmax=xmax)
      if ymin_phase is not None: mp.ylim(ymin=ymin_phase)
      if ymax_phase is not None: mp.ylim(ymax=ymax_phase)

      mp.ylabel('Phase (radians)')
      if self.sampRate==0:
                      mp.xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
      else:
                      mp.xlabel(r'Frequency (Hz)')
      mp.title(r'Phase response')
      mp.subplots_adjust(hspace=0.5)
      mp.show()

  #Plot step and impulse response
  def plotImpulseResponse(self,xmin=None,xmax=None,ymin_imp=None,ymax_imp=None,ymin_step=None,ymax_step=None):
      """Plot the frequency and phase response of the filter object.

      :param xmin: Minimum value for x-axis.
      :param xmax: Maximum value for x-axis.
      :param ymin_imp: Minimum value for y-axis for the impulse response plot.
      :param ymax_imp: Maximum value for y-axis for the impulse response plot.
      :param ymin_step: Minimum value for y-axis for the step response plot.
      :param ymax_step: Maximum value for y-axis for the step response plot.
      """
    #  def plotImpulseResponse(b,a=1):
      l = len(self.ir)
      impulse = np.repeat(0.,l); impulse[0] =1.
      x = np.arange(0,l)
      response = sp.signal.lfilter(self.ir,1,impulse)
      mp.subplot(211)
      mp.stem(x, response)
      mp.ylabel('Amplitude')
      mp.xlabel(r'n (samples)')
      mp.title(r'Impulse response')
      mp.subplot(212)

      step = np.cumsum(response)
      mp.stem(x, step)
      mp.ylabel('Amplitude')
      mp.xlabel(r'n (samples)')
      mp.title(r'Step response')
      mp.subplots_adjust(hspace=0.5)
      mp.show()

  def filter(self,vtsig,signal='active'):
      """Apply the filter to a vtsig object.

      :param vtsig: vtsig object
      :param xmax: Maximum value for x-axis.
      :param ymin_imp: Minimum value for y-axis for the impulse response plot.
      :param ymax_imp: Maximum value for y-axis for the impulse response plot.
      :param ymin_step: Minimum value for y-axis for the step response plot.
      :param ymax_step: Maximum value for y-axis for the step response plot.
      """
      
      sigobj = getattr(vtsig,signal)

      #Apply filter
      filt_data = sp.signal.lfilter(self.ir,[1.0],sigobj.data)

      #Make a new signal object based on the currently selected object.
      import copy 
      newsig = 'filtered'
#      vtsig.filtered = copy.copy(sigobj)

      setattr(vtsig,newsig,copy.deepcopy(sigobj))
      newsigobj = getattr(vtsig,newsig)

      #Put in the filtered data.
      newsigobj.data = copy.copy(filt_data)

      #Clear out ymin and ymax from metadata; make sure meta data block exists.
      #If not, create it.
      if hasattr(newsigobj,'metadata'):
        delMeta = ['ymin','ymax']
        for key in delMeta:
          if newsigobj.metadata.has_key(key):
            del newsigobj.metadata[key]
      else:
        newsigobj.metadata = {}

      key = 'title'
      if newsigobj.metadata.has_key(key):
        newsigobj.metadata[key] = ' '.join(['Filtered ',newsigobj.metadata[key]])
      elif vtsig.metadata.has_key(key):
        newsigobj.metadata[key] = ' '.join(['Filtered ',vtsig.metadata[key]])
      else:
        newsigobj.metadata[key] = 'Filtered'

      #newsigobj.metadata = 
      setattr(vtsig,'active',newsigobj)
