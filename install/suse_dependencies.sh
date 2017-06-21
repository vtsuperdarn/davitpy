#!/bin/bash

# Python install script for Suse
#	installs all pre-requisite software to run DaViT-py
#	tested on OpenSUSE 13.2

# You may wish to change your matplotlib gui backend after using this script.
# For me I had to make the change to the matplotlibrc file in:
# /usr/lib64/python2.7/site-packages/matplotlib/mpl-data/matplotlibrc

#ver=2.7

alias pip="pip2"    #davitpy only supports python 2 for now, suse defaults to using pip3

zypper -n install gcc-fortran
zypper -n install hdf5 hdf5-devel
zypper -n install netcdf netcdf-devel
zypper -n install gcc gcc-c++ make
#############################
#CHOOSE ONE OF THESE ONLY
#############################
#zypper -n install libatlas3-sse3-devel  
#zypper -n install libatlas3-sse2-devel
#zypper -n install libatlas3-sse-devel
zypper -n install libatlas3-devel
#############################
zypper -n install openblas-devel blas-devel
zypper -n install libopenssl-devel

#Now let's install mpich for raydarn!
#Now get mpich to compile
cd /tmp
wget http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz
tar -zxf mpich-3.1.4.tar.gz
cd mpich-3.1.4
./configure
make
make install
ldconfig

cd $dir

