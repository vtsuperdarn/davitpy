# -*- coding: utf-8 -*-

from datetime import *
from kpDay import *
import h5py

def kp2Hdf5():
	"""this is a function which will read a Kp ascii file and output an hdf5 file"""
	allKp = readKpAscii()
	
	#rearrage the Kp data
	dates = []
	vals = []
	for i in range(0,len(allKp)):
		dates.append(allKp[i].date)
		vals.append(allKp[i].vals)
		
	f = h5py.File('/davitpy/gmi/kp/kp_index.hdf5','w')
	f.create_dataset('kpDates', data=dates)
	f.create_dataset('kpVals',data=vals)
	f.close()
	
def readKpAscii():
	#open the Kp ascii file
	filename = '/davitpy/gmi/kp/kp_index.ascii'
	f = open(filename, 'r')
	allKp = []
	
	#read the first line
	myLine = f.readline()
	
	#iterate through the entire file
	while (myLine != '' ):
		myLine.replace( "\n", "" )
		
		#parse the date into a date object
		d = myLine[0:8]
		#parse the Kp values into a list
		kpVals = []
		for i in range(0,8):
			index = 9+i*2
			kpVals.append(myLine[index:index+2])
			
		#create a kpDay object with the date and values
		myDay = kpDay(d,kpVals)
		
		allKp.append(myDay)
		
		#read the next line in the file
		myLine = f.readline()
		
	#return the array of data
	return allKp
			


#def writeKpHdf5():
	#f= h5py.File('/davitpy/gmi/kp/kp_index.hdf5','w')
	#dt = h5py.special_dtype(vlen=str)
	#dset = f.create_dataset('kpIndex', (10,8), dtype=dt)
	#for i in range(0,10):
		#dset[i,:] = ['asd','asdfsdaf','asdfasdf','asdfsdf','asdfsdf','try','ytyr','eryrt']
	#f.close
