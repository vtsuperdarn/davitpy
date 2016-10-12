#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# calc_elevation.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Routines to calculate the elevation angle and its error.
#-----------------------------------------------------------------------------
"""calc_elevation

Routines to calculate the elevation angle and its error

Functions
------------------------------------------------------------------------------
calc_elv        Calculate elevation angle using phase lag
calc_elv_w_err  Calculate elevation angle and error using phase lag
calc_elv_list   Calculate elevation angle using input from lists or np.arrays
------------------------------------------------------------------------------

Author: Angeline G. Burrell (AGB)
Date: February 9, 2016
Inst: University of Leicester (UoL)
"""

# Import python packages
import numpy as np
from scipy import constants as scicon
import logging

#---------------------------------------------------------------------------
def calc_elv(beam, phi0_attr="phi0", phi0_e_attr="phi0_e", hard=None,
             tdiff=None, alias=0.0, fov='front'):
    """Calculate the elevation angle for observations along a beam at a radar

    Parameters
    -----------
    beam : (class `pydarn.sdio.radDataTypes.beamData`)
        Data for a single radar and beam along all range gates at a given time
    hard : (class `pydarn.radar.radStruct.site` or NoneType)
        Radar hardware data or None to load here (default=None)
    tdiff : (float or NoneType)
        The relative time delay of the signal paths from the interferometer
        array to the receiver and the main array to the reciver (microsec) or
        None to use the value supplied by the hardware file (default=None)
    alias : (float)
        Amount to offset the acceptable phase shifts by.  The default phase
        shift range starts at the calculated max - 2 pi, any (positive) alias
        will remove 2 pi from the minimum allowable phase shift. (default=0.0)
    fov : (str)
        'front' = Calculate elevation angles from front Field-of-View (fov);
        'back' = Calculate elevation angle from back FoV. (default='front')
    
    Returns
    --------
    elv : (np.array)
        A list of floats of the same size as the myBeam.fit.slist list,
        containing the new elevation angles for each range gate or NaN if an
        elevation angle could not be calculated
    phase_amb: (np.array)
        A list of integers containing the phase ambiguity integer used to
        alias the elevation angles
    hard : (class `pydarn.radar.radStruct.site` or NoneType)
        Radar hardware data or None to load here (default=None)
    """
    import davitpy.pydarn.sdio as sdio
    import davitpy.pydarn.radar as pyrad

    #-------------------------------------------------------------------------
    # Test input
    assert isinstance(beam, sdio.radDataTypes.beamData), \
        logging.error('the beam must be a beamData class')
    assert isinstance(phi0_attr, str) and hasattr(beam.fit, phi0_attr), \
        logging.error('the phase lag data is not in this beam')
    assert isinstance(hard, pyrad.site) or hard is None, \
        logging.error('supply the hardware class or None')
    assert isinstance(tdiff, float) or tdiff is None, \
        logging.error('the tdiff should be a float or NoneType')
    assert isinstance(alias, float), \
        logging.error('the alias number should be a float')
    assert(isinstance(fov, str) and (fov.find("front") >= 0 or
                                     fov.find("back") >= 0)), \
        logging.error('the field-of-view must be "front" or "back"')

    # Only use this if the interferometer data was stored during this scan
    assert beam.prm.xcf == 1, \
        logging.error('no interferometer data at this time')

    # Load the phase lag data
    phi0 = getattr(beam.fit, phi0_attr)

    # This method cannot be applied at Goose Bay or any other radar/beam that
    # does not include phi0 in their FIT output
    assert phi0 is not None, \
        logging.error('phi0 missing from rad {:d} beam {:d}'.format(beam.stid,
                                                                    beam.bmnum))

    # If possible, load the phase lag error data (not required to run)
    if hasattr(beam.fit, phi0_e_attr):
        phi0_e = getattr(beam.fit, phi0_e_attr)
    else:
        phi0_e = [1.0 for p in phi0]

    #-------------------------------------------------------------------------
    # Initialize output
    elv = np.empty(shape=(len(phi0),), dtype=float) * np.nan
    phase_amb = np.zeros(shape=(len(phi0),), dtype=int)

    #-------------------------------------------------------------------------
    # If desired, load the radar hardware data for the specified site and time
    if hard is None:
        hard = pyrad.site(radId=beam.stid, dt=beam.time)

    # Set the proper angle sign based on whether this is backlobe or
    # front lobe data
    if fov.find("front") == 0:
        back = 1.0
    else:
        back = -1.0

    # If desired, overwrite the hardware value for tdiff
    if tdiff is None:
        tdiff = hard.tdiff

    #-------------------------------------------------------------------------
    # Calculate the beam-specific variables
    #
    # Phi is the beam direction off the radar boresite assuming an elevation
    # angle of zero.  This is calculated by the hardware routine 'beamToAzim'
    # located in pydarn.radar.radStruct
    bm_az = np.radians(hard.beamToAzim(beam.bmnum) - hard.boresite)
    cos_az = np.cos(bm_az)
    sin_az = np.sin(bm_az)
    az_sign = 1.0 if hard.interfer[1] > 0.0 else -1.0

    # Find the elevation angle with the maximum phase lag
    el_max = np.arcsin(az_sign * hard.interfer[2] * cos_az /
                       np.sqrt(hard.interfer[1]**2 + hard.interfer[2]**2))
    if el_max < 0.0:
        el_max = 0.0

    cos_max = np.cos(el_max)
    sin_max = np.sin(el_max)

    # k is the wavenumber in radians per meter
    k = 2.0 * np.pi * beam.prm.tfreq * 1.0e3 / scicon.c

    # Calculate the phase shift due to the radar cables
    del_chi = -np.pi * beam.prm.tfreq * tdiff * 2.0e-3

    # Find the maximum possible phase shift
    chimax = k * (hard.interfer[0] * sin_az + hard.interfer[1] *
                  np.sqrt(cos_max**2- sin_az**2) + hard.interfer[2] * sin_max)
    chimin = chimax - (alias + 1.0) * az_sign * 2.0 * np.pi
    
    #-------------------------------------------------------------------------
    # Calculate the elevation for each value of phi0
    for i,p0 in enumerate(phi0):
        #---------------------------------------------------------------------
        # Use only data where the angular drift between signals is not
        # identically zero with an error of zero, since this could either be a
        # sloppy flag denoting no data or an actual measurement.
        if p0 != 0.0 or phi0_e[i] != 0.0:
            # Find the right phase.  This method works for both front and back
            # lobe calculations, unlike the more efficient method used by RST
            # in elevation.c:
            # phi_tempf = phi0 + 2.0*np.pi* np.floor(((chimax+del_chi)-phi0)/
            #                                       (2.0*np.pi))
            # if phi_sign < 0.:
            #     phi_tempf += 2.0 * np.pi
            # cos_thetaf = (phi_tempf - del_chi) / (k * asep)
            # sin2_deltaf = cos_phi**2 - cos_thetaf**2
            #
            # They both yield the same elevation for front lobe calculations
            phi_temp = (back * (p0 - del_chi)) % (2.0 * np.pi)
            amb_temp = -np.floor(back * (p0 - del_chi) / (2.0 * np.pi))

            # Ensure that phi_temp falls within the proper limits
            while phi_temp > max(chimax, chimin):
                phi_temp += az_sign * 2.0 * np.pi
                amb_temp += az_sign

            while abs(phi_temp) < abs(chimin):
                phi_temp += az_sign * 2.0 * np.pi
                amb_temp += az_sign

            #--------------------------
            # Evaluate the phase shift
            if phi_temp > max(chimax, chimin):
                estr = "can't fix phase shift for beam {:d}".format(beam.bmnum)
                estr = "{:s} [{:f} not between ".format(estr, phi_temp)
                estr = "{:s}{:f},{:f} on ".format(estr, chimin, chimax)
                estr = "{:s}{:} at range gate {:d}".format(estr, beam.time,
                                                           beam.fit.slist[i])
                logging.critical(estr)
            else:
                # Calcualte the elevation angle and set if realistic
                cos_theta = phi_temp / k - hard.interfer[0] * sin_az
                yz_sum2 = hard.interfer[1]**2 + hard.interfer[2]**2
                sin_delta = (cos_theta * hard.interfer[2] +
                             np.sqrt((cos_theta * hard.interfer[2])**2 -
                                     yz_sum2 * (cos_theta**2 -
                                                (hard.interfer[1] *
                                                 cos_az)**2))) / yz_sum2

                if sin_delta <= 1.0:
                    elv[i] = np.degrees(np.arcsin(sin_delta))
                    phase_amb[i] = int(amb_temp)

    return elv, phase_amb, hard

