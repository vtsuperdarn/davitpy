import copy 
import datetime

from matplotlib import pyplot as mp
import numpy as np
import scipy as sp

def detrend(vtsig,signal='active'):
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
    detrend_data = sp.signal.detrend(sigobj.data)

    #Create new signal object.
    newsigobj = sigobj.copy('detrended','Linear detrend (scipy.signal.detrend)')
    #Put in the filtered data.
    newsigobj.data = copy.copy(detrend_data)

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
      newsigobj.metadata[key] = ' '.join(['Detrended ',newsigobj.metadata[key]])
    elif vtsig.metadata.has_key(key):
      newsigobj.metadata[key] = ' '.join(['Detrended ',vtsig.metadata[key]])
    else:
      newsigobj.metadata[key] = 'Detrended'

    #newsigobj.metadata = 
    setattr(vtsig,'active',newsigobj)


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

    self.comment = ' '.join(['Filter:',window+',','sampRate:',str(sampRate),'sec,','Cuttoffs:',str(f_c[0])+',', str(f_c[1]),'Hz'])
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

#Filter causes a delay in the signal and also doesn't get the tail end of the signal...  Shift signal around, provide info about where the signal is valid.
      shift = np.int32(-np.floor(len(self.ir)/2.))

      start_line = np.zeros(len(filt_data))
      start_line[0] = 1

      filt_data  = np.roll(filt_data,shift)
      start_line = np.roll(start_line,shift)
      
      tinx0 = abs(shift)
      tinx1 = np.where(start_line == 1)[0][0]

      val_tm0 = sigobj.dtv[tinx0]
      val_tm1 = sigobj.dtv[tinx1]

      #Create new signal object.
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

      newsigobj.updateValidTimes([val_tm0,val_tm1])

      key = 'title'
      if newsigobj.metadata.has_key(key):
        newsigobj.metadata[key] = ' '.join(['Filtered ',newsigobj.metadata[key]])
      elif vtsig.metadata.has_key(key):
        newsigobj.metadata[key] = ' '.join(['Filtered ',vtsig.metadata[key]])
      else:
        newsigobj.metadata[key] = 'Filtered'

      #newsigobj.metadata = 
      setattr(vtsig,'active',newsigobj)
