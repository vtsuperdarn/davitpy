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

  def plot(self):
    """Plots the currently active signal.
    """
    self.active.plot()

  def plotfft(self):
    """Plots the spectrum of the currently active signal.
    """
    self.active.plotfft()

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
    for key in metadata: self.metadata[key] = metadata[key]

    self.history = {datetime.datetime.now():comment}


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

  def setActive(self):
    """Sets this signal as the currently active signal.
    """
    self.parent.active = self

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

  def updateValidTimes(self,times):
    """Update the metadata block times that a signal is valid for.
    :param: times: List of times between which the signal is valid.
    """
    if self.metadata.has_key('validTimes'):
      if self.metadata['validTimes'][0] < times[0]: self.metadata['validTimes'][0] = times[0]
      if self.metadata['validTimes'][1] > times[1]: self.metadata['validTimes'][1] = times[1]
    else:
      self.metadata['validTimes'] = times

  def getAllMetaData(self):
    return dict(self.parent.metadata.items() + self.metadata.items())

  def plot(self):
    #from matplotlib import pyplot as mp

    #Metadata of "processed" signal overrides defaults.
    metadata = self.getAllMetaData()

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

    if self.metadata.has_key('validTimes'):
      grey = '0.75'
      mp.axvspan(self.dtv[0],self.metadata['validTimes'][0],color=grey)
      mp.axvspan(self.metadata['validTimes'][1],self.dtv[-1],color=grey)
      mp.axvline(x=self.metadata['validTimes'][0],color='g',ls='--',lw=2)
      mp.axvline(x=self.metadata['validTimes'][1],color='g',ls='--',lw=2)

    mp.xlabel(metadata['xlabel'])
    mp.ylabel(metadata['ylabel'])
    mp.title(metadata['title'])

  def fft(self):
    """Calculates the FFT spectral magnitude for the signal.
    """
    sampRate = self.sampRate()
    assert sampRate != np.NAN, 'FFT requires a valid sample rate. Signal may not have a regularly spaced sampling rate.'
    nsamp = len(self.data)

#Nyquist Frequency
    f_max = 1/(2.*sampRate)

    freq_ax = np.arange(nsamp,dtype='f8')
    freq_ax = (freq_ax / max(freq_ax)) - 0.5
    freq_ax = freq_ax * 2. * f_max

    window  = np.hanning(nsamp)
    signal  = self.data*window

    sig_fft = sp.fftpack.fft(signal)
    sig_fft = sp.fftpack.fftshift(sig_fft)

    self.freqVec  = freq_ax
    self.spectrum = sig_fft

#Plot FFT of Some Signal
  def plotfft(self):
    """Plots the FFT spectral magnitude for the signal.
    """

    self.fft()
    freq_ax = self.freqVec
    sig_fft = self.spectrum

    #Metadata of "processed" signal overrides defaults.
    metadata = dict(self.parent.metadata.items() + self.metadata.items())

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
