# UTILS/geoPack
"""
*******************************
		geoPack
*******************************
This module contains the following functions
	geodToGeoc
		converts from geodetic to geocentric
	geodToGeocAzEl
		converts azimuth and elevation from geodetic to geocentric

Based on J.M. Ruohoniemi's geopack
Created by Sebastien
*******************************
"""

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
		latOut = degrees( atan( b**2/a**2 * tan( radians(lat) ) ) )
		lonOut = lon
		Re = a / sqrt( 1. + e2 * sin( radians(latOut) )**2 )
	elif into == 'geod':
		latOut = degrees( atan( a**2/b**2 * tan( radians(lat) ) ) )
		lonOut = lon
		Re = a / sqrt( 1. + e2 * sin( radians(lat) )**2 )
	else:
		print 'geodToGeoc: {} is not a valid system. Try again!'.format(into)
		return
		
	return latOut, lonOut, Re


def geodToGeocAzEl(lat,lon,az,el,into='geoc'):
	""" (az,el) = geodToGeocAzEl(lat,lon,az,el,into='geoc')
Converts pointing azimuth and elevation measured with respect to the local horizon 
to azimuth and elevation with respect to the horizon defined by the plane perpendicular 
to the Earth-centered radial vector drawn through a user defined point.

INPUTS:
	lat: latitude [degree]
	lon: longitude [degree]
	az: azimuth [degree]
	el: elevation [degree]
	into: 'geoc' (default) or 'geod' specifies the system to convert into
OUTPUTS
	az: azimuth [degree]
	el: elevation [degree]
	"""
	from math import degrees, radians, cos, sin, tan, atan, atan2, sqrt
	
	if not isinstance(into, str):
		print 'geodToGeoc: Argument "into" must be a string. Try again!'
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