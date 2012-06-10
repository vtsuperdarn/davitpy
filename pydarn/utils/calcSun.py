# UTILS/calcSun
"""
*******************************
            calcSun
*******************************
This subpackage contains def to calculate sunrise/sunset

This includes the following defs:
	calcTimeJulianCent( jd )
		convert Julian Day to centuries since J2000.0.
	calcGeomMeanLongSun( t )
		calculate the Geometric Mean Longitude of the Sun (in degrees)
	calcGeomMeanAnomalySun( t )
		calculate the Geometric Mean Anomaly of the Sun (in degrees)
	calcEccentricityEarthOrbit( t )
		calculate the eccentricity of earth's orbit (unitless)
	calcSunEqOfCenter( t )
		calculate the equation of center for the sun (in degrees)
	calcSunTrueLong( t )
		calculate the true longitude of the sun (in degrees)
	calcSunTrueAnomaly( t )
		calculate the true anamoly of the sun (in degrees)
	calcSunRadVector( t )
		calculate the distance to the sun in AU (in degrees)
	calcSunApparentLong( t )
		calculate the apparent longitude of the sun (in degrees)
	calcMeanObliquityOfEcliptic( t )
		calculate the mean obliquity of the ecliptic (in degrees)
	calcObliquityCorrection( t )
		calculate the corrected obliquity of the ecliptic (in degrees)
	calcSunRtAscension( t )
		calculate the right ascension of the sun (in degrees)
	calcSunDeclination( t )
		calculate the declination of the sun (in degrees)
	calcEquationOfTime( t )
		calculate the difference between true solar time and mean solar time (output: equation of time in minutes of time)
	calcHourAngleSunrise( lat, solarDec )
		calculate the hour angle of the sun at sunrise for the latitude (in radians)
	calcSolNoon( jd, longitude, timezone, dst )
		calculate time of solar noon the given day at the given location on earth (in minute since 0 UTC)
	calcAzEl( output, t, localtime, latitude, longitude, zone )
		
	calcSunriseSetUTC( rise, JD, latitude, longitude )
		
	getJD( day, month, year )
		
	calcSunriseSet( rise, JD, latitude, longitude, timezone, dst )
		
	calculate_sunset, date, latitude, longitude, timezone=timezone, dst=dst, risetime=risetime, settime=settime, solnoon=solnoon
		

*******************************
"""
import math
import time

def calcTimeJulianCent( jd ):
	# convert Julian Day to centuries since J2000.0.
	T = (jd - 2451545.0)/36525.0
	return T


def calcGeomMeanLongSun( t ):
	# calculate the Geometric Mean Longitude of the Sun (in degrees)
	L0 = 280.46646 + t * ( 36000.76983 + t*0.0003032 )
	while L0 > 360.0:
		L0 -= 360.0
	while L0 < 0.0:
		L0 += 360.0
	return L0 # in degrees


def calcGeomMeanAnomalySun( t ):
	# calculate the Geometric Mean Anomaly of the Sun (in degrees)
	M = 357.52911 + t * ( 35999.05029 - 0.0001537 * t)
	return M # in degrees


def calcEccentricityEarthOrbit( t ):
	# calculate the eccentricity of earth's orbit (unitless)
	e = 0.016708634 - t * ( 0.000042037 + 0.0000001267 * t)
	return e # unitless


def calcSunEqOfCenter( t ):
	# calculate the equation of center for the sun (in degrees)
	mrad = math.radians(calcGeomMeanAnomalySun(t))
	sinm = sin(mrad)
	sin2m = sin(mrad+mrad)
	sin3m = sin(mrad+mrad+mrad)
	C = sinm * (1.914602 - t * (0.004817 + 0.000014 * t)) + sin2m * (0.019993 - 0.000101 * t) + sin3m * 0.000289
	return C # in degrees


def calcSunTrueLong( t ):
	# calculate the true longitude of the sun (in degrees)
	l0 = calcGeomMeanLongSun(t)
	c = calcSunEqOfCenter(t)
	O = l0 + c
	return O # in degrees


def calcSunTrueAnomaly( t ):
	# calculate the true anamoly of the sun (in degrees)
	m = calcGeomMeanAnomalySun(t)
	c = calcSunEqOfCenter(t)
	v = m + c
	return v # in degrees


def calcSunRadVector( t ):
	# calculate the distance to the sun in AU (in degrees)
	v = calcSunTrueAnomaly(t)
	e = calcEccentricityEarthOrbit(t)
	R = (1.000001018 * (1. - e * e)) / ( 1. + e * cos( math.radians(v) ) )
	return R # n AUs


