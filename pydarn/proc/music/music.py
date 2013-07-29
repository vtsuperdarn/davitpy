import numpy as np
import datetime 
import time
import copy

import pydarn

Re = 6378   #Earth radius

options = {}
options['timeStep']       = 2.          #;timeStep between scans in Minutes.
options['param']          = 'power'
options['scale']          = [-25, 25]
options['filtered']       = False
options['ajground']       = False
options['scatterflag']    = 1
options['sim']            = 0 
options['keep_lr']        = 0 
options['kx_min']         = 0.05
options['ky_min']         = 0.05
options['coord']          = 'geog'
options['dkx']            = 0.001
options['dky']            = 0.001
options['gl']             = 3
options['test']           = 0
options['nmax']           = 5
options['fir_filter']     = 1
options['zero_padding']   = 1
options['use_all_cells']  = 1
options['fft_range']      = [0., 1.5]
options['fir_scale']      = [-10, 10]

params                    = {}
params['datetime']        = [datetime.datetime(2010,11,19,9,30), datetime.datetime(2010,11,19,19,30)]
params['radar']           = 'gbr'
params['channel']         = 'a'
params['bmnum']            = 6
params['drange']          = [500,1000]
params['band']            = [0.3,1.2]
params['kmax']            = 0.05
params['fir_datetime']    = [datetime.datetime(2010,11,19,14,10), datetime.datetime(2010,11,19,16,00)]

class music(object):
  def __init__(self):
   self.options = options
   self.params  = params

class musicDataObj(object):
  def __init__(self, time, data, fov=None, comment=None, parent=0, **metadata):
    self.parent = parent
    """Define a vtMUSIC sigStruct object.

    :param time: datetime.datetime list
    :param data: 3-dimensional array of data
    :param fov:  DaViTPy radar field of view object
    :param comment: String to be appended to the history of this object
    :param **metadata: keywords sent to matplot lib, etc.
    :returns: sig object
    """

    self.time     = np.array(time)
    self.data     = np.array(data)
    self.fov      = fov
    self.metadata = {}
    for key in metadata: self.metadata[key] = metadata[key]

    self.history = {datetime.datetime.now():comment}


  def copy(self,newsig,comment):
    """Copy a vtMUSIC object.  This deep copies data and metadata, updates the serial number, and logs a comment in the history.  Methods such as plot are kept as a reference.
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

    newsigobj.time      = copy.deepcopy(self.time)
    newsigobj.data      = copy.deepcopy(self.data)
    newsigobj.fov       = copy.deepcopy(self.fov)
    newsigobj.metadata  = copy.deepcopy(self.metadata)
    newsigobj.history   = copy.deepcopy(self.history)

    newsigobj.history[datetime.datetime.now()] = comment
    
    return newsigobj
  
#  def makeNewSignal(self,newsig,dtv,data,comment,**kwargs):
#    """Create a new vt sigStruct object that is a derivative of this one.  This deep copies data and metadata, updates the serial number, and logs a comment in the history.  Methods such as plot are kept as a reference.
#    :param newsig: A string with the name for the new signal.
#    :paran dtv: A new datetime.datetime array.
#    :param data: A new data array.
#    :param comment: A string comment describing the new signal.
#    :returns: sig object
#
#    :**kwargs:
#      appendTitle: String that will be appended to plot's title.
#    """
#    newobj = self.copy(newsig,comment)
#    newobj.dtv  = dtv
#    newobj.data = data
#
#    if kwargs.has_key('appendTitle'):
#      md = newobj.getAllMetaData()
#      if md.has_key('title'):
#        newobj.metadata['title'] = ' '.join([kwargs['appendTitle'],md['title']]) 
#
#    newobj.setActive()

  def setActive(self):
    """Sets this signal as the currently active signal.
    """
    self.parent.active = self
    
class musicArray(object):
  def __init__(self,myPtr,sTime=None,eTime=None,param='p_l',gscat=1,fovElevation=None,fovModel='GS',fovCoords='geo'):
