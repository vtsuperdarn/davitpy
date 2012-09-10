import utils,pydarn,aacgm,math,datetime,time,copy

def makeGrid(dateStr,rad,times=[0,2400],interval=120,vb=0):
	
	myDate = utils.yyyymmddToDate(dateStr)
	hr1,hr2 = int(math.floor(times[0]/100.)),int(math.floor(times[1]/100.))
	min1,min2 = int(times[0]-hr1*100),int(times[1]-hr2*100)
	stime = myDate.replace(hour=hr1,minute=min1)
	if(hr2 == 24):
		etime = myDate+datetime.timedelta(days=1)
	else:
		etime = myDate.replace(hour=hr2,minute=min2)
	
	#read the radar data
	myData = pydarn.io.radDataRead(dateStr,rad,time=times)
	
	assert(myData.nrecs > 0),'error, no data for this time period'
	
	site = pydarn.radar.network().getRadarByCode(rad).getSiteByDate(myData.times[0])
	coordsList = [[0]*site.maxgate]*site.maxbeam

	myGrids = []
	g = grid()
	ctime = stime
	lastInd = 0
	
	while ctime <= etime:
		
		bndT = ctime+datetime.timedelta(seconds=interval)
		
		g.delVecs()
		
		if(vb==1): print ctime
		
		for i in range(lastInd,myData.nrecs):
			
			t = myData.times[i]
			
			if(ctime < t <= bndT): 
				for j in range(0,myData[t]['fit']['npnts']):
					if(coordsList[myData[t]['prm']['bmnum']][myData[t]['fit']['slist'][j]] == 0):
						myPos = aacgm.rPosMag(myData[t]['prm']['bmnum'],myData[t]['fit']['slist'][j],\
						myData[t]['prm']['stid'],time.mktime(t.timetuple()),myData[t]['prm']['frang'],\
						myData[t]['prm']['rsep'],myData[t]['prm']['rxrise'],300.)
						
						coordsList[myData[t]['prm']['bmnum']][myData[t]['fit']['slist'][j]] = myPos
						
				g.enterData(myData[t],coordsList)
				
			elif(t > bndT): break
			
		lastInd = i
		if(g.nVecs > 0):
			g.stime = ctime
			g.etime = bndT
			myGrids.append(copy.deepcopy(g))
			
		ctime = bndT

	pydarn.plot.grid.plotGrid(myGrid = myGrids[0])
	
	for i in range(1,len(myGrids)):
		pydarn.plot.grid.plotGrid(myGrid=myGrids[i], grid=0)
		
	return myGrids
	
	
class gridVec(object):
	"""
	*******************************
	CLASS pydarn.proc.grid.gridVec
	
	a class defining a single gridded vector
	
	EXAMPLES:
	
	DECLARATION: 
		myVel = pydarn.proc.grid.gridVec(v,w_l,p_l,stid,time,azm):
	MEMBERS:
		v : Doppler velocity
		w_l : spectral width
		p_l : power
		stid : station id
		time: time of the measurement
		azm: azimuth of the measurement
		
		
	
	Written by AJ 20120907
	*******************************
	"""
	
	def __init__(self,v,w_l,p_l,stid,time,azm):
		self.v = v
		self.w_l = w_l
		self.p_l = p_l
		self.stid = stid
		self.time = time
		self.azm = azm
		
		
class gridCell(object):
	"""
	*******************************
	CLASS pydarn.proc.grid.gridCell
	
	a class defining a single grid cell

	EXAMPLES:
	
	DECLARATION: 
		myCell = pydarn.proc.grid.gridCell()
	MEMBERS:
		bl : bottom left corner in [lat,mlt]
		tl : bottom left corner in [lat,mlt]
		tr : top right corner in [lat,mlt]
		br : bottom right corner in [lat,mlt]
		
		
	
	Written by AJ 20120907
	*******************************
	"""
	
	def __init__(self,lat1,lat2,lon1,lon2,lon3,lon4):
		self.bl = [lat1,lon1]
		self.tl = [lat2,lon2]
		self.tr = [lat2,lon3]
		self.br = [lat1,lon4]
		self.center = [(lat1+lat2)/2.,(lon1+lon4)/2.]
		
		
		self.nVecs = 0
		self.vecs = []
		
		

		
