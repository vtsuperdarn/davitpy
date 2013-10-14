#!/bin/bash

# Python install script for Ubuntu
#	installs all pre-requisite software to run DaViT-py
#	tested on Ubuntu 12.04

ver=2.7

apt-get install -y python$ver
apt-get install -y python-pip
pip install --upgrade ipython
pip install jinja2
apt-get install -y ipython-notebook
apt-get install -y python-zmq
apt-get install -y python-imaging
apt-get install -y mpich2
apt-get install -y gfortran