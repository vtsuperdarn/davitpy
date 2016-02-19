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

"""A module for reading processed SD data (grid, map)

.. moduleauthor:: AJ, 20130607

************************************
Module: pydarn.sdio.sdDataRead
************************************

Functions
------------
sdDataOpen
sdDataReadRec
sdDataReadAll
"""

import logging

def sdDataOpen(stime, hemi='north', eTime=None, src=None, fileName=None,
               fileType='grdex', noCache=False, local_dirfmt=None,
               local_fnamefmt=None, local_dict=None, remote_dirfmt=None,
               remote_fnamefmt=None, remote_dict=None, remote_site=None,
               username=None, password=None, port=None, tmpdir=None):
    """A function to establish a pipeline through which we can read radar data.
    first it tries the mongodb, then it tries to find local files, and lastly
    it sftp's over to the VT data server.

    Parameters
    ------------
    stime : (datetime)
        The beginning time for which you want data
    hemi : (str)
        The hemisphere for which you want data, 'north' or 'south'.
        (default='north')
    eTime : (datetime or NoneType)
        The last time that you want data for.  If this is set to None, it will
        be set to 1 day after stime.  (default=None)
    src : (str or NoneType)
        the source of the data.  Valid inputs are 'local', 'sftp', or None.
        If this is set to None, it will try all possibilites sequentially.
        (default=None)
    fileName : (str)
        the name of a specific file which you want to open.  (default=None)
    fileType : (str)
        The type of data you want to read.  Valid inputs are 'grd', 'grdex',
        'map', and 'mapex'.  If you choose a file format and the specified one
        isn't found, we will search for one of the others (eg mapex instead of
        map). (default='grdex')
    noCache : (boolean)
        flag to indicate that you do not want to check first for cached files.
        (default=False)
    remote_site : (str or NoneType)
        The remote data server's address. If None, the rcParam value DB will be
        used. (default=None)
    port : (str or NoneType)
        The port number to use for remote_site.  If None, the rcParam value
        DB_PORT will be used.  (default=None)
    username : (str or NoneType)
        Username for remote_site.  If None, the rcParam value DBREADUSER will
        be used. (default=None)
    password : (str, bool or NoneType)
        Password for remote_site. If password is set to True, the user is
        prompted for the remote_site password.  If set to None, the rcParam
        value DBREADPASS will be used. (default=None)
    remote_dirfmt : (str or NoneType)
        The remote_site directory structure. Can include keywords to be replaced
        by dictionary keys in remote_dict.  If None, the rcParam value
        DAVIT_REMOTE_DIRFORMAT will be used. (default=None)
         ex) remote_dirfmt='/{year}/{month}'
    remote_fnamefmt : (str/list or NoneType)
        The remote_site file naming format. Can include keywords to be replaced
        by dictionary keys in remote_dict. If None, the rcParam value
        DAVIT_REMOTE_FNAMEFMT will be used.  (default=None)
        example: remote_fnamefmt=['{date}.{radar}.{ftype}',
                                  '{date}.{channel}.{radar}.{ftype}']
    local_dirfmt : (str or NoneType)
        The local directory structure. Can include keywords to be replaced by
        dictionary keys in remote_dict. If None, the rcParam value
        DAVIT_LOCAL_DIRFORMAT will be used. (default=None)
        ex) remote_dirfmt='/{year}/{month}'
    local_fnamefmt : (str/list or NoneType)
        The local file naming format. Can include keywords to be replaced by
        dictionary keys in remote_dict.  If None, the rcParam value
        DAVIT_LOCAL_FNAMEFMT will be used.  (default=None)
        example: remote_fnamefmt=['{date}.{radar}.{ftype}',
                                  '{date}.{channel}.{radar}.{ftype}']
    tmpdir : (str or NoneType)
        The directory in which to store temporary files.  If None, the rcParam
        value DAVIT_TMPDIR will be used. (default=None)

    Returns
    ---------
    my_ptr : (sdDataPtr or NoneType)
        A sdDataPtr object which contains a link to the data to be read. This
        can then be passed to sdDataReadRec in order to actually read the data.
        If this is empty, None will be returned.

    Notes
    -------
    The evironment variables are python dictionary capable formatted strings
    appended encode radar name, channel, and/or date information. Currently
    supported dictionary keys which can be used are: 

    'date'    : datetime.datetime.strftime("%Y%m%d")
    'year'    : 0 padded 4 digit year 
    'month'   : 0 padded 2 digit month 
    'day'     : 0 padded 2 digit day 
    'hour'    : 0 padded 2 digit day 
    'ftype'   : filetype string
    'hemi'    : hemisphere

    Written by AJ 20130607
    """
    from davitpy.pydarn.sdio.sdDataTypes import sdDataPtr

    my_ptr = sdDataPtr(sTime=stime, hemi=hemi, eTime=eTime, src=src,
                       fileType=fileType, fileName=fileName, noCache=noCache,
                       local_dirfmt=local_dirfmt, local_fnamefmt=local_fnamefmt,
                       local_dict=local_dict, remote_dirfmt=remote_dirfmt,
                       remote_fnamefmt=remote_fnamefmt, remote_dict=remote_dict,
                       remote_site=remote_site, username=username,
                       password=password, port=port, tmpdir=tmpdir)

    return my_ptr

