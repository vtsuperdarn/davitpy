#!/bin/bash

# Python install script for Ubuntu
#	installs all pre-requisite software to run DaViT-py
#	tested on Ubuntu 12.04

ver=2.7

apt-get install -y python$ver
apt-get install -d python-dev
apt-get install -y python-pip
apt-get install -y python-zmq
apt-get install -y python-imaging
apt-get install -y mpich2
apt-get install -y gfortran
apt-get install -y libhdf5-serial-dev
apt-get install -y libfreetype6-dev 
apt-get install -y python-matplotlib
pip install --upgrade matplotlib
apt-get install -y python-mpltoolkits.basemap
pip install --upgrade ipython
apt-get install -y ipython-notebook
pip install --upgrade jupyter
pip install --upgrade numpy
apt-get install -y python-scipy
pip install --upgrade basemap
pip install --upgrade h5py
pip install --upgrade tornado
pip install --upgrade paramiko
pip install --upgrade pymongo
pip install --upgrade mechanize
pip install --upgrade jinja2
pip install --upgrade jsonschema
pip install --upgrade ecdsa
pip install --upgrade pandas
pip install --upgrade scikit-image
apt-get install -y libnetcdf-dev
pip install --upgrade netcdf4

