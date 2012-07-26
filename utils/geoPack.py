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
	gspToCar
		converts global spherical coordinates to global cartesian coordinates (and vice-versa)
	gcarToLcar
		converts from global cartesian coordinates to local cartesian coordinates (and vice-versa)
	lspToLcar
		converts from local spherical coordinates to local cartesian coordinates (and vice-versa)
	*calcDistPnt
		calculates the coordines|distance,elevation,azimuth of a point given a point of origin and distance,elevation,azimuth|distant point coordinates

Based on J.M. Ruohoniemi's geopack
Created by Sebastien
*******************************
"""

# *************************************************************
def geodToGeoc(lat,lon,into='geoc'):
	""" (lat,lon,Re) = geodToGeoc(lat,lon,into='geoc')
Converts position from geodetic to geocentric and vice-versa.
Based on the IAU 1964 oblate spheroid model of the Earth

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
		print 'geodToGeoc: {} is not a valid system. Try again!'.format(into)
		return
		
	return latOut, lonOut, Re


# *************************************************************
def geodToGeocAzEl(lat,lon,az,el,into='geoc'):
	""" (az,el) = geodToGeocAzEl(lat,lon,az,el,into='geoc')
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
	else:
		print 'geodToGeocAzEl: {} is not a valid system. Try again!'.format(into)
		return
	
	return azOut, elOut


# *************************************************************
def gspToCar(X, Y, Z, into='car'):
	""" (X, Y, Z) = gspToCar(X, Y, Z, into='car')
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
	Z: altitude [km] or global cartesian Z [km]
	into: 'car' (cartesian, default) or 'gsp' (global spherical) specifies the system to convert into
OUTPUTS
	X: global cartesian X [km] or latitude [degree]
	Y: global cartesian Y [km] or longitude [degree]
	Z: global cartesian Z [km] or altitude [km]
	"""
	from math import radians, degrees, cos, sin, asin, atan2, sqrt
	
	if not isinstance(into, str):
		print 'gspToCar: Argument "into" must be a string. Try again!'
		return
	
	if into == 'car':
		# Global spherical to global cartesian
		xOut = Z * cos( radians(X) ) * cos( radians(lon) )
		yOut = Z * cos( radians(X) ) * sin( radians(lon) )
		zOut = Z * sin( radians(X) )
	elif into == 'gsp':
		# Calculate latitude (xOut), longitude (yOut) and distance from center of the Earth (zOut)
		zOut = sqrt( X**2 + Y**2 + Z**2 )
		xOut = asin( Z/zOut )
		yOut = atan2( Y, X )
	else:
		print 'gspToCar: {} is not a valid system. Try again!'.format(into)
		
	return xOut, yOut, zOut


# *************************************************************
def gcarToLcar(X, Y, Z, lat, lon , into='lcar'):
	""" (X, Y, Z) = gcarToLcar(X, Y, Z, lat=0., lon=0. , into='lcar')
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
	X: local cartesian X [km] or global cartesian X [km]
	Y: local cartesian Y [km] or global cartesian Y [km]
	Z: local cartesian Z [km] or global cartesian Z [km]
	lat: latitude [degree] of local cartesian system origin
	lon: longitude [degree] of local cartesian system origin
	into: 'lcar' (local cartesian, default) or 'gcar' (global cartesian) specifies the system to convert into
OUTPUTS
	X: global cartesian X [km] or local cartesian X [km]
	Y: global cartesian Y [km] or local cartesian Y [km]
	Z: global cartesian Z [km] or local cartesian Z [km]
	"""
	from math import radians, degrees, cos, sin
	
	if not isinstance(into, str):
		print 'gcarToLcar: Argument "into" must be a string. Try again!'
		return
	
	if into == 'lcar':
		# First, rotate about global-Z to get local-X pointing eastward
		sx = X * cos( radians(lon + 90.) ) - Y * sin( radians(lon + 90.) )
		sy = X * sin( radians(lon + 90.) ) + Y * cos( radians(lon + 90.) )
		sz = Z
		# Then, rotate about X axis to align Z with upward direction
		xOut = sx
		yOut = sy * cos( radians(90. - lat) ) - sz * sin( radians(90. - lat) )
		zOut = sy * sin( radians(90. - lat) ) + sz * cos( radians(90. - lat) )
	elif into == 'gcar':
		# First rotate about X axis to align Z with Earth rotational axis direction
		sx = sx
		sy = sy * cos( -radians(90. - lat) ) - sz * sin( -radians(90. - lat) )
		sz = sy * sin( -radians(90. - lat) ) + sz * cos( -radians(90. - lat) )
		# Then, rotate about global-Z to get global-X pointing to the prime meridian
		xOut = X * cos( -radians(lon + 90.) ) - Y * sin( -radians(lon + 90.) )
		yOut = X * sin( -radians(lon + 90.) ) + Y * cos( -radians(lon + 90.) )
		zOut = Z
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
	