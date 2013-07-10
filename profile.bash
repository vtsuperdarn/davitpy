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
export DBREADUSER='davitpy'
export DBREADPASS='d4vitPY-usask'
export VTDBREADUSER='sd_dbread'
export VTDBREADPASS='5d'

# Set Database users
export SDDB='sd-work9.ece.vt.edu:27017'

# Set SFTP DATABASE
export VTDB='sd-data.ece.vt.edu'
export ISASDB='chapman.usask.ca'


