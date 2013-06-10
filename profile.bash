#!/bin/bash

# Sets path and fundamental environment variables for DaViT-py

# *********************************
# You probably do not need to modify the following part
# *********************************
# Set path to DAVITPY
export DAVITPY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export PATH=${DAVITPY}/bin:${PATH}

# Set path to DAVITPY
export PYTHONPATH=$PYTHONPATH:$DAVITPY

# Set Database users
export DBREADUSER='sd_dbread'
export DBREADPASS='5d'

# Set Database users
export SDDB='sd-work9.ece.vt.edu:27017'

# Set SFTP DATABASE
export VTDB='sd-data.ece.vt.edu'

# Set data path and format
# UAF
#export DAVIT_DIRFORMAT='%(dirtree)s/%(ftype)s/%(year)s/%(month)s.%(day)s/'
#export DAVIT_LOCALDIR=/raid/SuperDARN/data/
# VT
export DAVIT_DIRFORMAT='%(dirtree)s/%(year)s/%(ftype)s/%(radar)s/'
export DAVIT_LOCALDIR=/sd-data/