#    fov = pydarn.radar.radFov.fov(frang=180.0, rsep=45.0, site=None, nbeams=None, ngates=None, bmsep=None, recrise=None, siteLat=None, siteLon=None, siteBore=None, siteAlt=None, elevation=None, altitude=300.0, model='IS', coords='geo')
#    0: plot all backscatter data 
#    1: plot ground backscatter only
#    2: plot ionospheric backscatter only
#    3: plot all backscatter data with a ground backscatter flag.

    if sTime == None: sTime = myPtr.sTime
    if eTime == None: eTime = myPtr.eTime

    scanTimeList = []
    dataList  = []
    cpidList  = []
    #Subscripts of columns in the dataList/dataArray
    scanInx = 0
    dateInx = 1
    beamInx = 2
    gateInx = 3
    dataInx = 4

    beamTime  = sTime
    scanNr    = np.uint64(0)
    fov       = None
    while beamTime < eTime:
      #Load one scan into memory.
      myScan = pydarn.sdio.radDataRead.radDataReadScan(myPtr)
      if myScan == None: break

      for myBeam in myScan:
        #Calculate the field of view if it has not yet been calculated.
        if fov == None:
          radStruct = pydarn.radar.radStruct.radar(radId=myPtr.stid)
          site      = pydarn.radar.radStruct.site(radId=myPtr.stid,dt=sTime)
          fov       = pydarn.radar.radFov.fov(frang=myBeam.prm.frang, rsep=myBeam.prm.rsep, site=site,elevation=fovElevation,model=fovModel,coords=fovCoords)

        #Get information from each beam in the scan.
        beamTime = myBeam.time 
        bmnum    = myBeam.bmnum
        fitDataList = getattr(myBeam.fit,param)
        slist       = getattr(myBeam.fit,'slist')
        gflag       = getattr(myBeam.fit,'gflg')

        for (gate,data,flag) in zip(slist,fitDataList,gflag):
          #Get information from each gate in scan.  Skip record if the chosen ground scatter option is not met.
          if (gscat == 1) and (flag == 0): continue
          if (gscat == 2) and (flag == 1): continue
          tmp = (scanNr,beamTime,bmnum,gate,data)
          dataList.append(tmp)

      #Determine the start time for each scan and save to list.
      scanTimeList.append(min([x.time for x in myScan]))

      #Advance to the next scan number.
      scanNr = scanNr + 1


    #Convert lists to numpy arrays.
    timeArray = np.array(scanTimeList)
    dataListArray = np.array(dataList)

    #Figure out what size arrays we need and initialize the arrays...
    nrTimes = np.max(dataListArray[:,scanInx]) + 1
    nrBeams = np.max(dataListArray[:,beamInx]) + 1
    nrGates = np.max(dataListArray[:,gateInx]) + 1

    #Make sure the FOV is the same size as the data array.
    if len(fov.beams) != nrBeams:
      fov.beams         = fov.beams[0:nrBeams]
      fov.latCenter     = fov.latCenter[0:nrBeams,:]
      fov.lonCenter     = fov.lonCenter[0:nrBeams,:]
      fov.slantRCenter  = fov.slantRCenter[0:nrBeams,:]
      fov.latFull       = fov.latFull[0:nrBeams+1,:]
      fov.lonFull       = fov.lonFull[0:nrBeams+1,:]
      fov.slantRFull    = fov.slantRFull[0:nrBeams+1,:]

    if len(fov.gates) != nrGates:
      fov.gates         = fov.gates[0:nrGates]
      fov.latCenter     = fov.latCenter[:,0:nrGates]
      fov.lonCenter     = fov.lonCenter[:,0:nrGates]
      fov.slantRCenter  = fov.slantRCenter[:,0:nrGates]
      fov.latFull       = fov.latFull[:,0:nrGates+1]
      fov.lonFull       = fov.lonFull[:,0:nrGates+1]
      fov.slantRFull    = fov.slantRFull[:,0:nrGates+1]

    #Convert the dataListArray into a 3 dimensional array.
    dataArray     = np.ndarray([nrTimes,nrBeams,nrGates])
    dataArray[:]  = np.nan
    for inx in range(len(dataListArray)):
      dataArray[dataListArray[inx,scanInx],dataListArray[inx,beamInx],dataListArray[inx,gateInx]] = dataListArray[inx,dataInx]
  
    #Make metadata block to hold information about the processing.
    metadata = {}
    metadata['dType']     = myPtr.dType
    metadata['stid']      = myPtr.stid
    metadata['name']      = radStruct.name
    metadata['code']      = radStruct.code
    metadata['fType']     = myPtr.fType
    metadata['cp']        = myPtr.cp
    metadata['channel']   = myPtr.channel
    metadata['sTime']     = sTime
    metadata['eTime']     = eTime
    metadata['param']     = param
    metadata['gscat']     = gscat
    metadata['elevation'] = fovElevation
    metadata['model']     = fovModel
    metadata['coords']    = fovCoords

    #Save data to be returned as self.variables
    self.originalFit = musicDataObj(timeArray,dataArray,fov=fov,parent=self,comment='Original Fit Data')
    self.originalFit.metadata = metadata

    #Set the new data active.
    self.originalFit.setActive()

