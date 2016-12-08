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
    hop : Optional[scalar or ndarray(ngates) or ndarray(nbeams,ngates)]
        Hop, used if elevation angle is used.
    model
        IS : standard ionospheric scatter projection model (default)
        GS : standard ground scatter projection model
        S : standard projection model
        E1 : for Chisham E-region 1/2-hop ionospheric projection model
        F1 : for Chisham F-region 1/2-hop ionospheric projection model
        F3 : for Chisham F-region 1-1/2-hop ionospheric projection model
        C : Chisham projection model
        None : if you trust your elevation or altitude values
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
                 elevation=None, altitude=300., hop=None, model='IS',
                 coords='geo', date_time=None, coord_alt=0., fov_dir='front'):
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

        # If altitude, elevation, or hop are arrays, then they should be of
        # shape (nbeams, ngates)
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

        if isinstance(hop, np.ndarray):
            if hop.ndim == 1:
                # Array is adjusted to add on extra beam/gate edge by copying
                # the last element and replicating the whole array as many
                # times as beams
                if hop.size != ngates:
                    estr = '{:s}: hop must be of a scalar or numpy '.format(rn)
                    estr = '{:s}ndarray of size (ngates) or '.format(estr)
                    estr = '{:s}(nbeans,ngates). Using first '.format(estr)
                    estr = '{:s}element: {}'.format(estr, hop[0])
                    logging.error(estr)
                    hop = hop[0] * np.ones((nbeams + 1, ngates + 1))
                else:
                    hop = np.resize(np.append(hop, hop[-1]),
                                    (nbeams + 1, ngates + 1))
            elif hop.ndim == 2:
                # Array is adjusted to add on extra beam/gate edge by copying
                # the last row and column
                if hop.shape != (nbeams, ngates):
                    estr = '{:s}: hop must be of a scalar or numpy '.format(rn)
                    estr = '{:s}ndarray of size (ngates) or '.format(estr)
                    estr = '{:s}(nbeans,ngates). Using first '.format(estr)
                    estr = '{:s}element: {}'.format(hop[0])
                    logging.error(estr)
                    hop = hop[0] * np.ones((nbeams + 1, ngates + 1))
                else:
                    hop = np.append(hop, hop[-1, :].reshape(1, ngates), axis=0)
                    hop = np.append(hop, hop[:, -1].reshape(nbeams, 1), axis=1)
            else:
                estr = '{:s}: hop must be a scalar or numpy ndarray'.format(rn)
                estr = '{:s} of size (ngates) or (nbeams,ngates).'.format(estr)
                estr = '{:s} Using first element: {}'.format(estr, hop[0])
                logging.error(estr)
                hop = hop[0] * np.ones((nbeams + 1, ngates + 1))

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
                srang_edge = slantRange(frang[ib], rsep[ib], recrise[ib],
                                        gates, center=False)
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
                thop = hop[ib, ig] if isinstance(hop, np.ndarray) else hop

                if model == 'GS':
                    if (~is_param_array and ib == 0) or is_param_array:
                        slant_range_center[ib, ig] = \
                            gsMapSlantRange(srang_center[ig], altitude=None,
                                            elevation=None)
                        slant_range_full[ib, ig] = \
                            gsMapSlantRange(srang_edge[ig], altitude=None,
                                            elevation=None)
                        srang_center[ig] = slant_range_center[ib, ig]
                        srang_edge[ig] = slant_range_full[ib, ig]

                if (srang_center[ig] != -1) and (srang_edge[ig] != -1):
                    # Then calculate projections
                    latc, lonc = calcFieldPnt(siteLat, siteLon, siteAlt * 1e-3,
                                              siteBore, boff_center[ib],
                                              srang_center[ig], elevation=telv,
                                              altitude=talt, hop=thop,
                                              model=model, fov_dir=fov_dir)
                    late, lone = calcFieldPnt(siteLat, siteLon, siteAlt * 1e-3,
                                              siteBore, boff_edge[ib],
                                              srang_edge[ig], elevation=telv,
                                              altitude=talt, hop=thop,
                                              model=model, fov_dir=fov_dir)
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
        self.fov_dir = fov_dir
        self.model = model

    # *************************************************************
    def __str__(self):
        outstring = 'latCenter: {}\nlonCenter: {}\nlatFull: {}\nlonFull: {} \
                     \nslantRCenter: {}\nslantRFull: {}\nbeams: {} \
                     \ngates: {} \ncoords: {} \nfield of view: {}\
                     \nmodel: {}'.format(np.shape(self.latCenter),
                                         np.shape(self.lonCenter),
                                         np.shape(self.latFull),
                                         np.shape(self.lonFull),
                                         np.shape(self.slantRCenter),
                                         np.shape(self.slantRFull),
                                         np.shape(self.beams),
                                         np.shape(self.gates), self.coords,
                                         self.fov_dir, self.model)
        return outstring


