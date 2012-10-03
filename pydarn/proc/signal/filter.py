import copy 
import datetime

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
    defaults['fft_xlabel'] = 'Frequency [Hz]'
    defaults['fft_ylabel'] = 'Amplitude'

    self.metadata = dict(defaults.items() + metadata.items())
    self.raw = sigStruct(dtv, data, parent=self)
    self.active = self.raw

class sigStruct(sig):
  def __init__(self, dtv, data, comment='Raw Data', parent=0, **metadata):
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

    self.history = {datetime.datetime.now():comment}

    for key in metadata:
      print "%s: %s" % (key, metadata[key])

    for key in metadata:
      self.metadata[key] = metadata[key]

  def copy(self,newsig,comment):
    """Copy a vtsig object.  This deep copies data and metadata, updates the serial number, and logs a comment in the history.  Methods such as plot are kept as a reference.


    :param newsig: A string with the name for the new signal.
    :param comment: A string comment describing the new signal.
    :returns: sig object
    """
    setattr(self.parent,newsig,copy.copy(self))
    newsigobj = getattr(self.parent,newsig)

    newsigobj.dtv       = copy.deepcopy(self.dtv)
    newsigobj.data      = copy.deepcopy(self.data)
    newsigobj.metadata  = copy.deepcopy(self.metadata)
    newsigobj.history   = copy.deepcopy(self.history)

    newsigobj.history[datetime.datetime.now()] = comment
    
    return newsigobj

  def sampRate(self):
    """Calculate the sample rate parameters of a vt sigStruct signal.
    :returns: sampRate: sample rate of signal in seconds.  This is NAN if more than one unique timestep in sig.
    """
    diffs = np.unique(np.diff(self.dtv))

    if len(diffs) == 1:
      sampRate = diffs[0].seconds
    else:
      sampRate = np.NAN

    return sampRate

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

#Plot FFT of Some Signal
  def plotfft(self):

    sampRate = self.sampRate()
    assert sampRate != np.NAN, 'FFT requires a valid sample rate. Signal may not have a regularly spaced sampling rate.'
    nsamp = len(self.data)

    #Metadata of "processed" signal overrides defaults.
    metadata = dict(self.parent.metadata.items() + self.metadata.items())

#Nyquist Frequency
    f_max = 1/(2.*sampRate)

    freq_ax = np.arange(nsamp,dtype='f8')
    freq_ax = (freq_ax / max(freq_ax)) - 0.5
    freq_ax = freq_ax * 2. * f_max

    window  = np.hanning(nsamp)
    signal  = self.data*window

    sig_fft = sp.fftpack.fft(signal)
    sig_fft = sp.fftpack.fftshift(sig_fft)

    fig = mp.figure()
    ax = fig.add_subplot(111)

    ax.plot(freq_ax,abs(sig_fft))

    fftsuptitle = 'FFT Spectrum Magnitude'

    if metadata.has_key('title'): mp.title(metadata['title'])
    if metadata.has_key('fft_title'): mp.title(metadata['fft_title'])
    if metadata.has_key('fft_suptitle'): mp.suptitle(metadata['fft_suptitle'])
    else: mp.suptitle(fftsuptitle)
    if metadata.has_key('fft_xlabel'): mp.xlabel(metadata['fft_xlabel'])
    if metadata.has_key('fft_ylabel'): mp.ylabel(metadata['fft_ylabel'])

    if metadata.has_key('fft_xmin'): mp.xlim(xmin=metadata['fft_xmin'])
    else: mp.xlim(xmin=0)

    if metadata.has_key('fft_xmax'): mp.xlim(xmax=metadata['fft_xmax'])
    else: mp.xlim(xmax=f_max)

    if metadata.has_key('fft_ymin'): mp.ylim(ymin=metadata['fft_ymin'])
    if metadata.has_key('fft_ymax'): mp.ylim(ymax=metadata['fft_ymax'])

    mp.show()

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

    self.comment = ' '.join(['Filter:',window+',','sampRate:',str(sampRate),'Hz,','Cuttoffs:',str(f_c[0])+',', str(f_c[1]),'Hz'])
    self.ir = d
  #These functions are modified from Matti Pastell's Page:
  # http://mpastell.com/2010/01/18/fir-with-scipy/

  #Plot frequency and phase response

  def __str__(self):
    return self.comment

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

      newsig = 'filtered'
      newsigobj = sigobj.copy(newsig,self.comment)
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
