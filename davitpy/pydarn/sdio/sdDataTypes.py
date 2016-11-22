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
The classes needed for reading, writing, and storing processed radar data,
such as grid and map data

.. moduleauthor:: AJ, 20130108
***************
* sdDataTypes *
***************

Classes
---------
sdDataPtr
sdBaseData
gridData
mapData
"""

import logging
from davitpy.utils import twoWayDict

alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',
         'r','s','t','u','v','w','x','y','z']

class sdDataPtr():
    """A class which contains a pipeline to a data source

    Parameters
    ----------
    sTime : datetime
        start time of the request
    hemi : str
        hemisphere of data interested in
    fileType : str
        the type of file: 'grd', 'grdex', 'map', or 'mapex'
    eTime : Optional[datetime]
        end time of the request.  If none, then a full day is
        requested.
    src : Optional[str]
        source of files: local of sftp
    fileName : Optional[str]
        name of the file opened
    noCache : Optional[bool]
        true to not use cached files, regenerate tmp files
    local_dirfmt : Optional[str]
        format of the local directory structure. Default: rcParams'
        'DAVIT_SD_LOCAL_DIRFORMAT' value.
    local_fnamefmt : Optional[str]
        format of the local filenames.  Default: rcParams'
        'DAVIT_SD_LOCAL_FNAMEFMT' value.
    local_dict : Optional[dict]
        dictionary of the hemisphere and file type. Default: use
        the values given for hemi and fileType.
    remote_dirfmt : Optional[str]
        format of the remote directory structure.  Default: rcParams'
        'DAVIT_SD_REMOTE_DIRFORMAT' value.
    remote_fnamefmt : Optional[str]
        format of the remote filenames.  Default: rcParams'
        'DAVIT_SD_REMOTE_FNAMEFMT' value.
    remote_dict : Optional[dict]
        dictionary of the hemisphere and file type. Default: use
        the values given for hemi and fileType.
    username : Optional[str]
        username to use for an sftp connection.  Default: rcParams'
        'DBREADUSER' value.
    password : Optional[str]
        password to use for an sftp connection.  Default: rcParams'
        'DBREADPASS' value.
    port : Optional[int]
        port to use for an sftp connection.  Deafult: rcParams'
        'DB_PORT' value.
    tmpdir : Optional[str]
        directory to download and source files from locally.  Default:
        rcParams' 'DAVIT_TMPDIR' value.
    

    Attributes
    -----------
    sTime : (datetime)
        start time of the request
    eTime : (datetime)
        end time of the request
    hemi : str
        hemisphere of data interested in
    fType : str
        the file type, 'grd', 'map', 'grdex' or 'mapex'
    recordIndex : (dict)
        look up dictionary for file offsets for scan times

    Private Attributes
    --------------------
    ptr : (file or mongodb query object)
        the data pointer (different depending on mongodo or dmap)
    fd : (int)
        the file descriptor 
    fileName : (str)
        name of the file opened
    nocache : (bool)
        do not use cached files, regenerate tmp files 
    src : (str)
        local or sftp 
 
    Methods
    --------
    open 
    close 
    createIndex
        Index the offsets for all records and scan boundaries
    offsetSeek
        Seek file to requested byte offset, checking to make sure it in the
        record index
    offsetTell
        Current byte offset
    rewind
        rewind file back to the beginning 
    readRec
        read record at current file offset
    readScan
        read scan associated with current record
    readAll
        read all records

    Written by AJ 20130607
    """
    def __init__(self, sTime, hemi, fileType, eTime=None, src=None,
                 fileName=None, noCache=False, local_dirfmt=None,
                 local_fnamefmt=None, local_dict=None, remote_dirfmt=None,
                 remote_fnamefmt=None, remote_dict=None, remote_site=None,
                 username=None, password=None, port=None, tmpdir=None):
#        from davitpy.pydarn.sdio import sdDataPtr
        from davitpy.utils.timeUtils import datetimeToEpoch
        import datetime as dt
        import os
        import glob
        import string
        from davitpy.pydarn.radar import network
        import davitpy.pydarn.sdio.fetchUtils as futils
        import davitpy

        self.sTime = sTime
        self.eTime = eTime
        self.hemi = hemi
        self.fType = fileType
        self.dType = None
        self.recordIndex = None
        self.__filename = fileName 
        self.__nocache  = noCache
        self.__src = src
        self.__fd = None
        self.__ptr = None

        # check inputs
        assert isinstance(self.sTime, dt.datetime), \
            logging.error('sTime must be datetime object')
        assert hemi is not None, \
            logging.error("hemi must not be None")
        assert self.eTime == None or isinstance(self.eTime, dt.datetime), \
            logging.error('eTime must be datetime object or None')
        assert(fileType == 'grd' or fileType == 'grdex' or
               fileType == 'map' or fileType == 'mapex'), \
            logging.error("fileType must be one of: grd, grdex, map, or mapex")
        assert fileName == None or isinstance(fileName, str), \
            logging.error('fileName must be None or a string')
        assert src == None or src == 'local' or src == 'sftp', \
            logging.error('src must be one of: None, local, or sftp')
    
        if self.eTime == None:
            self.eTime = self.sTime + dt.timedelta(days=1)
    
        filelist = []
        if fileType == 'grd':
            arr = ['grd', 'grdex']
        elif fileType == 'grdex':
            arr = ['grdex', 'grd']
        elif fileType == 'map':
            arr = ['map', 'mapex']
        elif fileType == 'mapex':
            arr = ['mapex', 'map']
        else:
            arr = [fileType]
    
        # a temporary directory to store a temporary file
        if tmpdir is None:
            try:
                tmpdir = davitpy.rcParams['DAVIT_TMPDIR']
            except:
                logging.warning("Unable to set temporary directory with "
                                "rcParams. Using extra default of /tmp/sd/")
                tmpdir = '/tmp/sd/'
        d = os.path.dirname(tmpdir)
        if not os.path.exists(d):
            os.makedirs(d)

        cached = False

        # First, check if a specific filename was given
        if fileName != None:
            try:
                if not os.path.isfile(fileName):
                    estr = 'problem reading [{:}]: file does '.format(fileName)
                    logging.error('{:s}not exist'.format(estr))
                    return None

                epoch = int(datetimeToEpoch(dt.datetime.now()))
                outname = "{:s}{:d}".format(tmpdir, epoch)
                if(string.find(fileName, '.bz2') != -1):
                    outname = string.replace(fileName, '.bz2', '')
                    command = 'bunzip2 -c {:s} > {:s}'.format(fileName, outname)
                elif(string.find(fileName,'.gz') != -1):
                    outname = string.replace(fileName, '.gz', '')
                    command = 'gunzip -c {:s} > {:s}'.format(fileName, outname)
                else:
                    command = 'cp {:s} {:s}'.format(fileName, outname)

                logging.info('performing: {:s}'.format(command))
                os.system(command)
                filelist.append(outname)
    
            except Exception, e:
                logging.error(e)
                logging.error('problem reading file [{:s}]'.format(fileName))
                return None

        # Next, check for a cached file
        if fileName == None and not noCache:
            try:
                if not cached:
                    command = "{:s}????????.??????.????????.????".format(tmpdir)
                    command = "{:s}??.{:s}.{:s}".format(command, hemi, fileType)
                    for f in glob.glob(command):
                        try:
                            ff = string.replace(f, tmpdir, '')
                            # check time span of file
                            t1 = dt.datetime(int(ff[0:4]), int(ff[4:6]),
                                             int(ff[6:8]), int(ff[9:11]),
                                             int(ff[11:13]), int(ff[13:15]))
                            t2 = dt.datetime(int(ff[16:20]), int(ff[20:22]),
                                             int(ff[22:24]), int(ff[25:27]),
                                             int(ff[27:29]), int(ff[29:31]))
                            # check if file covers our timespan
                            if t1 <= self.sTime and t2 >= self.eTime:
                                cached = True
                                filelist.append(f)
                                logging.info('Found cached file {:s}'.format(f))
                                break
                        except Exception, e:
                            logging.warning(e)
            except Exception, e:
                logging.warning(e)
  
        # Next, LOOK LOCALLY FOR FILES
        if not cached and (src == None or src == 'local') and fileName == None:
            try:
                for ftype in arr:
                    estr = "\nLooking locally for {:s} files ".format(ftype)
                    estr = "{:s}with hemi: {:s}".format(estr, hemi)
                    logging.info(estr)

                    # If the following aren't already, in the near future
                    # they will be assigned by a configuration dictionary 
                    # much like matplotlib's rcsetup.py (matplotlibrc)
                    if local_dirfmt is None:
                        try:
                            local_dirfmt = \
                                davitpy.rcParams['DAVIT_SD_LOCAL_DIRFORMAT']
                        except:
                            local_dirfmt = '/sd-data/{year}/{ftype}/{hemi}/'
                            estr = "Config entry DAVIT_SD_LOCAL_DIRFORMAT not "
                            estr = "{:s}set, using default: ".format(estr)
                            logging.info("{:s}{:s}".format(estr, local_dirfmt))
    
                    if local_dict is None:
                        local_dict = {'hemi':hemi, 'ftype':ftype}

                    if 'ftype' in local_dict.keys():
                        local_dict['ftype'] = ftype

                    if local_fnamefmt is None:
                        try:
                            local_fnamefmt = \
                        davitpy.rcParams['DAVIT_SD_LOCAL_FNAMEFMT'].split(',')
                        except:
                            local_fnamefmt = ['{date}.{hemi}.{ftype}']
                            estr = 'Environment variable DAVIT_SD_LOCAL_'
                            estr = '{:s}FNAMEFMT not set, using '.format(estr)
                            estr = '{:s}default: {:s}'.format(estr,
                                                              local_fnamefmt)
                            logging.info(estr)

                    outdir = tmpdir

                    # fetch the local files
                    temp = futils.fetch_local_files(self.sTime, self.eTime,
                                                    local_dirfmt, local_dict,
                                                    outdir, local_fnamefmt)

                    # check to see if the files actually have data between
                    # stime and etime
                    valid = self.__validate_fetched(temp, self.sTime,
                                                    self.eTime)
                    filelist = [x[0] for x in zip(temp, valid) if x[1]]
                    invalid_files = [x[0] for x in zip(temp, valid) if not x[1]]

                    if len(invalid_files) > 0:
                        for f in invalid_files:
                            estr = 'removing invalid file: {:s}'.format(f)
                            logging.info(estr)
                            os.system('rm {:s}'.format(f))

                    # If we have valid files then continue
                    if len(filelist) > 0:
                        estr = 'found {:s} data in local files'.format(ftype)
                        logging.info(estr)
                        self.fType = ftype
                        self.dType = 'dmap'
                        fileType = ftype
                        break
    
                    else:
                        estr = "couldn't find any local {:s}".format(ftype)
                        logging.info(estr)
    
            except Exception, e:
                logging.warning(e)
                estr = "Unable to fetch any local data, attempting to fetch "
                logging.warning("{:s}remote data".format(estr))
                src = None
              
        # Finally, check the sftp server if we have not yet found files
        if((src == None or src == 'sftp') and self.__ptr == None and
           len(filelist) == 0 and fileName == None):
            for ftype in arr:
                estr = 'Looking on the remote SFTP server for '
                logging.info('{:s}{:s} files'.format(estr, ftype))
                try:
                    # If the following aren't already, in the near future
                    # they will be assigned by a configuration dictionary 
                    # much like matplotlib's rcsetup.py (matplotlibrc)
                    if remote_site is None:
                        try:
                            remote_site = davitpy.rcParams['DB']
                        except:
                            remote_site = 'sd-data.ece.vt.edu'
                            estr = 'Config entry DB not set, using default: '
                            logging.info("{:s}{:s}".format(estr, remote_site))

                    if username is None:
                        try:
                            username = davitpy.rcParams['DBREADUSER']
                        except:
                            username = 'sd_dbread'
                            estr = 'Config entry DBREADUSER not set, using '
                            estr = '{:s}default: {:s}'.format(estr, username)
                            logging.info(estr)

                    if password is None:
                        try:
                            password = davitpy.rcParams['DBREADPASS']
                        except:
                            password = '5d'
                            estr = 'Config entry DBREADPASS not set, using '
                            estr = '{:s}default: {:s}'.format(estr, password)
                            logging.info(estr)

                    if remote_dirfmt is None:
                        try:
                            remote_dirfmt = \
                            davitpy.rcParams['DAVIT_SD_REMOTE_DIRFORMAT']
                        except:
                            remote_dirfmt = 'data/{year}/{ftype}/{hemi}/'
                            estr = 'Config entry DAVIT_SD_REMOTE_DIRFORMAT not'
                            estr = '{:s} set, using default: '.format(estr)
                            estr = '{:s}{:s}'.format(estr, remote_dirfmt)
                            logging.info(estr)

                    if remote_dict is None:
                        remote_dict = {'ftype':ftype, 'hemi':hemi}

                    if 'ftype' in remote_dict.keys():
                        remote_dict['ftype'] = ftype

                    if remote_fnamefmt is None:
                        try:
                            remote_fnamefmt = \
                    davitpy.rcParams['DAVIT_SD_REMOTE_FNAMEFMT'].split(',')
                        except:
                            remote_fnamefmt = ['{date}.{hemi}.{ftype}']
                            estr = 'Config entry DAVIT_SD_REMOTE_FNAMEFMT not '
                            estr = '{:s}set, using default: '.format(estr)
                            estr = '{:s}{:s}'.format(estr, remote_fnamefmt)
                            logging.info(estr)

                    if port is None:
                        try:
                            port = davitpy.rcParams['DB_PORT']
                        except:
                            port = '22'
                            estr = 'Config entry DB_PORT not set, using default'
                            logging.info('{:s}: {:s}'.format(estr, port))

                    outdir = tmpdir

                    # Now fetch the files
                    temp = futils.fetch_remote_files(self.sTime, self.eTime,
                                                     'sftp', remote_site,
                                                     remote_dirfmt, remote_dict,
                                                     outdir, remote_fnamefmt,
                                                     username=username,
                                                     password=password,
                                                     port=port)

                    # check to see if the files actually have data between
                    # stime and etime
                    valid = self.__validate_fetched(temp, self.sTime,
                                                    self.eTime)
                    filelist = [x[0] for x in zip(temp, valid) if x[1]]
                    invalid_files = [x[0] for x in zip(temp, valid) if not x[1]]

                    if len(invalid_files) > 0:
                        for f in invalid_files:
                            estr = "removing invalid file: {:s}".format(f)
                            logging.info(estr)
                            os.system("rm {:s}".format(f))

                    # If we have valid files then continue
                    if len(filelist) > 0 :
                        estr = 'found {:s} data on sftp server'.format(ftype)
                        logging.info(estr)
                        self.fType = ftype
                        self.dType = 'dmap'
                        fileType = ftype
                        break
                    else:
                        estr = "couldn't find {:s} data on sftp ".format(ftype)
                        logging.info("{:s}server".format(estr))
    
                except Exception, e:
                    logging.warning(e)
                    logging.warning('problem reading from sftp server')

        # check if we have found files
        if len(filelist) != 0:
            # concatenate the files into a single file
            if not cached:
                logging.info('Concatenating all the files in to one')
                # choose a temp file name with time span info for cacheing
                tmpname = '{:s}{:s}.{:s}'.format(tmpdir,
                                                 self.sTime.strftime("%Y%m%d"),
                                                 self.sTime.strftime("%H%M%S"))
                tmpname = '{:s}.{:s}.{:s}'.format(tmpname,
                                                  self.eTime.strftime("%Y%m%d"),
                                                  self.eTime.strftime("%H%M%S"))
                tmpname = '{:s}.{:s}.{:s}'.format(tmpname, hemi, fileType)
                command = "cat {:s} > {:s}".format(string.join(filelist),
                                                   tmpname)
                logging.info("performing: {:s}".format(command))
                os.system(command)
                for filename in filelist:
                    command = "rm {:s}".format(filename)
                    logging.info("performing: {:s}".format(command))
                    os.system(command)
            else:
                tmpname = filelist[0]
                self.fType = fileType
                self.dType = 'dmap'

            self.__filename = tmpname
            self.open()

        if self.__ptr != None:
            if self.dType == None:
                self.dType = 'dmap'
        else:
            logging.info('Sorry, we could not find any data for you :(')

    def __repr__(self):
        my_str = 'sdDataPtr\n'
        for key,var in self.__dict__.iteritems():
            my_str = "{:s}{:s} = {:s}\n".format(my_str, key, str(var))
        return my_str

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def next(self):
        beam = self.readRec()
        if beam is None:
            raise StopIteration
        else:
            return beam

    def open(self):
        """open the associated dmap filename."""
        import os
        self.__fd = os.open(self.__filename, os.O_RDONLY)
        self.__ptr = os.fdopen(self.__fd)

    def createIndex(self):
        import datetime as dt
        import davitpy.pydarn.dmapio as dmapio

        recordDict = {}
        starting_offset = self.offsetTell()

        # rewind back to start of file
        self.rewind()
        while 1:
            # read the next record from the dmap file
            offset = dmapio.getDmapOffset(self.__fd)
            dfile = dmapio.readDmapRec(self.__fd)
            if dfile is None:
                # if we dont have valid data, clean up, get out
                logging.info('reached end of data')
                break
            else:
                try:
                    dtime = dt.datetime(dfile['start.year'],
                                        dfile['start.month'],
                                        dfile['start.day'],
                                        dfile['start.hour'],
                                        dfile['start.minute'],
                                        int(dfile['start.second']))
                    dfile['time'] = (dtime -
                                     dt.datetime(1970, 1, 1)).total_seconds()
                except Exception,e:
                    logging.warning(e)
                    logging.warning('problem reading time from file')
                    break

                dfile_utc = dt.datetime.utcfromtimestamp(dfile['time'])
                if dfile_utc >= self.sTime and dfile_utc <= self.eTime: 
                    rectime = dt.datetime.utcfromtimestamp(dfile['time'])
                    recordDict[rectime] = offset

        # reset back to before building the index 
        self.recordIndex = recordDict
        self.offsetSeek(starting_offset)
        return recordDict

    def offsetSeek(self, offset, force=False):
        """jump to dmap record at supplied byte offset.
           Require offset to be in record index list unless forced. 
        """
        from davitpy.pydarn.dmapio import setDmapOffset, getDmapOffset

        if force:
            return dmapio.setDmapOffset(self.__fd, offset)
        else:
            if self.recordIndex is None:        
                self.createIndex()

            if offset in self.recordIndex.values():
                return setDmapOffset(self.__fd, offset)
            else:
                return getDmapOffset(self.__fd)

    def offsetTell(self):
        """jump to dmap record at supplied byte offset. 
        """
        from davitpy.pydarn.dmapio import getDmapOffset
        return getDmapOffset(self.__fd)
  
    def rewind(self):
        """jump to beginning of dmap file."""
        from davitpy.pydarn.dmapio import setDmapOffset 
        return setDmapOffset(self.__fd, 0)
  
    def readRec(self):
        """A function to read a single record of radar data from a radDataPtr
        object

        Returns
        --------
        mydata : (gridData, mapData, or NoneType)
            An object filled with the specified type of data.  Will return None
            when there is no more data in the pointer to read.
        """
        import davitpy.pydarn.dmapio as dmapio
        import datetime as dt

        # check input
        if self.__ptr == None:
            logging.error('the pointer does not point to any data')
            return None

        if self.__ptr.closed:
            logging.error('the file pointer is closed')
            return None
  
        # do this until we reach the requested start time
        # and have a parameter match
        while 1:
            offset = dmapio.getDmapOffset(self.__fd)
            dfile = dmapio.readDmapRec(self.__fd)
            # check for valid data
            try:
                dtime = dt.datetime(dfile['start.year'], dfile['start.month'],
                                    dfile['start.day'], dfile['start.hour'],
                                    dfile['start.minute'],
                                    int(dfile['start.second']))
                dfile['time'] = (dtime -
                                 dt.datetime(1970, 1, 1)).total_seconds()

            except Exception, e:
                logging.warning(e)
                logging.warning('problem reading time from file')
                break

            if(dfile == None or
               dt.datetime.utcfromtimestamp(dfile['time']) > self.eTime):
                # if we dont have valid data, clean up, get out
                logging.info('reached end of data')
                return None

            # check that we're in the time window, and that we have a 
            # match for the desired params  
            if(dt.datetime.utcfromtimestamp(dfile['time']) >= self.sTime and
               dt.datetime.utcfromtimestamp(dfile['time']) <= self.eTime):
                # fill the beamdata object, checking the file type
                if self.fType == 'grd' or self.fType == 'grdex':
                    mydata = gridData(dataDict=dfile)
                elif self.fType == 'map' or self.fType == 'mapex':
                    mydata = mapData(dataDict=dfile)
                else:
                    logging.error('unrecognized file type')
                    return None

                mydata.recordDict = dfile
                mydata.fType = self.fType
                mydata.fPtr = self
                mydata.offset = offset
  
                return mydata

    def close(self):
        """close associated dmap file."""
        import os

        if self.__ptr is not None:
            self.__ptr.close()
            self.__fd = None

    def __validate_fetched(self, filelist, stime, etime):
        """ This function checks if the files in filelist contain data
        for the start and end times (stime,etime) requested by a user.

        Parameters
        -----------
        filelist : (list)
            List of filenames to validate
        stime : (datetime.datetime)
            Starting time for files
        etime : (datetime.datetime)
            Ending time for files

        Returns
        --------
        valid : (list of bool)
            List of booleans corresponding to each filename. True if a file
            contains data in the time range (stime,etime), False if not
        """
        # This method will need some modification for it to work with
        # file formats that are NOT DMAP (i.e. HDF5). Namely, the dmapio
        # specific code will need to be modified (readDmapRec).

        import datetime as dt
        import numpy as np
        from davitpy.pydarn.dmapio import readDmapRec

        valid = []

        for f in filelist:
            logging.info('Checking file: {:s}'.format(f))
            stimes = []
            etimes = []

            # Open the file and create a file pointer
            self.__filename = f
            self.open()

            # Iterate through the file and grab the start time for beam
            # integration and calculate the end time from intt.sc and intt.us
            while 1:
                # read the next record from the dmap file
                dfile = readDmapRec(self.__fd)
                if(dfile is None):
                    break
                else:
                    temp = dt.datetime(int(dfile['start.year']),
                                       int(dfile['start.month']),
                                       int(dfile['start.day']),
                                       int(dfile['start.hour']),
                                       int(dfile['start.minute']),
                                       int(dfile['start.second']))
                    stimes.append(temp)
                    temp = dt.datetime(int(dfile['end.year']),
                                       int(dfile['end.month']),
                                       int(dfile['end.day']),
                                       int(dfile['end.hour']),
                                       int(dfile['end.minute']),
                                       int(dfile['end.second']))
                    etimes.append(temp)

            # Close the file and clean up
            self.close()
            self.__ptr = None

            inds = np.where((np.array(stimes) >= stime) &
                            (np.array(stimes) <= etime))
            inde = np.where((np.array(etimes) >= stime) &
                            (np.array(etimes) <= etime))

            if np.size(inds) > 0 or np.size(inde) > 0:
                valid.append(True)
            else:
                valid.append(False) # ISSUE 217: FASTER TO NOT USE APPEND

        return valid

class sdBaseData():
    """A base class for the processed SD data types.  This allows for single
    definition of common routines

    Methods
    ---------
    updateValsFromDict
        converts a dict from a dmap file to baseData

    Written by AJ 20130607
    """
    def updateValsFromDict(self, adict):
        """A function to to fill an sdBaseData object with the data in a
        dictionary that is returned from the reading of a dmap file

        Parameters
        ------------
        adict : (dict)
            the dictionary containing the radar data

        Returns
        ----------
        Void

        Notes
        -------
        In general, users will not need to use this.

        Written by AJ 20121130
        """
        import datetime as dt

        syr = 1
        smo = 1
        sdy = 1
        shr = 1
        smt = 1
        ssc = 1
        eyr = 1
        emo = 1
        edy = 1
        ehr = 1
        emt = 1
        esc = 1

        for key,val in adict.iteritems():
            if key == 'start.year':
                syr = adict['start.year']
            elif key == 'start.month':
                smo = adict['start.month']
            elif key == 'start.day':
                sdy = adict['start.day']
            elif key == 'start.hour':
                shr = adict['start.hour']
            elif key == 'start.minute':
                smt = adict['start.minute']
            elif key == 'start.second':
                ssc = int(adict['start.second'])
            elif key == 'end.year':
                eyr = adict['end.year']
            elif key == 'end.month':
                emo = adict['end.month']
            elif key == 'end.day':
                edy = adict['end.day']
            elif key == 'end.hour':
                ehr = adict['end.hour']
            elif key == 'end.minute':
                emt = adict['end.minute']
            elif key == 'end.second':
                esc = int(adict['end.second'])
            elif 'vector.' in key:
                if isinstance(self, sdVector):
                    name = key.replace('vector.', '')
                    name = name.replace('.', '')
                    if hasattr(self, name):
                        setattr(self, name, val)
            elif 'model.' in key:
                if isinstance(self, sdModel):
                    name = key.replace('model.', '')
                    name = name.replace('.', '')
                    if hasattr(self, name):
                        setattr(self, name, val)
            elif '+' in key:
                name = key.replace('+', 'p')
                if hasattr(self, name):
                    setattr(self, name, val)
            else:
                name = key.replace('.', '')
                if hasattr(self, name):
                    setattr(self, name, val)

        if isinstance(self, gridData) or isinstance(self, mapData):
            self.sTime = dt.datetime(syr, smo, sdy, shr, smt, ssc)
            self.eTime = dt.datetime(eyr, emo, edy, ehr, emt, esc)

    def __repr__(self):
        mystr = ''
        for key,val in self.__dict__.iteritems():
            mystr = "{:s}{:s} = {:s}\n".format(mystr, str(key), str(val))
        return mystr

class gridData(sdBaseData):
    """ a class to contain a record of gridded data, extends sdBaseData

    Attributes
    -----------
    sTime : (datetime)
        start time of the record
    eTime : (datetime)
        end time of the record
    stid : (list)
        a list of the station IDs in the record, by radar
    nvec : (list)
        a list of the number of vectors in the record, by radar
    freq : (list)
        a list of the transmit frequencies, in kHz, by radar
    programid : (list)
        a list of the program IDs, by radar
    noisemean : (list)
        a list of the mean noise level, by radar
    noisesd : (list)
        a list of the standard deviation of noise level, by radar
    gsct : (list)
        a list of flags indicating whether ground scatter was excluded from the
        gridding, by radar
    vmin : (list)
        a list of minimum allowed Doppler velocity, by radar
    vmax : (list)
        a list of the maximum allowed Doppler velocity, by radar
    pmin : (list)
        a list of the minimum allowed power level, by radar
    pmax : (list)
        a list of the maximum allowed power level, by radar
    wmin : (list)
        a list of the minimum allowed spectral width, by radar
    wmax : (list)
        a list of the maximum allowed spectral width, by radar
    vemin : (list)
        a list of the minimum allowed velocity error, by radar
    vemax : (list)
        a list of the maximum allowed velocity error, by radar
    vector : (sdVector)
        an object containing all of the vector.* elements from the file

    Written by AJ 20130607
    """
    # initialize the struct
    def __init__(self, dataDict=None):
        self.sTime = None
        self.eTime = None
        self.stid = None
        self.channel = None
        self.nvec = None
        self.freq = None
        self.programid = None
        self.noisemean = None
        self.noisesd = None
        self.gsct = None
        self.vmin = None
        self.vmax = None
        self.pmin = None
        self.pmax = None
        self.wmin = None
        self.wmax = None
        self.vemin = None
        self.vemax = None
        self.vector = sdVector(dataDict=dataDict)

        if dataDict != None:
            self.updateValsFromDict(dataDict)

# HERE
class mapData(sdBaseData):
    """ a class to contain a record of map potential data, extends sdBaseData

    Attributes
    ------------
    sTime : (datetime)
        start time of the record
    eTime : (datetime)
        end time of the record
    dopinglevel : (int)
    modelwt : (int)
    errorwt : (int)
    IMFflag : (int)
    IMFdelay : (int)
    IMFBx : (float)
        the Bx component of the IMF
    IMFBy : (float)
        the By component of the IMF
    IMFBz : (float)
        the Bz component of the IMF
    modelangle : (string)
    modellevel : (string)
    hemi : (int)
        A flag to denote the hemisphere, with 1=north, 2=south?
    fitorder : (int)
        the order of the spherical harmonic fit
    latmin : (float)
        the minimum latitude in the spherical harmonic fit
    chisqr : (double)
        Chi squared value of the spherical harmonic fit
    chisqrdat : (double)
        Something pertaining to the Chi squared value
    rmserr : (double)
        an object containing all of the vector.* elements from the file
    lonshft : (double)
    latshft : (double)
    mltstart : (double)
        Magnetic local time of the start
    mltend : (double)
        Magnetic local time of the end
    mltav : (double)
        Average magnetic local time (?)
    potdrop : (double)
        the cross polar cap potential, in Volts
    potdroperr : (int)
        the error in the cross polar cap potential, in Volts
    potmax : (double)
        Maximum of the cross polar cap potential ?
    potmaxerr : (double)
        Error of the previous value
    potmin : (double)
        Minimum of the cross polar cap potential ?
    potminerr : (double)
        Error of the previous value
    grid : (gridData)
        an object to hold all of the grid data in the record 
    N : (list)
    Np1 : (list)
    Np2 : (list)
    Np3 : (list)
    model : (sdModel)
        an object to hold the model data in the record

    Written by AJ 20130607
    """
    # initialize the struct
    def __init__(self, dataDict=None):
        self.sTime = None
        self.eTime = None
        self.dopinglevel = None
        self.modelwt = None
        self.errorwt = None
        self.IMFflag = None
        self.IMFdelay = None
        self.IMFBx = None
        self.IMFBy = None
        self.IMFBz = None
        self.modelangle = None
        self.modellevel = None
        self.hemi = None
        self.fitorder = None
        self.latmin = None
        self.chisqr = None
        self.chisqrdat = None
        self.rmserr = None
        self.lonshft = None
        self.latshft = None
        self.mltstart = None
        self.mltend = None
        self.mltav = None
        self.potdrop = None
        self.potdroperr = None
        self.potmax = None
        self.potmaxerr = None
        self.potmin = None
        self.potminerr = None
        self.grid = gridData(dataDict=dataDict)
        self.N = None
        self.Np1 = None
        self.Np2 = None
        self.Np3 = None
        self.model = sdModel(dataDict=dataDict)

        if(dataDict != None): 
            self.updateValsFromDict(dataDict)

class sdVector(sdBaseData):
    """ a class to contain vector records of gridded data, extends sdBaseData

    Attributes
    -----------
    mlat : (list)
        the magnetic longitude of the grid cells
    mlon : (list)
        the magnetic longitude of the grid cells
    kvect : (list)
        the kvectors of the vectors in the grid cells
    stid : (int)
        the station ID of the radar which made the measurement of the vector
        in the grid cell
    channel : (int)
        the channel of the radar which made the measurement of the vector in
        the grid cell
    index : (int)
    velmedian : (int)
        the median velocity of the vector
    velsd : (float)
        the standard deviation of the velocity of the vector
    pwrmedian : (float)
        the median power of the vector
    pwrsd : (float)
        the standard devation of the power of the vector
    wdtmedian : (string)
        the median spectral width of the vector
    wdtsd : (string)
        the standard devation on the spectral width of the vector

    Written by AJ 20130607
    """
    # initialize the struct
    def __init__(self, dataDict=None):
        self.mlat = None
        self.mlon = None
        self.kvect = None
        self.stid = None
        self.channel = None
        self.index = None
        self.velmedian = None
        self.velsd = None
        self.pwrmedian = None
        self.pwrsd = None
        self.wdtmedian = None
        self.wdtsd = None

        if(dataDict != None):
            self.updateValsFromDict(dataDict)

class sdModel(sdBaseData):
    """ a class to contain model records of map poential data, extends
    sdBaseData

    Attributes
    -------------
    mlat : (list)
        Magnetic latitude
    kvect : (list)
        Positional vector
    velmedian : (list)
        Median velocity at the specified location
    boundarymlat : (int)
        Bounding magnetic latitude
    boundarymlon : (int)
        Bounding magnetic longitude

    Written by AJ 20130607
    """
    # initialize the struct
    def __init__(self, dataDict=None):
        self.mlat = None
        self.mlon = None
        self.kvect = None
        self.velmedian = None
        self.boundarymlat = None
        self.boundarymlon = None

        if(dataDict != None):
            self.updateValsFromDict(dataDict)

# TESTING CODE
if __name__=="__main__":
    import os
    import datetime as dt
    import hashlib
    import davitpy

    try:
        tmpdir = davitpy.rcParams['DAVIT_TMPDIR']
    except:
        tmpdir = '/tmp/sd/'

    hemi = 'north'
    channel = None
    stime = dt.datetime(2012, 7, 10)
    etime = dt.datetime(2012, 7, 11, 2)
    expected_filename = "20120710.000000.20120711.020000.north.mapex"
    expected_path = os.path.join(tmpdir, expected_filename)
    expected_filesize = 32975826
    expected_md5sum = "1b0e78cb339e875cc17f82e240ef360f"
    print "Expected File:", expected_path

    print "\nRunning sftp grab example for sdDataPtr."
    print "Environment variables used:"
    print "  DB:", davitpy.rcParams['DB']
    print "  DB_PORT:", davitpy.rcParams['DB_PORT']
    print "  DBREADUSER:", davitpy.rcParams['DBREADUSER']
    print "  DBREADPASS:", davitpy.rcParams['DBREADPASS']
    print "  DAVIT_SD_REMOTE_DIRFORMAT:", \
        davitpy.rcParams['DAVIT_SD_REMOTE_DIRFORMAT']
    print "  DAVIT_SD_REMOTE_FNAMEFMT:", \
        davitpy.rcParams['DAVIT_SD_REMOTE_FNAMEFMT']
    print "  DAVIT_SD_REMOTE_TIMEINC:", \
        davitpy.rcParams['DAVIT_SD_REMOTE_TIMEINC']
    print "  DAVIT_TMPDIR:", davitpy.rcParams['DAVIT_TMPDIR']

    src = 'sftp'
    if os.path.isfile(expected_path):
        os.remove(expected_path)
    vtptr = sdDataPtr(stime, hemi, eTime=etime, fileType='mapex', src=src,
                      noCache=True)
    if os.path.isfile(expected_path):
        statinfo = os.stat(expected_path)
        print "Actual File Size:  ", statinfo.st_size
        print "Expected File Size:", expected_filesize 
        md5sum = hashlib.md5(open(expected_path).read()).hexdigest()
        print "Actual Md5sum:  ", md5sum
        print "Expected Md5sum:", expected_md5sum
        if expected_md5sum != md5sum:
            print "Error: Cached dmap file has unexpected md5sum."
    else:
        print "Error: Failed to create expected cache file"
    print "Let's read two records from the remote sftp server:"
    try:
        ptr = vtptr
        mydata = ptr.readRec()
        print mydata.recordDict['time']
        mydata = ptr.readRec()
        print mydata.recordDict['time']
        print "Close pointer"
        ptr.close()
        print "reopen pointer"
        ptr.open()
        print "Should now be back at beginning:"
        mydata = ptr.readRec()
        print mydata.recordDict['time']
        print "What is the current offset:"
        print ptr.offsetTell()
        print "Try to seek to offset 4, shouldn't work:"
        print ptr.offsetSeek(4)
        print "What is the current offset:"
        print ptr.offsetTell()
    except:
        print "record read failed for some reason"

    ptr.close()
    del vtptr

    print "\nRunning local grab example for sdDataPtr."
    print "Environment variables used:"
    print "  DAVIT_SD_LOCAL_DIRFORMAT:", \
        davitpy.rcParams['DAVIT_SD_LOCAL_DIRFORMAT']
    print "  DAVIT_SD_LOCAL_FNAMEFMT:", \
        davitpy.rcParams['DAVIT_SD_LOCAL_FNAMEFMT']
    print "  DAVIT_SD_LOCAL_TIMEINC:", \
        davitpy.rcParams['DAVIT_SD_LOCAL_TIMEINC']
    print "  DAVIT_TMPDIR:", davitpy.rcParams['DAVIT_TMPDIR']

    src = 'local'
    if os.path.isfile(expected_path):
        os.remove(expected_path)
    localptr = sdDataPtr(stime, hemi, eTime=etime, src=src, fileType='mapex',
                         noCache=True)
    if os.path.isfile(expected_path):
        statinfo = os.stat(expected_path)
        print "Actual File Size:  ", statinfo.st_size
        print "Expected File Size:", expected_filesize 
        md5sum = hashlib.md5(open(expected_path).read()).hexdigest()
        print "Actual Md5sum:  ", md5sum
        print "Expected Md5sum:", expected_md5sum
        if expected_md5sum != md5sum:
            print "Error: Cached dmap file has unexpected md5sum."
    else:
        print "Error: Failed to create expected cache file"
    print "Let's read two records:"
    try:
        ptr = localptr
        mydata = ptr.readRec()
        print mydata.recordDict['time']
        mydata = ptr.readRec()
        print mydata.recordDict['time']
        print "Close pointer"
        ptr.close()
        print "reopen pointer"
        ptr.open()
        print "Should now be back at beginning:"
        mydata = ptr.readRec()
        print mydata.recordDict['time']
    except:
        print "record read failed for some reason"
    ptr.close()

    del localptr
