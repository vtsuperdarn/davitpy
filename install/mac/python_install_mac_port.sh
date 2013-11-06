#!/bin/bash

# Python install script for mac
# 	installs all pre-requisite software to run DaViT-py
#	requires MacPort

ver=27

port install python${ver}
port install py${ver}-pip
port install py${ver}-ipython
port install py${ver}-numpy
port install py${ver}-matplotlib
port install py${ver}-matplotlib-basemap
port install py${ver}-scipy
port install py${ver}-h5py
port install py${ver}-tornado
port install py${ver}-zmq
port install py${ver}-pil
port install py${ver}-pymongo
port install py${ver}-paramiko
port install mpich +gcc47
port install coreutils
pip install --upgrade jinja2
pip install --upgrade cython
pip install --upgrade scikit-image


dir=$(pwd)
cd /tmp
git clone https://github.com/matplotlib/basemap.git
python2.7 setup.py install


cd $dir
install_dir=$(greadlink -f ../..)
echo "source $install_dir/profile.mac" >> ~/.bash_profile


cd ../..
./mastermake
