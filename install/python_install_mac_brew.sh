#!/bin/bash

# Python install script for mac
#   installs all pre-requisite software to run DaViT-py
#   requires HomeBrew

# Non-python dependencies
brew install gfortran
brew install mpich2
brew install coreutils
brew install pkg-config
brew install freetype
brew install libpng
brew install python
# Python dependencies
easy_install pip
brew install readline
brew install zeromq
pip install --upgrade pyzmq tornado pygments
pip install --upgrade ipython
pip install --upgrade jupyter
python -c 'from IPython.external import mathjax; mathjax.install_mathjax()'
pip install --upgrade numpy
pip install --upgrade matplotlib
pip install --upgrade scipy
pip install --upgrade h5py
pip install --upgrade PIL
pip install --upgrade pymongo
pip install --upgrade paramiko
pip install --upgrade jinja2
pip install --upgrade jsonschema
pip install --upgrade cython
pip install --upgrade scikit-image
pip install --upgrade pandas

dir=$(pwd)
cd /tmp
git clone --branch v1.0.7rel https://github.com/matplotlib/basemap.git
python2.7 setup.py install