def beamInterpolation(dataObj,dataSet='active',newDataSetName='beamInterpolated',comment='Beam Linear Interpolation'):
  """Interpolates the data in a vtMUSIC object along the beams of the radar.  This method will ensure that no
  rangegates are missing data.  Ranges outside of metadata['gateLimits'] will be set to 0.

  **Args**:
      * **dataObj**:  vtMUSIC object
      * **dataSet**:  which dataSet in the vtMUSIC object to process
      * **comment**: String to be appended to the history of this object
      * **newSigName**: String name of the attribute of the newly created signal.
  """
  from scipy.interpolate import interp1d
  currentData = getattr(dataObj,dataSet)

  nrTimes = len(currentData.time)
  nrBeams = len(currentData.fov.beams)
  nrGates = len(currentData.fov.gates)

  interpArr = np.zeros([nrTimes,nrBeams,nrGates])
  for tt in range(nrTimes):
    for bb in range(nrBeams):
      rangeVec  = currentData.fov.slantRCenter[bb,:]
      input_x   = copy.copy(rangeVec)
      input_y   = currentData.data[tt,bb,:]

      #If metadata['gateLimits'], select only those measurements...
      if currentData.metadata.has_key('gateLimits'):
        limits = currentData.metadata['gateLimits']
        gateInx = np.where(np.logical_and(currentData.fov.gates >= limits[0],currentData.fov.gates <= limits[1]))[0]

        if len(gateInx) < 2: continue
        input_x   = input_x[gateInx]
        input_y   = input_y[gateInx]

      good      = np.where(np.isfinite(input_y))[0]
      if len(good) < 2: continue
      input_x   = input_x[good]
      input_y   = input_y[good]

      intFn     = interp1d(input_x,input_y,bounds_error=False,fill_value=0)
      interpArr[tt,bb,:] = intFn(rangeVec)
  newDataSet = currentData.copy(newDataSetName,comment)
  newDataSet.data = interpArr
  newDataSet.setActive()

def defineLimits(dataObj,dataSet='active',rangeLimits=None,gateLimits=None,beamLimits=None,timeLimits=None):
  """Sets the range, gate, beam, and time limits for the chosen data set. This method only changes metadata;
  it does not create a new data set or alter the data in any way.  If you specify rangeLimits, they will be changed to correspond
  with the center value of the range cell.  Gate limits always override range limits.
  Use the applyLimits() method to remove data outside of the data limits.

  :param dataObj: vtMUSIC object
  :param dataSet: which dataSet in the vtMUSIC object to process
  :param rangeLimits: Two-element array defining the maximum and minumum slant ranges to use. [km]
  :param gateLimits: Two-element array defining the maximum and minumum gates to use.
  :param beamLimits: Two-element array defining the maximum and minumum beams to use.
  :param timeLimits: Two-element array of datetime.datetime objects defining the maximum and minumum times to use.
  :param newSigName: String name of the attribute of the newly created signal.
  """
  currentData = getattr(dataObj,dataSet)
  try:
    if (rangeLimits != None) or (gateLimits != None):
      if (rangeLimits != None) and (gateLimits == None):
        inx = np.where(np.logical_and(currentData.fov.slantRCenter >= rangeLimits[0],currentData.fov.slantRCenter <= rangeLimits[1]))
        gateLimits = [np.min(inx[1][:]),np.max(inx[1][:])]

      if gateLimits != None:
        rangeMin = np.int(np.min(currentData.fov.slantRCenter[:,gateLimits[0]]))
        rangeMax = np.int(np.max(currentData.fov.slantRCenter[:,gateLimits[1]]))
        rangeLimits = [rangeMin,rangeMax]

      currentData.metadata['gateLimits']  = gateLimits
      currentData.metadata['rangeLimits'] = rangeLimits

    if beamLimits != None:
      currentData.metadata['beamLimits'] = beamLimits

    if timeLimits != None:
      currentData.metadata['timeLimits'] = timeLimits

  except:
    print "Warning!  An error occured while defining limits.  No limits set.  Check your input values."

