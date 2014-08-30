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
.. module:: sdDataRead
   :synopsis: A module for reading processed SD data (grid, map)

.. moduleauthor:: AJ, 20130607

************************************
**Module**: pydarn.sdio.sdDataRead
************************************

**Functions**:
  * :func:`pydarn.sdio.sdDataRead.sdDataOpen`
  * :func:`pydarn.sdio.sdDataRead.sdDataReadRec`
  * :func:`pydarn.sdio.sdDataRead.sdDataReadAll`
"""

def sdDataOpen(sTime,hemi='north',eTime=None, src=None,fileName=None, \
          fileType='grdex',noCache=False,verbose=False,local_dirfmt=None,\
          local_fnamefmt=None,local_dict=None,remote_dirfmt=None,  \
          remote_fnamefmt=None,remote_dict=None,local_timeinc=None,\
          remote_timeinc=None,remote_site=None,username=None,      \
          password=None, port=None,tmpdir=None):

  """A function to establish a pipeline through which we can read radar data.  first it tries the mongodb, then it tries to find local files, and lastly it sftp's over to the VT data server.

  **Args**:
    * **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the beginning time for which you want data
    * **[hemi]** (str): the hemisphere for which you want data, 'north' or 'south'.  default = 'north'
    * **[eTime]** (`datetime <http://tinyurl.com/bl352yx>`_): the last time that you want data for.  if this is set to None, it will be set to 1 day after sTime.  default = None
    * **[src]** (str): the source of the data.  valid inputs are 'local' 'sftp'.  if this is set to None, it will try all possibilites sequentially.  default = None
    * **[fileName]** (str): the name of a specific file which you want to open.  default=None
    * **[fileType]** (str):  The type of data you want to read.  valid inputs are: 'grd','grdex','map','mapex'.  If you choose a file format and the specified one isn't found, we will search for one of the others (eg mapex instead of map). default = 'grdex'.
    * **[noCache]** (boolean): flag to indicate that you do not want to check first for cached files.  default = False.
    * **[verbose]** (boolean): Be very verbose about file fetching and reading. default=False
    * **[remote_site]** (str): The remote data server's address.
    * **[port]** (str): The port number to use for remote_site.
    * **[username]** (str): Username for remote_site.
    * **[password]** (str/bool): Password for remote_site. If password is set to True, the user is prompted for the remote_site password.
    * **[remote_dirfmt]** (str): The remote_site directory structure. Can include keywords to be replaced by dictionary keys in remote_dict. ex) remote_dirfmt='/{year}/{month}'
    * **[remote_fnamefmt]** (str/list): The remote_site file naming format. Can include keywords to be replaced by dictionary keys in remote_dict. ex) remote_fnamefmt=['{date}.{radar}.{ftype}','{date}.{channel}.{radar}.{ftype}']
    * **[remote_timeinc]** (str): The time increment between remote_site files. Must be given in hours.
    * **[local_dirfmt]** (str): The local directory structure. Can include keywords to be replaced by dictionary keys in remote_dict. ex) remote_dirfmt='/{year}/{month}' 
    * **[local_fnamefmt]** (str/list): The local file naming format. Can include keywords to be replaced by dictionary keys in remote_dict. ex) remote_fnamefmt=['{date}.{radar}.{ftype}','{date}.{channel}.{radar}.{ftype}']
    * **[local_timeinc]** (str): The time increment between locally stored files. Must be given in hours.
    * **[tmpdir]** (str): The directory in which to store temporary files.

  **Returns**:
    * **myPtr** (:class:`pydarn.sdio.sdDataTypes.sdDataPtr`): a sdDataPtr object which contains a link to the data to be read.  this can then be passed to sdDataReadRec in order to actually read the data.
    
  **ENVIRONMENT Variables**:
    * DB                        : Used to specify the DB address (overridden by remote_site).
    * DB_PORT                   : Used to specify the DB port (overridden by port).
    * DBREADUSER                : Used to specify the DB user username (overridden by username).
    * DBREADPASS                : Used to specify the DB user password (overridden by password).
    * DAVIT_SD_REMOTE_DIRFORMAT : Used to specify the remote data directory structure (overridden by remote_dirfmt).
    * DAVIT_SD_REMOTE_FNAMEFMT  : Used to specify the remote filename format (overridden by remote_fnamefmt).
    * DAVIT_SD_REMOTE_TIMEINC   : Used to specify the remote time increment between files (overridden by remote_timeinc).
    * DAVIT_SD_LOCAL_DIRFORMAT  : Used to specify the local data directory structure (overridden by local_dirfmt).
    * DAVIT_SD_LOCAL_FNAMEFMT   : Used to specify the local filename format (overridden by local_fnamefmt).
    * DAVIT_SD_LOCAL_TIMEINC    : Used to specify the local time increment between files (overridden by local_timeinc).
    * DAVIT_TMPDIR              : Directory used for davitpy temporary file cache (overridden by tmpdir).

    The evironment variables are python dictionary capable formatted strings appended encode radar name, channel, and/or date information. Currently supported dictionary keys which can be used are: 

    "date"    : datetime.datetime.strftime("%Y%m%d")
    "year"    : 0 padded 4 digit year 
    "month"   : 0 padded 2 digit month 
    "day"     : 0 padded 2 digit day 
    "hour"    : 0 padded 2 digit day 
    "ftype"   : filetype string
    "hemi"    : hemisphere

  **Example**:
    ::
    
      import datetime as dt
      myPtr = sdDataOpen(dt.datetime(2011,1,1),hemi='north'):
    
  Written by AJ 20130607
  """

  from pydarn.sdio import sdDataPtr

  myPtr = sdDataPtr(sTime=sTime,hemi=hemi,eTime=eTime, src=src, \
            fileType=fileType,fileName=fileName,noCache=noCache, \
            verbose=verbose,local_dirfmt=local_dirfmt, \
            local_fnamefmt=local_fnamefmt,local_dict=local_dict, \
            remote_dirfmt=remote_dirfmt,remote_fnamefmt=remote_fnamefmt, \
            remote_dict=remote_dict,local_timeinc=local_timeinc, \
            remote_timeinc=remote_timeinc,remote_site=remote_site, \
            username=username,password=password,port=port,tmpdir=tmpdir)

  return myPtr


def sdDataReadRec(myPtr):
  """A function to read a single record of radar data from a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object
  
  .. note::
    to use this, you must first create a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object with :func:`sdDataOpen` 

  **Args**:
    * **myPtr** (:class:`pydarn.sdio.sdDataTypes.sdDataPtr`): contains the pipeline to the data we are after
  **Returns**:
    * **myData** (:class:`pydarn.sdio.sdDataTypes.gridData` or :class:`pydarn.sdio.sdDataTypes.mapData`): an object filled with the data we are after.  *will return None when finished reading the file*
    
  **Example**:
    ::
    
      import datetime as dt
      myPtr = sdDataOpen(dt.datetime(2011,1,1),'south')
      myData = sdDataReadRec(myPtr)
    
  Written by AJ 20130610
  """

  from pydarn.sdio.sdDataTypes import sdDataPtr
  assert(isinstance(myPtr,sdDataPtr)),\
    'error, input must be of type sdDataPtr'

  return myPtr.readRec() 

def sdDataCreateIndex(myPtr):
  """A function to index radar data into dict from a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object
  
  .. note::
    to use this, you must first create a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object with :func:`sdDataOpen`

  **Args**:
    * **myPtr** (:class:`pydarn.sdio.sdDataTypes.sdDataPtr`): contains the pipeline to the data we are after
  **Returns**:
    * **myIndex** (dict): keys are record timedate objects and values are byte offsets into the file. 
    
  **Example**:
    ::
    
      import datetime as dt
      myPtr = sdDataOpen(dt.datetime(2011,1,1),'south')
      myIndex = radDataCreateIndex(myPtr)
    
  Written by JDS 20140606
  """
  from pydarn.sdio.sdDataTypes import sdDataPtr
  assert(isinstance(myPtr,sdDataPtr)),\
    'error, input must be of type sdDataPtr'
  return myPtr.createIndex()


def sdDataReadAll(myPtr):
  """A function to read a large amount (to the end of the request) of radar data into a list from a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object
  
  .. note::
    to use this, you must first create a :class:`pydarn.sdio.sdDataTypes.sdDataPtr` object with :func:`sdDataOpen`

  **Args**:
    * **myPtr** (:class:`pydarn.sdio.sdDataTypes.sdDataPtr`): contains the pipeline to the data we are after
  **Returns**:
    * **myList** (list): a list filled with :class:`pydarn.sdio.sdDataTypes.gridData` or :class:`pydarn.sdio.sdDataTypes.mapData` objects holding the data we are after.  *will return None if nothing is found*
    
  **Example**:
    ::
    
      import datetime as dt
      myPtr = sdDataOpen(dt.datetime(2011,1,1),'south')
      myList = sdDataReadAll(myPtr)
    
  Written by AJ 20130606
  """
  from pydarn.sdio.sdDataTypes import sdDataPtr
  
  #check input
  assert(isinstance(myPtr,sdDataPtr)),\
    'error, input must be of type sdDataPtr'
  myList=[beam for beam in myPtr]
  return myList

