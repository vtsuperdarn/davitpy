#!/bin/bash

# Python install script for Ubuntu
#	installs all pre-requisite software to run DaViT-py
#	tested on Ubuntu 12.04

ver=2.7

#NOTE TO DEVs (asreimer May 12, 2016)
#THE ORDER THAT THE PACKAGES ARE INSTALLED IN MATTERS!!

#First make sure user has python2.7 and dev install
#Then make sure pip is installed.
apt-get install -y python$ver
apt-get install -y python-dev
apt-get install -y python-pip

#VERY IMPORTANT BEFORE ANYTHING ELSE IS DONE
#WE MUCH UPGRADE PIP OR WE RISK BREAKING EVERYTHING
#(especially in Ubuntu 12.04)
pip install -U pip

#Now install the python package dependencies dependencies
apt-get install -y python-imaging
apt-get install -y python-gi-cairo  #needed in Ubuntu 16.04
apt-get install -y mpich2
apt-get install -y gfortran
apt-get install -y libhdf5-serial-dev
apt-get install -y libfreetype6-dev 
apt-get install -y libpng-dev
apt-get install -y libffi-dev
apt-get install -y libssl-dev
apt-get install -y libnetcdf-dev
apt-get install -y g++

#Now install the required python packages
pip install -U pyzmq
pip install -U ipython
pip install -U matplotlib
pip install -U jupyter
pip install -U numpy
pip install -U scipy
pip install -U h5py
pip install -U tornado
pip install -U paramiko
pip install -U pymongo
pip install -U mechanize
pip install -U jinja2
pip install -U jsonschema
pip install -U ecdsa
pip install -U pandas
pip install -U scikit-image
pip install -U netcdf4
pip install -U pyproj
pip install -U cryptography

#install basemap
cd /tmp
git clone --branch v1.0.7rel https://github.com/matplotlib/basemap.git
cd basemap/geos-3.3.3
export GEOS_DIR=/usr/local
./configure --prefix=$GEOS_DIR
make
make check
make install
ldconfig
cd ..
python setup.py install
