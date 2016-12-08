# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""Millstone Hill module

This module handles Millstone Hill ISR data

Classes
-------------------------------------------
mhoData     Millstone Hill data interaction
-------------------------------------------

"""
import logging

# constants
user_fullname = 'Sebastien de Larquier'
user_email = 'sdelarquier@vt.edu'
user_affiliation = 'Virginia Tech'

#####################################################
#####################################################
class mhoData(object):
    """Read Millstone Hill data, either locally if it can be found, or directly from Madrigal

    Parameters
    ----------
    expDate : datetime.datetime
        experiment date
    endDate : Optional[datetime.datetime]
        end date/time to look for experiment files on Madrigal
    getMad : Optional[bool]
        force download from Madrigal (overwrite any matching local file)
    dataPath : Optional[str]
        path where the local data should be read/saved
    fileExt : Optional[str]
        file extension (i.e., 'g.002'). If None is provided, it will just look for the most recent available one
    user_fullname : Optional[str]
        required to download data from Madrigal (no registration needed)
    user_email : Optional[str]
        required to download data from Madrigal (no registration needed)
    user_affiliation : Optional[str]
        required to download data from Madrigal (no registration needed)

    Attributes
    ----------
    expDate : datetime.datetime
        experiment date
    endDate : datetime.datetime
        end date/time to look for experiment files on Madrigal
    dataPath : str
        path where the local data should be read/saved
    fileExt : str
        file extension (i.e., 'g.002'). If None is provded, it will just
        look for the most recent available one
    mhoCipher : dict

    Example
    -------
        # Get data for November 17-18, 2010
        import datetime as dt
        user_fullname = 'Sebastien de Larquier'
        user_email = 'sdelarquier@vt.edu'
        user_affiliation = 'Virginia Tech'
        date = dt.datetime(2010,11,17,20)
        edate = dt.datetime(2010,11,18,13)
        data = mhoData( date, endDate=edate, 
             user_fullname=user_fullname, 
             user_email=user_email, 
             user_affiliation=user_affiliation )

    written by Sebastien de Larquier, 2013-03

    """

    def __init__(self, expDate, endDate=None, 
        dataPath=None, fileExt=None, getMad=False, 
        user_fullname=None, user_email=None, user_affiliation=None):
        self.expDate = expDate
        self.endDate = endDate
        self.dataPath = dataPath
        self.fileExt = fileExt

        self.mhoCipher = {'nel': r'N$_e$ [$\log$(m$^{-3}$)]',
                          'ti': r'T$_i$ [K]',
                          'te': r'T$_e$ [K]', 
                          'vo': r'v$_i$ [m/s]'}

        # Look for the file locally
        if not getMad:
            filePath = self.getFileLocal()
        # If no local files, get it from madrigal
        if getMad or not filePath:
            if None in [user_fullname, user_email, user_affiliation]:
                logging.error('Please provide user_fullname, user_email, user_affiliation.')
                return
            filePath = self.getFileMad(user_fullname, user_email, user_affiliation)
        logging.info(filePath)

        if filePath:
            self.readData(filePath)


    def look(self):
        """Find radar pointing directions during selected experiment

        Parameters
        ----------
        None

        Returns
        -------
        np.unique(pointing) :
            Radar pointing directions during selected experiment

        """
        import numpy as np

        pointing = [(el, az) for el, az in zip(np.around(self.elev.flatten(),1), np.around(self.azim.flatten(),1))]

        return np.unique(pointing)


    def readData(self, filePath):
        """Read data from HDF5 file

        Parameters
        ----------
        filePath : str
            Path and name of HDF5 file

        """
        import h5py as h5
        import matplotlib as mp
        import numpy as np
        from utils import geoPack as gp
        from utils import Re
        import datetime as dt

        with h5.File(filePath,'r') as f:
            data = f['Data']['Array Layout']
            data2D = data['2D Parameters']
            data1D = data['1D Parameters']
            params = f['Metadata']['Experiment Parameters']
            self.nel = data2D['nel'][:].T
            self.ne = data2D['ne'][:].T
            self.ti = data2D['ti'][:].T
            self.vo = data2D['vo'][:].T
            self.te = data2D['tr'][:].T * self.ti
            self.range = data['range'][:]
            self.time = np.array( [ dt.datetime.utcfromtimestamp(tt) for tt in data['timestamps'][:].T ] )
            self.elev = np.array( [data1D['el1'][:],
                data1D['el2'][:]] ).T
            self.azim = np.array( [data1D['az1'][:], 
                data1D['az2'][:]] ).T
            try:
                self.scntyp = data1D['scntyp'][:]
            except:
                self.scntyp = np.zeros(self.time.shape)
            vinds = np.where( self.elev[:,0] >= 88. )
            if len(vinds[0]) > 0:
                self.scntyp[vinds] = 5
            self.gdalt = data2D['gdalt'][:].T
            self.position = [float(params[7][1]),
                            float(params[8][1]),
                            float(params[9][1])]
            self.lat = data2D['glat'][:].T
            self.lon = data2D['glon'][:].T


    def getFileLocal(self):
        """Look for the file in the dataPath or current directory

        Returns
        -------
        filePath : str
            the path and name of the data file

        Notes
        -----
        Belongs to class mhoData

        """
        import os, glob, datetime
        import numpy as np

        fileName = 'mlh{:%y%m%d}'.format( self.expDate )
        if not self.fileExt:
            dfiles = np.sort(glob.glob(self.dataPath+fileName+'?.???.hdf5'))
            if not not list(dfiles):
                self.fileExt = dfiles[-1][-10:-5]
            else: return

        fileName = fileName + self.fileExt + '.hdf5'
        filePath = os.path.join(self.dataPath, fileName)

        return filePath


    def getFileMad(self, user_fullname, user_email, user_affiliation):
        """Look for the data on Madrigal

        Returns
        -------
        filePath : str
            the path and name of the data file

        Notes
        -----
        Belongs to class mhoData

        """
        import madrigalWeb.madrigalWeb
        import os, h5py, numpy, datetime
        from matplotlib.dates import date2num, epoch2num, num2date

        madrigalUrl = 'http://cedar.openmadrigal.org'
        madData = madrigalWeb.madrigalWeb.MadrigalData(madrigalUrl)

        # Start and end date/time
        sdate = self.expDate
        fdate = self.endDate if self.endDate else sdate + datetime.timedelta(days=1)

        # Get experiment list
        expList = madData.getExperiments(30, 
            sdate.year, sdate.month, sdate.day, sdate.hour, 
            sdate.minute, sdate.second, 
            fdate.year, fdate.month, fdate.day, fdate.hour, 
            fdate.minute, fdate.second)
        if not expList: return

        # Try to get the default file
        thisFilename = False
        fileList = madData.getExperimentFiles(expList[0].id)
        for thisFile in fileList:
            if thisFile.category == 1:
                thisFilename = thisFile.name
                break
        if not thisFilename: return

        # Download HDF5 file
        result = madData.downloadFile(thisFilename, 
            os.path.join( self.dataPath,"{}.hdf5"\
            .format(os.path.split(thisFilename)[1]) ), 
            user_fullname, user_email, user_affiliation, 
            format="hdf5")

        # Now add some derived data to the hdf5 file
        res = madData.isprint(thisFilename, 
                'YEAR,MONTH,DAY,HOUR,MIN,SEC,RANGE,GDALT,NE,NEL,MDTYP,GDLAT,GLON',
                '', user_fullname, user_email, user_affiliation)

        rows = res.split("\n") 
        filePath = os.path.join( self.dataPath,
            os.path.split(thisFilename)[1]+'.hdf5' )
        self.fileExt = ( os.path.split(thisFilename)[1] )[-1]
        # Add new datasets to hdf5 file
        with h5py.File(filePath,'r+') as f:
            ftime = epoch2num( f['Data']['Array Layout']['timestamps'] )
            frange = f['Data']['Array Layout']['range']
            tDim, rDim = ftime.shape[0], frange.shape[0]
            shape2d = (tDim, rDim)
            gdalt = numpy.empty(shape2d)
            gdalt[:] = numpy.nan
            gdlat = numpy.empty(shape2d)
            gdlat[:] = numpy.nan
            gdlon = numpy.empty(shape2d)
            gdlon[:] = numpy.nan
            ne = numpy.empty(shape2d)
            ne[:] = numpy.nan
            nel = numpy.empty(shape2d)
            nel[:] = numpy.nan
            dtfmt = '%Y-%m-%d %H:%M:%S'
            dttype = numpy.dtype('a{}'.format(len(dtfmt)+2))
            dtime = numpy.empty(tDim, dtype=dttype)

            # Iterate through the downloaded data
            for r in rows:
                dat = r.split()
                if not dat: continue
                # Figure out your range/time index
                dt = datetime.datetime( int(dat[0]), int(dat[1]), int(dat[2]), 
                                        int(dat[3]), int(dat[4]), int(dat[5]) )
                tind = numpy.where(ftime[:] <= date2num(dt))[0]
                rind = numpy.where(frange[:] <= float(dat[6]))[0]
                if not list(tind) or not list(rind): continue
                if dat[7] != 'missing':
                    gdalt[tind[-1],rind[-1]] = float(dat[7])
                if dat[8] != 'missing':
                    ne[tind[-1],rind[-1]] = float(dat[8])
                if dat[9] != 'missing':
                    nel[tind[-1],rind[-1]] = float(dat[9])
                dtime[tind[-1]] = dt.strftime(dtfmt)
                if dat[11] != 'missing':
                    gdlat[tind[-1],rind[-1]] = float(dat[11])
                if dat[12] != 'missing':
                    gdlon[tind[-1],rind[-1]] = float(dat[12])

            # Add 2D datasets
            parent = f['Data']['Array Layout']['2D Parameters']
            gdalt_ds = parent.create_dataset('gdalt', data=gdalt)
            gdalt_ds = parent.create_dataset('glat', data=gdlat)
            gdalt_ds = parent.create_dataset('glon', data=gdlon)
            ne_ds = parent.create_dataset('ne', data=ne)
            nel_ds = parent.create_dataset('nel', data=nel)

            # Add 1D datasets
            parent = f['Data']['Array Layout']
            datetime_ds = parent.create_dataset('datetime', data=dtime)

        return filePath
