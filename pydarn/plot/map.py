# pydarn/plot/map.py
"""
*******************************
			map
*******************************
Plot maps in polar projections 

This includes the following function(s):
	plot
		Plot an empty map
	overlayRadar
		Overlay radar position and name on a map
	*overlayFov
	*overlayTerminator
	*overlayDaynight
			
Created by Sebastien
*******************************
"""

# *************************************************************
def map(limits=None, lon_0=290., hemi='north', boundingLat=None, \
		grid=True, fillContinents='grey', fillOceans='None', fillLakes='white', coastLineWidth=0.):
	"""
Plot empty map

INPUTS:
	limits: [llLat, llLon, urLat, urLon] lower-left and upper-right corners coordinates
	lon_0: center meridian (default is -70E)
	hemi: 'north' (default) or 'south'
	boundingLat: bounding latitude (default it +/-20)
	grid: show/hide parallels and meridians grid
	fill_continents: continent color. Default is 'grey'
	fill_water: water color. Default is 'None'
OUTPUTS:
	map: a Basemap object
	"""
	from mpl_toolkits.basemap import Basemap, pyproj
	from numpy import arange
	from math import sqrt
	
	# Set map projection limits and center point depending on hemisphere selection
	if hemi.lower() == 'north':
		sgn = 1
		# Map origin
		lat_0 = sgn*90.
	elif hemi.lower() == 'south':
		sgn = -1
		# Map origin
		lat_0 = sgn*90.
	# Map limits
	if not limits:
		# Set bounding latitude and calculate corner latitudes
		if not boundingLat:
			boundingLat = sgn*20.
		# This is a bit tricky, but this is how you get the proper corner coordinates to satisfy boundingLat value
		projparams = {'lon_0': lon_0, 'lat_ts': lat_0, 'R': 6370997.0, 'proj': 'stere', 'units': 'm', 'lat_0': lat_0}
		proj = pyproj.Proj(projparams)
		x,y = proj(lon_0,boundingLat)
		lon,llcLat = proj(sqrt(2.)*y,0., inverse=True)
		urcLat = llcLat
		# Finally, set limits for an isotropic map plot
		limits = [llcLat, lon_0-sgn*45., urcLat, lon_0+sgn*135.]
	
	# Draw map
	map = Basemap(projection='stere', resolution='l', \
				llcrnrlat=limits[0], llcrnrlon=limits[1], \
				urcrnrlat=limits[2], urcrnrlon=limits[3], \
				lat_0=lat_0, lon_0=lon_0)
	map.drawcoastlines(linewidth=coastLineWidth)
	map.drawmapboundary(fill_color=fillOceans)
	map.fillcontinents(color=fillContinents, lake_color=fillLakes)
	
	# draw parallels and meridians.
	if grid:
		out = map.drawparallels(arange(-80.,81.,20.))
		out = map.drawmeridians(arange(-180.,181.,20.))
	
	return map
	

# *************************************************************
def overlayRadar(Basemap, codes=None, ids=None, names=None, dateTime=None, annotate=True, coords='geo', all=False, \
				zorder=2, markerColor='k', markerSize=10, fontSize=10, xOffset=None):
	"""
Overlay radar position(s) and name(s) on map

INPUTS:
	Basemap: a python Basemap object on which to overplot the radar position(s)
	codes: a list of radar 3-letter codes to plot
	ids: a list of radar IDs to plot
	names: a list of radar names to plot
	dateTime: the date and time as a python datetime object
	annotate: wether or not to show the radar(s) name(s)
	coords: 'geo' (default), 'mag', 'mlt' (not implemented yest)
	all: set to true to plot all the radars (active ones)
	zorder: the overlay order number
	markerColor: 
	markerSize: [point]
	fontSize: [point]
	xOffset: x-Offset of the annotation in map projection coordinates
OUTPUTS:
	
	"""
	from ..radar.radNetwork import network
	from datetime import datetime as dt
	from datetime import timedelta
	import matplotlib.pyplot as plt
	
	# Set default date/time to now
	if not dateTime:
		dateTime = dt.utcnow()
	
	# Load radar structure
	NetworkObj = network()
	
	# If all radars are to be plotted, create the list
	if all:
		codes = []
		for irad in range( len(NetworkObj) ):
			if NetworkObj.info[irad].status != 0 and NetworkObj.info[irad].stTime <= dateTime <= NetworkObj.info[irad].edTime:
				codes.append(NetworkObj.info[irad].code[0])
	
	# Define how the radars to be plotted are identified (code, id or name)
	if codes:
		input = {'meth': 'code', 'vals': codes}
	elif ids:
		input = {'meth': 'id', 'vals': ids}
	elif names:
		input = {'meth': 'name', 'vals': names}
	else:
		print 'overlayRadar: no radars to plot'
		return
	
	# Check if radars is given as a list
	if not isinstance(input['vals'], list): input['vals'] = [input['vals']]
	
	# Map width and height
	width = Basemap.urcrnrx - Basemap.llcrnrx
	height = Basemap.urcrnry - Basemap.llcrnry
	
	# iterates through radars to be plotted
	for radN in input['vals']:
		rad = NetworkObj.getRadarBy(radN, input['meth'])
		if not rad: continue
		site = rad.getSiteByDate(dateTime)
		if not site: continue
		# Get radar coordinates in map projection
		x,y = Basemap(site.geolon, site.geolat)
		if not Basemap.xmin <= x <= Basemap.xmax: continue
		if not Basemap.ymin <= y <= Basemap.ymax: continue
		# Plot radar position
		Basemap.scatter(x, y, s=markerSize, marker='o', color=markerColor, zorder=2)
		# Now add radar name
		if annotate:
			# If any of the other radar is too close...
			if rad.code[0] in ['aiw', 'kod', 'cve', 'fhe', 'wal', 'gbr', 'pyk', 'aze']:
				xOff = width*.005 if not xOffset else xOffset
				ha = 'left'
			elif rad.code[0] in ['aie', 'ksr', 'cvw', 'fhw', 'bks', 'sch', 'sto', 'azw']:
				xOff = -width*.005 if not xOffset else xOffset
				ha = 'right'
			else: 
				xOff = 0.0
				ha = 'center'
			# Plot radar name
			plt.text(x + xOff, y - height*.01, rad.code[0].upper(), ha=ha, va='top', variant='small-caps', fontsize=fontSize, zorder=zorder)

	return