def calcSunApparentLong( t ):
	# calculate the apparent longitude of the sun (in degrees)
	o = calcSunTrueLong(t)
	omega = 125.04 - 1934.136 * t
	SunLong = o - 0.00569 - 0.00478 * sin(math.radians(omega))
	return SunLong # in degrees


def calcMeanObliquityOfEcliptic( t ):
	# calculate the mean obliquity of the ecliptic (in degrees)
	seconds = 21.448 - t*(46.8150 + t*(0.00059 - t*(0.001813)))
	e0 = 23.0 + (26.0 + (seconds/60.0))/60.0
	return e0 # in degrees


def calcObliquityCorrection( t ):
	# calculate the corrected obliquity of the ecliptic (in degrees)
	e0 = calcMeanObliquityOfEcliptic(t)
	omega = 125.04 - 1934.136 * t
	e = e0 + 0.00256 * cos(math.radians(omega))
	return e # in degrees


def calcSunRtAscension( t ):
	# calculate the right ascension of the sun (in degrees)
	e = calcObliquityCorrection(t)
	SunLong = calcSunApparentLong(t)
	tananum = ( cos(math.radians(e)) * sin(math.radians(SunLong)) )
	tanadenom = cos(math.radians(SunLong))
	alpha = math.degrees(atan(tananum, tanadenom))
	return alpha # in degrees


def calcSunDeclination( t ):
	# calculate the declination of the sun (in degrees)
	e = calcObliquityCorrection(t)
	SunLong = calcSunApparentLong(t)
	sint = sin(math.radians(e)) * sin(math.radians(SunLong))
	theta = math.degrees(asin(sint))
	return theta # in degrees


def calcEquationOfTime( t ):
	# calculate the difference between true solar time and mean solar time (output: equation of time in minutes of time)	
	epsilon = calcObliquityCorrection(t)
	l0 = calcGeomMeanLongSun(t)
	e = calcEccentricityEarthOrbit(t)
	m = calcGeomMeanAnomalySun(t)
	y = tan(math.radians(epsilon/2.0))
	y *= y

	sin2l0 = sin(math.radians(2.0 * l0))
	sinm   = sin(math.radians(m))
	cos2l0 = cos(math.radians(2.0 * l0))
	sin4l0 = sin(math.radians(4.0 * l0))
	sin2m  = sin(math.radians(2.0 * m))

	Etime = y * sin2l0 - 2.0 * e * sinm + 4.0 * e * y * sinm * cos2l0 - 0.5 * y * y * sin4l0 - 1.25 * e * e * sin2m
	return math.degrees(Etime*4.0) # in minutes of time


def calcHourAngleSunrise( lat, solarDec ):
	# calculate the hour angle of the sun at sunrise for the latitude (in radians)
	latRad = math.radians(lat)
	sdRad  = math.radians(solarDec)
	HAarg = cos(math.radians(90.833)) / ( cos(latRad)*cos(sdRad) ) - tan(latRad) * tan(sdRad)
	HA = acos(HAarg);
	return HA # in radians (for sunset, use -HA)


def calcSolNoon( jd, longitude, timezone, dst ):
	# calculate time of solar noon the given day at the given location on earth (in minute since 0 UTC)
	tnoon = calcTimeJulianCent(jd - longitude/360.0)
	eqTime = calcEquationOfTime(tnoon)
	solNoonOffset = 720.0 - (longitude * 4.) - eqTime # in minutes
	newt = calcTimeJulianCent(jd + solNoonOffset/1440.0)
	eqTime = calcEquationOfTime(newt)
	solNoonLocal = 720.0 - (longitude * 4.) - eqTime + (timezone*60.0) # in minutes
	if dst: 
		solNoonLocal += 60.0
	return solNoonLocal


