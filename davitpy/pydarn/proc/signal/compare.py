# -*- coding: utf-8 -*-
from matplotlib import pyplot as mp
import numpy as np
from signalCommon import *

class oplot(object):

    def __init__(self, sigList, **metadata):
        """Plots multiple vt sig/vt sigStruct objects on the same plot.

        Parameters
        ----------
        sigList : list
            A list of vt sig or sigStruct objects.
            If a sig object is provided, then the sig.active is used.
        **metadata
            keywords sent to matplot lib, etc.

        Attributes
        ----------
        sigList : list
            A list of vt sig or sigStruct objects.
            If a sig object is provided, then the sig.active is used.
        metadata
            keywords sent to matplot lib, etc.

        """
        self.sigList = sigList
        self.metadata = {}
        for key in metadata:
            self.metadata[key] = metadata[key]

        self.redraw()

    def redraw(self, **metadata):
        """Redraws the oplot object with any newly provided metadata
        keywords taken into account.

        Parameters
        ----------
        **metadata
            keywords sent to matplot lib, etc.

        """
        # Add metadata in keywords to object's metadata.
        for key in metadata:
            self.metadata[key] = metadata[key]

        # Make sure each item in siglist is a sigStruct object, not a sig
        # object.
        sigList = self.sigList
        nSigs = len(sigList)
        sigRange = range(nSigs)

        for xx in sigRange:
            if hasattr(sigList[xx], 'data') is False:
                sigList[xx] = sigList[xx].active

        # Generate color iterator.
        cm = mp.get_cmap('gist_rainbow')
        colors = [cm(1. * i / nSigs) for i in sigRange]

        fig = mp.figure()
        mp.hold(True)

        # Allow linestyles to be passed.
        if self.metadata.has_key('ls'):
            ls0 = self.metadata['ls']
        else:
            ls0 = '-'

        if np.size(ls0) != nSigs:
            if np.size(ls0) != 1:
                ls0 = ls0[0]
            ls = [ls0 for x in sigRange]

        # Plot the traces.
        for xx in sigRange:
            plotData = sigList[xx].data
            if self.metadata.has_key('normalize'):
                if self.metadata['normalize'] is True:
                    plotData = plotData / np.nanmax(np.abs(plotData))
            # mp.plot(sigList[xx].dtv,plotData,color=colors[xx],ls=ls[xx])
            mp.plot(sigList[xx].dtv, plotData, ls[xx], color=colors[xx])

        # Parse out valid times, grey out bad sections.
        t0 = []
        t1 = []
        val_t0 = []
        val_t1 = []
        # Find the most restrictive valid ranges.
        for xx in sigRange:
            t0.append(sigList[xx].dtv[0])
            t1.append(sigList[xx].dtv[-1])
            md = sigList[xx].getAllMetaData()
            if md.has_key('validTimes'):
                val_t0.append(md['validTimes'][0])
                val_t1.append(md['validTimes'][1])

        t0.sort()
        t1.sort(reverse=True)
        val_t0.sort(reverse=True)
        val_t1.sort()

        self.val_t0 = val_t0
        self.val_t1 = val_t1

        grey = '0.75'
        if len(val_t0) != 0:
            mp.axvspan(t0[0], val_t0[0], color=grey)
            mp.axvline(x=val_t0[0], color='g', ls='--', lw=2)
        if len(val_t1) != 0:
            mp.axvspan(val_t1[0], t1[0], color=grey)
            mp.axvline(x=val_t1[0], color='g', ls='--', lw=2)

        fig.autofmt_xdate()
#    title(data['title'])

        md = sigList[0].getAllMetaData()
        if md.has_key('xlabel'):
            mp.xlabel(md['xlabel'])
        if md.has_key('xmin'):
            mp.xlim(xmin=md['xmin'])
        if md.has_key('xmax'):
            mp.xlim(xmax=md['xmax'])

        mp.grid()

        # Make the legend.
        legend = []
        for xx in sigRange:
            md = sigList[xx].getAllMetaData()
            if md.has_key('legend'):
                temp = md['legend']
            elif md.has_key('title'):
                temp = md['title']
            else:
                temp = 'Data source ' + str(xx)

            if md.has_key('ylabel'):
                temp = ''.join([temp, ', ', md['ylabel']])

            legend.append(temp)

        if self.metadata.has_key('legend_size'):
            leg_size = self.metadata['legend_size']
        else:
            leg_size = 10
        font = {'size': leg_size}
        mp.legend(legend, loc='best', shadow=True, fancybox=True, prop=font)

        if self.metadata.has_key('normalize'):
            if self.metadata['normalize'] is True:
                mp.ylabel('All Data Normalized')

        # Use local plot settings.
        if hasattr(self, 'metadata'):
            if self.metadata.has_key('title'):
                mp.title(self.metadata['title'])
            if self.metadata.has_key('xlabel'):
                mp.xlabel(self.metadata['xlabel'])
            if self.metadata.has_key('ylabel'):
                mp.ylabel(self.metadata['ylabel'])
            if self.metadata.has_key('xmin'):
                mp.xlim(xmin=self.metadata['xmin'])
            if self.metadata.has_key('xmax'):
                mp.xlim(xmax=self.metadata['xmax'])
            if self.metadata.has_key('ymin'):
                mp.ylim(ymin=self.metadata['ymin'])
            if self.metadata.has_key('ymax'):
                mp.ylim(ymax=self.metadata['ymax'])

        mp.hold(False)
        mp.show()


