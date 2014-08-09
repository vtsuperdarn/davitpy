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
  * :func:`utils.coordUtils.coordConv`: Convert between geographic, 
        AACGM, and MLT coordinates
  * :func:`utils.coordUtils.planeRot`: Rotate coordinates in the plane

Written by Matt W. based on code by...Sebastien?
"""


def coordConv(lon, lat, start, end, dateTime=None):
    """Convert between geographical, AACGM, and MLT coordinates.  
        dateTime must be set to use any AACGM systems.
  
    **Args**: 
        * **lon**: longitude (MLT must be in degrees, not hours)
        * **lat**: latitude
        * **start**: coordinate system of input. Options: 'geo', 'mag',
            'mlt'
        * **end**: desired output coordinate system. Options: 'geo', 
            'mag', 'mlt'
        * **[dateTime]**: python datetime object. Default: None
    **Returns**:
        * **lon,lat**: lists
    **Example**:
        ::
    
        lon, lat = coordConv(lon, lat, 'geo', 'mlt', 
                             dateTime=datetime(2012,3,12,0,56))
        
    written by Matt W., 2013-09 based on code by...Sebastien?
    """
    import numpy as np
    
    from models import aacgm

    date_time = dateTime

    # Define acceptable coordinate systems.
    coords_dict = {"mag": "AACGM",
                   "geo": "Geographic",
                   "mlt": "MLT"}
    
    # Check that the coordinates are possible.
    if end and end not in coords_dict:
        print "Invalid end coordinate system given ({}):"
        print "setting 'mag'".format(end)
        end = "mag"
    if start and start not in coords_dict:
        print "Invalid start coordinate system given ({}):"
        print "setting '{}'".format(start,end)
        start = end 
    
    # MLT requires a datetime.
    if start == "mlt" or end == "mlt": 
        assert(date_time is not None),\
                "date_time must be provided for MLT coordinates to work."
    # Mag requires a datetime.
    if start == 'mag' or end == 'mag': 
        assert(date_time is not None),\
                "date_time must be provided for MAG coordinates to work."

    # Make the inputs into numpy arrays because single element lists 
    # have no len.
    lon = np.array(lon)
    lat = np.array(lat)

    # If there is an actual conversion to do:
    if start and end and start != end:
        # Set the conversion specifier.
        trans = start+'-'+end

        # Geographical and AACGM conversions:
        if trans in ['geo-mag','mag-geo']:
            flag = 0 if trans == 'geo-mag' else 1
            lont = lon
            latt = lat
            nlon, nlat = np.size(lont), np.size(latt)
            shape = lont.shape
            lat, lon, _ = aacgm.aacgmConvArr(list(latt.flatten()), 
                                             list(lont.flatten()), [0.]*nlon, 
                                             date_time.year,flag)
            lon = np.array(lon).reshape(shape)
            lat = np.array(lat).reshape(shape)

        # Geographical and MLT conversions:
        elif trans in ['geo-mlt','mlt-geo']:
            flag = 0 if trans == 'geo-mlt' else 1
            if flag:
                latt = lat
                lon_mlt = lon
                shape = lon_mlt.shape
                nlon, nlat = np.size(lon_mlt), np.size(latt)
                lon_mag = []
                # Find MLT at zero mag lon.
                mlt_0 = aacgm.mltFromYmdhms(date_time.year,date_time.month,
                                            date_time.day, date_time.hour,
                                            date_time.minute, date_time.second,
                                            0.)
                for el in range(nlon):
                    # Convert input mlt from degrees to hours.
                    mlt = lon_mlt.flatten()[el]*24./360.%24.
                    # Calculate mag lon.
                    mag = (mlt - mlt_0)*15.%360.
                    # Put in -180 to 180 range.
                    if mag > 180.: mag -= 360.
                    # Stick on end of the list.
                    lon_mag.append(mag)
                # Make into a numpy array.
                lont = np.array(lon_mag).reshape(shape)
                # Convert mag to geo.
                lat, lon, _ = aacgm.aacgmConvArr(list(latt.flatten()), 
                                                 list(lont.flatten()), 
                                                 [0.]*nlon, date_time.year, 
                                                 flag)
                # Make into numpy arrays.
                lon = np.array(lon).reshape(shape)
                lat = np.array(lat).reshape(shape)
            else:
                # MLT list.
                lon_mlt = []
                lont = lon
                latt = lat
                nlon, nlat = np.size(lont), np.size(latt)
                shape = lont.shape
                # Convert geo to mag.
                lat, lon, _ = aacgm.aacgmConvArr(list(latt.flatten()), 
                                                 list(lont.flatten()), 
                                                 [0.]*nlon, date_time.year, 
                                                 flag)
                for lonel in range(nlon):
                    # Get MLT from mag lon.
                    mlt = aacgm.mltFromYmdhms(date_time.year,date_time.month,
                                              date_time.day, date_time.hour,
                                              date_time.minute,
                                              date_time.second, lon[lonel]) 
                    # Convert hours to degrees.
                    lon_mlt.append(mlt/24.*360.)
                # Make into numpy arrays.
                lon = np.array(lon_mlt).reshape(shape)
                lat = np.array(lat).reshape(shape)

        # Magnetic and MLT conversions:
        elif trans in ['mag-mlt','mlt-mag']:
            flag = 0 if trans == 'mag-mlt' else 1
            if flag:
                lon_mag=[]
                lon_mlt = lon
                nlon = np.size(lon_mlt)
                shape = lon_mlt.shape
                # Find MLT of zero mag lon.
                mlt_0 = aacgm.mltFromYmdhms(date_time.year, date_time.month,
                                            date_time.day, date_time.hour,
                                            date_time.minute, date_time.second,
                                            0.)     
                for el in range(nlon):
                    # Convert MLT from degrees to hours.
                    mlt = lon_mlt.flatten()[el]*24./360.%24.
                    # Calculate mag lon from MLT.
                    mag = (mlt - mlt_0)*15.%360.
                    # Put in -180 to 180 range.
                    if mag > 180.: mag -= 360.
                    lon_mag.append(mag)
                lon = np.array(lon_mag).reshape(shape)
                lat = lat.reshape(shape)
            else:
                lon_mlt = []
                lont = lon
                nlon = np.size(lont)
                shape=lont.shape
                for lonel in range(nlon):
                    # Find MLT from mag lon and datetime.
                    mlt = aacgm.mltFromYmdhms(date_time.year, date_time.month,
                            date_time.day, date_time.hour, date_time.minute,
                            date_time.second, lont.flatten()[lonel])
                    # Convert hours to degrees.
                    lon_mlt.append(mlt/24.*360.)
                lon = np.array(lon_mlt).reshape(shape)
                lat = lat.reshape(shape)
        
    return list(lon.flatten()), list(lat.flatten())

########################################################################
########################################################################

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

    print "All of these results may have varying sigfigs"

    print "Single coord pair tests"
    print "geo to geo, mag to mag, mlt to mlt, ashes to ashes; these results should be ([50.7],[34.5])"
    print coordConv(50.7,34.5,'geo','geo')
    print coordConv(50.7,34.5,'mag','mag',dateTime=datetime(2013,7,23,12,6,34))
    print coordConv(50.7,34.5,'mlt','mlt',dateTime=datetime(2013,7,23,12,6,34))
    print "geo to mag, this result should be ([123.53805352405843], [29.419420613372086])"
    print coordConv(50.7,34.5,'geo','mag',dateTime=datetime(2013,7,23,12,6,34))
    print "geo to mlt, this result should be ([229.16163697416806], [29.419420613372086])"
    print coordConv(50.7,34.5,'geo','mlt',dateTime=datetime(2013,7,23,12,6,34))
    print "mag to geo, this result should be ([50.7],[34.5])"
    print coordConv(123.53805352405843,29.419420613372086,'mag','geo',dateTime=datetime(2013,7,23,12,6,34))
    print "mlt to geo, this result should be ([50.7,34.5])"
    print coordConv(229.16163697416806,29.419420613372086,'mlt','geo',dateTime=datetime(2013,7,23,12,6,34))
    print "mag to mlt, this result should be ([229.16163697416806], [29.419420613372086])"

    print coordConv(123.53805352405843,29.419420613372086,'mag','mlt',dateTime=datetime(2013,7,23,12,6,34))
    print "mlt to mag, this result should be ([123.53805352405843], [29.419420613372086])"

    print coordConv(229.16163697416806,29.419420613372086,'mlt','mag',dateTime=datetime(2013,7,23,12,6,34))

    print "Coord array tests"
    print "geo to geo, mag to mag, mlt to mlt; these results should be ([50.7,53.8],[34.5,40.2])"
    print coordConv([50.7,53.8],[34.5,40.2],'geo','geo')
    print coordConv([50.7,53.8],[34.5,40.2],'mag','mag',dateTime=datetime(2013,7,23,12,6,34))
    print coordConv([50.7,53.8],[34.5,40.2],'mlt','mlt',dateTime=datetime(2013,7,23,12,6,34))
    print "geo to mag, this result should be ([123.53805352405843, 126.76454464467615], [29.419420613372086, 35.725172012254788])"
    print coordConv([50.7,53.8],[34.5,40.2],'geo','mag',dateTime=datetime(2013,7,23,12,6,34))
    print "geo to mlt, this result should be ([229.16163697416806, 232.38812809478577], [29.419420613372086, 35.725172012254788])"
    print coordConv([50.7,53.8],[34.5,40.2],'geo','mlt',dateTime=datetime(2013,7,23,12,6,34))
    print "mag to geo, this result should be ([50.7,53.8],[34.5,40.2])"
    print coordConv([123.53805352405843, 126.76454464467615],[29.419420613372086, 35.725172012254788],'mag','geo',dateTime=datetime(2013,7,23,12,6,34))
    print "mlt to geo, this result should be ([50.7,53.8],[34.5,40.2])"
    print coordConv([229.16163697416806, 232.38812809478577], [29.419420613372086, 35.725172012254788],'mlt','geo',dateTime=datetime(2013,7,23,12,6,34))
    print "mag to mlt, this result should be ([229.16163697416806, 232.38812809478577], [29.419420613372086, 35.725172012254788])"

    print coordConv([123.53805352405843, 126.76454464467615],[29.419420613372086, 35.725172012254788],'mag','mlt',dateTime=datetime(2013,7,23,12,6,34))
    print "mlt to mag, this result should be ([123.53805352405843, 126.76454464467615], [29.419420613372086, 35.725172012254788])"

    print coordConv([229.16163697416806, 232.38812809478577], [29.419420613372086, 35.725172012254788],'mlt','mag',dateTime=datetime(2013,7,23,12,6,34))