def applyLimits(dataObj,dataSet='active',rangeLimits=None,gateLimits=None,newDataSetName='limitsApplied',comment='Limits Applied'):
  """Removes data outside of the rangeLimits and gateLimits boundaries.

  :param dataObj: vtMUSIC object
  :param dataSet: which dataSet in the vtMUSIC object to process
  :param rangeLimits: Two-element array defining the maximum and minumum slant ranges to use. [km]
  :param gateLimits: Two-element array defining the maximum and minumum gates to use.
  :param newSigName: String name of the attribute of the newly created signal.
  """

  if (rangeLimits != None) or (gateLimits != None):
    define_limits(dataObj,dataSet='active',rangeLimits=rangeLimits,gateLimits=gateLimits)

  try:
    #Make a copy of the current data set.
    currentData = getattr(dataObj,dataSet)
    newData     = currentData.copy(newDataSetName,comment)

    commentList = []

    #Apply the gateLimits
    if currentData.metadata.has_key('gateLimits'):
      limits      = currentData.metadata['gateLimits']
      gateInx     = np.where(np.logical_and(currentData.fov.gates >= limits[0],currentData.fov.gates<= limits[1]))[0]

      newData.data = newData.data[:,:,gateInx]
      newData.fov.gates = newData.fov.gates[gateInx]

      newData.fov.latCenter     = newData.fov.latCenter[:,gateInx] 
      newData.fov.lonCenter     = newData.fov.lonCenter[:,gateInx] 
      newData.fov.slantRCenter  = newData.fov.slantRCenter[:,gateInx] 

      #Update the full FOV.
      #This works as long as we look at only consecutive gates.  If we ever do something where we are not looking at consecutive gates
      #(typically for computational speed reasons), we will have to do something else.
      gateInxFull = np.append(gateInx,gateInx[-1]+1) #We need that extra gate since this is the full FOV.
      newData.fov.latFull = newData.fov.latFull[:,gateInxFull] 
      newData.fov.lonFull = newData.fov.lonFull[:,gateInxFull] 
      newData.fov.slantRFull = newData.fov.slantRFull[:,gateInxFull] 

      commentList.append('gate: %i,%i' % tuple(limits))
      rangeLim = (np.min(newData.fov.slantRCenter), np.max(newData.fov.slantRCenter))
      commentList.append('range [km]: %i,%i' % rangeLim)

      #Remove limiting item from metadata.
      newData.metadata.pop('gateLimits')
      if newData.metadata.has_key('rangeLimits'): newData.metadata.pop('rangeLimits')
      
    #Apply the beamLimits.
    if currentData.metadata.has_key('beamLimits'):
      limits      = currentData.metadata['beamLimits']
      beamInx     = np.where(np.logical_and(currentData.fov.beams >= limits[0],currentData.fov.beams <= limits[1]))[0]

      newData.data = newData.data[:,beamInx,:]
      newData.fov.beams = newData.fov.beams[beamInx]

      newData.fov.latCenter     = newData.fov.latCenter[beamInx,:] 
      newData.fov.lonCenter     = newData.fov.lonCenter[beamInx,:] 
      newData.fov.slantRCenter  = newData.fov.slantRCenter[beamInx,:] 

      #Update the full FOV.
      #This works as long as we look at only consecutive gates.  If we ever do something where we are not looking at consecutive gates
      #(typically for computational speed reasons), we will have to do something else.
      beamInxFull = np.append(beamInx,beamInx[-1]+1) #We need that extra beam since this is the full FOV.
      newData.fov.latFull = newData.fov.latFull[beamInxFull,:] 
      newData.fov.lonFull = newData.fov.lonFull[beamInxFull,:] 
      newData.fov.slantRFull = newData.fov.slantRFull[beamInxFull,:] 

      commentList.append('beam: %i,%i' % tuple(limits))
      #Remove limiting item from metadata.
      newData.metadata.pop('beamLimits')
    
    #Apply the time limits.
    if currentData.metadata.has_key('timeLimits'):
      limits      = currentData.metadata['timeLimits']
      timeInx     = np.where(np.logical_and(currentData.time >= limits[0],currentData.time <= limits[1]))[0]

      newData.data = newData.data[timeInx,:,:]
      newData.time = newData.time[timeInx]

      commentList.append('time: '+limits[0].strftime('%Y-%m-%d/%H:%M,')+limits[1].strftime('%Y-%m-%d/%H:%M'))
      #Remove limiting item from metadata.
      newData.metadata.pop('timeLimits')
    
    #Update the history with what limits were applied.
    if commentList != []:
      commentStr = comment+': '+'; '.join(commentList)
      key = max(newData.history.keys())
      newData.history[key] = commentStr

    newData.setActive()
    return newData
  except:
    if hasattr(dataObj,newDataSetName): delattr(dataObj,newDataSetName)
    print 'Warning! Limits not applied.'
    return None

