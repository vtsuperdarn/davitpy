def readPygridRec(myFile,myGrid,sEpoch,eEpoch):
	"""
|	*******************************
|	PACKAGE: pydarn.io.gridIo
|	FUNCTION: readPygridRec(myFile):
|	
|	reads pygrid records from sEpoch to eEpoch into a grid structure
|	
|	INPUTS:
|		myFile: the pygrid file to read from
|		myGrid: the pydarn.proc.pygridLib.pygrid object to be filled
|		sEpoch: read times >= this time (in epoch)
|		eEpoch: read times < this time (in epoch)
|			NOTE: if eEpoch <= sEpoch, only the first record after 
|			sEpoch will be read
|	OUTPUTS:
|		outGrid: the pygrid object that has been filled
|		
|	Written by AJ 201209118
|	*******************************
	"""
	import math,numpy,pydarn,datetime
	keys = []
	for k in myFile.keys():
		keys.append(int(float(k)))
	keys=numpy.array(keys)
	keys = keys[sEpoch <= keys]
	keys.sort()
	if(eEpoch > sEpoch):
		keys = keys[keys < eEpoch]
	else:
		keys = keys[0:1]
	for k in keys:
		k=str(int(k))+'.0'
		for r in myFile[k].keys():
			if(r == 'allVecs'):
				for v in myFile[k]['allVecs']:
					latInd = int(math.floor(v['index']/500))
					lonInd = int(v['index']-latInd*500)
					
					#create a gridVec object and append it to the list of gridCells
					myGrid.lats[latInd].cells[lonInd].allVecs.append(pydarn.proc.pygridLib.pygridVec(abs(v['v']),v['w_l'],\
					v['p_l'],v['stid'],-1,v['bmnum'],v['rng'],v['azm']))
					
					myGrid.lats[latInd].cells[lonInd].nVecs += 1
					myGrid.nVecs += 1
					
			elif(r == 'avgVecs'):
				for v in myFile[k]['avgVecs']:
					latInd = int(math.floor(v['index']/500))
					lonInd = int(v['index']-latInd*500)
					
					#create a gridVec object and append it to the list of gridCells
					myGrid.lats[latInd].cells[lonInd].avgVecs.append(pydarn.proc.pygridLib.pygridVec(abs(v['v']),v['w_l'],\
					v['p_l'],v['stid'],-1,-1,-1,v['azm']))
					
					myGrid.lats[latInd].cells[lonInd].nAvg += 1
					myGrid.nAvg += 1
					
			elif(r == 'mrgVec'):
				
				for v in myFile[k]['mrgVec']:
					latInd = int(math.floor(v['index']/500))
					lonInd = int(v['index']-latInd*500)
					
					#create a gridVec object and append it to the list of gridCells
					myGrid.lats[latInd].cells[lonInd].mrgVec = pydarn.proc.pygridLib.mergeVec(abs(v['v']),v['w_l'],\
					v['p_l'],v['stid1'],v['stid2'],v['azm'])
					
					myGrid.nMrg += 1
		
	return myGrid
	
	
