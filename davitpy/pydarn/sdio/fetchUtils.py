#!/usr/bin/env python
#-----------------------------------------------------------------------------
# $Id: $
#
# fetchUtils.py, Angeline G. Burrell (AGB), UoL
#-----------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------
"""
.. module:: pydarn.sdio.fetchUtils
   :synopsis: Routines to fetch SuperDARN radar data locally and remotely

.. moduleauthor:: Angeline G. Burrell, UoL

************************************
**Module**: pydarn.sdio.fetchUtils
************************************

**Functions**:
  * :func:`pydarn.sdio.fetchUtils.uncompress_file`
  * :func:`pydarn.sdio.fetchUtils.fetch_local_files`
  * :func:`pydarn.sdio.fetchUtils.fetch_remote_files`

Contains: uncompress_file    - uncompresses a file using various methods
          fetch_local_files  - uncompress and copy local files to a temporary
                               directory
          fetch_remote_files - download and uncompress files from a specified
                               server to a temporary directory
"""

import datetime as dt
from dateutil.relativedelta import relativedelta

def uncompress_file(filename, outname=None, verbose=True):
    """
    A function to perform an appropriate type of uncompression on a specified 
    file.  Current extensions include: bz2, gz, zip. This function does not 
    removed the compressed file. Requires bunzip2, gunzip, and unzip to be 
    installed.

    **Inputs**: 
        * **filename**     (str): name of the compressed file
        * **outname**      (nonetype/str): compressed name of the desired output file
                                          (allows uncompressed file to be placed in
                                          a different location) or None (if the
                                          uncompressed file will stay in the same
                                          directory).  (default=None)
        * **verbose**      (bool): Print warnings and errors? (default=True)

    **Output**: 
        * **outname**      (nonetype/str): name of uncompressed file or None if the
                                          command was unsuccessful or the compression 
                                          method could not be determined

    """

    #from copy import deepcopy as dc
    import os

    rn = "uncompress_files"

    #Check the inputs
    assert(isinstance(filename,str)), \
    'error, filename must be a string'
    assert(isinstance(outname,(str,type(None)))), \
    'error, outname must be a string or None'
    assert(isinstance(verbose,bool)), \
    'error, verbose must be True or False'

    command = None  #Initialize command as None. It will be updated 
                    #if a known file compression is found.

    if (outname is None):
        outname = filename #dc(filename)

    if (filename.find('.bz2') != -1):
        outname = outname.replace('.bz2','')
        command = 'bunzip2 -c '+filename+' > '+outname
    elif (filename.find('.gz') != -1):
        outname = outname.replace('.gz','')
        command = 'gunzip -c '+filename+' > '+outname
    elif (filename.find('.zip') != -1):
        outname = outname.replace('.zip','')
        command = 'unzip -c '+filename+' > '+outname
    #elif (filename.find('.tar') != -1):
    #    outname = outname.replace('.tar','')
    #    command = 'tar -xf '+filename

    if type(command) is str:
        try:
            os.system(command)
            if verbose: print rn,"ADVISEMENT: performed [",command,"]"
        except:
            if verbose:
                print rn,"WARNING: unable to perform [",command,"]"
            # Returning None instead of setting outname=None to avoid
            # messing with inputted outname variable
            return(None)
    else:
        return(None)
        if verbose:
            print rn, "WARNING: unknown compression type for [", filename, "]"

    return outname


