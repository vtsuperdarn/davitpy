#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------
# bscatter_distribution.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Functions that indicate how well backscatter fall about a specified
#           location
#-----------------------------------------------------------------------------
"""This module contains the functions that indicate how well backscatter fall
about a specified location

Functions
------------------------------------------------------------------------------
lat_distribution     Calculate the deviation about a specified latitude
vheight_distribution Calculate the deviation about a specified virtual height
distribution_min     Optimize distribution of backscatter about a specified
                     location
------------------------------------------------------------------------------

References
------------------------------------------------------------------------------
A.G. Burrell et al. (2016) submitted to Radio Science doi:xxx
------------------------------------------------------------------------------
"""
import numpy as np

#---------------------------------------------------------------------------
def lat_distribution(tdiff, ref_lat, hard, asep, phi_sign, ecor, phi0, phi0e,
                     fovflg, cos_phi, tfreq, bmnum, dist):
    '''Returns the squared sum of the difference between the mean and the
    specified latitude and the standard deviation of the backscatter latitudes

    Parameters
    -----------
    tdiff : (float)
        tdiff in microseconds
    ref_lat : (float)
        reference latitude in degrees
    hard : (class davitpy.pydarn.radar.radStruct.site)
        radar hardware data
    asep : (float)
        antenna seperation in m
    phi_sign : (float)
        states whether or not the interferometer is in front of the radar
    ecor : (float)
        correction to elevation angle based on interferometer alt
    phi0 : (list)
        phase lags in radians
    phi0e : (list)
        phase lag errors in radians
    fovflg : (list)
        field-of-view flags
    cos_phi : (list)
        cos of azimuthal angles
    tfreq : (list)
        transmission frequencies in kHz
    bmnum : (list)
        beam number
    dist : (list)
        slant distance from radar to ionospheric reflection point in km

    Returns
    ---------
    ff : (float)
        standard deviation of the latitude distribution

    Notes
    -------
    Calculates equation 3 in Burrell et al. (2016)
    '''
    import davitpy.utils.geoPack as geo
    import davitpy.pydarn.proc.fov.calc_elevation as celv
    # Ensure that TDIFF is a single number and not a list or array element
    try:
        len(tdiff)
        tdiff = tdiff[0]
    except:
        pass

    if not isinstance(tdiff, float):
        tdiff = float(tdiff)

    # Calculate the elevation and latitude
    try:
        # elevation is in radians
        elv = np.array(celv.calc_elv_list(phi0, phi0e, fovflg, cos_phi, tfreq,
                                          asep, ecor, phi_sign, tdiff)) 
        loc = geo.calcDistPnt(hard.geolat, hard.geolon, hard.alt,
                              az=hard.beamToAzim(np.array(bmnum)),
                              el=np.degrees(elv), dist=np.array(dist))
        lat = loc['distLat'][~np.isnan(loc['distLat'])] # Remove nan

        #--------------------------------------------------------------------
        # When the distribution is approximately gaussian, the error depends
        # on the location of the peak and the amount of spread.  Testing the
        # standard deviation prevents the formation of a bimodal distribution
        # who each flank the desired location
        #
        # Sum the errors
        ff = np.nan if len(lat) == 0 else np.sqrt((lat.mean() - ref_lat)**2 +
                                                  lat.std()**2)
    except:
        ff = np.nan

    # Return the square root of the summed squared errors
    return ff

