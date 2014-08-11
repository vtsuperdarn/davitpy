# Copyright (C) 2013  University of Saskatchewan SuperDARN group
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

"""
.. module:: coordUtils
    :synopsis: A module for manipulating coordinates

.. moduleauthor:: mrwessel

****************************
**Module**: utils.coordUtils
****************************
**Functions**:
    
    * :func:`utils.coordUtils.coordConv`: Kept for back-compat, calls
        coord_conv
    * :func:`utils.coordUtils.coord_conv`: Convert between geographic, 
        AACGM, and MLT coordinates
    * :func:`utils.coordUtils.planeRot`: Rotate coordinates in the plane

Written by Matt W.
"""
def coordConv(lon, lat, altitude, start, end, dateTime=None):
    """coordConv has been renamed coord_conv, and dateTime has been 
        renamed date_time for PEP 8 compliance.  Please use those 
        from now on.
    """
    from utils.coordUtils import coord_conv
    print "coordConv has been renamed coord_conv, and dateTime has"
    print "been renamed date_time for PEP 8 compliance.  Please use"
    print "those from now on."
    return coord_conv(lon, lat, altitude, start, end, date_time=dateTime)

def coord_conv(lon, lat, altitude, start, end, date_time=None):
    """Convert between geographical, AACGM, and MLT coordinates.  
        dateTime must be set to use any AACGM systems.
  
    **Args**: 
        * **lon**: longitude (MLT must be in degrees, not hours)
        * **lat**: latitude
        * **altitude**: altitude to be used (km).
        * **start**: coordinate system of input. Options: 'geo', 'mag',
            'mlt'
        * **end**: desired output coordinate system. Options: 'geo', 
            'mag', 'mlt'
        * **[date_time]**: python datetime object. Default: None
    **Returns**:
        * **lon, lat**: (float, list, or numpy array) MLT is in degrees, not
            hours.  Output type is the same as input type (except int becomes
            float)
    **Example**:
        ::
        import utils
        lon, lat = utils.coord_conv(lon, lat, 'geo', 'mlt', 
                             date_time=datetime(2012,3,12,0,56))
        
    original version written by Matt W., 2013-09 based on code by...Sebastien?
    brand new version by Matt W., 2014-08
    """
    import numpy as np
    
    from models import aacgm

    # Define acceptable coordinate systems.
    coords_dict = {"mag": "AACGM",
                   "geo": "Geographic",
                   "mlt": "MLT"}
    
    # List all systems that use AACGM.
    aacgm_sys = ["mag", "mlt"]

    # Create a string of these for printing to the terminal.
    for num, sys in enumerate(aacgm_sys):
        if num == 0:
            aacgm_string = coords_dict[sys] + " (" + sys + ")"
        elif num < len(aacgm_sys) - 1:
            aacgm_string = aacgm_string + ", " + coords_dict[sys] + " (" +\
                    sys + ")"
        elif len(aacgm_sys) < 3:
            aacgm_string = aacgm_string + " or " + coords_dict[sys] + " (" +\
                    sys + ")"
        else:
            aacgm_string = aacgm_string + ", or " + coords_dict[sys] + " (" +\
                    sys + ")"

    # Check that the coordinates are possible.
    if end not in coords_dict:
        print "Invalid end coordinate system given ({}):"
        print "setting 'mag'".format(end)
        end = "mag"
    if start not in coords_dict:
        print "Invalid start coordinate system given ({}):"
        print "setting '{}'".format(start,end)
        start = end 
    
    # AACGM systems require a datetime.
    if start in aacgm_sys or end in aacgm_sys:
        assert(date_time is not None),\
                "date_time must be provided for " + aacgm_string

    # Sanitise inputs.
    if isinstance(lon, int):
        lon = float(lon)
        lat = float(lat)
    is_list = isinstance(lon, (list, tuple))
    is_float = isinstance(lon, float)
    if is_float:
        lon = [lon]
        lat = [lat]
    if not (is_float or is_list):
        assert(isinstance(lon, np.ndarray)),\
                "Must input int, float, list, or numpy array."

    # Make the inputs into numpy arrays because single element lists 
    # have no len.
    lon, lat = np.array(lon), np.array(lat)
    shape = np.shape(lon)

    # Test whether we are using the same altitude for everything.
    alt = np.array(altitude)
    if np.size(alt) == 1:
        altitude = [altitude]*np.size(lon)

    # Check whether there is a conversion to do.
    if start != end:

        # Handle conversions from AACGM systems.
        if start in aacgm_sys:

            # Convert all other AACGM systems to AACGM.

            # Convert MLT to AACGM
            if start == "mlt":
                # Convert MLT from degrees to hours.
                lon *= 24./360.
                # Sanitise for later.
                lon %= 24.
                # Find MLT of 0 magnetic lon.
                mlt_0 = aacgm.mltFromYmdhms(date_time.year, date_time.month,
                                            date_time.day, date_time.hour,
                                            date_time.minute, date_time.second,
                                            0.)     
                # Calculate MLT difference, which is magnetic lon in hours.
                lon -= mlt_0
                # Sanitise and convert to degrees.
                lon %= 24.
                lon *= 360./24.
                # Covert from (0,360) to (-180,180).
                lon[np.where(lon > 180.)] -= 360.
                start = "mag"
        
            # Now it is in AACGM.  
            assert(start == "mag"),"Error, should be in AACGM now"

            # If the end result is not an AACGM system, convert to geo.
            if end not in aacgm_sys:
                lat, lon, _ = aacgm.aacgmConvArr(list(lat.flatten()), 
                                                list(lon.flatten()), altitude,
                                                date_time.year,1)
                lon = np.array(lon).reshape(shape)
                lat = np.array(lat).reshape(shape)
                start = "geo"

    # Now it is in:
    # AACGM if the end is also an AACGM system
    # geo if the end is not an AACGM system

    # Check whether there is still a conversion to do.
    if start != end:

        # Handle conversions to AACGM systems.
        if end in aacgm_sys:
            # If it isn't in AACGM already it's in geo.
            if start == "geo":
                lat, lon, _ = aacgm.aacgmConvArr(list(lat.flatten()), 
                                                list(lon.flatten()), altitude,
                                                date_time.year,0)
                lon = np.array(lon).reshape(shape)
                lat = np.array(lat).reshape(shape)
                start = "mag"

            # It is in AACGM now.
            assert(start == "mag"),"Error, should be in AACGM now"

            # Convert AACGM to all other AACGM systems.

            # Handle conversions to MLT.
            if end == "mlt":
                for num, el in enumerate(lon):
                    # Find MLT from magnetic lon and datetime.
                    lon[num] = aacgm.mltFromYmdhms(date_time.year, 
                                                   date_time.month, 
                                                   date_time.day, 
                                                   date_time.hour, 
                                                   date_time.minute, 
                                                   date_time.second, 
                                                   el)
                # Convert hours to degrees.
                lon *= 360./24.
                # Convert from (0,360) to (-180,180).
                lon[np.where(lon > 180.)] -= 360.
                start = "mlt"

    # Now it should be in the end system.
    assert(start == end),"Error, not in correct end system...?????"

    # Convert outputs to input type.
    if is_list:
        lon = list(lon.flatten())
        lat = list(lat.flatten())
    elif is_float:
        lon = list(lon.flatten())[0]
        lat = list(lat.flatten())[0]
    # Otherwise it stays a numpy array.

    return lon, lat


