# -*- coding: utf-8 -*-
#!usr/bin/env python
# Copyright (C) 2014 University of Saskatchewan SuperDARN group
# Full license can be found in LICENSE.txt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A module for manipulating coordinates

Functions
------------------------------------------------------
coordConv       Kept for back-compat, calls coord_conv
coord_conv      Convert between coordinate systems
planeRot        Rotate coordinates in the plane
get_coord_dict  dict and string for coordinate systems
------------------------------------------------------

Written by Matt W.

"""
import logging

def coordConv(lon, lat, altitude, start, end, dateTime=None):
    """deprecated function, please use coord_conv


    Notes
    ----
    coordConv has been renamed coord_conv and dateTime has been
    renamed date_time for PEP 8 compliance.  Please use those
    from now on.  Also altitude is now optional.

    """
    from davitpy.utils.coordUtils import coord_conv
    logging.warning("coordConv has been renamed coord_conv and dateTime has")
    logging.warning("been renamed date_time for PEP 8 compliance.  Please use")
    logging.warning("those from now on.  Also altitude is now optional.")
    return coord_conv(lon, lat, start, end, altitude=altitude,
                      date_time=dateTime)


def coord_conv(lon, lat, start, end, altitude=None, date_time=None,
               end_altitude=None):
    """Convert between geographical, AACGM, and MLT coordinates.  
    date_time must be set to use any AACGM systems.
  
    Parameters
    ----------
    lon : (int/float/list/np.array)
        longitude (if using MLT, it must be in degrees, not hours)
    lat : (int/float/list/np.array)
        latitude in degrees.  Must be the same size as lon.
    start : (str)
        coordinate system of input. Options: 'geo', 'mag', 'mlt'
    end : (str)
        desired output coordinate system. Options: 'geo', 'mag', 'mlt'
    altitude : (int/float/list/np.array)
        Altitude to be used (km); required for 'mag' and 'mlt' conversions.
        May be a single value or a list/array the same size as lat and lon.
        (default=None)
    date_time : (datetime)
        Universal time for conversion.  Must be provided for 'mag' and 'mlt'
        (default=None)
    end_altitude : (int/float/list/np.array)
        used for conversions from coords at one
        altitude to coords at another.  In km.  Can be int/float or
        list of same size as lon and lat.  Default:  None

    Returns
    -------
    lon : (float, list, or numpy array) 
        MLT is in degrees, not hours.  Output type is the same as
        input type (except int becomes float)
    lat : (float, list, numpy array)
        MLT is in degrees, not hours.  Output type is the same as
        input type (except int becomes float)

    Example
    -------
        import utils
        lon, lat = utils.coord_conv(lon, lat, 'geo', 'mlt',
                                    altitude=300.,
                                    date_time=datetime(2012,3,12,0,56))
        
    Notes
    -----
    A how-to for expansion of this function to handle new coordinate
    systems is included in the code comments.

    original version written by Matt W., 2013-09, based on code by...Sebastien?
    brand new version by Matt W., 2014-08

    """
    import numpy as np

    from davitpy import rcParams
    from davitpy.models import aacgm
    from davitpy.utils.coordUtils import get_coord_dict

    # Define IGRF file location
    igrf_file = rcParams['IGRF_DAVITPY_COEFF_FILE']
    root = rcParams['AACGM_DAVITPY_DAT_PREFIX']

    ####################################################################
    #                                                                  #
    # Sections of code that must be modified to add new coordinate     #
    # systems are highlighted by pound-lines (like this comment is)    #
    # and are provided with instructions in the comments.              #
    #                                                                  #
    ####################################################################

    ####################################################################
    # Coordinate systems are named and listed in this block. Add a new 
    # system to coords_dict with a code (for start and end) and a name.
    # Add the code to the list for the family it belongs to, or create a
    # new list if adding a new family.  Finally, add the code to the 
    # appropriate list if the system requires altitude or date_time.

    # Define acceptable coordinate systems in the function 
    # get_coord_dict
    
    # List all systems in the AACGM family.
    aacgm_sys = ["mag", "mlt"]

    # List all systems that require altitude.
    alti_sys = ["mag", "mlt"]

    # List all systems that require date_time.
    dt_sys = ["mag", "mlt"]

    # End of system list block.
    ####################################################################
    coords_dict, coords_string = get_coord_dict()

    # Create a string for printing of systems requiring altitude.
    alti_string = ""
    for code in alti_sys:
        alti_string += "\n" + coords_dict[code] + " (" + code + ")"

    # Create a string for printing of systems requiring datetime.
    dt_string = ""
    for code in dt_sys:
        dt_string += "\n" + coords_dict[code] + " (" + code + ")"

    # Check that the coordinates are possible.
    assert(start in coords_dict and end in coords_dict),\
            logging.error("Start coords are " + start +
                          " and end coords are " + end +
                          ".\n" + coords_string)

    # Check whether altitude is needed and provided.
    if start in alti_sys or end in alti_sys or end_altitude is not None:
        assert(altitude is not None),\
                logging.error("altitude must be provided for: " +
                              alti_string + "\nto perform altitude " +
                              "conversions")
    
    # Check whether date_time is needed and provided.
    if start in dt_sys or end in dt_sys:
        assert(date_time is not None),\
                logging.error("date_time must be provided for: " +
                              dt_string)

    # Sanitise inputs.
    if isinstance(lon, int):
        lon, lat = float(lon), float(lat)
    is_list = isinstance(lon, (list, tuple))
    is_float = isinstance(lon, float)
    if is_float:
        lon, lat = [lon], [lat]
    if not (is_float or is_list):
        assert(isinstance(lon, np.ndarray)),\
                logging.error("Must input int, float, list, or " +
                              "numpy array.")

    # Make the inputs into numpy arrays because single element lists 
    # have no len.
    lon, lat = np.array(lon), np.array(lat)
    orig_shape = np.shape(lon)
    lon, lat = lon.flatten(), lat.flatten()

    # Test whether we are using the same altitude for everything.
    if altitude is not None:
        alt = np.array(altitude)
        if np.size(alt) == 1:
            alt = np.resize(alt, np.size(lon))

    if end_altitude is not None:
        e_alt = np.array(end_altitude)
        if np.size(e_alt) == 1:
            e_alt = np.resize(e_alt, np.size(lon))

    # Set a flag that we are doing and altitude conversion.
    alt_conv = (end_altitude is not None and end_alt != alt)

    ####################################################################
    # FROM conversions for system families are performed in this 
    # section.  Within the family of the start system, convert into the 
    # base system for that family.  If the end system is not in the same
    # family, end by converting from the base system into geographic.
    #
    # Add new systems and families by following the example of the AACGM 
    # family block.

    # Check whether there is a conversion to do.
    if start != end or alt_conv:
        ################################################################
        # AACGM family FROM conversions.
        # This is the reason for having the aacgm_sys list:
        if start in aacgm_sys:
            # Convert all other AACGM systems to AACGM.  Follow the
            # example of the MLT block to add new systems within the
            # family.

            ############################################################
            # Convert MLT to AACGM
            if start == "mlt":
                # Convert MLT from degrees to hours.
                lon *= 24.0 / 360.0
                # Sanitise for later.
                lon %= 24.0
                # Find MLT of 0 magnetic lon.
                mlt_0 = aacgm.mlt_convert(date_time.year, date_time.month,
                                          date_time.day, date_time.hour,
                                          date_time.minute, date_time.second,
                                          0.0, root, igrf_file)     
                # Calculate MLT difference, which is magnetic lon in hours.
                lon -= mlt_0
                # Sanitise and convert to degrees.
                lon %= 24.0
                lon *= 360.0 / 24.0
                # Covert from (0,360) to (-180,180).
                lon[np.where(lon > 180.0)] -= 360.0
                start = "mag"

            # End of MLT FROM block.
            ############################################################
        
            # Now it is in AACGM.  
            assert(start == "mag"),logging.error("should be in AACGM now")

            # If the end result is not an AACGM system or there is an
            # altitude conversion, convert to geo.
            if (end not in aacgm_sys) or alt_conv:
                lat, lon, _ = aacgm.convert_latlon_arr(lat, lon, alt,
                                                       date_time, 'A2G',
                                                       igrf_file=igrf_file,
                                                       coeff_prefix=root)
                start = "geo"
        
        # End of AACGM family FROM block.
        ################################################################

    # End of FROM block.
    ####################################################################

    # Now it is in:
    # AACGM if the start and end are in an AACGM system
    # geo otherwise
    # Add to this list for new system families to help keep track.

    # If there is an altitude conversion, it will be in geo now and the
    # next step is to convert to the end system even if it's the same
    # as the start system.  When we do that we want to set:
    if alt_conv:
        alt = e_alt

    ####################################################################
    # TO conversions for system families are performed in this 
    # section.  If the start system was not in the same family as the
    # end system (i.e., it is now in geographic), convert into the base 
    # system for the family of the end system.  Then convert within the
    # family to the end system.
    #
    # Add new systems and families by following the example of the AACGM 
    # family block.
    
    # Check whether there is still a conversion to do.  If the
    # conversion is to geographic or to the base system of whatever
    # family the start was in, then all the work is done.
    if start != end:

        ################################################################
        # AACGM family TO conversions.
        if end in aacgm_sys:
            # If it isn't in AACGM already it's in geo.
            if start == "geo":
                lat, lon, _ = aacgm.convert_latlon_arr(lat, lon, alt, date_time,
                                                       'G2A', igrf_file, root)
                start = "mag"

            # It is in AACGM now.
            assert start == "mag", logging.error("should be in AACGM now")

            # Convert AACGM to all other AACGM systems.  Follow the
            # example of the MLT block to add new systems within the
            # family.

            ############################################################
            # MLT TO conversions.
            if end == "mlt":
                for num, el in enumerate(lon):
                    # Find MLT from magnetic lon and datetime.
                    lon[num] = aacgm.mlt_convert(date_time.year,
                                                 date_time.month, date_time.day,
                                                 date_time.hour,
                                                 date_time.minute, 
                                                 date_time.second, el, root,
                                                 igrf_file)
                # Convert hours to degrees.
                lon *= 360.0 / 24.0
                # Convert from (0,360) to (-180,180).
                lon[np.where(lon > 180.0)] -= 360.0
                start = "mlt"

            # End of MLT TO block.
            ############################################################

        # End of AACGM family TO block.
        ################################################################

    # End of TO block.
    ####################################################################

    # Now it should be in the end system.
    assert(start == end),logging.error("not in correct end system...?????")

    # Convert outputs to input type and shape.
    if is_list:
        lon, lat = list(lon), list(lat)
    elif is_float:
        lon, lat = list(lon)[0], list(lat)[0]
    else:
        # Otherwise it stays a numpy array.
        lon, lat = lon.reshape(orig_shape), lat.reshape(orig_shape)

    return lon, lat


def planeRot(x, y, theta):
    """Rotate coordinates in the plane.
  
    Parameters
    ----------
    x : (int/float/list/np.array)
        x coordinate
    y : (int/float/list/np.array)
        y coordinate
    theta : (float/np.array)
        angle of rotation of new coordinate frame in radians

    Returns
    -------
    x_prime : (np.array)
        x coordinates in rotated frame
    y_prime : (np.array)
        y coordinates in rotated frame

    Example
    -------
        import numpy as np
        x, y = planeRot(x, y, 30.*np.pi/180.)
        
    written by Matt W., 2013-09

    """
    import numpy as np

    oldx, oldy = np.array(x), np.array(y)

    x = oldx * np.cos(theta) + oldy * np.sin(theta)
    y = -oldx * np.sin(theta) + oldy * np.cos(theta)

    return x, y


def get_coord_dict():
    """A function to return the coordinate dictionary and a string
    listing the possible coordinates for use.

    Returns
    -------
    coord_dict : (dict)
        the dictonary
    coord_string : (str)
        the string

    Example
    -------
        from utils.coordUtils import get_coord_dict
        coord_dict, coord_string = get_coord_dict()
        print coord_string
        > Possible coordinate systems are:
          AACGM (mag)
          Geographic (geo)
          MLT (mlt)

    written by Matt W., 2014-08

    """
    # Define the dictionary.
    coord_dict = {"mag": "AACGM", "geo": "Geographic", "mlt": "MLT"}

    # Create a string of coord systems for printing to the terminal.
    coord_string = "Possible coordinate systems are:"
    for code, name in coord_dict.iteritems():
        coord_string += "\n" + name + " (" + code + ")"

    return coord_dict, coord_string


# Some testing stuff.
if __name__ == "__main__":
    from datetime import datetime
    import numpy

    print
    print "All of these results may have varying sigfigs."
    print "The expected values were found on a 32-bit system."
    print
    print "Test of redirection function coordConv"
    print coordConv(50.7, 34.5, 300., "geo", "geo", 
                    dateTime=datetime(2012, 1, 1, 0, 2))
    print
    print "Single coord pair tests"
    print
    print "Test of list -> list"
    print "Expected for 32-bit system:  ([50.700000000000003], [34.5])"
    print "Expected for 64-bit system:  ([50.700000000000003], [34.5])"
    print "Result:                      " + \
str(coord_conv([50.7], [34.5], 'geo', 'geo'))
    print
    print "Test of float -> float"
    print "Expected for 32-bit system:  (50.700000000000003, 34.5)"
    print "Expected for 64-bit system:  (50.700000000000003, 34.5)" 
    print "Result:                      " + \
str(coord_conv(50.7, 34.5, 'geo', 'geo'))
    print
    print "Test of int -> float"
    print "Expected for 32-bit system:  (50.0, 34.0)"
    print "Expected for 64-bit system:  (50.0, 34.0)"
    print "Result:                      " + \
str(coord_conv(50, 34, 'geo', 'geo'))
    print
    print "Tests of numpy array -> numpy array"
    print "Expected for 32-bit system:  (array([ 50.7]), array([ 34.5]))"
    print "Expected for 64-bit system:  (array([ 50.7]), array([ 34.5]))"
    print "Result:                      " + \
str(coord_conv(numpy.array([50.7]), numpy.array([34.5]), 'geo', 'geo'))
    print
    print "geo to geo, mag to mag, mlt to mlt, ashes to ashes"
    print "Expected for 32-bit system: (50.700000000000003, 34.5)"
    print "Expected for 64-bit system: (50.700000000000003, 34.5)"
    print "Result:                     " + \
str(coord_conv(50.7, 34.5, 'geo', 'geo'))
    print "Result:                     " + \
str(coord_conv(50.7, 34.5, 'mag', 'mag', altitude=300., 
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print "Result:                     " + \
str(coord_conv(50.7, 34.5, 'mlt', 'mlt', altitude=300.,
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "geo to mag"
    print "Expected for 32-bit system: " +\
"(123.71642616363432, 31.582924632749929)"
    print "Expected for 64-bit system: " +\
"(123.7164261636343, 31.582924632749936)"
    print "Result:                     " + \
str(coord_conv(50.7, 34.5, 'geo', 'mag', altitude=300.,
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "geo to mlt"
    print "Expected for 32-bit system:  " +\
"(-130.65999038625603, 31.582924632749929)"
    print "Expected for 64-bit system:  " +\
"(-130.65999038625606, 31.582924632749936)"
    print "Result:                      " + \
str(coord_conv(50.7, 34.5, 'geo', 'mlt', altitude=300.,
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mag to geo"
    print "Expected for 32-bit system:  " +\
"(50.563320914903102, 32.408924471374895)"
    print "Expected for 64-bit system:  " +\
"(50.563320914903116, 32.408924471374867)" 
    print "Result:                      " + \
str(coord_conv(123.53805352405843, 29.419420613372086,
               'mag', 'geo', altitude=300.,
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mlt to geo"
    print "Expected for 32-bit system: " +\
"(50.563320914903137, 32.408924471374895)"
    print "Expected for 64-bit system: " +\
"(50.563320914903088, 32.408924471374867)"
    print "Result:                     " + \
str(coord_conv(229.16163697416806, 29.419420613372086,
               'mlt', 'geo', altitude=300.,
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mag to mlt"
    print "Expected for 32-bit system: " +\
"(-130.83836302583194, 29.419420613372086)"
    print "Expected for 64-bit system: " +\
"(-130.83836302583194, 29.419420613372086)"
    print "Result:                     " + \
str(coord_conv(123.53805352405843, 29.419420613372086,
               'mag', 'mlt', altitude=300.,
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mlt to mag"
    print "Expected for 32-bit system:  " +\
"(123.53805352405843, 29.419420613372086)"
    print "Expected for 64-bit system:  " +\
"(123.53805352405841, 29.419420613372086)"
    print "Result:                      " + \
str(coord_conv(229.16163697416806, 29.419420613372086,
            'mlt', 'mag', altitude=300.,
            date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "Coord array tests"
    print
    print "Test of n x m arrays"
    print "Expected for 32-bit system:  (array([[-130.65999039, -120.89269136], [-139.26450185, -149.12386912]]), array([[ 31.58292463,  42.81408443], [ 18.42380165,  36.68788184]]))"
    print "Expected for 64-bit system:  "
    print "Result:                      " + \
str(coord_conv(numpy.array([[50.7, 60.1],[42.4, 32.1]]),
               numpy.array([[34.5, 45.6],[21.1, 40.4]]), "geo", "mlt",
               altitude=300., date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "geo to geo, mag to mag, mlt to mlt"
    print "Expected for 32-bit system: " +\
"([50.700000000000003, 53.799999999999997], \
[34.5, 40.200000000000003])"
    print "Expected for 64-bit system: " +\
"([50.700000000000003, 53.799999999999997], \
[34.5, 40.200000000000003])"
    print "Result:                     " + \
str(coord_conv([50.7, 53.8], [34.5, 40.2], 'geo', 'geo'))
    print "Result:                     " + \
str(coord_conv([50.7, 53.8], [34.5, 40.2], 'mag', 'mag',
               altitude=300., date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print "Result:                     " + \
str(coord_conv([50.7, 53.8], [34.5, 40.2], 'mlt', 'mlt',
               altitude=300., date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "geo to mag"
    print "Expected for 32-bit system: " +\
"([123.65800072339718, 126.97463420949806], \
[30.892913121194589, 37.369211032553089])"
    print "Expected for 64-bit system: " +\
"([123.65800072339719, 126.97463420949806], \
[30.892913121194589, 37.36921103255311])" 
    print "Result:                     " + \
str(coord_conv([50.7, 53.8], [34.5, 40.2], 'geo', 'mag',
                altitude=[200., 300.],
                date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "geo to mlt"
    print "Expected for 32-bit system: " +\
"([-130.71841582649319, -127.40178234039229], \
[30.892913121194589, 37.369211032553089])"
    print "Expected for 64-bit system: " +\
"([-130.71841582649316, -127.40178234039229], \
[30.892913121194589, 37.36921103255311])"
    print "Result:                     " + \
str(coord_conv([50.7, 53.8], [34.5, 40.2], 'geo', 'mlt',
                altitude=[200., 300.],
                date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mag to geo"
    print "Expected for 32-bit system: " +\
"([50.615511474515607, 53.648287906901672], \
[33.150771171950133, 38.637420715148586])"
    print "Expected for 64-bit system: " +\
"([50.615511474515607, 53.648287906901686], \
[33.150771171950126, 38.637420715148593])"
    print "Result:                     " + \
str(coord_conv([123.53805352405843, 126.76454464467615], 
               [29.419420613372086, 35.725172012254788], 'mag', 'geo',
               altitude=[200., 300.], 
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mlt to geo"
    print "Expected for 32-bit system: " +\
"([50.563320914903137, 53.648287906901672], \
[32.408924471374895, 38.637420715148586])"
    print "Expected for 64-bit system: " +\
"([50.563320914903088, 53.648287906901686], \
[32.408924471374867, 38.637420715148593])"
    print "Result:                     " + \
str(coord_conv([229.16163697416806, 232.38812809478577], 
               [29.419420613372086, 35.725172012254788], 'mlt', 'geo',
               altitude=300., date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mag to mlt"
    print "Expected for 32-bit system: " +\
"([-130.83836302583194, -127.61187190521423], \
[29.419420613372086, 35.725172012254788])"
    print "Expected for 64-bit system: " +\
"([-130.83836302583194, -127.61187190521423], \
[29.419420613372086, 35.725172012254788])"
    print "Result:                     " + \
str(coord_conv([123.53805352405843, 126.76454464467615],
               [29.419420613372086, 35.725172012254788], 'mag', 'mlt',
               altitude=300., date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mlt to mag"
    print "Expected for 32-bit system: " +\
"([123.53805352405843, 126.76454464467615], \
[29.419420613372086, 35.725172012254788])"
    print "Expected for 64-bit system: " +\
"([123.53805352405841, 126.76454464467616], \
[29.419420613372086, 35.725172012254788])" 
    print "Result:                     " + \
str(coord_conv([229.16163697416806, 232.38812809478577], 
               [29.419420613372086, 35.725172012254788], 'mlt', 'mag',
               altitude=200., date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "Altitude conversion tests"
    print "mlt at 300 to mlt at 200"
    print "Expected for 32-bit system: " +\
"(50.672783138859764, 53.443261761838208)"
    print "Expected for 64-bit system: " +\
"(50.672783138859778, 53.443261761838208)"
    print "Result:                     " + \
str(coord_conv(50.7, 53.8, "mlt", "mlt", altitude=300., end_altitude=200.,
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mlt at 300 to mag at 200"
    print "Expected for 32-bit system: " +\
"(-54.950800311249871, 53.443261761838208)"
    print "Expected for 64-bit system: " +\
"(-54.950800311249857, 53.443261761838208)" 
    print "Result:                     " + \
str(coord_conv(50.7, 53.8, "mlt", "mag", altitude=300., end_altitude=200.,
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "mag at 300 to mlt at 200"
    print "Expected for 32-bit system: " +\
"(156.31132401765453, 53.423480021345064)"
    print "Expected for 64-bit system: " +\
"(156.3113240176545, 53.423480021345057)"
    print "Result:                     " + \
str(coord_conv(50.7, 53.8, "mag", "mlt", altitude=300., end_altitude=200.,
               date_time=datetime(2013, 7, 23, 12, 6, 34)))
    print
    print "testing with lists, mag to mag"
    print "Expected for 32-bit system: " +\
"([-130.82669554662644, -127.53759707536527], \
[29.04361718657001, 34.973380997519293])"
    print "Expected for 64-bit system: " +\
"([-130.82669554662647, -127.53759707536523], \
[29.043617186570032, 34.973380997519286])"
    print "Result:                     " + \
str(coord_conv([229.16163697416806, 232.38812809478577], 
               [29.419420613372086, 35.725172012254788], 'mag', 'mag', 
               altitude=[200., 300.], end_altitude=[150., 175.], 
               date_time= datetime(2013, 7, 23, 12, 6, 34)))
    print "OTHER TESTS:  these tests will fail because of asserts so"
    print "they should be done in an interpreter."
    print "-set start or end to a fictional system code like abc"
    print "-set start or end to mlt or mag and don't supply altitude"
    print "-same but don't supply date_time"
