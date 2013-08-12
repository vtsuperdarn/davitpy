# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: pydarn.plotting.mapOverlay
*********************
Overlay information on maps

**Functions**:
	* :func:`overlayRadar`: Overlay radar position and name on a map
	* :func:`overlayFov`: Overlay field(s)-of-view on a map

"""


# *************************************************************
def overlayRadar(Basemap, codes=None, ids=None, names=None, dateTime=None, 
				annotate=True, all=False, hemi=None,
				zorder=2, markerColor='k', markerSize=10, 
				fontSize=10, xOffset=None):
	"""Overlay radar position(s) and name(s) on map 
	
	**Args**: 
		* **Basemap**: a python Basemap object on which to overplot the radar position(s)    
		* **[codes]**: a list of radar 3-letter codes to plot    
		* **[ids]**: a list of radar IDs to plot    
		* **[names]**: a list of radar names to plot    
		* **[dateTime]**: the date and time as a python datetime object    
		* **[annotate]**: wether or not to show the radar(s) name(s)       
		* **[all]**: set to true to plot all the radars (active ones) 
		* **[hemi]**: 'north' or 'south', ignore radars from the other hemisphere   
		* **[zorder]**: the overlay order number    
		* **[markerColor]**:     
		* **[markerSize]**: [point]    
		* **[fontSize]**: [point]    
		* **[xOffset]**: x-Offset of the annotation in points  
	**Returns**:
		* None
	**Example**:
		::

			import pydarn, utils
			m1 = utils.plotUtils.mapObj(boundinglat=30., gridLabels=True, coords='mag')
			pydarn.plot.overlayRadar(m1, fontSize=8, all=True, markerSize=5)
			
	written by Sebastien, 2012-08
	"""
	from pydarn.radar import network
	from datetime import datetime as dt
	from datetime import timedelta
	from utils.plotUtils import textHighlighted
	
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
		if not hasattr(Basemap, 'coords'): 
			x,y = Basemap(site.geolon, site.geolat)
		else:
			x,y = Basemap(site.geolon, site.geolat, coords='geo')
		if not Basemap.xmin <= x <= Basemap.xmax: continue
		if not Basemap.ymin <= y <= Basemap.ymax: continue
		# Plot radar position
		Basemap.scatter(x, y, s=markerSize, marker='o', color=markerColor, zorder=zorder)
		# Now add radar name
		if annotate:
			# If any of the other radar is too close...
			if rad.code[0] in ['adw', 'kod', 'cve', 'fhe', 'wal', 'gbr', 'pyk', 'aze', 'sys']:
				xOff = 5 if not xOffset else xOffset
				ha = 0
			elif rad.code[0] in ['ade', 'ksr', 'cvw', 'fhw', 'bks', 'sch', 'sto', 'azw', 'sye']:
				xOff = -5 if not xOffset else xOffset
				ha = 1
			else: 
				xOff = 0.0
				ha = .5
			# Plot radar name
			textHighlighted((x, y), rad.code[0].upper(), xytext=(xOff, -5), 
				text_alignment=(ha,1), variant='small-caps', fontsize=fontSize, zorder=zorder)

	return


# *************************************************************
def overlayFov(Basemap, codes=None, ids=None, names=None, 
				dateTime=None, all=False, 
				maxGate=None, fovColor=None, fovAlpha=0.2, 
				beams=None, beamsColors=None, hemi=None, fovObj=None, 
				zorder=2, lineColor='k', lineWidth=1):
	"""Overlay FoV position(s) on map
	
	**Args**: 
		* **Basemap**: a python Basemap object on which to overplot the radar position(s)
		* **[codes]**: a list of radar 3-letter codes to plot
		* **[ids]**: a list of radar IDs to plot
		* **[names]**: a list of radar names to plot
		* **[dateTime]**: the date and time as a python datetime object
		* **[all]**: set to true to plot all the radars (active ones)
		* **[maxGate]**: Maximum number of gates to be plotted. Defaults to hdw.dat information.
		* **[zorder]**: the overlay order number
		* **[lineColor]**: FoV contour line color
		* **[lineWidth]**: FoV contour line width
		* **[fovColor]**: field of view fill color
		* **[fovAlpha]**: field of view fill color transparency
		* **[fovObj]**: a fov object. See pydarn.radar.radFov.fov
		* **[hemi]**: 'north' or 'south', ignore radars from the other hemisphere
		* **[beams]**: hightlight specified beams 
		* **[beamsColors]**: colors of the hightlighted beams 
	**Returns**:
		* None
	**Example**:
		::

			import pydarn, utils
			width = 111e3*40
			m = utils.plotUtils.mapObj(width=width, height=width, lat_0=50., lon_0=-95.)
			# Plot radar position and code
			pydarn.plot.overlayRadar(m, fontSize=12, codes='bks')
			# Plot radar fov
			pydarn.plot.overlayFov(m, codes='bks', maxGate=75, beams=[0,4,7,8,23])
			
	written by Sebastien, 2012-09
	"""
	from pydarn.radar import network
	from pydarn.radar.radFov import fov
	from datetime import datetime as dt
	from datetime import timedelta
	import matplotlib.cm as cm
	from numpy import transpose, ones, concatenate, vstack, shape
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
		input = {'meth': 'code', 'vals': codes}
	elif ids:
		input = {'meth': 'id', 'vals': ids}
	elif names:
		input = {'meth': 'name', 'vals': names}
	else:
		print 'overlayFov: no radars to plot'
		return
	
	# Check if radars is given as a list
	if not isinstance(input['vals'], list): input['vals'] = [input['vals']]

	nradars = len(input['vals'])
	
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
			if not hasattr(Basemap, 'coords'): 
				radFov = fov(site=site, ngates=eGate+1)
			else:
				radFov = fov(site=site, ngates=eGate+1, coords=Basemap.coords)
		else:
			radFov = fovObj
			eGate = len(fovObj.gates)
		# Get radar coordinates in map projection
		if hasattr(Basemap, 'coords'): 
			x, y = Basemap(radFov.lonFull, radFov.latFull, coords=radFov.coords)
		else:
			x, y = Basemap(radFov.lonFull, radFov.latFull)
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
			color=lineColor, zorder=zorder, linewidth=lineWidth)
		# Field of view fill
		if fovColor:
			contour = transpose( vstack((contourX,contourY)) )
			patch = Polygon( contour, color=fovColor, alpha=fovAlpha, zorder=zorder)
			gca().add_patch(patch)
		# Beams fill
		if beams:
			try:
				[b for b in beams]
			except:
				beams = [beams]
			for ib in beams:
				if not (0 <= ib <= x.shape[0]): continue
				if not beamsColors:
					bColRGB = ib/float(x.shape[0])
					bCol = (bColRGB/2.,bColRGB,1)
				else:
					bCol = beamsColors[beams.index(ib)]
				contourX = concatenate( (x[ib,0:eGate+1], 
										 x[ib:ib+2,eGate],
										 x[ib+1,eGate::-1],
										 x[ib+1:ib-1:-1,0]) )
				contourY = concatenate( (y[ib,0:eGate+1], 
										 y[ib:ib+2,eGate],
										 y[ib+1,eGate::-1],
										 y[ib+1:ib-1:-1,0]) )
				contour = transpose( vstack((contourX,contourY)) )
				patch = Polygon( contour, color=bCol, alpha=.4, zorder=zorder)
				gca().add_patch(patch)
	
	return