def fetch_local_files(stime, etime, localdirfmt, localdict, outdir, fnamefmt,
                      verbose=True,back_time=relativedelta(years=1)):

    """
    A routine to locate and retrieve file names from locally stored SuperDARN 
    radar files that fit the input criteria.

    **Inputs**: 
        * **stime** (datetime): data starting time
        * **etime**      (datetime): data ending time
        * **localdirfmt**     (str): string defining the local directory structure
                                     (eg "{ftype}/{year}/{month}/{day}/")
        * **localdict**      (dict): Contains keys for non-time related information in remotedirfmt 
                                     and fnamefmt (eg remotedict={'ftype':'fitex','radar':'sas','channel':'a'})
        * **outdir**          (str): Temporary directory in which to store
                                     uncompressed files (must end with a "/")
        * **fnamefmt**   (str/list): Optional string or list of file name formats (eg 
                                     fnamefmt = ['{date}.{hour}......{radar}.{channel}.{ftype}', \
                                                '{date}.C0.{radar}.{ftype}'] 
                                     or fnamefmt = '{date}.{hour}......{radar}.{ftype}'
        * **[verbose]**        (bool): Print warnings or not? (default=True)
        * **[back_time]** (dateutil.relativedelta.relativedelta): Time difference from stime
                            that fetchUtils should search backwards until before giving up.

    **Output**: file_stime (datetime): actual starting time for located files
            filelist       (list): list of uncompressed files (including path)

    **Note**: Weird edge case behaviour occurs when attempting to fetch all channel data (e.g. localdict['channel'] = '.').

    **Example**:
      
      Fetches one locally stored fitacf file stored in a directory structure
      given by localdirfmt. The file name format is specified by the fnamefmt 
      arguement. 

      :: 

        from pydarn.sdio import fetchUtils
        import datetime as dt
        import os

        filelist = fetchUtils.fetch_local_files(dt.datetime(2002,6,20), \
            dt.datetime(2002,6,21), '/sd-data/{year}/{month}/',{'ftype':'fitacf'}, \
            "/tmp/sd/",'{date}.{hour}......{radar}.{channel}.{ftype}', \
            verbose=False)

    """

    #from dateutil.relativedelta import relativedelta
    import os
    import glob
    import re

    rn = "fetch_local_files"
    filelist = []
    temp_filelist = []

    # Test input
    assert(isinstance(stime, dt.datetime)), \
        (rn, 'ERROR: stime must be datetime object')
    assert(isinstance(etime,dt.datetime)), \
        (rn, 'ERROR: eTime must be datetime object')
    assert(isinstance(localdirfmt, str) and localdirfmt[-1] == "/"), \
        (rn, 'ERROR: localdirfmt must be a string ending in "/"')
    assert(isinstance(outdir, str) and outdir[-1] == "/"), \
        (rn, 'ERROR: outdir must be a string ending in "/"')
    assert(os.path.isdir(outdir)), (rn, "ERROR: outdir is not a directory")
    assert(isinstance(fnamefmt, (str,list))), \
        (rn, 'ERROR: fnamefmt must be str or list')
    assert(isinstance(verbose, bool)), (rn, 'ERROR: verbose must be Boolean')


    #--------------------------------------------------------------------------
    # If fnamefmt isn't a list, make it one.

    if isinstance(fnamefmt,str):
        fnamefmt = [fnamefmt]
      
    #--------------------------------------------------------------------------
    # Initialize the start time for the loop
    ctime = stime.replace(second=0, microsecond=0)
    time_reverse = 1
    mintime = ctime - back_time

    # construct a checkstruct dictionary to detect if changes in ctime
    # lead to a change in directory to limit how often directories are listed
    time_keys = ["year","month","day","hour","min","date"]
    keys_in_localdir = [x for x in time_keys if localdirfmt.find('{'+x+'}') > 0 ]

    checkstruct={}
    for key in keys_in_localdir:
      checkstruct[key]=''

    while ctime <= etime:

        # set the temporal parts of the possible local directory structure
        localdict["year"] = "{:04d}".format(ctime.year)
        localdict["month"] = "{:02d}".format(ctime.month)
        localdict["day"] = "{:02d}".format(ctime.day)
        localdict["hour"] = ctime.strftime("%H")
        localdict["min"] = ctime.strftime("%M")
        localdict["date"] = ctime.strftime("%Y%m%d")
        
        # check for a directory change
        dir_change = 0
        for key in keys_in_localdir:
            if (checkstruct[key] != localdict[key]):
                checkstruct[key] = localdict[key]    
                dir_change = 1   

        # get the files in the directory if directory has changed
        if dir_change:
          local_dir = localdirfmt.format(**localdict)
          try:
              files = os.listdir(local_dir)
          except:
              files = []

        # check to see if any files in the directory match the fnamefmt
        for namefmt in fnamefmt:

            # create a regular expression to check for the desired files
            name = namefmt.format(**localdict)
            regex = re.compile(name)

            # Go thorugh all the files in the directory
            for lf in files:

                #if we have a file match between a file and our regex
                if(regex.match(lf)):
                    if lf in temp_filelist: 
                        continue
                    else:
                        temp_filelist.append(lf)

                    # copy the file to outdir
                    outname = os.path.join(outdir,lf)
                    command='cp {:s} {:s}'.format(os.path.join(local_dir,lf), outname)
                    try:    
                        os.system(command)
                        if verbose: print rn, "ADVISEMENT: performed [",command,"]"
                    except:
                        if verbose: print rn, "WARNING: unable to perform [",command,"]"

        # Advance the cycle time by the "lowest" time increment 
        # in the namefmt (either forward or reverse)

        if ((time_reverse == 1) and (len(temp_filelist) > 0)) or \
                (ctime < mintime):
            time_reverse = 0
            ctime = stime.replace(second=0, microsecond=0)

        # Calculate if we are going forward or backward in time and set
        # ctime accordingly
        base_time_inc = 1 - 2*time_reverse        

        if ("{min}" in namefmt):
            ctime = ctime + relativedelta(minutes=base_time_inc)
        elif ("{hour}" in namefmt):
            ctime = ctime + relativedelta(hours=base_time_inc)
        elif (("{date}" in namefmt) or ("{day}" in remotedirfmt)):
            ctime = ctime + relativedelta(days=base_time_inc)
        elif ("{month}" in namefmt):
            ctime = ctime + relativedelta(months=base_time_inc)
        elif ("{year}" in namefmt):    
            ctime = ctime + relativedelta(years=base_time_inc)

    # Make sure the found files are in order.  Otherwise the concatenation later
    # will put records out of order
    temp_filelist = sorted(temp_filelist)
    # attempt to unzip the files
    for lf in temp_filelist:
        outname = os.path.join(outdir,lf)
        uncompressed = uncompress_file(outname, None, verbose)

        if (type(uncompressed) is str):
        # save name of uncompressed file for output
            filelist.append(uncompressed)
        else:
        # file wasn't compressed, use outname
            filelist.append(outname)

    # Return the list of uncompressed files
    return filelist


