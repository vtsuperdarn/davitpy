# -*- coding: utf-8 -*-
import copy
import datetime
from matplotlib import pyplot as mp
import numpy as np
import scipy as sp
import scipy.signal
from signalCommon import *
import logging


def dtvToSeconds(dtv, start=None):
    """Convert a datetime.datetime iterable to a numpy array of seconds from start.

    Parameters
    ---------
    dtv : list
        datetime.datetime iterable to convert.
    start : Optional[datatime.datetime]
        If None, then start = dtv[0].

    Returns
    -------
    sec : numpy.array
        numpy.array of seconds from dtv[0].

    """
    if start is None:
        start = dtv[0]
    npDtv = np.array(dtv)
    timeDelta = npDtv - start
    sec = np.array([x.total_seconds() for x in timeDelta])
    return sec


def interpolate(vtsig, start=None, stop=None, samplePeriod=None,
                newSigName='interpolated'):
    """Interpolates signal onto a regular grid.

    Parameters
    ---------
    vtsig : VT sig/sigStruct object
        VT sig/sigStruct object to be interpolated. If not set,
        vtsig.getValidTimes()[0] is used.
    start : Optional[datatime.datetime]
        datetime.datetime to start the new grid.
    stop : Optional[datatime.datetime]
        datetime.datetime to end the new grid.
        If not set, vtsig.getValidTimes()[1] is used.
    samplePeriod : Optional[float]
        Time resolution of the new grid in seconds.
        If not set, 0.1*vtsig.samplePeriod() is used.
    newSigName : Optional[str]
        String name of the attribute of the newly created signal.

    """
    sigobj = prepForProc(vtsig)
    valid = sigobj.getValidTimes()
    if start is None:
        start = valid[0]
    if stop is None:
        stop = valid[1]
    if samplePeriod is None:
        samplePeriod = 0.1 * sigobj.getSamplePeriod()

    # Create new date time vector.
    dt = datetime.timedelta(0, samplePeriod)
    ndt = np.int(np.ceil((stop - start).total_seconds() / dt.total_seconds()))
    dtv = [start + dt * xx for xx in range(ndt)]
    newDtv = np.array(dtv)

    # Convert sigobj.dtv to seconds from newDtv[0].
    start = newDtv[0]
    oldsec = dtvToSeconds(sigobj.dtv, start=start)
    f = sp.interpolate.interp1d(oldsec, sigobj.data)

    # Convert newDtv to seconds from newDtv[0].
    newsec = dtvToSeconds(newDtv)
    newsig = f(newsec)

    sampPeriod = sigobj.samplePeriod(dtv=newDtv)
    nyq = sigobj.nyquistFrequency(dtv=newDtv)
    comment = 'Interpolate: [' + str(newDtv[0]) + ' to ' + str(
        newDtv[-1]) + '] dt=' + str(sampPeriod) + ' s, Nyq=' + str(nyq) + ' Hz'

    sigobj.makeNewSignal(
        newSigName, newDtv, newsig, comment, appendTitle='Interpolated')


def commonDtv(siglist):
    """Takes a list of vt sig/sigStruct objects and interpolates them all to
    a common datetime.datetime grid. The most restrictive range of validtimes
    and the highest time resolution is used.

    Parameters
    ---------
    siglist: list
        list of vt sig/sigStruct objects

    """
    sl = []
    start = []
    stop = []
    dt = []

    # Find out the properties of each of the signals, put them into lists.
    for sig in siglist:
        s = prepForProc(sig)
        sl.append(s)

        dt.append(s.samplePeriod())

        rang = s.getValidTimes()
        start.append(rang[0])
        stop.append(rang[1])

    # Sort the lists appropriately.
    dt.sort()
    start.sort(reverse=True)
    stop.sort()

    for sig in sl:
        interpolate(sig, start[0], stop[0], 0.1 * dt[0], 'common')


