# IO
"""
*******************************
read a datamap file

INPUT:

Created by AJ
*******************************
"""
import binascii
import struct

def readBin(filename):
	f = open(filename,'rb')
	rsize = 1
	c = f.read(rsize)
	x=0
	while x<10:
		print c
		print struct.unpack('s', c)
		c = f.read(rsize)
		x = x + 1
	f.close
