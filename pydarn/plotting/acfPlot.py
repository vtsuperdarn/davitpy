# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
.. module:: acfPlot
   :synopsis: A module for generating plotting ACF and XCF data

.. moduleauthor:: ASR, 20141230

*********************
**Module**: pydarn.plotting.acfPlot
*********************
**Functions**:
  * :func:`pydarn.plotting.acfPlot.plot_acf`
  * :func:`pydarn.plotting.acfPlot.calc_blanked`
  * :func:`pydarn.plotting.acfPlot.plot_rli`
  * :func:`pydarn.plotting.acfPlot.nuft`
"""

def plot_acf(myBeam, gate, mark_blanked=True, xcf=False, panel=0, ax=None):

    """Plot the ACF/XCF for a specified beamData object at a
       specified range gate

    **Args**:
        * **myBeam** : a beamData object from pydarn.sdio.radDataTypes
        * **gate**: (int) The range gate to plot data for.
        * **[mark_blanked]**: (boolean) Specifies whether magnitude and 
                              phase should be plotted instead of real and 
                              imaginary.
        * **[xcf]**: (boolean) Specifies wheather to plot XCF data or not 
        * **[panel]**: (int) from 0 to 3 specifies which data to plot of
                       ACF/XCF, ACF/XCF amplitude, ACF/XCF phase, or
                       power spectrum, respectively.
        * **[ax]**: a matplotlib axis object

    **Returns**:
        Nothing.

    **Example**:
        ::
            from datetime import datetime
            myPtr = pydarn.sdio.radDataOpen(datetime(2012,5,21), \
                                          'kap',fileType='rawacf')
            myBeam = myPtr.readRec()
            pydarn.plotting.acfPlot.plot_acf(myBeam,24)

        Written by ASR 20141230
    """

    from matplotlib import pyplot
    import numpy as np
    import pydarn
                 
    number_lags = myBeam.prm.mplgs
    lags = list(set([x[1]-x[0] for x in myBeam.prm.ltab]))
    ltab = myBeam.prm.ltab
    smsep = myBeam.prm.smsep
    tau = myBeam.prm.mpinc
    tfr = myBeam.prm.lagfr
    tp = myBeam.prm.txpl
    nrang = myBeam.prm.nrang
    nave = myBeam.prm.nave
    mplgs = myBeam.prm.mplgs
    noise = np.array(myBeam.prm.noisesearch)
    power = np.array(myBeam.rawacf.pwr0)
    fluct = 1/np.sqrt(nave)*(1+1/(power[gate]/noise))

    #Grab the appropriate data for plotting
    if ((xcf) and (myBeam.prm.xcf == 0)):
        print "No interferometer data available."
        return
    elif ((xcf) and (myBeam.prm.xcf == 1)):
        re = np.array([x[0]/power[gate] for x in myBeam.rawacf.xcfd[gate]]) 
        im = np.array([x[1]/power[gate] for x in myBeam.rawacf.xcfd[gate]])
    else:
        re = np.array([x[0]/power[gate] for x in myBeam.rawacf.acfd[gate]])
        im = np.array([x[1]/power[gate] for x in myBeam.rawacf.acfd[gate]])

    # determine which lags are blanked by Tx pulses
    blanked = calc_blanked(ltab,tp,tau,tfr,gate)
    tx = np.zeros(mplgs)
    for l,lag in enumerate(lags):
        if len(blanked[lag]):
            tx[l] = 1
        else:
            tx[l] = 0 

    # Take the fourier transform of the complex ACF to 
    # get the power spectrum
    temp = nuft(re+1j*im,np.array(lags),lags[-1])
    acfFFT = []
    acfFFT.extend(temp[len(temp)/2+1:])
    acfFFT.extend(temp[0:len(temp)/2+1])
    freq_scale_factor = 1/(lags[-1]*myBeam.prm.mpinc*10.0**-6)/(myBeam.prm.tfreq*1000.)/2.*(3.*10**8)
    vels = freq_scale_factor*(np.array(range(len(acfFFT)))-len(acfFFT)/2)  

    # Calculate the amplitude and phase of the complex ACF/XCF
    amplitude = np.sqrt(re**2 + im**2)
    phase = np.arctan2(im,re)

    #Calculate bounds for plotting
    lag_numbers = []
    for lag in lags:
        temp = [lag-0.5, lag+0.5]
        lag_numbers.extend(temp)

    if ax is None:
        fig=pyplot.figure()
        ax1=fig.add_axes([0.1,0.55,0.35,0.35])
        ax2=fig.add_axes([0.1,0.1,0.35,0.35])
        ax3=fig.add_axes([0.5,0.1,0.35,0.35])
        ax4=fig.add_axes([0.5,0.55,0.35,0.35])
    else:
        ax1=None
        ax2=None
        ax3=None
        ax4=None

    #Now plot the ACF/XCF panel as necessary
    if (ax is not None) and (panel == 0):
        ax1 = ax
    elif (ax1 is not None):
        title1 = myBeam.time.strftime('%d %b, %Y %H:%M:%S UT')
        ax1.set_title(title1)
   
    if (ax1 is not None):
        if ((blanked) and (mark_blanked)):
            inds = np.where(tx == 1)[0]
            if len(inds):
                for ind in inds:
                    ax1.plot(lags[ind],re[ind],marker='x',color='red',mew=3,ms=8,zorder=10)
                    ax1.plot(lags[ind],im[ind],marker='x',color='red',mew=3,ms=8,zorder=10)
    
        ax1.plot(lags,re,marker='o',color='blue',lw=2)
        ax1.plot(lags,im,marker='o',color='green',lw=2)
        ax1.plot([lags[0],lags[-1]+1],[0,0],'k--',lw=2)

        ax1.set_xlim([-0.5,lag_numbers[-1]])
        ax1.set_xlabel('Lag Number') 
        ax1.set_ylabel('ACF') 
        ax1.set_ylim([-1.5,1.5])
        ax1.set_yticks(np.linspace(-1,1,num=5))


    #Now plot the ACF/XCF amplitude panel as necessary
    if ((ax is not None) and (panel == 1)):
        ax2 = ax

    if (ax2 is not None):
        if ((blanked) and (mark_blanked)):
            inds = np.where(tx == 1)[0]
            if len(inds):
                for ind in inds:
                    ax2.plot(lags[ind],amplitude[ind],marker='x',color='red',mew=3,ms=8,zorder=10)  

        ax2.plot(lags,amplitude,marker='o',color='black',lw=2,zorder=1)
        ax2.plot([lags[0],lags[-1]+1],[fluct,fluct],'b--',lw=2,zorder=1)
  
        ax2.set_xlim([-0.5,lag_numbers[-1]])
        ax2.set_xlabel('Lag Number') 
        ax2.set_ylabel('Lag Power')   
        ax2.set_ylim([0,1.05*np.max(amplitude)])
        ax2.set_yticks(np.linspace(0.2,1.2,num=6))

    #Now plot the ACF/XCF phase panel as necessary
    if ((ax is not None) and (panel == 2)):
        ax3 = ax

    if (ax3 is not None):
        if ((blanked) and (mark_blanked)):
            inds = np.where(tx == 1)[0]
            if len(inds):
                for ind in inds:
                    ax3.plot(lags[ind],phase[ind],marker='x', \
                             color='black',mew=3,ms=8,zorder=10)
    
        ax3.plot(lags,phase,marker='o',color='red',lw=2)
        ax3.plot([lags[0],lags[-1]+1],[0,0],'k--',lw=2)
  
        ax3.set_xlim([-0.50,lag_numbers[-1]])
        ax3.set_xlabel('Lag Number')  
        ax3.set_ylabel('Phase')
        ax3.set_ylim([-np.pi-0.5,np.pi+0.5])
        ax3.set_yticks(np.linspace(-3,3,num=7))
        if ax is None:
            ax3.yaxis.set_ticks_position('right')
            ax3.yaxis.set_label_position('right')

    #Now plot the power spectrum panel as necessary
    if ((ax is not None) and (panel == 3)):
        ax4 = ax
    elif (ax4 is not None):
        title2 = pydarn.radar.network().getRadarById(myBeam.stid).name+\
                 ' Beam: '+str(myBeam.bmnum)+' Gate: '+str(gate)
        ax4.set_title(title2)

    if (ax4 is not None):
        ax4.plot(vels,np.abs(acfFFT),marker='o',lw=2)
        ax4.set_xlabel('Velocity (m/s)')  
        ax4.set_ylabel('Spectral Power (arb)')
        if ax is None:
            ax4.yaxis.set_ticks_position('right')
            ax4.yaxis.set_label_position('right')

    if ax is None:
        fig.show()
  

def calc_blanked(ltab,tp,tau,tfr,gate):

    """Function that calculates the lags that are affected by Tx pulse 
       receiver blanking.

    **Args**:
        * **ltab** : (list) The received lag table for the Tx-ed pulse sequence.
        * **tp**: (int) The Tx pulse length in microseconds.
        * **tau**: (int) The lag time in microseconds.
        * **tfr**: (int) The time to first range gate in microseconds.
        * **gate**: (int) The range gate to plot data for.

    **Returns**:
        Nothing.

    **Example**:
        ::
            from datetime import datetime
            myPtr = pydarn.sdio.radDataOpen(datetime(2012,5,21), \
                                          'kap',fileType='rawacf')
            myBeam = myPtr.readRec()
            ltab = myBeam.prm.ltab
            tau = myBeam.prm.mpinc
            tfr = myBeam.prm.lagfr
            tp = myBeam.prm.txpl
            pydarn.plotting.acfPlot.calc_blanked(ltab,tp,tau,tfr,24)

        Written by ASR 20141230
    """

    import numpy as np

    #Calculate the lags and the pulse table
    lags = []
    ptab = []
    for pair in ltab:
        lags.append(pair[1]-pair[0])
        ptab.extend(pair)
    lags=list(set(lags))
    ptab=list(set(ptab))
    lags.sort()  
    ptab.sort()

    txs_in_lag={}
    for lag in lags:
        txs_in_lag[lag]=[]

    #number of ranges per tau
    tp_in_tau = tau/tp

    #determine which range gates correspond to blanked samples
    tx_times=[p*tp_in_tau for p in ptab]
    blanked_samples=[]
    for tx in tx_times:
        blanked_samples.extend([tx, tx+1])

    for lag in lags:
        for pair in ltab:
            if (pair[1] - pair[0] == lag):
                #which samples were used to generate the acf
                S1=tp_in_tau*pair[0]+gate + 1.*tfr/(tp)
                S2=tp_in_tau*pair[1]+gate + 1.*tfr/(tp)
                br=[]
                #check to see if the samples are blanked or not
                if S1 in blanked_samples:
                    br.append(S1)
                if S2 in blanked_samples:
                    br.append(S2)
                txs_in_lag[lag].extend(br)

    return txs_in_lag




def plot_rli(myBeam, xcf=False):

    """This function plots a range-lag-intensity plot of ACF/XCF data for
       an input beamData object.

    **Args**:
        * **myBeam** : A beamData object from pydarn.sdio.radDataTypes.
        * **[xcf]**: (boolean) Specifies wheather to plot XCF data or not.

    **Returns**:
        Nothing.

    **Example**:
        ::
            from datetime import datetime
            myPtr = pydarn.sdio.radDataOpen(datetime(2012,5,21), \
                                          'kap',fileType='rawacf')
            myBeam = myPtr.readRec()
            pydarn.plotting.acfPlot.plot_rli(myBeam)

        Written by ASR 20141230
    """

    from matplotlib import pyplot
    import numpy as np
    from matplotlib import colors
    import matplotlib as mpl
    import matplotlib.cm as cmx

    #Get parameters
    number_lags = myBeam.prm.mplgs
    lags = list(set([x[1]-x[0] for x in myBeam.prm.ltab]))
    range_gates = np.linspace(0.5,myBeam.prm.nrang+0.5,num=myBeam.prm.nrang+1)
    power=np.array(myBeam.rawacf.pwr0)
    noise=np.array(myBeam.prm.noisesearch)

    #Make the figure and axes
    fig=pyplot.figure()
    ax1=fig.add_axes([0.1,0.1,0.77,0.1])
    ax2=fig.add_axes([0.1,0.2,0.77,0.7])
    ax3=fig.add_axes([0.88,0.2,0.02,0.7])

    #Plot the SNR
    ax1.plot(range(1,myBeam.prm.nrang+1),10*np.log10(power/noise),lw=5)

    #Calculate bounds for plotting
    lag_numbers = []
    for lag in lags:
        temp = [lag-0.5, lag+0.5]
        lag_numbers.extend(temp)

    #generate a scalar colormapping to map data to cmap
    cl=[-1,1]
    cmap='jet'
    cNorm = colors.Normalize(vmin=cl[0], vmax=cl[1])
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

    #Now plot SCR data  
    for r in range(myBeam.prm.nrang):

        #Grab the appropriate data for plotting
        if ((xcf) and (myBeam.prm.xcf == 0)):
            print "No interferometer data available."
            return
        elif ((xcf) and (myBeam.prm.xcf == 1)):
            re = np.array([x[0]/power[r] for x in myBeam.rawacf.xcfd[r]]) 
            im = np.array([x[1]/power[r] for x in myBeam.rawacf.xcfd[r]])
        else:
            re = np.array([x[0]/power[r] for x in myBeam.rawacf.acfd[r]])
            im = np.array([x[1]/power[r] for x in myBeam.rawacf.acfd[r]])

      #Index needed for plotting but not incrementing on missing lags
        i=0
        for l in range(lags[-1]+1):
            #Make coordinates for:
            #Real and
            x1 = np.array([r+0.5,r+0.5,r+1.0,r+1.0])
            #Imaginary compenents of ACF/XCF
            x2 = np.array([r+1.0,r+1.0,r+1.5,r+1.5])
            y = np.array([l-0.5,l+0.5,l+0.5,l-0.5])

            #If the lag isn't a "missing" lag plot the data, else plot a black square.
            if (l in lags):
                ax2.fill(x1,y,color=scalarMap.to_rgba(re[i]))
                ax2.fill(x2,y,color=scalarMap.to_rgba(im[i]))
                i+=1
            else:
                ax2.fill(x1,y,color='black')
                ax2.fill(x2,y,color='black')

    #Add the colorbar and label it    
    cbar = mpl.colorbar.ColorbarBase(ax3,norm=cNorm,cmap=cmap)
    cbar.set_label('Amplitude')

    #Set plot axis labels
    ax2.set_ylim([-0.5,lag_numbers[-1]])
    ax2.set_yticks(np.linspace(0,lags[-1],num=lags[-1]+1))
    ax2.set_xlim([range_gates[0],range_gates[-1]])
    ax2.set_xticklabels([],visible=False)
    ax2.set_ylabel('Lag Number')

    #Set pwr0 plot axis labels
    ax1.set_xlim([range_gates[0],range_gates[-1]])
    ax1.set_ylim([0,40])
    ax1.set_yticks(np.linspace(0,30,num=4))
    ax1.set_ylabel(r'pwr$_{0}$''\n(dB)')
    ax1.set_xlabel('Range Gate')

    fig.show()




def nuft(a,tn,T):
    """A function to calculate the non-uniformly sampled discrete Fourier transform.

    **Args**:
        * **a** : (np.array) The input array to be transformed.
        * **tn**: (float) An array of timestamps for the input array.
        * **T**: (float) The end time of the input array.

    **Returns**:
        Nothing.

        Written by ASR 20141230
    """

    import numpy as np
    T=float(T)
    ft=np.zeros((len(a),),np.complex)
    for m in range(len(a)):
        ft[m] = np.sum(a*np.exp(-1j*2*np.pi/T*m*tn))

    return ft



if __name__ == "__main__":

    import pydarn
    from datetime import datetime
    from matplotlib import pyplot

    print "First we need to fetch an rawacf file and read a beam record..."
    myPtr = pydarn.sdio.radDataOpen(datetime(2012,5,21),'sas', eTime=datetime(2012,5,21,2),fileType='rawacf')
    myBeam = myPtr.readRec()

    print "Testing the plot_rli method and it's options...."
    print "...First test default options..."
    pydarn.plotting.acfPlot.plot_rli(myBeam)

    print "...Next test with 'xcf=True'..."
    pydarn.plotting.acfPlot.plot_rli(myBeam,xcf=True)

    print "Close the figures to proceed with testing..."
    pyplot.show()

    print "Testing the plot_acf method and it's options...."
    print "...First test default options, at range gate 31, you should see ground scatter and lags marked that are blanked by Tx blanking..."
    pydarn.plotting.acfPlot.plot_acf(myBeam,31)

    print "...Next, with 'mark_blanked=False', blanking marking turned off "
    pydarn.plotting.acfPlot.plot_acf(myBeam,31,mark_blanked=False)

    print "...Next, with 'xcf=True', plotting xcf data"
    pydarn.plotting.acfPlot.plot_acf(myBeam,31,xcf=True)

    fig = pyplot.figure()
    ax = fig.add_axes([0.1,0.1,0.8,0.8])
    print "...Next, plotting to our own axis object, 'ax=ax'"
    pydarn.plotting.acfPlot.plot_acf(myBeam,31,ax=ax)

    pyplot.show()

