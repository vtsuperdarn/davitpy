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
    defaults['fft_ylabel'] = 'FFT Spectrum Magnitude'

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
    self.dtv      = np.array(dtv)
    self.data     = np.array(data)
    self.metadata = {}
    for key in metadata: self.metadata[key] = metadata[key]

    self.history = {datetime.datetime.now():comment}


  def copy(self,newsig,comment):
    """Copy a vtsig object.  This deep copies data and metadata, updates the serial number, and logs a comment in the history.  Methods such as plot are kept as a reference.
    :param newsig: A string with the name for the new signal.
    :param comment: A string comment describing the new signal.
    :returns: sig object
    """
    
    if hasattr(self.parent,newsig):
      xx = 0
      ok = False
      while ok is False:
        xx += 1
        testsig = '-'.join([newsig,'%03d' % xx])
        if hasattr(self.parent,testsig) == False:
          newsig = testsig
          ok = True

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

  def preFftSampRate(self):
    """Calculate the sample rate parameters of a vt sigStruct signal for the period in which the FFT is valid.
    :param validTimes: Two-element list of datetime.datetime.  The sample rate is calculated between these times.
    :returns: sampRate: sample rate of signal in seconds.  This is NAN if more than one unique timestep in sig.
    """
    diffs = np.unique(np.diff(self.preFftDtv))

    if len(diffs) == 1:
      sampRate = diffs[0].seconds
    else:
      maxDt = np.max(diffs) - np.min(diffs)
      maxDt = maxDt.seconds + (maxDt.microseconds / 1000000.)
      avg = np.sum(diffs)/len(diffs)
      avg = avg.seconds + (avg.microseconds / 1000000.)
      print 'WARNING: Date time vector is not regularly sampled!'
      print '   Maximum difference in sampling rates is ' + str(maxDt) + ' sec.'
      print '   Using average sampling rate of ' + str(avg) + ' sec.'
      sampRate = avg

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

  def truncate(self):
    """Trim the ends of the current signal to match the valid time.
    """
   
    #Don't do anything if the whole thing is valid.
    valid = self.getValidTimes()

    if valid == None:
      return self
    elif (valid[0] <= self.dtv[0]) & (valid[1] >= self.dtv[1]):
      return self

    comment = ' - '.join([x.strftime('%Y%b%d %H:%M UT').upper() for x in valid])
    comment = 'Truncate: ' + comment
    newsig = self.copy('truncate',comment)

    inx = self.getValidInx()
    newsig.dtv = newsig.dtv[inx]
    newsig.data = newsig.data[inx]
    newsig.updateValidTimes([newsig.dtv[0], newsig.dtv[-1]])
    
    #Remove old time limits.
    if newsig.metadata.has_key('xmin'):
      if newsig.metadata['xmin'] <= newsig.dtv[0]: del newsig.metadata['xmin']

    if newsig.metadata.has_key('xmax'):
      if newsig.metadata['xmax'] >= newsig.dtv[-1]: del newsig.metadata['xmax']
    
    newsig.setActive()
    return newsig

  def plot(self):
    #from matplotlib import pyplot as mp

    #Metadata of "processed" signal overrides defaults.
    metadata = self.getAllMetaData()

    fig = mp.figure()
    mp.plot(self.dtv,self.data)
    fig.autofmt_xdate()

    if 'xmin' in metadata:
      mp.xlim(xmin=metadata['xmin'])
    if 'xmax' in metadata:
      mp.xlim(xmax=metadata['xmax'])

    if 'ymin' in metadata:
      mp.ylim(ymin=metadata['ymin'])
    if 'ymax' in metadata:
      mp.ylim(ymax=metadata['ymax'])

    if metadata.has_key('validTimes'):
      grey = '0.75'
      mp.axvspan(self.dtv[0],metadata['validTimes'][0],color=grey)
      mp.axvspan(metadata['validTimes'][1],self.dtv[-1],color=grey)
      mp.axvline(x=metadata['validTimes'][0],color='g',ls='--',lw=2)
      mp.axvline(x=metadata['validTimes'][1],color='g',ls='--',lw=2)

    mp.xlabel(metadata['xlabel'])
    mp.ylabel(metadata['ylabel'])
    mp.title(metadata['title'])

  def getFftTimes(self):
    """Returns the time window for which to calculate the FFT times for a given signal.
    This will look in the for the signal's metadata object and return the most restrictive 
    range of metadata['validTimes'] and metadata['fftTimes'] ranges.
    :returns : None or 2-element list of datetime.dateime where the FFT should be taken.
    """
    md = self.getAllMetaData()
    start = []
    end = []

    keys = ['validTimes','fftTimes']
    for kk in keys:
      if md.has_key(kk):
        start.append(md[kk][0])
        end.append(md[kk][1])
    
    start.sort(reverse=True)
    end.sort()

    if start == []:
      return None
    else:
      return [start[0],end[0]]

  def getFftInx(self):
    """Returns indices of the signal for the time range over which the FFT is going to be taken.
    Uses time range from getFftTimes().
    :returns inx: list of indices of the signal for the time range over which the FFT is going to be taken.
    """

    valid = self.getFftTimes()
    if valid == None:
      inx = range(len(self.dtv)) 
    else:
      inx  = np.where((self.dtv >= valid[0]) & (self.dtv <= valid[1]))

    return inx

  def getValidTimes(self):
    """Returns the time window for which the signal is valid.
    This will look in the for the signal's metadata object and return the 
    range of metadata['validTimes'].
    :returns : None or 2-element list of datetime.dateime.
    """

    md = self.getAllMetaData()
    if md.has_key('validTimes'):
      valid = md['validTimes']
    else:
      valid = None

    return valid

  def getValidInx(self):
    """Returns indices of the signal for the time range over which the signal is valid.
    Uses time range from getValidTimes().
    :returns inx: list of indices of the signal for the time range over which the signal is valid.
    """

    valid = self.getValidTimes()
    if valid == None:
      inx = range(len(self.dtv)) 
    else:
      inx  = np.where((self.dtv >= valid[0]) & (self.dtv <= valid[1]))

    return inx

  def fft(self):
    """Calculates the FFT spectral magnitude for the signal.
    """

    valid = self.getFftTimes()
    inx =  self.getFftInx() 
    dtv  = self.dtv[inx]
    data = self.data[inx]

    self.preFftDtv = dtv
    self.preFftData = data

    sampRate = self.preFftSampRate()
    assert sampRate != np.NAN, 'FFT requires a valid sample rate. Signal may not have a regularly spaced sampling rate.'
    nsamp = len(data)

