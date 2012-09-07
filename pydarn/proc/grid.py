import utils,pydarn,math

class gridCell(object):
	"""
	*******************************
	CLASS pydarn.proc.grid

	EXAMPLES:
	
	DECLARATION: 
		
	ACCESS:
	
	Written by AJ 20120906
	*******************************
	"""
	
	def __init__(self,lat1,lat2,lon1,lon2,lon3,lon4):
		self.bl = [lat1,lon1]
		self.tl = [lat2,lon2]
		self.tr = [lat2,lon3]
		self.br = [lat1,lon4]
		
		
class latCell(object):
	"""
	*******************************
	CLASS pydarn.proc.grid

	EXAMPLES:
	
	DECLARATION: 
		
	ACCESS:
	
	Written by AJ 20120906
	*******************************
	"""
	
	def __init__(self,lat):
		
		self.lat = lat
		
		self.nCells = int(round(360.*math.sin(math.radians(90.-lat))))
		
		
		Re = 6378.1e3
		self.botLat = lat
		botRad = Re*math.cos(math.radians(lat))
		self.botDel = 2.*math.pi*botRad/self.nCells
		
		self.topLat = lat+1.
		topRad = Re*math.cos(math.radians(lat+1))
		self.topDel = 2.*math.pi*topRad/self.nCells
		
		self.cells = []
		oldLon = [0.,0.]
		for i in range(0,self.nCells):
			print self.botLat,self.topLat,oldLon[0],oldLon[1]
			
			coords1 = utils.greatCircleMove(self.botLat, oldLon[0], self.botDel, 90.)
			coords2 = utils.greatCircleMove(self.topLat, oldLon[1], self.topDel, 90.)
			c = gridCell(self.botLat,self.topLat,oldLon[0],oldLon[1],coords2[1],coords1[1])
			print c.bl,c.tl,c.tr,c.br
			oldLon = [coords1[1],coords2[1]]
		
		
class grid(object):
	"""
	*******************************
	CLASS pydarn.proc.grid

	EXAMPLES:
	
	DECLARATION: 
		
	ACCESS:
	
	Written by AJ 20120906
	*******************************
	"""
	
	def __init__(self):
		self.lats = []
		for i in range(0,90):
			l = latCell(float(i))
			self.lats.append(l)