def detrend(vtsig):
    """Linearly detrend a vtsig object.

    Parameters
    ---------
    vtsig : vtsig object

    """
    sigobj = prepForProc(vtsig)
    vtsig = sigobj.parent

    # Detrend data
    detrend_data = sp.signal.detrend(sigobj.data)

    # Create new signal object.
    newsigobj = sigobj.copy(
        'detrended', 'Linear detrend (scipy.signal.detrend)')
    newsigobj.data = copy.copy(detrend_data)

    # Clear out ymin and ymax from metadata; make sure meta data block exists.
    # If not, create it.
    if hasattr(newsigobj, 'metadata'):
        delMeta = ['ymin', 'ymax']
        for key in delMeta:
            if newsigobj.metadata.has_key(key):
                del newsigobj.metadata[key]
    else:
        newsigobj.metadata = {}

    key = 'title'
    if newsigobj.metadata.has_key(key):
        newsigobj.metadata[key] = ' '.join(
            ['Detrended ', newsigobj.metadata[key]])
    elif vtsig.metadata.has_key(key):
        newsigobj.metadata[key] = ' '.join(['Detrended ', vtsig.metadata[key]])
    else:
        newsigobj.metadata[key] = 'Detrended'

    setattr(vtsig, 'active', newsigobj)


