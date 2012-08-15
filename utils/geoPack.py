# UTILS/geoPack
"""
*******************************
		geoPack
*******************************
This module contains the following functions
	geodToGeoc
		converts from geodetic to geocentric (and vice-versa)
	geodToGeocAzEl
		converts azimuth and elevation from geodetic to geocentric (and vice-versa)
	gspToGcar
		converts global spherical coordinates to global cartesian coordinates (and vice-versa)
	gcarToLcar
		converts from global cartesian coordinates to local cartesian coordinates (and vice-versa)
	lspToLcar
		converts from local spherical coordinates to local cartesian coordinates (and vice-versa)
	*calcDistPnt
		calculates the coordines|distance,elevation,azimuth of a point given a point of origin and distance,elevation,azimuth|distant point coordinates

Based on J.M. Ruohoniemi's geopack
Based on R.J. Barnes radar.pro
Created by Sebastien
*******************************
"""

# *************************************************************
def geodToGeoc(lat,lon,into='geoc'):
	""" (lat,lon,Re) = geodToGeoc(lat,lon,into='geoc')
Converts position from geodetic to geocentric and vice-versa.
Based on the IAU 1964 oblate spheroid model of the Earth.

INPUTS:
	lat: latitude [degree]
	lon: longitude [degree]
	into: 'geoc' (default) or 'geod' specifies the system to convert into
OUTPUTS
	lat: latitude [degree]
	lon: longitude [degree]
	Re: Earth radius [km]
	"""
	from math import degrees, radians, cos, sin, tan, atan, atan2, sqrt
	
	if not isinstance(into, str):
		print 'geodToGeoc: Argument "into" must be a string. Try again!'
		return
	
	a = 6378.16
	f = 1./298.25
	b = a*(1.-f)
	e2 = (a**2/b**2) - 1.
	
	if into == 'geoc':
		# geodetic into geocentric
		latOut = degrees( atan( b**2/a**2 * tan( radians(lat) ) ) )
		lonOut = lon
		Re = a / sqrt( 1. + e2 * sin( radians(latOut) )**2 )
	elif into == 'geod':
		# geocentric into geodetic
		latOut = degrees( atan( a**2/b**2 * tan( radians(lat) ) ) )
		lonOut = lon
		Re = a / sqrt( 1. + e2 * sin( radians(lat) )**2 )
	else:
		print 'geodToGeoc: {} is not a valid system.'.format(into)
		return
		
	return latOut, lonOut, Re


# *************************************************************
def geodToGeocAzEl(lat,lon,az,el,into='geoc'):
	""" (lat, lon, Re, az,el) = geodToGeocAzEl(lat,lon,az,el,into='geoc')
Converts pointing azimuth and elevation measured with respect to the local horizon 
to azimuth and elevation with respect to the horizon defined by the plane perpendicular 
to the Earth-centered radial vector drawn through a user defined point.

INPUTS:
	lat: latitude [degree]
	lon: longitude [degree]
	az: azimuth [degree, N]
	el: elevation [degree]
	into: 'geoc' (default) or 'geod' specifies the system to convert into
OUTPUTS
	lat: latitude [degree]
	lon: longitude [degree]
	Re: Earth radius [km]
	az: azimuth [degree, N]
	el: elevation [degree]
	"""
	from math import degrees, radians, cos, sin, tan, atan, atan2, sqrt
	
	if not isinstance(into, str):
		print 'geodToGeocAzEl: Argument "into" must be a string. Try again!'
		return
	
	# In this transformation x is east, y is north and z is up
	if into == 'geoc':
		# Calculate deviation from vertical (in radians)
		(geocLat, geocLon, Re) = geodToGeoc(lat, lon)
		devH = radians(lat - geocLat)
		# Calculate cartesian coordinated in local system
		kxGD = cos( radians(el) ) * sin( radians(az) )
		kyGD = cos( radians(el) ) * cos( radians(az) )
		kzGD = sin( radians(el) )
		# Now rotate system about the x axis to align local vertical vector with Earth radial vector
		kxGC = kxGD
		kyGC = kyGD * cos( devH ) + kzGD * sin( devH )
		kzGC = -kyGD * sin( devH ) + kzGD * cos( devH )
		# Finally calculate the new azimuth and elevation in the geocentric frame
		azOut = degrees( atan2( kxGC, kyGC ) )
		elOut = degrees( atan( kzGC / sqrt( kxGC**2 + kyGC**2 ) ) )
		latOut = geocLat
		lonOut = geocLon
	elif into == 'geod':
		# Calculate deviation from vertical (in radians)
		(geodLat, geodLon, Re) = geodToGeoc(lat, lon, into='geod')
		devH = radians(geodLat - lat)
		# Calculate cartesian coordinated in geocentric system
		kxGC = cos( radians(el) ) * sin( radians(az) )
		kyGC = cos( radians(el) ) * cos( radians(az) )
		kzGC = sin( radians(el) )
		# Now rotate system about the x axis to align local vertical vector with Earth radial vector
		kxGD = kxGC
		kyGD = kyGC * cos( -devH ) + kzGC * sin( -devH )
		kzGD = -kyGC * sin( -devH ) + kzGC * cos( -devH )
		# Finally calculate the new azimuth and elevation in the geocentric frame
		azOut = degrees( atan2( kxGD, kyGD ) )
		elOut = degrees( atan( kzGD / sqrt( kxGD**2 + kyGD**2 ) ) )
		latOut = geodLat
		lonOut = geodLon
	else:
		print 'geodToGeocAzEl: {} is not a valid system. Try again!'.format(into)
		return
	
	return latOut, lonOut, Re, azOut, elOut