# *************************************************************
def overlayFov(Basemap, codes=None, ids=None, names=None, dateTime=None, coords='geo', all=False, \
				maxGate=None, \
				zorder=2, lineColor='k'):
	"""
Overlay FoV position(s) on map

INPUTS:
	Basemap: a python Basemap object on which to overplot the radar position(s)
	codes: a list of radar 3-letter codes to plot
	ids: a list of radar IDs to plot
	names: a list of radar names to plot
	dateTime: the date and time as a python datetime object
	coords: 'geo' (default), 'mag', 'mlt' (not implemented yest)
	all: set to true to plot all the radars (active ones)
	maxGate: Maximum number of gates to be plotted. Defaults to hdw.dat information.
	zorder: the overlay order number
	lineColor: FoV contour color
OUTPUTS:
	
	"""
	from ..radar.radNetwork import network
	from ..radar.radFov import fov
	from datetime import datetime as dt
	from datetime import timedelta
	import matplotlib.pyplot as plt
	
	# Set default date/time to now
	if not dateTime:
		dateTime = dt.utcnow()
	
	# Load radar structure
	NetworkObj = network()
	
	# If all radars are to be plotted, create the list
	if all:
		codes = []
		for irad in range( len(NetworkObj) ):
			if NetworkObj.info[irad].status != 0 and NetworkObj.info[irad].stTime <= dateTime <= NetworkObj.info[irad].edTime:
				codes.append(NetworkObj.info[irad].code[0])
	
	# Define how the radars to be plotted are identified (code, id or name)
	if codes:
		input = {'meth': 'code', 'vals': codes}
	elif ids:
		input = {'meth': 'id', 'vals': ids}
	elif names:
		input = {'meth': 'name', 'vals': names}
	else:
		print 'overlayRadar: no radars to plot'
		return
	
	# Check if radars is given as a list
	if not isinstance(input['vals'], list): input['vals'] = [input['vals']]
	
	# iterates through radars to be plotted
	for radN in input['vals']:
		rad = NetworkObj.getRadarBy(radN, input['meth'])
		if not rad: continue
		site = rad.getSiteByDate(dateTime)
		if not site: continue
		# Set number of gates to be plotted
		eGate = site.maxgate-1 if not maxGate else maxGate
		# Get field of view coordinates
		radFov = fov(site=site)
		# Get radar coordinates in map projection
		x,y = Basemap(radFov.lonFull, radFov.latFull)
#		if not Basemap.xmin <= x <= Basemap.xmax: continue
#		if not Basemap.ymin <= y <= Basemap.ymax: continue
		# Plot field of view
		# Side boundary
		Basemap.plot(x[0,0:eGate,0], y[0,0:eGate,0], color=lineColor)
		# Other side boundary
		Basemap.plot(x[-1,0:eGate,1], y[-1,0:eGate,1], color=lineColor)
		# Furthest boundary
		Basemap.plot(x[:,eGate,0], y[:,eGate,0], color=lineColor)
		Basemap.plot(x[-1,eGate,[0,1]], y[-1,eGate,[0,1]], color=lineColor)
		# Closest boundary
		Basemap.plot(x[:,0,0], y[:,0,0], color=lineColor)
		Basemap.plot(x[:,0,[0,1]], y[:,0,[0,1]], color=lineColor)
	
	return