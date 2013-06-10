#!/bin/bash

# Python install script for Ubuntu
#	installs all pre-requisite software to run DaViT-py
#	tested on Ubuntu 12.04

zypper install -y gcc gcc-c++ make
zypper install -y freetype2-devel
zypper install -y libpng14-devel
zypper install -y python
zypper install -y python-devel
zypper install -y python-pip
zypper install -y ipython
zypper install -y python-numpy python-numpy-devel
pip install --upgrade numpy
zypper install -y python-scipy
zypper install -y python-matplotlib
zypper install -y python-matplotlib-tk
pip install --upgrade matplotlib
zypper install -y python-imaging
zypper install -y python-paramiko
zypper install -y python-pymongo
zypper install -y python-tornado
zypper install -y openmpi openmpi-devel lam-devel
zypper install -y libgfortran3
zypper install -y hdf5 hdf5-devel

dir=$(pwd)

cd /tmp
git clone https://github.com/matplotlib/basemap.git
cd basemap/geos-3.3.3
export GEOS_DIR=/usr/local
./configure --prefix=$GEOS_DIR
make; make install
cd ..
python setup.py install


cd $dir
install_dir=$(readlink -f ../..)
echo "source $install_dir/profile.bash" >> ~/.bashrc

# PS1='$ '
# source ~/.bashrc
# cd ../..
# ./mastermake

