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
'''
fetchUtils.py, Angeline G. Burrell, UoL

Module: pydarn.sdio.fetchUtils

Comments: Routines to fetch SuperDARN radar data locally and remotely

Contains: uncompress_file    - uncompresses a file using various methods
          fetch_local_files  - uncompress and copy local files to a temporary
                               directory
          fetch_remote_files - download and uncompress files from a specified
                               server to a temporary directory
'''
import datetime as dt
import os

def uncompress_file(filename, outname=None, verbose=True):
    '''
    uncompress_file: a routine to perform an appropriate type of uncompression
                     on a specified file.  Current extensions include:
                         .bz2
                         .gz
                         .zip

    Input: filename         (str): name of the compressed file
           outname (nonetype/str): compressed name of the desired output file
                                   (allows uncompressed file to be placed in
                                   a different location) or None (if the
                                   uncompressed file will stay in the same
                                   directory).  (default=None)
           verbose         (bool): Print warnings and errors? (default=True)

    Output: outname (nonetype/str): name of uncompressed file or None if the
                                    command was unsuccessful or the compression 
                                    method could not be determined

    '''
    from copy import deepcopy as dc
    rn = "uncompress_files"
    command = None

    if outname is None:
        outname = dc(filename)

    if(filename.find('.bz2') != -1):
        outname = outname.replace('.bz2','')
        command = 'bunzip2 -c '+filename+' > '+outname
    elif(filename.find('.gz') != -1):
        outname = outname.replace('.gz','')
        command = 'gunzip -c '+filename+' > '+outname
    elif(filename.find('.zip') != -1):
        outname = outname.replace('.zip','')
        command = 'unzip -c '+filename+' > '+outname
    elif(filename.find('.tar') != -1):
        outname = outname.replace('.tar','')
        command = 'tar -xf '+filename

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

