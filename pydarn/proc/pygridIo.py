def readPygridRec(myFile,myGrid,sEpoch,eEpoch):
	"""
	*******************************
	PACKAGE: pydarn.proc.gridIo
	FUNCTION: readPygridRec(myFile):
	
	reads pygrid records from sEpoch to eEpoch into a grid structure
	
	INPUTS:
		myFile: the pygrid file to read from
		myGrid: the pydarn.proc.gridLib.grid object to be filled
		sEpoch: read times >= this time (in epoch)
		eEpoch: read times < this time (in epoch)
	OUTPUTS:
		outGrid: the grid object that has been filled
		
	Written by AJ 201209118
	*******************************
	"""
	import math,numpy,pydarn,datetime
	
	keys = numpy.array(myFile.keys()).astype('i')
	keys = keys[sEpoch <= keys]
	keys = keys[keys < eEpoch]
	
	for k in keys:
		k=str(k)
		for v in myFile[k]['allVecs']:
			latInd = int(math.floor(v['index']/500))
			lonInd = int(v['index']-latInd*500)
			
			#create a gridVec object and append it to the list of gridCells
			myGrid.lats[latInd].cells[lonInd].allVecs.append(pydarn.proc.pygridLib.pygridVec(abs(v['v']),v['w_l'],\
			v['p_l'],v['stid'],-1,v['bmnum'],v['rng'],v['azm']))
			
			myGrid.lats[latInd].cells[lonInd].nVecs += 1
			myGrid.nVecs += 1
			
		for v in myFile[k]['avgVecs']:
			latInd = int(math.floor(v['index']/500))
			lonInd = int(v['index']-latInd*500)
			
			#create a gridVec object and append it to the list of gridCells
			myGrid.lats[latInd].cells[lonInd].avgVecs.append(pydarn.proc.pygridLib.pygridVec(abs(v['v']),v['w_l'],\
			v['p_l'],v['stid'],-1,-1,-1,v['azm']))
			
			myGrid.lats[latInd].cells[lonInd].nAvg += 1
			myGrid.nAvg += 1
		
	return myGrid
	
	
def writePygridRec(myFile,myGrid):
	"""
	*******************************
	PACKAGE: pydarn.proc.gridIo
	FUNCTION: writePygridRec(myFile,myGrid):
	
	writes a single grid record to a pygrid file
	
	INPUTS:
		myFile: the pygrid file to write to
		myGrid: the pydarn.proc.gridLib.grid object to be written
	OUTPUTS:
		None
		
	Written by AJ 20120914
	*******************************
	"""
	import utils,numpy
	
	#convert the start time to epoch time
	epoch = utils.datetimeToEpoch(myGrid.stime)
	
	#create a group in the file with a key value of epoch
	myFile.create_group(str(epoch))  
	
	#store some attributes
	myFile[str(epoch)].attrs['nVecs'] = myGrid.nVecs
	myFile[str(epoch)].attrs['nAvg'] = myGrid.nAvg
	myFile[str(epoch)].attrs['stime'] = epoch
	myFile[str(epoch)].attrs['etime'] =  utils.datetimeToEpoch(myGrid.etime)
	
	#check if we have data
	if(myGrid.nVecs == 0): return
	
	#create a numpy type to store the gridded vectors
	vecType = numpy.dtype([('index', 'i4'), ('v', 'f4'), ('w_l', 'f4'), ('p_l', 'f4'), ('stid', 'i2'),\
	('azm', 'f4'), ('bmnum', 'i2'), ('rng', 'i2')])
	myVecs = numpy.empty(myGrid.nVecs,dtype=vecType)
	cnt = 0
	#iterate through lat, lon, vecs
	for l in myGrid.lats:
		for c in l.cells:
			for i in range(0,c.nVecs):
				#print cnt,myGrid.nVecs
				#store the values of the data
				v = c.allVecs[i]
				myVecs[cnt]['index'] = c.index
				myVecs[cnt]['v'] = v.v
				myVecs[cnt]['w_l'] = v.w_l
				myVecs[cnt]['p_l'] = v.p_l
				myVecs[cnt]['stid'] = v.stid
				myVecs[cnt]['azm'] = v.azm
				myVecs[cnt]['bmnum'] = v.bmnum
				myVecs[cnt]['rng'] = v.rng
				cnt += 1
	#create the dataset within the epoch group
	myFile[str(epoch)].create_dataset('allVecs',data=myVecs,dtype=vecType)

	#create a numpy type to store the averaged vectors
	avgType = numpy.dtype([('index', 'i4'), ('v', 'f4'), ('w_l', 'f4'), ('p_l', 'f4'), ('stid', 'i2'),\
	('azm', 'f4')])
	myAvg = numpy.empty(myGrid.nAvg,dtype=avgType)
	cnt = 0
	#iterate through lat, lon, vecs
	for l in myGrid.lats:
		for c in l.cells:
			for v in c.avgVecs:
				#store the values of the data
				myAvg[cnt]['index'] = c.index
				myAvg[cnt]['v'] = v.v
				myAvg[cnt]['w_l'] = v.w_l
				myAvg[cnt]['p_l'] = v.p_l
				myAvg[cnt]['stid'] = v.stid
				myAvg[cnt]['azm'] = v.azm
				cnt += 1
				
	#create the dataset within the epoch group
	myFile[str(epoch)].create_dataset('avgVecs',data=myAvg,dtype=avgType)
	
	return
	
def openPygrid(fileName,action):
	"""
	*******************************
	PACKAGE: pydarn.proc.gridIo
	FUNCTION: openPygrid(dateStr,rad,action):
	
	opens a pygrid file for reading or writing or appending
	
	INPUTS:
		fileName: the fule to open
		action: the action to be done, e.g. 'w', 'a', etc.
	OUTPUTS:
		myFile: an h5py file instance
		
	Written by AJ 20120914
	*******************************
	"""
	import h5py
	
	myFile = h5py.File(fileName,action)

	return myFile
		
def closePygrid(myFile):
	"""
	*******************************
	PACKAGE: pydarn.proc.gridIo
	FUNCTION: closePygrid(dateStr,rad,action):
	
	closes a pygrid file
	
	INPUTS:
		myFile: the file to be closed
	OUTPUTS:
		NONE
		
	Written by AJ 20120914
	*******************************
	"""
	
	myFile.close()