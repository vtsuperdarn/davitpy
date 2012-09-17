import utils,pydarn,aacgm,math,datetime,time,copy,numpy,gridIo

def makeGrid(dateStr,rad,times=[0,2400],fileType='fitex',interval=120,vb=0,filter=1,plot=0):
	"""
	*******************************
	PACKAGE: pydarn.proc.grid
	FUNCTION: makeGrid(dateStr,rad,[times],[fileType],[interval],[vb],[filter],[plot]):
	
	reads in fitted radar data and puts it into a geospatial grid
	
	INPUTS:
		dateStr : a string containing the target date in yyyymmdd format
		rad: the 3 letter radar code, e.g. 'bks'
		[times]: the range of times for which the file should be read in
			MINIMIZED hhmm format, ie [23,456], NOT [0023,0456]
			default = [0,2400]
		[fileType]: 'fitex', 'fitacf', or 'lmfit'; default = 'fitex'
		[interval]: the time interval at which to do the gridding
			in seconds; default = 120
		[filter]: 1 to boxcar filter, 0 for normal data; default = 1
		[plot]: whether to plot the gridded data after gridding, 
			1 for yes, 0 for no; default = 0
	OUTPUTS:
		NONE
		
	Written by AJ 20120807
	*******************************
	"""
	#convert date string, start time, end time to datetime
	myDate = utils.yyyymmddToDate(dateStr)
	hr1,hr2 = int(math.floor(times[0]/100.)),int(math.floor(times[1]/100.))
	min1,min2 = int(times[0]-hr1*100),int(times[1]-hr2*100)
	stime = myDate.replace(hour=hr1,minute=min1)
	if(hr2 == 24):
		etime = myDate+datetime.timedelta(days=1)
	else:
		etime = myDate.replace(hour=hr2,minute=min2)
	
	#read the radar data
	myData = pydarn.io.radDataRead(dateStr,rad,time=times,filter=filter)
	#check for data in this time period
	assert(myData.nrecs > 0),'error, no data for this time period'
	#get a radar site object
	site = pydarn.radar.network().getRadarByCode(rad).getSiteByDate(myData.times[0])
	myFov = pydarn.radar.radFov.fov(site=site,rsep=myData[myData.times[0]]['prm']['rsep'],\
	ngates=site.maxgate+1,nbeams=site.maxbeam+1)
	
	#create a 2D list to hold coords of RB cells
	coordsList = [[None]*site.maxgate for _ in range(site.maxbeam)]
	
	for i in range(site.maxbeam):
		for j in range(site.maxgate):
			t=myData.times[0]
			arr1=aacgm.aacgmConv(myFov.latCenter[i][j],myFov.lonCenter[i][j],300,0)
			arr2=aacgm.aacgmConv(myFov.latCenter[i][j+1],myFov.lonCenter[i][j+1],300,0)
			
			azm = utils.geoPack.greatCircleAzm(arr1[0],arr1[1],arr2[0],arr2[1])
			myPos = aacgm.rPosAzm(i,j,\
			myData[t]['prm']['stid'],time.mktime(t.timetuple()),myData[t]['prm']['frang'],\
			myData[t]['prm']['rsep'],myData[t]['prm']['rxrise'],300.,1)
			print azm,myPos[2]

	#a list for all the grid objects
	myGrids = []
	#create a grid object
	g = grid()
	#initialize start time
	ctime = stime
	lastInd = 0
	#open a pygrid file
	gFile = pydarn.proc.gridIo.openPygrid(dateStr,rad,'w')
	
	#until we reach the designated end time
	while ctime < etime:
		#boundary time
		bndT = ctime+datetime.timedelta(seconds=interval)
		#remove vectors from the grid object
		g.delVecs()
		#verbose option
		if(vb==1): print ctime
		#iterate through the radar data
		for i in range(lastInd,myData.nrecs):
			#current time of radar data
			t = myData.times[i]
			#are we in the target time interval?
			if(ctime < t <= bndT): 
				#iterate through the number of scatter points on this beam
				for j in range(0,myData[t]['fit']['npnts']):
					#check if we have calculated the coords for this RB cell
					if(coordsList[myData[t]['prm']['bmnum']][myData[t]['fit']['slist'][j]] == None):
						#calculate and save [mlat,mlon,mazm] of the RB cell
						myPos = aacgm.rPosAzm(myData[t]['prm']['bmnum'],myData[t]['fit']['slist'][j],\
						myData[t]['prm']['stid'],time.mktime(t.timetuple()),myData[t]['prm']['frang'],\
						myData[t]['prm']['rsep'],myData[t]['prm']['rxrise'],300.,1)
						coordsList[myData[t]['prm']['bmnum']][myData[t]['fit']['slist'][j]] = myPos
				#enter the radar data into the grid
				g.enterData(myData[t],coordsList)
			#if we have exceeded the boundary time
			elif(t >= bndT): break
		#record the last record we examined
		lastInd = i
		#if we have > 0 gridded vector
		if(g.nVecs > 0):
			#record some information
			g.stime = ctime
			g.etime = bndT
			#average is LOS vectors
			g.averageVecs()
			#write to the hdf5 file
			pydarn.proc.gridIo.writePygridRec(gFile,g)
			
		#reassign the current time we are at
		ctime = bndT
		
		
	pydarn.proc.gridIo.closePygrid(gFile)
	
	
	#if the user desires plots
	if(plot == 1):
		#make a plot
		for i in range(0,len(myGrids)):
			pydarn.plot.grid.plotGrid(myGrid=myGrids[i], grid=0)
	
