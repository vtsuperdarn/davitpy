class attrdict(dict):
  def __getattr__(self, attr):
    return self[attr]
  def __setattr__(self, attr, value):
    self[attr] = value

class sig(object):
  def __init__(self, dtv, data, **metadata):
    """Define a vtsd sig object.

    :param dtv: datetime.datetime list
    :param data: raw data
    :param ylabel: Y-Label String for data
    :returns: sig object
    """
    defaults = attrdict({})
    defaults.ylabel = 'Untitled Y-Axis'
    defaults.xlabel = 'Time [UT]'
    defaults.title  = 'Untitled Plot'

    self.metadata = attrdict(defaults.items() + metadata.items())
    self.items = metadata.items()

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
    self.metadata = attrdict({})

    self.id = id

    for key in metadata:
      print "%s: %s" % (key, metadata[key])

    for key in metadata:
      self.metadata[key] = metadata[key]

  def plot(self):
    from matplotlib import pyplot as mp

    #Metadata of "processed" signal overrides defaults.
    metadata = attrdict(self.parent.metadata.items() + self.metadata.items())

    fig = mp.figure()
    mp.plot(self.dtv,self.data)
    fig.autofmt_xdate()

    if 'dtStart' in metadata:
      mp.xlim(xmin=metadata.dtStart)
    if 'dtEnd' in metadata:
      mp.xlim(xmax=metadata.dtEnd)

    if 'xmin' in metadata:
      mp.xlim(xmin=metadata.xmin)
    if 'xmax' in metadata:
      mp.xlim(xmax=metadata.xmax)

    if 'ymin' in metadata:
      mp.ylim(ymin=metadata.ymin)
    if 'ymax' in metadata:
      mp.ylim(ymax=metadata.ymax)

    mp.xlabel(metadata.xlabel)
    mp.ylabel(metadata.ylabel)
    mp.title(metadata.title)

class filter(object):
  #Highpass FIR Filter
  def hp(nsamp,f_c,sampRate):
      f_c = f_c[0]
      #Nyquist Frequency
      f_max = 1/(2.*sampRate)
      f_cn = f_c / f_max

      a = sp.signal.firwin(nsamp,cutoff = f_cn,window="hamming")

      #Spectral Inversion
      a = -a
      a[nsamp/2] = a[nsamp/2] + 1
      return a
  #These functions are modified from Matti Pastell's Page:
  # http://mpastell.com/2010/01/18/fir-with-scipy/

  #Plot frequency and phase response
  def mfreqz(b,a=1,sampRate=0,xmin=0,xmax=0):
      w,h = sp.signal.freqz(b,a)
      h_dB = 20 * np.log10 (abs(h))
      pyplot.subplot(211)
      w = w/max(w)
      if sampRate != 0:
          maxw = 1./(2.* sampRate)
          w = w * maxw
      pyplot.plot(w,h_dB)
      pyplot.ylim(-150, 5)

      if xmax==0: xmax = max(w)

      pyplot.xlim(xmin,xmax)

      pyplot.ylabel('Magnitude (db)')

      if sampRate==0:
                      pyplot.xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
      else:
                      pyplot.xlabel(r'Frequency (Hz)')
      pyplot.title(r'Frequency response')
      pyplot.subplot(212)
      h_Phase = np.unwrap(np.arctan2(np.imag(h),np.real(h)))
      pyplot.plot(w,h_Phase)
      pyplot.xlim(xmin,xmax)
      pyplot.ylabel('Phase (radians)')
      if sampRate==0:
                      pyplot.xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
      else:
                      pyplot.xlabel(r'Frequency (Hz)')
      pyplot.title(r'Phase response')
      pyplot.subplots_adjust(hspace=0.5)
      pyplot.show()

  #Plot step and impulse response
  def impz(b,a=1):
      l = len(b)
      impulse = np.repeat(0.,l); impulse[0] =1.
      x = np.arange(0,l)
      response = sp.signal.lfilter(b,a,impulse)
      pyplot.subplot(211)
      pyplot.stem(x, response)
      pyplot.ylabel('Amplitude')
      pyplot.xlabel(r'n (samples)')
      pyplot.title(r'Impulse response')
      pyplot.subplot(212)
      step = np.cumsum(response)
      pyplot.stem(x, step)
      pyplot.ylabel('Amplitude')
      pyplot.xlabel(r'n (samples)')
      pyplot.title(r'Step response')
      pyplot.subplots_adjust(hspace=0.5)
