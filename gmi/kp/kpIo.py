# -*- coding: utf-8 -*-

def parseKpAsciiLine( line, yr, mo, dy, vals)

def readKpAscii( filename ):
	f = open(filename, 'r')
	myLine = f.readline()
	while (myLine != '' ):
			myLine.replace( "\n", "" )
			print myLine
			#parseKpAsciiLine(myLine,yr,mo,dy,vals)
			myLine = f.readline()

