import copy 
import datetime

from matplotlib import pyplot as mp
import numpy as np
import scipy as sp

# Create a system for handling metadata that applies to all signals. ###########
glob = {}
def globalMetaData():
  """Return the glob (global metadata) dictionary.
  """
  return glob

def globalMetaData_add(**metadata):
  """Add an item to the glob (global metadata) dictionary.
  :**metadata : keywords and values to be added to the glob dictionary.
  """
  global glob
  glob = dict(glob.items() + metadata.items())

def globalMetaData_del(keys):
  """Delete an item from the glob (global metadata) dictionary.
  :param keys: List of keys to be deleted.
  """
  global glob
  for key in keys:
    if glob.has_key(key): del glob[key]

def globalMetaData_clear():
  """Clear the glob (global metadata) dictionary.
  """
  global glob
  glob.clear()

# Signal Objects Start Here ####################################################
class sig(object):
  def __init__(self, dtv, data, comment='Signal Object Created', **metadata):
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
    self.raw = sigStruct(dtv, data, comment=comment, parent=self)
    self.active = self.raw

  def plot(self):
    """Plots the currently active signal.
    """
    self.active.plot()

  def plotfft(self,**metadata):
    """Plots the spectrum of the currently active signal.
    """
    self.active.plotfft(**metadata)

class sigStruct(sig):
  def __init__(self, dtv, data, comment=None, parent=0, **metadata):
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
        testsig = '_'.join([newsig,'%03d' % xx])
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
    self.diffs = diffs

    if len(diffs) == 1:
      sampRate = diffs[0].total_seconds()
    else:
      maxDt = np.max(diffs) - np.min(diffs)
      maxDt = maxDt.total_seconds()
      avg = np.sum(diffs)/len(diffs)
      avg = avg.total_seconds()
      md  = self.getAllMetaData()
      warn = 'WARNING'
      if md.has_key('title'): warn = ' '.join([warn,'FOR','"'+md['title']+'"'])
      print warn + ':'
      print '   Date time vector is not regularly sampled!'
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
    return dict(globalMetaData().items() + self.parent.metadata.items() + self.metadata.items())

  def setMetaData(self,**metadata):
    self.metadata = dict(self.metadata.items() + metadata.items())

  def truncate(self):
    """Trim the ends of the current signal to match the valid time and sets the truncated signal to active.
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
    md = self.getAllMetaData()

    if md.has_key('lineStyle'): lineStyle=md['lineStyle']
    else: lineStyle = '-'
    fig = mp.figure()
    mp.plot(self.dtv,self.data,lineStyle)
    fig.autofmt_xdate()

    if 'xmin' in md:
      mp.xlim(xmin=md['xmin'])
    if 'xmax' in md:
      mp.xlim(xmax=md['xmax'])

    if 'ymin' in md:
      mp.ylim(ymin=md['ymin'])
    if 'ymax' in md:
      mp.ylim(ymax=md['ymax'])

    if md.has_key('validTimes'):
      grey = '0.75'
      mp.axvspan(self.dtv[0],md['validTimes'][0],color=grey)
      mp.axvspan(md['validTimes'][1],self.dtv[-1],color=grey)
      mp.axvline(x=md['validTimes'][0],color='g',ls='--',lw=2)
      mp.axvline(x=md['validTimes'][1],color='g',ls='--',lw=2)

    mp.xlabel(md['xlabel'])
    mp.ylabel(md['ylabel'])
    mp.title(md['title'])

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
      return [self.dtv[0],self.dtv[-1]]
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
  def plotfft(self,**metadata):
    """Plots the FFT spectral magnitude for the signal.
    """

    self.fft()
    freq_ax = self.freqVec
    sig_fft = self.spectrum

    self.setMetaData(**metadata)
    #Metadata of "processed" signal overrides defaults.
    md = self.getAllMetaData()

    fig = mp.figure()
    ax = fig.add_subplot(111)

    if md.has_key('fft_lineStyle'): lineStyle=md['fft_lineStyle']
    else: lineStyle = '-'
    ax.plot(freq_ax,abs(sig_fft),lineStyle)

    if md.has_key('title'): mp.title(md['title'])
    if md.has_key('fft_title'): mp.title(md['fft_title'])

    if md.has_key('fft_xlabel'): mp.xlabel(md['fft_xlabel'])
    if md.has_key('fft_ylabel'): mp.ylabel(md['fft_ylabel'])

    if md.has_key('fft_xmin'): mp.xlim(xmin=md['fft_xmin'])
    else: mp.xlim(xmin=0)

    if md.has_key('fft_xmax'): mp.xlim(xmax=md['fft_xmax'])

    if md.has_key('fft_ymin'): mp.ylim(ymin=md['fft_ymin'])
    if md.has_key('fft_ymax'): mp.ylim(ymax=md['fft_ymax'])

    
    #Print the time window of the FFT on the side of the plot.
    valid = self.getFftTimes()
    s = ' - '.join([x.strftime('%Y%b%d %H:%M UT').upper() for x in valid])
    mp.annotate(s, xy=(1.01, 0.95), xycoords="axes fraction",rotation=90)

    mp.show()
