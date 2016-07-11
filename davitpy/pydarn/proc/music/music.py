# -*- coding: utf-8 -*-
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

"""music processing module

A module for running the MUltiple SIgnal Classification (MUSIC) algorithm for the detection of
MSTIDs and wave-like structures in SuperDARN data.

For usage examples, please see the iPython notebooks included in the docs folder of the DaViTPy distribution.

References
----------
See Samson et al. [1990] and Bristow et al. [1994] for details regarding the MUSIC algorithm and SuperDARN-observed MSTIDs.

Bristow, W. A., R. A. Greenwald, and J. C. Samson (1994), Identification of high-latitude acoustic gravity wave sources
    using the Goose Bay HF Radar, J. Geophys. Res., 99(A1), 319-331, doi:10.1029/93JA01470.

Samson, J. C., R. A. Greenwald, J. M. Ruohoniemi, A. Frey, and K. B. Baker (1990), Goose Bay radar observations of Earth-reflected,
    atmospheric gravity waves in the high-latitude ionosphere, J. Geophys. Res., 95(A6), 7693-7709, doi:10.1029/JA095iA06p07693.

Module author:: Nathaniel A. Frissell, Fall 2013

Functions
--------------------------------------------------------------------------------------------------------------------------
getDataSet                  get music data object from music array object
stringify_signal            convert dictionary to a string
stringify_signal_list       convert list of dictionaries into strings
beamInterpolation           interpolate music array object along beams
defineLimits                set limits for chosen data set
checkDataQuality            mark data as bad base on radar operations
applyLimits                 remove data outside of limits
determineRelativePosition   find center of cell in music array object
timeInterpolation           interpolate music array object along time
filterTimes                 calculate time range for data set
detrend                     linear detrend of music array/data object
nan_to_num                  convert undefined numbers to finite numbers
windowData                  apply window to music array object
calculateFFT                calculate spectrum of an object
calculateDlm                calculate the cross-spectral matrix of a musicArray/musicDataObj object.
calculateKarr               calculate the two-dimensional horizontal wavenumber array of a musicArray/musicDataObj object.
simulator                   insert a simulated MSTID into the processing chain.
scale_karr                  scale/normalize kArr for plotting and signal detection.
detectSignals               detect local maxima of signals
add_signal                  add signal to detected signal list
del_signal                  remove signal from detected signal list
--------------------------------------------------------------------------------------------------------------------------

Classes
-----------------------------------------------------------
emptyObj        create an empty object
SigDetect       information about detected signals
musicDataObj    basic container for holding MUSIC data.
musicArray      container object for holding musicDataObj's
filter          a filter object for VT sig/siStruct objects
-----------------------------------------------------------

"""
import numpy as np
import datetime 
import time
import copy
import logging

Re = 6378   #Earth radius

def getDataSet(dataObj,dataSet='active'):
    """Returns a specified musicDataObj from a musicArray object.  If the musicArray object has the exact attribute
    specified in the dataSet keyword, then that attribute is returned.  If not, all attributes of the musicArray object
    will be searched for attributes which contain the string specified in the dataSet keyword.  If more than one are
    found, the last attribute of a sorted list will be returned.  If no attributes are found which contain the specified
    string, the 'active' dataSet is returned.

    Parameters
    ----------
    dataObj :  musicArray

    dataSet :  Optional[str]
        which dataSet in the musicArray object to process

    Returns
    -------
    currentData : musicDataObj object

    Written by Nathaniel A. Frissell, Fall 2013

    """
    lst = dir(dataObj)
    if dataSet not in lst:
        tmp = []
        for item in lst:
            if dataSet in item:
                tmp.append(item)
        if len(tmp) == 0:
            dataSet = 'active'
        else:
            tmp.sort()
            dataSet = tmp[-1]

    currentData = getattr(dataObj,dataSet)
    return currentData

class emptyObj(object):
    """Create an empty object.
    """
    def __init__(self):
        pass

def stringify_signal(sig):
    """Method to convert a signal information dictionary into a string.

    Parameters
    ----------
    sig : dict
        Information about a detected signal.

    Returns
    -------
    sigInfo : str
        String representation of the signal information.

    Written by Nathaniel A. Frissell, Fall 2013
    """
    sigInfo = {}
    if sig.has_key('order'):
        sigInfo['order']    = '%d' % sig['order']                   #Order of signals by strength as detected by image detection algorithm
    if sig.has_key('kx'):
        sigInfo['kx']       = '%.5f' % sig['kx']
    if sig.has_key('ky'):
        sigInfo['ky']       = '%.5f' % sig['ky']
    if sig.has_key('k'):
        sigInfo['k']        = '%.3f' % sig['k']
    if sig.has_key('lambda'):
        if np.isinf(sig['lambda']):
            sigInfo['lambda'] = 'inf'
        else:
            sigInfo['lambda'] = '%d' % np.round(sig['lambda'])      # km
    if sig.has_key('lambda_x'):
        if np.isinf(sig['lambda_x']):
            sigInfo['lambda_x'] = 'inf'
        else:
            sigInfo['lambda_x'] = '%d' % np.round(sig['lambda_x'])      # km
    if sig.has_key('lambda_y'):
        if np.isinf(sig['lambda_y']):
            sigInfo['lambda_y'] = 'inf'
        else:
            sigInfo['lambda_y'] = '%d' % np.round(sig['lambda_y'])      # km
    if sig.has_key('azm'):
        sigInfo['azm']      = '%d' % np.round(sig['azm'])           # degrees
    if sig.has_key('freq'):
        sigInfo['freq']     = '%.2f' % (sig['freq']*1000.)          # mHz
    if sig.has_key('period'):
        sigInfo['period']   = '%d' % np.round(sig['period']/60.)    # minutes
    if sig.has_key('vel'):
        if np.isinf(np.round(sig['vel'])):
            sigInfo['vel']      = 'Inf'
        else:
            sigInfo['vel']      = '%d' % np.round(sig['vel'])           # km/s
    if sig.has_key('area'):
        sigInfo['area']     = '%d' % sig['area']                    # Pixels
    if sig.has_key('max'):
        sigInfo['max']      = '%.4f' % sig['max']                   # Value from kArr in arbitrary units, probably with some normalization
    if sig.has_key('maxpos'):
        sigInfo['maxpos']   = str(sig['maxpos'])                    # Index position in kArr of maximum value.
    if sig.has_key('labelInx'):
        sigInfo['labelInx'] = '%d' % sig['labelInx']                # Label value from image processing
    if sig.has_key('serialNr'):
        sigInfo['serialNr'] = '%d' % sig['serialNr']                # Label value from image processing

    return sigInfo

