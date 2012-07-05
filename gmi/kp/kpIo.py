# -*- coding: utf-8 -*-

from datetime import *
from kpDay import *
import h5py

def readKpAscii():
	filename = '/davitpy/gmi/kp/kp_index.ascii'
	f = open(filename, 'r')
	myLine = f.readline()
	while (myLine != '' ):
		myLine.replace( "\n", "" )
		#print myLine
		d = date(int(myLine[0:4]),int(myLine[4:6]),int(myLine[6:8]))
		kp_vals = []
		for i in range(0,8):
			index = 9+i*2
			kp_vals.append(myLine[index:index+2])
		x = kpDay(d,kp_vals)
		print x.date,x.vals
		myLine = f.readline()
		
			


def writeKpHdf5():
	f = h5py.File('/davitpy/gmi/kp/kp_index.hdf5','w')
	dset = f.create_dataset("MyDataset", (1, 8), 'S#')
	dset[...] = 'this is a test'
	f.close()

tert