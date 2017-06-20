# -*- coding: utf-8 -*-
from __future__ import absolute_import
from matplotlib import pyplot as mp
import numpy as np
from .signalCommon import *

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
        sigRange = list(range(nSigs))

        for xx in sigRange:
            if hasattr(sigList[xx], 'data') is False:
                sigList[xx] = sigList[xx].active

        # Generate color iterator.
        cm = mp.get_cmap('gist_rainbow')
        colors = [cm(1. * i / nSigs) for i in sigRange]

        fig = mp.figure()
        mp.hold(True)

        # Allow linestyles to be passed.
        if 'ls' in self.metadata:
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
            if 'normalize' in self.metadata:
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
            if 'validTimes' in md:
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
        if 'xlabel' in md:
            mp.xlabel(md['xlabel'])
        if 'xmin' in md:
            mp.xlim(xmin=md['xmin'])
        if 'xmax' in md:
            mp.xlim(xmax=md['xmax'])

        mp.grid()

        # Make the legend.
        legend = []
        for xx in sigRange:
            md = sigList[xx].getAllMetaData()
            if 'legend' in md:
                temp = md['legend']
            elif 'title' in md:
                temp = md['title']
            else:
                temp = 'Data source ' + str(xx)

            if 'ylabel' in md:
                temp = ''.join([temp, ', ', md['ylabel']])

            legend.append(temp)

        if 'legend_size' in self.metadata:
            leg_size = self.metadata['legend_size']
        else:
            leg_size = 10
        font = {'size': leg_size}
        mp.legend(legend, loc='best', shadow=True, fancybox=True, prop=font)

        if 'normalize' in self.metadata:
            if self.metadata['normalize'] is True:
                mp.ylabel('All Data Normalized')

        # Use local plot settings.
        if hasattr(self, 'metadata'):
            if 'title' in self.metadata:
                mp.title(self.metadata['title'])
            if 'xlabel' in self.metadata:
                mp.xlabel(self.metadata['xlabel'])
            if 'ylabel' in self.metadata:
                mp.ylabel(self.metadata['ylabel'])
            if 'xmin' in self.metadata:
                mp.xlim(xmin=self.metadata['xmin'])
            if 'xmax' in self.metadata:
                mp.xlim(xmax=self.metadata['xmax'])
            if 'ymin' in self.metadata:
                mp.ylim(ymin=self.metadata['ymin'])
            if 'ymax' in self.metadata:
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
        sigRange = list(range(nSigs))

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
            if 'normalize' in self.metadata:
                if self.metadata['normalize'] is True:
                    plotData = plotData / np.nanmax(np.abs(plotData))
            mp.plot(sigList[xx].freqVec, plotData, color=colors[xx])

        mp.xlim(xmin=0)

        md = sigList[0].getAllMetaData()
        if 'fft_xlabel' in md:
            mp.xlabel(md['fft_xlabel'])
        if 'fft_xmin' in md:
            mp.xlim(xmin=md['fft_xmin'])
        if 'fft_xmax' in md:
            mp.xlim(xmax=md['fft_xmax'])

        mp.grid()

        # Make the legend.
        legend = []
        for xx in sigRange:
            md = sigList[xx].getAllMetaData()
            if 'fft_legend' in md:
                temp = md['fft_legend']
            elif 'legend' in md:
                temp = md['legend']
            elif 'title' in md:
                temp = md['title']
            else:
                temp = 'Data source ' + str(xx)

            if 'fft_ylabel' in md:
                temp = ''.join([temp, ', ', md['fft_ylabel']])
            elif 'ylabel' in md:
                temp = ''.join([temp, ', ', md['ylabel']])

            legend.append(temp)

        if 'legend_size' in self.metadata:
            leg_size = self.metadata['legend_size']
        else:
            leg_size = 10
        font = {'size': leg_size}
        mp.legend(legend, loc='best', shadow=True, fancybox=True, prop=font)

        if 'normalize' in self.metadata:
            if self.metadata['normalize'] is True:
                mp.ylabel('All Data Normalized')

        # Use local plot settings.
        if hasattr(self, 'metadata'):
            if 'title' in self.metadata:
                mp.title(self.metadata['title'])
            if 'xlabel' in self.metadata:
                mp.xlabel(self.metadata['xlabel'])
            if 'ylabel' in self.metadata:
                mp.ylabel(self.metadata['ylabel'])
            if 'xmin' in self.metadata:
                mp.xlim(xmin=self.metadata['xmin'])
            if 'xmax' in self.metadata:
                mp.xlim(xmax=self.metadata['xmax'])
            if 'ymin' in self.metadata:
                mp.ylim(ymin=self.metadata['ymin'])
            if 'ymax' in self.metadata:
                mp.ylim(ymax=self.metadata['ymax'])
            if 'fft_title' in self.metadata:
                mp.title(self.metadata['fft_title'])
            if 'fft_xlabel' in self.metadata:
                mp.xlabel(self.metadata['fft_xlabel'])
            if 'fft_ylabel' in self.metadata:
                mp.ylabel(self.metadata['fft_ylabel'])
            if 'fft_xmin' in self.metadata:
                mp.xlim(xmin=self.metadata['fft_xmin'])
            if 'fft_xmax' in self.metadata:
                mp.xlim(xmax=self.metadata['fft_xmax'])
            if 'fft_ymin' in self.metadata:
                mp.ylim(ymin=self.metadata['fft_ymin'])
            if 'fft_ymax' in self.metadata:
                mp.ylim(ymax=self.metadata['fft_ymax'])

        # Print the time window of the FFT on the side of the plot.
        s = ' - '.join([x.strftime('%Y%b%d %H:%M UT').upper()
                        for x in fftTimes])
        mp.annotate(s, xy=(1.01, 0.95), xycoords="axes fraction", rotation=90)

        mp.hold(False)
        mp.show()