def stringify_signal_list(signal_list,sort_key='order'):
    """Method to convert a list of signal dictionaries into strings.

    Parameters
    ----------
    signal_list : list of dict
        Information about a detected signal.
    sort_key : Optional[string]
        Dictionary key to sort on, or None for no sort. 'order' will sort the signal list
        from strongest signal to weakest, as determined by the MUSIC algorithm.

    Returns
    -------
    stringInfo : list of str
        String representation of the signal information.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    string_info = []

    if sort_key is not None:
        orders  = [x[sort_key] for x in signal_list]
        orders.sort()

        for order in orders:
            for sig in signal_list:
                if sig[sort_key] == order:
                    string_info.append(stringify_signal(sig))
                    signal_list.remove(sig)
    else:
        for sig in signal_list:
            string_info.append(stringify_signal(sig))

    return string_info

class SigDetect(object):
    """Class to hold information about detected signals.

    Methods
    -------
    string
    reorder

    Written by Nathaniel A. Frissell, Fall 2013
    """
    def __init__(self):
        pass
    def string(self):
        """Method to convert a list of signal dictionaries into strings.

        Returns
        -------
        stringInfo : list of str
            String representation of the signal information.

        Written by Nathaniel A. Frissell, Fall 2013
        """
        return stringify_signal_list(self.info)
    def reorder(self):
        """Method to sort items in .info by signal maximum value (from the scaled kArr) and update nrSignals.

        Written by Nathaniel A. Frissell, Fall 2013
        """
        #Do the sorting...
        from operator import itemgetter
        newlist = sorted(self.info,key=itemgetter('max'),reverse=True)

        #Put in the order numbers...
        order = 1
        for item in newlist:
            item['order'] = order
            order = order + 1

        #Save the list to the dataObj...
        self.info = newlist

        #Update the nrSigs
        self.nrSigs = len(newlist)

class musicDataObj(object):
    """This class is the basic container for holding MUSIC data.

    Parameters
    ---------- 
    time : list of datetime.datetime
        list of times corresponding to data
    data : numpy.array
        3-dimensional array of data
    fov : Optional[pydarn.radar.radFov.fov]
        Radar field-of-view object.
    comment : Optional[str]
        String to be appended to the history of this object
    parent : Optional[musicArray]
        reference to parent musicArray object
    **metadata
        keywords sent to matplot lib, etc.

    Attributes
    ----------
    time : numpy.array of datetime.datetime
        numpy array of times corresponding to data
    data : numpy.array
        3-dimensional array of data
    fov : Optional[pydarn.radar.radFov.fov]
        Radar field-of-view object.
    metadata : dict
        keywords sent to matplot lib, etc.
    history : dict 

    Methods
    ---------
    copy
    setActive
    nyquistFrequency
    samplePeriod
    applyLimits
    setMetadata
    printMetadata
    appendHistory
    printHistory

    Written by Nathaniel A. Frissell, Fall 2013
    """

    def __init__(self, time, data, fov=None, comment=None, parent=0, **metadata):
        self.parent = parent

        self.time     = np.array(time)
        self.data     = np.array(data)
        self.fov      = fov
        self.metadata = {}
        for key in metadata: self.metadata[key] = metadata[key]

        self.history = {datetime.datetime.now():comment}

    def copy(self,newsig,comment):
        """Copy a musicDataObj object.  This deep copies data and metadata, updates the serial
        number, and logs a comment in the history.  Methods such as plot are kept as a reference.

        Parameters
        ----------
        newsig : str
            Name for the new musicDataObj object.
        comment : str
            Comment describing the new musicDataObj object.

        Returns
        -------
        newsigobj : musicDataObj
            Copy of the original musicDataObj with new name and history entry.

        Written by Nathaniel A. Frissell, Fall 2013
        """

        serial = self.metadata['serial'] + 1
        newsig = '_'.join(['DS%03d' % serial,newsig])

        setattr(self.parent,newsig,copy.copy(self))
        newsigobj = getattr(self.parent,newsig)

        newsigobj.time      = copy.deepcopy(self.time)
        newsigobj.data      = copy.deepcopy(self.data)
        newsigobj.fov       = copy.deepcopy(self.fov)
        newsigobj.metadata  = copy.deepcopy(self.metadata)
        newsigobj.history   = copy.deepcopy(self.history)

        newsigobj.metadata['dataSetName'] = newsig
        newsigobj.metadata['serial']      = serial
        newsigobj.history[datetime.datetime.now()] = '['+newsig+'] '+comment
        
        return newsigobj
  
    def setActive(self):
        """Sets this signal as the currently active signal.

        Written by Nathaniel A. Frissell, Fall 2013
        """
        self.parent.active = self

    def nyquistFrequency(self,timeVec=None):
        """Calculate the Nyquist frequency of a vt sigStruct signal.

        Parameters
        ----------
        timeVec : Optional[list of datetime.datetime]
            List of datetime.datetime to use instead of self.time.

        Returns
        -------
        nq : float
            Nyquist frequency of the signal in Hz.

        Written by Nathaniel A. Frissell, Fall 2013
        """

        dt  = self.samplePeriod(timeVec=timeVec)
        nyq = float(1. / (2*dt))
        return nyq

    def samplePeriod(self,timeVec=None):
        """Calculate the sample period of a vt sigStruct signal.

        Parameters
        ----------
        timeVec : Optional[list of datetime.datetime]
            List of datetime.datetime to use instead of self.time.

        Returns
        -------
        samplePeriod : float
            samplePeriod: sample period of signal in seconds.

        Written by Nathaniel A. Frissell, Fall 2013
        """
        
        if timeVec  == None: timeVec = self.time

        diffs       = np.diff(timeVec)
        diffs_unq   = np.unique(diffs)
        self.diffs  = diffs_unq

        if len(diffs_unq) == 1:
            samplePeriod = diffs[0].total_seconds()
        else:
            diffs_sec   = np.array([x.total_seconds() for x in diffs])
            maxDt       = np.max(diffs_sec)
            avg         = np.mean(diffs_sec)

            md          = self.metadata
            warn        = 'WARNING'
            if md.has_key('title'): warn = ' '.join([warn,'FOR','"'+md['title']+'"'])
            logging.warning(warn + ':')
            logging.warning('   Date time vector is not regularly sampled!')
            logging.warning('   Maximum difference in sampling rates is ' + str(maxDt) + ' sec.')
            logging.warning('   Using average sampling period of ' + str(avg) + ' sec.')
            samplePeriod = avg
            import ipdb; ipdb.set_trace()

        return samplePeriod

    def applyLimits(self,rangeLimits=None,gateLimits=None,timeLimits=None,newDataSetName='limitsApplied',comment='Limits Applied'):
        """Removes data outside of the rangeLimits, gateLimits, and timeLimits boundaries.

        Parameters
        ----------
        rangeLimits : Optional[interable]
            Two-element array defining the maximum and minumum slant ranges to use. [km]
        gateLimits : Optional[iterable]
            Two-element array defining the maximum and minumum gates to use.
        timeLimits :  Optional[]

        newDataSetName : Optional[str]
            Name of the new musicDataObj to be created in the current musicArray object as a result of this processing.
        comment : Optional[str]
            String to be appended to the history of this object.

        Returns
        -------
        newMusicDataObj : musicDataObj
            New musicDataObj.  The musicDataObj is also stored in it's parent musicArray object.

        Written by Nathaniel A. Frissell, Fall 2013
        """
        return applyLimits(self.parent,self.metadata['dataSetName'],rangeLimits=rangeLimits,gateLimits=gateLimits,timeLimits=timeLimits,newDataSetName=newDataSetName,comment=comment)

    def setMetadata(self,**metadata):
        """Adds information to the current musicDataObj's metadata dictionary.
        Metadata affects various plotting parameters and signal processing routinges.

        Parameters
        ----------
        **metadata :
            keywords sent to matplot lib, etc.

        Written by Nathaniel A. Frissell, Fall 2013
        """
        self.metadata = dict(self.metadata.items() + metadata.items())

    def printMetadata(self):
        """Nicely print all of the metadata associated with the current musicDataObj object.

        Written by Nathaniel A. Frissell, Fall 2013
        """
        keys = self.metadata.keys()
        keys.sort()
        for key in keys:
            print key+':',self.metadata[key]

    def appendHistory(self,comment):
        """Add an entry to the processing history dictionary of the current musicDataObj object.

        Parameters
        ----------
        comment : string
            Infomation to add to history dictionary.

        Written by Nathaniel A. Frissell, Fall 2013
        """
        self.history[datetime.datetime.now()] = '['+self.metadata['dataSetName']+'] '+comment

    def printHistory(self):
        """Nicely print all of the processing history associated with the current musicDataObj object.

        Written by Nathaniel A. Frissell, Fall 2013
        """
        keys = self.history.keys()
        keys.sort()
        for key in keys:
            print key,self.history[key]


    
class musicArray(object):
    """This class is the basic container for holding MUSIC data.

    Parameters
    ----------
    myPtr : pydarn.sdio.radDataTypes.radDataPtr
        contains the pipeline to the data we are after
    sTime : Optional[datetime.datetime]
        start time UT (if None myPtr.sTime is used)
    eTime : Optional[datetime.datetime]
        end time UT (if None myPtr.eTime is used)
    param : Optional[str]
        Radar FIT parameter to load and process.  Any appropriate attribute of the
        FIT data structure is allowed.
    gscat : Optional[int]
        Ground scatter flag.
            0: all backscatter data 
            1: ground backscatter only
            2: ionospheric backscatter only
            3: all backscatter data with a ground backscatter flag.
    fovElevation : Optional[float]
        Passed directly to pydarn.radar.radFov.fov()
    fovModel : Optional[str]
        Scatter mapping model.
            'GS': Ground Scatter Mapping Model.  See Bristow et al. [1994]
            'IS': Standard SuperDARN scatter mapping model.
    fovCoords : Optional[str]
        Map coordinate system. WARNING: 'geo' is curently only tested coordinate system.
    full_array : Optional[bool]
        If True, make the data array the full beam, gate dimensions listed in the hdw.dat file.
        If False, truncate the array to the maximum dimensions that there is actually data.
        False will save space without throwing out any data, but sometimes it is easier to work
        with the full-size array.

    Attributes
    ----------
    messages : list

    prm : 

    Methods
    -------
    get_data_sets

    Example
    -------
        #Set basic event parameters.
        rad         ='wal'
        sTime       = datetime.datetime(2011,5,9,8,0)
        eTime       = datetime.datetime(2011,5,9,19,0)
        #Connect to a SuperDARN data source.
        myPtr       = pydarn.sdio.radDataOpen(sTime,rad,eTime=eTime)
        #Create the musicArray Object.
        dataObj     = music.musicArray(myPtr,fovModel='GS')

    References
    ----------
    Bristow, W. A., R. A. Greenwald, and J. C. Samson (1994), Identification of high-latitude acoustic gravity wave sources
        using the Goose Bay HF Radar, J. Geophys. Res., 99(A1), 319-331, doi:10.1029/93JA01470.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    def __init__(self,myPtr,sTime=None,eTime=None,param='p_l',gscat=1,
            fovElevation=None,fovModel='GS',fovCoords='geo',full_array=False):
        from davitpy import pydarn
        # Create a list that can be used to store top-level messages.
        self.messages   = []

        no_data_message = 'No data for this time period.'
        # If no data, report and return.
        if myPtr is None:
            self.messages.append(no_data_message)
            return

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

        beamTime    = sTime
        scanNr      = np.uint64(0)
        fov         = None


        # Create a place to store the prm data.
        prm             = emptyObj()
        prm.time        = []
        prm.mplgs       = []
        prm.nave        = []
        prm.noisesearch = []
        prm.scan        = []
        prm.smsep       = []
        prm.mplgexs     = []
        prm.xcf         = []
        prm.noisesky    = []
        prm.rsep        = []
        prm.mppul       = []
        prm.inttsc      = []
        prm.frang       = []
        prm.bmazm       = []
        prm.lagfr       = []
        prm.ifmode      = []
        prm.noisemean   = []
        prm.tfreq       = []
        prm.inttus      = []
        prm.rxrise      = []
        prm.mpinc       = []
        prm.nrang       = []

        while beamTime < eTime:
            #Load one scan into memory.