def calcAzEl( output, t, localtime, latitude, longitude, zone ):
	# 
	eqTime = calcEquationOfTime(t)
	theta  = calcSunDeclination(t)

	solarTimeFix = eqTime + 4.0 * longitude - 60.0 * zone
	earthRadVec = calcSunRadVector(t)

	trueSolarTime = localtime + solarTimeFix
	while trueSolarTime > 1440:
		trueSolarTime -= 1440.

	hourAngle = trueSolarTime / 4.0 - 180.0
	if hourAngle < -180.: 
		hourAngle += 360.0

	haRad = math.radians(hourAngle)
	csz = sin(math.radians(latitude)) * sin(math.radians(theta)) + cos(math.radians(latitude)) * cos(math.radians(theta)) * cos(haRad)
	if csz > 1.0: 
		csz = 1.0 
	elif csz < -1.0: 
		csz = -1.0
	zenith = math.degrees(acos(csz))
	azDenom = cos(math.radians(latitude)) * sin(math.radians(zenith))
	if abs(azDenom) > 0.001: 
		azRad = (( sin(math.radians(latitude)) * cos(math.radians(zenith)) ) - sin(math.radians(theta))) / azDenom
		if abs(azRad) > 1.0: 
			if azRad < 0.: 
				azRad = -1.0 
			else:
				azRad = 1.0
		
		azimuth = 180.0 - math.degrees(acos(azRad))
		if hourAngle > 0.0: 
			azimuth = -azimuth
	else:
		if latitude > 0.0: 
			azimuth = 180.0 
		else:
			azimuth = 0.0
	endelse
	if azimuth < 0.0: 
		azimuth += 360.0
	exoatmElevation = 90.0 - zenith

	# Atmospheric Refraction correction
	if exoatmElevation > 85.0: 
		refractionCorrection = 0.0
	else:
		te = tan(math.radians(exoatmElevation))
		if exoatmElevation > 5.0: 
			refractionCorrection = 58.1 / te - 0.07 / (te*te*te) + 0.000086 / (te*te*te*te*te) 
		elif exoatmElevation > -0.575: 
			refractionCorrection = 1735.0 + exoatmElevation * (-518.2 + exoatmElevation * (103.4 + exoatmElevation * (-12.79 + exoatmElevation * 0.711) ) ) 
		else:
			refractionCorrection = -20.774 / te
		refractionCorrection = refractionCorrection / 3600.0

	solarZen = zenith - refractionCorrection
	output = solarZen
	
	return azimuth


def calcSunriseSetUTC( rise, JD, latitude, longitude ):
	# 
	t = calcTimeJulianCent(JD)
	eqTime = calcEquationOfTime(t)
	solarDec = calcSunDeclination(t)
	hourAngle = calcHourAngleSunrise(latitude, solarDec)
	if ~rise: 
		hourAngle = -hourAngle
	delta = longitude + math.degrees(hourAngle)
	timeUTC = 720. - (4.0 * delta) - eqTime # in minutes
	return timeUTC


def getJD( day, month, year ):
	# 
	if month < 2: 
		year -= 1
		month += 12
	
	A = floor(year/100.)
	B = 2. - A + floor(A/4.)
	JD = floor(365.25*(year + 4716.)) + floor(30.6001*(month+1)) + day + B - 1524.5
	return JD


def calcSunriseSet( rise, JD, latitude, longitude, timezone, dst ):
	# 
	# rise = 1 for sunrise, 0 for sunset
	timeUTC    = calcSunriseSetUTC(rise, JD, latitude, longitude)
	newTimeUTC = calcSunriseSetUTC(rise, JD + timeUTC/1440.0, latitude, longitude)
	timeLocal = newTimeUTC + (timezone * 60.0)
	riseT = calcTimeJulianCent(JD + newTimeUTC/1440.0)
	riseAz = calcAzEl(0, riseT, timeLocal, latitude, longitude, timezone)
	timeLocal += 60.0 if dst else 0.0
	if timeLocal >= 0.0 and timeLocal < 1440.0: 
		return timeLocal 
	else:
		jday = JD
		increment = 1. if timeLocal < 0. else -1.
		while timeLocal < 0.0 or timeLocal >= 1440.0:
			timeLocal += increment * 1440.0
			jday -= increment
		return timeLocal
	
	return
		

def calculate_sunset( date, latitude, longitude, timezone=0., dst=0):

	if n_elements(timezone) == 0: 
		timezone = 0.
	tz = double(timezone)

	dst = keyword_set(dst)

	if n_elements(date) == 0: 
		print 'Must give date.'
		return

	parse_date, date, year, month, day
	jday = getJD(day, month, year)
	# calculate local sunrise time
	rise = calcSunriseSet(1, jday, latitude, longitude, tz, dst)
	set = calcSunriseSet(0, jday, latitude, longitude, tz, dst)
	noon = calcSolNoon(jday, longitude, tz, dst)

	risetime = long(rise/60.)*100 + round(rise % 60L)
	settime =  long(set/60.)*100 + round(set % 60L)
	solnoon = long(noon/60.)*100 + round(noon % 60L)
	
	return

