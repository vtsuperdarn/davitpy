# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: utils.plot
*********************
Basic plotting tools

**Functions**:
	* :func:`map`: Create empty map 
"""

# *************************************************************
def map(limits=None, lon_0=290., hemi='north', boundingLat=None, 
		grid=True, gridLabels=True,
		fillContinents='.8', fillOceans='None', 
		fillLakes='white', coastLineWidth=0., 
		coords='geo', datetime=None):
	"""Create empty map 
	
	**Args**: 
		* **[limits]**: [llLat, llLon, urLat, urLon] lower-left and upper-right corners coordinates    
		* **[lon_0]**: center meridian (default is -70E)    
		* **[hemi]**: 'north' (default) or 'south'    
		* **[boundingLat]**: bounding latitude (default it +/-20)    
		* **[grid]**: show/hide parallels and meridians grid    
		* **[fill_continents]**: continent color. Default is 'grey'    
		* **[fill_water]**: water color. Default is 'None'    
		* **[coords]**: 'geo'
	**Returns**:
		* **map**: a Basemap object 
	**Example**:
		::

			radars = pydarn.radar.radarRead()
			
	written by Sebastien, 2012-08
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


def genCmap(fig,coll,param,scale,pos=[0,0,1,1],colors='lasse',map=0,gflg=0):

	"""
	******************************
	genCmap(fig,coll,param,scale,pos,[colors]):
	
	generates a colormap and plots a colorbar

	INPUTS:
		fig: the parent figure
		coll: the collection of items (e.g. polygons) being mapped 
			to this colormap
		param: the parameter being plotted, valid for 'velocity',
			'power', 'width', 'elevation', 'phi0'
		scale: the max and min values of the color scale in list form
		pos: the position of the parent plot, NOT of the COLORBAR
		[colors]: a string indicating which colorbar to use, valid 
			inputs are 'lasse', 'aj'
			default: 'lasse'
	OUTPUTS:

	EXAMPLE:
		genCmap(myFig,polyCollection,'velocity',[-200,200],pos)
		
	Written by AJ 20120820
	
	*******************************
	"""
	import matplotlib,numpy
	import matplotlib.pyplot as plot
	
	#the MPL colormaps we will be using
	cmj = matplotlib.cm.jet
	cmpr = matplotlib.cm.prism
	
	#check for a velocity plot
	if(param == 'velocity'):
		
		#check for what color scale we want to use
		if(colors == 'aj'):
			if(gflg == 0):
				#define our discrete colorbar
				cmap = matplotlib.colors.ListedColormap([cmpr(.142),cmpr(.125),cmpr(.11),cmpr(.1),\
				cmpr(.175),cmpr(.158),cmj(.32),cmj(.37)])
			else:
				cmap = matplotlib.colors.ListedColormap([cmpr(.142),cmpr(.125),cmpr(.11),cmpr(.1),'.6',\
				cmpr(.175),cmpr(.158),cmj(.32),cmj(.37)])
		else:
			if(gflg == 0):
				#define our discrete colorbar
				cmap = matplotlib.colors.ListedColormap([cmj(.9),cmj(.8),cmj(.7),cmj(.65),\
				cmpr(.142),cmj(.45),cmj(.3),cmj(.1)])
			else:
				cmap = matplotlib.colors.ListedColormap([cmj(.9),cmj(.8),cmj(.7),cmj(.65),'.6',\
				cmpr(.142),cmj(.45),cmj(.3),cmj(.1)])
				
		#define the boundaries for color assignments
		bounds = numpy.round(numpy.linspace(scale[0],scale[1],7))
		if(gflg == 1):
			bounds[3] = -15.
			bounds = numpy.insert(bounds,4,15.)
		bounds = numpy.insert(bounds,0,-50000.)
		bounds = numpy.append(bounds,50000.)
		norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
		
	elif(param == 'phi0'):
		#check for what color scale we want to use
		if(colors == 'aj'):
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmpr(.142),cmpr(.125),cmpr(.11),cmpr(.1),\
			cmpr(.18),cmpr(.16),cmj(.32),cmj(.37)])
		else:
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmj(.9),cmj(.8),cmj(.7),cmj(.65),\
			cmpr(.142),cmj(.45),cmj(.3),cmj(.1)])
			
		#define the boundaries for color assignments
		bounds = numpy.linspace(scale[0],scale[1],9)
		norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
		
	elif(param == 'grid'):
		#check what color scale we want to use
		if(colors == 'aj'):
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmpr(.175),cmpr(.17),cmj(.32),cmj(.37),\
			cmpr(.142),cmpr(.13),cmpr(.11),cmpr(.10)])
		else:
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmj(.1),cmj(.3),cmj(.45),cmpr(.142),\
			cmj(.65),cmj(.7),cmj(.8),cmj(.9)])
			
		#define the boundaries for color assignments
		bounds = numpy.round(numpy.linspace(scale[0],scale[1],8))
		bounds = numpy.append(bounds,50000.)
		norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
		
	#if its a non-velocity plot
	else:
		
		#check what color scale we want to use
		if(colors == 'aj'):
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmpr(.175),cmpr(.158),cmj(.32),cmj(.37),\
			cmpr(.142),cmpr(.13),cmpr(.11),cmpr(.10)])
		else:
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmj(.1),cmj(.3),cmj(.45),cmpr(.142),\
			cmj(.65),cmj(.7),cmj(.8),cmj(.9)])
			
		#define the boundaries for color assignments
		bounds = numpy.round(numpy.linspace(scale[0],scale[1],8))
		bounds = numpy.append(bounds,50000.)
		norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
		

	cmap.set_bad('w',1.0)
	cmap.set_over('w',1.0)
	#cmap.set_under('w',1.0)

	cb = drawCB(fig,coll,cmap,norm,map=map,pos=pos)
	l = []
	#define the colorbar labels
	for i in range(0,len(bounds)):
		if(param == 'phi0'):
			ln = 4
			if(bounds[i] == 0): ln = 3
			elif(bounds[i] < 0): ln = 5
			l.append(str(bounds[i])[:ln])
			continue
		if((i == 0 and param == 'velocity') or i == len(bounds)-1):
			l.append(' ')
			continue
		l.append(str(int(bounds[i])))
	cb.ax.set_yticklabels(l)
		
	#set colorbar ticklabel size
	for t in cb.ax.get_yticklabels():
		t.set_fontsize(9)
	
	#set colorbar label
	if(param == 'velocity'): cb.set_label('Velocity [m/s]',size=10)
	if(param == 'grid'): cb.set_label('Velocity [m/s]',size=10)
	if(param == 'power'): cb.set_label('Power [dB]',size=10)
	if(param == 'width'): cb.set_label('Spec Wid [m/s]',size=10)
	if(param == 'elevation'): cb.set_label('Elev [deg]',size=10)
	if(param == 'phi0'): cb.set_label('Phi0 [rad]',size=10)
	
	return

def drawCB(fig,coll,cmap,norm,map=0,pos=[0,0,1,1]):
	import matplotlib,numpy
	import matplotlib.pyplot as plot

	if(map == 0):
		#create a new axes for the colorbar
		cax = fig.add_axes([pos[0]+pos[2]+.03, pos[1], 0.03, pos[3]])
		#set the colormap and boundaries for the collection
		#of plotted items
		if(isinstance(coll,list)):
			for c in coll:
				c.set_cmap(cmap)
				c.set_norm(norm)
				cb = plot.colorbar(c,cax=cax)
		else:
			coll.set_cmap(cmap)
			coll.set_norm(norm)
			cb = plot.colorbar(coll,cax=cax)
	else:
		if(isinstance(coll,list)):
			for c in coll:
				c.set_cmap(cmap)
				c.set_norm(norm)
				cb = fig.colorbar(c,location='right')
		else:
			coll.set_cmap(cmap)
			coll.set_norm(norm)
			cb = fig.colorbar(coll,location='right',pad="5%")
	
	cb.ax.tick_params(axis='y',direction='out')
	return cb