#            myScan = pydarn.sdio.radDataRead.radDataReadScan(myPtr)
            myScan  = myPtr.readScan()
            if myScan == None: break

            goodScan = False # This flag turns to True as soon as good data is found for the scan.
            for myBeam in myScan:
                #Calculate the field of view if it has not yet been calculated.
                if fov == None:
                    radStruct = pydarn.radar.radStruct.radar(radId=myPtr.stid)
                    site      = pydarn.radar.radStruct.site(radId=myPtr.stid,dt=sTime)
                    fov       = pydarn.radar.radFov.fov(frang=myBeam.prm.frang, rsep=myBeam.prm.rsep, site=site,elevation=fovElevation,model=fovModel,coords=fovCoords)

                #Get information from each beam in the scan.
                beamTime = myBeam.time 
                bmnum    = myBeam.bmnum

                # Save all of the radar operational parameters.
                prm.time.append(beamTime)
                prm.mplgs.append(myBeam.prm.mplgs)
                prm.nave.append(myBeam.prm.nave)
                prm.noisesearch.append(myBeam.prm.noisesearch)
                prm.scan.append(myBeam.prm.scan)
                prm.smsep.append(myBeam.prm.smsep)
                prm.mplgexs.append(myBeam.prm.mplgexs)
                prm.xcf.append(myBeam.prm.xcf)
                prm.noisesky.append(myBeam.prm.noisesky)
                prm.rsep.append(myBeam.prm.rsep)
                prm.mppul.append(myBeam.prm.mppul)
                prm.inttsc.append(myBeam.prm.inttsc)
                prm.frang.append(myBeam.prm.frang)
                prm.bmazm.append(myBeam.prm.bmazm)
                prm.lagfr.append(myBeam.prm.lagfr)
                prm.ifmode.append(myBeam.prm.ifmode)
                prm.noisemean.append(myBeam.prm.noisemean)
                prm.tfreq.append(myBeam.prm.tfreq)
                prm.inttus.append(myBeam.prm.inttus)
                prm.rxrise.append(myBeam.prm.rxrise)
                prm.mpinc.append(myBeam.prm.mpinc)
                prm.nrang.append(myBeam.prm.nrang)

                #Get the fitData.
                fitDataList = getattr(myBeam.fit,param)
                slist       = getattr(myBeam.fit,'slist')
                gflag       = getattr(myBeam.fit,'gflg')

                if len(slist) > 1:
                    for (gate,data,flag) in zip(slist,fitDataList,gflag):
                        #Get information from each gate in scan.  Skip record if the chosen ground scatter option is not met.
                        if (gscat == 1) and (flag == 0): continue
                        if (gscat == 2) and (flag == 1): continue
                        tmp = (scanNr,beamTime,bmnum,gate,data)
                        dataList.append(tmp)
                        goodScan = True
                elif len(slist) == 1:
                    gate,data,flag = (slist[0],fitDataList[0],gflag[0])
                    #Get information from each gate in scan.  Skip record if the chosen ground scatter option is not met.
                    if (gscat == 1) and (flag == 0): continue
                    if (gscat == 2) and (flag == 1): continue
                    tmp = (scanNr,beamTime,bmnum,gate,data)
                    dataList.append(tmp)
                    goodScan = True
                else:
                    continue

            if goodScan:
                #Determine the start time for each scan and save to list.
                scanTimeList.append(min([x.time for x in myScan]))

                #Advance to the next scan number.
                scanNr = scanNr + 1

        #Convert lists to numpy arrays.
        timeArray       = np.array(scanTimeList)
        dataListArray   = np.array(dataList)

        # If no data, report and return.
        if dataListArray.size == 0:
            self.messages.append(no_data_message)
            return

        #Figure out what size arrays we need and initialize the arrays...
        nrTimes = int(np.max(dataListArray[:,scanInx]) + 1)

        if full_array:
            nrBeams = int(fov.beams.max() + 1)
            nrGates = int(fov.gates.max() + 1)
        else:
            nrBeams = int(np.max(dataListArray[:,beamInx]) + 1)
            nrGates = int(np.max(dataListArray[:,gateInx]) + 1)

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
            dataArray[int(dataListArray[inx,scanInx]),int(dataListArray[inx,beamInx]),int(dataListArray[inx,gateInx])] = dataListArray[inx,dataInx]

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

        dataSet = 'DS000_originalFit'
        metadata['dataSetName'] = dataSet
        metadata['serial']      = 0
        comment = '['+dataSet+'] '+ 'Original Fit Data'
        #Save data to be returned as self.variables
        setattr(self,dataSet,musicDataObj(timeArray,dataArray,fov=fov,parent=self,comment=comment))
        newSigObj = getattr(self,dataSet)
        setattr(newSigObj,'metadata',metadata)

        #Set the new data active.
        newSigObj.setActive()

        #Make prm data part of the object.
        self.prm = prm

    def get_data_sets(self):
        """Return a sorted list of musicDataObj's contained in this musicArray.

        Returns
        -------
        dataSets : list of str
            Names of musicDataObj's contained in this musicArray.

        Written by Nathaniel A. Frissell, Fall 2013
        """

        attrs = dir(self)

        dataSets = []
        for item in attrs:
            if item.startswith('DS'):
                dataSets.append(item)
        dataSets.sort()
        return dataSets

def beamInterpolation(dataObj,dataSet='active',newDataSetName='beamInterpolated',comment='Beam Linear Interpolation'):
    """Interpolates the data in a musicArray object along the beams of the radar.  This method will ensure that no
    rangegates are missing data.  Ranges outside of metadata['gateLimits'] will be set to 0.
    The result is stored as a new musicDataObj in the given musicArray object.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    newDataSetName : Optional[str]
        Name of the new musicDataObj to be created in the current musicArray object as a result of this processing.
    comment : Optional[str]
        String to be appended to the history of this object.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    from scipy.interpolate import interp1d
    currentData = getDataSet(dataObj,dataSet)

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

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    rangeLimits : Optional[iterable]
        Two-element array defining the maximum and minumum slant ranges to use. [km]
    gateLimits : Optional[iterable]
        Two-element array defining the maximum and minumum gates to use.
    beamLimits : Optional[iterable]
        Two-element array defining the maximum and minumum beams to use.
    timeLimits : Optional[iterable]
        Two-element array of datetime.datetime objects defining the maximum and minumum times to use.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    currentData = getDataSet(dataObj,dataSet)
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
        logging.warning("An error occured while defining limits.  No limits set.  Check your input values.")

def checkDataQuality(dataObj,dataSet='active',max_off_time=10,sTime=None,eTime=None):
    """Mark the data set as bad (metadata['good_period'] = False) if the radar was not operational within the chosen time period
    for a specified length of time.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    max_off_time : Optional[int/float]
        Maximum length in minutes radar may remain off.
    sTime : Optional[datetime.datetime]
        Starting time of checking period.  If None, min(currentData.time) is used.
    eTime : Optional[datetime.datetime]
        End time of checking period.  If None, max(currentData.time) is used.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    currentData = getDataSet(dataObj,dataSet)

    if sTime is None:
        sTime   = np.min(currentData.time)

    if eTime is None:
        eTime   = np.max(currentData.time)

    time_vec    = currentData.time[np.logical_and(currentData.time > sTime, currentData.time < eTime)]
    time_vec    = np.concatenate(([sTime],time_vec,[eTime]))
    max_diff    = np.max(np.diff(time_vec))

    if max_diff > datetime.timedelta(minutes=max_off_time):
        currentData.setMetadata(good_period=False)
    else:
        currentData.setMetadata(good_period=True)

    return dataObj

