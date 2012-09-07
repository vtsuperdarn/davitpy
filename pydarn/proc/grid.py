import utils,pydarn,aacgm,math,datetime

def makeGrid(dateStr,rad,times=[0,2400],interval=120):
	
	myDate = utils.yyyymmddToDate(dateStr)
	hr1,hr2 = int(math.floor(times[0]/100./2.)*2),int(math.floor(times[1]/100./2.)*2)
	min1 = int(times[0]-int(math.floor(times[0]/100.)*100))
	stime = myDate.replace(hour=hr1,minute=min1)
	stime = stime-datetime.timedelta(minutes=4)
	if(hr2 == 24):
		etime = myDate+datetime.timedelta(days=1)
	else:
		etime = myDate.replace(hour=hr2)
	
	#read the radar data
	myData = pydarn.io.radDataRead(dateStr,rad,time=times)
	
	myGrids = []
	
	ctime = stime
	lastInd = 0
	while ctime <= etime:
		bt = ctime+datetime.timedelta(seconds=interval)
		
		for i in range(lastInd,myData.nrecs):
			t = myData.times[i]
			print i,ctime,t,myData.nrecs
			if(ctime < t <= bt):
				g = grid()
				#g.enterData(myData)
			elif(t > bt):
				lastInd = i
				break
	
	
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
		
		self.center = [(lat1+lat2)/2,(lon1+lon4)/2.]

		
		
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
		self.lats = []
		self.nLats = 90;
		for i in range(0,self.nLats):
			l = latCell(float(i))
			self.lats.append(l)