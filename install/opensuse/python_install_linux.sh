# Python install script for Ubuntu
#	installs all pre-requisite software to run DaViT-py
#	tested on Ubuntu 12.04

zypper install -y python
zypper install -y python-pip
zypper install -y ipython
zypper install -y python-numpy
zypper install -y python-scipy
zypper install -y python-matplotlib
zypper install -y python-imaging
zypper install -y python-paramiko
zypper install -y python-pymongo
zypper install -y python-tornado
zypper install -y openmpi
zypper install -y libgfortran3
