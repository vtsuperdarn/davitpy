"""
*******************************
MODULE: models.tsyganenko.trace
*******************************

This module contains the following functions:

  trace

This module contains the following classes:

  aClass
    
*******************************
"""


def trace(lat, lon, rho, coords='geo', datetime=None, 
        vswgse=[-400.,0.,0.], pdyn=2., dst=-5., byimf=0., bzimf=-5.
        lmax=5000, rmax=60., rmin=1., dsmax=0.01, err=0.000001):
    """
|   **PACKAGE**: models.tsyganenko.trace
|   **FUNCTION**: trace(lat, lon, rho, coords='geo', datetime=None, 
|        vswgse=[-400.,0.,0.], Pdyn=2., Dst=-5., ByIMF=0., BzIMF=-5.
|        lmax=5000, rmax=60., rmin=1., dsmax=0.01, err=0.000001)
|   **PURPOSE**: trace magnetic field line(s) from point(s)
|
|   **INPUTS**:
|       **lat**: latitude [degrees]
|       **lon**: longitude [degrees]
|       **rho**: distance from center of the Earth [km]
|       **[coords]**: coordinates used for start point ['geo']
|       **[datetime]**: a python datetime object
|       **[vswgse]**: solar wind velocity in GSE coordinates [m/s, m/s, m/s]
|       **[pdyn]**: solar wind dynamic pressure [nPa]
|       **[dst]**: Dst index [nT]
|       **[byimf]**: IMF By [nT]
|       **[bzimf]**: IMF Bz [nT]
|       **[lmax]**: maximum number of points to trace
|       **[rmax]**: upper trace boundary in Re
|       **[rmin]**: lower trace boundary in Re
|       **[dsmax]**: maximum tracing step size
|       **[err]**: tracing step tolerance
|
|   **OUTPUTS**:
|       NONE
|   
|   **EXAMPLES**:
|       
|       
|   Written by Sebastien 20121005
    """
    from models.tsyganenko import tsygFort
    from numpy import radians, degrees
    from datetime import datetime as pydt
    
    # Declare the same Re as used in Tsyganenko models [km]
    Re = 6371.2
    
    assert (len(vswgse) == 3), 'vswgse must have 3 elements'
    assert (coords.lower() == 'geo'), '{}: this coordinae system is not supported'.format(coords.lower())
    
    # If no datetime is provided, defaults to today
    if not datetime: datetime = pydt.utcnow()

    # This has to be called first
    tsygFort.recalc_08(datetime.year,datetime.timetuple().tm_yday,
                            datetime.hour,datetime.minute,datetime.second,
                            vswgse[0],vswgse[1],vswgse[2])

    # A provision for those who want to batch trace
    try:
        [l for l in lat]
    except:
        lat = [lat]
    try:
        [l for l in lon]
    except:
        lon = [lon]
    try:
        [r for r in rho]
    except:
        rho = [rho]
    # Make sure they're all the sam elength
    assert (len(lat) == len(lon) == len(rho)), 'lat, lon and rho must me the same length'
    
    # And now iterate through the desired points
    for ip in xrange(len(lat)):
        # Convert lat,lon to geographic cartesian and then gsw
        r, theta, phi, xgeo, ygeo, zgeo = tsygFort.sphcar_08(
                                                rho[ip]/Re, radians(90.-lat[ip]), radians(lon[ip]), 
                                                0., 0., 0., 
                                                1)
        if coords.lower() == 'geo':
            xgeo, ygeo, zgeo, xgsw, ygsw, zgsw = tsygFort.geogsw_08(
                                                        xgeo, ygeo, zgeo,
                                                        0. ,0. ,0. ,
                                                        1)

        # Trace field line
        xfgsw, yfgsw, zfgsw, xarr, yarr, zarr, l = tsygFort.trace_08(
                                                        xgsw, ygsw, zgsw,
                                                        mapto, dsmax, err, 
                                                        rmax, rmin, 0,
                                                        [pdyn, dst, byimf, bzimf, 0, 0, 0, 0, 0, 0], 
                                                        'T96_01', 'IGRF_GSW_08',
                                                        lmax)

        # Convert back to spherical geographic coords
        xfgeo, yfgeo, zfgeo, xfgsw, yfgsw, zfgsw  = tsygFort.geogsw_08(
                                                            0. ,0. ,0. ,
                                                            xfgsw, yfgsw, zfgsw,
                                                            -1)
        geoR, geoColat, geoLon, xgeo, ygeo, zgeo = tsygFort.sphcar_08(
                                                            0., 0., 0., 
                                                            xfgeo, yfgeo, zfgeo, 
                                                            -1)
    
        # Get coordinates of traced point
        latTr = 90. - degrees(geoColat)
        lonTr = degrees(geoLon)
        rhoTr = geoR*Re
    
    
    