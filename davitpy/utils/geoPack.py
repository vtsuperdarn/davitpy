# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""geoPack module

Functions
---------
geodToGeoc          converts from geodetic to geocentric (and vice-versa)
geodToGeocAzEl      converts azimuth and elevation from geodetic to geocentric (and vice-versa)
gspToGcar           converts global spherical coordinates to global cartesian coordinates (and vice-versa)
gcarToLcar          converts from global cartesian coordinates to local cartesian coordinates (and vice-versa)
lspToLcar           converts from local spherical coordinates to local cartesian coordinates (and vice-versa)
calcDistPnt         calculates the coordines|distance,elevation,azimuth of a point given a point of origin and 
        distance,elevation,azimuth|distant point coordinates
greatCircleMove     Calculates the coordinates of an end point along a great circle path 
        given the original coordinates, distance, azimuth, and altitude.
greatCircleAzm      Calculates the azimuth from the coordinates of a start point to and end point
        along a great circle path.
greatCircleDist     Calculates the distance in radians along a great circle path between two points.

References
----------
Based on J.M. Ruohoniemi's geopack
Based on R.J. Barnes radar.pro

"""
import logging


def geodToGeoc(lat,lon,inverse=False):
    """Converts position from geodetic to geocentric and vice-versa.
    Based on the IAU 1964 oblate spheroid model of the Earth.

    Parameters
    ----------
    lat : float
        latitude [degree]
    lon : float
        longitude [degree]
    inverse : Optional[bool]
        inverse conversion.  Default is false.

    Returns
    -------
    lat : float
        latitude [degree]
    lon : float
        longitude [degree]
    Re : float
        Earth radius [km]

    """
    import numpy as np
    
    a = 6378.16
    f = 1./298.25
    b = a*(1.-f)
    e2 = (a**2/b**2) - 1.
    
    if not inverse:
        # geodetic into geocentric
        latOut = np.degrees( np.arctan( b**2/a**2 * np.tan( np.radians(lat) ) ) )
        lonOut = lon
        Re = a / np.sqrt( 1. + e2 * np.sin( np.radians(latOut) )**2 )
    else:
        # geocentric into geodetic
        latOut = np.degrees( np.arctan( a**2/b**2 * np.tan( np.radians(lat) ) ) )
        lonOut = lon
        Re = a / np.sqrt( 1. + e2 * np.sin( np.radians(lat) )**2 )
        
    return latOut, lonOut, Re


def geodToGeocAzEl(lat,lon,az,el,inverse=False):
    """Converts pointing azimuth and elevation measured with respect to the local horizon 
    to azimuth and elevation with respect to the horizon defined by the plane perpendicular 
    to the Earth-centered radial vector drawn through a user defined point.

    Parameters
    ----------
    lat : float
        latitude [degree]
    lon : float
        longitude [degree]
    az : float
        azimuth [degree, N]
    el : float
        elevation [degree]
    inverse : Optional[bool]
        inverse conversion

    Returns
    -------
    lat : float
        latitude [degree]
    lon : float
        longitude [degree]
    Re : float
        Earth radius [km]
    az : float
        azimuth [degree, N]
    el : float
        elevation [degree]

    """
    from numpy import degrees, radians, cos, sin, tan, arctan, arctan2, sqrt
    
    taz = radians(az)
    tel = radians(el)
    
    # In this transformation x is east, y is north and z is up
    if not inverse:
        # Calculate deviation from vertical (in radians)
        (geocLat, geocLon, Re) = geodToGeoc(lat, lon)
        devH = radians(lat - geocLat)
        # Calculate cartesian coordinated in local system
        kxGD = cos( tel ) * sin( taz )
        kyGD = cos( tel ) * cos( taz )
        kzGD = sin( tel )
        # Now rotate system about the x axis to align local vertical vector with Earth radial vector
        kxGC = kxGD
        kyGC = kyGD * cos( devH ) + kzGD * sin( devH )
        kzGC = -kyGD * sin( devH ) + kzGD * cos( devH )
        # Finally calculate the new azimuth and elevation in the geocentric frame
        azOut = degrees( arctan2( kxGC, kyGC ) )
        elOut = degrees( arctan( kzGC / sqrt( kxGC**2 + kyGC**2 ) ) )
        latOut = geocLat
        lonOut = geocLon
    else:
        # Calculate deviation from vertical (in radians)
        (geodLat, geodLon, Re) = geodToGeoc(lat, lon, inverse=True)
        devH = radians(geodLat - lat)
        # Calculate cartesian coordinated in geocentric system
        kxGC = cos( tel ) * sin( taz )
        kyGC = cos( tel ) * cos( taz )
        kzGC = sin( tel )
        # Now rotate system about the x axis to align local vertical vector with Earth radial vector
        kxGD = kxGC
        kyGD = kyGC * cos( -devH ) + kzGC * sin( -devH )
        kzGD = -kyGC * sin( -devH ) + kzGC * cos( -devH )
        # Finally calculate the new azimuth and elevation in the geocentric frame
        azOut = degrees( arctan2( kxGD, kyGD ) )
        elOut = degrees( arctan( kzGD / sqrt( kxGD**2 + kyGD**2 ) ) )
        latOut = geodLat
        lonOut = geodLon
    
    return latOut, lonOut, Re, azOut, elOut


def gspToGcar(X, Y, Z, inverse=False):
    """Converts a position from global spherical (geocentric) to global cartesian (and vice-versa).
    The global cartesian coordinate system is defined as:
        - origin: center of the Earth
        - X axis in the equatorial plane and through the prime meridian.
        - Z axis in the direction of the rotational axis and through the North pole
    The meaning of the input (X,Y,Z) depends on the direction of the conversion 
    (to global cartesian or to global spherical).

    Parameters
    ----------
    X : float
        latitude [degree] or global cartesian X [km]
    Y : float
        longitude [degree] or global cartesian Y [km]
    Z : float
        distance from center of the Earth [km] or global cartesian Z [km]
    inverse : Optional[bool]
        inverse conversion

    Returns
    -------
    X : float
        global cartesian X [km] or latitude [degree]
    Y : float
        global cartesian Y [km] or longitude [degree]
    Z : float
        global cartesian Z [km] or distance from center of the Earth [km]

    """
    from numpy import radians, degrees, cos, sin, arcsin, arctan2, sqrt
    
    if not inverse:
        # Global spherical to global cartesian
        xOut = Z * cos( radians(X) ) * cos( radians(Y) )
        yOut = Z * cos( radians(X) ) * sin( radians(Y) )
        zOut = Z * sin( radians(X) )
    else:
        # Calculate latitude (xOut), longitude (yOut) and distance from center of the Earth (zOut)
        zOut = sqrt( X**2 + Y**2 + Z**2 )
        xOut = degrees( arcsin( Z/zOut ) )
        yOut = degrees( arctan2( Y, X ) )
        
    return xOut, yOut, zOut


def gcarToLcar(X, Y, Z, lat, lon, rho , inverse=False):
    """Converts a position from global cartesian to local cartesian (and vice-versa).
    The global cartesian coordinate system is defined as:
        - origin: center of the Earth
        - Z axis in the direction of the rotational axis and through the North pole
        - X axis in the equatorial plane and through the prime meridian.
    The local cartesian coordinate system is defined as:
        - origin: local position
        - X: East
        - Y: North
        - Z: up
    The meaning of the input (X,Y,Z) depends on the direction of the conversion 
    (to global cartesian or to global spherical).

    Parameters
    ----------
    X : float
        global cartesian X [km] or local cartesian X [km]
    Y : flaot
        global cartesian Y [km] or local cartesian Y [km]
    Z : float
        global cartesian Z [km] or local cartesian Z [km]
    lat : float
        geocentric latitude [degree] of local cartesian system origin
    lon : float
        geocentric longitude [degree] of local cartesian system origin
    rho : float
        distance from center of the Earth [km] of local cartesian system origin
    inverse : Optional[bool]
        inverse conversion

    Returns
    -------
    X : float
        local cartesian X [km] or global cartesian X [km]
    Y : float
        local cartesian Y [km] or global cartesian Y [km]
    Z : float
        local cartesian Z [km] or global cartesian Z [km]

    """
    from numpy import radians, degrees, cos, sin
    
    # First get global cartesian coordinates of local origin
    (goX, goY, goZ) = gspToGcar(lat, lon, rho)
    
    if not inverse:
        # Translate global position to local origin
        tx = X - goX
        ty = Y - goY
        tz = Z - goZ
        # Then, rotate about global-Z to get local-X pointing eastward
        rot = -radians(lon + 90.)
        sx = tx * cos( rot ) - ty * sin( rot )
        sy = tx * sin( rot ) + ty * cos( rot )
        sz = tz
        # Finally, rotate about X axis to align Z with upward direction
        rot = -radians(90. - lat)
        xOut = sx
        yOut = sy * cos( rot ) - sz * sin( rot )
        zOut = sy * sin( rot ) + sz * cos( rot )
    else:
        # First rotate about X axis to align Z with Earth rotational axis direction
        rot = radians(90. - lat)
        sx = X
        sy = Y * cos( rot ) - Z * sin( rot )
        sz = Y * sin( rot ) + Z * cos( rot )
        # Then, rotate about global-Z to get global-X pointing to the prime meridian
        rot = radians(lon + 90.)
        xOut = sx * cos( rot ) - sy * sin( rot )
        yOut = sx * sin( rot ) + sy * cos( rot )
        zOut = sz
        # Finally, translate local position to global origin
        xOut = xOut + goX
        yOut = yOut + goY
        zOut = zOut + goZ
    
    return xOut, yOut, zOut


def lspToLcar(X, Y, Z, inverse=False):
    """Converts a position from local spherical to local cartesian (and vice-versa).
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
    The meaning of the input (X,Y,Z) depends on the direction of the conversion 
    (to global cartesian or to global spherical).

    Parameters
    ----------
    X : float
        azimuth [degree, N] or local cartesian X [km]
    Y : float
        elevation [degree] or local cartesian Y [km]
    Z : float
        distance origin [km] or local cartesian Z [km]
    inverse : Optional[bool]
        inverse conversion

    Returns
    -------
    X : float
        local cartesian X [km] or azimuth [degree, N]
    Y : float
        local cartesian Y [km] or elevation [degree]
    Z : float
        local cartesian Z [km] or distance from origin [km]

    """
    from numpy import radians, degrees, cos, sin, arcsin, arctan2, sqrt
    
    if not inverse:
        # local spherical into local cartesian
        r = Z
        el = Y
        az = X
        xOut = r * cos( radians(el) ) * sin( radians(az) )
        yOut = r * cos( radians(el) ) * cos( radians(az) )
        zOut = r * sin( radians(el) )
    else:
        # local cartesian into local spherical
        r = sqrt( X**2 + Y**2 + Z**2 )
        el = degrees( arcsin(Z/r) )
        az = degrees( arctan2(X, Y) )
        xOut = az
        yOut = el
        zOut = r
    
    return xOut, yOut, zOut


# *************************************************************
def calcDistPnt(origLat, origLon, origAlt, \
            dist=None, el=None, az=None, \
            distLat=None, distLon=None, distAlt=None):
    """Calculate: 
        - the coordinates and altitude of a distant point given a point of origin, distance, azimuth and elevation, or 
        - the coordinates and distance of a distant point given a point of origin, altitude, azimuth and elevation, or 
        - the distance, azimuth and elevation between a point of origin and a distant point or 
        - the distance, azimuth between a point of origin and a distant point and the altitude of said distant point given 
        a point of origin, distant point and elevation angle.
    Input/output is in geodetic coordinates, distances are in km and angles in degrees.

    Parameters
    ----------
    origLat : float
        geographic latitude of point of origin [degree]
    origLon : float
        geographic longitude of point of origin [degree]
    origAlt : float
        altitude of point of origin [km]
    dist : Optional[float]
        distance to point [km]
    el : Optional[float]
        azimuth [degree]
    az : Optional[float]
        elevation [degree]
    distLat : Optional[float]
        latitude [degree] of distant point
    distLon : Optional[float]
        longitude [degree] of distant point
    distAlt : Optional[float]
        altitide [km] of distant point

    Returns
    -------
    dict : dict
        a dictionary containing all the information about origin and distant points and their relative positions

    """
    from math import sqrt, pi
    import numpy
    
    # If all the input parameters (keywords) are set to 0, show a warning, and default to fint distance/azimuth/elevation
    if dist is None and el is None and az is None:
        assert None not in [distLat, distLon, distAlt], logging.error('Not enough keywords.')

        # Convert point of origin from geodetic to geocentric
        (gcLat, gcLon, origRe) = geodToGeoc(origLat, origLon)
        # Convert distant point from geodetic to geocentric
        (gcDistLat, gcDistLon, distRe) = geodToGeoc(distLat, distLon)
        # convert distant point from geocentric to global cartesian
        (pX, pY, pZ) = gspToGcar(gcDistLat, gcDistLon, distRe+distAlt)
        # convert pointing direction from global cartesian to local cartesian
        (dX, dY, dZ) = gcarToLcar(pX, pY, pZ, gcLat, gcLon, origRe+origAlt)
        # convert pointing direction from local cartesian to local spherical
        (gaz, gel, rho) = lspToLcar(dX, dY, dZ, inverse=True)
        # convert pointing azimuth and elevation to geodetic
        (lat, lon, Re, az, el) = geodToGeocAzEl(gcLat, gcLon, gaz, gel, inverse=True)
        dist = sqrt( dX**2 + dY**2 + dZ**2 )

    elif distLat is None and distLon is None and distAlt is None:
        assert None not in [dist, el, az], logging.error('Not enough keywords.')

        # convert pointing azimuth and elevation to geocentric
        (gcLat, gcLon, origRe, gaz, gel) = geodToGeocAzEl(origLat, origLon, az, el)
        # convert pointing direction from local spherical to local cartesian
        (pX, pY, pZ) = lspToLcar(gaz, gel, dist)
        # convert pointing direction from local cartesian to global cartesian
        (dX, dY, dZ) = gcarToLcar(pX, pY, pZ, gcLat, gcLon, origRe+origAlt, inverse=True)
        # Convert distant point from global cartesian to geocentric
        (gcDistLat, gcDistLon, rho) = gspToGcar(dX, dY, dZ, inverse=True)
        # Convert distant point from geocentric to geodetic
        (distLat, distLon, Re) = geodToGeoc(gcDistLat, gcDistLon, inverse=True)
        distAlt = rho - Re
        distRe = Re

    elif dist is None and distAlt is None and az is None:
        assert None not in [distLat, distLon, el], logging.error('Not enough keywords.')

        # Convert point of origin from geodetic to geocentric
        (gcLat, gcLon, origRe) = geodToGeoc(origLat, origLon)
        Dref = origRe + origAlt
        # convert point of origin from geocentric to global cartesian
        (pX, pY, pZ) = gspToGcar(gcLat, gcLon, Dref)
        # Convert distant point from geodetic to geocentric
        (gcDistLat, gcDistLon, distRe) = geodToGeoc(distLat, distLon)
        # convert distant point from geocentric to global cartesian
        (pdX, pdY, pdZ) = gspToGcar(gcDistLat, gcDistLon, Dref)
        # convert pointing direction from global cartesian to local cartesian
        (dX, dY, dZ) = gcarToLcar(pdX, pdY, pdZ, gcLat, gcLon, Dref)
        # convert pointing direction from local cartesian to local spherical
        (gaz, gel, rho) = lspToLcar(dX, dY, dZ, inverse=True)
        # convert pointing azimuth and elevation to geodetic
        (lat, lon, Re, az, _) = geodToGeocAzEl(gcLat, gcLon, gaz, gel, inverse=True)
        # convert pointing azimuth and elevation to geocentric
        (gcLat, gcLon, origRe, gaz, gel) = geodToGeocAzEl(origLat, origLon, az, el)
        # calculate altitude and distance
        theta = numpy.arccos( (pdX*pX + pdY*pY + pdZ*pZ)/Dref**2 )
        distAlt = Dref*( numpy.cos(numpy.radians(gel))/numpy.cos(theta+numpy.radians(gel)) - 1. )
        distAlt -= distRe - origRe
        dist = Dref*numpy.sin(theta)/numpy.cos(theta+numpy.radians(gel))

    elif distLat is None and distLon is None and dist is None:
        assert None not in [distAlt, el, az], logging.error('Not enough keywords.')

        # convert pointing azimuth and elevation to geocentric
        (gcLat, gcLon, origRe, gaz, gel) = geodToGeocAzEl(origLat, origLon, az, el)
        # Calculate angles
        alpha = numpy.arcsin( (origRe+origAlt)*numpy.cos(numpy.radians(gel))/(origRe+distAlt) )
        theta = pi/2. - alpha - numpy.radians(gel)
        # calculate distance
        dist = numpy.sqrt( (origRe+origAlt)**2 + (origRe+distAlt)**2 -
                            2.*(origRe+distAlt)*(origRe+origAlt)*numpy.cos(theta) )
        # convert pointing direction from local spherical to local cartesian
        (pX, pY, pZ) = lspToLcar(gaz, gel, dist)
        # convert pointing direction from local cartesian to global cartesian
        (dX, dY, dZ) = gcarToLcar(pX, pY, pZ, gcLat, gcLon, origRe+origAlt, inverse=True)
        # Convert distant point from global cartesian to geocentric
        (gcDistLat, gcDistLon, rho) = gspToGcar(dX, dY, dZ, inverse=True)
        # Convert distant point from geocentric to geodetic
        (distLat, distLon, distRe) = geodToGeoc(gcDistLat, gcDistLon, inverse=True)
        distAlt = rho - distRe

    else:
        return
    
    # Fill output dictionary
    dictOut = {'origLat': origLat, 'origLon': origLon, 'origAlt': origAlt, \
                'distLat': distLat, 'distLon': distLon, 'distAlt': distAlt, \
                'az': az, 'el': el, 'dist': dist, 'origRe': origRe, 'distRe': distRe}
    
    return dictOut


def greatCircleMove(origLat, origLon, dist, az, alt=0,Re=6371.):
    """Calculates the coordinates of an end point along a great circle path 
    given the original coordinates, distance, azimuth, and altitude.

    Parameters
    ----------
    origLat : float
        latitude [degree]
    origLon : float
        longitude [degree]
    dist : float
        distance [km]
    az : float
        azimuth [deg]
    alt : Optional[float]
        altitude [km] (added to default Re = 6378.1 km)
    Re : Optional[float]
        Earth radius, default 6371.

    Returns
    -------
    list : list
        latitude, longitude in deg

    """
    import numpy
    
    Re_tot = (Re + alt) * 1e3
    dist = dist * 1e3
    lat1 = numpy.radians(origLat) 
    lon1 = numpy.radians(origLon)
    az = numpy.radians(az)
    
    lat2 = numpy.arcsin(numpy.sin(lat1)*numpy.cos(dist/Re_tot) +\
    numpy.cos(lat1)*numpy.sin(dist/Re_tot)*numpy.cos(az))
    lon2 = lon1 + numpy.arctan2(numpy.sin(az)*numpy.sin(dist/Re_tot)*numpy.cos(lat1),\
    numpy.cos(dist/Re_tot)-numpy.sin(lat1)*numpy.sin(lat2))

    # Convert everything to numpy arrays to make selective processing easier.
    ret_lat = numpy.degrees(lat2)
    ret_lon = numpy.degrees(lon2)
    
    ret_lat = numpy.array(ret_lat)
    if ret_lat.shape == ():
        ret_lat.shape = (1,)

    ret_lon = numpy.array(ret_lon)
    if ret_lon.shape == ():
        ret_lon.shape = (1,)

    # Put all longitudes on -180 to 180 domain.
    ret_lon = ret_lon % 360. 

    tf = ret_lon > 180.
    ret_lon[tf] = ret_lon[tf] - 360.

    return (ret_lat,ret_lon)


def greatCircleAzm(lat1,lon1,lat2,lon2):
    """Calculates the azimuth from the coordinates of a start point to and end point
    along a great circle path.

    Parameters
    ----------
    lat1 : float
        latitude [deg]
    lon1 : float
        longitude [deg]
    lat2 : float
        latitude [deg]
    lon2 : float
        longitude [deg]

    Returns
    -------
    azm : float
        azimuth [deg]

    """
    from numpy import sin, cos, arctan2, degrees, radians
    lat1,lon1,lat2,lon2 = radians(lat1),radians(lon1),radians(lat2),radians(lon2)
    dlon  = lon2-lon1
    y     = sin(dlon)*cos(lat2)
    x     = cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(dlon)
    azm   = degrees(arctan2(y,x))

    return azm


def greatCircleDist(lat1,lon1,lat2,lon2):
    """Calculates the distance in radians along a great circle path between two points.

    Parameters
    ----------
    lat1 : float
        latitude [deg]
    lon1 : float
        longitude [deg]
    lat2 : float
        latitude [deg]
    lon2 : float
        longitude [deg]

    Returns
    -------
    radDist : float
        distance [radians]

    """
    from numpy import cos, sin, arctan2, radians, sqrt

    lat1,lon1,lat2,lon2 = radians(lat1),radians(lon1),radians(lat2),radians(lon2)

    dlat = lat2-lat1
    dlon = lon2-lon1
    a    = sin(dlat/2.)*sin(dlat/2.)+cos(lat1)*cos(lat2)*sin(dlon/2.)*sin(dlon/2.)
    radDist = 2.*arctan2(sqrt(a),sqrt(1.-a))

    return radDist