def fetch_local_files(stime, etime, rad, ftype, localdirfmt, dirtree, tempdir,
                      cycle_inc=dt.timedelta(hours=1), verbose=True):
    '''
    fetch_local_files: A routine to locate and retrieve file names from locally
                      stored SuperDARN radar files that fit the input criteria.

    Input: stime      (datetime): data starting time
           etime      (datetime): data ending time
           rad             (str): 3 letter radar code (eg "han")
           ftype           (str): radar file type ("fitex", "fitacf", "lmfit",
                                  or "iqdat")
           localdirfmt     (str): string defining the local directory structure
                                  (eg "{dirtree}{ftype}/{year}/{month}/{day}/")
           dirtree         (str): Local directory housing the SuperDARN data
                                  (must end with a "/")
           tempdir         (str): Temporary directory in which to store
                                  uncompressed files (must end with a "/")
           cycle_inc (timedelta): Time incriment between files (default=1 hour)
           verbose        (bool): Print warnings or not? (default=True)

    Output: file_stime (datetime): actual starting time for located files
            filelist       (list): list of uncompressed files (including path)

    Example: Fetches a day of locally stored data, sets directory format
             environment variable to "{dirtree}{ftype}/{radar}/{year}/".  This
             environment variable may eventually be phased out, so it is input
             as a string in this routine.

    import pydarn.sdio as sdio
    import glob

    sdio.dbUtils.setDIRFORMAT(0, 1, 2, 3)
    st_out, filelist = sdio.fetchUtils.fetch_local_files(dt.datetime(2002,6,20),
        dt.datetime(2002,6,21), "han", "fitacf", os.environ['DAVIT_DIRFORMAT'],
        "/Users/agb/Programs/Data/SuperDARN/", "/tmp/sd/")
    '''
    rn = "fetch_local_files"

    # Test input
    assert(isinstance(stime, dt.datetime)), \
        (rn, 'ERROR: stime must be datetime object')
    assert(isinstance(etime,dt.datetime)), \
        (rn, 'ERROR: eTime must be datetime object')
    assert(isinstance(rad,str) and len(rad) == 3), \
        (rn, 'ERROR: rad must be a 3 char string')
    assert(ftype == 'rawacf' or ftype == 'fitacf' or ftype == 'fitex' or
           ftype == 'lmfit' or ftype == 'iqdat'), \
        (rn, 'ERROR: ftype must be one of: rawacf, fitacf, fitex, lmfit, iqdat')
    assert(isinstance(localdirfmt, str) and localdirfmt[-1] == "/"), \
        (rn, 'ERROR: localdirfmt must be a string ending in "/"')
    assert(isinstance(dirtree, str) and dirtree[-1] == "/"), \
        (rn, 'ERROR: dirtree must be a string ending in "/"')
    assert(os.path.isdir(dirtree)), (rn, "ERROR: dirtree is not a directory")
    assert(isinstance(tempdir, str) and tempdir[-1] == "/"), \
        (rn, 'ERROR: tempdir must be a string ending in "/"')
    assert(os.path.isdir(tempdir)), (rn, "ERROR: tempdir is not a directory")
    assert(isinstance(cycle_inc, dt.timedelta)), \
        (rn, 'ERROR: cycle_inc must be a timedelta object')
    assert(isinstance(verbose, bool)), (rn, 'ERROR: verbose must be Boolian')

    # Initialize output
    file_stime = None
    filelist = list()

    # Start building the radar file name using the UAF naming convention:
    # YYYYmmdd.HHMM.??.rad.ftype.extention
    fname = '*.{:s}.{:s}*'.format(rad, ftype)

    # Set the unchanging parts of the possible local directory structure
    localstruct = dict()
    localstruct['dirtree'] = dirtree
    localstruct["ftype"] = ftype 
    localstruct["radar"] = rad 

    # Iterate through all of the hours in the request (round the starting time
    # down to the nearest even hour)
    ctime = stime.replace(minute=0, second=0, microsecond=0)
    if(ctime.hour % 2 == 1): ctime = ctime.replace(hour=ctime.hour-1)

    while ctime <= etime:
        # Set the temporal parts of the possible local directory structure
        localstruct["year"] = "{:4d}".format(ctime.year)
        localstruct["month"] = "{:2d}".format(ctime.month)
        localstruct["day"] = "{:2d}".format(ctime.day)
        
        # Build the name of the local files (uses wildcards)
        local_dir = localdirfmt.format(**localstruct)
        files = "{:s}{:s}.{:s}{:s}".format(local_dir, ctime.strftime("%Y%m%d"),
                                           ctime.strftime("%H"), fname)

        # Find and uncompress files which begin in this hour, saving the
        # names of the uncompressed files for the output
        for filename in glob.glob(files):
            # Begin to construct the name for the uncompressed file
            outname = filename.replace(local_dir, tempdir)

            # Unzip the compressed file
            outfile = uncompress_file(filename, outname, verbose)
            if outfile is None:
                # Then this is probably an uncompressed file
                command='cp {:s} {:s}'.format(filename, outname)
                try:
                    os.system(command)
                    outfile = outname
                    if verbose: print rn, "ADVISEMENT: performed [",command,"]"
                except:
                    if verbose:
                        print rn, "WARNING: unable to perform [",command,"]"

            if type(outfile) is str:
                # Save name of uncompressed file for output
                filelist.append(outname)

                # Ensure that the actual data start time is recorded
                ff = outname.replace(tempdir, '')
                #check the beginning time of the file
                t1 = dt.datetime(int(ff[0:4]), int(ff[4:6]), int(ff[6:8]),
                                 int(ff[9:11]), int(ff[11:13]), int(ff[14:16]))
                if file_stime == None or t1 < file_stime: file_stime = t1

        # Advance the cycle time by the specified incriment
        ctime = ctime + cycle_inc

    # Return the actual file start time and the list of uncompressed files
    return(file_stime, filelist)

