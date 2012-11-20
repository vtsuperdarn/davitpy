# pydarn/plot/map.py
"""
*******************************
pydarn.plot.map
*******************************
Plot maps in polar projections 

This includes the following function(s):
	* **plot**
		Create an empty map

	* **overlayRadar**
		Overlay radar position and name on a map

	* **overlayFov**
		Overlay field(s)-of-view on a map
			
Created by Sebastien

*******************************
"""

# *************************************************************
def map(limits=None, lon_0=290., hemi='north', boundingLat=None, 
		grid=True, gridLabels=True,
		fillContinents='.8', fillOceans='None', 
		fillLakes='white', coastLineWidth=0., 
		coords='geo', datetime=None):
	"""Create empty map    

**INPUTS**:    
	* **[limits]**: [llLat, llLon, urLat, urLon] lower-left and upper-right corners coordinates    
	* **[lon_0]**: center meridian (default is -70E)    
	* **[hemi]**: 'north' (default) or 'south'    
	* **[boundingLat]**: bounding latitude (default it +/-20)    
	* **[grid]**: show/hide parallels and meridians grid    
	* **[fill_continents]**: continent color. Default is 'grey'    
	* **[fill_water]**: water color. Default is 'None'    
	* **[coords]**: 'geo'

**OUTPUTS**:    
	* **map**: a Basemap object  
	
**EXAMPLES**:     


Written by Sebastien 2012-08    

	"""
	from mpl_toolkits.basemap import Basemap, pyproj
	from pylab import text
	from numpy import arange, ones
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
		# draw parallels and meridians.
		# labels = [left,right,top,bottom]
		# label parallels on map
		parallels = arange(-80.,81.,20.)
		out = map.drawparallels(parallels, color='.6')
		if gridLabels: 
			lablon = int(limits[1]/10)*10
			x,y = map(lablon*ones(parallels.shape), parallels)
			for ix,iy,ip in zip(x,y,parallels):
				if not map.xmin <= ix <= map.xmax: continue
				if not map.ymin <= iy <= map.ymax: continue
				text(ix, iy, r"{:3.0f}$^\circ$".format(ip), 
					rotation=lablon-lon_0, va='center')
		# label meridians on bottom and left
		meridians = arange(-180.,181.,20.)
		if gridLabels: 
			merLabels = [True,False,False,True]
		else: 
			merLabels = [False,False,False,False]
		out = map.drawmeridians(meridians,
			labels=merLabels, color='.6')
	
	# Save projection coordinates
	map.projparams['coords'] = coords

	return map
	

# *************************************************************
def overlayRadar(Basemap, codes=None, ids=None, names=None, dateTime=None, 
				annotate=True, coords='geo', all=False, hemi=None,
				zorder=2, markerColor='k', markerSize=10, fontSize=10, xOffset=None):
	"""Overlay radar position(s) and name(s) on map    

**INPUTS**:    
	* **Basemap**: a python Basemap object on which to overplot the radar position(s)    
	* **[codes]**: a list of radar 3-letter codes to plot    
	* **[ids]**: a list of radar IDs to plot    
	* **[names]**: a list of radar names to plot    
	* **[dateTime]**: the date and time as a python datetime object    
	* **[annotate]**: wether or not to show the radar(s) name(s)    
	* **[coords]**: 'geo' (default), 'mag', 'mlt' (not implemented yet)    
	* **[all]**: set to true to plot all the radars (active ones) 
	* **[hemi]**: 'north' or 'south', ignore radars from the other hemisphere   
	* **[zorder]**: the overlay order number    
	* **[markerColor]**:     
	* **[markerSize]**: [point]    
	* **[fontSize]**: [point]    
	* **[xOffset]**: x-Offset of the annotation in map projection coordinates    

**OUTPUTS**:     

Written by Sebastien 2012-08 
	
	"""
	from pydarn.radar import network
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
		codes = NetworkObj.getAllCodes(datetime=dateTime, hemi=hemi)
	
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

	if hemi is None:
		hemiInt = 0
	else:
		hemiInt = 1 if hemi.lower()[0]=='n' else -1
	
	# iterates through radars to be plotted
	for radN in input['vals']:
		rad = NetworkObj.getRadarBy(radN, input['meth'])
		if not rad: continue
		site = rad.getSiteByDate(dateTime)
		if not site: continue
		# Check for hemisphere specification
		if site.geolat*hemiInt < 0: continue
		# Get radar coordinates in map projection
		if(coords == 'geo'):
			x,y = Basemap(site.geolon, site.geolat)
		elif(coords == 'mag'):
			import models.aacgm as aacgm
			magc = aacgm.aacgmConv(site.geolat,site.geolon,0.,0)
			x,y = Basemap(magc[1], magc[0])
		if not Basemap.xmin <= x <= Basemap.xmax: continue
		if not Basemap.ymin <= y <= Basemap.ymax: continue
		# Plot radar position
		Basemap.scatter(x, y, s=markerSize, marker='o', color=markerColor, zorder=2)
		# Now add radar name
		if annotate:
			# If any of the other radar is too close...
			if rad.code[0] in ['adw', 'kod', 'cve', 'fhe', 'wal', 'gbr', 'pyk', 'aze']:
				xOff = width*.005 if not xOffset else xOffset
				ha = 'left'
			elif rad.code[0] in ['ade', 'ksr', 'cvw', 'fhw', 'bks', 'sch', 'sto', 'azw']:
				xOff = -width*.005 if not xOffset else xOffset
				ha = 'right'
			else: 
				xOff = 0.0
				ha = 'center'
			# Plot radar name
			plt.text(x + xOff, y - height*.01, rad.code[0].upper(), 
				ha=ha, va='top', variant='small-caps', fontsize=fontSize, zorder=zorder)

	return


