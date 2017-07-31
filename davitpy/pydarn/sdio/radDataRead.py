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
.. module:: radDataRead
   :synopsis: A module for reading radar data (iqdat, raw, fit)

.. moduleauthor:: AJ, 20130110

************************************
**Module**: pydarn.sdio.radDataRead
************************************

Functions
----------
  :func:`pydarn.sdio.radDataRead.radDataOpen`
  :func:`pydarn.sdio.radDataRead.radDataReadRec`
  :func:`pydarn.sdio.radDataRead.radDataReadScan`
  :func:`pydarn.sdio.radDataRead.radDataReadAll`
  :func:`pydarn.sdio.radDataRead.radDataCreateIndex`
"""
import logging

def radDataOpen(sTime, radcode, eTime=None, channel=None, bmnum=None, cp=None,
                fileType='fitex', filtered=False, src=None, fileName=None,
                noCache=False, local_dirfmt=None, local_fnamefmt=None,
                local_dict=None, remote_dirfmt=None, remote_fnamefmt=None,
                remote_dict=None, remote_site=None, username=None,
                password=None, port=None, tmpdir=None, remove=False,
                try_file_types=True):

    """A function to establish a pipeline through which we can read radar data.
    first it tries the mongodb, then it tries to find local files, and lastly
    it sftp's over to the VT data server.

    Parameters
    -----------
    sTime : (datetime)
        The beginning time for which you want data
    radcode : (str)
        The 3-letter radar code with optional channel extension for which you
        want data
    eTime : (datetime/NoneType)
        The last time that you want data for.  If this is set to None, it will
        be set to 1 day after sTime.  (default=None)
    channel : (str/NoneType)
        The 1-letter code for what channel you want data from, eg 'a','b',...
        if this is set to None, data from ALL channels will be read.
        (default=None)
    bmnum : (int/NoneType)
        The beam number which you want data for.  If this is set to None, data
        from all beams will be read. (default=None)
    cp : (int)
        The control program which you want data for.  If this is set to None,
        data from all cp's will be read.  (default=None)
    fileType : (str)
        The type of data you want to read.  valid inputs are: 'fitex','fitacf',
        'lmfit','rawacf','iqdat'.   If you choose a fit file format and the
        specified one isn't found, we will search for one of the others.
        Beware: if you ask for rawacf/iq data, these files are large and the
        data transfer might take a long time.  (default='fitex')
    filtered : (boolean)
        A boolean specifying whether you want the fit data to be boxcar
        filtered.  ONLY VALID FOR FIT.  (default=False)
    src : (str/NoneType)
        The source of the data.  Valid inputs are 'local' 'sftp'.  If this is
        set to None, it will try all possibilites sequentially.  (default=None)
    fileName : (str/NoneType)
        The name of a specific file which you want to open.  (default=None)
    noCache : (boolean)
        Flag to indicate that you do not want to check first for cached files.
        (default=False)
    remote_site : (str/NoneType)
        The remote data server's address.  If None, the rcParam value DB will be
        used. (default=None)
    port : (str/NoneType)
        The port number to use for remote_site.  If None, the rcParam value
        DB_PORT will be used. (default=None)
    username : (str/NoneType)
        Username for remote_site.  If None, the rcParam value DBREADUSER will
        be used. (default=None)
    password : (str/bool/NoneType)
        Password for remote_site. If password is set to True, the user is
        prompted for the remote_site password.  If set to None, the rcParam
        value DBREADPASS will be used (default=None)
    remote_dirfmt : (str/NoneType)
        The remote_site directory structure. Can include keywords to be
        replaced by dictionary keys in remote_dict.  If None, the rcParam value
        DAVIT_REMOTE_DIRFORMAT will be used. (default=None)
        Ex) remote_dirfmt='/{year}/{month}'
    remote_fnamefmt : (str/list/NoneType)
        The remote_site file naming format. Can include keywords to be replaced
        by dictionary keys in remote_dict. If None, the rcParam value
        DAVIT_REMOTE_FNAMEFMT will be used.  (default=None)
        Ex) remote_fnamefmt=['{date}.{radar}.{ftype}',
                             '{date}.{channel}.{radar}.{ftype}']
    local_dirfmt : (str/None)
        The local directory structure. Can include keywords to be replaced by
        dictionary keys in remote_dict. If None, the rcParam value
        DAVIT_LOCAL_DIRFORMAT will be used. (default=None)
        Ex) local_dirfmt='/{year}/{month}' 
    local_fnamefmt : (str/list/NoneType)
        The local file naming format. Can include keywords to be replaced by
        dictionary keys in remote_dict. If None, the rcParam value
        DAVIT_LOCAL_FNAMEFMT will be used. (default=None)
        Ex) local_fnamefmt=['{date}.{radar}.{ftype}',
                            '{date}.{channel}.{radar}.{ftype}']
    tmpdir : (str/NoneType)
        The directory in which to store temporary files. If None, the rcParam
        value DAVIT_TMPDIR will be used. (default=None)
    remove : (bool)
        Remove compressed file after uncompression (default=False)
    try_file_types : (bool)
        If desired file type could not be found, try to download others
        (default=True)

    Returns
    --------
    myPtr : (pydarn.sdio.radDataTypes.radDataPtr)
        A radDataPtr object which contains a link to the data to be read.
        This can then be passed to radDataReadRec in order to actually read the
        data.

    Notes
    -------
    The evironment variables are python dictionary capable formatted strings
    appended encode radar name, channel, and/or date information. Currently
    supported dictionary keys which can be used are: 

    "date"    : datetime.datetime.strftime("%Y%m%d")
    "year"    : 0 padded 4 digit year 
    "month"   : 0 padded 2 digit month 
    "day"     : 0 padded 2 digit day 
    "hour"    : 0 padded 2 digit day 
    "ftype"   : filetype string
    "radar"   : 3-chr radarcode 
    "channel" : single character string, ex) 'a'

    Example
    ----------
    ::

    import datetime as dt
    myPtr = pydarn.sdio.radDataOpen(dt.datetime(2011,1,1),'bks', \
                  eTime=dt.datetime(2011,1,1,2),channel=None, bmnum=7,cp=153, \
                  fileType='fitex',filtered=False, src=None)

    Written by AJ 20130110
    """
    from davitpy.pydarn.sdio import radDataPtr
    from davitpy.pydarn.radar import network

    myPtr = radDataPtr(sTime=sTime, radcode=radcode, eTime=eTime,
                       channel=channel, bmnum=bmnum, cp=cp, fileType=fileType,
                       filtered=filtered, src=src, fileName=fileName,
                       noCache=noCache, local_dirfmt=local_dirfmt,
                       local_fnamefmt=local_fnamefmt, local_dict=local_dict,
                       remote_dirfmt=remote_dirfmt, remote_dict=remote_dict,
                       remote_fnamefmt=remote_fnamefmt, remote_site=remote_site,
                       username=username, port=port, password=password,
                       stid=int(network().getRadarByCode(radcode).id),
                       tmpdir=tmpdir, remove=remove,
                       try_file_types=try_file_types)
    return myPtr
  
def radDataReadRec(my_ptr):
    """A function to read a single record of radar data from a
    :class:`pydarn.sdio.radDataTypes.radDataPtr` object

    Parameters
    ------------
    my_ptr : (pydarn.sdio.radDataTypes.radDataPtr)
        Contains the pipeline to the data we are after.

    Returns
    ---------
    my_beam : (pydarn.sdio.radDataTypes.beamData/NoneType)
        An object filled with the data we are after.  Will return None when
        finished reading.
    
    Example
    ---------
    ::
    
    import datetime as dt
    my_ptr = radDataOpen(dt.datetime(2011,1,1),'bks', \
                   eTime=dt.datetime(2011,1,1,2),channel=None,bmnum=7,cp=153,
                   fileType='fitex',filtered=False,src=None)
    my_beam = radDataReadRec(my_ptr)
    
    Notes
    ------
    To use this, you must first create a
    :class:`pydarn.sdio.radDataTypes.radDataPtr` object with
    :func:`radDataOpen` 

    Written by AJ 20130110
    """
    from davitpy.pydarn.sdio import radDataPtr

    assert isinstance(my_ptr, radDataPtr), \
      logging.error('input must be of type radDataPtr')

    return my_ptr.readRec()
      
def radDataReadScan(my_ptr):
    """A function to read a full scan of data from a
    :class:`pydarn.sdio.radDataTypes.radDataPtr` object
  
    Parameters
    -----------
    my_ptr : (pydarn.sdio.radDataTypes.radDataPtr)
        Contains the pipeline to the data we are after

    Returns
    --------
    my_scan : (pydarn.sdio.radDataTypes.scanData)
        A class created to define a list of pydarn.sdio.radDataTypes.beamData
        objects, filled with a scan (pattern of beams) of data from the
        specified pipeline.  The pointer will return None when finished reading.

    Example
    --------
    ::
    
    import datetime as dt
    my_ptr = radDataOpen(dt.datetime(2011,1,1),'bks', \
                  eTime=dt.datetime(2011,1,1,2),channel=None, bmnum=7,cp=153, \
                  fileType='fitex',filtered=False, src=None):
    my_scan = radDataReadScan(my_ptr)

    Notes
    -------
    To use this, you must first create a
    :class:`pydarn.sdio.radDataTypes.radDataPtr` object with :func:`radDataOpen`

    This will ignore any beam number (bmnum) request.  Also, if no channel was
    specified in radDataOpen, it will only read channel 'a'

    Written by AJ 20130110
    """
    from davitpy.pydarn.sdio import radDataPtr

    # check input
    assert isinstance(my_ptr, radDataPtr), \
      logging.error('input must be of type radDataPtr')

    return my_ptr.readScan()

def radDataCreateIndex(my_ptr):
    """A function to index radar data into dict from a
    :class:`pydarn.sdio.radDataTypes.radDataPtr` object
  
    Parameters
    -----------
    my_ptr : (pydarn.sdio.radDataTypes.radDataPtr)
        Contains the pipeline to the data we are after

    Returns
    --------
    my_index : (dict)
        A dictionary with keys recording the time of each bean in the specified
        pointer and the value corresponding to the location for that record
        in the data file (byte offsets in the file). 
    
    Example
    ---------
    ::

    import datetime as dt
    my_ptr = radDataOpen(dt.datetime(2011,1,1),'bks', \
                   eTime=dt.datetime(2011,1,1,2),channel=None, bmnum=7,cp=153, \
                   fileType='fitex',filtered=False, src=None)
    my_index = radDataCreateIndex(my_ptr)
    
    Notes
    ------
    To use this, you must first create a
    :class:`pydarn.sdio.radDataTypes.radDataPtr` object with :func:`radDataOpen`

    Written by JDS 20140606
    """
    from davitpy.pydarn.sdio.radDataTypes import radDataPtr

    assert isinstance(my_ptr, radDataPtr), \
      logging.error('input must be of type radDataPtr')

    return my_ptr.createIndex() 

def radDataReadAll(my_ptr):
    """A function to read a large amount (to the end of the request) of radar
    data into a list from a :class:`pydarn.sdio.radDataTypes.radDataPtr` object

    Parameters
    -----------
    my_ptr : (pydarn.sdio.radDataTypes.radDataPtr)
        Contains the pipeline to the data we are after

    Returns
    ----------
    my_list : (list)
        A list filled with pydarn.sdio.radDataTypes.scanData objects holding
        the data we are after.  The list will contain None if nothing is found.

    Example
    -----------
    ::
    
    import datetime as dt
    my_ptr = radDataOpen(dt.datetime(2011,1,1),'bks', \
             eTime=dt.datetime(2011,1,1,2),channel=None, bmnum=7,cp=153, \
             fileType='fitex',filtered=False, src=None)
    my_list = radDataReadAll(my_ptr)

    Notes
    ------
    To use this, you must first create a
    :class:`pydarn.sdio.radDataTypes.radDataPtr` object with :func:`radDataOpen`

    Written by AJ 20130606
    """
    from davitpy.pydarn.sdio import radDataPtr
  
    # check input
    assert isinstance(my_ptr, radDataPtr), \
      logging.error('input must be of type radDataPtr')

    my_list = [beam for beam in my_ptr]

    return my_list