def sdDataReadRec(my_ptr):
    """A function to read a single record of radar data from a sdDataPtr object

    Parameters
    -----------
    my_ptr : (sdDataPtr)
        Contains the pipeline to the data we are after

    Returns
    ---------
    my_data : (gridData or mapData or NoneType)
        An object filled with the data we are after.  Will return None when
        finished reading the file.

    Example
    --------
    ::
    
    import datetime as dt
    my_ptr = sdDataOpen(dt.datetime(2011,1,1), 'south')
    my_data = sdDataReadRec(my_ptr)

    Notes
    -------
    To use this, you must first create a sdDataPtr object with sdDataOpen

    Written by AJ 20130610
    """
    from davitpy.pydarn.sdio.sdDataTypes import sdDataPtr

    assert isinstance(my_ptr, sdDataPtr), \
        logging.error('input must be of type sdDataPtr')

    return my_ptr.readRec() 

def sdDataCreateIndex(my_ptr):
    """A function to index radar data into dict from a sdDataPtr object

    Parameters
    ------------
    my_ptr : (sdDataPtr)
        Contains the pipeline to the data we are after

    Returns
    ----------
    my_index : (dict)
        Keys are record timedate objects and values are byte offsets into the
        file. 

    Example
    --------
    ::
    import datetime as dt
    my_ptr = sdDataOpen(dt.datetime(2011,1,1), 'south')
    my_index = radDataCreateIndex(my_ptr)

    Notes
    -------
    To use this, you must first create a sdDataPtr object with sdDataOpen

    Written by JDS 20140606
    """
    from davitpy.pydarn.sdio.sdDataTypes import sdDataPtr
    assert isinstance(my_ptr,sdDataPtr), \
        logging.error('input must be of type sdDataPtr')

    return my_ptr.createIndex()

def sdDataReadAll(my_ptr):
    """A function to read a large amount (to the end of the request) of radar
    data into a list from a sdDataPtr object

    Notes
    -------
    To use this, you must first create a sdDataPtr object with sdDataOpen

    Parameters
    -----------
    my_ptr : (sdDataPtr)
        Contains the pipeline to the data we are after

    Returns
    ---------
    my_list : (list or NoneType)
        A list filled with gridData or mapData objects holding the data we are
        after.  Vill return None if nothing is found.
 
    Examples
    ---------
    ::
    import datetime as dt
    my_ptr = sdDataOpen(dt.datetime(2011,1,1), 'south')
    my_list = sdDataReadAll(my_ptr)

    Written by AJ 20130606
    """
    from davitpy.pydarn.sdio.sdDataTypes import sdDataPtr

    # check input
    assert isinstance(my_ptr, sdDataPtr), \
        logging.error('input must be of type sdDataPtr')

    my_list = [beam for beam in my_ptr]
    return my_list
