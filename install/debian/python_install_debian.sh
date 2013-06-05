#!/bin/bash

# Python install script for Ubuntu
#	installs all pre-requisite software to run DaViT-py
#	tested on Ubuntu 12.04

ver=2.7

apt-get install -y python$ver
apt-get install -y python-pip
apt-get install -y ipython
pip install --upgrade ipython
apt-get install -y ipython-notebook
apt-get install -y python-numpy
apt-get install -y python-scipy
apt-get install -y python-matplotlib
sudo apt-get install libfreetype6-dev
sudo apt-get install libpng-dev
pip install --upgrade matplotlib
apt-get install -y python-mpltoolkits.basemap
apt-get install -y python-h5py
apt-get install -y python-tornado
pip install --upgrade tornado
apt-get install -y python-zmq
apt-get install -y python-imaging
apt-get install -y python-paramiko
apt-get install -y python-pymongo
pip install --upgrade pymongo
apt-get install -y mpich2
apt-get install -y gfortran

dir=$(pwd)

cd /tmp
git clone https://github.com/matplotlib/basemap.git
cd basemap/geos-3.3.3
export GEOS_DIR=/usr/local
./configure --prefix=$GEOS_DIR
make; make install
cd ..
python setup.py install

#basemap install needs some finesse so python can find it.  Hopefully this works for you.  Otherise, you need to track down the old and new versions.
cd /usr/lib/pymodules/python2.7/mpl_toolkits 
cp -a basemap basemap_old
rm -r basemap
ln -s /usr/local/lib/python2.7/dist-packages/mpl_toolkits/basemap ./basemap

PS1='$ '
cd $dir
install_dir=$(readlink -f ../..)
echo "source $install_dir/profile.bash" >> ~/.bashrc

# PS1='$ '
# source ~/.bashrc
echo "source $install_dir/profile.bash" >> tempsh
. tempsh
rm tempsh
cd ../..

./mastermake