#Nyquist Frequency
    f_max = 1/(2.*sampRate)

    freq_ax = np.arange(nsamp,dtype='f8')
    freq_ax = (freq_ax / max(freq_ax)) - 0.5
    freq_ax = freq_ax * 2. * f_max

    window  = np.hanning(nsamp)
    signal  = data*window

    sig_fft = sp.fftpack.fft(signal)
    sig_fft = sp.fftpack.fftshift(sig_fft)

    self.fftTimes = valid
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

    if metadata.has_key('title'): mp.title(metadata['title'])
    if metadata.has_key('fft_title'): mp.title(metadata['fft_title'])

    if metadata.has_key('fft_xlabel'): mp.xlabel(metadata['fft_xlabel'])
    if metadata.has_key('fft_ylabel'): mp.ylabel(metadata['fft_ylabel'])

    if metadata.has_key('fft_xmin'): mp.xlim(xmin=metadata['fft_xmin'])
    else: mp.xlim(xmin=0)

    if metadata.has_key('fft_xmax'): mp.xlim(xmax=metadata['fft_xmax'])

    if metadata.has_key('fft_ymin'): mp.ylim(ymin=metadata['fft_ymin'])
    if metadata.has_key('fft_ymax'): mp.ylim(ymax=metadata['fft_ymax'])

    
    valid = self.getFftTimes()
    s = ' - '.join([x.strftime('%Y%b%d %H:%M UT').upper() for x in valid])

    mp.annotate(s, xy=(1.01, 0.95), xycoords="axes fraction",rotation=90)

    #    print s

    mp.show()