class latCell(object):
	"""
	*******************************
	CLASS pydarn.proc.grid.latCell
	
	a class to hols the information for a single latitude
	or a geospatial grid

	EXAMPLES:
	
	DECLARATION: 
		myLat = pydarn.proc.grid.latCell()
	MEMBERS:
		nCells : the number of gridCells contained in this latCell
		botLat : the lower latitude limit of thsi cell
		topLat : the upper latitude limit of this cell
		delta : the step size (in degrees) in longitude for this
			latCell
		cells : a list of coords of the actual gridCells in
			lat,mlt coords
		
	
	Written by AJ 20120907
	*******************************
	"""
	
	def __init__(self,lat):
		
		self.nCells = int(round(360.*math.sin(math.radians(90.-lat))))
		
		Re = 6378.1
		self.botLat = lat
		delt = 360./self.nCells
		self.delta = delt
		self.topLat = lat+1.
		
		self.cells = []
		
		oldLon = [0.,0.]
		
		for i in range(0,self.nCells):

			newLon = [oldLon[0]+delt,oldLon[1]+delt]

			mlt1 = aacgm.mltFromYmdhms(2012,1,1,0,0,0,oldLon[0])
			mlt2 = aacgm.mltFromYmdhms(2012,1,1,0,0,0,oldLon[1])
			mlt3 = aacgm.mltFromYmdhms(2012,1,1,0,0,0,newLon[1])
			mlt4 = aacgm.mltFromYmdhms(2012,1,1,0,0,0,newLon[0])

			c = gridCell(self.botLat,self.topLat,mlt1,mlt2,mlt3,mlt4)

			self.cells.append(c)
			oldLon = newLon
		
		
class grid(object):
	"""
	*******************************
	CLASS pydarn.proc.grid
	
	the top level class for defining a geospatial grid for 
	velocity gridding

	EXAMPLES:
	
	DECLARATION: 
		myGrid = pydarn.proc.grid.grid()
	MEMBERS:
		lats : a list of latCell objects
		nLats : an integer number equal to the number of
			items in the lats list
		
	
	Written by AJ 20120907
	*******************************
	"""
	
	def __init__(self):
		self.nVecs = 0
		self.lats = []
		self.nLats = 90
		
		for i in range(0,self.nLats):
			l = latCell(float(i))
			self.lats.append(l)
			
	def delVecs(self):
		self.nVecs = 0
		for i in range(0,self.nLats):
			for j in range(self.lats[i].nCells):
				self.lats[i].cells[j].vecs = [];
				self.lats[i].cells[j].nVecs = 0;
				
	def enterData(self,myData,coordsList):
		
		for i in range(0,myData['fit']['npnts']):
			
			rng = myData['fit']['slist'][i]
			
			myPos = coordsList[myData['prm']['bmnum']][myData['fit']['slist'][i]]
			
			latInd = int(math.floor(myPos[0]))
			lonInd = int(math.floor(myPos[1]/self.lats[latInd].delta))
			
			mlt1 = aacgm.mltFromEpoch(time.mktime(myData['prm']['time'].timetuple()),myPos[1])
			newPos = utils.geoPack.greatCircleMove(myPos[0],myPos[1],1e3,myPos[2])
			mlt2 = aacgm.mltFromEpoch(time.mktime(myData['prm']['time'].timetuple()),newPos[1])
			
			newAzm = utils.geoPack.greatCircleAzm(myPos[0],mlt1/24.*360.,newPos[0],mlt2/24.*360.)
			
			self.lats[latInd].cells[lonInd].vecs.append(gridVec(myData['fit']['v'][i],myData['fit']['w_l'][i],\
			myData['fit']['p_l'][i],myData['prm']['stid'],myData['prm']['time'],myPos[2]))
			self.lats[latInd].cells[lonInd].nVecs = self.lats[latInd].cells[lonInd].nVecs + 1
			self.nVecs = self.nVecs+1
			
			
			