# *************************************************************
def gspToGcar(X, Y, Z, into='gcar'):
	""" (X, Y, Z) = gspToGcar(X, Y, Z, into='gcar')
Converts a position from global spherical (geocentric) to global cartesian (and vice-versa).
The global cartesian coordinate system is defined as:
	- origin: center of the Earth
	- X axis in the equatorial plane and through the prime meridian.
	- Z axis in the direction of the rotational axis and through the North pole
The meaning of the input (X,Y,Z) depends on the direction of the conversion (to global cartesian
or to global spherical).

INPUTS:
	X: latitude [degree] or global cartesian X [km]
	Y: longitude [degree] or global cartesian Y [km]
	Z: distance from center of the Earth [km] or global cartesian Z [km]
	into: 'gcar' (global cartesian, default) or 'gsp' (global spherical) specifies the system to convert into
OUTPUTS
	X: global cartesian X [km] or latitude [degree]
	Y: global cartesian Y [km] or longitude [degree]
	Z: global cartesian Z [km] or distance from center of the Earth [km]
	"""
	from math import radians, degrees, cos, sin, asin, atan2, sqrt
	
	if not isinstance(into, str):
		print 'gspToGcar: Argument "into" must be a string. Try again!'
		return
	
	if into == 'gcar':
		# Global spherical to global cartesian
		xOut = Z * cos( radians(X) ) * cos( radians(Y) )
		yOut = Z * cos( radians(X) ) * sin( radians(Y) )
		zOut = Z * sin( radians(X) )
	elif into == 'gsp':
		# Calculate latitude (xOut), longitude (yOut) and distance from center of the Earth (zOut)
		zOut = sqrt( X**2 + Y**2 + Z**2 )
		xOut = degrees( asin( Z/zOut ) )
		yOut = degrees( atan2( Y, X ) )
	else:
		print 'gspToGcar: {} is not a valid system. Try again!'.format(into)
		
	return xOut, yOut, zOut


