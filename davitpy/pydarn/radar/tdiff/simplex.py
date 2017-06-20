#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------
# simplex.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Simplex minimization functions
#-----------------------------------------------------------------------------
"""Simplex minimization functions

Functions
------------------------------------------------------------------------------
rigerous_simplex  Implimentation of the Nelder-Mead simplex minimization
------------------------------------------------------------------------------

References
------------------------------------------------------------------------------
A.G. Burrell et al. (2016) submitted to Radio Science doi:xxx
Nelder and Mead (1965) The Computer Journal, 7(4), 308-313
------------------------------------------------------------------------------
"""

import scipy.optimize as sciopt
import numpy as np

#---------------------------------------------------------------------------
def rigerous_simplex(x0, args, minfunc, tol, maxiter=500):
    '''
    An implimentation of the Nelder-Mead Simplex minimization function that
    performs several tests to ensure that the returned minimum is a global
    rather than local minima

    Parameters
    -----------
    x0 : (float/int)
        Initial guess for function minimum
    args : (tuple)
        Tuple containing the arguments needed to call the function
    minfunc : (function)
        Function to minimize
    tol : (float)
        Tolerance for the minimum.
    maxiter : (int)
        Maximum number of iterations to perform.  (default=500)

    Returns
    ---------
    new_xmin : (float)
        Function minimum
    miter : (int)
        Number of iterations needed to estimate xmin
    res : (tuple)
        Results from the successful simplex minimization run
    '''
    # Initialize test variables
    mi = 0
    local_min = None
    func_min = dict()
    imin = 2
    xmin = x0

    #--------------------------------------------------------------------------
    # Perform the minimization using the Nelder-Mead Simplex method
    while mi < maxiter:
        # The Nelder-Mead method is not robust, and so will often return
        # a local minimum.  Starting with this minimum, though, will cause
        # the routine to consider a larger portion of data and eventually land
        # in the a grand minimum
        res = sciopt.minimize(minfunc, np.array(xmin), args=args,
                              method='Nelder-Mead', tol=tol,
                              options={"maxiter":maxiter, "disp":True})
        new_xmin = float(res['x'])
        mi += res['nit']

        if local_min is not None:
            xmin = local_min

        if abs(new_xmin - xmin) < tol:
            if local_min is None and not func_min.has_key(res['fun']):
                # This function likely has a lot of local minima.  Give xmin
                # a kick in both directions and see if it is stable
                local_min = xmin
                imin += 0.5
                tinc = 0.001 * imin
                tsign = np.sign(xmin - x0)
                new_xmin += tinc * tsign
                func_min[res['fun']] = [1, tinc, tsign, xmin, res]
            elif func_min.has_key(res['fun']) and func_min[res['fun']][0] == 1:
                # Now try the second direction
                fmin = func_min[res['fun']]
                new_xmin = fmin[3] - fmin[2] * fmin[1]
                func_min[res['fun']][0] += 1
            else:
                break
        elif local_min is not None:
            local_min = None

        xmin = new_xmin

    if mi > maxiter:
        new_xmin = np.nan
    else:
        # Test to ensure that the minimum we settled is closest to the global
        # minimum
        fmin = min(func_min.keys())
        if res['fun'] > fmin:
            new_xmin = func_min[fmin][3]
            res = func_min[fmin][4]

    return new_xmin, mi, res
