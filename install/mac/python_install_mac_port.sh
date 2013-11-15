#!/bin/bash -v

# Python install script for mac
# 	installs all pre-requisite software to run DaViT-py
#	requires MacPort

ver=27

port -n install python${ver}
port -n install py${ver}-pip
port -n install py${ver}-ipython
port -n install py${ver}-numpy
port -n install py${ver}-matplotlib
port -n install py${ver}-matplotlib-basemap
port -n install py${ver}-scipy
port -n install py${ver}-h5py
port -n install py${ver}-tornado
port -n install py${ver}-zmq
port -n install py${ver}-pil
port -n install py${ver}-pymongo
port -n install py${ver}-paramiko
port -n install mpich +gcc47
port -n install coreutils

dir=$(pwd)
cd /tmp
git clone https://github.com/matplotlib/basemap.git
cd basemap
python2.7 setup.py install


cd $dir
install_dir=$(greadlink -f ../..)
echo "source $install_dir/profile.mac" >> ~/.bash_profile
source ~/.bash_profile

cd ../..
./mastermake