# *************************************************************
# *************************************************************
def calcFieldPnt(tr_glat, tr_glon, tr_alt, boresight, beam_off, slant_range,
                 adjusted_sr=True, elevation=None, altitude=None, hop=None,
                 model=None, coords='geo', gs_loc="G", max_vh=400.0,
                 fov_dir='front'):
    """Calculate coordinates of field point given the radar coordinates and
    boresight, the pointing direction deviation from boresight and elevation
    angle, and the field point slant range and altitude. Either the elevation
    or the altitude must be provided. If none is provided, the altitude is set
    to 300 km and the elevation evaluated to accomodate altitude and range.

    Parameters
    ----------
    tr_glat
        transmitter latitude [degree, N]
    tr_glon
        transmitter longitude [degree, E]
    tr_alt
        transmitter altitude [km]
    boresight
        boresight azimuth [degree, E]
    beam_off
        beam azimuthal offset from boresight [degree]
    slant_range
        slant range [km]
    adjusted_sr : Optional(bool)
        Denotes whether or not the slant range is the total measured slant
        range (False) or if it has been adjusted to be the slant distance to
        last ionospheric reflection point (True).  (default=True)
    elevation : Optional[float]
        elevation angle [degree] (estimated if None)
    altitude : Optional[float]
        altitude [km] (default 300 km)
    hop : Optional[float]
        backscatter hop (ie 0.5, 1.5 for ionospheric; 1.0, 2.0 for ground)
    model : Optional[str]
        IS : for standard ionopsheric scatter projection model (ignores hop)
        GS : for standard ground scatter projection model (ignores hop)
        S : for standard projection model (uses hop)
        E1 : for Chisham E-region 1/2-hop ionospheric projection model
        F1 : for Chisham F-region 1/2-hop ionospheric projection model
        F3 : for Chisham F-region 1-1/2-hop ionospheric projection model
        C : for Chisham projection model (ionospheric only, ignores hop,
            requires total measured slant range)
        None : if you trust your elevation or altitude values. more to come
    coords
        'geo' (more to come)
    gs_loc : (str)
        Provide last ground scatter location 'G' or ionospheric refraction
        location 'I' for groundscatter (default='G')
    max_vh : (float)
        Maximum height for longer slant ranges in Standard model (default=400)
    fov_dir
        'front' (default) or 'back'.  Specifies fov direction

    Returns
    ---------
    geo_dict['geoLat'] : (float or np.ndarray)
        Field point latitude(s) in degrees or np.nan if error
    geo_dict['geoLon'] : (float or np.ndarray)
        Field point longitude(s) in degrees or np.nan if error
    """
    from davitpy.utils import Re, geoPack
    import davitpy.utils.model_vheight as vhm

    # Only geo is implemented.
    if coords != "geo":
        logging.error("Only geographic (geo) is implemented in calcFieldPnt.")
        return np.nan, np.nan

    # Use model to get altitude if desired
    xalt = np.nan
    calt = None
    if model is not None:
        if model in ['IS', 'GS', 'S']:
            # The standard model can be used with or without an input altitude
            # or elevation.  Returns an altitude that has been adjusted to
            # comply with common scatter distributions
            if hop is None:
                if model == "S":
                    # Default to ionospheric backscatter if hop not specified
                    hop = 0.5
                else:
                    hop = 0.5 if model == "IS" else 1.0

            xalt = vhm.standard_vhm(slant_range, adjusted_sr=adjusted_sr,
                                    max_vh=max_vh, hop=hop, alt=altitude,
                                    elv=elevation)
        else:
            # The Chisham model uses only the total slant range to determine
            # altitude based on years of backscatter data at SAS.  Performs
            # significantly better than the standard model for ionospheric
            # backscatter, not tested on groundscatter
            if adjusted_sr:
                logging.error("Chisham model needs total slant range")
                return np.nan, np.nan

            # Use Chisham model to calculate virtual height
            cmodel = None if model == "C" else model
            xalt, shop = vhm.chisham_vhm(slant_range, cmodel, hop_output=True)

            # If hop is not known, set using model divisions
            if hop is None:
                hop = shop

            # If hop is greater than 1/2, the elevation angle needs to be
            # calculated from the ground range rather than the virtual height
            if hop > 0.5:
                calt = float(xalt)

    elif elevation is None or np.isnan(elevation):
        if hop is None or adjusted_sr:
            logging.error("Total slant range and hop needed with measurements")
            return np.nan, np.nan
        if altitude is None or np.isnan(altitude):
            logging.error("No observations supplied")
            return np.nan, np.nan

        # Adjust slant range if there is groundscatter and the location
        # desired is the ionospheric reflection point
        asr = slant_range
        if hop == np.floor(hop) and gs_loc == "I":
            asr *= 1.0 - 1.0 / (2.0 * hop)

        # Adjust altitude if it's unrealistic
        if asr < altitude:
            altitude = asr - 10

        xalt = altitude

    # Use model altitude to determine elevation angle and then the location,
    # or if elevation angle was supplied, find the location
    if not np.isnan(xalt):
        # Since we have a modeled or measured altitude, start by setting the
        # Earth radius below field point to Earth radius at radar
        (lat, lon, tr_rad) = geoPack.geodToGeoc(tr_glat, tr_glon)
        rad_pos = tr_rad

        # Iterate until the altitude corresponding to the calculated elevation
        # matches the desired altitude.  Assumes straight-line path to last
        # ionospheric scattering point, so adjust slant range if necessary
        # for groundscatter
        asr = slant_range
        shop = hop
        if not adjusted_sr and hop == np.floor(hop) and gs_loc == "I":
            asr *= 1.0 - 1.0 / (2.0 * hop)
            shop = hop - 0.5

        # Set safty counter and iteratively determine location
        maxn = 30
        hdel = 100.0
        htol = 0.5
        if (slant_range >= 800.0 and model != 'GS') or shop > 1.0:
            htol = 5.0
        n = 0
        while n < maxn:
            tr_dist = tr_rad + tr_alt
            if calt is not None:
                # Adjust elevation angle for any hop > 1 (Chisham et al. 2008)
                pos_dist = rad_pos + calt
                phi = np.arccos((tr_dist**2 + pos_dist**2 - asr**2) /
                                (2.0 * tr_dist * pos_dist))
                beta = np.arcsin((tr_dist * np.sin(phi / (shop * 2.0))) /
                                 (asr / (shop * 2.0)))
                tel = np.pi / 2.0 - beta - phi / (shop * 2.0)

                if xalt == calt:
                    xalt = np.sqrt(tr_rad**2 + asr**2 + 2.0 * asr * tr_rad *
                                   np.sin(tel)) - tr_rad
                tel = np.degrees(tel)
            else:
                # pointing elevation (spherical Earth value) [degree]
                tel = np.arcsin(((rad_pos + xalt)**2 - tr_dist**2 - asr**2) /
                                (2.0 * tr_dist * asr))
                tel = np.degrees(tel)

            # estimate off-array-normal azimuth (because it varies slightly
            # with elevation) [degree]
            boff = calcAzOffBore(tel, beam_off, fov_dir=fov_dir)
            # pointing azimuth
            taz = boresight + boff
            # calculate position of field point
            geo_dict = geoPack.calcDistPnt(tr_glat, tr_glon, tr_alt,
                                           dist=asr, el=tel, az=taz)

            # Update Earth radius
            rad_pos = geo_dict['distRe']

            # stop if the altitude is what we want it to be (or close enough)
            new_hdel = abs(xalt - geo_dict['distAlt'])
            if new_hdel <= htol:
                break

            # stop unsuccessfully if the altitude difference hasn't improved
            if abs(new_hdel - hdel) < 1.0e-3:
                n = maxn

            # Prepare the next iteration
            hdel = new_hdel
            n += 1

        if n >= maxn:
            estr = 'Accuracy on height calculation ({}) not '.format(htol)
            estr = '{:s}reached quick enough. Returning nan, nan.'.format(estr)
            logging.warning(estr)
            return np.nan, np.nan
        else:
            return geo_dict['distLat'], geo_dict['distLon']
    elif elevation is not None:
        # No projection model (i.e., the elevation or altitude is so good that
        # it gives you the proper projection by simple geometric
        # considerations). Using no models simply means tracing based on
        # trustworthy elevation or altitude
        if hop is None or adjusted_sr:
            logging.error("Hop and total slant range needed with measurements")
            return np.nan, np.nan

        if np.isnan(elevation):
            logging.error("No observations provided")
            return np.nan, np.nan

        shop = hop - 0.5 if hop == np.floor(hop) and gs_loc == "I" else hop
        asr = slant_range
        if hop > 0.5 and hop != shop:
            asr *= 1.0 - 1.0 / (2.0 * hop)

        # The tracing is done by calcDistPnt
        boff = calcAzOffBore(elevation, beam_off, fov_dir=fov_dir)
        geo_dict = geoPack.calcDistPnt(tr_glat, tr_glon, tr_alt, dist=asr,
                                       el=elevation, az=boresight + boff)

        return geo_dict['distLat'], geo_dict['distLon']


