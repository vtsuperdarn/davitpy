#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------
# calc_tdiff.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Function to estimate tdiff
#-----------------------------------------------------------------------------
"""This module contains routines to estimate tdiff from backscatter at a known
location

Functions
-------------------------------------------------------------------------------
calc_tdiff       Calculate tdiff by minimizing the distribution about a location
select_bscatter  Select appropriate backscatter
-------------------------------------------------------------------------------

References
------------------------------------------------------------------------------
A.G. Burrell et al. (2016) submitted to Radio Science doi:xxx
------------------------------------------------------------------------------
"""
import numpy as np
import logging

def calc_tdiff(init_tdiff, ref_loc, ref_err, loc_args, loc_func, func_tol,
               tdiff_tol=1.0e-4, tperiod=np.nan, maxiter=2000):
    ''' Calculate tdiff by minimizing the distribution about a location

    Parameters
    ----------
    init_tdiff : (float)
        Initial tdiff guess (recommend using tdiff from hdw files)
    ref_loc : (float)
        Reference location (e.g. latitude or altitude)
    ref_err : (float)
        Uncertainty in reference location
    loc_args : (list)
        List of arguements needed to calculate the location, in the correct
        order to use as input for the location function.  For example, latitude
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
    -----------
    tdiff : (float)
        tdiff in microseconds
    terr : (float)
        uncertainty in tdiff in microseconds
    miter : (int)
        Number of iterations needed to estimate tdiff
    res : (tuple)
        Results from the successful simplex minimization run
    '''
    import bscatter_distribution as bdist

    terr = np.nan

    # Estimate tdiff:
    tdiff, miter, res = bdist.distribution_min(init_tdiff, ref_loc, loc_args,
                                               loc_func, func_tol,
                                               tdiff_tol=tdiff_tol,
                                               tperiod=tperiod, maxiter=maxiter)
    if np.isnan(tdiff):
        return tdiff, terr, miter, res

    # Find the tdiff uncertainty by calculating tdiff with
    # ref_lat +/- ref_err and taking the larger of the two
    thigh, eiter, eres = bdist.distribution_min(init_tdiff, ref_loc + ref_err,
                                                loc_args, loc_func, func_tol,
                                                tdiff_tol=tdiff_tol,
                                                tperiod=tperiod,
                                                maxiter=maxiter)

    tlow, eiter, eres = bdist.distribution_min(init_tdiff, ref_loc - ref_err,
                                               loc_args, loc_func, func_tol,
                                               tdiff_tol=tdiff_tol,
                                               tperiod=tperiod, maxiter=maxiter)
    if not np.isnan(thigh):
        terr = abs(thigh - tdiff)
    if not np.isnan(tlow):
        if np.isnan(terr) or terr < abs(tlow - tdiff):
            terr = abs(tlow - tdiff)

    return tdiff, terr, miter, res

def select_bscatter(beams, ret_attrs, radcp, tband, bnum, min_power=0.0,
                    min_rg=0, max_rg=75, fovflg=None, gflg=None, stimes=list(),
                    etimes=list()):
    '''Sample selection routine for heater backscatter

    Parameters
    ------------
    beams : (list or np.ndarray)
        List or array of beam class objects, or scan class object from a
        single radar
    ret_attrs : (list of strings)
        List of desired attributes to return
    radcp : (int)
        Desired radar program mode
    tband : (int)
        Desired radar transmission frequency band
    bnum : (int)
        Desired radar beam number
    min_power : (float)
        Minimum allowed power (dB) (default=0.0)
    min_rg : (int)
        Minimum allowed range gate (default=0)
    max_rg : (int)
        Maximum allowed range gate (default=75)
    fovflg : (int)
        Desired field-of-view or None to ignore (default=None)
    gflg : (int)
        Desired type of backscatter or None to ignore (default=None)
    stimes : (list)
        List of allowed starting time periods (default=[])
    etimes : (list)
        List of allowed ending time periods (default=[])

    Returns
    ----------
    ret_data : (dict of lists)
        Dictionary containing lists of desired return attributes
    '''
    import rad_freqbands

    # Define the local routines
    def good_fov(fovflg, bfit, i):
        if fovflg is None:
            return True
        else:
            if hasattr(bfit, "fovflg"):
                fitflg = getattr(bfit, "fovflg")
                if fitflg is not None and fitflg[i] == fovflg:
                    return True
        return False
            
    def good_time(stimes, etimes, btime):
        if len(stimes) > 0:
            for i,ss in enumerate(stimes):
                if ss <= btime and  btime <= etimes[i]:
                    return True
        else:
            return True
        return False
                
    # Initialize output
    ret_data = {rkey:list() for rkey in ret_attrs}

    # Begin evaluating beam data
    rad_tfreq = None

    for beam in beams:
        # Use the first beam to define the frequency band object
        if rad_tfreq is None:
            rad_tfreq = rad_freqbands.radFreqBands(beam.stid)

            # Test to see if the frequency band is defined
            if len(rad_tfreq.tbands) < tband:
                logging.warn("undefined frequency band [{:}]".format(tband))
                return ret_data

        # Identify acceptable backscatter for this beam
        if(hasattr(beam, "fit") and beam.cp == radcp and beam.bmnum == bnum
           and hasattr(beam, "prm") and
           tband == rad_tfreq.get_tfreq_band_num(beam.prm.tfreq)):
            igood = [i for i,p in enumerate(beam.fit.p_l) if p >= min_power and
                     min_rg <= beam.fit.slist[i] and max_rg >= beam.fit.slist[i]
                     and good_fov(fovflg, beam.fit, i) and
                     (gflg is None or beam.fit.gflg[i] == gflg)
                     and good_time(stimes, etimes, beam.time)]

            if len(igood) > 0:
                # Assign values for each requested data type, padding with
                # NaN if the key or values aren't available
                for rkey in ret_data.keys():
                    if hasattr(beam, rkey):
                        # Add beam attribute
                        rdata = getattr(beam, rkey)
                        ret_data[rkey].extend([rdata for i in igood])
                    elif hasattr(beam.fit, rkey):
                        # Add fit attribute
                        rdata = getattr(beam.fit, rkey)
                        if rdata is not None:
                            ret_data[rkey].extend([rdata[i] for i in igood])
                        else:
                            ret_data[rkey].extend([np.nan for i in igood])
                    elif hasattr(beam.prm, rkey):
                        # Add parameter attribute
                        rdata = getattr(beam.prm, rkey)
                        ret_data[rkey].extend([rdata for i in igood])
                    else:
                        # Pad unavailable attribute
                        ret_data[rkey].extend([np.nan for i in igood])

    return ret_data