class gridVec(object):
	"""
	*******************************
	PACKAGE: pydarn.proc.grid
	CLASS: gridVec
	
	a class defining a single gridded vector
	
	DECLARATION: 
		myVel = pydarn.proc.grid.gridVec(v,w_l,p_l,stid,time,bmnum,rng,azm):
	MEMBERS:
		v : Doppler velocity
		w_l : spectral width
		p_l : power
		stid : station id
		time : time of the measurement
		bmnum : beam number of the measurement
		rng : range gate of the measurement
		azm : azimuth of the measurement

	Written by AJ 20120907
	*******************************
	"""
	
	def __init__(self,v,w_l,p_l,stid,time,bmnum,rng,azm):
		
		#initialize all the values, pretty self-explanatory
		self.v = v
		self.w_l = w_l
		self.p_l = p_l
		self.stid = stid
		self.time = time
		self.azm = azm
		self.bmnum = bmnum
		self.rng = rng
		
		
class gridCell(object):
	"""
	*******************************
	PACKAGE: pydarn.proc.grid
	CLASS: gridCell
	
	a class defining a single grid cell

	EXAMPLES:
	
	DECLARATION: 
		myCell = pydarn.proc.grid.gridCell(botLat,topLat,leftLon,rightLon)
	MEMBERS:
		bl : bottom left corner in [lat,mlt]
		tl : bottom left corner in [lat,mlt]
		tr : top right corner in [lat,mlt]
		br : bottom right corner in [lat,mlt]
		center : the center coordinate pair in [lat,mlt]
		nVecs : the number of gridded vectors in this cell
		vecs : a list to hold the gridVec objects
		
	Written by AJ 20120907
	*******************************
	"""
	
	def __init__(self,lat1,lat2,mlt1,mlt2,n):
		#define the 4 corners of the cell
		self.bl = [lat1,mlt1]
		self.tl = [lat2,mlt1]
		self.tr = [lat2,mlt2]
		self.br = [lat1,mlt2]
		
		self.index = int(math.floor(lat1))*500+n
		
		#check for a wrap around midnight (causes issues with mean) and then
		#calculate the center point of the cell
		if(mlt2 < mlt1): self.center = [(lat1+lat2)/2.,(24.-mlt1+mlt2)/2.]
		else: self.center = [(lat1+lat2)/2.,(mlt1+mlt2)/2.]
		
		#initialize number of grid vectors in this cell and the list to hold them
		self.nVecs = 0
		self.allVecs = []
		self.nAvg = 0
		self.avgVecs = []
		
class latCell(object):
	"""
	*******************************
	PACKAGE: pydarn.proc.grid
	CLASS: latCell
	
	a class to hold the information for a single latitude
		for a geospatial grid
	
	DECLARATION: 
		myLat = pydarn.proc.grid.latCell()
	MEMBERS:
		nCells : the number of gridCells contained in this latCell
		botLat : the lower latitude limit of thsi cell
		topLat : the upper latitude limit of this cell
		delLon : the step size (in degrees) in longitude for this
			latCell
		cells : a list of the gridCell objects
		
	
	Written by AJ 20120907
	*******************************
	"""
	
	def __init__(self,lat):
		
		#calculate number of gridCells, defined in Ruohoniemi and Baker
		self.nCells = int(round(360.*math.sin(math.radians(90.-lat))))
		#bottom latitude boundary of this latCell
		self.botLat = lat
		#latitude step size of this cell
		self.delLon = 360./self.nCells
		#top latitude boundary of this cell
		self.topLat = lat+1
		#list for gridCell objects
		self.cells = []
		
		#iterate over all longitudinal cells
		for i in range(0,self.nCells):
			#calculate left and right mlt boundaries for this gridCell
			mlt1 = aacgm.mltFromYmdhms(2012,1,1,0,0,0,self.delLon*i)
			mlt2 = aacgm.mltFromYmdhms(2012,1,1,0,0,0,self.delLon*(i+1))
			#create a new gridCell object and append it to the list
			self.cells.append(gridCell(self.botLat,self.topLat,mlt1,mlt2,i))
			
		
		
