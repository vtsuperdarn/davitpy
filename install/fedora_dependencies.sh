#!/bin/bash

# Python install script for Fedora
#	installs all pre-requisite software to run DaViT-py
#	tested on Fedora 21

ver=2.7

dnf install -y python$ver
dnf install -d python-dev
dnf install -y python-pip
dnf install -y python-zmq
dnf install -y python-imaging
dnf install -y mpich2
dnf install -y gcc-gfortran
dnf install -y hdf5-devel
dnf install -y python-matplotlib
pip install --upgrade matplotlib
dnf install -y python-basemap-data
pip install --upgrade ipython
dnf install -y ipython-notebook
pip install --upgrade numpy
dnf install -y scipy
dnf install -y geos-python
dnf install -y geos-devel
pip install --allow-external basemap --allow-unverified basemap--upgrade basemap	# different
pip install --upgrade Cython
pip install --upgrade h5py
pip install --upgrade tornado
pip install --upgrade paramiko
pip install --upgrade pymongo
pip install --upgrade mechanize
pip install --upgrade jinja2
pip install --upgrade ecdsa

# gfortran module files need to be recompiled for this version
cd ../models/hwm/
rm ./*.mod
gfortran *.f90

dir=$(pwd)
echo "source $dir/../profile.bash" >> ~/.bashrc
