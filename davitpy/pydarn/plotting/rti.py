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
.. module:: rti
   :synopsis: A module for generating rti plots

.. moduleauthor:: AJ, 20130123

*********************
**Module**: pydarn.plotting.rti
*********************
**Functions**:
  * :func:`pydarn.plotting.rti.plotRti`
  * :func:`pydarn.plotting.rti.plotFreq`
  * :func:`pydarn.plotting.rti.plotNoise`
  * :func:`pydarn.plotting.rti.plotCpid`
  * :func:`pydarn.plotting.rti.rtiTitle`
  * :func:`pydarn.plotting.rti.drawAxes`
"""


import numpy,math,matplotlib,calendar,datetime,pylab
import matplotlib.pyplot as plot
import matplotlib.lines as lines
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import MultipleLocator
from matplotlib.collections import PolyCollection
from davitpy.utils.timeUtils import *
from davitpy.pydarn.sdio import *
from matplotlib.figure import Figure


def plotRti(sTime,rad,eTime=None,bmnum=7,fileType='fitex',params=['velocity','power','width'], \
              scales=[],channel=None,coords='gate',colors='lasse',yrng=-1,gsct=False,lowGray=False, \
              pdf=False,png=False,dpi=500,show=True,retfig=False,filtered=False,fileName=None, \
              custType='fitex', tFreqBands=[], myFile=None,figure=None,xtick_size=9,ytick_size=9,xticks=None,axvlines=None,plotTerminator=False):
  """create an rti plot for a secified radar and time period

  **Args**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): a datetime object indicating the start time which you would like to plot
    * **rad** (str): the 3 letter radar code, e.g. 'bks'
    * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): a datetime object indicating th end time you would like plotted.  If this is None, 24 hours will be plotted.  default = None.
    * **[bmnum] (int)**: The beam to plot.  default: 7
    * **[fileType]** (str): The file type to be plotted, one of ['fitex','fitacf','lmfit'].  default = 'fitex'.
    * **[params]** (list): a list of the fit parameters to plot, allowable values are: ['velocity', 'power', 'width', 'elevation', 'phi0'].  default: ['velocity', 'power', 'width']
    * **[scales]** (list): a list of the min/max values for the color scale for each param.  If omitted, default scales will be used.  If present, the list should be n x 2 where n is the number of elements in the params list.  Use an empty list for default range, e.g. [[-250,300],[],[]].  default: [[-200,200],[0,30],[0,150]]
    * **[channel]** (char): the channel you wish to plot, e.g. 'a', 'b', 'c', ...  default: 'a'
    * **[coords]** (str): the coordinates to use for the y axis.  The allowable values are 'gate', 'rng', 'geo', 'mag' default: 'gate'
    * **[colors]** (str): a string indicating what color bar to use, valid inputs are ['lasse','aj'].  default: 'lasse'
    * **[yrng]** (list or -1): a list indicating the min and max values for the y axis in the chosen coordinate system, or a -1 indicating to plot everything.  default: -1.
    * **[gsct]** (boolean): a flag indicating whether to plot ground scatter as gray. default: False (ground scatter plotted normally)
    * **[lowGray]** (boolean): a flag indicating whether to plot low velocity scatter as gray. default: False (low velocity scatter plotted normally)
    * **[pdf]** (boolean): a flag indicating whether to output to a pdf file.  default = False.  WARNING: saving as pdf is slow.
    * **[png]** (boolean): a flag indicating whether to output to a png file.  default = False
    * **[dpi]** (int): dots per inch if saving as png.  default = 300
    * **[show]** (boolean): a flag indicating whether to display the figure on the screen.  This can cause problems over ssh.  default = True
    * **[retfig]** (boolean):  a flag indicating that you want the figure to be returned from the function.  Only the last figure in the list of frequency bands will be returned.  default = False
    * **[filtered]** (boolean): a flag indicating whether to boxcar filter the data.  default = False (no filter)
    * **[fileName]** (string): If you want to plot for a specific file, indicate the name of the file as fileName.  Include the type of the file in custType.
    * **[custType]** (string): the type (fitacf, lmfit, fitex) of file indicated by fileName
    * **[tFreqBands]** (list): a list of the min/max values for the transmitter frequencies in kHz.  If omitted, the default band will be used.  If more than one band is specified, retfig will cause only the last one to be returned.  default: [[8000,20000]]
    * **[myFile]** (:class:`pydarn.sdio.radDataTypes.radDataPtr`): contains the pipeline to the data we want to plot. If specified, data will be plotted from the file pointed to by myFile. default: None
    * **[figure]** (matplotlib.figure) figure object to plot on.  If None, a figure object will be created for you.
    * **[xtick_size]**: (int) fontsize of xtick labels
    * **[ytick_size]**: (int) fontsize of ytick labels
    * **[xticks]**: (list) datetime.datetime objects indicating the location of xticks
    * **[axvlines]**: (list) datetime.datetime objects indicating the location vertical lines marking the plot
    * **[plotTerminator]**: (boolean) Overlay the day/night terminator.
  **Returns**:
    * Possibly figure, depending on the **retfig** keyword

  **Example**:
    ::
    
      import datetime as dt
      pydarn.plotting.rti.plotRti(dt.datetime(2013,3,16), 'bks', eTime=dt.datetime(2013,3,16,14,30), bmnum=12, fileType='fitacf', scales=[[-500,500],[],[]], coords='geo',colors='aj', filtered=True, show=True)

    
  Written by AJ 20121002
  Modified by Matt W. 20130715
  Modified by Nathaniel F. 20131031 (added plotTerminator)
  """
  import os
  from davitpy import pydarn
  from davitpy import utils
    
  t1 = datetime.datetime.now()
  #check the inputs
  assert(isinstance(sTime,datetime.datetime)),'error, sTime must be a datetime object'
  assert(isinstance(rad,str) and len(rad) == 3),'error, rad must be a string 3 chars long'
  assert(isinstance(eTime,datetime.datetime) or eTime is None),'error, eTime must be a datetime object or None'
  assert(coords == 'gate' or coords == 'rng' or coords == 'geo' or coords == 'mag'),\
  "error, coords must be one of 'gate','rng','geo','mag"
  assert(isinstance(bmnum,int)),'error, beam must be integer'
  assert(0 < len(params) < 6),'error, must input between 1 and 5 params in LIST form'
  for i in range(0,len(params)):
    assert(params[i] == 'velocity' or params[i] == 'power' or params[i] == 'width' or \
    params[i] == 'elevation' or params[i] == 'phi0'), \
    "error, allowable params are 'velocity','power','width','elevation','phi0'"
  assert(scales == [] or len(scales)==len(params)), \
  'error, if present, scales must have same number of elements as params'
  assert(yrng == -1 or (isinstance(yrng,list) and yrng[0] <= yrng[1])), \
  'error, yrng must equal -1 or be a list with the 2nd element larger than the first'
  assert(colors == 'lasse' or colors == 'aj'),"error, valid inputs for color are 'lasse' and 'aj'"

  #assign any default color scales
  tscales = []
  for i in range(0,len(params)):
    if(scales == [] or scales[i] == []):
      if(params[i] == 'velocity'): tscales.append([-200,200])
      elif(params[i] == 'power'): tscales.append([0,30])
      elif(params[i] == 'width'): tscales.append([0,150])
      elif(params[i] == 'elevation'): tscales.append([0,50])
      elif(params[i] == 'vel_err'): tscales.append([-200,200])
      elif(params[i] == 'phi0'): tscales.append([-numpy.pi,numpy.pi])
    else: tscales.append(scales[i])
  scales = tscales

  #assign default frequency band
  tbands = []
  if tFreqBands == []: tbands.append([8000,20000])
  else: 
    for band in tFreqBands: 
      #make sure that starting frequncy is less than the ending frequency for each band
      assert(band[0] < band[1]),"Starting frequency must be less than ending frequency!"
      tbands.append(band)


  if eTime is None: eTime = sTime+datetime.timedelta(days=1)
  assert(sTime<eTime),"eTime must be greater than sTime!" 
   
  #open the file if a pointer was not given to us
  #if fileName is specified then it will be read
  if not myFile:
    myFile = radDataOpen(sTime,rad,eTime,channel=channel,bmnum=bmnum,fileType=fileType,filtered=filtered,fileName=fileName)
  else:
    #make sure that we will only plot data for the time range specified by sTime and eTime
    if myFile.sTime <= sTime and myFile.eTime > sTime and myFile.eTime >= eTime:
      myFile.sTime=sTime
      myFile.eTime=eTime
    else:
      #if the times range is not covered by the file, throw an error
      print 'error, data not available in myFile for the whole sTime to eTime'
      return None


  #check that we have data available now that we may have tried
  #to read it using radDataOpen
  if not myFile:
    print 'error, no files available for the requested time/radar/filetype combination'
    return None

  #Finally we can start reading the data file
  myBeam = radDataReadRec(myFile)
  if not myBeam:
    print 'error, no data available for the requested time/radar/filetype combination'
    return None

  #initialize empty lists
  vel,pow,wid,elev,phi0,times,freq,cpid,nave,nsky,nsch,slist,mode,rsep,nrang,frang,gsflg = \
        [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
  vel_err = []
  for i in range(len(tbands)):
    times.append([])
    cpid.append([])
    nave.append([])
    nsky.append([])
    rsep.append([])
    nrang.append([])
    frang.append([])
    nsch.append([])
    freq.append([])
    slist.append([])
    mode.append([])
    vel.append([])
    pow.append([])
    wid.append([])
    elev.append([])
    phi0.append([])
    gsflg.append([])
    vel_err.append([])
  
  #read the parameters of interest
  while(myBeam is not None):
    if(myBeam.time > eTime): break
    if(myBeam.bmnum == bmnum and (sTime <= myBeam.time)):
      for i in range(len(tbands)):
        if myBeam.prm.tfreq >= tbands[i][0] and myBeam.prm.tfreq <= tbands[i][1]:
          times[i].append(myBeam.time)
          cpid[i].append(myBeam.cp)
          nave[i].append(myBeam.prm.nave)
          nsky[i].append(myBeam.prm.noisesky)
          rsep[i].append(myBeam.prm.rsep)
          nrang[i].append(myBeam.prm.nrang)
          frang[i].append(myBeam.prm.frang)
          nsch[i].append(myBeam.prm.noisesearch)
          freq[i].append(myBeam.prm.tfreq/1e3)
          slist[i].append(myBeam.fit.slist)
          mode[i].append(myBeam.prm.ifmode)
          if('velocity' in params): vel[i].append(myBeam.fit.v)
          if('power' in params): pow[i].append(myBeam.fit.p_l)
          if('width' in params): wid[i].append(myBeam.fit.w_l)
          if('elevation' in params): elev[i].append(myBeam.fit.elv)
          if('phi0' in params): phi0[i].append(myBeam.fit.phi0)
          if('vel_err' in params): vel_err[i].append(myBeam.fit.v_e)
          gsflg[i].append(myBeam.fit.gflg)
      
    myBeam = radDataReadRec(myFile)

  for fplot in range(len(tbands)):
    #Check to ensure that data exists for the requested frequency band else
    #continue on to the next range of frequencies
    if not freq[fplot]:
      print 'error, no data in frequency range '+str(tbands[fplot][0])+' kHz to '+str(tbands[fplot][1])+' kHz'
      rtiFig=None	#Need this line in case no data is plotted
      continue

    #get/create a figure
    if figure is None:
        if show:
          rtiFig = plot.figure(figsize=(11,8.5))
        else:
          rtiFig = Figure(figsize=(14,14))
    else:
        rtiFig = figure
  
    #give the plot a title
    rtiTitle(rtiFig,sTime,rad,fileType,bmnum)
    #plot the noise bar
    plotNoise(rtiFig,times[fplot],nsky[fplot],nsch[fplot])
    #plot the frequency bar
    plotFreq(rtiFig,times[fplot],freq[fplot],nave[fplot])
    #plot the cpid bar
    plotCpid(rtiFig,times[fplot],cpid[fplot],mode[fplot])
    
    #plot each of the parameter panels
    figtop = .77
    figheight = .72/len(params)
    for p in range(len(params)):
      if(params[p] == 'velocity'): pArr = vel[fplot]
      elif(params[p] == 'power'): pArr = pow[fplot]
      elif(params[p] == 'width'): pArr = wid[fplot]
      elif(params[p] == 'elevation'): pArr = elev[fplot]
      elif(params[p] == 'phi0'): pArr = phi0[fplot]
      elif(params[p] == 'vel_err'): pArr = vel_err[fplot]
      pos = [.1,figtop-figheight*(p+1)+.02,.76,figheight-.02]
      
      #draw the axis
      ax = drawAxes(rtiFig,times[fplot],rad,cpid[fplot],bmnum,nrang[fplot],frang[fplot],rsep[fplot],p==len(params)-1,yrng=yrng,coords=coords,\
                    pos=pos,xtick_size=xtick_size,ytick_size=ytick_size,xticks=xticks,axvlines=axvlines)
  
      
      if(pArr == []): continue
      
      rmax = max(nrang[fplot])
      data=numpy.zeros((len(times[fplot])*2,rmax))+100000
      if gsct: gsdata=numpy.zeros((len(times[fplot])*2,rmax))+100000
      x=numpy.zeros(len(times[fplot])*2)
      tcnt = 0

      dt_list   = []
      for i in range(len(times[fplot])):
        x[tcnt]=matplotlib.dates.date2num(times[fplot][i])
        dt_list.append(times[fplot][i])

        if(i < len(times[fplot])-1):
          if(matplotlib.dates.date2num(times[fplot][i+1])-x[tcnt] > 4./1440.):
            tcnt += 1
            x[tcnt] = x[tcnt-1]+1./1440.
            dt_list.append(matplotlib.dates.num2date(x[tcnt]))
        tcnt += 1
            
        if(pArr[i] == []): continue
        
        if slist[fplot][i] is not None:
          for j in range(len(slist[fplot][i])):
            if(not gsct or gsflg[fplot][i][j] == 0):
              data[tcnt][slist[fplot][i][j]] = pArr[i][j]
            elif gsct and gsflg[fplot][i][j] == 1:
              data[tcnt][slist[fplot][i][j]] = -100000.
  
      if (coords != 'gate' and coords != 'rng') or plotTerminator == True:
        site    = pydarn.radar.network().getRadarByCode(rad).getSiteByDate(times[fplot][0])
        myFov   = pydarn.radar.radFov.fov(site=site,ngates=rmax,nbeams=site.maxbeam,rsep=rsep[fplot][0],coords=coords, date_time=times[fplot][0])
        myLat   = myFov.latCenter[bmnum]
        myLon   = myFov.lonCenter[bmnum]
          
      if(coords == 'gate'): y = numpy.linspace(0,rmax,rmax+1)
      elif(coords == 'rng'): y = numpy.linspace(frang[fplot][0],rmax*rsep[fplot][0],rmax+1)
      else: y = myFov.latFull[bmnum]
        
      X, Y = numpy.meshgrid(x[:tcnt], y)

      # Calculate terminator. ########################################################
      if plotTerminator:
            def daynight_terminator(date, lons):
                """
                date is datetime object (assumed UTC).
                """
                import mpl_toolkits.basemap.solar as solar
                dg2rad = np.pi/180.
                # compute greenwich hour angle and solar declination
                # from datetime object (assumed UTC).
                tau, dec = solar.epem(date)
                # compute day/night terminator from hour angle, declination.
                longitude = lons + tau
                lats = np.arctan(-np.cos(longitude*dg2rad)/np.tan(dec*dg2rad))/dg2rad
                return lats,tau,dec

            daylight = np.ones([len(dt_list),len(myLat)],np.bool)
            for tm_inx in range(len(dt_list)):
                tm                  = dt_list[tm_inx]
                term_lats,tau,dec   = daynight_terminator(tm,myLon)

                if dec > 0: # NH Summer
                    day_inx = np.where(myLat < term_lats)[0]
                else:
                    day_inx = np.where(myLat > term_lats)[0]

                if day_inx.size != 0:
                    daylight[tm_inx,day_inx] = False
     
            from numpy import ma
            daylight = ma.array(daylight,mask=daylight)
            ax.pcolormesh(X, Y, daylight.T, lw=0,alpha=0.10,cmap=matplotlib.cm.binary_r,zorder=99)
      ################################################################################
      
      cmap,norm,bounds = utils.plotUtils.genCmap(params[p],scales[p],colors=colors,lowGray=lowGray)
      
      pcoll = ax.pcolormesh(X, Y, data[:tcnt][:].T, lw=0.01,edgecolors='None',alpha=1,lod=True,cmap=cmap,norm=norm)
  
      cb = utils.drawCB(rtiFig,pcoll,cmap,norm,map_plot=0,pos=[pos[0]+pos[2]+.02, pos[1], 0.02, pos[3]])
      
      l = []
      #define the colorbar labels
      for i in range(0,len(bounds)):
        if(params[p] == 'phi0'):
          ln = 4
          if(bounds[i] == 0): ln = 3
          elif(bounds[i] < 0): ln = 5
          l.append(str(bounds[i])[:ln])
          continue
        if((i == 0 and (params[p] == 'velocity' or params[p] == 'vel_err')) or i == len(bounds)-1):
          l.append(' ')
          continue
        l.append(str(int(bounds[i])))
      cb.ax.set_yticklabels(l)
        
      #set colorbar ticklabel size
      for t in cb.ax.get_yticklabels():
        t.set_fontsize(9)
      
      #set colorbar label
      if(params[p] == 'velocity'): cb.set_label('Velocity [m/s]',size=10)
      if(params[p] == 'grid'): cb.set_label('Velocity [m/s]',size=10)
      if(params[p] == 'power'): cb.set_label('Power [dB]',size=10)
      if(params[p] == 'width'): cb.set_label('Spec Wid [m/s]',size=10)
      if(params[p] == 'elevation'): cb.set_label('Elev [deg]',size=10)
      if(params[p] == 'phi0'): cb.set_label('Phi0 [rad]',size=10)
      if(params[p] == 'vel_err'): cb.set_label('Velocity Error [m/s]',size=10)
  
    #handle the outputs
    if png == True:
      if not show:
        canvas = FigureCanvasAgg(rtiFig)
      rtiFig.savefig(sTime.strftime("%Y%m%d")+'_'+str(tbands[fplot][0])+'_'+str(tbands[fplot][1])+'.'+rad+'.png',dpi=dpi)
    if pdf:
      if not show:
        canvas = FigureCanvasAgg(rtiFig)
      rtiFig.savefig(sTime.strftime("%Y%m%d")+'_'+str(tbands[fplot][0])+'_'+str(tbands[fplot][1])+'.'+rad+'.pdf')
    if show:
      rtiFig.show()
      
    print 'plotting took:',datetime.datetime.now()-t1
    #end of plotting for loop
    
  if retfig:
    return rtiFig
  
def drawAxes(myFig,times,rad,cpid,bmnum,nrang,frang,rsep,bottom,yrng=-1,coords='gate',pos=[.1,.05,.76,.72],xtick_size=9,ytick_size=9,xticks=None,axvlines=None):
  """draws empty axes for an rti plot

  **Args**:
    * **myFig**: the MPL figure we are plotting to
    * **times**: a list of datetime objects referencing the beam soundings
    * **rad**: 3 letter radar code
    * **cpid**: list of the cpids or the beam soundings
    * **bmnum**: beam number being plotted
    * **nrang**: list of nrang for the beam soundings
    * **frang**: list of frang of the beam soundings
    * **rsep**: list of rsep of the beam soundings
    * **bottom**: flag indicating if we are at the bottom of the page
    * **[yrng]**: range of y axis, -1=autoscale (default)
    * **[coords]**: y axis coordinate system, acceptable values are 'geo', 'mag', 'gate', 'rng'
    * **[pos]**: position of the plot
    * **[xtick_size]**: fontsize of xtick labels
    * **[ytick_size]**: fontsize of ytick labels
    * **[xticks]**: (list) datetime.datetime objects indicating the location of xticks
    * **[axvlines]**: (list) datetime.datetime objects indicating the location vertical lines marking the plot
  **Returns**:
    * **ax**: an axes object
    
  **Example:
    ::

      ax = drawAxes(aFig,times,rad,cpid,beam,nrang,frang,rsep,0)
      
  Written by AJ 20121002
  """

  from davitpy import pydarn

  nrecs = len(times)
  #add an axes to the figure
  ax = myFig.add_axes(pos)
  ax.yaxis.set_tick_params(direction='out')
  ax.xaxis.set_tick_params(direction='out')
  ax.yaxis.set_tick_params(direction='out',which='minor')
  ax.xaxis.set_tick_params(direction='out',which='minor')

  #draw the axes
  ax.plot_date(matplotlib.dates.date2num(times), numpy.arange(len(times)), fmt='w', \
  tz=None, xdate=True, ydate=False, alpha=0.0)
  
  if(yrng == -1):
    ymin,ymax = 99999999,-999999999
    if(coords != 'gate'):
      oldCpid = -99999999
      for i in range(len(cpid)):
        if(cpid[i] == oldCpid): continue
        oldCpid = cpid[i]
        if(coords == 'geo' or coords == 'mag'):
          site = pydarn.radar.network().getRadarByCode(rad).getSiteByDate(times[i])
          myFov = pydarn.radar.radFov.fov(site=site, ngates=nrang[i],nbeams=site.maxbeam,rsep=rsep[i],coords=coords, date_time=times[i])
          if(myFov.latFull[bmnum].max() > ymax): ymax = myFov.latFull[bmnum].max()
          if(myFov.latFull[bmnum].min() < ymin): ymin = myFov.latFull[bmnum].min()
        else:
          ymin = 0
          if(nrang[i]*rsep[i]+frang[i] > ymax): ymax = nrang[i]*rsep[i]+frang[i]
    
    else:
      ymin,ymax = 0,max(nrang)
  else:
    ymin,ymax = yrng[0],yrng[1]

  xmin,xmax = matplotlib.dates.date2num(times[0]),matplotlib.dates.date2num(times[len(times)-1])
  xrng = (xmax-xmin)
  inter = int(round(xrng/6.*86400.))
  inter2 = int(round(xrng/24.*86400.))
  #format the x axis
  ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
  ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))

  
  # ax.xaxis.xticks(size=9)
  if(not bottom):
    for tick in ax.xaxis.get_major_ticks():
      tick.label.set_fontsize(0) 
  else:
    if xticks is not None:
      ax.xaxis.set_ticks(xticks)

  if axvlines is not None:
    for line in axvlines:
       ax.axvline(line,color='0.25',ls='--')

    for tick in ax.xaxis.get_major_ticks():
      tick.label.set_fontsize(xtick_size) 
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
    ax.xaxis.set_label_text('UT')
    
  #set ytick size
  for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(ytick_size) 
  #format y axis depending on coords
  if(coords == 'gate'): 
    ax.yaxis.set_label_text('Range gate',size=10)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))
    ax.yaxis.set_major_locator(MultipleLocator((ymax-ymin)/5.))
    ax.yaxis.set_minor_locator(MultipleLocator((ymax-ymin)/25.))
  elif(coords == 'geo' or coords == 'mag'): 
    if(coords == 'mag'): ax.yaxis.set_label_text('Mag Lat [deg]',size=10)
    else: ax.yaxis.set_label_text('Geo Lat [deg]',size=10)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%0.2f'))
    ax.yaxis.set_major_locator(MultipleLocator((ymax-ymin)/5.))
    ax.yaxis.set_minor_locator(MultipleLocator((ymax-ymin)/25.))
  elif(coords == 'rng'): 
    ax.yaxis.set_label_text('Slant Range [km]',size=10)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))
    ax.yaxis.set_major_locator(MultipleLocator(1000))
    ax.yaxis.set_minor_locator(MultipleLocator(250))
  
  ax.set_ylim(bottom=ymin,top=ymax)

  return ax
    
def rtiTitle(fig,d,rad,fileType,beam,xmin=.1,xmax=.86):
  """draws title for an rti plot

  **Args**:
    * **d**: the date being plotted as a datetime object
    * **rad**: the 3 letter radar code
    * **fileType**: the file type being plotted
    * **beam**: the beam number being plotted
    * **[xmin]**: minimum x value o the plot in page coords
    * **[xmax]**: maximum x value o the plot in page coords
  * **Returns**:
    *Nothing.
    
  **Example**:
    ::

      import datetime as dt
      rtiTitle(dt.datetime(2011,1,1),'bks','fitex',7)
      
  Written by AJ 20121002
  """
  from davitpy import pydarn

  r=pydarn.radar.network().getRadarByCode(rad)
  
  fig.text(xmin,.95,r.name+'  ('+fileType+')',ha='left',weight=550)
  
  fig.text((xmin+xmax)/2.,.95,str(d.day)+'/'+calendar.month_name[d.month][:3]+'/'+str(d.year), \
  weight=550,size='large',ha='center')
  
  fig.text(xmax,.95,'Beam '+str(beam),weight=550,ha='right')
  
def plotCpid(myFig,times,cpid,mode,pos=[.1,.77,.76,.05]):
  """plots cpid panel at position pos

  **Args**:
    * **myFig**: the MPL figure we are plotting on
    * **times**: a list of the times of the beam soundings
    * **cpid**: a lsit of the cpids of th beam soundings
    * **mode**: a list of the ifmode param
    * **[pos]**: position of the panel
  **Returns**:
    * Nothing.
    
  **Example**:
    ::

      plotCpid(rtiFig,times,cpid,mode)
      
  Written by AJ 20121002
  """
  from davitpy import pydarn
  oldCpid = -9999999
  
  #add an axes to the figure
  ax = myFig.add_axes(pos)
  ax.yaxis.tick_left()
  ax.yaxis.set_tick_params(direction='out')
  ax.set_ylim(bottom=0,top=1)
  ax.yaxis.set_minor_locator(MultipleLocator(1))
  ax.yaxis.set_tick_params(direction='out',which='minor')
  
  #draw the axes
  ax.plot_date(matplotlib.dates.date2num(times), numpy.arange(len(times)), fmt='w', \
  tz=None, xdate=True, ydate=False, alpha=0.0)
  
  for i in range(0,len(times)):
    if(cpid[i] != oldCpid):
      
      ax.plot_date([matplotlib.dates.date2num(times[i]),matplotlib.dates.date2num(times[i])],\
      [0,1], fmt='k-', tz=None, xdate=True, ydate=False)
      
      oldCpid = cpid[i]
      
      s = ' '+pydarn.radar.radUtils.getCpName(oldCpid)
    
      istr = ' '
      if(mode[i] == 1): istr = ' IF'
      if(mode == 0): istr = ' RF'
      
      ax.text(times[i],.5,' '+str(oldCpid)+s+istr,ha='left',va='center', size=10)
      
      
  xmin,xmax = matplotlib.dates.date2num(times[0]),matplotlib.dates.date2num(times[len(times)-1])
  xrng = (xmax-xmin)
  inter = int(round(xrng/6.*86400.))
  inter2 = int(round(xrng/24.*86400.))
  #format the x axis
  ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
  ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))

      
  # ax.xaxis.xticks(size=9)
  for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(0) 

  ax.set_yticks([])
  myFig.text(pos[0]-.07,pos[1]+pos[3]/2.,'CPID',ha='center',va='center', \
  size=8.5,rotation='vertical')
  
  
  
    
def plotNoise(myFig,times,sky,search,pos=[.1,.88,.76,.06],xlim=None,xticks=None):
  """plots a noise panel at position pos

  **Args**:
    * **myFig**: the MPL figure we are plotting on
    * **times**: a list of the times of the beam soundings
    * **sky**: a lsit of the noise.sky of the beam soundings
    * **search**: a list of the noise.search param
    * **[pos]**: position of the panel
    * **[xlim]**: 2-element limits of the x-axis.  None for default.
    * **[xticks]**: List of xtick poisitions.  None for default.
  **Returns**:
    * Nothing
    
  **Example**:
    ::

      plotNoise(rtiFig,times,nsky,nsch)
      
  Written by AJ 20121002
  Modified by NAF 20131101
  """
  
  #read the data
  #add an axes to the figure
  ax = myFig.add_axes(pos)
  ax.yaxis.tick_left()
  ax.yaxis.set_tick_params(direction='out')
  ax.set_ylim(bottom=0,top=6)
  ax.yaxis.set_minor_locator(MultipleLocator())
  ax.yaxis.set_tick_params(direction='out',which='minor')
  
  xmin,xmax = matplotlib.dates.date2num(times[0]),matplotlib.dates.date2num(times[len(times)-1])
  xrng = (xmax-xmin)
  inter = int(round(xrng/6.*86400.))
  inter2 = int(round(xrng/24.*86400.))
  #format the x axis
  ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
  ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))

  if xlim is not None: ax.set_xlim(xlim)
  if xticks is not None: ax.set_xticks(xticks)
  
  #plot the sky noise data
  ax.plot_date(matplotlib.dates.date2num(times), numpy.log10(sky), fmt='k-', \
  tz=None, xdate=True, ydate=False)
  #remove the x tick labels
  ax.set_xticklabels([' '])
  #use only 2 major yticks
  ax.set_yticks([0,6])
  ax.set_yticklabels([' ',' '])

  #left y axis annotation
  myFig.text(pos[0]-.01,pos[1]+.004,'10^0',ha='right',va='bottom',size=8)
  myFig.text(pos[0]-.01,pos[1]+pos[3],'10^6',ha='right',va='top',size=8)
  myFig.text(pos[0]-.07,pos[1]+pos[3]/2.,'N.Sky',ha='center',va='center',size=8.5,rotation='vertical')
  l=lines.Line2D([pos[0]-.06,pos[0]-.06], [pos[1]+.01,pos[1]+pos[3]-.01], \
      transform=myFig.transFigure,clip_on=False,ls='-',color='k',lw=1.5)                              
  ax.add_line(l)
  
  
  #add an axes to the figure
  ax2 = myFig.add_axes(pos,frameon=False)
  ax2.yaxis.tick_right()
  ax2.yaxis.set_tick_params(direction='out')
  ax2.set_ylim(bottom=0,top=6)
  ax2.yaxis.set_minor_locator(MultipleLocator())
  ax2.yaxis.set_tick_params(direction='out',which='minor')
  
  #plot the search noise data
  ax2.plot_date(matplotlib.dates.date2num(times), numpy.log10(search), fmt='k:', \
  tz=None, xdate=True, ydate=False,lw=1.5)

  ax2.set_xticklabels([' '])
  #use only 2 major yticks
  ax2.set_yticks([0,6])
  ax2.set_yticklabels([' ',' '])


  
  #right y axis annotation
  myFig.text(pos[0]+pos[2]+.01,pos[1]+.004,'10^0',ha='left',va='bottom',size=8)
  myFig.text(pos[0]+pos[2]+.01,pos[1]+pos[3],'10^6',ha='left',va='top',size=8)
  myFig.text(pos[0]+pos[2]+.06,pos[1]+pos[3]/2.,'N.Sch',ha='center',va='center',size=8.5,rotation='vertical')
  l=lines.Line2D([pos[0]+pos[2]+.07,pos[0]+pos[2]+.07], [pos[1]+.01,pos[1]+pos[3]-.01], \
  transform=myFig.transFigure,clip_on=False,ls=':',color='k',lw=1.5)                              
  ax2.add_line(l)
  
def plotFreq(myFig,times,freq,nave,pos=[.1,.82,.76,.06],xlim=None,xticks=None):
  """plots a frequency panel at position pos

  **Args**:
    * **myFig**: the MPL figure we are plotting on
    * **times**: a list of the times of the beam soundings
    * **freq**: a lsit of the tfreq of the beam soundings
    * **search**: a list of the nave param
    * **[pos]**: position of the panel
    * **[xlim]**: 2-element limits of the x-axis.  None for default.
    * **[xticks]**: List of xtick poisitions.  None for default.
  **Returns**:
    *Nothing.
    
  **Example**:
    ::

      plotFreq(rtiFig,times,tfreq,nave)
      
  Written by AJ 20121002
  Modified by NAF 20131101
  """
    
  #FIRST, DO THE TFREQ PLOTTING
  ax = myFig.add_axes(pos)
  ax.yaxis.tick_left()
  ax.yaxis.set_tick_params(direction='out')
  #ax.set_ylim(bottom=10,top=16)
  ax.set_ylim(bottom=8,top=20)
  ax.yaxis.set_minor_locator(MultipleLocator())
  ax.yaxis.set_tick_params(direction='out',which='minor')
  
  #for f in freq:
    #if(f > 16): f = 16
    #if(f < 10): f = 10
    
  ax.plot_date(matplotlib.dates.date2num(times), freq, fmt='k-', \
  tz=None, xdate=True, ydate=False,markersize=2)

  if xlim is not None: ax.set_xlim(xlim)
  if xticks is not None: ax.set_xticks(xticks)

  ax.set_xticklabels([' '])
  #use only 2 major yticks
  ax.set_yticks([10,16])
  ax.set_yticklabels([' ',' '])
  
  xmin,xmax = matplotlib.dates.date2num(times[0]),matplotlib.dates.date2num(times[len(times)-1])
  xrng = (xmax-xmin)
  inter = int(round(xrng/6.*86400.))
  inter2 = int(round(xrng/24.*86400.))
  #format the x axis
  ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=inter2))
  ax.xaxis.set_major_locator(matplotlib.dates.SecondLocator(interval=inter))
  
  myFig.text(pos[0]-.01,pos[1]+.005,'10',ha='right',va='bottom',size=8)
  myFig.text(pos[0]-.01,pos[1]+pos[3]-.015,'16',ha='right',va='top',size=8)
  myFig.text(pos[0]-.07,pos[1]+pos[3]/2.,'Freq',ha='center',va='center',size=9,rotation='vertical')
  myFig.text(pos[0]-.05,pos[1]+pos[3]/2.,'[MHz]',ha='center',va='center',size=7,rotation='vertical')
  l=lines.Line2D([pos[0]-.04,pos[0]-.04], [pos[1]+.01,pos[1]+pos[3]-.01], \
  transform=myFig.transFigure,clip_on=False,ls='-',color='k',lw=1.5)                              
  ax.add_line(l)
  
  
  #NEXT, DO THE NAVE PLOTTING
  ax2 = myFig.add_axes(pos,frameon=False)
  ax2.yaxis.tick_right()
  ax2.yaxis.set_tick_params(direction='out')
  ax2.set_ylim(bottom=0,top=80)
  ax2.yaxis.set_minor_locator(MultipleLocator(20))
  ax2.yaxis.set_tick_params(direction='out',which='minor')
  
  ax2.plot_date(matplotlib.dates.date2num(times), nave, fmt='k:', \
  tz=None, xdate=True, ydate=False,markersize=2)

  ax2.set_xticklabels([' '])
  #use only 2 major yticks
  ax2.set_yticks([0,80])
  ax2.set_yticklabels([' ',' '])

  
  myFig.text(pos[0]+pos[2]+.01,pos[1]+.004,'0',ha='left',va='bottom',size=8)
  myFig.text(pos[0]+pos[2]+.01,pos[1]+pos[3],'80',ha='left',va='top',size=8)
  myFig.text(pos[0]+pos[2]+.06,pos[1]+pos[3]/2.,'Nave',ha='center',va='center',size=8.5,rotation='vertical')
  l=lines.Line2D([pos[0]+pos[2]+.07,pos[0]+pos[2]+.07], [pos[1]+.01,pos[1]+pos[3]-.01], \
  transform=myFig.transFigure,clip_on=False,ls=':',color='k',lw=1.5)                              
  ax2.add_line(l)