# *************************************************************
def overlayFov(Basemap, codes=None, ids=None, names=None, 
				dateTime=None, coords='geo', all=False, 
				maxGate=None, fovColor=None, fovAlpha=0.2, 
				beams=None, hemi=None, fovObj=None, 
				zorder=2, lineColor='k', lineWidth=1):
	"""Overlay FoV position(s) on map

**INPUTS**:

	* **Basemap**: a python Basemap object on which to overplot the radar position(s)
	* **[codes]**: a list of radar 3-letter codes to plot
	* **[ids]**: a list of radar IDs to plot
	* **[names]**: a list of radar names to plot
	* **[dateTime]**: the date and time as a python datetime object
	* **[coords]**: 'geo' (default), 'mag', 'mlt' (not implemented yet)
	* **[all]**: set to true to plot all the radars (active ones)
	* **[maxGate]**: Maximum number of gates to be plotted. Defaults to hdw.dat information.
	* **[zorder]**: the overlay order number
	* **[lineColor]**: FoV contour line color
	* **[lineWidth]**: FoV contour line width
	* **[fovColor]**: field of view fill color
	* **[fovAlpha]**: field of view fill color transparency
	* **[fovObj]**: a fov object. See pydarn.radar.radFov.fov
	* **[hemi]**: 'north' or 'south', ignore radars from the other hemisphere
	* **[beam]**: hightlight specified beams

**OUTPUTS**:

Written by Sebastien 2012-09
	
	"""
	from pydarn.radar import network
	from pydarn.radar.radFov import fov
	from datetime import datetime as dt
	from datetime import timedelta
	import matplotlib.cm as cm
	from numpy import transpose, ones, concatenate, vstack
	from matplotlib.patches import Polygon
	from pylab import gca
	
	# Set default date/time to now
	if not dateTime:
		dateTime = dt.utcnow()
	
	# Load radar structure
	NetworkObj = network()
	
	# If all radars are to be plotted, create the list
	if all: codes = NetworkObj.getAllCodes(datetime=dateTime, hemi=hemi)
	
	# Define how the radars to be plotted are identified (code, id or name)
	if codes:
		if isinstance(codes, str): codes = [codes]
		nradars = len(codes)
		input = {'meth': 'code', 'vals': codes}
	elif ids:
		try:
			[c for c in ids]
		except:
			ids = [ids]
		finally:
			nradars = len(ids)
			input = {'meth': 'id', 'vals': ids}
	elif names:
		if isinstance(names, str): names = [names]
		nradars = len(names)
		input = {'meth': 'name', 'vals': names}
	elif fovObj == None:
		print 'overlayRadar: no radars to plot'
		return
	else: nradars = 1
	
	# iterates through radars to be plotted
	for ir in xrange(nradars):
		# Get field of view coordinates
		if(fovObj == None):
			rad = NetworkObj.getRadarBy(input['vals'][ir], input['meth'])
			if not rad: continue
			site = rad.getSiteByDate(dateTime)
			if not site: continue
			# Set number of gates to be plotted
			eGate = site.maxgate-1 if not maxGate else maxGate
			radFov = fov(site=site, ngates=eGate+1, coords = coords)
		else:
			radFov = fovObj
			eGate = len(fovObj.gates)
		# Get radar coordinates in map projection
		x,y = Basemap(radFov.lonFull, radFov.latFull)
		# Plot field of view
		# Create contour
		contourX = concatenate( (x[0,0:eGate], 
								 x[:,eGate],
								 x[-1,eGate::-1],
								 x[-1::-1,0]) )
		contourY = concatenate( (y[0,0:eGate], 
								 y[:,eGate],
								 y[-1,eGate::-1],
								 y[-1::-1,0]) )
		# Plot contour
		Basemap.plot(contourX, contourY, 
			color=lineColor, zorder=4, linewidth=lineWidth)
		# Field of view fill
		if fovColor:
			contour = transpose( vstack((contourX,contourY)) )
			patch = Polygon( contour, color=fovColor, alpha=fovAlpha)
			gca().add_patch(patch)
		# Beams fill
		if beams:
			for ib in beams:
				if not (0 <= ib <= site.maxbeam): continue
				bCol = ib/float(site.maxbeam)
				contourX = concatenate( (x[ib,0:eGate], 
										 x[ib:ib+2,eGate],
										 x[ib+1,eGate::-1],
										 x[ib+1:ib-1:-1,0]) )
				contourY = concatenate( (y[ib,0:eGate], 
										 y[ib:ib+2,eGate],
										 y[ib+1,eGate::-1],
										 y[ib+1:ib-1:-1,0]) )
				contour = transpose( vstack((contourX,contourY)) )
				patch = Polygon( contour, color=(bCol/2.,bCol,1), alpha=.4)
				gca().add_patch(patch)
	
	return