#!/bin/bash

# Python install script for Fedora
#	installs all pre-requisite software to run DaViT-py
#	tested on Fedora 21 and 22

# Installs dependencies for python 2.7.

dnf install -y python
dnf install -y python-devel
dnf install -y python-pip
dnf install -y python-zmq
dnf install -y python-imaging
dnf install -y openmpi-devel
ln -s /usr/lib64/openmpi/bin/mpif90 /usr/bin/mpif90 #Needed for raydarn to compile properly
dnf install -y gcc-gfortran
dnf install -y gcc-c++
dnf install -y hdf5-devel
dnf install -y python-matplotlib
pip install --upgrade matplotlib
dnf install -y python-basemap
dnf install -y python-basemap-data
pip install --upgrade ipython
dnf install -y ipython-notebook
pip install --upgrade numpy
dnf install -y scipy
dnf install -y geos-python
dnf install -y geos-devel
pip install --upgrade Cython
pip install --upgrade h5py
pip install --upgrade tornado
pip install --upgrade paramiko
pip install --upgrade pymongo
pip install --upgrade mechanize
pip install --upgrade jinja2
pip install --upgrade ecdsa
pip install --upgrade pandas