#---------------------------------------------------------------------------
def vheight_distribution(tdiff, ref_height, radius, asep, phi_sign, ecor, phi0,
                         phi0e, fovflg, cos_phi, tfreq, dist):
    '''Returns the squared sum of the difference between the mean and the
    specified height and the standard deviation of the backscatter heights

    Parameters
    -----------
    tdiff : (float)
        tdiff in microseconds
    ref_height : (float)
        reference altitude in km
    radius : (float)
        earth radius in km
    asep : (float)
        antenna seperation in m
    phi_sign : (float)
        states whether or not the interferometer is in front of the radar
    ecor : (float)
        correction to elevation angle based on interferometer alt
    phi0 : (list)
        phase lags in radians
    phi0e : (list)
        phase lag errors in radians
    fovflg : (list)
        field-of-view flags
    cos_phi : (list)
        cos of azimuthal angles
    tfreq : (list)
        transmission frequencies in kHz
    dist : (list)
        slant distance from radar to ionospheric reflection point in km

    Returns
    ---------
    ff : (float)
        standard deviation of the height distribution

    Notes
    -------
    Calculates equation 3 in Burrell et al. (2016)
    '''
    import davitpy.pydarn.proc.fov.calc_elevation as celv
    
    # Ensure that TDIFF is a single number and not a list or array element
    try:
        len(tdiff)
        tdiff = tdiff[0]
    except:
        pass

    if not isinstance(tdiff, float):
        tdiff = float(tdiff)

    # Calculate the elevation and virtual height
    try:
        elv = celv.calc_elv_list(phi0, phi0e, fovflg, cos_phi, tfreq, asep,
                                 ecor, phi_sign, tdiff) # in radians
        heights = [np.sqrt(dd**2 + radius**2 + 2.0 * dd * radius *
                           np.sin(elv[di])) - radius
                   for di,dd in enumerate(dist)
                   if not np.isnan(dd) and not np.isnan(elv[di])] # in km

        #--------------------------------------------------------------------
        # When the distribution is approximately gaussian, the error depends
        # on the location of the peak and the amount of spread.  Testing the
        # standard deviation prevents the formation of a bimodal distribution
        # who each flank the desired location
        #
        # Sum the errors
        ff = np.nan if len(heights) == 0 else np.sqrt((np.mean(heights) -
                                                       ref_height)**2
                                                      + np.std(heights)**2)
    except:
        ff = np.nan

    # Return the square root of the summed squared errors
    return ff


