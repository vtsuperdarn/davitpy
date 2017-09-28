# -*- coding: utf-8 -*-
'''Pythonic wrappers for AACGM-V2 C functions.

Functions
--------------
convert_latlon
convert_latlon_arr
get_aacgm_coord
get_aacgm_coord_arr
convert_str_to_bit
--------------
'''

from __future__ import division, print_function, absolute_import
from __future__ import unicode_literals
import numpy as np
import datetime as dt
import logging


def convert_latlon(in_lat, in_lon, height, dtime, code="G2A", igrf_file=None,
                   coeff_prefix=None):
    '''Converts between geomagnetic coordinates and AACGM coordinates

    Parameters
    ------------
    in_lat : (float)
        Input latitude in degrees N (code specifies type of latitude)
    in_lon : (float)
        Input longitude in degrees E (code specifies type of longitude)
    height : (float)
        Altitude above the surface of the earth in km
    dtime : (datetime)
        Datetime for magnetic field
    code : Optional[str]
        String denoting which type(s) of conversion to perform
        G2A        - geographic (geodetic) to AACGM-v2
        A2G        - AACGM-v2 to geographic (geodetic)
        TRACE      - use field-line tracing, not coefficients
        ALLOWTRACE - use trace only above 2000 km
        BADIDEA    - use coefficients above 2000 km
        GEOCENTRIC - assume inputs are geocentric w/ RE=6371.2
        (default is "G2A")
    igrf_file : Optional[str]
        Full filename of IGRF coefficient file or None to use
        rcParams["IGRF_DAVITPY_COEFF_FILE"]. (default=None)
    coeff_prefix : Optional[str]
        Location and file prefix for aacgm coefficient files or None to use
        rcParams["AACGM_DAVITPY_DAT_PREFEX"]. (default=None)

    Returns
    -------
    out_lat : (float)
        Output latitude in degrees
    out_lon : (float)
        Output longitude in degrees
    out_r : (float)
        Geocentric radial distance in R
    '''
    from davitpy import rcParams
    from davitpy.models import aacgm

    # Define coefficient file prefix if not supplied
    if coeff_prefix is None:
        coeff_prefix = rcParams['AACGM_DAVITPY_DAT_PREFIX']

    # Define IGRF file if not supplied
    if igrf_file is None:
        igrf_file = rcParams['IGRF_DAVITPY_COEFF_FILE']

    # Test time
    if isinstance(dtime, dt.date):
        date = dt.datetime.combine(dtime, dt.time(0))

    assert isinstance(dtime, dt.datetime), \
        logging.error('time must be specified as datetime object')

    # Test height
    if height < 0:
        logging.warn('conversion not intended for altitudes < 0 km')

    # Test code
    code = code.upper()

    if(height > 2000 and code.find("TRACE") < 0 and
       code.find("ALLOWTRACE") < 0 and code.find("BADIDEA")):
        estr = 'coefficients are not valid for altitudes above 2000 km. You '
        estr += 'must either use field-line tracing (trace=True '
        estr += 'or allowtrace=True) or indicate you know this '
        estr += 'is a bad idea'
        logging.error(estr)

    # Test latitude range
    if abs(in_lat) > 90.0:
        assert abs(in_lat) <= 90.1, logging.error('unrealistic latitude')
        in_lat = np.sign(in_lat) * 90.0

    # Constrain longitudes between -180 and 180
    in_lon = ((in_lon + 180.0) % 360.0) - 180.0

    # Set current date and time
    aacgm.set_datetime(dtime.year, dtime.month, dtime.day, dtime.hour,
                       dtime.minute, dtime.second, coeff_prefix)

    # make flag
    bit_code = convert_str_to_bit(code)

    # convert
    lat_out, lon_out, r_out = aacgm.convert(in_lat, in_lon, height, bit_code,
                                            igrf_file)

    return lat_out, lon_out, r_out