#---------------------------------------------------------------------------
def calc_elv_w_err(beam, phi0_attr="phi0", phi0_e_attr="phi0_e", hard=None,
                   bmaz_e=0.0, boresite_e=0.0, ix_e=0.0, iy_e=0.0, iz_e=0.0,
                   tdiff=None, tdiff_e=0.0, alias=0.0, fov='front'):
    """Calculate the elevation angle for observations along a beam at a radar

    Parameters
    -----------
    beam : (class `pydarn.sdio.radDataTypes.beamData`)
        Data for a single radar and beam along all range gates at a given time
    phi0_attr : (str)
        Name of the phase lag attribute in the beam.fit object (default="phi0")
    phi0_e_attr : (str)
        Name of the phase lag error attribute (default="phi0_e")
    hard : (class `pydarn.radar.radStruct.site` or NoneType)
        Radar hardware data or None to load here (default=None)
    bmaz_e : (float)
        Error in beam azimuth in degrees (default=0.0)
    boresite_e : (float)
        Error in the boresite location in degrees (default=0.0)
    ix_e : (float)
        Error in the interferometer x coordinate in meters (default=0.0)
    iy_e : (float)
        Error in the interferometer y coordinate in meters (default=0.0)
    iz_e : (float)
        Error in the interferometer z coordinate in meters (default=0.0)
    tdiff : (float or NoneType)
        The relative time delay of the signal paths from the interferometer
        array to the receiver and the main array to the reciver (microsec) or
        None to use the value supplied by the hardware file (default=None)
    tdiff_e : (float)
        Error in the tdiff value in microseconds (default=0.0)
    alias : (float)
        Amount to offset the acceptable phase shifts by.  The default phase
        shift range starts at the calculated max - 2 pi, any (positive) alias
        will remove 2 pi from the minimum allowable phase shift. (default=0.0)
    fov : (str)
        'front' = Calculate elevation angles from front Field-of-View (fov);
        'back' = Calculate elevation angle from back FoV. (default='front')
    
    Returns
    --------
    elv : (np.array)
        A list of floats of the same size as the myBeam.fit.slist list,
        containing the elevation angle for each range gate or NaN if an
        elevation angle could not be calculated.
    elv_e : (np.array)
        A list of floats of the same size as the myBeam.fit.slist list,
        containing the elevation angle errors for each range gate or NaN if an
        elevation angle error could not be calculated.
    phase_amb: (np.array)
        A list of integers containing the phase ambiguity integer used to
        alias the elevation angles
    hard : (class `pydarn.radar.radStruct.site` or NoneType)
        Radar hardware data or None to load here (default=None)
    """
    import davitpy.pydarn.sdio as sdio
    import davitpy.pydarn.radar as pyrad

    #-------------------------------------------------------------------------
    # Test input
    assert isinstance(beam, sdio.radDataTypes.beamData), \
        logging.error('the beam must be a beamData class')
    assert isinstance(phi0_attr, str) and hasattr(beam.fit, phi0_attr), \
        logging.error('the phase lag data is not in this beam')
    assert isinstance(phi0_e_attr, str) and hasattr(beam.fit, phi0_attr), \
        logging.error('the phase lag error data is not in this beam')
    assert isinstance(hard, pyrad.site) or hard is None, \
        logging.error('supply the hardware class or None')
    assert isinstance(tdiff, float) or tdiff is None, \
        logging.error('the tdiff should be a float or NoneType')
    assert isinstance(tdiff_e, float) or tdiff is None, \
        logging.error('the tdiff should be a float or NoneType')
    assert isinstance(bmaz_e, float), \
        logging.error('the beam azimuth error should be a float')
    assert isinstance(boresite_e, float), \
        logging.error('the boresite error should be a float')
    assert isinstance(ix_e, float), \
        logging.error('the interferometer x error should be a float')
    assert isinstance(iy_e, float), \
        logging.error('the interferometer y error should be a float')
    assert isinstance(iz_e, float), \
        logging.error('the interferometer z error should be a float')
    assert isinstance(alias, float), \
        logging.error('the alias number should be a float')
    assert(isinstance(fov, str) and (fov.find("front") >= 0 or
                                     fov.find("back") >= 0)), \
        logging.error('the field-of-view must be "front" or "back"')

    # Only use this if the interferometer data was stored during this scan
    assert beam.prm.xcf == 1, \
        logging.error('no interferometer data at this time')

    # Load the phase lag data
    phi0 = getattr(beam.fit, phi0_attr)

    # This method cannot be applied at Goose Bay or any other radar/beam that
    # does not include phi0 in their FIT output
    assert phi0 is not None, \
        logging.error('phi0 missing from rad {:d} beam {:d}'.format(beam.stid,
                                                                    beam.bmnum))

    # If possible, load the phase lag error data (not required to run)
    if hasattr(beam.fit, phi0_e_attr):
        phi0_e = getattr(beam.fit, phi0_e_attr)
    else:
        phi0_e = [0.0 for p in phi0]

    # If any of the errors are NaN, set to zero
    if np.isnan(bmaz_e):
        bmaz_e = 0.0
    if np.isnan(boresite_e):
        boresite_e = 0.0
    if np.isnan(ix_e):
        ix_e = 0.0
    if np.isnan(iy_e):
        iy_e = 0.0
    if np.isnan(iz_e):
        iz_e = 0.0
    if np.isnan(tdiff_e):
        tdiff_e = 0.0

    #-------------------------------------------------------------------------
    # Initialize output
    elv = np.empty(shape=(len(phi0),), dtype=float) * np.nan
    elv_e = np.empty(shape=(len(phi0),), dtype=float) * np.nan
    phase_amb = np.zeros(shape=(len(phi0),), dtype=int)

    #-------------------------------------------------------------------------
    # If desired, load the radar hardware data for the specified site and time
    if hard is None:
        hard = pyrad.site(radId=beam.stid, dt=beam.time)

    # Set the proper angle sign based on whether this is backlobe or
    # front lobe data
    if fov.find("front") == 0:
        back = 1.0
    else:
        back = -1.0

    # If desired, overwrite the hardware value for tdiff
    if tdiff is None:
        tdiff = hard.tdiff

    #-------------------------------------------------------------------------
    # Calculate the beam-specific variables
    #
    # Phi is the beam direction off the radar boresite assuming an elevation
    # angle of zero.  This is calculated by the hardware routine 'beamToAzim'
    # located in pydarn.radar.radStruct
    bm_az = np.radians(hard.beamToAzim(beam.bmnum) - hard.boresite)
    cos_az = np.cos(bm_az)
    sin_az = np.sin(bm_az)
    az_sign = 1.0 if hard.interfer[1] > 0.0 else -1.0
    sig2_az = bmaz_e**2 + boresite_e**2 
    
    # Find the elevation angle with the maximum phase lag
    el_max = np.arcsin(az_sign * hard.interfer[2] * cos_az /
                       np.sqrt(hard.interfer[1]**2 + hard.interfer[2]**2))
    if el_max < 0.0:
        el_max = 0.0

    cos_max = np.cos(el_max)
    sin_max = np.sin(el_max)
    
    # k is the wavenumber in radians per meter
    k = 2.0 * np.pi * beam.prm.tfreq * 1.0e3 / scicon.c

    # Calculate the phase-lag independent portion of the theta error
    theta2_base = sig2_az * (hard.interfer[0] * cos_az)**2

    if ix_e > 0.0:
        theta2_base += (ix_e * sin_az)**2

    if tdiff_e > 0.0:
        theta2_base += (scicon.c * tdiff_e * 1.0e-6)**2

    # Calculate the phase shift due to the radar cables
    del_chi = -np.pi * beam.prm.tfreq * tdiff * 2.0e-3

    # Find the maximum possible phase shift
    chimax = k * (hard.interfer[0] * sin_az + hard.interfer[1] *
                  np.sqrt(cos_max**2- sin_az**2) + hard.interfer[2] * sin_max)
    chimin = chimax - (alias + 1.0) * az_sign * 2.0 * np.pi
    
    #-------------------------------------------------------------------------
    # Calculate the elevation for each value of phi0
    for i,p0 in enumerate(phi0):
        #---------------------------------------------------------------------
        # Use only data where the angular drift between signals is not
        # identically zero and the error is not NaN
        if p0 != 0.0 and not np.isnan(phi0_e[i]):
            # Find the right phase.  This method works for both front and back
            # lobe calculations, unlike the more efficient method used by RST
            # in elevation.c:
            # phi_tempf = phi0 + 2.0*np.pi* np.floor(((chimax+del_chi)-phi0)/
            #                                       (2.0*np.pi))
            # if phi_sign < 0.:
            #     phi_tempf += 2.0 * np.pi
            # cos_thetaf = (phi_tempf - del_chi) / (k * asep)
            # sin2_deltaf = cos_phi**2 - cos_thetaf**2
            #
            # They both yield the same elevation for front lobe calculations
            phi_temp = (back * (p0 - del_chi)) % (2.0 * np.pi)
            amb_temp = -np.floor(back * (p0 - del_chi) / (2.0 * np.pi))

            # Ensure that phi_temp falls within the proper limits
            while phi_temp > max(chimax, chimin):
                phi_temp += az_sign * 2.0 * np.pi
                amb_temp += az_sign

            while abs(phi_temp) < abs(chimin):
                phi_temp += az_sign * 2.0 * np.pi
                amb_temp += az_sign

            #--------------------------
            # Evaluate the phase shift
            if phi_temp > max(chimax, chimin):
                estr = "can't fix phase shift for beam {:d}".format(beam.bmnum)
                estr = "{:s} [{:f} not between ".format(estr, phi_temp)
                estr = "{:s}{:f},{:f} on ".format(estr, chimin, chimax)
                estr = "{:s}{:} at range gate {:d}".format(estr, beam.time,
                                                           beam.fit.slist[i])
                logging.critical(estr)
            else:
                # Calculate the elevation angle and set if realistic
                cos_theta = phi_temp / k - hard.interfer[0] * sin_az
                yz_sum2 = hard.interfer[1]**2 + hard.interfer[2]**2
                yscale2 = ((cos_theta * hard.interfer[2])**2 -
                           yz_sum2 * (cos_theta**2 -
                                      (hard.interfer[1] * cos_az)**2))
                sin_delta = (cos_theta * hard.interfer[2] +
                             np.sqrt(yscale2)) / yz_sum2

                if sin_delta <= 1.0:
                    # Calculate the elevation
                    elv[i] = np.degrees(np.arcsin(sin_delta))
                    phase_amb[i] = int(amb_temp)

                    # Now that the elevation was calculated, find the
                    # elevation error, using the propagation of error to
                    # propagate the provided uncertainties
                    asin_der = 1.0 / np.sqrt(1.0 - sin_delta**2)

                    # If the azimuthal error is not zero, calculate derivative
                    if sig2_az > 0.0:
                        az_term2 = (cos_az * sin_az)**2 / yscale2
                        az_term2 *= np.power(hard.interfer[1], 4) * sig2_az

                    else:
                        az_term2 = 0.0

                    # If there is an error in the phase lag, add this to the
                    # theta sigma and then calculate the theta term
                    if phi0_e[i] > 0.0:
                        theta_term2 = theta2_base + (phi0_e[i] / k)**2
                    else:
                        theta_term2 = theta2_base

                    if theta_term2 > 0.0:
                        theta_term2 *= ((hard.interfer[2] - hard.interfer[1]**2
                                        * cos_theta / np.sqrt(yscale2))
                                       / yz_sum2)**2

                    # If the interferometer Y error is not zero, get derivative
                    if iy_e > 0.0:
                        iy_term2 = (yz_sum2 - 2.0 * cos_theta *
                                    hard.interfer[1] * hard.interfer[2] - 2.0 *
                                    hard.interfer[1] * np.sqrt(yscale2) +
                                    hard.interfer[1]**2 * yz_sum2 *
                                    (yz_sum2 * cos_az**2 - cos_theta**2) /
                                    np.sqrt(yscale2))**2 / np.power(yz_sum2, 4)
                        iy_term2 *= iy_e**2
                    else:
                        iy_term2 = 0.0

                    # If the interferometer Z error is not zero, get derivative
                    if iz_e > 0.0:
                        iz_term2 = ((yz_sum2 * (cos_theta + hard.interfer[2] *
                                                (hard.interfer[1] * cos_az)**2 /
                                                np.sqrt(yscale2)) - 2.0 *
                                     hard.interfer[2] * np.sqrt(yscale2))
                                    * iz_e)**2 / np.power(yz_sum2, 4)
                    else:
                        iz_term2 = 0.0                        

                    # Calculate the elevation error, adding in quadrature
                    temp = np.sqrt(az_term2 + theta_term2 + iy_term2 + iz_term2)

                    # If the elevation error is identically zero, assume
                    # that no error could be obtained
                    elv_e[i] = np.nan if temp == 0.0 else temp

    return elv, elv_e, phase_amb, hard