def determine_relative_position(dataObj,dataSet='active',altitude=250.):
  """Finds the center cell of the field-of-view of a vtMUSIC data object.
  The range, azimuth, x-range, and y-range from the center to each cell in the FOV
  is calculated and saved to the FOV object. The following objects are added to
  dataObj.dataSet:
    fov.relative_centerInx: [beam, gate] index of the center cell
    fov.relative_azm:       Azimuth relative to center cell [deg]
    fov.relative_range:     Range relative to center cell [km]
    fov.relative_x:         X-range relative to center cell [km]
    fov.relative_y:         Y-range relative to center cell [km]

  **Args**:
      * **dataObj**:  vtMUSIC object
      * **dataSet**:  name of dataSet to use
      * **altitude**: altitude added to Re = 6378.1 km [km]
  **Returns**:
      * **None**:  None.
  """
  import utils

  #Get the chosen dataset.
  currentData = getattr(dataObj,dataSet)

  #Determine center beam.
  ctrBeamInx  = len(currentData.fov.beams)/2
  ctrGateInx  = len(currentData.fov.gates)/2

  currentData.fov.relative_centerInx = [ctrBeamInx, ctrGateInx]

  #Set arrays of lat1/lon1 to the center cell value.  Use this to calculate all other positions
  #with numpy array math.
  lat1 = np.zeros_like(currentData.fov.latCenter)   
  lon1 = np.zeros_like(currentData.fov.latCenter)   

  lat1[:] = currentData.fov.latCenter[ctrBeamInx,ctrGateInx]
  lon1[:] = currentData.fov.lonCenter[ctrBeamInx,ctrGateInx]

  #Make lat2/lon2 the center position array of the dataset.
  lat2    = currentData.fov.latCenter
  lon2    = currentData.fov.lonCenter

  #Calculate the azimuth and distance from the centerpoint to the endpoint.
  azm     = utils.greatCircleAzm(lat1,lon1,lat2,lon2)
  dist    = (Re + altitude)*utils.greatCircleDist(lat1,lon1,lat2,lon2)

  #Save calculated values to the current data object, as well as calculate the
  #X and Y relatvie positions of each cell.
  currentData.fov.relative_azm    = azm
  currentData.fov.relative_range  = dist
  currentData.fov.relative_x      = dist * np.sin(np.radians(azm)) 
  currentData.fov.relative_y      = dist * np.cos(np.radians(azm)) 

  return None

def timeInterpolation(dataObj,dataSet='active',newDataSetName='timeInterpolated',comment='Time Linear Interpolation',timeRes=10,newTimeVec=None):
  """Interpolates the data in a vtMUSIC object to a regular time grid.

  **Args**:
      * **dataObj**:    vtMUSIC object
      * **dataSet**:    which dataSet in the vtMUSIC object to process
      * **comment**:    String to be appended to the history of this object
      * **newSigName**: String name of the attribute of the newly created signal.
      * **timeRes**:    time resolution of new time vector [seconds]
      * **newTimeVec**: Sequence of datetime.datetime objects that data will be interpolated to.  This overides timeRes.
  """
  from scipy.interpolate import interp1d
  import utils 
  currentData = getattr(dataObj,dataSet)

  sTime = currentData.time[0]
  sTime = datetime.datetime(sTime.year,sTime.month,sTime.day,sTime.hour,sTime.minute) #Make start time a round time.
  fTime = currentData.time[-1]

  #Create new time vector.
  if newTimeVec == None:
    newTimeVec = [sTime]
    while newTimeVec[-1] < fTime:
      newTimeVec.append(newTimeVec[-1] + datetime.timedelta(seconds=timeRes))

  #Ensure that the new time vector is within the bounds of the actual data set.
  newTimeVec  = np.array(newTimeVec)
  good        = np.where(np.logical_and(newTimeVec > min(currentData.time),newTimeVec < max(currentData.time)))
  newTimeVec  = newTimeVec[good]
  newEpochVec = utils.datetimeToEpoch(newTimeVec)

  #Initialize interpolated data.
  nrTimes = len(newTimeVec)
  nrBeams = len(currentData.fov.beams)
  nrGates = len(currentData.fov.gates)

  interpArr = np.zeros([nrTimes,nrBeams,nrGates])

  for rg in range(nrGates):
    for bb in range(nrBeams):
      input_x   = currentData.time[:]
      input_y   = currentData.data[:,bb,rg]

      good      = np.where(np.isfinite(input_y))[0]
      if len(good) < 2: continue
      input_x   = input_x[good]
      input_y   = input_y[good]

      input_x   = toUnixEpochTime(input_x)

      intFn     = interp1d(input_x,input_y,bounds_error=False)#,fill_value=0)
      interpArr[:,bb,rg] = intFn(newEpochVec)
  newDataSet = currentData.copy(newDataSetName,comment)
  newDataSet.time = newTimeVec
  newDataSet.data = interpArr
  newDataSet.setActive()