# *************************************************************
# *************************************************************
def slantRange(frang, rsep, recrise, range_gate, center=True):
    """ Calculate slant range

    Parameters
    ----------
    frang : (float)
        first range gate position [km]
    rsep : (float)
        range gate separation [km]
    recrise : (float)
        receiver rise time [us]
    range_gate : (int)
        range gate number(s)
    center : (bool)
        whether or not to compute the slant range in the center of
        the gate rather than at the edge (default=True)

    Returns
    -------
    srang : (float)
        slant range [km]
    """
    # Lag to first range gate [us]
    lagfr = frang * 2.0 / 0.3
    # Sample separation [us]
    smsep = rsep * 2.0 / 0.3
    # Range offset if calculating slant range at center of the gate
    range_offset = -0.5 * rsep if not center else 0.0

    # Slant range [km]
    srang = (lagfr - recrise + range_gate * smsep) * 0.3 / 2.0 + range_offset

    return srang


# *************************************************************
# *************************************************************
def calcAzOffBore(elevation, boff_zero, fov_dir='front'):
    """Calculate off-boresight azimuth as a function of elevation angle and
    zero-elevation off-boresight azimuth.
    See Milan et al. [1997] for more details on how this works.

    Parameters
    ----------
    elevation
        elevation angle [degree]
    boff_zero
        zero-elevation off-boresight azimuth [degree]
    fov_dir
        field-of-view direction ('front','back'). Default='front'

    Returns
    -------
    bore_offset
        off-boresight azimuth [degree]
    """
    # Test to see where the true beam direction lies
    bdir = np.cos(np.radians(boff_zero))**2 - np.sin(np.radians(elevation))**2

    # Calculate the front fov azimuthal angle off the boresite
    if bdir < 0.0:
        bore_offset = np.pi / 2.
    else:
        tan_boff = np.sqrt(np.sin(np.radians(boff_zero))**2 / bdir)
        bore_offset = np.arctan(tan_boff)