# *************************************************************
def gcarToLcar(X, Y, Z, lat, lon, rho , into='lcar'):
	""" (X, Y, Z) = gcarToLcar(X, Y, Z, lat, lon, alt, into='lcar')
Converts a position from global cartesian to local cartesian (and vice-versa).
The global cartesian coordinate system is defined as:
	- origin: center of the Earth
	- Z axis in the direction of the rotational axis and through the North pole
	- X axis in the equatorial plane and through the prime meridian.
The local cartesian coordinate system is defined as:
	- origin: local position
	- X: East
	- Y: North
	- Z: up
The meaning of the input (X,Y,Z) depends on the direction of the conversion (to global cartesian
or to global spherical).

INPUTS:
	X: global cartesian X [km] or local cartesian X [km]
	Y: global cartesian Y [km] or local cartesian Y [km]
	Z: global cartesian Z [km] or local cartesian Z [km]
	lat: geocentric latitude [degree] of local cartesian system origin
	lon: geocentric longitude [degree] of local cartesian system origin
	rho: distance from center of the Earth [km] of local cartesian system origin
	into: 'lcar' (local cartesian, default) or 'gcar' (global cartesian) specifies the system to convert into
OUTPUTS
	X: local cartesian X [km] or global cartesian X [km]
	Y: local cartesian Y [km] or global cartesian Y [km]
	Z: local cartesian Z [km] or global cartesian Z [km]
	"""
	from math import radians, degrees, cos, sin
	
	if not isinstance(into, str):
		print 'gcarToLcar: Argument "into" must be a string. Try again!'
		return
	
	# First get global cartesian coordinates of local origin
	(goX, goY, goZ) = gspToGcar(lat, lon, rho)
	
	if into == 'lcar':
		# Translate global position to local origin
		tx = X - goX
		ty = Y - goY
		tz = Z - goZ
		# Then, rotate about global-Z to get local-X pointing eastward
		sx = tx * cos( -radians(lon + 90.) ) - ty * sin( -radians(lon + 90.) )
		sy = tx * sin( -radians(lon + 90.) ) + ty * cos( -radians(lon + 90.) )
		sz = tz
		# Finally, rotate about X axis to align Z with upward direction
		xOut = sx
		yOut = sy * cos( -radians(90. - lat) ) - sz * sin( -radians(90. - lat) )
		zOut = sy * sin( -radians(90. - lat) ) + sz * cos( -radians(90. - lat) )
	elif into == 'gcar':
		# First rotate about X axis to align Z with Earth rotational axis direction
		sx = X
		sy = Y * cos( radians(90. - lat) ) - Z * sin( radians(90. - lat) )
		sz = Y * sin( radians(90. - lat) ) + Z * cos( radians(90. - lat) )
		# Then, rotate about global-Z to get global-X pointing to the prime meridian
		xOut = sx * cos( radians(lon + 90.) ) - sy * sin( radians(lon + 90.) )
		yOut = sx * sin( radians(lon + 90.) ) + sy * cos( radians(lon + 90.) )
		zOut = sz
		# Finally, translate local position to global origin
		xOut = xOut + goX
		yOut = yOut + goY
		zOut = zOut + goZ
	else:
		print 'gcarToLcar: {} is not a valid system. Try again!'.format(into)
	
	return xOut, yOut, zOut


# *************************************************************
def lspToLcar(X, Y, Z, into='lcar'):
	""" (X, Y, Z) = lspToLcar(X, Y, Z, into='lcar')
Converts a position from local spherical to local cartesian (and vice-versa).
The local spherical coordinate system is defined as:
	- origin: local position
	- azimuth (with respect to North)
	- Elevation (with respect to horizon)
	- Altitude
The local cartesian coordinate system is defined as:
	- origin: local position
	- X: East
	- Y: North
	- Z: up
The meaning of the input (X,Y,Z) depends on the direction of the conversion (to global cartesian
or to global spherical).

INPUTS:
	X: azimuth [degree, N] or local cartesian X [km]
	Y: elevation [degree] or local cartesian Y [km]
	Z: distance origin [km] or local cartesian Z [km]
	into: 'lcar' (local cartesian, default) or 'lsp' (local spherical) specifies the system to convert into
OUTPUTS
	X: local cartesian X [km] or azimuth [degree, N]
	Y: local cartesian Y [km] or elevation [degree]
	Z: local cartesian Z [km] or distance from origin [km]
	"""
	from math import radians, degrees, cos, sin, asin, atan2, sqrt
	
	if not isinstance(into, str):
		print 'lspToLcar: Argument "into" must be a string. Try again!'
		return
	
	if into == 'lcar':
		# local spherical into local cartesian
		r = Z
		el = Y
		az = X
		xOut = r * cos( radians(el) ) * sin( radians(az) )
		yOut = r * cos( radians(el) ) * cos( radians(az) )
		zOut = r * sin( radians(el) )
	elif into == 'lsp':
		# local cartesian into local spherical
		r = sqrt( X**2 + Y**2 + Z**2 )
		el = degrees( asin(Z/r) )
		az = degrees( atan2(X, Y) )
		xOut = az
		yOut = el
		zOut = r
	else:
		print 'lspToLcar: {} is not a valid system. Try again!'.format(into)
	
	return xOut, yOut, zOut


