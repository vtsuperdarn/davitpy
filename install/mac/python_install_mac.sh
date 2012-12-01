# Python install script for mac
# 	installs all pre-requisite software to run DaViT-py
#	requires MacPort

ver=27

port install python${ver}
port install py${ver}-ipython
port install py${ver}-numpy
port install py${ver}-matplotlib
port install py${ver}-matplotlib-basemap
port install py${ver}-scipy
port install py${ver}-h5py
port install py${ver}-tornado
port install py${ver}-zmq
port install py${ver}-pil
port install py${ver}-sqlalchemy
port install py${ver}-psycopg2