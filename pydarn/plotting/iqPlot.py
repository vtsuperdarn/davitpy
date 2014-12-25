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
.. module:: iqPlot
   :synopsis: A module for generating plotting IQ voltage data

.. moduleauthor:: ASR, 20141225

*********************
**Module**: pydarn.plotting.iqPlot
*********************
**Functions**:
  * :func:`pydarn.plotting.iqPlot.plot_iq`
"""

def plot_iq(myBeam, sequences=None, mag_phase=False, scale=None, user_ax=None):

  """create an rti plot for a secified radar and time period

  **Args**:
    * **myBeam** : a beamData object from pydarn.sdio.radDataTypes
    * **[sequences]**: (list of ints or None) Defines which sequences of 
                       voltage data to plot. Default is None which plots 
                       all.
    * **[mag_phase]**: (boolean) Specifies whether magnitude and phase 
                       should be plotted instead of real and imaginary.
    * **[scale]**: (None or float) Specifies the scaling to use on real, 
                   imaginary, or magnitude axes. Default is None which 
                   auto-scales.
    * **[ax]**: a matplotlib axis object
  **Returns**:
    Nothing.

  **Example**:
    ::
      from datetime import datetime
      myPtr = pydarn.sdio.radDataOpen(datetime(2014,7,10),'sas',fileType='iqdat')
      pydarn.plotting.iqPlot.plot_iq(myBeam)

  Written by ASR 20141225
  """

  from matplotlib import pyplot
  import numpy as np
  import pydarn
  import matplotlib as mpl

  # obtain relevant parameters
  number_lags = myBeam.prm.mplgs
  tp = myBeam.prm.txpl
  rp = myBeam.prm.smsep
  tau = myBeam.prm.mpinc
  ltab = myBeam.prm.ltab
  ptab = myBeam.prm.ptab
  skpnum = myBeam.iqdat.skpnum
  seqnum = myBeam.iqdat.seqnum
  smpnum = myBeam.iqdat.smpnum
  smsep = myBeam.prm.smsep
  lagfr = myBeam.prm.lagfr

  # If an axis object is provided, but the sequence number is not,
  # set sequences so that the first sequence is plotted to the axis 
  # object
  if user_ax is not None:
    if sequences is None:
      sequences = [0]

  # check input
  # default to plotting all sequences
  if sequences is None:
    sequences = range(0,seqnum)

  # figure out when the tx pulses went out
  #number of ranges per tau
  tp_in_tau = tau/tp

  #determine which samples overlap with tx pulses
  tx_times=[p*tp_in_tau for p in ptab]
  blanked_samples=[]
  for tx in tx_times:
    blanked_samples.extend([tx])
  
  # Start plotting
  if user_ax is None:
    fig = pyplot.figure(figsize=(11,8.5))

  len_seq = len(sequences)
  figtop = .88
  figheight = .82/len_seq

  #plot the iq data for each of the requested pulse sequences
  for s,seq in enumerate(sequences):

    #calculate the positions of the data axis and colorbar axis 
    #for the current parameter and then add them to the figure
    pos = [.1,figtop-figheight*(s+1)+.05,.8,figheight]#-.04]
    #cpos = [.86,figtop-figheight*(p+1)+.05,.03,figheight-.04]    
    if user_ax is None:
      ax = fig.add_axes(pos)
    else:
      ax = user_ax

    if (s == 0):
      rad = pydarn.radar.network().getRadarById(5).code[0]
      time = myBeam.time.strftime('%H:%M:%S UT %d/%m/%Y')
      title='Pulse Sequence IQ Data  '+rad+'   Beam '+str(myBeam.bmnum)+'   Tx Freq '+str(myBeam.prm.tfreq)+'kHz   Time: '+ time
      ax.set_title(title)

    ax.set_xticklabels([])
    ax.set_yticklabels([])

    sample_nums = range(0,myBeam.iqdat.smpnum)

    iq_real = np.array([x[0] for x in myBeam.iqdat.mainData[seq]])
    iq_imag = np.array([x[1] for x in myBeam.iqdat.mainData[seq]])

    if (mag_phase):
      mag = np.sqrt(iq_real**2 + iq_imag**2)
      phase = np.arctan2(iq_imag,iq_real)
      if scale is None:
        scale_const = np.mean(mag)
      else:
        scale_const = scale
      ax.plot(sample_nums, mag/scale_const - np.pi,'k')
      ax.plot(sample_nums, phase,'r')
      ax.set_xlim([0,smpnum])
      ax.set_ylim([-np.pi,np.pi])
    else:
      mag = np.sqrt(iq_real**2 + iq_imag**2)
      if scale is None:
        scale_const = np.mean(mag)/np.sqrt(2.)
      else:
        scale_const = scale
      ax.plot(sample_nums, iq_real/scale_const,'k')
      ax.plot(sample_nums, iq_imag/scale_const,'r')
      ax.set_xlim([0,smpnum])
      ax.set_ylim([-np.pi,np.pi])
    ax.set_ylabel(str(seq))


  # Now plot when the Tx pulses were sent out

  txs = [1 if (x in blanked_samples) else 0 for x in sample_nums]
  pos = [.1,figtop-figheight*(len_seq)+.02,.8,0.03]

  if user_ax is None:
    ax = fig.add_axes(pos)

  # constant for setting the "width" of the Tx pulse
  const = tp/float(rp)
  for x in blanked_samples:
    time = np.array([x, x, x+const, x+const])
    amp = np.array([0, 1, 1, 0])
    if user_ax is None:
      ax.fill(time,amp,color='black')
      ax.set_ylabel('Tx')
      ax.set_xlabel('Sample Number')
      ax.set_xlim([0,smpnum])
      ax.set_yticklabels([])
    else:
      ax.plot(time,amp,color='black')

  if user_ax is None:
    fig.show()


