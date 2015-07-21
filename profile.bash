#!/bin/bash

# Sets path and fundamental environment variables for DaViT-py

# *********************************
# You probably do not need to modify the following part
# *********************************
# Set path to DAVITPY
export DAVITPY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PATH=${DAVITPY}/bin:${PATH}

# NEED TO MOVE TO rcsetup.py and setup.py
export AACGM_DAVITPY_DAT_PREFIX=${DAVITPY}/tables/aacgm/aacgm_coeffs

# NEEDED FOR GME DATABASE STUFF
#export DBWRITEUSER=''
#export DBWRITEPASS=''
#export SDDB='sd-work9.ece.vt.edu:27017'

#
# IN LIEU OF CONFIGURATION FILE LIKE MATPLOTLIBRC
# FOR NOW:
#
# The evironment variables are python dictionary capable formatted strings appended 
# encode radar name, channel, and/or date information.  Currently supported 
# dictionary keys which can be used are: 
#
#    "date"    : datetime.datetime.strftime("%Y%m%d")
#    "year"    : 0 padded 4 digit year 
#    "month"   : 0 padded 2 digit month 
#    "day"     : 0 padded 2 digit day 
#    "hour"    : 0 padded 2 digit day 
#    "ftype"   : filetype string
#    "radar"   : 3-chr radarcode 
#    "channel" : single character string, ex) 'a'
#
# So for time = datetime(2012,2,1,0), rad='sas', and fileType='fitacf'
# DAVIT_REMOTE_DIRFORMAT='data/{year}/{ftype}/{radar}/' would become:
# 'data/2012/fitacf/sas/'
#
# ONLY the *FNAMEFMT environment variables will be converted to lists 
# if the environment variable contain a comma (','). For example:
#
# DAVIT_REMOTE_FNAMEFMT='{date}.{hour}......{radar}.{ftype},{date}.{hour}......{radar}.{channel}.{ftype}'
# becomes remote_fnamefmt = ['{date}.{hour}......{radar}.{ftype}','{date}.{hour}......{radar}.{channel}.{ftype}'] in python.
#

# Set SFTP DATABASE
#export DB='sd-data.ece.vt.edu'

# Set Database users
#export DBREADUSER='sd_dbread'
#export DBREADPASS='5d'

# Set Database users
#export SDDB='sd-work9.ece.vt.edu:27017'

#export DB_PORT='22'

# Set default temporary directory
#export DAVIT_TMPDIR='/tmp/sd/'
# RAD FILES 
#export DAVIT_REMOTE_DIRFORMAT='data/{year}/{ftype}/{radar}/'
#export DAVIT_REMOTE_FNAMEFMT='{date}.{hour}......{radar}.{ftype},{date}.{hour}......{radar}.{channel}.{ftype}'

#export DAVIT_LOCAL_DIRFORMAT='/sd-data/{year}/{ftype}/{radar}/'
#export DAVIT_LOCAL_FNAMEFMT='{date}.{hour}......{radar}.{ftype},{date}.{hour}......{radar}.{channel}.{ftype}'

# SD FILES 
#export DAVIT_SD_REMOTE_DIRFORMAT='data/{year}/{ftype}/{hemi}/'
#export DAVIT_SD_REMOTE_FNAMEFMT='{date}.{hemi}.{ftype}'

#export DAVIT_SD_LOCAL_DIRFORMAT='/sd-data/{year}/{ftype}/{hemi}/'
#export DAVIT_SD_LOCAL_FNAMEFMT='{date}.{hemi}.{ftype}'