def fetch_remote_files(stime, etime, method, remotesite, remotedirfmt,
                       remotedict, outdir, fnamefmt, username=None, password=False,
                       port=None, verbose=True, check_cache=True,
                       back_time=relativedelta(years=1)):
    """
    A routine to locate and retrieve file names from remotely stored 
    SuperDARN radar files that fit the input criteria.

    **Inputs**: 
      * **stime**       (datetime): data starting time
      * **etime**       (datetime): data ending time
      * **method**           (str): remote connection method (eg sftp, http)
      * **remotesite**       (str): remote site address (eg 'sd-data.ece.vt.edu')
      * **remotedirfmt**     (str): string defining the remote directory
                                    structure (eg "{ftype}/{year}/{month}/{day}/")
      * **remotedict**      (dict): Contains keys for non-time related information in remotedirfmt 
                                    and fnamefmt (eg remotedict={'ftype':'fitex','radar':'sas','channel':'a'})
      * **outdir**           (str): Temporary directory in which to store
                                    uncompressed files (must end with a "/")
      * **fnamefmt**    (str/list): Optional string or list of file name formats (eg 
                                    fnamefmt = ['{date}.{hour}......{radar}.{channel}.{ftype}', \
                                                '{date}.C0.{radar}.{ftype}'] 
                                    or fnamefmt = '{date}.{hour}......{radar}.{ftype}'
      * **username**         (str): Optional input for remote access
      * **password**    (bool/str): Optional input for remote access.  True will
                                    prompt the user for a password, False
                                    indicates no password is needed, unsecured
                                    passwords may be entered as a string
                                    (default=False)
      * **port**             (str): Optional input for http file access
                                    (default=None)
      * **verbose**         (bool): Print out warnings? (default=True)
      * **[back_time]** (dateutil.relativedelta.relativedelta): Time difference from stime
                            that fetchUtils should search backwards until before giving up.

    **Outputs**: 
      * **file_stime**  (datetime): actual starting time for located files
      * **filelist**        (list): list of uncompressed files (including path)

    **Note**: Weird edge case behaviour occurs when attempting to fetch all channel data (e.g. remotedict['channel'] = '.').

    **Example**: 
             Fetches 3 remotely stored fitex files from the Virginia Tech
             database using sftp. The directory structure is specified by
             the remotedirfmt argument. The file name format is specified 
             by the fnamefmt arguement. 

      ::

        from pydarn.sdio import fetchUtils
        import datetime as dt

        fitex = fetchUtils.fetch_remote_files(datetime(2013,11,30,22), datetime(2013,12,1,2), \
                 'sftp','sd-data2.ece.vt.edu','data/{year}/{ftype}/{radar}/', \ 
                 {'ftype':'fitex','radar':'mcm','channel':'a'}, '/tmp/sd/', \
                 '{date}.{hour}......{radar}.{channel}.{ftype}', username='sd_dbread', \
                 password='5d',verbose=False)

        print fitex
        ['/tmp/sd/20131130.2201.00.mcm.a.fitex',
         '/tmp/sd/20131201.0000.04.mcm.a.fitex',
         '/tmp/sd/20131201.0201.00.mcm.a.fitex']

    """

    from dateutil.relativedelta import relativedelta
    # getpass allows passwords to be entered without them appearing onscreen
    import getpass
    # paramiko is necessary to use sftp, pyCurl currently requires much fiddling
    import paramiko as p

    # NOTE: Could use the requests library instead ASR 18 July, 2014
    # import requests
    # urllib is best at transferring files of any type using non-sftp protocols
    import urllib
    # urllib2 is best at finding the files available using non-sftp protocols
    import urllib2

    import os
    import re

    rn = "fetch_remote_files"
    filelist = []
    temp_filelist = []

    #--------------------------------------------------------------------------
    # Test input
    assert(isinstance(stime, dt.datetime)), \
        (rn, 'ERROR: stime must be datetime object')
    assert(isinstance(etime,dt.datetime)), \
        (rn, 'ERROR: eTime must be datetime object')
    assert(method == 'sftp' or method == 'http' or method == 'ftp' or
           method == 'file'), \
        (rn, 'ERROR: method must be one of: sftp, http, ftp, or file.',
         'Other protocols may work but need testing')
    assert(isinstance(remotesite, str)), \
        (rn, 'ERROR: remotesite must be a string')
    assert(isinstance(remotedirfmt, str)), \
        (rn, 'ERROR: remotedirfmt must be a string')
    assert(isinstance(outdir, str) and outdir[-1] == "/"), \
        (rn, 'ERROR: outdir must be a string ending in "/"')
    assert(os.path.isdir(outdir)), (rn, "ERROR: outdir is not a directory")
    assert(isinstance(username, str) or username is None), \
        (rn, 'ERROR: username must be a string or None')
    assert(isinstance(password, str) or isinstance(password, bool)), \
        (rn, 'ERROR: password must be a string or Boolean')
    assert(isinstance(port, str) or port is None), \
        (rn, 'ERROR: port must be a string')
    assert(isinstance(fnamefmt, (str,list))), \
        (rn, 'ERROR: fnamefmt must be str or list')
    assert(isinstance(verbose, bool)), (rn, 'ERROR: verbose must be Boolean')

    #--------------------------------------------------------------------------
    # Initialize the unchanging parts of the remote access (not *) (not used +)
    # Possibilities are: method, *username, *password, host, port, *path,
    #                    +parameters, +query, +fragment
    # 'method://username:password@host:port/path;parameters?query#fragment'
    remoteaccess = dict()
    remoteaccfmt = "{method}://"
    remoteaccess['method'] = method

    if username is not None:
        remoteaccess['username'] = username
        remoteaccfmt += "{username}"

        if type(password) is str:
            remoteaccess['password'] = password
            remoteaccfmt += ":{password}"
        elif password is True:
            prompt = 'Password for {:s}@{:s}: '.format(username,remotesite)
            remoteaccess['password'] = getpass.getpass(prompt)
            remoteaccfmt += ":{password}"
        remoteaccfmt += "@"

    remoteaccess['host'] = remotesite
    remoteaccfmt += "{host}"

    if port is not None:
        remoteaccess['port'] = port
        remoteaccfmt += ":{port}"
    remoteaccfmt += "{path}"


    #--------------------------------------------------------------------------
    # Build the possible radar filenames for matching using re module

    if isinstance(fnamefmt,str):
        fnamefmt = [fnamefmt]

    #--------------------------------------------------------------------------
    # Perform method-specific initialization that does not require time info
    if method is "sftp":
        #create a transport object for use in sftp-ing
        transport = p.Transport((remotesite, 22))
        try:
            transport.connect(username=remoteaccess['username'],
                              password=remoteaccess['password'])
        except:
            print (rn, "ERROR: can't connect to", remotesite,
                  "with username and password")
            return filelist

        try:
            sftp = p.SFTPClient.from_transport(transport)
        except:
            print rn, "ERROR: cannot engage sftp client at", remotesite
            return filelist


    #--------------------------------------------------------------------------
    # Iterate through all of the hours in the request (round the starting time
    # down to the nearest even hour). ctime is the current iteration's time.


    #--------------------------------------------------------------------------
    # construct a checkstruct dictionary to detect if changes in ctime
    # lead to a change in directory to limit how often directories are listed
    time_keys = ["year","month","day","hour","min","date"]
    keys_in_remotedir = [x for x in time_keys if remotedirfmt.find('{'+x+'}') > 0 ]

    checkstruct={}
    for key in keys_in_remotedir:
      checkstruct[key]=''

    #--------------------------------------------------------------------------
    # Initialize the list of remote filenames
    remotefiles = []

    #--------------------------------------------------------------------------
    # Initialize the start time for the loop
    ctime = stime.replace(second=0, microsecond=0)
    time_reverse = 1
    mintime = ctime - back_time

    # Cycle through the specified times, first look "backwards" in time to cover
    # the edge case where file start time starts after ctime
    while ctime <= etime:

        #----------------------------------------------------------------------
        # Set the temporal parts of the possible remote directory structure
        remotedict["year"] = "{:04d}".format(ctime.year)
        remotedict["month"] = "{:02d}".format(ctime.month)
        remotedict["day"] = "{:02d}".format(ctime.day)
        remotedict["hour"] = ctime.strftime("%H")
        remotedict["min"] = ctime.strftime("%M")
        remotedict["date"] = ctime.strftime("%Y%m%d")

        #----------------------------------------------------------------------
        # Build the name of the remote files (uses wildcards)
        path = remotedirfmt.format(**remotedict)
        remoteaccess['path'] = path
 
        # check for a directory change
        dir_change = 0
        for key in keys_in_remotedir:
            if (checkstruct[key] != remotedict[key]):
                checkstruct[key] = remotedict[key]    
                dir_change = 1   
    
        # get the files in the directory if directory has changed
        if dir_change:

            # get the files in the directory
            # Get a list of all the files in the new remote directory
            if method is "sftp":
                try:
                    remotefiles = sftp.listdir(remoteaccess['path'])
                except:
                    if verbose: print rn, "WARNING: cannot access [", path, "]"
            else:
                # Any other method can use urllib2
                url = remoteaccfmt.format(**remoteaccess) # Build the url
                req = urllib2.Request(url) # Set up a request
                try:
                    # Establish a connection
                    response = urllib2.urlopen(req)
                    # Extract the available files.  Assumes that the filename
                    # will be the first reference in the line
                    remotefiles.append([f[f.find('<a href="') + 9:
                                 f[f.find('<a href="') + 9:-1].find('">')
                                 +f.find('<a href="') + 9]
                               for f in response.readlines()
                               if f.find('<a href="') >= 0])
    
                        # Close the connection
                    response.close()
                except:
                    if verbose:
                        print rn, "WARNING: unable to connect to [", url, "]"

    #----------------------------------------------------------------------
    # Search through the remote files for the ones we want and download them
    # Ensure that the list of remote files include those that can possibly
    # be a radar file: YYYYMMDD.HHMM.XX.RRR.ext (len is 22 for 1 char ext)  
        for namefmt in fnamefmt:
            if len(remotefiles) > 0:


                #fill in the date, time, and radar information using remotedict
                name = namefmt.format(**remotedict)
                
                # Create a regular expression to find files of this time
                regex = re.compile(name)

                # Go thorugh all the files in the directory
                for rf in remotefiles:
                    #if we have a file match between a file and our regex
                    if(regex.match(rf)):
                        if rf in temp_filelist: 
                            continue
                        else:
                            temp_filelist.append(str(rf))

                        tf = "{:s}{:s}".format(outdir, rf)

                        # Test to see if the temporary file already exists
                        try:
                            tfsize = int(os.stat(tf).st_size)
                        except:
                            tfsize = -1

                        if method is "sftp":
                            # Build the complete name of the remote file
                            rflong = "{:s}{:s}".format(remoteaccess['path'], rf)

                            # If a local file of some sort of size has been
                            # found, test to see if the size is identical to the
                            # remote file to prevent multiple downloads
                            if ((tfsize >= 0) and (check_cache)):
                                try:
                                    rfsize = int(sftp.stat(rflong).st_size)

                                    if rfsize != tfsize:
                                        tfsize = -1
                                    elif verbose:
                                        estr = "{:s} ADVISEMENT: ".format(rn)
                                        estr = "{:s}found tmp file".format(estr)
                                        print "{:s} {:s}".format(estr, tf)

                                except:
                                    tfsize = -1

                            if ((tfsize < 0) or (not check_cache)):
                                # Use the open sftp connection to get the file
                                try:
                                    sftp.get(rflong,tf)
                                    if verbose:
                                        estr = "{:s} ADVISEMENT: ".format(rn)
                                        estr = "{:s}downloading ".format(estr)
                                        print "{:s}file {:s}".format(estr, tf)
                                except:
                                    tf = None
                                    if verbose:
                                        estr = "{:s} ADVISEMENT: ".format(rn)
                                        estr = "{:s}can't retrieve ".format(estr)
                                        print "{:s}{:s}".format(estr,rflong)
                        else:
                            # Use a different connection method
                            furl = "{:s}{:s}".format(url, rf)

                            # If a local file of some sort of size has been
                            # found, test to see if the size is identical to the
                            # remote file to prevent multiple downloads
                            if ((tfsize >= 0) and (check_cache)):
                                f = urllib2.urlopen(furl)
                                if f.headers.has_key("Content-Length"):
                                    rfsize = int(f.headers["Content-Length"])
                                    if rfsize != tfsize:
                                        tfsize = -1
                                    elif verbose:
                                        estr = "{:s} ADVISEMENT: ".format(rn)
                                        estr = "{:s}found tmp file".format(estr)
                                        print "{:s} {:s}".format(estr, tf)
                                else:
                                    tfsize = -1

                            if ((tfsize < 0) or (not check_cache)):
                                try:
                                    urllib.urlretrieve(furl, tf)
                                    if verbose:
                                        estr = "{:s} ADVISEMENT: ".format(rn)
                                        estr = "{:s}downloading ".format(estr)
                                        print "{:s}file {:s}".format(estr, tf)
                                except:
                                    tf = None
                                    if verbose:
                                        estr = "{:s} ADVISEMENT: ".format(rn)
                                        estr = "{:s}can't retrieve".format(estr)
                                        print "{:s} {:s}".format(estr, furl)

                            

        # Advance the cycle time by the "lowest" time increment 
        # in the namefmt (either forward or reverse)
        if ((time_reverse == 1) and (len(temp_filelist) > 0)) or \
                (ctime < mintime):
            time_reverse = 0
            ctime = stime.replace(second=0, microsecond=0)

        # Calculate if we are going forward or backward in time and set
        #ctime accordingly
        base_time_inc = 1 - 2*time_reverse        

        if ("{min}" in namefmt):
            ctime = ctime + relativedelta(minutes=base_time_inc)
        elif ("{hour}" in namefmt):
            ctime = ctime + relativedelta(hours=base_time_inc)
        elif (("{date}" in namefmt) or ("{day}" in remotedirfmt)):
            ctime = ctime + relativedelta(days=base_time_inc)
        elif ("{month}" in namefmt):
            ctime = ctime + relativedelta(months=base_time_inc)
        elif ("{year}" in namefmt):    
            ctime = ctime + relativedelta(years=base_time_inc)

    # Make sure the found files are in order.  Otherwise the concatenation later
    # will put records out of order
    temp_filelist = sorted(temp_filelist)
    # attempt to unzip the files
    for rf in temp_filelist:
        outname = os.path.join(outdir,rf)
        uncompressed = uncompress_file(outname, None, verbose)

        if type(uncompressed) is str:
        # save name of uncompressed file for output
            filelist.append(uncompressed)
        else:
        # file wasn't compressed, use outname
            filelist.append(outname)


    #--------------------------------------------------------------------------
    # Return the actual file start time and the list of uncompressed files
    # after deleting the dictionary structure containing the password
    del remoteaccess

    return filelist