def applyLimits(dataObj,dataSet='active',rangeLimits=None,gateLimits=None,timeLimits=None,newDataSetName='limitsApplied',comment=None):
    """Removes data outside of the rangeLimits and gateLimits boundaries.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    rangeLimits : Optional[iterable]
        Two-element array defining the maximum and minumum slant ranges to use. [km]
    gateLimits : Optional[iterable]
        Two-element array defining the maximum and minumum gates to use.
    beamLimits : Optional[iterable]
        Two-element array defining the maximum and minumum beams to use.
    timeLimits : Optional[iterable]
        Two-element array of datetime.datetime objects defining the maximum and minumum times to use.
    newDataSetName : Optional[str]
        Name of the new musicDataObj to be created in the current musicArray object as a result of this processing.
    comment : Optional[str]
        String to be appended to the history of this object.  Set to None for the Default comment (recommended).

    Returns
    -------
    newData : musicDataObj
        Processed version of input musicDataObj (if succeeded), or the original musicDataObj (if failed).

    Written by Nathaniel A. Frissell, Fall 2013
    """

    if (rangeLimits != None) or (gateLimits != None) or (timeLimits != None):
        defineLimits(dataObj,dataSet='active',rangeLimits=rangeLimits,gateLimits=gateLimits,timeLimits=timeLimits)

    currentData = getDataSet(dataObj,dataSet)
    try:
        #Make a copy of the current data set.

        commentList = []

        if (currentData.metadata.has_key('timeLimits') == False and 
            currentData.metadata.has_key('beamLimits') == False and 
            currentData.metadata.has_key('gateLimits') == False):
            return currentData

        newData     = currentData.copy(newDataSetName,comment)
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
            comment = 'Limits Applied'
            commentStr = '['+newData.metadata['dataSetName']+'] '+comment+': '+'; '.join(commentList)
            key = max(newData.history.keys())
            newData.history[key] = commentStr
            logging.debug(commentStr)

        newData.setActive()
        return newData
    except:
        if hasattr(dataObj,newDataSetName): delattr(dataObj,newDataSetName)
#        print 'Warning! Limits not applied.'
        return currentData

def determineRelativePosition(dataObj,dataSet='active',altitude=250.):
    """Finds the center cell of the field-of-view of a musicArray data object.
    The range, azimuth, x-range, and y-range from the center to each cell in the FOV
    is calculated and saved to the FOV object. The following objects are added to
    dataObj.dataSet:
      fov.relative_centerInx: [beam, gate] index of the center cell
      fov.relative_azm:       Azimuth relative to center cell [deg]
      fov.relative_range:     Range relative to center cell [km]
      fov.relative_x:         X-range relative to center cell [km]
      fov.relative_y:         Y-range relative to center cell [km]

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    altitude : Optional[float]
        altitude added to Re = 6378.1 km [km]

    Returns
    -------
    None

    Written by Nathaniel A. Frissell, Fall 2013

    """
    from davitpy import utils

    #Get the chosen dataset.
    currentData = getDataSet(dataObj,dataSet)

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
    """Interpolates the data in a musicArray object to a regular time grid.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    newDataSetName : Optional[str]
        Name of the new musicDataObj to be created in the current musicArray object as a result of this processing.
    comment : Optional[str]
        String to be appended to the history of this object.
    timeRes : Optional[float]
        time resolution of new time vector [seconds]
    newTimeVec : Optional[list of datetime.datetime]
        Sequence of datetime.datetime objects that data will be interpolated to.  This overides timeRes.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    from scipy.interpolate import interp1d
    from davitpy import utils 
    currentData = getDataSet(dataObj,dataSet)

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

            input_x   = utils.datetimeToEpoch(input_x)

            intFn     = interp1d(input_x,input_y,bounds_error=False)#,fill_value=0)
            interpArr[:,bb,rg] = intFn(newEpochVec)
    newDataSet = currentData.copy(newDataSetName,comment)
    newDataSet.time = newTimeVec
    newDataSet.data = interpArr
    newDataSet.setActive()

def filterTimes(sTime,eTime,timeRes,numTaps):
    """The linear filter is going to cause a delay in the signal and also won't get to the end of the signal.
    This function will calcuate the full time period of data that needs to be loaded in order to provide filtered data
    for the event requested.

    Parameters
    ----------
    sTime : datetime.datetime
        Start time of event.
    eTime : datetime.datetime
        End time of event.
    timeRes : float
        Time resolution in seconds of data to be sent to filter.
    numtaps : int
        Length of the filter 

    Returns
    -------
    newSTime, newETime : datetime.datetime, datetime.datetime
        Start and end times of data that needs to be fed into the filter.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    td = datetime.timedelta(seconds=(numTaps*timeRes/2.))
    newSTime = sTime - td
    newETime = eTime + td
    return (newSTime, newETime)

