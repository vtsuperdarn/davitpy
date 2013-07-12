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
pip install --upgrade ipython
zypper install -y python-numpy python-numpy-devel
pip install --upgrade numpy
zypper install -y python-scipy
zypper install -y python-matplotlib
zypper install -y python-matplotlib-tk
pip install --upgrade matplotlib
zypper install -y python-imaging
zypper install -y python-paramiko
pip install pymongo
zypper install -y python-tornado
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

cd /tmp
wget http://www.mpich.org/static/downloads/3.0.4/mpich-3.0.4.tar.gz
tar xfz mpich-3.0.4.tar.gz
cd mpich-3.0.4
./configure --enable-fc --enable-f77 FC=gfortran F77=gfortran CC=gcc
make |& tee m.txt
make install |& tee mi.txt

cd $dir
WHO=$(who am i | sed -e 's/ .*//')
install_dir=$(readlink -f ../..)
echo "source $install_dir/profile.bash" >> /home/${WHO}/.bashrc
# PS1='$ '
# source ~/.bashrc
# cd ../..
# ./mastermake