# *************************************************************
def calcDistPnt(origLat, origLon, origAlt, dist=None, el=None, az=None, distLat=None, distLon=None, distAlt=None):
	""" dict = calcDistPnt(origLat, origLon, origAlt, dist=None, el=None, az=None, distLat=None, distLon=None, distAlt=None)
Calculate the coordinates of a distant point given a point of origin, distance, azimuth and elevation,
or calculate the distance, azimuth and elevation between a point of origin and a distant point.
Input/output is in geodetic coordinates, distances are in km and angles in degrees.

INPUTS:
	origLat: geographic latitude of point of origin [degree]
	origLon: geographic longitude of point of origin [degree]
	origAlt: altitude of point of origin [km]
	dist, el, az: distance [km], azimuth [degree] and elevation [degree]. Must be set together.
	distLat, distLon, distAlt: latitude [degree], longitude [degree] and altitide [km] of distant point. Must be set together.
OUTPUTS
	dict: a dictionary containing all the information about origin and distant points and their relative positions
	"""
	from math import sqrt
	
	# If all the input parameters (keywords) are set to 0, show a warning, and default to fint distance/azimuth/elevation
	if None in [dist, el, az]:
		mode = 'findDistAzEl'
		if  None in [distLat, distLon, distAlt]:
			print 'calcDistPnt: Warning: No keywords are set.'
			return
		else: pass
#			print 'Calculating distance/azimuth/elevation to point ({:6.2f}N, {:6.2f}E, {:6.2f} km)'.format(distLat, distLon, distAlt)
	elif None in [distLat, distLon, distAlt]:
#		print 'Calculating coordinates of distant point at {:6.2f} km, {:6.2f}'.format(dist,az)+unichr(176)+'E, {:6.2f}'.format(el)+unichr(176)+' elevation.'
		mode = 'findDistPnt'
	else:
#		print 'calcDistPnt: Too many keywords set at once. This function does not understand what you are asking. Do you?'
		return
	
	if mode == 'findDistAzEl':
		# Convert point of origin from geodetic to geocentric
		(gcLat, gcLon, origRe) = geodToGeoc(origLat, origLon, into='geoc')
		# Convert distant point from geodetic to geocentric
		(gcDistLat, gcDistLon, distRe) = geodToGeoc(distLat, distLon, into='geoc')
		# convert point of origin from geocentric to global cartesian
		(pX, pY, pZ) = gspToGcar(gcDistLat, gcDistLon, distRe+distAlt, into='gcar')
		# convert pointing direction from global cartesian to local cartesian
		(dX, dY, dZ) = gcarToLcar(pX, pY, pZ, gcLat, gcLon, origRe+origAlt, into='lcar')
		# convert pointing direction from local cartesian to local spherical
		(gaz, gel, rho) = lspToLcar(dX, dY, dZ, into='lsp')
		# convert pointing azimuth and elevation to geodetic
		(lat, lon, Re, az, el) = geodToGeocAzEl(gcLat, gcLon, gaz, gel, into='geod')
		dist = sqrt( dX**2 + dY**2 + dZ**2 )
	elif mode == 'findDistPnt':
		# convert pointing azimuth and elevation to geocentric
		(gcLat, gcLon, origRe, gaz, gel) = geodToGeocAzEl(origLat, origLon, az, el, into='geoc')
		# convert pointing direction from local spherical to local cartesian
		(pX, pY, pZ) = lspToLcar(gaz, gel, dist, into='lcar')
		# convert pointing direction from local cartesian to global cartesian
		(dX, dY, dZ) = gcarToLcar(pX, pY, pZ, gcLat, gcLon, origRe+origAlt, into='gcar')
		# Convert distant point from global cartesian to geocentric
		(gcDistLat, gcDistLon, rho) = gspToGcar(dX, dY, dZ, into='gsp')
		# Convert distant point from geocentric to geodetic
		(distLat, distLon, Re) = geodToGeoc(gcDistLat, gcDistLon, into='geod')
		distAlt = rho - Re
		distRe = Re
	# Fill output dictionary
	dictOut = {'origLat': origLat, 'origLon': origLon, 'origAlt': origAlt, \
				'distLat': distLat, 'distLon': distLon, 'distAlt': distAlt, \
				'az': az, 'el': el, 'dist': dist, 'origRe': origRe, 'distRe': distRe}
	
	return dictOut

	
		
	
