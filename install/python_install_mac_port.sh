#!/bin/bash -v

# Python install script for mac
# 	installs all pre-requisite software to run DaViT-py
#	requires MacPort

port -n install mpich 
port -n install gcc49
port -n select gcc mp-gcc49
hash gfotran
port -n install coreutils