def convert_latlon_arr(in_lat, in_lon, height, dtime, code="G2A",
                       igrf_file=None, coeff_prefix=None):
    '''Converts between geomagnetic coordinates and AACGM coordinates

    Parameters
    ------------
    in_lat : (np.ndarray)
        Input latitude in degrees N (code specifies type of latitude)
    in_lon : (np.ndarray)
        Input longitude in degrees E (code specifies type of longitude)
    height : (np.ndarray)
        Altitude above the surface of the earth in km
    dtime : (datetime)
        Single datetime object for magnetic field
    code : Optional[str]
        String denoting which type(s) of conversion to perform
        G2A        - geographic (geodetic) to AACGM-v2
        A2G        - AACGM-v2 to geographic (geodetic)
        TRACE      - use field-line tracing, not coefficients
        ALLOWTRACE - use trace only above 2000 km
        BADIDEA    - use coefficients above 2000 km
        GEOCENTRIC - assume inputs are geocentric w/ RE=6371.2
        (default = "G2A")
    igrf_file : Optional[str]
        Full filename of IGRF coefficient file or None to use
        rcParams["IGRF_DAVITPY_COEFF_FILE"]. (default=None)
    coeff_prefix : Optional[str]
        Location and file prefix for aacgm coefficient files or None to use
        rcParams["AACGM_DAVITPY_DAT_PREFEX"]. (default=None)

    Returns
    -------
    out_lat : (np.ndarray)
        Output latitudes in degrees
    out_lon : (np.ndarray)
        Output longitudes in degrees
    out_r : (np.ndarray)
        Geocentric radial distances in R
    '''
    from davitpy import rcParams
    from davitpy.models import aacgm
    import numpy as np

    # If someone was lazy and entered a list instead of a numpy array,
    # recast it here

    if isinstance(in_lat, list):
        in_lat = np.array(in_lat)

    if isinstance(in_lon, list):
        in_lon = np.array(in_lon)

    if isinstance(height, list):
        height = np.array(height)

    # Ensure that lat, lon, and height are the same length or if the lengths
    # differ that the different ones contain only a single value
    ulen = np.unique([height.shape, in_lat.shape, in_lon.shape])
    if ulen.shape[0] > 2 or (ulen.shape[0] == 2 and ulen[0] > 1):
        logging.error("mismatched input arrays")
        return None, None, None

    # Define coefficient file prefix if not supplied
    if coeff_prefix is None:
        coeff_prefix = rcParams['AACGM_DAVITPY_DAT_PREFIX']

    # Define IGRF file if not supplied
    if igrf_file is None:
        igrf_file = rcParams['IGRF_DAVITPY_COEFF_FILE']

    # Test time
    if isinstance(dtime, dt.date):
        date = dt.datetime.combine(dtime, dt.time(0))

    assert isinstance(dtime, dt.datetime), \
        logging.error('time must be specified as datetime object')

    # Test height
    if np.min(height) < 0:
        logging.warn('conversion not intended for altitudes < 0 km')

    # Test code
    code = code.upper()

    if(np.max(height) > 2000 and code.find("TRACE") < 0 and
       code.find("ALLOWTRACE") < 0 and code.find("BADIDEA")):
        estr = 'coefficients are not valid for altitudes above 2000 km. You '
        estr += 'must either use field-line tracing (trace=True '
        estr += 'or allowtrace=True) or indicate you know this '
        estr += 'is a bad idea'
        logging.error(estr)

    # Test latitude range
    if np.abs(in_lat).max() > 90.0:
        assert np.abs(in_lat).max() <= 90.1, \
            logging.error('unrealistic latitude')
        in_lat = np.clip(in_lat, -90.0, 90.0)

    # Constrain longitudes between -180 and 180
    in_lon = ((in_lon + 180.0) % 360.0) - 180.0

    # Set current date and time
    aacgm.set_datetime(dtime.year, dtime.month, dtime.day, dtime.hour,
                       dtime.minute, dtime.second, coeff_prefix)

    # make flag
    bit_code = convert_str_to_bit(code)

    # Vectorise the AACGM code
    convert_vectorised = np.vectorize(aacgm.convert)

    # convert
    lat_out, lon_out, r_out = convert_vectorised(in_lat, in_lon, height,
                                                 bit_code, igrf_file)

    return lat_out, lon_out, r_out


def get_aacgm_coord(glat, glon, height, dtime, method="TRACE",
                    igrf_file=None, coeff_prefix=None):
    '''Get AACGM latitude, longitude, and magnetic local time

    Parameters
    ------------
    glat : (float)
        Geodetic latitude in degrees N
    glon : (float)
        Geodetic longitude in degrees E
    height : (float)
        Altitude above the surface of the earth in km
    dtime : (datetime)
        Date and time to calculate magnetic location
    method : Optional[str]
        String denoting which type(s) of conversion to perform
        TRACE      - use field-line tracing, not coefficients
        ALLOWTRACE - use trace only above 2000 km
        BADIDEA    - use coefficients above 2000 km
        GEOCENTRIC - assume inputs are geocentric w/ RE=6371.2
        (default = "TRACE")
    igrf_file : Optional[str]
        Full filename of IGRF coefficient file or None to use
        rcParams["IGRF_DAVITPY_COEFF_FILE"]. (default=None)
    coeff_prefix : Optional[str]
        Location and file prefix for aacgm coefficient files or None to use
        rcParams["AACGM_DAVITPY_DAT_PREFEX"]. (default=None)

    Returns
    -------
    mlat : (float)
        magnetic latitude in degrees
    mlon : (float)
        magnetic longitude in degrees
    mlt : (float)
        magnetic local time in hours
    '''
    from davitpy import rcParams
    from davitpy.models import aacgm

    # Define coefficient file prefix if not supplied
    if coeff_prefix is None:
        coeff_prefix = rcParams['AACGM_DAVITPY_DAT_PREFIX']

    # Define IGRF file if not supplied
    if igrf_file is None:
        igrf_file = rcParams['IGRF_DAVITPY_COEFF_FILE']

    # Initialize return values
    mlat = None
    mlon = None
    mlt = None

    try:
        # Get magnetic lat and lon.
        mlat, mlon, mr = convert_latlon(glat, glon, height, dtime,
                                        code="G2A|{:s}".format(method),
                                        igrf_file=igrf_file,
                                        coeff_prefix=coeff_prefix)
        # Get magnetic local time
        mlt = aacgm.mlt_convert(dtime.year, dtime.month, dtime.day, dtime.hour,
                                dtime.minute, dtime.second, mlon, coeff_prefix,
                                igrf_file)
    except:
        logging.error("Unable to get magnetic lat/lon")

    return mlat, mlon, mlt


