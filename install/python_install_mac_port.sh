#!/bin/bash -v

# Python install script for mac
# 	installs all pre-requisite software to run DaViT-py
#	requires MacPort

ver=27

port -n install python${ver}
port -n install mpich 
port -n install gcc49
port -n select gcc mp-gcc49
hash gfotran
port -n install coreutils
#easy_install pip
port install py${ver}-pip
port install pip_select
port select --set pip pip${ver}
pip install --upgrade numpy
pip install --upgrade matplotlib
port -n install py${ver}-matplotlib-basemap
pip install --upgrade scipy
pip install --upgrade h5py
pip install --upgrade pyzmq tornado pygments
pip install --upgrade ipython
pip install --upgrade jupyter
python -c 'from IPython.external import mathjax; mathjax.install_mathjax()'
pip install --upgrade pillow
pip install --upgrade pymongo
pip install --upgrade paramiko
pip install --upgrade jinja2
pip install --upgrade jsonschema
pip install --upgrade cython
pip install --upgrade scikit-image
pip install --upgrade pandas
pip install netCDF4 

dir=$(pwd)
cd /tmp
git clone --branch v1.0.7rel https://github.com/matplotlib/basemap.git

cd basemap/geos-3.3.3
export GEOS_DIR=/usr/local/geos
./configure --prefix=$GEOS_DIR
make
make install
cd ..
python setup.py install