class filter(object):
    """Filter a VT sig/sigStruct object and define a FIR filter object.
    If only cutoff_low is defined, this is a high pass filter.
    If only cutoff_high is defined, this is a low pass filter.
    If both cutoff_low and cutoff_high is defined, this is a band pass filter.

    Uses scipy.signal.firwin()
    High pass and band pass filters inspired by Matti Pastell's page:
      http://mpastell.com/2010/01/18/fir-with-scipy/

    Metadata keys:
      'filter_cutoff_low'   --> cutoff_low
      'filter_cutoff_high'  --> cutoff_high
      'filter_numtaps'      --> cutoff_numtaps

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    numtaps : Optional[int]
        Length of the filter (number of coefficients, i.e. the filter
        order + 1).  `numtaps` must be even if a passband includes the
        Nyquist frequency.

        If dataObj.dataSet.metadata['filter_numptaps'] is set and this keyword is None,
        the metadata value will be used.

    cutoff_low : Optional[float, 1D array_like or None]
        High pass cutoff frequency of filter (expressed in the same units as `nyq`)
        OR an array of cutoff frequencies (that is, band edges). In the
        latter case, the frequencies in `cutoff` should be positive and
        monotonically increasing between 0 and `nyq`.  The values 0 and
        `nyq` must not be included in `cutoff`. If None, a low-pass filter will not
        be applied.

        If dataObj.dataSet.metadata['filter_cutoff_low'] is set and this keyword is None,
        the metadata value will be used.

    cutoff_high : Optional[float, 1D array_like, or None]
        Like cutoff_low, but this is the low pass cutoff frequency of the filter.

        If dataObj.dataSet.metadata['filter_cutoff_high'] is set and this keyword is None,
        the metadata value will be used.

    width : Optional[float]
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
            0 (DC) if the first passband starts at 0 (i.e. pass_zero is True);
            nyq` (the Nyquist rate) if the first passband ends at
            `nyq` (i.e the filter is a single band highpass filter);
            center of first passband otherwise.

    Attributes
    ----------
    comment : str

    cutoff_low : float, 1D array_like or None
        High pass cutoff frequency of filter (expressed in the same units as `nyq`)
        OR an array of cutoff frequencies (that is, band edges).
    cutoff_high : float, 1D array_like, or None
        Like cutoff_low, but this is the low pass cutoff frequency of the filter.
    nyq : float
        the Nyquist rate
    ir : 

    Methods
    -------
    plotTransferFunction
    plotImpulseResponse
    filter

    Written by Nathaniel A. Frissell, Fall 2013

    """
    def __init__(self, dataObj, dataSet='active', numtaps=None, cutoff_low=None, cutoff_high=None, width=None, window='blackman', pass_zero=True, scale=True,newDataSetName='filtered'):
        import scipy as sp
        
        sigObj = getattr(dataObj,dataSet)
        nyq = sigObj.nyquistFrequency()

        #Get metadata for cutoffs and numtaps.
        md = sigObj.metadata
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
                logging.warning('You must provide numtaps.')
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
            d = -1.*d #Needed to correct 180 deg phase shift.

        if cutoff_high == None and cutoff_low == None:
            logging.warning("You must define cutoff frequencies!")
            return
    
        self.comment = ' '.join(['Filter:',window+',','Nyquist:',str(nyq),'Hz,','Cuttoff:','['+str(cutoff_low)+', '+str(cutoff_high)+']','Hz,','Numtaps:',str(numtaps)])
        self.cutoff_low   = cutoff_low
        self.cutoff_high  = cutoff_high
        self.nyq = nyq
        self.ir = d

        self.filter(dataObj,dataSet=dataSet,newDataSetName=newDataSetName)


    def __str__(self):
        return self.comment

    def plotTransferFunction(self,xmin=0,xmax=None,ymin_mag=-150,ymax_mag=5,ymin_phase=None,ymax_phase=None,worN=None,fig=None):
        import scipy as sp
        """Plot the frequency and phase response of the filter object.

        Parameters
        ----------
        xmin : Optional[float]
            Minimum value for x-axis.
        xmax : Optional[float]
            Maximum value for x-axis.
        ymin_mag : Optional[float]
            Minimum value for y-axis for the frequency response plot.
        ymax_mag : Optional[float]
            Maximum value for y-axis for the frequency response plot.
        ymin_phase : Optional[float]
            Minimum value for y-axis for the phase response plot.
        ymax_phase : Optional[float]
            Maximum value for y-axis for the phase response plot.
        worN : Optional[int]
            passed to scipy.signal.freqz()
            If None, then compute at 512 frequencies around the unit circle.
            If the len(filter) > 512, then compute at len(filter) frequencies around the unit circle.
            If a single integer, the compute at that many frequencies.
            Otherwise, compute the response at frequencies given in worN
        fig : Optional[matplotlib.Figure]
            Figure object on which to plot.  If None, a figure will be created.

        Returns
        -------
        fig : matplotlib.Figure
            Figure object containing the plot.

        Written by Nathaniel A. Frissell, Fall 2013
        """

        if fig == None:
            from matplotlib import pyplot as plt
            fig   = plt.figure(figsize=(20,10))

        if worN == None:
            if len(self.ir) > 512: worN = len(self.ir)
            else: worN = None
        else: pass

        w,h = sp.signal.freqz(self.ir,1,worN=worN)
        h_dB = 20 * np.log10(abs(h))
        axis = fig.add_subplot(211)

        #Compute frequency vector.
        w = w/max(w) * self.nyq
        axis.plot(w,h_dB,'.-')
        #mp.axvline(x=self.fMax,color='r',ls='--',lw=2)

        if xmin is not None: axis.set_xlim(xmin=xmin)
        if xmax is not None: axis.set_xlim(xmax=xmax)
        if ymin_mag is not None: axis.set_ylim(ymin=ymin_mag)
        if ymax_mag is not None: axis.set_ylim(ymax=ymax_mag)

        axis.set_xlabel(r'Frequency (Hz)')
        axis.set_ylabel('Magnitude (db)')

        axis.set_title(r'Frequency response')

        axis = fig.add_subplot(212)
        h_Phase = np.unwrap(np.arctan2(np.imag(h),np.real(h)))
        axis.plot(w,h_Phase,'.-')

        if xmin is not None: axis.set_xlim(xmin=xmin)
        if xmax is not None: axis.set_xlim(xmax=xmax)
        if ymin_phase is not None: axis.set_ylim(ymin=ymin_phase)
        if ymax_phase is not None: axis.set_ylim(ymax=ymax_phase)

        axis.set_ylabel('Phase (radians)')
        axis.set_xlabel(r'Frequency (Hz)')
        axis.set_title(r'Phase response')
        fig.suptitle(self.comment)
        fig.subplots_adjust(hspace=0.5)

        return fig

    def plotImpulseResponse(self,xmin=None,xmax=None,ymin_imp=None,ymax_imp=None,ymin_step=None,ymax_step=None,fig=None):
        import scipy as sp
        """Plot the frequency and phase response of the filter object.

        Parameters
        ----------
        xmin : Optional[float]
            Minimum value for x-axis.
        xmax : Optional[float]
            Maximum value for x-axis.
        ymin_imp : Optional[float]
            Minimum value for y-axis for the impulse response plot.
        ymax_imp : Optional[float]
            Maximum value for y-axis for the impulse response plot.
        ymin_step : Optional[float]
            Minimum value for y-axis for the step response plot.
        ymax_step : Optional[float]
            Maximum value for y-axis for the step response plot.
        fig : Optional[matplotlib.Figure]
            Figure object on which to plot.  If None, a figure will be created.

        Returns
        -------
        fig : matplotlib.Figure
            Figure object containing the plot.

        Written by Nathaniel A. Frissell, Fall 2013
        """

        if fig == None:
            from matplotlib import pyplot as plt
            fig   = plt.figure(figsize=(20,10))

        l = len(self.ir)
        impulse = np.repeat(0.,l); impulse[0] =1.
        x = np.arange(0,l)
        response = sp.signal.lfilter(self.ir,1,impulse)
        axis = fig.add_subplot(211)
        axis.stem(x, response)
        axis.set_ylabel('Amplitude')
        axis.set_xlabel(r'n (samples)')
        axis.set_title(r'Impulse response')

        axis = fig.add_subplot(212)
        step = np.cumsum(response)
        axis.stem(x, step)
        axis.set_ylabel('Amplitude')
        axis.set_xlabel(r'n (samples)')
        axis.set_title(r'Step response')
        fig.suptitle(self.comment)
        fig.subplots_adjust(hspace=0.5)

        return fig

    def filter(self,dataObj,dataSet='active',newDataSetName='filtered'):
        """Apply the filter to a vtsig object.

        Parameters
        ----------
        dataObj : musicArray
            musicArray object
        dataSet : Optional[str]
            which dataSet in the musicArray object to process
        newDataSetName : Optional[str]
            Name of the new musicDataObj to be created in the current musicArray object as a result of this processing.

        Written by Nathaniel A. Frissell, Fall 2013

        """
        import scipy as sp

        sigobj = getattr(dataObj,dataSet)
        vtsig  = sigobj.parent

        nrTimes,nrBeams,nrGates = np.shape(sigobj.data)

        #Filter causes a delay in the signal and also doesn't get the tail end of the signal...  Shift signal around, provide info about where the signal is valid.
        shift = np.int32(-np.floor(len(self.ir)/2.))

        start_line    = np.zeros(nrTimes)
        start_line[0] = 1
        start_line    = np.roll(start_line,shift)

        tinx0 = abs(shift)
        tinx1 = np.where(start_line == 1)[0][0]

        val_tm0 = sigobj.time[tinx0]
        val_tm1 = sigobj.time[tinx1]

        filteredData = np.zeros_like(sigobj.data)

        #Apply filter
        for bm in range(nrBeams):
            for rg in range(nrGates):
                tmp = sp.signal.lfilter(self.ir,[1.0],sigobj.data[:,bm,rg])
                tmp = np.roll(tmp,shift)
                filteredData[:,bm,rg] = tmp[:]

        #Create new signal object.
        newsigobj = sigobj.copy(newDataSetName,self.comment)
        #Put in the filtered data.
        newsigobj.data = copy.copy(filteredData)
        newsigobj.time = copy.copy(sigobj.time)

        #Clear out ymin and ymax from metadata; make sure meta data block exists.
        #If not, create it.

        if hasattr(newsigobj,'metadata'):
            delMeta = ['ymin','ymax','ylim']
            for key in delMeta:
                if newsigobj.metadata.has_key(key):
                    del newsigobj.metadata[key]
        else:
            newsigobj.metadata = {}

        newsigobj.metadata['timeLimits'] = (val_tm0,val_tm1)

        key = 'title'
        if newsigobj.metadata.has_key(key):
            newsigobj.metadata[key] = ' '.join(['Filtered',newsigobj.metadata[key]])
        else:
            newsigobj.metadata[key] = 'Filtered'

        newsigobj.metadata['fir_filter'] = (self.cutoff_low,self.cutoff_high)
        newsigobj.setActive()

