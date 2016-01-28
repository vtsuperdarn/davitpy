# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
Module
------
pydarn.radar.radFov
    This module handles generating field-of-view projctions

Classes
-------
pydarn.radar.radFov.fov
    field of view position

Functions
---------
pydarn.radar.radFov.slantRange
    Calculate slant range
pydarn.radar.radFov.calcAzOffBore
    Calculate off-array-normal azimuth
pydarn.radar.radFov.calcFieldPnt
    Calculate field point projection

References
----------
Based on Mike Ruohoniemi's GEOPACK
Based on R.J. Barnes radar.pro

"""
import numpy as np
import logging

class fov(object):
    """ This class calculates and stores field-of-view coordinates.
    Provide the input-set [nbeams, ngates, bmsep, recrise] or a SITE object.
    Parameters from the input-set will always take precedence over parameters
    from the SITE object.  Make sure to provide frang and rsep, the default
    values are not always applicable. The full projection gives the coordinates
    at each corner of each gate, in the following order: looking in the beam
    direction, lower-left, lower-right, upper-right, upper-left.

    Parameters
    ----------
    site : Optional[site object]
        site structure for a given radar and date-time
    frang : scalar or ndarray(nbeams)
        first range gate position [km] (defaults to 180 km)
    rsep : scalar or ndarray(nbeams)
        range gate separation [km] (defaults to 45 km)
    nbeams : Optional[int]
        number of beams (use site information if not provided)
    ngates : Optional[int]
        number of gates (use site information if not provided)
    bmsep : Optional[float]
        beam separation [degree] (use site information if not provided)
    siteLat : Optional[float]
        geographic latitude of radar [degree] (use site information if not
        provided)
    siteLon : Optional[float]
        geographic longitude of radar [degree] (use site information if not
        provided)
    siteAlt : Optional[float]
        altitude of radar site [m] (use site information if not provided)
    siteBore : Optional[float]
        radar boresite [degree] (use site information if not provided)
    recrise : Optional[scalar or ndarray(nbeams)]
        receiver rise time [us] (use site information if not provided)
    elevation : Optional[scalar or ndarray(ngates) or ndarray(nbeams,ngates)]
        elevation angle [degree] (if not provided, is evaluated using 'model')
    altitude : scalar or ndarray(ngates) or ndarray(nbeams,ngates)
        altitude [km] (if not provided, set to 300 km)
    model
        IS : for ionopsheric scatter projection model (default)
        GS : for ground scatter projection model
        None : if you trust your elevation or altitude values. more to come
    coords
        anything accepted by coord_conv; see utils.get_coord_dict. Default: geo
    date_time : Optional[datetime.datetime object]
        the datetime for which the FOV is desired. Required for mag and mlt,
        and possibly others in the future. Default: None
    coord_alt
        like altitude, but only used for conversion from geographic to
        other coordinate systems. Default: 0.
    fov_dir : str
        Provide the front or back field of view?  If not specified,
        defaults to 'front'. Use 'front' or 'back'.

    """
    def __init__(self, frang=180.0, rsep=45.0, site=None, nbeams=None,
                 ngates=None, bmsep=None, recrise=None, siteLat=None,
                 siteLon=None, siteBore=None, siteAlt=None, siteYear=None,
                 elevation=None, altitude=300., model='IS', coords='geo',
                 date_time=None, coord_alt=0., fov_dir='front'):
        # Import neccessary functions and classes
        from davitpy.utils.coordUtils import coord_conv

        # Define class constants
        rn = 'fov'

        # Test that we have enough input arguments to work with
        if(not site and None in [nbeams, ngates, bmsep, recrise, siteLat,
                                 siteLon, siteBore, siteAlt, siteYear]):
            estr = '{:s}: must provide either a site object or '.format(rn)
            estr = '{:s}[nbeams, ngates, bmsep, recrise, siteLat,'.format(estr)
            estr = '{:s} siteLon, siteBore, siteAlt, siteYear].'.format(estr)
            logging.error(estr)
            return

        # date_time checking is handled by coord_conv, and it already
        # knows all of the possible coord systems, so no need to do it
        # here.

        # Then assign variables from the site object if necessary
        if site:
            if not nbeams:
                nbeams = site.maxbeam
            if not ngates:
                ngates = site.maxgate
            if not bmsep:
                bmsep = site.bmsep
            if not recrise:
                recrise = site.recrise
            if not siteLat:
                siteLat = site.geolat
            if not siteLon:
                siteLon = site.geolon
            if not siteAlt:
                siteAlt = site.alt
            if not siteBore:
                siteBore = site.boresite
            if not siteYear:
                siteYear = site.tval.year

        # Some type checking is neccessary. If frang, rsep or recrise are
        # arrays, then they should be of shape (nbeams,).  Set a flag if any of
        # frang, rsep or recrise is an array
        is_param_array = False
        if isinstance(frang, np.ndarray):
            is_param_array = True
            # Array is adjusted to add on extra beam edge by copying the last
            # element
            if len(frang) != nbeams:
                estr = "{:s}: frang must be a scalar or numpy ".format(rn)
                estr = "{:s}ndarray of size (nbeams). Using first".format(estr)
                estr = "{:s} element: {}".format(estr, frang[0])
                logging.error(estr)
                frang = frang[0] * np.ones(nbeams + 1)
            else:
                frang = np.append(frang, frang[-1])
        else:
            frang = np.array([frang])
        if isinstance(rsep, np.ndarray):
            is_param_array = True
            # Array is adjusted to add on extra beam edge by copying the last
            # element
            if len(rsep) != nbeams:
                estr = "{:s}: rsep must be a scalar or numpy ndarray".format(
                    rn)
                estr = "{:s} of size (nbeams). Using first element".format(
                    estr)
                estr = "{:s}: {}".format(estr, rsep[0])
                logging.error(estr)
                rsep = rsep[0] * np.ones(nbeams + 1)
            else:
                rsep = np.append(rsep, rsep[-1])
        else:
            rsep = np.array([rsep])
        if isinstance(recrise, np.ndarray):
            is_param_array = True
            # Array is adjusted to add on extra beam edge by copying the last
            # element
            if len(recrise) != nbeams:
                estr = "{:s}: recrise must be a scalar or numpy ".format(rn)
                estr = "{:s}ndarray of size (nbeams). Using first ".format(
                    estr)
                estr = "{:s}element: {}".format(estr, recrise[0])
                logging.error(estr)
                recrise = recrise[0] * np.ones(nbeams + 1)
            else:
                recrise = np.append(recrise, recrise[-1])
        else:
            recrise = np.array([recrise])

        # If altitude or elevation are arrays, then they should be of shape
        # (nbeams, ngates)
        if isinstance(altitude, np.ndarray):
            if altitude.ndim == 1:
                # Array is adjusted to add on extra beam/gate edge by copying
                # the last element and replicating the whole array as many
                # times as beams
                if altitude.size != ngates:
                    estr = '{:s}: altitude must be of a scalar or '.format(rn)
                    estr = '{:s}numpy ndarray of size (ngates) or '.format(
                        estr)
                    estr = '{:s}(nbeans,ngates). Using first '.format(estr)
                    estr = '{:s}element: {}'.format(estr, altitude[0])
                    logging.error(estr)
                    altitude = altitude[0] * np.ones((nbeams + 1, ngates + 1))
                else:
                    altitude = np.resize(np.append(altitude, altitude[-1]),
                                         (nbeams + 1, ngates + 1))
            elif altitude.ndim == 2:
                # Array is adjusted to add on extra beam/gate edge by copying
                # the last row and column
                if altitude.shape != (nbeams, ngates):
                    estr = '{:s}: altitude must be of a scalar or '.format(rn)
                    estr = '{:s}numpy ndarray of size (ngates) or '.format(
                        estr)
                    estr = '{:s}(nbeans,ngates). Using first '.format(estr)
                    estr = '{:s}element: {}'.format(altitude[0])
                    logging.error(estr)
                    altitude = altitude[0] * np.ones((nbeams + 1, ngates + 1))
                else:
                    altitude = np.append(altitude,
                                         altitude[-1, :].reshape(1, ngates),
                                         axis=0)
                    altitude = np.append(altitude,
                                         altitude[:, -1].reshape(nbeams, 1),
                                         axis=1)
            else:
                estr = '{:s}: altitude must be of a scalar or '.format(rn)
                estr = '{:s}numpy ndarray of size (ngates) or '.format(estr)
                estr = '{:s}(nbeans,ngates). Using first element: '.format(
                    estr)
                estr = '{:s}{}'.format(estr, altitude[0])
                logging.error(estr)
                altitude = altitude[0] * np.ones((nbeams + 1, ngates + 1))
        if isinstance(elevation, np.ndarray):
            if elevation.ndim == 1:
                # Array is adjusted to add on extra beam/gate edge by copying
                # the last element and replicating the whole array as many
                # times as beams
                if elevation.size != ngates:
                    estr = '{:s}: elevation must be of a scalar or '.format(rn)
                    estr = '{:s}numpy ndarray of size (ngates) or '.format(
                        estr)
                    estr = '{:s}(nbeans,ngates). Using first '.format(estr)
                    estr = '{:s}element: {}'.format(estr, elevation[0])
                    logging.error(estr)
                    elevation = elevation[0] * \
                        np.ones((nbeams + 1, ngates + 1))
                else:
                    elevation = np.resize(np.append(elevation, elevation[-1]),
                                          (nbeams + 1, ngates + 1))
            elif elevation.ndim == 2:
                # Array is adjusted to add on extra beam/gate edge by copying
                # the last row and column
                if elevation.shape != (nbeams, ngates):
                    estr = '{:s}: elevation must be of a scalar or '.format(rn)
                    estr = '{:s}numpy ndarray of size (ngates) or '.format(
                        estr)
                    estr = '{:s}(nbeans,ngates). Using first '.format(estr)
                    estr = '{:s}element: {}'.format(estr, elevation[0])
                    logging.error(estr)
                    elevation = elevation[0] * \
                        np.ones((nbeams + 1, ngates + 1))
                else:
                    elevation = np.append(elevation,
                                          elevation[-1, :].reshape(1, ngates),
                                          axis=0)
                    elevation = np.append(elevation,
                                          elevation[:, -1].reshape(nbeams, 1),
                                          axis=1)
            else:
                estr = '{:s}: elevation must be a scalar or '.format(rn)
                estr = '{:s}numpy ndarray of size (ngates) or '.format(estr)
                estr = '{:s}(nbeans,ngates). Using first element'.format(estr)
                estr = '{:s}: {}'.format(estr, elevation[0])
                logging.error(estr)
                elevation = elevation[0] * np.ones((nbeams + 1, ngates + 1))

        # Do for coord_alt what we just did for altitude.
        if isinstance(coord_alt, np.ndarray):
            if coord_alt.ndim == 1:
                # Array is adjusted to add on extra beam/gate edge by copying
                # the last element and replicating the whole array as many
                # times as beams
                if coord_alt.size != ngates:
                    estr = '{:s}: coord_alt must be a scalar or '.format(rn)
                    estr = '{:s}numpy ndarray of size (ngates) or '.format(
                        estr)
                    estr = '{:s}(nbeans,ngates). Using first '.format(estr)
                    estr = '{:s}element: {}'.format(estr, coord_alt[0])
                    logging.error(estr)
                    coord_alt = coord_alt[0] * \
                        np.ones((nbeams + 1, ngates + 1))
                else:
                    coord_alt = np.resize(np.append(coord_alt, coord_alt[-1]),
                                          (nbeams + 1, ngates + 1))
            elif coord_alt.ndim == 2:
                # Array is adjusted to add on extra beam/gate edge by copying
                # the last row and column
                if coord_alt.shape != (nbeams, ngates):
                    estr = '{:s}: coord_alt must be a scalar or '.format(estr)
                    estr = '{:s}numpy ndarray of size (ngates) or '.format(
                        estr)
                    estr = '{:s}(nbeans,ngates). Using first '.format(estr)
                    estr = '{:s}element: {}'.format(estr, coord_alt[0])
                    logging.error(estr)
                    coord_alt = coord_alt[0] * \
                        np.ones((nbeams + 1, ngates + 1))
                else:
                    coord_alt = np.append(coord_alt,
                                          coord_alt[-1, :].reshape(1, ngates),
                                          axis=0)
                    coord_alt = np.append(coord_alt,
                                          coord_alt[:, -1].reshape(nbeams, 1),
                                          axis=1)
            else:
                estr = '{:s}: coord_alt must be a scalar or '.format(rn)
                estr = '{:s}numpy ndarray of size (ngates) or '.format(estr)
                estr = '{:s}(nbeans,ngates). Using first element'.format(estr)
                estr = '{:s}: {}'.format(estr, coord_alt[0])
                logging.error(estr)
                coord_alt = coord_alt[0] * np.ones((nbeams + 1, ngates + 1))

        # Generate beam/gate arrays
        beams = np.arange(nbeams + 1)
        gates = np.arange(ngates + 1)

        # Create output arrays
        slant_range_full = np.zeros((nbeams + 1, ngates + 1), dtype='float')
        lat_full = np.zeros((nbeams + 1, ngates + 1), dtype='float')
        lon_full = np.zeros((nbeams + 1, ngates + 1), dtype='float')
        slant_range_center = np.zeros((nbeams + 1, ngates + 1), dtype='float')
        lat_center = np.zeros((nbeams + 1, ngates + 1), dtype='float')
        lon_center = np.zeros((nbeams + 1, ngates + 1), dtype='float')

        # Calculate deviation from boresight for center of beam
        boff_center = bmsep * (beams - (nbeams - 1) / 2.0)
        # Calculate deviation from boresight for edge of beam
        boff_edge = bmsep * (beams - (nbeams - 1) / 2.0 - 0.5)

        # Iterates through beams
        for ib in beams:
            # if none of frang, rsep or recrise are arrays, then only execute
            # this for the first loop, otherwise, repeat for every beam
            if (~is_param_array and ib == 0) or is_param_array:
                # Calculate center slant range
                srang_center = slantRange(frang[ib], rsep[ib], recrise[ib],
                                          gates, center=True)
                # Calculate edges slant range
                srang_edge = slantRange(frang[ib], rsep[ib], recrise[ib], gates,
                                        center=False)
            # Save into output arrays
            slant_range_center[ib, :-1] = srang_center[:-1]
            slant_range_full[ib, :] = srang_edge

            # Calculate coordinates for Edge and Center of the current beam
            for ig in gates:
                # Handle array-or-not question.
                talt = altitude[ib, ig] if isinstance(altitude, np.ndarray) \
                    else altitude
                telv = elevation[ib, ig] if isinstance(elevation, np.ndarray) \
                    else elevation
                t_c_alt = coord_alt[ib, ig] \
                    if isinstance(coord_alt, np.ndarray) else coord_alt

                if model == 'GS':
                    if (~is_param_array and ib == 0) or is_param_array:
                        slant_range_center[ib, ig] = \
                            gsMapSlantRange(srang_center[ig], altitude=None,
                                            elevation=None)
                        slant_range_full[ib, ig] = gsMapSlantRange(srang_edge[ig],
                                                                   altitude=None,
                                                                   elevation=None)
                        srang_center[ig] = slant_range_center[ib, ig]
                        srang_edge[ig] = slant_range_full[ib, ig]

                if (srang_center[ig] != -1) and (srang_edge[ig] != -1):
                    # Then calculate projections
                    latc, lonc = calcFieldPnt(siteLat, siteLon, siteAlt * 1e-3,
                                              siteBore, boff_center[ib],
                                              srang_center[ig], elevation=telv,
                                              altitude=talt, model=model,
                                              fov_dir=fov_dir)
                    late, lone = calcFieldPnt(siteLat, siteLon, siteAlt * 1e-3,
                                              siteBore, boff_edge[ib],
                                              srang_edge[ig], elevation=telv,
                                              altitude=talt, model=model,
                                              fov_dir=fov_dir)
                    if(coords != 'geo'):
                        lonc, latc = coord_conv(lonc, latc, "geo", coords,
                                                altitude=t_c_alt,
                                                date_time=date_time)
                        lone, late = coord_conv(lone, late, "geo", coords,
                                                altitude=t_c_alt,
                                                date_time=date_time)
                else:
                    latc, lonc = np.nan, np.nan
                    late, lone = np.nan, np.nan

                # Save into output arrays
                lat_center[ib, ig] = latc
                lon_center[ib, ig] = lonc
                lat_full[ib, ig] = late
                lon_full[ib, ig] = lone

        # Output is...
        self.latCenter = lat_center[:-1, :-1]
        self.lonCenter = lon_center[:-1, :-1]
        self.slantRCenter = slant_range_center[:-1, :-1]
        self.latFull = lat_full
        self.lonFull = lon_full
        self.slantRFull = slant_range_full
        self.beams = beams[:-1]
        self.gates = gates[:-1]
        self.coords = coords

    # *************************************************************
    def __str__(self):
        outstring = 'latCenter: {} \
                     \nlonCenter: {} \
                     \nlatFull: {} \
                     \nlonFull: {} \
                     \nslantRCenter: {} \
                     \nslantRFull: {} \
                     \nbeams: {} \
                     \ngates: {} \
                     \ncoords: {}'.format(np.shape(self.latCenter),
                                          np.shape(self.lonCenter),
                                          np.shape(self.latFull),
                                          np.shape(self.lonFull),
                                          np.shape(self.slantRCenter),
                                          np.shape(self.slantRFull),
                                          np.shape(self.beams),
                                          np.shape(self.gates), self.coords)
        return outstring


# *************************************************************
# *************************************************************
def calcFieldPnt(tGeoLat, tGeoLon, tAlt, boreSight, boreOffset, slantRange,
                 elevation=None, altitude=None, model=None, coords='geo',
                 fov_dir='front'):
    """Calculate coordinates of field point given the radar coordinates and
    boresight, the pointing direction deviation from boresight and elevation
    angle, and the field point slant range and altitude. Either the elevation
    or the altitude must be provided. If none is provided, the altitude is set
    to 300 km and the elevation evaluated to accomodate altitude and range.

    Parameters
    ----------
    tGeoLat
        transmitter latitude [degree, N]
    tGeoLon
        transmitter longitude [degree, E]
    tAlt
        transmitter altitude [km]
    boreSight
        boresight azimuth [degree, E]
    boreOffset
        offset from boresight [degree]
    slantRange
        slant range [km]
    elevation : Optional[float]
        elevation angle [degree] (estimated if None)
    altitude : Optional[float]
        altitude [km] (default 300 km)
    model : Optional[str]
        IS : for ionopsheric scatter projection model
        GS : for ground scatter projection model
        None : if you trust your elevation or altitude values. more to come
    coords
        'geo' (more to come)
    fov_dir
        'front' (default) or 'back'.  Specifies fov direction

    """
    from math import asin
    from davitpy.utils import Re, geoPack

    # Make sure we have enough input stuff
    # if (not model) and (not elevation or not altitude): model = 'IS'

    # Only geo is implemented.
    assert(coords == "geo"), \
        "Only geographic (geo) is implemented in calcFieldPnt."

    # Now let's get to work
    # Classic Ionospheric/Ground scatter projection model
    if model in ['IS', 'GS']:
        # Make sure you have altitude (even if it isn't used), because these
        # 2 projection models rely on it
        if not elevation and not altitude:
            # Set default altitude to 300 km
            altitude = 300.0
        elif elevation and not altitude:
            # If you have elevation but not altitude, then you calculate
            # altitude, and elevation will be adjusted anyway
            altitude = np.sqrt(Re ** 2 + slantRange ** 2 + 2. * slantRange * Re *
                               np.sin(np.radians(elevation))) - Re

        # Now you should have altitude (and maybe elevation too, but it won't
        # be used in the rest of the algorithm).  Adjust altitude so that it
        # makes sense with common scatter distribution
        xAlt = altitude
        if model == 'IS':
            if altitude > 150. and slantRange <= 600.:
                xAlt = 115.
            elif altitude > 150. and slantRange > 600. and slantRange <= 800.:
                xAlt = 115. + (slantRange - 600.) / 200. * (altitude - 115.)
        elif model == 'GS':
            if altitude > 150. and slantRange <= 300:
                xAlt = 115.
            elif altitude > 150. and slantRange > 300. and slantRange <= 500.:
                xAlt = 115. + (slantRange - 300.) / 200. * (altitude - 115.)
        if slantRange < 150.:
            xAlt = slantRange / 150. * 115.

        # To start, set Earth radius below field point to Earth radius at radar
        (lat, lon, tRe) = geoPack.geodToGeoc(tGeoLat, tGeoLon)
        RePos = tRe

        # Iterate until the altitude corresponding to the calculated elevation
        # matches the desired altitude
        n = 0  # safety counter
        while True:
            # pointing elevation (spherical Earth value) [degree]
            tel = np.degrees(asin(((RePos + xAlt) ** 2 - (tRe + tAlt) ** 2 -
                                   slantRange ** 2) / (2. * (tRe + tAlt) *
                                                       slantRange)))

            # estimate off-array-normal azimuth (because it varies slightly
            # with elevation) [degree]
            boff = calcAzOffBore(tel, boreOffset, fov_dir=fov_dir)

            # pointing azimuth
            taz = boreSight + boff

            # calculate position of field point
            dictOut = geoPack.calcDistPnt(tGeoLat, tGeoLon, tAlt,
                                          dist=slantRange, el=tel, az=taz)

            # Update Earth radius
            RePos = dictOut['distRe']

            # stop if the altitude is what we want it to be (or close enough)
            n += 1
            if abs(xAlt - dictOut['distAlt']) <= 0.5 or n > 2:
                return dictOut['distLat'], dictOut['distLon']
                break

    # No projection model (i.e., the elevation or altitude is so good that it
    # gives you the proper projection by simple geometric considerations)
    elif not model:
        # Using no models simply means tracing based on trustworthy elevation
        # or altitude
        if not altitude:
            altitude = np.sqrt(Re ** 2 + slantRange ** 2 + 2. * slantRange * Re *
                               np.sin(np.radians(elevation))) - Re
        if not elevation:
            if(slantRange < altitude):
                altitude = slantRange - 10
            elevation = np.degrees(asin(((Re + altitude) ** 2 - (Re + tAlt) ** 2 -
                                         slantRange ** 2) /
                                        (2. * (Re + tAlt) * slantRange)))
        # The tracing is done by calcDistPnt
        dict = geoPack.calcDistPnt(tGeoLat, tGeoLon, tAlt, dist=slantRange,
                                   el=elevation, az=boreSight + boreOffset)
        return dict['distLat'], dict['distLon']


# *************************************************************
# *************************************************************
def slantRange(frang, rsep, recrise, range_gate, center=True):
    """ Calculate slant range

    Parameters
    ----------
    frang
        first range gate position [km]
    rsep
        range gate separation [km]
    recrise
        receiver rise time [us]
    range_gate
        range gate number(s)
    center
        whether or not to compute the slant range in the center of
        the gate rather than at the edge

    Returns
    -------
    srang
        slant range [km]

    """
    # Lag to first range gate [us]
    lagfr = frang * 2. / 0.3
    # Sample separation [us]
    smsep = rsep * 2. / 0.3
    # Range offset if calculating slant range at center of the gate
    range_offset = -0.5 * rsep if not center else 0.0

    # Slant range [km]
    srang = (lagfr - recrise + range_gate * smsep) * 0.3 / 2. + range_offset

    return srang


# *************************************************************
# *************************************************************
def calcAzOffBore(elevation, boreOffset0, fov_dir='front'):
    """Calculate off-boresight azimuth as a function of elevation angle and
    zero-elevation off-boresight azimuth.
    See Milan et al. [1997] for more details on how this works.

    Parameters
    ----------
    elevation
        elevation angle [degree]
    boreOffset0
        zero-elevation off-boresight azimuth [degree]
    fov_dir
        field-of-view direction ('front','back'). Default='front'

    Returns
    -------
    bore_offset
        off-boresight azimuth [degree]

    """
    from math import atan

    # Test to see where the true beam direction lies
    bdir = np.cos(np.radians(boreOffset0)) ** 2 - \
        np.sin(np.radians(elevation)) ** 2

    # Calculate the front fov azimuthal angle off the boresite
    if bdir < 0.0:
        bore_offset = np.pi / 2.
    else:
        tan_boff = np.sqrt(np.sin(np.radians(boreOffset0)) ** 2 / bdir)
        bore_offset = atan(tan_boff)

# Old version
#   if bdir < 0.0:
#       if boreOffset0 >= 0: boreOffset = np.pi/2.
#       else: boreOffset = -np.pi/2.
#   else:
#       tan_boff = np.sqrt(np.sin(np.radians(boreOffset0))**2 / bdir)
#       if boreOffset0 >= 0: boreOffset = atan(tan_boff)
#       else: boreOffset = -atan(tan_boff)

    # If the rear lobe is desired, adjust the azimuthal offset from the
    # boresite
    if fov_dir is 'back':
        bore_offset = np.pi - bore_offset

    # Correct the sign based on the sign of the zero-elevation off-boresight
    # azimuth
    if boreOffset0 < 0.0:
        bore_offset *= -1.0

    return np.degrees(bore_offset)


def gsMapSlantRange(slantRange, altitude=None, elevation=None):
    """Calculate the ground scatter mapped slant range.
    See Bristow et al. [1994] for more details.

    Parameters
    ----------
    slantRange
        normal slant range [km]
    altitude : Optional[float]
        altitude [km] (defaults to 300 km)
    elevation : Optional[float]
        elevation angle [degree]

    Returns
    -------
    gsSlantRange
        ground scatter mapped slant range [km] (typically slightly less than
        0.5*slantRange. Will return -1 if (slantRange**2/4. - altitude**2 >= 0).
        This occurs when the scatter is too close and this model breaks down.

    """
    from math import asin
    from davitpy.utils import Re

    # Make sure you have altitude, because these 2 projection models rely on it
    if not elevation and not altitude:
        # Set default altitude to 300 km
        altitude = 300.0
    elif elevation and not altitude:
        # If you have elevation but not altitude, then you calculate altitude,
        # and elevation will be adjusted anyway
        altitude = np.sqrt(Re ** 2 + slantRange ** 2 + 2. * slantRange * Re *
                           np.sin(np.radians(elevation))) - Re

    if (slantRange ** 2) / 4. - altitude ** 2 >= 0:
        gsSlantRange = Re * \
            asin(np.sqrt(slantRange ** 2 / 4. - altitude ** 2) / Re)
        # From Bristow et al. [1994]
    else:
        gsSlantRange = -1

    return gsSlantRange

if __name__ == "__main__":
    from davitpy.pydarn.radar import radStruct
    from datetime import datetime

    print
    print "Testing radFov"
    print "Expected and result samples are from the fov's"
    print "fov.latCenter[0][0:4] and fov.lonCenter[0][0:4]"
    print "(in that order) on a 32-bit machine"
    print
    time = datetime(2012, 1, 1, 0, 2)
    print "Create a site object for Saskatoon, 2012-01-01 00:02 UT."
    site_sas = radStruct.site(code="sas", dt=time)
    print
    print "Create a fov object using that site, coords are geo."
    fov1 = fov(site=site_sas)
    print "Expected: [ 53.20468706  53.7250585   54.18927222  54.63064699]"
    print "Result:   " + str(fov1.latCenter[0][0:4])
    print "Expected: [-106.87506589 -106.80488558 -106.77349475 -106.75811049]"
    print "Result:   " + str(fov1.lonCenter[0][0:4])
    print "coords of result are " + fov1.coords
    print
    print "Now create a fov object with mag coords."
    fov2 = fov(site=site_sas, coords="mag", date_time=time)
    print "Expected: [ 61.55506679  62.08849503  62.55831358  63.00180636]"
    print "Result:   " + str(fov2.latCenter[0][0:4])
    print "Expected: [-43.22579758 -43.25962883 -43.33474048 -43.42848079]"
    print "Result:   " + str(fov2.lonCenter[0][0:4])
    print "coords of result are " + fov2.coords
    print
    print "Another fov, now in MLT"
    fov3 = fov(site=site_sas, coords="mlt", date_time=time)
    print "Expected: [ 61.55506679  62.08849503  62.55831358  63.00180636]"
    print "Result:   " + str(fov3.latCenter[0][0:4])
    print "Expected: [-121.24209635 -121.27592761 -121.35103925 -121.44477957]"
    print "Result:   " + str(fov3.lonCenter[0][0:4])
    print "coords of result are " + fov3.coords