#---------------------------------------------------------------------------
def distribution_min(tdiff, ref_loc, loc_args, loc_func, func_tol,
                     tdiff_tol=1.0e-4, tperiod=np.nan, maxiter=2000):
    '''Finds the minimum of the locaiton distribution about an ideal location

    Parameters
    -----------
    tdiff : (float)
        initial tdiff in microseconds
    ref_loc : (float)
        reference location
    loc_args : (tuple)
        A set containing the values for each backscatter measurement needed to
        calculate the location of the scattering point.  For example, latitude
        requires:
        (hard, asep, phi_sign, ecor, phi0, phi0e, fovflg, cos_phi, tfreq)
    loc_func : (function)
        Function that describes the goodness of the backscatter distribution
        about the reference location, where a lower value indicates a better fit
    func_tol : (float)
        Level of significance between minima in units of location
    tdiff_tol : (float)
        Level of significance for resulting tdiff in microseconds.
        (default=1.0e-4)
    tperiod : (float)
        If this is a cyclical function, include the period where another
        minimum is expected.  If not, use NaN (default=np.nan)
    maxiter : (int)
        Maximum number of iterations to allow in estimation process.
        (default=2000)

    Returns
    ---------
    new_tdiff : (float)
        New tdiff estimate in microseconds
    miter : (int)
        Number of iterations needed to estimate tdiff
    res : (tuple)
        Results from the successful simplex minimization run
    '''
    import davitpy.pydarn.radar.tdiff.simplex as simplex

    # Perform the minimization using the Nelder-Mead Simplex method
    tdiff1, mi1, res1 = simplex.rigerous_simplex(tdiff, (ref_loc,) + loc_args,
                                                 loc_func, tol=tdiff_tol,
                                                 maxiter=maxiter)

    if np.isnan(tperiod) or np.isnan(tdiff1) or mi1 >= maxiter:
        # If the function is not cyclical, or a minima could not be found,
        # return with the result
        return tdiff1, mi1, res1

    # If this is a cyclical function, perturb the initial guess by one period
    # Choose the direction that should find an estimate that brackets the
    # initial guess
    tsign = np.sign(tdiff - tdiff1)
    new_sign = tsign
    mi2 = mi1
    tdiff2 = tdiff1
    while np.sign(new_sign) == tsign and mi2 < maxiter and not np.isnan(tdiff2):
        tdiff2, mi, res2 = simplex.rigerous_simplex(tdiff1+new_sign*tperiod,
                                                    (ref_loc,) + loc_args,
                                                    loc_func, tol=tdiff_tol,
                                                    maxiter=maxiter)
        mi2 += mi
        if not np.isnan(tdiff2):
            new_sign = np.sign(tdiff - tdiff2)
            if new_sign == tsign:
                # We have found a minima closer to the initial guess, but not
                # bracketing the initial guess
                tdiff1 = tdiff2
                mi1 = mi2
                res1 = res2

    # If a bracketing minima could not be found, return the first minima
    if np.isnan(tdiff2) or mi2 >= maxiter:
        return tdiff1, mi1, res1

    # Ensure that there is not a thrid minima of equal signicance close to the
    # initial guess
    if tdiff1 < tdiff2:
        a = tdiff1
        c = tdiff2
        fa = res1['fun']
        fc = res2['fun']
    else:
        a = tdiff2
        c = tdiff1
        fa = res2['fun']
        fc = res1['fun']

    # If the two minima bracket the initial guess, there may be another minima
    # that is closer to the initial guess
    if a < tdiff and tdiff < c:
        fb = loc_func(tdiff, *((ref_loc,) + loc_args))

        # Move upper and lower limits to exclude the identified minima
        while fb >= fa and tdiff - a > tdiff_tol:
            a = tdiff - 0.5 * (tdiff - a)
            fa = loc_func(a, *((ref_loc,) + loc_args))
        
        while fb >= fc and c - tdiff > tdiff_tol:
            c = tdiff + 0.5 * (c - tdiff)
            fc = loc_func(c, *((ref_loc,) + loc_args))

        # But we won't bother messing about with minimization at this point.
        # Now that the problem is constrained, make a list with tdiff
        # incrimenting at the rate of the tolerence
        if a <= tdiff and tdiff <= c:  
            x = np.arange(a, c, tdiff_tol*1.0e-1)
        else:
            x = []

        # Of course the tdiff correction may be really close to tdiff already.
        # Only continue if there was enough of a difference between the two
        # bracketing points to provide a range of points to calcuate a minima.
        if len(x) > 1:
            y = [loc_func(xx, *((ref_loc,) + loc_args)) for xx in x]
            ymin = min(y)
            xx = y.index(ymin)
            # A minima between the two previously found was located.
            if abs(res1['fun'] - ymin) <= func_tol:
                # This minima is equally significant.  Keep it if it is
                # closer to the initial guess than the first minima
                if abs(tdiff1 - tdiff) > abs(x[xx] - tdiff):
                    tdiff1 = x[xx]
                    mi1 = maxiter - 1
                    res1 = {'status':0, 'nfev':len(y), 'success':True,
                            'fun':ymin, 'x':x[xx], 'message':'Found from list',
                            'nit':mi1}
            elif ymin < res1['fun']:
                # This minima is more significant.  Keep it
                mi1 = maxiter - 1
                res1 = {'status':0, 'nfev':len(y), 'success':True, 'fun':ymin,
                        'x':x[xx], 'message':'Found from list', 'nit':mi1}
                return x[xx], mi1, res1

    # See if the remaining minima are equally significant.  If they are pick the
    # one closest to the original guess.  Otherwise choose the deepest minima
    if abs(res1['fun'] - res2['fun']) <= func_tol:
        # Check to see if the difference between the distances between the
        # tdiff estimate and the initial guess are significant.  If they are not
        # then choose the tdiff with the lowest function value.  If they are
        # significant, than choose the value closest to the inital guess
        diff1 = abs(tdiff1 - tdiff)
        diff2 = abs(tdiff2 - tdiff)

        if abs(diff1 - diff2) <= tdiff_tol:
            if res1['fun'] <= res2['fun']:
                return tdiff1, mi1, res1
            else:
                return tdiff2, mi2, res2
        else:
            if diff1 <= diff2:
                return tdiff1, mi1, res1
            else:
                return tdiff2, mi2, res2
    elif res1['fun'] < res2['fun']:
        return tdiff1, mi1, res1
    else:
        return tdiff2, mi2, res2
