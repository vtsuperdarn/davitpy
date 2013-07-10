import numpy as np
import datetime 
import copy

import pydarn

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
  def __init__(self, time, data, fov=None, beamVec=None, gateVec=None, comment=None, parent=0, **metadata):
    self.parent = parent
    """Define a vtMUSIC sigStruct object.

    :param time: datetime.datetime list
    :param data: 3-dimensional array of data
    :param fov:  DaViTPy radar field of view object
    :param beamVec: Vector explicitly identifying the beams used in the data array
    :param gateVec: Vector explicitly identifying the gates used in the data array
    :param comment: String to be appended to the history of this object
    :param **metadata: keywords sent to matplot lib, etc.
    :returns: sig object
    """

    self.time     = np.array(time)
    self.data     = np.array(data)

    dims          = np.shape(self.data)
    if beamVec == None:
      beamVec = np.arange(dims[1])
    if gateVec == None:
      gateVec = np.arange(dims[2])

    self.fov      = fov
    self.beamVec  = beamVec
    self.gateVec  = gateVec
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
    newsigobj.beamVec   = copy.deepcopy(self.beamVec)
    newsigobj.gateVec   = copy.deepcopy(self.gateVec)
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

    #Create vectors explicitly identifying the beam and gate numbers.
    beamVec = np.arange(nrBeams)
    gateVec = np.arange(nrGates)

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
    self.originalFit = musicDataObj(timeArray,dataArray,fov=fov,parent=self,beamVec=beamVec,gateVec=gateVec,comment='Original Fit Data')
    self.originalFit.metadata = metadata

    #Set the new data active.
    self.originalFit.setActive()

def beam_interpolation(dataObj,dataSet='active',newDataSetName='beamInterpolated',comment='Beam Linear Interpolation'):
  """Interpolates the data in a vtMUSIC object along the beams of the radar.  This method will ensure that no
  rangegates are missing data.  Ranges outside of metadata['gateLimits'] will be set to 0.

  :param dataObj: vtMUSIC object
  :param dataSet: which dataSet in the vtMUSIC object to process
  :param comment: String to be appended to the history of this object
  :param newSigName: String name of the attribute of the newly created signal.
  """
  from scipy.interpolate import interp1d
  currentData = getattr(dataObj,dataSet)

  nrTimes = len(currentData.time)
  nrBeams = len(currentData.beamVec)
  nrGates = len(currentData.gateVec)

  interpArr = np.zeros([nrTimes,nrBeams,nrGates])
  for tt in range(nrTimes):
    for bb in range(nrBeams):
      rangeVec  = currentData.fov.slantRCenter[currentData.beamVec[bb],currentData.gateVec]
      input_x   = copy.copy(rangeVec)
      input_y   = currentData.data[tt,bb,:]

      #If metadata['gateLimits'], select only those measurements...
      if currentData.metadata.has_key('gateLimits'):
        limits = currentData.metadata['gateLimits']
        gateInx = np.where(np.logical_and(currentData.gateVec >= limits[0],currentData.gateVec <= limits[1]))[0]

        if len(gateInx) < 2: continue
        input_x   = input_x[gateInx]
        input_y   = input_y[gateInx]

      good      = np.where(np.isfinite(input_y))[0]
      if len(good) < 2: continue
      input_x   = input_x[good]
      input_y   = input_y[good]

      intFn     = interp1d(input_x,input_y,bounds_error=False,fill_value=0)
      interpArr[tt,bb,:] = intFn(rangeVec)
  currentData.copy(newDataSetName,comment)
  dataObj.beamInterpolated.data = interpArr
  dataObj.beamInterpolated.setActive()

def define_limits(dataObj,dataSet='active',rangeLimits=None,gateLimits=None):
  """Sets the rangeLimits and gateLimits metadata for the chosen data set. This method only changes metadata;
  it does not create a new data set or alter the data in any way.  If you specify rangeLimits, they will be changed to correspond
  with the center value of the range cell.  Gate limits always override range limits.
  Use the apply_limits() method to remove data outside of the data limits.

  :param dataObj: vtMUSIC object
  :param dataSet: which dataSet in the vtMUSIC object to process
  :param rangeLimits: Two-element array defining the maximum and minumum slant ranges to use. [km]
  :param gateLimits: Two-element array defining the maximum and minumum gates to use.
  :param newSigName: String name of the attribute of the newly created signal.
  """
  currentData = getattr(dataObj,dataSet)
  try:
    if (rangeLimits == None) and (gateLimits == None):
      pass
    #I was thinking of having this remove the limits if they are both set to None, but then I thought I might be using this function
    #in the future to define time limits, too.  The, I would want to be able to set time limits without altering the spatial limits
    #and vice-versa.  So, I'm just going to have this function leave everything alone.  I may create an explicit way to remove limits later.
#      if currentData.metadata.has_key('gateLimits'):  currentData.metadata.pop('gateLimits')
#      if currentData.metadata.has_key('rangeLimits'): currentData.metadata.pop('rangeLimits')
    else:
      if (rangeLimits != None) and (gateLimits == None):
        inx = np.where(np.logical_and(currentData.fov.slantRCenter >= rangeLimits[0],currentData.fov.slantRCenter <= rangeLimits[1]))
        gateLimits = [np.min(inx[1][:]),np.max(inx[1][:])]

      if gateLimits != None:
        rangeMin = np.int(np.min(currentData.fov.slantRCenter[:,gateLimits[0]]))
        rangeMax = np.int(np.max(currentData.fov.slantRCenter[:,gateLimits[1]]))
        rangeLimits = [rangeMin,rangeMax]

      currentData.metadata['gateLimits']  = gateLimits
      currentData.metadata['rangeLimits'] = rangeLimits
  except:
    print "Warning!  An error occured while defining limits.  No limits set.  Check your input values."