def writePygridRec(myFile,myGrid):
	"""
|	*******************************
|	PACKAGE: pydarn.io.pygridIo
|	FUNCTION: writePygridRec(myFile,myGrid):
|	
|	writes a single grid record to a pygrid file
|	
|	INPUTS:
|		myFile: the pygrid file to write to
|		myGrid: the pydarn.proc.gridLib.grid object to be written
|	OUTPUTS:
|		None
|		
|	Written by AJ 20120914
|	*******************************
	"""
	import utils,numpy
	
	#convert the start time to epoch time
	epoch = utils.datetimeToEpoch(myGrid.sTime)
	
	#create a group in the file with a key value of epoch
	myFile.create_group(str(epoch))  
	
	#store some attributes
	myFile[str(epoch)].attrs['nVecs'] = myGrid.nVecs
	myFile[str(epoch)].attrs['nAvg'] = myGrid.nAvg
	myFile[str(epoch)].attrs['stime'] = epoch
	myFile[str(epoch)].attrs['etime'] =  utils.datetimeToEpoch(myGrid.eTime)
	
	#check if we have data
	if(myGrid.nVecs == 0 and myGrid.nAvg == 0 and myGrid.nMrg == 0): return
	
	if(myGrid.nVecs > 0):
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

	if(myGrid.nAvg > 0):
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
	
	if(myGrid.nMrg > 0):
		#create a numpy type to store the averaged vectors
		mrgType = numpy.dtype([('index', 'i4'), ('v', 'f4'), ('w_l', 'f4'), ('p_l', 'f4'), ('stid1', 'i2'),\
		('stid2', 'i2'),('azm', 'f4')])
		myMrg = numpy.empty(myGrid.nMrg,dtype=mrgType)
		cnt = 0
		#iterate through lat, lon, vecs
		for l in myGrid.lats:
			for c in l.cells:
				if(c.mrgVec != None):
					v = c.mrgVec
					#store the values of the data
					myMrg[cnt]['index'] = c.index
					myMrg[cnt]['v'] = v.v
					myMrg[cnt]['w_l'] = v.w_l
					myMrg[cnt]['p_l'] = v.p_l
					myMrg[cnt]['stid1'] = v.stids[0]
					myMrg[cnt]['stid2'] = v.stids[1]
					myMrg[cnt]['azm'] = v.azm
					cnt += 1
					
		#create the dataset within the epoch group
		myFile[str(epoch)].create_dataset('mrgVec',data=myMrg,dtype=mrgType)
		
	return
	
def openPygrid(fileName,action):
	"""
|	*******************************
|	PACKAGE: pydarn.io.pygridIo
|	FUNCTION: openPygrid(dateStr,rad,action):
|	
|	opens a pygrid file for reading or writing or appending
|	
|	INPUTS:
|		fileName: the file to open
|		action: the action to be done, e.g. 'w', 'a', etc.
|	OUTPUTS:
|		myFile: an h5py file instance
|		
|	Written by AJ 20120914
|	*******************************
	"""
	import h5py
	
	myFile = h5py.File(fileName,action)

	return myFile
		
def closePygrid(myFile):
	"""
|	*******************************
|	PACKAGE: pydarn.proc.pygridIo
|	FUNCTION: closePygrid(dateStr,rad,action):
|	
|	closes a pygrid file
|	
|	INPUTS:
|		myFile: the file to be closed
|	OUTPUTS:
|		NONE
|		
|	Written by AJ 20120914
|	*******************************
	"""
	
	myFile.close()
	
def locatePygridFile(dateStr,ext):
	"""
|	*******************************
|	PACKAGE: pydarn.proc.pygridIo
|	FUNCTION: locatePygridFile(dateStr,ext):
|	
|	locates a pygrid file for the given dateStr and ext
|	
|	INPUTS:
|		dateStr: the date in the file title, eg '20110101'
|		ext: the extension in the filename, eg 'bks', 'cve', 'north', etc.
|	OUTPUTS:
|		fileName: the complete filename (including path) of the
|			pygrid file
|		
|	Written by AJ 20120919
|	*******************************
	"""
	import os,string
	
	radDir = os.environ['DATADIR']+'/pygrid'+'/'+ext
	if not os.path.exists(radDir):
		print 'dir '+radDir+' does not exist'
		return None
	
	fileName = radDir+'/'+dateStr+'.'+ext+'.pygrid.hdf5.bz2'
	if not os.path.exists(fileName):
		fileName = string.replace(fileName,'.bz2','')
		if not os.path.exists(fileName):
			print 'file '+fileName+'[.bz2] does not exist'
			return None
	else:
		print 'bunzip2 '+fileName
		os.system('bunzip2 '+fileName)
		fileName = string.replace(fileName,'.bz2','')
	
	return fileName