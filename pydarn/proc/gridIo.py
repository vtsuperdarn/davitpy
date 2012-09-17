import utils,pydarn,math,datetime,time,copy,numpy,gridLib,h5py

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
	
	#convert the start time to epoch time
	epoch = utils.datetimeToEpoch(myGrid.stime)
	
	#create a group in the file with a key value of epoch
	myFile.create_group(str(epoch))
	
	#store some attributes
	myFile[str(epoch)].attrs['nVecs'] = myGrid.nVecs
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
				cnt = cnt+1
				
	#create the dataset within the epoch group
	myFile[str(epoch)].create_dataset('allVecs',data=myVecs,dtype=vecType)

	return
	
def openPygrid(dateStr,rad,action):
	"""
	*******************************
	PACKAGE: pydarn.proc.gridIo
	FUNCTION: openPygrid(dateStr,rad,action):
	
	opens a pygrid file for reading or writing or appending
	
	INPUTS:
		dateStr : a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		action: the action to be done, e.g. 'w', 'a', etc.
	OUTPUTS:
		myFile: an h5py file instance
		
	Written by AJ 20120914
	*******************************
	"""
	
	fileName = dateStr+'.'+rad+'.pygrid.hdf5'
	
	myFile = h5py.File('/data/grd/hdf5/'+fileName,action)

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