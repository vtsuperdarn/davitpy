import utils,pydarn

class latCells():
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
		self.nCells = round(360.*sin(radians(90.-lat)))
		Re = 6378.1e3
		self.bot = lat
		self.top = lat+1
		
		calcDistPnt(origLat, origLon, origAlt, dist=None, el=None, az=None, distLat=None, distLon=None, distAlt=None)
		
class grid():
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
			self.lats.append()