def fetch_remote_files(stime, etime, rad, ftype, method, remotesite,
                       remotedirfmt, dirtree, tempdir, username=None,
                       password=False, port=None, channel='a',
                       cycle_inc=dt.timedelta(hours=1), verbose=True):
    '''
    fetch_remote_files: A routine to locate and retrieve file names from
                        remotely stored SuperDARN radar files that fit the
                        input criteria.

    Input: stime       (datetime): data starting time
           etime       (datetime): data ending time
           rad              (str): 3 letter radar code (eg "han")
           ftype            (str): radar file type ("fitex", "fitacf", "lmfit",
                                   or "iqdat")
           method           (str): remote connection method (eg sftp, http)
           remotesite       (str): remote site address (eg 'sd-data.ece.vt.edu')
           remotedirfmt     (str): string defining the remote directory
                                   structure
                                   (eg "{dirtree}{ftype}/{year}/{month}/{day}/")
           dirtree          (str): Remote directory housing the SuperDARN data
                                   (must end with a "/")
           tempdir          (str): Temporary directory in which to store
                                   uncompressed files (must end with a "/")
           username    (none/str): Optional input for remote access
           password    (bool/str): Optional input for remote access.  True will
                                   prompt the user for a password, False
                                   indicates no password is needed, unsecured
                                   passwords may be entered as a string
                                   (default=False)
           port        (none/str): Optional input for http file access
                                   (default=None)
           channel          (str): 1-character string denoting the radar
                                   channel (default='a')
           cycle_inc  (timedelta): Time incriment between files (default=1 hour)
           verbose         (bool): Print out warnings? (default=True)

    Output: file_stime (datetime): actual starting time for located files
            filelist       (list): list of uncompressed files (including path)

    Example: Fetches a day of remotely stored data from the Virginia Tech
             database, sets directory format environment variable to
             "{dirtree}{year}/{ftype}/{radar}/".  This environment variable may
             eventually be phased out, so it is input as a string in this
             routine.  The routine will prompt for a password and print out
             all warnings and advisements.

    import pydarn.sdio as sdio
    import datetime as dt

    sdio.dbUtils.setDIRFORMAT(0, 2, 3, 1)
    print "You will be propmted for this password:", os.environ['DBREADPASS']
    st_out,filelist = sdio.fetchUtils.fetch_remote_files(dt.datetime(2002,3,6),
        dt.datetime(2002,3,7), "han", "fitacf", "sftp", "sd-data.ece.vt.edu",
        os.environ['DAVIT_DIRFORMAT'], "/data/", "/tmp/", "sd_dbread", True)

    print st_out
    > "2002-03-06 00:00:00"
    print filelist
    > "['/tmp/20020306.0000.00.han.fitacf', '/tmp/20020306.0200.00.han.fitacf',
        '/tmp/20020306.0400.00.han.fitacf', '/tmp/20020306.0600.00.han.fitacf',
        '/tmp/20020306.0800.00.han.fitacf', '/tmp/20020306.1000.00.han.fitacf',
        '/tmp/20020306.1200.00.han.fitacf', '/tmp/20020306.1400.00.han.fitacf',
        '/tmp/20020306.1600.00.han.fitacf', '/tmp/20020306.1800.00.han.fitacf',
        '/tmp/20020306.2000.00.han.fitacf', '/tmp/20020306.2200.00.han.fitacf',
        '/tmp/20020307.0000.00.han.fitacf']"
    '''
    # getpass allows passwords to be entered without them appearing onscreen
    import getpass
    # urllib is best at transferring files of any type using non-sftp protocols
    import urllib
    # urllib2 is best at finding the files available using non-sftp protocols
    import urllib2
    # paramiko is necessary to use sftp, pyCurl currently requires much fiddling
    import paramiko as p

    rn = "fetch_remote_files"

    #--------------------------------------------------------------------------
    # Test input
    assert(isinstance(stime, dt.datetime)), \
        (rn, 'ERROR: stime must be datetime object')
    assert(isinstance(etime,dt.datetime)), \
        (rn, 'ERROR: eTime must be datetime object')
    assert(isinstance(rad,str) and len(rad) == 3), \
        (rn, 'ERROR: rad must be a 3 char string')
    assert(ftype == 'rawacf' or ftype == 'fitacf' or ftype == 'fitex' or
           ftype == 'lmfit' or ftype == 'iqdat'), \
        (rn, 'ERROR: ftype must be one of: rawacf, fitacf, fitex, lmfit, iqdat')
    assert(method == 'sftp' or method == 'http' or method == 'ftp' or
           method == 'file'), \
        (rn, 'ERROR: method must be one of: sftp, http, ftp, or file.',
         'Other protocols may work but need testing')
    assert(isinstance(remotesite, str)), \
        (rn, 'ERROR: remotesite must be a string')
    assert(isinstance(remotedirfmt, str)), \
        (rn, 'ERROR: remotedirfmt must be a string')
    assert(isinstance(dirtree, str)), (rn, 'ERROR: dirtree must be a string')
    assert(isinstance(tempdir, str) and tempdir[-1] == "/"), \
        (rn, 'ERROR: tempdir must be a string ending in "/"')
    assert(os.path.isdir(tempdir)), (rn, "ERROR: tempdir is not a directory")
    assert(isinstance(username, str) or username is None), \
        (rn, 'ERROR: username must be a string or None')
    assert(isinstance(password, str) or isinstance(password, bool)), \
        (rn, 'ERROR: password must be a string or Boolian')
    assert(isinstance(port, str) or port is None), \
        (rn, 'ERROR: port must be a string')
    assert(isinstance(channel, str) and len(channel) == 1), \
        (rn, 'ERROR: channel must be a one-character string')
    assert(isinstance(cycle_inc, dt.timedelta)), \
        (rn, 'ERROR: cycle_inc must be timedelta object')
    assert(isinstance(verbose, bool)), (rn, 'ERROR: verbose must be Boolian')

    #--------------------------------------------------------------------------
    # Initialize output
    file_stime = None
    filelist = list()

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

    # Build the possible radar filenames for matching using re module
    fname = ['......'+rad+'.'+ftype, '......'+rad+'.'+channel+'.'+ftype]

    #--------------------------------------------------------------------------
    # Perform method-specific initialization that does not require time info
    if method is "sftp":
        #create a transport object for use in sftp-ing
        transport = p.Transport((remotesite, 22))
        try:
            transport.connect(username=remoteaccess['username'],
                              password=remoteaccess['password'])
        except:
            print(rn, "ERROR: can't connect to", remotesite,
                  "with username and password")
            return(file_stime, filelist)

        try:
            sftp = p.SFTPClient.from_transport(transport)
        except:
            print rn, "ERROR: cannot engage sftp client at", remotesite
            return(file_stime, filelist)

    #--------------------------------------------------------------------------
    # Set the unchanging parts of the possible remote directory structure
    remotestruct = dict()
    remotestruct["dirtree"] = dirtree
    remotestruct["ftype"] = ftype
    remotestruct["radar"] = rad

    #--------------------------------------------------------------------------
    # Iterate through all of the hours in the request (round the starting time
    # down to the nearest even hour). ctime is the current iteration's time.
    ctime = stime.replace(minute=0, second=0, microsecond=0)
    if(ctime.hour % 2 == 1):
        ctime = ctime.replace(hour=ctime.hour-1)

    #--------------------------------------------------------------------------
    # Initialize the list of remote filenames
    remotefiles = list()

    #--------------------------------------------------------------------------
    # Cycle through the specified times
    while ctime <= etime:
        #----------------------------------------------------------------------
        # Set the temporal parts of the possible remote directory structure
        remotestruct["year"] = "{:04d}".format(ctime.year)
        remotestruct["month"] = "{:02d}".format(ctime.month)
        remotestruct["day"] = "{:02d}".format(ctime.day)

        #----------------------------------------------------------------------
        # Build the name of the remote files (uses wildcards)
        path = remotedirfmt.format(**remotestruct)
        if(remoteaccess.has_key('path') is False
           or path is not remoteaccess['path']):
            remoteaccess['path'] = path

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
                    remotefiles = [f[f.find('<a href="')+9:
                                     f[f.find('<a href="')+9:-1].find('">')
                                     +f.find('<a href="')+9]
                                   for f in response.readlines()
                                   if f.find('<a href="') >= 0]

                    # Close the connection
                    response.close()
                except:
                    if verbose:
                        print rn, "WARNING: unable to connect to [", url, "]"

        #----------------------------------------------------------------------
        # Search through the remote files for the ones we want and download them
        # Ensure that the list of remote files include those that can possibly
        # be a radar file: YYYYMMDD.HHMM.XX.RRR.ext (len is 22 for 1 char ext)  
        if len(remotefiles) > 0 and max([len(rf) for rf in remotefiles]) > 21:
            hour_str = ctime.strftime("%H")
            date_str = ctime.strftime("%Y%m%d")

            for form in fname:
                # Create a regular expression to find files of this time
                regex = urllib.re.compile(date_str+'.'+hour_str+form)

                # Go thorugh all the files in the directory
                for rf in remotefiles:
                    #if we have a file match between a file and our regex
                    if(regex.match(rf)):
                        tf = "{:s}{:s}".format(tempdir, rf)

                        if method is "sftp":
                            # Use the open sftp connection to get the file
                            rflong = "{:s}{:s}".format(remoteaccess['path'], rf)
                            
                            try:
                                sftp.get(rflong,tf)
                                if verbose:
                                    print rn, 'ADVISEMENT: downloading file', tf
                            except:
                                tf = None
                                if verbose:
                                    print rn,"ADVISEMENT: can't retrieve",rflong
                        else:
                            # Use a different connection method
                            furl = "{:s}{:s}".format(url, rf)

                            try:
                                urllib.urlretrieve(furl, tf)
                                if verbose:
                                    print rn, 'ADVISEMENT: downloading file', tf
                            except:
                                tf = None
                                if verbose:
                                    print rn,"ADVISEMENT: can't retrieve",furl

                        if type(tf) is str:
                            # Unzip the compressed file in place
                            outfile = uncompress_file(tf, verbose=verbose)
                            if outfile is None:
                                # Then this is probably an uncompressed file
                                outfile = tf

                            filelist.append(outfile)

                            # Use filename to find the file starting time
                            ff = outfile.replace(tempdir, '')
                            t1 = dt.datetime(int(ff[0:4]), int(ff[4:6]),
                                             int(ff[6:8]), int(ff[9:11]),
                                             int(ff[11:13]), int(ff[14:16]))
                            if file_stime == None or t1 < file_stime:
                                file_stime = t1

        #----------------------------------------------------------------------
        # Move to the next time
        ctime = ctime + cycle_inc

    #--------------------------------------------------------------------------
    # Return the actual file start time and the list of uncompressed files
    # after deleting the dictionary structure containing the password
    del remoteaccess
    return(file_stime, filelist)