class grid(object):
	"""
	*******************************
	PACKAGE: pydarn.proc.grid
	CLASS: grid
	
	the top level class for defining a geospatial grid for 
	velocity gridding

	EXAMPLES:
	
	DECLARATION: 
		myGrid = pydarn.proc.grid.grid()
	MEMBERS:
		lats : a list of latCell objects
		nLats : an integer number equal to the number of
			items in the lats list
		delLat : the spacing between latCell objects
		nVecs : the number of gridded vectors in the grid object
		
	
	Written by AJ 20120907
	*******************************
	"""
	
	def __init__(self):
		self.nVecs = 0
		nlats = 90
		self.lats = []
		self.nLats = nlats
		
		#latitude step size
		self.delLat = 90./self.nLats
		
		self.stime = None
		self.etime = None
		
		#for all the latitude steps
		for i in range(0,self.nLats):
			#create a new latCell object and append it to the list
			l = latCell(float(i)*self.delLat)
			self.lats.append(l)
			
	def delVecs(self):
		"""
		*******************************
		PACKAGE: pydarn.proc.grid
		FUNCTION: grid.delVecs():
		BELONGS TO: CLASS: pydarn.proc.grid.grid
		
		delete all vectors from a grid object
		
		INPUTS:
			None
		OUTPUTS:
			None
			
		EXAMPLE:
			myGrid.delVecs()
			
		Written by AJ 20120911
		*******************************
		"""
		self.nVecs = 0

		
		for l in self.lats:
			for c in l.cells:
				c.allVecs = [];
				c.nVecs = 0;
				c.avgVecs = [];
				c.nAvg = 0;
				
	def averageVecs(self):
		"""
		*******************************
		PACKAGE: pydarn.proc.gridLib
		FUNCTION: grid.averageVecs():
		BELONGS TO: CLASS: pydarn.proc.gridLib.grid
		
		go through all grid cells and average the vectors in 
		cells with more than 1 vector
		
		INPUTS:
			None
		OUTPUTS:
			None
			
		EXAMPLE:
			myGrid.averageVecs()
			
		Written by AJ 20120917
		*******************************
		"""
		
		for l in self.lats:
			for c in l.cells:
				if(c.nVecs == 4):
					print ''
					print c.nVecs
					for v in c.allVecs:
						print v.azm,v.bmnum,v.rng
					print ''
				
				
	def enterData(self,myData,coordsList):
		"""
		*******************************
		PACKAGE: pydarn.proc.grid
		FUNCTION grid.enterData():
		
		inserts radar fitacf data into a grid object
		
		BELONGS TO: CLASS: pydarn.proc.grid.grid

		INPUTS:
			myData: a pydarn.io.radDataTypes.beam object
			coordsList: a 2D list containing the coords [lat,lon,azm] 
				corresponding to range-beam cells
		OUTPUTS:
			None
			
		EXAMPLE:
			myGrid.enterData(myBeam,myCoords)
			
		Written by AJ 20120911
		*******************************
		"""
		
		#go through all scatter points on this beam
		for i in range(0,myData['fit']['npnts']):
			
			#check for good ionospheric scatter
			if(myData['fit']['gflg'][i] == 0 and myData['fit']['v'][i] != 0.0):
				
				#range gate number
				rng = myData['fit']['slist'][i]
				#get coords of r-b cell
				myPos = coordsList[myData['prm']['bmnum']][rng]
				#latitudinal index
				latInd = int(math.floor(myPos[0]/self.delLat))
				
				#convert coords to mlt
				mlt1 = aacgm.mltFromEpoch(time.mktime(myData['prm']['time'].timetuple()),myPos[1])
				#move a small amount in the azm direction
				newPos = utils.geoPack.greatCircleMove(myPos[0],myPos[1],1e3,myPos[2])
				#convert new position to mlt
				mlt2 = aacgm.mltFromEpoch(time.mktime(myData['prm']['time'].timetuple()),newPos[1])
				#get azimuth in mlt coords
				newAzm = utils.geoPack.greatCircleAzm(myPos[0],mlt1/24.*360.,newPos[0],mlt2/24.*360.)
				#compensate for neg. direction is away from radar
				newAzm = newAzm*(-1.)*myData['fit']['v'][i]/abs(myData['fit']['v'][i])
				
				#longitudinal index
				lonInd = int(math.floor(mlt1/24.*360./self.lats[latInd].delLon))
				
				#create a gridVec object and append it to the list of gridCells
				self.lats[latInd].cells[lonInd].allVecs.append(gridVec(abs(myData['fit']['v'][i]),myData['fit']['w_l'][i],\
				myData['fit']['p_l'][i],myData['prm']['stid'],myData['prm']['time'],myData['prm']['bmnum'],rng,newAzm))
				
				#increment number of vectors in grid cell and grid object
				self.lats[latInd].cells[lonInd].nVecs = self.lats[latInd].cells[lonInd].nVecs + 1
				self.nVecs = self.nVecs+1
			
			
			