class filter(object):
  def __init__(self, vtsig, numtaps=None, cutoff_low=None, cutoff_high=None, width=None, window='blackman', pass_zero=True, scale=True,newSigName='filtered'):
    """Filter a VT sig/sigStruct object and define a FIR filter object.
    If only cutoff_low is defined, this is a high pass filter.
    If only cutoff_high is defined, this is a low pass filter.
    If both cutoff_low and cutoff_high is defined, this is a band pass filter.

    Uses scipy.signal.firwin()
    High pass and band pass filters inspired by Matti Pastell's page:
      http://mpastell.com/2010/01/18/fir-with-scipy/

    Metadata keys:
      'filter_cutoff_low' --> cutoff_low
      'filter_cutoff_high' --> cutoff_high
      'filter_cutoff_numtaps' --> cutoff_numtaps

    numtaps : int
      Length of the filter (number of coefficients, i.e. the filter
      order + 1).  `numtaps` must be even if a passband includes the
      Nyquist frequency.

    cutoff_low: float or 1D array_like
        High pass cutoff frequency of filter (expressed in the same units as `nyq`)
        OR an array of cutoff frequencies (that is, band edges). In the
        latter case, the frequencies in `cutoff` should be positive and
        monotonically increasing between 0 and `nyq`.  The values 0 and
        `nyq` must not be included in `cutoff`.

    cutoff_high: float or 1D array_like
        Like cutoff_low, but this is the low pass cutoff frequency of the filter.

    width : float or None
        If `width` is not None, then assume it is the approximate width
        of the transition region (expressed in the same units as `nyq`)
        for use in Kaiser FIR filter design.  In this case, the `window`
        argument is ignored.

    window : string or tuple of string and parameter values
        Desired window to use. See `scipy.signal.get_window` for a list
        of windows and required parameters.

    pass_zero : bool
        If True, the gain at the frequency 0 (i.e. the "DC gain") is 1.
        Otherwise the DC gain is 0.

    scale : bool
        Set to True to scale the coefficients so that the frequency
        response is exactly unity at a certain frequency.
        That frequency is either:
                  0 (DC) if the first passband starts at 0 (i.e. pass_zero is True);
                  `nyq` (the Nyquist rate) if the first passband ends at
                      `nyq` (i.e the filter is a single band highpass filter);
                  center of first passband otherwise.

    nyq : float
        Nyquist frequency.  Each frequency in `cutoff` must be between 0
        and `nyq`.

    :returns: filter object
    """
    
    sigObj = prepForProc(vtsig)
    nyq = sigObj.nyquistFrequency()

    #Get metadata for cutoffs and numtaps.
    md = sigObj.getAllMetaData()
    if cutoff_high == None:
      if md.has_key('filter_cutoff_high'):
        cutoff_high = md['filter_cutoff_high']

    if cutoff_low == None:
      if md.has_key('filter_cutoff_low'):
        cutoff_low = md['filter_cutoff_low']

    if numtaps == None:
      if md.has_key('filter_numtaps'):
        numtaps = md['filter_numtaps']
      else:
        print 'WARNING: You must provide numtaps.'
        return


    if   cutoff_high != None:    #Low pass
      lp = sp.signal.firwin(numtaps=numtaps, cutoff=cutoff_high, width=width, window=window, pass_zero=pass_zero, scale=scale, nyq=nyq)
      d = lp

    if   cutoff_low != None:    #High pass
      hp = -sp.signal.firwin(numtaps=numtaps, cutoff=cutoff_low, width=width, window=window, pass_zero=pass_zero, scale=scale, nyq=nyq)
      hp[numtaps/2] = hp[numtaps/2] + 1
      d = hp

    if cutoff_high != None and cutoff_low != None:
      d = -(lp+hp)
      d[numtaps/2] = d[numtaps/2] + 1

    if cutoff_high == None and cutoff_low == None:
      print "WARNING!! You must define cutoff frequencies!"
      return
    
    self.comment = ' '.join(['Filter:',window+',','Nyquist:',str(nyq),'Hz,','Cuttoff:','['+str(cutoff_low)+', '+str(cutoff_high)+']','Hz'])
    self.nyq = nyq
    self.ir = d

    self.filter(sigObj,newSigName=newSigName)


  def __str__(self):
    return self.comment

  def plotTransferFunction(self,xmin=0,xmax=None,ymin_mag=-150,ymax_mag=5,ymin_phase=None,ymax_phase=None,worN=None):
      """Plot the frequency and phase response of the filter object.

      :param xmin: Minimum value for x-axis.
      :param xmax: Maximum value for x-axis.
      :param ymin_mag: Minimum value for y-axis for the frequency response plot.
      :param ymax_mag: Maximum value for y-axis for the frequency response plot.
      :param ymin_phase: Minimum value for y-axis for the phase response plot.
      :param ymax_phase: Maximum value for y-axis for the phase response plot.
      :param worN: worN : {None, int}, optional
          passed to scipy.signal.freqz()
          If None, then compute at 512 frequencies around the unit circle.
          If the len(filter) > 512, then compute at len(filter) frequencies around the unit circle.
          If a single integer, the compute at that many frequencies.
          Otherwise, compute the response at frequencies given in worN
      """
      if worN == None:
        if len(self.ir) > 512: worN = len(self.ir)
        else: worN = None
      else: pass

      w,h = sp.signal.freqz(self.ir,1,worN=worN)
      h_dB = 20 * np.log10(abs(h))
      mp.subplot(211)
    
      #Compute frequency vector.
      w = w/max(w) * self.nyq
      mp.plot(w,h_dB,'.-')
      #mp.axvline(x=self.fMax,color='r',ls='--',lw=2)

      if xmin is not None: mp.xlim(xmin=xmin)
      if xmax is not None: mp.xlim(xmax=xmax)
      if ymin_mag is not None: mp.ylim(ymin=ymin_mag)
      if ymax_mag is not None: mp.ylim(ymax=ymax_mag)

      mp.ylabel('Magnitude (db)')
      mp.xlabel(r'Frequency (Hz)')

      mp.title(r'Frequency response')
      mp.subplot(212)
      h_Phase = np.unwrap(np.arctan2(np.imag(h),np.real(h)))
      mp.plot(w,h_Phase,'.-')

      if xmin is not None: mp.xlim(xmin=xmin)
      if xmax is not None: mp.xlim(xmax=xmax)
      if ymin_phase is not None: mp.ylim(ymin=ymin_phase)
      if ymax_phase is not None: mp.ylim(ymax=ymax_phase)

      mp.ylabel('Phase (radians)')
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

  def filter(self,vtsig,newSigName='filtered'):
      """Apply the filter to a vtsig object.

      :param vtsig: vtsig object
      :param xmax: Maximum value for x-axis.
      :param ymin_imp: Minimum value for y-axis for the impulse response plot.
      :param ymax_imp: Maximum value for y-axis for the impulse response plot.
      :param ymin_step: Minimum value for y-axis for the step response plot.
      :param ymax_step: Maximum value for y-axis for the step response plot.
      """
      
      sigobj = prepForProc(vtsig)
      vtsig  = sigobj.parent

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
      newsigobj = sigobj.copy(newSigName,self.comment)
      #Put in the filtered data.
      newsigobj.data = copy.copy(filt_data)
      newsigobj.dtv = copy.copy(sigobj.dtv)

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
        newsigobj.metadata[key] = ' '.join(['Filtered',newsigobj.metadata[key]])
      elif vtsig.metadata.has_key(key):
        newsigobj.metadata[key] = ' '.join(['Filtered',vtsig.metadata[key]])
      else:
        newsigobj.metadata[key] = 'Filtered'

      setattr(vtsig,'active',newsigobj)