def get_aacgm_coord_arr(glat, glon, height, dtime, method="TRACE",
                        igrf_file=None, coeff_prefix=None):
    '''Get AACGM latitude, longitude, and magnetic local time

    Parameters
    ------------
    glat : (np.array or list)
        Geodetic latitude in degrees N
    glon : (np.array or list)
        Geodetic longitude in degrees E
    height : (np.array or list)
        Altitude above the surface of the earth in km
    dtime : (datetime)
        Date and time to calculate magnetic location
    method : Optioanl[str]
        String denoting which type(s) of conversion to perform
        TRACE      - use field-line tracing, not coefficients
        ALLOWTRACE - use trace only above 2000 km
        BADIDEA    - use coefficients above 2000 km
        GEOCENTRIC - assume inputs are geocentric w/ RE=6371.2
        (default = "TRACE")
    igrf_file : Optional[str]
        Full filename of IGRF coefficient file or None to use
        rcParams["IGRF_DAVITPY_COEFF_FILE"]. (default=None)
    coeff_prefix : Optional[str]
        Location and file prefix for aacgm coefficient files or None to use
        rcParams["AACGM_DAVITPY_DAT_PREFEX"]. (default=None)

    Returns
    -------
    mlat : (float)
        magnetic latitude in degrees
    mlon : (float)
        magnetic longitude in degrees
    mlt : (float)
        magnetic local time in hours
    '''
    from davitpy import rcParams
    from davitpy.models import aacgm
    import numpy as np

    # Define coefficient file prefix if not supplied
    if coeff_prefix is None:
        coeff_prefix = rcParams['AACGM_DAVITPY_DAT_PREFIX']

    # Define IGRF file if not supplied
    if igrf_file is None:
        igrf_file = rcParams['IGRF_DAVITPY_COEFF_FILE']

    # Initialize return values
    mlat = None
    mlon = None
    mlt = None

    try:
        # Get magnetic lat and lon.
        mlat, mlon, mr = convert_latlon_arr(glat, glon, height, dtime,
                                            code="G2A|{:s}".format(method),
                                            igrf_file=igrf_file,
                                            coeff_prefix=coeff_prefix)

        if mlon is not None:
            # Get magnetic local time
            mlt_vectorised = np.vectorize(aacgm.mlt_convert)
            mlt = mlt_vectorised(dtime.year, dtime.month, dtime.day,
                                 dtime.hour, dtime.minute, dtime.second, mlon,
                                 coeff_prefix, igrf_file)
    except:
        logging.error("Unable to get magnetic lat/lon")

    return mlat, mlon, mlt


def convert_str_to_bit(code):
    '''convert string code specification to bit code specification

    Parameters
    code : (str)
        Bitwise code for passing options into converter (default=0)
        G2A        - geographic (geodetic) to AACGM-v2
        A2G        - AACGM-v2 to geographic (geodetic)
        TRACE      - use field-line tracing, not coefficients
        ALLOWTRACE - use trace only above 2000 km
        BADIDEA    - use coefficients above 2000 km
        GEOCENTRIC - assume inputs are geocentric w/ RE=6371.2
    '''
    from davitpy.models import aacgm

    convert_code = {"G2A": aacgm.G2A, "A2G": aacgm.A2G, "TRACE": aacgm.TRACE,
                    "GEOCENTRIC": aacgm.GEOCENTRIC,
                    "ALLOWTRACE": aacgm.ALLOWTRACE, "BADIDEA": aacgm.BADIDEA}

    code = code.upper()

    bit_code = sum([convert_code[k] for k in convert_code.keys()
                    if code.find(k) >= 0])

    return bit_code