# Old version
#   if bdir < 0.0:
#       if boff_zero >= 0: boreOffset = np.pi/2.
#       else: boreOffset = -np.pi/2.
#   else:
#       tan_boff = np.sqrt(np.sin(np.radians(boff_zero))**2 / bdir)
#       if boff_zero >= 0: boreOffset = atan(tan_boff)
#       else: boreOffset = -atan(tan_boff)

    # If the rear lobe is desired, adjust the azimuthal offset from the
    # boresite
    if fov_dir is 'back':
        bore_offset = np.pi - bore_offset

    # Correct the sign based on the sign of the zero-elevation off-boresight
    # azimuth
    if boff_zero < 0.0:
        bore_offset *= -1.0

    return np.degrees(bore_offset)


def gsMapSlantRange(slant_range, altitude=None, elevation=None):
    """Calculate the ground scatter mapped slant range.
    See Bristow et al. [1994] for more details. (Needs full reference)

    Parameters
    ----------
    slant_range
        normal slant range [km]
    altitude : Optional[float]
        altitude [km] (defaults to 300 km)
    elevation : Optional[float]
        elevation angle [degree]

    Returns
    -------
    gsSlantRange
        ground scatter mapped slant range [km] (typically slightly less than
        0.5 * slant_range.  Will return -1 if
        (slant_range**2 / 4. - altitude**2) >= 0. This occurs when the scatter
        is too close and this model breaks down.
    """
    from davitpy.utils import Re

    # Make sure you have altitude, because these 2 projection models rely on it
    if not elevation and not altitude:
        # Set default altitude to 300 km
        altitude = 300.0
    elif elevation and not altitude:
        # If you have elevation but not altitude, then you calculate altitude,
        # and elevation will be adjusted anyway
        altitude = np.sqrt(Re ** 2 + slant_range ** 2 + 2. * slant_range * Re *
                           np.sin(np.radians(elevation))) - Re

    if (slant_range**2) / 4. - altitude ** 2 >= 0:
        gsSlantRange = Re * \
            np.arcsin(np.sqrt(slant_range ** 2 / 4. - altitude ** 2) / Re)
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
    print "Create a fov object using that site, coords are geo, model Chisham."
    fov1 = fov(site=site_sas, model="C")