#---------------------------------------------------------------------------
def calc_elv_list(phi0, phi0_e, fovflg, bm_az, tfreq, interfer_offset,
                  tdiff, alias=0.0):
    '''Calculate the elevation angle in radians for a single radar

    Parameters
    -----------
    phi0 : (list of floats)
        List of phase lags in radians
    phi0_e : (list of floats or None)
        List of phase lag errors in radians
    fovflg : (list of ints)
        List of field-of-view flags where 1 indicates the front, -1 the rear
    bm_az : (list of floats)
        Azimuthal angle between the beam and the radar boresite at zero
        elevation (radians)
    tfreq : (list of floats)
        Transmission frequency (kHz)
    interfer_offset : (list or numpy.ndarray of floats)
        Offset of the midpoints of the interferometer and main array (meters),
        where [0] is X, [1] is Y, and [2] is Z.
    tdiff : (float)
        The relative time delay of the signal paths from the interferometer
        array to the receiver and the main array to the reciver (microsec)
    alias : (float)
        Amount to offset the acceptable phase shifts by.  The default phase
        shift range starts at the calculated max - 2 pi, any (positive) alias
        will remove 2 pi from the minimum allowable phase shift. (default=0.0)
    
    Returns
    --------
    elv : (list)
        A list of floats containing the new elevation angles for each phi0 in
        radians or NaN if an elevation angle could not be calculated
    '''
    #-------------------------------------------------------------------------
    # Initialize output
    elv = list()

    #-------------------------------------------------------------------------
    # Test input
    if not isinstance(phi0, list) and not isinstance(phi0, np.ndarray):
        logging.error("the phase lag must be a list or numpy array")
        return elv

    if((not isinstance(phi0_e, list) and not isinstance(phi0_e, np.ndarray))
       or phi0_e is None):
        estr = "the phase lag error has been discarded, it is not a list or "
        logging.warn("{:s} numpy array".format(estr))
        phi0_e = [1.0 for p in phi0]

    if(not isinstance(fovflg, list) and not isinstance(fovflg, np.ndarray)):
        logging.error("the FoV flag must be a list or numpy array")
        return elv

    if len(phi0) == 0 or len(phi0_e) != len(phi0) or len(fovflg) != len(phi0):
        logging.error("the input lists are empty or are not the same size")
        return elv

    if not isinstance(interfer_offset, list) or len(interfer_offset) != 3:
        logging.error("the elevation correction must be a float")
        return elv

    if isinstance(tdiff, int):
        tdiff = float(tdiff)
    elif not isinstance(tdiff, float):
        logging.error("the TDIFF must be a float")
        return elv

    if isinstance(alias, int):
        alias = float(alias)
    elif not isinstance(alias, float):
        logging.error("the alias must be a float")
        return elv
    
    #-------------------------------------------------------------------------
    # Calculate the elevation for each value of phi0
    for i,p0 in enumerate(phi0):
        #---------------------------------------------------------------------
        # Use only data where the angular drift between signals is not
        # identically zero with an error of zero, since this could either be a
        # sloppy flag denoting no data or an actual measurement.
        if p0 != 0.0 or phi0_e[i] != 0.0 and abs(fovflg[i]) == 1:
            # Calculate the frequency based values
            #
            # k is the wavenumber in radians per meter
            k = 2.0 * np.pi * tfreq[i] * 1.0e3 / scicon.c

            # Calculate the phase shift due to the radar cables
            del_chi = -np.pi * tfreq[i] * tdiff * 2.0e-3

            # Calculate geometry parameters
            sin_az = np.sin(bm_az[i])
            cos_az = np.cos(bm_az[i])
            az_sign = 1.0 if interfer_offset[1] > 0.0 else -1.0

            # Find the elevation angle with the maximum phase lag
            el_max = np.arcsin(az_sign * interfer_offset[2] * cos_az /
                               np.sqrt(interfer_offset[1]**2 +
                                       interfer_offset[2]**2))
            if el_max < 0.0:
                el_max = 0.0

            cos_max = np.cos(el_max)
            sin_max = np.sin(el_max)

            # Find the maximum possible phase shift
            chimax = k * (interfer_offset[0] * sin_az + interfer_offset[1] *
                          np.sqrt(cos_max**2- sin_az**2)
                          + interfer_offset[2] * sin_max)
            chimin = chimax - (alias + 1.0) * az_sign * 2.0 * np.pi
    
            # Find the right phase.  This method works for both front and
            # back lobe calculations.
            phi_temp = (fovflg[i] * (p0 - del_chi)) % (2.0 * np.pi)

            # Ensure that phi_temp falls within the proper limits
            while phi_temp > max(chimax, chimin):
                phi_temp += az_sign * 2.0 * np.pi

            while abs(phi_temp) < abs(chimin):
                phi_temp += az_sign * 2.0 * np.pi

            #--------------------------
            # Evaluate the phase shift
            if phi_temp > max(chimax, chimin):
                estr = "BUG: can't fix phase shift [{:f} ".format(phi_temp)
                estr = "{:s}not between {:f},".format(estr, chimin)
                estr = "{:s}{:f}] for index [{:d}]".format(estr, chimax, i)
                logging.critical(estr)
                elv.append(np.nan)
            else:
                # Calcualte the elevation angle and set if realistic
                cos_theta = phi_temp / k - interfer_offset[0] * sin_az
                yz_sum2 = interfer_offset[1]**2 + interfer_offset[2]**2
                sin_delta = (cos_theta * interfer_offset[2] +
                             np.sqrt((cos_theta * interfer_offset[2])**2 -
                                     yz_sum2 * (cos_theta**2 -
                                                (interfer_offset[1] *
                                                 cos_az)**2))) / yz_sum2

                if sin_delta <= 1.0:
                    new_elv = np.arcsin(sin_delta)
                    elv.append(new_elv)
                else:
                    elv.append(np.nan)
        else:
            # Pad the elevation and phase ambiguity arrays if insufficient data
            # is available to calculate the elevation
            elv.append(np.nan)

    return elv