def detrend(dataObj,dataSet='active',newDataSetName='detrended',comment=None,type='linear'):
    """Linearly detrend a data in a musicArray/musicDataObj object.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    newDataSetName : Optional[str]
        Name of the new musicDataObj to be created in the current musicArray object as a result of this processing.
    comment : Optional[str]
        String to be appended to the history of this object.  Set to None for the Default comment (recommended).
    type : Optional[str]
        The type of detrending. If type == 'linear' (default), the result of a linear least-squares fit to data
        is subtracted from data. If type == 'constant', only the mean of data is subtracted.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    import scipy as sp

    currentData = getDataSet(dataObj,dataSet)
    currentData = currentData.applyLimits()

    nrTimes, nrBeams, nrGates = np.shape(currentData.data)

    newDataArr= np.zeros_like(currentData.data)
    for bm in range(nrBeams):
        for rg in range(nrGates):
            try:
                newDataArr[:,bm,rg] = sp.signal.detrend(currentData.data[:,bm,rg],type=type)
            except:
                newDataArr[:,bm,rg] = np.nan
  
    if comment == None:
        comment = type.capitalize() + ' detrend (scipy.signal.detrend)'
      
    newDataSet      = currentData.copy(newDataSetName,comment)
    newDataSet.data = newDataArr
    newDataSet.setActive()

def nan_to_num(dataObj,dataSet='active',newDataSetName='nan_to_num',comment=None):
    """Convert all NANs and INFs to finite numbers using numpy.nan_to_num().

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    newDataSetName : Optional[str]
        Name of the new musicDataObj to be created in the current musicArray object as a result of this processing.
    comment : Optional[str]
        String to be appended to the history of this object.  Set to None for the Default comment (recommended).

    Written by Nathaniel A. Frissell, Fall 2013

    """
    currentData = getDataSet(dataObj,dataSet)
    currentData = currentData.applyLimits()

    if comment == None:
        comment = 'numpy.nan_to_num'
      
    newDataSet      = currentData.copy(newDataSetName,comment)
    newDataSet.data = np.nan_to_num(currentData.data)
    newDataSet.setActive()

def windowData(dataObj,dataSet='active',newDataSetName='windowed',comment=None,window='hann'):
    """Apply a window to a musicArray object.  The window is calculated using scipy.signal.get_window().

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    newDataSetName : Optional[str]
        Name of the new musicDataObj to be created in the current musicArray object as a result of this processing.
    comment : Optional[str]
        String to be appended to the history of this object.  Set to None for the Default comment (recommended).
    window : Optional[str]
        boxcar, triang, blackman, hamming, hann, bartlett, flattop, parzen, bohman, blackmanharris, nuttall,
        barthann, kaiser (needs beta), gaussian (needs std), general_gaussian (needs power, width),
        slepian (needs width), chebwin (needs attenuation)

    Written by Nathaniel A. Frissell, Fall 2013

    """
    import scipy as sp

    currentData = getDataSet(dataObj,dataSet)
    currentData = currentData.applyLimits()

    nrTimes, nrBeams, nrGates = np.shape(currentData.data)

    win = sp.signal.get_window(window,nrTimes,fftbins=False)
    newDataArr= np.zeros_like(currentData.data)
    for bm in range(nrBeams):
        for rg in range(nrGates):
            newDataArr[:,bm,rg] = currentData.data[:,bm,rg] * win
  
    if comment == None:
        comment = window.capitalize() + ' window applied (scipy.signal.get_window)'
      
    newDataSet      = currentData.copy(newDataSetName,comment)
    newDataSet.data = newDataArr
    newDataSet.setActive()

def calculateFFT(dataObj,dataSet='active',comment=None):
    """Calculate the spectrum of an object.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    comment : Optional[str]
        String to be appended to the history of this object.  Set to None for the Default comment (recommended).

    Written by Nathaniel A. Frissell, Fall 2013

    """
    import scipy as sp

    currentData = getDataSet(dataObj,dataSet)
    currentData = currentData.applyLimits()

    nrTimes, nrBeams, nrGates = np.shape(currentData.data)

    #Determine frequency axis.
    nyq = currentData.nyquistFrequency()
    freq_ax = np.arange(nrTimes,dtype='f8')
    freq_ax = (freq_ax / max(freq_ax)) - 0.5
    freq_ax = freq_ax * 2. * nyq

    #Use complex64, not complex128!  If you use complex128, too much numerical noise will accumulate and the final plot will be bad!
    newDataArr= np.zeros((nrTimes,nrBeams,nrGates),dtype=np.complex64)
    for bm in range(nrBeams):
        for rg in range(nrGates):
            newDataArr[:,bm,rg] = sp.fftpack.fftshift(sp.fftpack.fft(currentData.data[:,bm,rg])) / np.size(currentData.data[:,bm,rg])
  
    currentData.freqVec   = freq_ax
    currentData.spectrum  = newDataArr

    # Calculate the dominant frequency #############################################
    posFreqInx  = np.where(currentData.freqVec >= 0)[0]
    posFreqVec  = currentData.freqVec[posFreqInx]
    npf         = len(posFreqVec) #Number of positive frequencies

    data        = np.abs(currentData.spectrum[posFreqInx,:,:]) #Use the magnitude of the positive frequency data.

    #Average Power Spectral Density
    avg_psd = np.zeros(npf)
    for x in range(npf): avg_psd[x] = np.mean(data[x,:,:])
    currentData.dominantFreq = posFreqVec[np.argmax(avg_psd)]
    currentData.appendHistory('Calculated FFT')
  
def calculateDlm(dataObj,dataSet='active',comment=None):
    """Calculate the cross-spectral matrix of a musicaArray object. FFT must already have been calculated.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    comment : Optional[str]
        String to be appended to the history of this object.  Set to None for the Default comment (recommended).

    Written by Nathaniel A. Frissell, Fall 2013

    """
    currentData = getDataSet(dataObj,dataSet)

    nrTimes, nrBeams, nrGates = np.shape(currentData.data)

    nCells                    = nrBeams * nrGates
    currentData.llLookupTable = np.zeros([5,nCells])
    currentData.Dlm           = np.zeros([nCells,nCells],dtype=np.complex128)

    #Only use positive frequencies...
    posInx = np.where(currentData.freqVec > 0)[0]

    #Explicitly write out gate/range indices...

    llList = []
    for gg in xrange(nrGates):
        for bb in xrange(nrBeams):
            llList.append((bb,gg))


    for ll in range(nCells):
        llAI  = llList[ll]
        ew_dist           = currentData.fov.relative_x[llAI]
        ns_dist           = currentData.fov.relative_y[llAI]
        currentData.llLookupTable[:,ll]  = [ll, currentData.fov.beams[llAI[0]], currentData.fov.gates[llAI[1]],ns_dist,ew_dist]
        spectL            = currentData.spectrum[posInx,llAI[0],llAI[1]]
        for mm in range(nCells):
            mmAI  = llList[mm]
            spectM          = currentData.spectrum[posInx,mmAI[0],mmAI[1]]
            currentData.Dlm[ll,mm] = np.sum(spectL * np.conj(spectM))

    currentData.appendHistory('Calculated Cross-Spectral Matrix Dlm')

def calculateKarr(dataObj,dataSet='active',kxMax=0.05,kyMax=0.05,dkx=0.001,dky=0.001,threshold=0.15):
    """Calculate the two-dimensional horizontal wavenumber array of a musicArray/musicDataObj object.
    Cross-spectrum array Dlm must already have been calculated.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    kxMax : Optional[float]
        Maximum kx (East-West) wavenumber to calculate [rad/km]
    kyMax : Optional[float]
        Maximum ky (North-South) wavenumber to calculate [rad/km]
    dkx : Optional[float]
        kx resolution [rad/km]
    dky : Optional[float]
        ky resolution [rad/km]
    threshold : Optional[float]
        threshold of signals to detect as a fraction of the maximum eigenvalue

    Written by Nathaniel A. Frissell, Fall 2013

    """
    currentData = getDataSet(dataObj,dataSet)

    nrTimes, nrBeams, nrGates = np.shape(currentData.data)

    #Calculate eigenvalues, eigenvectors
    eVals,eVecs = np.linalg.eig(np.transpose(dataObj.active.Dlm))

    nkx     = np.ceil(2*kxMax/dkx)
    if (nkx % 2) == 0: nkx = nkx+1
    kxVec  = kxMax * (2*np.arange(nkx)/(nkx-1) - 1)

    nky     = np.ceil(2*kyMax/dky)
    if (nky % 2) == 0: nky = nky+1
    kyVec  = kyMax * (2*np.arange(nky)/(nky-1) - 1)

    nkx = int(nkx)
    nky = int(nky)

    xm      = currentData.llLookupTable[4,:] #x is in the E-W direction.
    ym      = currentData.llLookupTable[3,:] #y is in the N-S direction.

    threshold   = 0.15
    maxEval     = np.max(np.abs(eVals))

    minEvalsInx = np.where(eVals <= threshold*maxEval)[0]
    cnt         = np.size(minEvalsInx)
    maxEvalsInx = np.where(eVals >  threshold*maxEval)[0]
    nSigs       = np.size(maxEvalsInx)

    if cnt < 3:
        logging.warning('Not enough small eigenvalues!')
        import ipdb; ipdb.set_trace()

    logging.info('K-Array: ' + str(nkx) + ' x ' + str(nky))
    logging.info('Kx Max: ' + str(kxMax))
    logging.info('Kx Res: ' + str(dkx))
    logging.info('Ky Max: ' + str(kyMax))
    logging.info('Ky Res: ' + str(dky))
    logging.info('')
    logging.info('Signal Threshold:      ' + str(threshold))
    logging.info('Number of Det Signals: ' + str(nSigs))
    logging.info('Number of Noise Evals: ' + str(cnt))

    logging.info('Starting kArr Calculation...')
    t0 = datetime.datetime.now()
    def vCalc(um,v):
        return np.dot( np.conj(um), v) * np.dot( np.conj(v), um)

    vList = [eVecs[:,minEvalsInx[ee]] for ee in xrange(cnt)]
    kArr  = np.zeros((nkx,nky),dtype=np.complex64)
    for kk_kx in xrange(nkx):
        kx  = kxVec[kk_kx]
        for kk_ky in xrange(nky):
            ky  = kyVec[kk_ky]
            um  = np.exp(1j*(kx*xm + ky*ym))
            kArr[kk_kx,kk_ky]= 1. / np.sum(map(lambda v: vCalc(um,v), vList))
    t1 = datetime.datetime.now()
    logging.info('Finished kArr Calculation.  Total time: ' + str(t1-t0))

    currentData.karr  = kArr
    currentData.kxVec = kxVec
    currentData.kyVec = kyVec
    currentData.appendHistory('Calculated kArr')

def simulator(dataObj, dataSet='active',newDataSetName='simulated',comment=None,keepLocalRange=True,sigs=None,noiseFactor=0):
    """Replace SuperDARN Data with simulated MSTID(s).  This is useful for understanding how the signal processing
    routines of this module affect ideal data.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    newDataSetName : Optional[str]
        Name of the new musicDataObj to be created in the current musicArray object as a result of this processing.
    comment : Optional[str]
        String to be appended to the history of this object.  Set to None for the Default comment (recommended).
    keepLocalRange : Optional[bool]
        If true, the locations calculated for the actual radar field of view will be used.  If false,
        a linearly-spaced will replace the true grid.
    sigs : Optional[list of tuples]
        A list of tuples defining the characteristics of the simulated signal.  Sample list is as follows.
        If this keyword is None, the values in this sample list are used as the default values.::

        sigs = []
            #           (amp,    kx,      ky,      f, phi, dcOffset)
            sigs.append((  5,  0.01,  -0.010, 0.0004,   0,       5.))
            sigs.append((  5, 0.022,  -0.023, 0.0004,   0,       5.))

        Each signal is evaluated as a cosine and then summed together.  The cosine evaluated is::
        sig  = amp * np.cos(kx*xgrid + ky*ygrid - 2.*np.pi*f*t + phi) + dc
    noiseFactor : Optional[float]
        Add white gaussian noise to the simulated signal.  noiseFactor is a scalar such that:
        noise             = noiseFactor*np.random.standard_normal(nSteps)

    Written by Nathaniel A. Frissell, Fall 2013

    """
    from davitpy import utils
    currentData = getDataSet(dataObj,dataSet)

    #Typical TID Parameters:
    #       Frequency:      0.0003 mHz
    #       Period:         55.5 min
    #       H. Wavelength:  314 km
    #       k:              0.02 /km

    if keepLocalRange == True:
        nx, ny  = np.shape(currentData.fov.relative_x)
        xRange  = np.max(currentData.fov.relative_x) - np.min(currentData.fov.relative_x)
        yRange  = np.max(currentData.fov.relative_y) - np.min(currentData.fov.relative_y)

        xgrid   = currentData.fov.relative_x
        ygrid   = currentData.fov.relative_y
    else:
        nx      = 16
        xRange  = 800.
        ny      = 25
        yRange  = 600.

        xvec    = np.linspace(-xRange/2.,xRange/2.,nx)
        yvec    = np.linspace(-yRange/2.,yRange/2.,ny)

        dx      = np.diff(xvec)[0]
        dy      = np.diff(yvec)[0]

        xaxis   = np.append(xvec,xvec[-1]+dx)
        yayis   = np.append(yvec,yvec[-1]+dy)

        xgrid   = np.zeros((nx,ny))
        ygrid   = np.zeros((nx,ny))

        for kk in xrange(nx): ygrid[kk,:] = yvec[:]
        for kk in xrange(ny): xgrid[kk,:] = yvec[:]

    if sigs == None:
        #Set some default signals.
        sigs = []
        #           (amp,    kx,      ky,      f, phi, dcOffset)
        sigs.append((  5,  0.01,  -0.010, 0.0004,   0,       5.))
        sigs.append((  5, 0.022,  -0.023, 0.0004,   0,       5.))
  
    secVec  = np.array(utils.datetimeToEpoch(currentData.time))
    secVec  = secVec - secVec[0]

    nSteps  = len(secVec)
    dt      = currentData.samplePeriod()

    dataArr = np.zeros((nSteps,nx,ny)) 

    for step in xrange(nSteps):
        t = secVec[step]
        for kk in xrange(len(sigs)):
            amp     = sigs[kk][0]
            kx      = sigs[kk][1]
            ky      = sigs[kk][2]
            f       = sigs[kk][3]
            phi     = sigs[kk][4]
            dc      = sigs[kk][5]

            if 1./dt <= 2.*f:
                logging.warning('Nyquist Violation in f.')
                logging.warning('Signal #: %i' % kk)

#            if 1./dx <= 2.*kx/(2.*np.pi):
#                print 'WARNING: Nyquist Violation in kx.'
#                print 'Signal #: %i' % kk
#
#            if 1./dy <= 2.*ky/(2.*np.pi):
#                print 'WARNING: Nyquist Violation in ky.'
#                print 'Signal #: %i' % kk

            temp    = amp * np.cos(kx*xgrid + ky*ygrid - 2.*np.pi*f*t + phi) + dc
            dataArr[step,:,:] = dataArr[step,:,:] + temp

    #Signal RMS
    sig_rms = np.zeros((nx,ny))
    for xx in xrange(nx):
        for yy in xrange(ny):
            sig_rms[xx,yy] = np.sqrt(np.mean((dataArr[:,xx,yy])**2.))

    noise_rms = np.zeros((nx,ny))
    if noiseFactor > 0:
        nf = noiseFactor
        #Temporal White Noise
        for xx in xrange(nx):
            for yy in xrange(ny):
                noise             = nf*np.random.standard_normal(nSteps)
                noise_rms[xx,yy]  = np.sqrt(np.mean(noise**2))
                dataArr[:,xx,yy]  = dataArr[:,xx,yy] + noise

    xx      = np.arange(ny)
    mu      = (ny-1.)/2.
    sigma2  = 10.0
    sigma   = np.sqrt(sigma2)
    rgDist  = 1./(sigma*np.sqrt(2.*np.pi)) * np.exp(-0.5 * ((xx-mu)/sigma)**2)
    rgDist  = rgDist / np.max(rgDist)

    mask    = np.zeros((nx,ny))
    for nn in xrange(nx): mask[nn,:] = rgDist[:]

    mask3d  = np.zeros((nSteps,nx,ny))
    for nn in xrange(nSteps): mask3d[nn,:,:] = mask[:]

    #Apply Range Gate Dependence
    dataArr = dataArr * mask3d

    snr     = (sig_rms/noise_rms)**2
    snr_db  = 10.*np.log10(snr)

    if comment == None:
        comment = 'Simulated data injected.'
      
    newDataSet      = currentData.copy(newDataSetName,comment)
    newDataSet.data = dataArr
    newDataSet.setActive()

    #OPENW,unit,'simstats.txt',/GET_LUN,WIDTH=300
    #stats$  = ' Mean: '   + NUMSTR(MEAN(sig_rms),3)         $
    #        + ' STDDEV: ' + NUMSTR(STDDEV(sig_rms),3)       $
    #        + ' Var: '    + NUMSTR(STDDEV(sig_rms)^2,3)
    #PRINTF,unit,'SIG_RMS'
    #PRINTF,unit,stats$
    #PRINTF,unit,sig_rms
    #
    #PRINTF,unit,''
    #PRINTF,unit,'NOISE_RMS'
    #stats$  = ' Mean: '   + NUMSTR(MEAN(noise_rms),3)         $
    #        + ' STDDEV: ' + NUMSTR(STDDEV(noise_rms),3)       $
    #        + ' Var: '    + NUMSTR(STDDEV(noise_rms)^2,3)
    #PRINTF,unit,stats$
    #PRINTF,unit,noise_rms
    #
    #PRINTF,unit,''
    #PRINTF,unit,'SNR_DB'
    #stats$  = ' Mean: '   + NUMSTR(MEAN(snr_db),3)         $
    #        + ' STDDEV: ' + NUMSTR(STDDEV(snr_db),3)       $
    #        + ' Var: '    + NUMSTR(STDDEV(snr_db)^2,3)
    #PRINTF,unit,stats$
    #PRINTF,unit,snr_db
    #CLOSE,unit

def scale_karr(kArr):
    from scipy import stats
    """Scale/normalize kArr for plotting and signal detection.
    
    Parameters
    ----------
    kArr : 2D numpy.array
        Two-dimensional horizontal wavenumber array of a musicArray/musicDataObj object.

    Returns
    -------
    data : 2D numpy.array
        Scaled and normalized version of kArr.

    Written by Nathaniel A. Frissell, Fall 2013

    """
    data        = np.abs(kArr) - np.min(np.abs(kArr))

    #Determine scale for colorbar.
    scale       = [0.,1.]
    sd          = stats.nanstd(data,axis=None)
    mean        = stats.nanmean(data,axis=None)
    scMax       = mean + 6.5*sd
    data        = data / scMax
    return data

def detectSignals(dataObj,dataSet='active',threshold=0.35,neighborhood=(10,10)):
    """Automatically detects local maxima/signals in a calculated kArr.  This routine uses the watershed
    algorithm from the skimage image processing library.  Results are automatically stored in
    dataObj.dataSet.sigDetect.

    Parameters
    ----------
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    threshold : Optional[float]
        Scaled input data must be above this value to be detected.  A higher number
        will reduce the number of signals detected.
    neighborhood : Optional[tuple]
        Local region in which to search for peaks at every point in the image/array.
        (10,10) will search a 10x10 pixel area.

    Returns
    -------
    currentData : musicDataObj
        object

    Written by Nathaniel A. Frissell, Fall 2013

    """
    currentData = getDataSet(dataObj,dataSet)
    ################################################################################
    #Feature detection...
    #Now lets do a little image processing...
    from scipy import ndimage
    from skimage.morphology import watershed
    from skimage.feature import peak_local_max

    #sudo pip install cython
    #sudo pip install scikit-image

    data = scale_karr(currentData.karr)

    mask        = data > threshold
    labels, nb  = ndimage.label(mask)

    distance    = ndimage.distance_transform_edt(mask)
    local_maxi  = peak_local_max(distance,footprint=np.ones(neighborhood),indices=False)
    markers,nb  = ndimage.label(local_maxi)
    labels      = watershed(-distance,markers,mask=mask)

    areas         = ndimage.sum(mask,labels,xrange(1,labels.max()+1))
    maxima        = ndimage.maximum(data,labels,xrange(1, labels.max()+1))
    order         = np.argsort(maxima)[::-1] + 1
    maxpos        = ndimage.maximum_position(data,labels,xrange(1, labels.max()+1))

    sigDetect = SigDetect()
    sigDetect.mask    = mask
    sigDetect.labels  = labels
    sigDetect.nrSigs  = nb
    sigDetect.info    = []
    for x in xrange(labels.max()):
        info = {}
        info['labelInx']    = x+1
        info['order']       = order[x]
        info['area']        = areas[x]
        info['max']         = maxima[x]
        info['maxpos']      = maxpos[x]
        info['kx']          = currentData.kxVec[info['maxpos'][0]]
        info['ky']          = currentData.kyVec[info['maxpos'][1]]
        info['k']           = np.sqrt( info['kx']**2 + info['ky']**2 )
        info['lambda_x']    = 2*np.pi / info['kx']
        info['lambda_y']    = 2*np.pi / info['ky']
        info['lambda']      = 2*np.pi / info['k']
        info['azm']         = np.degrees(np.arctan2(info['kx'],info['ky']))
        info['freq']        = currentData.dominantFreq
        info['period']      = 1./currentData.dominantFreq
        info['vel']         = (2.*np.pi/info['k']) * info['freq'] * 1000.
        sigDetect.info.append(info)

    currentData.appendHistory('Detected KArr Signals')
    currentData.sigDetect = sigDetect
    return currentData

def add_signal(kx,ky,dataObj,dataSet='active',frequency=None):
    """Manually add a signal to the detected signal list.  All signals will be re-ordered according to value in the 
    scaled kArr.  Added signals can be distinguished from autodetected signals because 
    'labelInx' and 'area' will both be set to -1.

    Parameters
    ----------
    kx : float
        Value of kx of new signal.
    ky : float
        Value of ky of new signal.
    dataObj : musicArray
        musicArray object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process
    frequency : Optional[float]
        Frequency to use to calculate period, phase velocity, etc.  If None, 
        the calculated dominant frequency will be used.

    Returns
    -------
    currentData : musicDataObj
        object

    Written by Nathaniel A. Frissell, Fall 2013

    """
    currentData = getDataSet(dataObj,dataSet)
    data = scale_karr(currentData.karr)

    def find_nearest_inx(array,value):
        return (np.abs(array-value)).argmin()

    kx_inx  = find_nearest_inx(currentData.kxVec,kx)
    ky_inx  = find_nearest_inx(currentData.kyVec,ky)

    maxpos      = (kx_inx,ky_inx)
    value       = data[kx_inx,ky_inx]

    true_value  = currentData.karr[kx_inx,ky_inx] #Get the unscaled kArr value.

    if frequency == None:
        freq    = currentData.dominantFreq
    else:
        freq = frequency

    info = {}
    info['labelInx']    = -1
    info['area']        = -1
    info['order']       = -1
    info['max']         = value
    info['true_max']    = true_value    #Unscaled kArr value
    info['maxpos']      = maxpos
    info['kx']          = currentData.kxVec[info['maxpos'][0]]
    info['ky']          = currentData.kyVec[info['maxpos'][1]]
    info['k']           = np.sqrt( info['kx']**2 + info['ky']**2 )
    info['lambda_x']    = 2*np.pi / info['kx']
    info['lambda_y']    = 2*np.pi / info['ky']
    info['lambda']      = 2*np.pi / info['k']
    info['azm']         = np.degrees(np.arctan2(info['kx'],info['ky']))
    info['freq']        = freq
    info['period']      = 1./freq
    info['vel']         = (2.*np.pi/info['k']) * info['freq'] * 1000.

    currentData.sigDetect.info.append(info)
    currentData.sigDetect.reorder()
    currentData.appendHistory('Appended Signal to sigDetect List')

    return currentData

def del_signal(order,dataObj,dataSet='active'):
    """Remove a signal to the detected signal list.

    Parameters
    ----------
    order :
        Single value of list of signal orders (ID's) to be removed from the list.
    dataObj : musicArray
        object
    dataSet : Optional[str]
        which dataSet in the musicArray object to process

    Returns
    -------
    currentData : musicDataObj
        object

    Written by Nathaniel A. Frissell, Fall 2013
    """

    currentData = getDataSet(dataObj,dataSet)
    data = scale_karr(currentData.karr)

    orderArr = np.array(order)

    for item in list(currentData.sigDetect.info):
        if item['order'] in orderArr:
            currentData.sigDetect.info.remove(item)

    currentData.sigDetect.reorder()
    currentData.appendHistory('Deleted Signals from sigDetect List')
    return currentData