class filter(object):

    def __init__(self, vtsig, numtaps=None, cutoff_low=None, cutoff_high=None,
                 width=None, window='blackman', pass_zero=True, scale=True,
                 newSigName='filtered'):
        """Filter a VT sig/sigStruct object and define a FIR filter object.
        If only cutoff_low is defined, this is a high pass filter.
        If only cutoff_high is defined, this is a low pass filter. If both
        cutoff_low and cutoff_high is defined, this is a band pass filter.

        Uses scipy.signal.firwin()
        High pass and band pass filters inspired by Matti Pastell's page:
            http://mpastell.com/2010/01/18/fir-with-scipy/

        Metadata keys
            'filter_cutoff_low' --> cutoff_low
            'filter_cutoff_high' --> cutoff_high
            'filter_cutoff_numtaps' --> cutoff_numtaps

        Parameters
        ----------
        vtsig : vtsig object
        numtaps : Optional[int]
            Length of the filter (number of coefficients, i.e. the filter
            order + 1).  `numtaps` must be even if a passband includes the
            Nyquist frequency.
        cutoff_low : Optional[float or 1D array_like]
            High pass cutoff frequency of filter (expressed in the same units
            as `nyq`) OR an array of cutoff frequencies (that is, band edges).
            In the latter case, the frequencies in `cutoff` should be positive
            and monotonically increasing between 0 and `nyq`.  The values 0 and
            `nyq` must not be included in `cutoff`.
        cutoff_high : Optional[float or 1D array_like]
            Like cutoff_low, but this is the low pass cutoff frequency of
            the filter.
        width : Optional[float or None]
            If `width` is not None, then assume it is the approximate width
            of the transition region (expressed in the same units as `nyq`)
            for use in Kaiser FIR filter design.  In this case, the `window`
            argument is ignored.
        window : Optional[string or tuple of string and parameter values]
            Desired window to use. See `scipy.signal.get_window` for a list
            of windows and required parameters.
        pass_zero : Optional[bool]
            If True, the gain at the frequency 0 (i.e. the "DC gain") is 1.
            Otherwise the DC gain is 0.
        scale : Optional[bool]
            Set to True to scale the coefficients so that the frequency
            response is exactly unity at a certain frequency.
            That frequency is either:
                0 (DC) if the first passband starts at 0 (i.e. pass_zero is
                True); `nyq` (the Nyquist rate) if the first passband ends at
                `nyq` (i.e the filter is a single band highpass filter);
                center of first passband otherwise.
        newSigName : Optional[str]

        Attributes
        ----------
        comment : str
        nyq : float
            Nyquist frequency.  Each frequency in `cutoff` must be between 0
            and `nyq`.
        ir

        Returns
        -------
        filter object

        """
        sigObj = prepForProc(vtsig)
        nyq = sigObj.nyquistFrequency()

        # Get metadata for cutoffs and numtaps.
        md = sigObj.getAllMetaData()
        if cutoff_high is None:
            if md.has_key('filter_cutoff_high'):
                cutoff_high = md['filter_cutoff_high']

        if cutoff_low is None:
            if md.has_key('filter_cutoff_low'):
                cutoff_low = md['filter_cutoff_low']

        if numtaps is None:
            if md.has_key('filter_numtaps'):
                numtaps = md['filter_numtaps']
            else:
                logging.warning('WARNING: You must provide numtaps.')
                return

        if cutoff_high is not None:  # Low pass
            lp = sp.signal.firwin(numtaps=numtaps, cutoff=cutoff_high,
                                  width=width, window=window,
                                  pass_zero=pass_zero, scale=scale, nyq=nyq)
            d = lp

        if cutoff_low is not None:  # High pass
            hp = -sp.signal.firwin(numtaps=numtaps, cutoff=cutoff_low,
                                   width=width, window=window,
                                   pass_zero=pass_zero, scale=scale, nyq=nyq)
            hp[numtaps / 2] = hp[numtaps / 2] + 1
            d = hp

        if (cutoff_high is not None) and (cutoff_low is not None):
            d = -(lp + hp)
            d[numtaps / 2] = d[numtaps / 2] + 1

        if cutoff_high is None and cutoff_low is None:
            logging.warning("WARNING!! You must define cutoff frequencies!")
            return

        self.comment = ' '.join(['Filter:', window +
                                 ',', 'Nyquist:', str(nyq),
                                 'Hz,', 'Cuttoff:', '[' + str(cutoff_low) +
                                 ', ' + str(cutoff_high) + ']', 'Hz'])
        self.nyq = nyq
        self.ir = d

        self.filter(sigObj, newSigName=newSigName)

    def __str__(self):
        return self.comment

    def plotTransferFunction(self, xmin=0, xmax=None, ymin_mag=-150,
                             ymax_mag=5, ymin_phase=None, ymax_phase=None,
                             worN=None):
        """Plot the frequency and phase response of the filter object.

        Parameters
        ----------
        xmin : Optional[int or float]
            Minimum value for x-axis.
        xmax : Optional[int or float]
            Maximum value for x-axis.
        ymin_mag : Optional[int or float]
            Minimum value for y-axis for the frequency response plot.
        ymax_mag : Optional[int or float]
            Maximum value for y-axis for the frequency response plot.
        ymin_phase : Optional[int or float]
            Minimum value for y-axis for the phase response plot.
        ymax_phase : Optional[int or float]
            Maximum value for y-axis for the phase response plot.
        worN : Optional[None or int]
            passed to scipy.signal.freqz()
            If None, then compute at 512 frequencies around the unit circle.
            If the len(filter) > 512, then compute at len(filter) frequencie
            s around the unit circle.
            If a single integer, the compute at that many frequencies.
            Otherwise, compute the response at frequencies given in worN

        """
        if worN is None:
            if len(self.ir) > 512:
                worN = len(self.ir)
            else:
                worN = None
        else:
            pass

        w, h = sp.signal.freqz(self.ir, 1, worN=worN)
        h_dB = 20 * np.log10(abs(h))
        mp.subplot(211)

        # Compute frequency vector.
        w = w / max(w) * self.nyq
        mp.plot(w, h_dB, '.-')
        # mp.axvline(x=self.fMax,color='r',ls='--',lw=2)

        if xmin is not None:
            mp.xlim(xmin=xmin)
        if xmax is not None:
            mp.xlim(xmax=xmax)
        if ymin_mag is not None:
            mp.ylim(ymin=ymin_mag)
        if ymax_mag is not None:
            mp.ylim(ymax=ymax_mag)

        mp.ylabel('Magnitude (db)')
        mp.xlabel(r'Frequency (Hz)')

        mp.title(r'Frequency response')
        mp.subplot(212)
        h_Phase = np.unwrap(np.arctan2(np.imag(h), np.real(h)))
        mp.plot(w, h_Phase, '.-')

        if xmin is not None:
            mp.xlim(xmin=xmin)
        if xmax is not None:
            mp.xlim(xmax=xmax)
        if ymin_phase is not None:
            mp.ylim(ymin=ymin_phase)
        if ymax_phase is not None:
            mp.ylim(ymax=ymax_phase)

        mp.ylabel('Phase (radians)')
        mp.xlabel(r'Frequency (Hz)')
        mp.title(r'Phase response')
        mp.subplots_adjust(hspace=0.5)
        mp.show()

    # Plot step and impulse response
    def plotImpulseResponse(self, xmin=None, xmax=None, ymin_imp=None,
                            ymax_imp=None, ymin_step=None, ymax_step=None):
        """Plot the frequency and phase response of the filter object.

        Parameters
        ----------
        xmin : Optional[int or float]
            Minimum value for x-axis.
        xmax : Optional[int or float]
            Maximum value for x-axis.
        ymin_imp : Optional[int or float]
            Minimum value for y-axis for the impulse response plot.
        ymax_imp : Optional[int or float]
            Maximum value for y-axis for the impulse response plot.
        ymin_step : Optional[int or float]
            Minimum value for y-axis for the step response plot.
        ymax_step : Optional[int or float]
            Maximum value for y-axis for the step response plot.

        """
        #  def plotImpulseResponse(b,a=1):
        l = len(self.ir)
        impulse = np.repeat(0., l)
        impulse[0] = 1.
        x = np.arange(0, l)
        response = sp.signal.lfilter(self.ir, 1, impulse)
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

    def filter(self, vtsig, newSigName='filtered'):
        """Apply the filter to a vtsig object.

        Parameters
        ----------
        vtsig: vtsig object
        newSigName : Optional[str]

        """
        sigobj = prepForProc(vtsig)
        vtsig = sigobj.parent

        # Apply filter
        filt_data = sp.signal.lfilter(self.ir, [1.0], sigobj.data)