def planeRot(x, y, theta):
    """Rotate coordinates in the plane.
  
    **Args**: 
        * **x**: x coordinate
        * **y**: y coordinate
        * **theta**: angle of rotation of new coordinate frame
    **Returns**:
        * **x_prime,y_prime**: x, y coordinates in rotated frame
    **Example**:
        ::
        import numpy as np
        x, y = planeRot(x, y, 30.*np.pi/180.)
        
    written by Matt W., 2013-09
    """
    import numpy as np

    oldx, oldy = np.array(x), np.array(y)

    x = oldx*np.cos(theta) + oldy*np.sin(theta)
    y = -oldx*np.sin(theta) + oldy*np.cos(theta)

    return x, y


# Some testing stuff.
if __name__ == "__main__":
    from datetime import datetime
    import numpy

    print
    print "All of these results may have varying sigfigs."
    print "The expected values were found on a 32-bit system."
    print
    print "Test of redirection function coordConv"
    print coordConv(50.7, 34.5, 300., "geo", "geo")
    print
    print "Single coord pair tests"
    print
    print "Test of list -> list"
    print "Expected:  ([50.700000000000003], [34.5])"
    print "Result:    " + str(coord_conv([50.7],[34.5],300.,'geo','geo'))
    print
    print "Test of float -> float"
    print "Expected:  (50.700000000000003, 34.5)"
    print "Result:    " + str(coord_conv(50.7,34.5,300.,'geo','geo'))
    print
    print "Test of int -> float"
    print "Expected:  (50.0, 34.0)"
    print "Result:    " + str(coord_conv(50,34,300.,'geo','geo'))
    print
    print "Test of numpy array -> numpy array"
    print "Expected:  (array([ 50.7]), array([ 34.5]))"
    print "Result:    " + str(coord_conv(numpy.array([50.7]),numpy.array([34.5]),300.,'geo','geo'))
    print
    print "geo to geo, mag to mag, mlt to mlt, ashes to ashes"
    print "Expected:  (50.700000000000003, 34.5)"
    print "Result:    " + str(coord_conv(50.7,34.5,300.,'geo','geo'))
    print "Result:    " + str(coord_conv(50.7,34.5,300.,'mag','mag',date_time=datetime(2013,7,23,12,6,34)))
    print "Result:    " + str(coord_conv(50.7,34.5,300.,'mlt','mlt',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "geo to mag"
    print "Expected: (123.71642616363432, 31.582924632749929)"
    print "Result:   " + str(coord_conv(50.7,34.5,300.,'geo','mag',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "geo to mlt"
    print "Expected: (-130.65999038625603, 31.582924632749929)"
    print "Result:   " + str(coord_conv(50.7,34.5,300.,'geo','mlt',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "mag to geo"
    print "Expected: (50.563320914903102, 32.408924471374895)"
    print "Result:   " + str(coord_conv(123.53805352405843,29.419420613372086,300.,'mag','geo',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "mlt to geo"
    print "Expected: (50.563320914903137, 32.408924471374895)"
    print "Result:   " + str(coord_conv(229.16163697416806,29.419420613372086,300.,'mlt','geo',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "mag to mlt"
    print "Expected: (-130.83836302583194, 29.419420613372086)"
    print "Result:   " + str(coord_conv(123.53805352405843,29.419420613372086,300.,'mag','mlt',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "mlt to mag"
    print "Expected: (123.53805352405843, 29.419420613372086)"
    print "Result:   " + str(coord_conv(229.16163697416806,29.419420613372086,300.,'mlt','mag',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "Coord array tests"
    print
    print "geo to geo, mag to mag, mlt to mlt"
    print "Expected: ([50.700000000000003, 53.799999999999997], [34.5, 40.200000000000003])"
    print "Result    " + str(coord_conv([50.7,53.8],[34.5,40.2],300.,'geo','geo'))
    print "Result    " + str(coord_conv([50.7,53.8],[34.5,40.2],300.,'mag','mag',date_time=datetime(2013,7,23,12,6,34)))
    print "Result    " + str(coord_conv([50.7,53.8],[34.5,40.2],300.,'mlt','mlt',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "geo to mag"
    print "Expected: ([123.65800072339718, 126.97463420949806], [30.892913121194589, 37.369211032553089])"
    print "Result    " + str(coord_conv([50.7,53.8],[34.5,40.2],[200.,300.],'geo','mag',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "geo to mlt"
    print "Expected: ([-130.71841582649319, -127.40178234039229], [30.892913121194589, 37.369211032553089])"
    print "Result    " + str(coord_conv([50.7,53.8],[34.5,40.2],[200.,300.],'geo','mlt',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "mag to geo"
    print "Expected: ([50.615511474515607, 53.648287906901672], [33.150771171950133, 38.637420715148586])"
    print "Result    " + str(coord_conv([123.53805352405843, 126.76454464467615],[29.419420613372086, 35.725172012254788],[200.,300.],'mag','geo',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "mlt to geo"
    print "Expected: ([50.563320914903137, 53.648287906901672], [32.408924471374895, 38.637420715148586])"
    print "Result    " + str(coord_conv([229.16163697416806, 232.38812809478577], [29.419420613372086, 35.725172012254788],300.,'mlt','geo',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "mag to mlt"
    print "Expected: ([-130.83836302583194, -127.61187190521423], [29.419420613372086, 35.725172012254788])"
    print "Result    " + str(coord_conv([123.53805352405843, 126.76454464467615],[29.419420613372086, 35.725172012254788],300.,'mag','mlt',date_time=datetime(2013,7,23,12,6,34)))
    print
    print "mlt to mag"
    print "Expected: ([123.53805352405843, 126.76454464467615], [29.419420613372086, 35.725172012254788])"
    print "Result    " + str(coord_conv([229.16163697416806, 232.38812809478577], [29.419420613372086, 35.725172012254788],200.,'mlt','mag',date_time=datetime(2013,7,23,12,6,34)))
    print