class oplotfft(object):

    def __init__(self, sigList, **metadata):
        """Plots the spectrum of multiple vt sig/vt sigStruct objects
        on the same plot.

        Parameters
        ----------
        sigList : list
            A list of vt sig or sigStruct objects.
            If a sig object is provided, then the sig.active is used.
        **metadata
            keywords sent to matplot lib, etc.

        Attributes
        ----------
        sigList : list
            A list of vt sig or sigStruct objects.
            If a sig object is provided, then the sig.active is used.
        metadata
            keywords sent to matplot lib, etc.

        """
        self.sigList = sigList
        self.metadata = {}
        for key in metadata:
            self.metadata[key] = metadata[key]

        self.redraw()

    def redraw(self, **metadata):
        """Redraws the oplot object with any newly provided metadata keywords
        taken into account.

        Parameters
        ----------
        **metadata
            keywords sent to matplot lib, etc.

        """
        for key in metadata:
            self.metadata[key] = metadata[key]
        sigList = self.sigList
        nSigs = len(sigList)
        sigRange = range(nSigs)

        for xx in sigRange:
            if hasattr(sigList[xx], 'data') is False:
                sigList[xx] = sigList[xx].active

        # Find the most restrictive FFT time limits for all of the signals.
        fftStart = []
        fftEnd = []
        for xx in sigRange:
            temp = sigList[xx].getFftTimes()
            fftStart.append(temp[0])
            fftEnd.append(temp[1])

        fftStart.sort(reverse=True)
        fftEnd.sort()
        fftTimes = [fftStart[0], fftEnd[0]]

        # Generate color iterator.
        cm = mp.get_cmap('gist_rainbow')
        colors = [cm(1. * i / nSigs) for i in sigRange]

        fig = mp.figure()
        mp.hold(True)

        # Plot the traces.
        for xx in sigRange:
            sigList[xx].metadata['fftTimes'] = fftTimes
            sigList[xx].fft()
            plotData = abs(sigList[xx].spectrum)
            if self.metadata.has_key('normalize'):
                if self.metadata['normalize'] is True:
                    plotData = plotData / np.nanmax(np.abs(plotData))
            mp.plot(sigList[xx].freqVec, plotData, color=colors[xx])

        mp.xlim(xmin=0)

        md = sigList[0].getAllMetaData()
        if md.has_key('fft_xlabel'):
            mp.xlabel(md['fft_xlabel'])
        if md.has_key('fft_xmin'):
            mp.xlim(xmin=md['fft_xmin'])
        if md.has_key('fft_xmax'):
            mp.xlim(xmax=md['fft_xmax'])

        mp.grid()

        # Make the legend.
        legend = []
        for xx in sigRange:
            md = sigList[xx].getAllMetaData()
            if md.has_key('fft_legend'):
                temp = md['fft_legend']
            elif md.has_key('legend'):
                temp = md['legend']
            elif md.has_key('title'):
                temp = md['title']
            else:
                temp = 'Data source ' + str(xx)

            if md.has_key('fft_ylabel'):
                temp = ''.join([temp, ', ', md['fft_ylabel']])
            elif md.has_key('ylabel'):
                temp = ''.join([temp, ', ', md['ylabel']])

            legend.append(temp)

        if self.metadata.has_key('legend_size'):
            leg_size = self.metadata['legend_size']
        else:
            leg_size = 10
        font = {'size': leg_size}
        mp.legend(legend, loc='best', shadow=True, fancybox=True, prop=font)

        if self.metadata.has_key('normalize'):
            if self.metadata['normalize'] is True:
                mp.ylabel('All Data Normalized')

        # Use local plot settings.
        if hasattr(self, 'metadata'):
            if self.metadata.has_key('title'):
                mp.title(self.metadata['title'])
            if self.metadata.has_key('xlabel'):
                mp.xlabel(self.metadata['xlabel'])
            if self.metadata.has_key('ylabel'):
                mp.ylabel(self.metadata['ylabel'])
            if self.metadata.has_key('xmin'):
                mp.xlim(xmin=self.metadata['xmin'])
            if self.metadata.has_key('xmax'):
                mp.xlim(xmax=self.metadata['xmax'])
            if self.metadata.has_key('ymin'):
                mp.ylim(ymin=self.metadata['ymin'])
            if self.metadata.has_key('ymax'):
                mp.ylim(ymax=self.metadata['ymax'])
            if self.metadata.has_key('fft_title'):
                mp.title(self.metadata['fft_title'])
            if self.metadata.has_key('fft_xlabel'):
                mp.xlabel(self.metadata['fft_xlabel'])
            if self.metadata.has_key('fft_ylabel'):
                mp.ylabel(self.metadata['fft_ylabel'])
            if self.metadata.has_key('fft_xmin'):
                mp.xlim(xmin=self.metadata['fft_xmin'])
            if self.metadata.has_key('fft_xmax'):
                mp.xlim(xmax=self.metadata['fft_xmax'])
            if self.metadata.has_key('fft_ymin'):
                mp.ylim(ymin=self.metadata['fft_ymin'])
            if self.metadata.has_key('fft_ymax'):
                mp.ylim(ymax=self.metadata['fft_ymax'])

        # Print the time window of the FFT on the side of the plot.
        s = ' - '.join([x.strftime('%Y%b%d %H:%M UT').upper()
                        for x in fftTimes])
        mp.annotate(s, xy=(1.01, 0.95), xycoords="axes fraction", rotation=90)

        mp.hold(False)
        mp.show()
