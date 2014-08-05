#!/bin/bash

# Sets path and fundamental environment variables for DaViT-py

# *********************************
# You probably do not need to modify the following part
# *********************************
# Set path to DAVITPY
export DAVITPY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export PATH=${DAVITPY}/bin:${PATH}

export AACGM_DAVITPY_DAT_PREFIX=${DAVITPY}/tables/aacgm/aacgm_coeffs

# Set Database users
export DBREADUSER='sd_dbread'
export DBREADPASS='5d'

# Set Database users
export SDDB='sd-work9.ece.vt.edu:27017'

# Set SFTP DATABASE
export DB='sd-data.ece.vt.edu'


# IN LIEU OF CONFIGURATION FILE LIKE
# MATPLOTLIBRC

export DB_PORT='22'

# Set default temporary directory
export DAVIT_TMPDIR='/tmp/sd/'

export DAVIT_REMOTE_DIRFORMAT='data/{year}/{ftype}/{radar}/'
export DAVIT_REMOTE_FNAMEFMT='{date}.{hour}......{radar}.{ftype},{date}.{hour}......{radar}.{channel}.{ftype}'

export DAVIT_LOCAL_DIRFORMAT='/sd-data/{year}/{ftype}/{radar}/'
export DAVIT_LOCAL_FNAMEFMT='{date}.{hour}......{radar}.{ftype},{date}.{hour}......{radar}.{channel}.{ftype}'

#in hours
export DAVIT_REMOTE_TIMEINC='2'
export DAVIT_LOCAL_TIMEINC='2'


