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
  def __init__(self, time, data, fov=None, comment=None, parent=0, **metadata):
    self.parent = parent
    """Define a vtsd sigStruct object.

    :param dtv: datetime.datetime list
    :param data: raw data
    :param id: A serial number uniquely identifying this signal in the
    : processing chain.
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
    """Copy a vtsig object.  This deep copies data and metadata, updates the serial number, and logs a comment in the history.  Methods such as plot are kept as a reference.
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

def beam_interpolation(dataObj,dataSet='active',limits=None,units='km'):
  import copy
  from scipy.interpolate import interp1d
  currentData = getattr(dataObj,dataSet)
  nrTimes,nrBeams,nrGates = np.shape(currentData.data)

  interpArr = np.zeros([nrTimes,nrBeams,nrGates])
  for tt in range(nrTimes):
    for bb in range(nrBeams):
      rangeVec  = currentData.fov.slantRCenter[bb,0:nrGates]
      dataVec   = currentData.data[tt,bb,:]
      good      = np.where(np.isfinite(dataVec))[0]
      if len(good) < 2: continue
      input_x   = rangeVec[good]
      input_y   = dataVec[good]

      #If the user specifies a limits to range or gates, select only those measurements...
      if limits != None:
        if units == 'gate':
          limits  = rangeVec[limits]
          units   = 'km'
        good    = np.where((input_x >= limits[0]) & (input_x <= limits[1]))[0]
        if len(good) < 2: continue
        input_x   = input_x[good]
        input_y   = input_y[good]

      intFn     = interp1d(input_x,input_y,bounds_error=False,fill_value=0)
      interpArr[tt,bb,:] = intFn(rangeVec)
  currentData.copy('beamInterpolated','Beam Linear Interpolation')
  dataObj.beamInterpolated.data = interpArr
  dataObj.beamInterpolated.setActive()
