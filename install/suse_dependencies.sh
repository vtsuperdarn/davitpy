#!/bin/bash

# Python install script for Ubuntu
#	installs all pre-requisite software to run DaViT-py
#	tested on OpenSUSE 13.2

# You may wish to change your matplotlib gui backend after using this script.
# For me I had to make the change to the matplotlibrc file in:
# /usr/lib64/python2.7/site-packages/matplotlib/mpl-data/matplotlibrc

#ver=2.7

alias pip="pip2"    #davitpy only supports python 2 for now, suse defaults to using pip3

#apt-get install -y python$ver
zypper -n install python
#apt-get install -y python-dev
zypper -n install python-devel
zypper -n install python-pip
#apt-get install -y python-zmq
zypper -n install python-pyzmq
#apt-get install -y python-imaging
zypper -n install python-Pillow
#apt-get install -y mpich2
#apt-get install -y gfortran
zypper -n install gcc-fortran
#apt-get install -y libhdf5-serial-dev
zypper -n install hdf5 hdf5-devel
zypper -n install netcdf netcdf-devel
zypper -n install python-matplotlib python-matplotlib-tk
zypper -n install tk-devel
zypper -n install freetype2-devel libpng16-devel
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
zypper -n install python-Cython python3-Cython
zypper -n install libagg2
#apt-get install -y python-mpltoolkits.basemap
pip install --upgrade numpy
zypper -n install python-scipy
pip install --upgrade h5py
pip install --upgrade tornado
pip install --upgrade paramiko
pip install --upgrade pymongo
pip install --upgrade mechanize
pip install --upgrade jinja2
pip install --upgrade jsonschema
pip install --upgrade ecdsa
pip install --upgrade pandas
#zypper -n install libnetcdf-dev
pip install --upgrade netcdf4
pip install --upgrade pyparsing
#apt-get install -y ipython-notebook
pip install --upgrade ipython
pip install --upgrade matplotlib
#pip install --upgrade basemap

dir=$(pwd)

#Now install basemap!
cd /tmp
git clone https://github.com/matplotlib/basemap.git
cd basemap/geos-3.3.3
export GEOS_DIR=/usr/local
./configure --prefix=$GEOS_DIR
make
make check
make install
ldconfig
cd ..
python setup.py install


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