#    print "Expected: [ 53.20468706  53.7250585   54.18927222  54.63064699]"
#    print "Result:   " + str(fov1.latCenter[0][0:4])
#    print "Expected: [-106.87506589 -106.80488558 -106.77349475 "
#    print "-106.75811049]"
#    print "Result:   " + str(fov1.lonCenter[0][0:4])
#    print "coords of result are " + fov1.coords
    print
    print "Now create a fov object with mag coords."
    fov2 = fov(site=site_sas, coords="mag", date_time=time)
    print "Expected: [ 61.55506679  62.08849503  62.55831358  63.00180636]"
    print "Result:   " + str(fov2.latCenter[0][0:4])
    print "Expected: [-43.22579758 -43.25962883 -43.33474048 -43.42848079]"
    print "Result:   " + str(fov2.lonCenter[0][0:4])
    print "coords of result are " + fov2.coords
    print
    print "Another fov, now in MLT."
    fov3 = fov(site=site_sas, coords="mlt", date_time=time)
    print "Expected: [ 61.55506679  62.08849503  62.55831358  63.00180636]"
    print "Result:   " + str(fov3.latCenter[0][0:4])
    print "Expected: [-121.24209635 -121.27592761 -121.35103925 -121.44477957]"
    print "Result:   " + str(fov3.lonCenter[0][0:4])
    print "coords of result are " + fov3.coords