# Filter causes a delay in the signal and also doesn't get the tail end of
# the signal...  Shift signal around, provide info about where the signal
# is valid.
        shift = np.int32(-np.floor(len(self.ir) / 2.))

        start_line = np.zeros(len(filt_data))
        start_line[0] = 1

        filt_data = np.roll(filt_data, shift)
        start_line = np.roll(start_line, shift)

        tinx0 = abs(shift)
        tinx1 = np.where(start_line == 1)[0][0]

        val_tm0 = sigobj.dtv[tinx0]
        val_tm1 = sigobj.dtv[tinx1]

        # Create new signal object.
        newsigobj = sigobj.copy(newSigName, self.comment)
        # Put in the filtered data.
        newsigobj.data = copy.copy(filt_data)
        newsigobj.dtv = copy.copy(sigobj.dtv)

        # Clear out ymin and ymax from metadata;
        # make sure meta data block exists.
        # If not, create it.
        if hasattr(newsigobj, 'metadata'):
            delMeta = ['ymin', 'ymax']
            for key in delMeta:
                if newsigobj.metadata.has_key(key):
                    del newsigobj.metadata[key]
        else:
            newsigobj.metadata = {}

        newsigobj.updateValidTimes([val_tm0, val_tm1])

        key = 'title'
        if newsigobj.metadata.has_key(key):
            newsigobj.metadata[key] = ' '.join(
                ['Filtered', newsigobj.metadata[key]])
        elif vtsig.metadata.has_key(key):
            newsigobj.metadata[key] = ' '.join(
                ['Filtered', vtsig.metadata[key]])
        else:
            newsigobj.metadata[key] = 'Filtered'

        setattr(vtsig, 'active', newsigobj)