def test_fetchutils():

    tests = 3
    success = 0

    print "Testing fetchUtils.uncompress_files"
    print "    Testing .zip"
    try:
        uncompress_file('20121107.0201.00.kod.d.fitacf.zip',outname='test.fitacf')
        print "SUCCESS!"
        success += 1
    except:
        print "FAILED!"

    print "    Testing .bz2"
    try:
        uncompress_file('20121107.0201.00.kod.d.fitacf.bz2',outname='test.fitacf')
        print "SUCCESS!"
        success += 1
    except:
        print "FAILED!"

    print "    Testing .gz"
    try:
        uncompress_file('20121107.0201.00.kod.d.fitacf.gz',outname='test.fitacf')
        print "SUCCESS!"
        success += 1
    except:
        print "FAILED!"

    print "Finished testing. Success: {:s}/{:s}".format(str(success),str(tests))






if __name__=="__main__":

    import os
    from datetime import datetime,timedelta

    print "*************************************************"
    print "*************************************************"
    print "    Running examples of fetch_remote_files..."
    print "*************************************************"
    print "*************************************************"

    print "Attempting to fetch a mapex file from the VT server..."
    mapexFiles = fetch_remote_files(datetime(2012,11,24), datetime(2012,11,24,23,59),'sftp','sd-data2.ece.vt.edu','data/{year}/{ftype}/north/',{'ftype':'mapex'}, '/tmp/sd/','{date}.north.{ftype}', username='sd_dbread', password='5d', verbose=False)

    print "Expected the file: ['/tmp/sd/20121124.north.mapex']"
    print "Received the file: " + str(mapexFiles)


    print "*************************************************"


    print "Attempting to fetch map files from the usask server..."
    mapFiles = fetch_remote_files(datetime(2001,11,24), datetime(2001,11,24,23,59),'sftp','chapman.usask.ca','mapfiles/{year}/{month}/',{'ftype':'map'}, '/tmp/sd/',['{date}.{ftype}','{date}s.{ftype}'], username='davitpy', password='d4vitPY-usask',verbose=False)

    print "Expected the files: ['/tmp/sd/20011124.map', '/tmp/sd/20011124s.map']"
    print "Received the files: " + str(mapFiles)


    print "*************************************************"


    print "Attempting to fetch a fitex file from the VT server..."
    fitex = fetch_remote_files(datetime(2013,11,30,22), datetime(2013,12,1,2),'sftp','sd-data2.ece.vt.edu','data/{year}/{ftype}/{radar}/', {'ftype':'fitex','radar':'mcm','channel':'a'}, '/tmp/sd/','{date}.{hour}......{radar}.{channel}.{ftype}', username='sd_dbread', password='5d', verbose=False)

    print "Expected the files: ['/tmp/sd/20131130.2201.00.mcm.a.fitex','/tmp/sd/20131201.0000.04.mcm.a.fitex','/tmp/sd/20131201.0201.00.mcm.a.fitex']"
    print "Received the files: " + str(fitex)


    print "*************************************************"


    print "Attempting to fetch a fitex file from the VT server..."
    fitex = fetch_remote_files(datetime(2013,01,21,00), datetime(2013,01,21,05),'sftp','sd-data2.ece.vt.edu','data/{year}/{ftype}/{radar}/', {'ftype':'fitex','radar':'ade','channel':'a'}, '/tmp/sd/','{date}.{hour}......{radar}.{channel}.{ftype}', username='sd_dbread', password='5d', verbose=False)

    print "Expected the files: ['/tmp/sd/20130121.0001.00.ade.a.fitex','/tmp/sd/20130121.0201.00.ade.a.fitex','/tmp/sd/20130121.0349.59.ade.a.fitex','/tmp/sd/20130121.0401.00.ade.a.fitex']"
    print "Received the files: " + str(fitex)


    print "*************************************************"


    print "Attempting to fetch fitacf files from the usask server..."
    fitacf = fetch_remote_files(datetime(2012,11,24,4), datetime(2012,11,24,7),'sftp','chapman.usask.ca','fitcon/{year}/{month}/', {'ftype':'fitacf','radar':'sas'}, '/tmp/sd/', '{date}.C0.{radar}.{ftype}', username='davitpy', password='d4vitPY-usask', verbose=False)

    print "Expected the file: ['/tmp/sd/20121124.C0.sas.fitacf']"
    print "Received the file: " + str(fitacf)



