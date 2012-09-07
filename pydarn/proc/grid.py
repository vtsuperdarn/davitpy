import utils,pydarn,aacgm,math,numpy

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

	EXAMPLES:
	
	DECLARATION: 
		
	ACCESS:
	
	Written by AJ 20120906
	*******************************
	"""
	
	def __init__(self):
		self.lats = []
		self.nLats = 90;
		for i in range(0,self.nLats):
			l = latCell(float(i))
			self.lats.append(l)