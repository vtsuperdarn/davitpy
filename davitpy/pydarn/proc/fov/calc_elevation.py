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
             asep=None, ecor=None, phi_sign=None, tdiff=None, del_chi=None,
             del_chif=0.0, alias=0.0, fov='front'):
    """Calculate the elevation angle for observations along a beam at a radar

    Parameters
    -----------
    beam : (class `pydarn.sdio.radDataTypes.beamData`)
        Data for a single radar and beam along all range gates at a given time
    hard : (class `pydarn.radar.radStruct.site` or NoneType)
        Radar hardware data or None to load here (default=None)
    asep : (float or NoneType)
        Antenna separation in meters or None to calculate (default=None)
    ecor : (float or NoneType)
        Elevation correction in radians based on the altitude difference between
        the radar and the interferometer or None to calculate (default=None)
    phi_sign : (float or NoneType)
        Sign change determined by the relative location of the interferometer
        to the radar or None to calculate (default=None)
    tdiff : (float or NoneType)
        The relative time delay of the signal paths from the interferometer
        array to the receiver and the main array to the reciver (microsec) or
        None to use the value supplied by the hardware file (default=None)
    del_chi : (float or NoneType)
        The total phase shift caused by the cables and the filter in radians.
        If None, will be calculated. (default=None)
    del_chif : (float)
        Additional phase shift in radians (default=0.0)
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
    asep : (float or NoneType)
        Antenna separation in meters or None to calculate (default=None)
    ecor : (float or NoneType)
        Elevation correction in radians based on the altitude difference between
        the radar and the interferometer or None to calculate (default=None)
    phi_sign : (float or NoneType)
        Sign change determined by the relative location of the interferometer
        to the radar or None to calculate (default=None)
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
    assert isinstance(asep, float) or asep is None, \
        logging.error('the asep should be a float or NoneType')
    assert isinstance(ecor, float) or ecor is None, \
        logging.error('the ecor should be a float or NoneType')
    assert isinstance(phi_sign, float) or phi_sign is None, \
        logging.error('the phi_sign should be a float or NoneType')
    assert isinstance(tdiff, float) or tdiff is None, \
        logging.error('the tdiff should be a float or NoneType')
    assert isinstance(del_chi, float) or del_chi is None, \
        logging.error('the del_chi should be a float or NoneType')
    assert isinstance(del_chif, float), \
        logging.error('the del_chif should be a float')
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

    # If desired, calculate the radar specific variables
    if asep is None or ecor is None or phi_sign is None:
        # Calculate the elevation angle correction due to differences in
        # altitude between the interferometer and the radar and determine
        # whether the interferometer is in front or behind the radar
        asep = np.sqrt(np.dot(hard.interfer, hard.interfer)) # meters
        phi_sign = 1.0 if hard.interfer[1] > 0.0 else -1.0
        ecor = phi_sign * hard.phidiff * np.arcsin(hard.interfer[2] / asep)

    #-------------------------------------------------------------------------
    # Calculate the beam-specific variables
    #
    # Phi is the beam direction off the radar boresite assuming an elevation
    # angle of zero.  This is calculated by the hardware routine 'beamToAzim'
    # located in pydarn.radar.radStruct
    cos_phi = np.cos(np.radians(hard.beamToAzim(beam.bmnum) - hard.boresite))

    # k is the wavenumber in radians per meter
    k = 2.0 * np.pi * beam.prm.tfreq * 1.0e3 / scicon.c

    # Calculate the phase shift due to the radar cables and any additional
    # amount (due to the radar mode, etc.) unless a phase shift was supplied
    if del_chi is None:
        del_chi = -np.pi * beam.prm.tfreq * tdiff * 2.0e-3 - del_chif

    # Find the maximum possible phase shift
    chimax = phi_sign * k * asep * cos_phi
    chimin = chimax - (alias + 1.0) * phi_sign * 2.0 * np.pi
    
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
                phi_temp += phi_sign * 2.0 * np.pi
                amb_temp += phi_sign

            while abs(phi_temp) < abs(chimin):
                phi_temp += phi_sign * 2.0 * np.pi
                amb_temp += phi_sign

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
                cos_theta = phi_temp / (k * asep)
                sin2_delta = cos_phi**2 - cos_theta**2

                if sin2_delta >= 0.0:
                    sin_delta = np.sqrt(sin2_delta)
                    if sin_delta <= 1.0:
                        new_elv = np.degrees(np.arcsin(sin_delta) + ecor)
                        elv[i] = new_elv
                        phase_amb[i] = int(amb_temp)

    return elv, phase_amb, hard, asep, ecor, phi_sign

#---------------------------------------------------------------------------
def calc_elv_w_err(beam, phi0_attr="phi0", phi0_e_attr="phi0_e", hard=None,
                   asep=None, ecor=None, phi_sign=None, bmaz_e=0.0,
                   boresite_e=0.0, ix_e=0.0, iy_e=0.0, iz_e=0.0, tdiff=None,
                   tdiff_e=0.0, alias=0.0, fov='front'):
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
    asep : (float or NoneType)
        Antenna separation in meters or None to calculate (default=None)
    ecor : (float or NoneType)
        Elevation correction in radians based on the altitude difference between
        the radar and the interferometer or None to calculate (default=None)
    phi_sign : (float or NoneType)
        Sign change determined by the relative location of the interferometer
        to the radar or None to calculate (default=None)
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
    asep : (float or NoneType)
        Antenna separation in meters or None to calculate (default=None)
    ecor : (float or NoneType)
        Elevation correction in radians based on the altitude difference between
        the radar and the interferometer or None to calculate (default=None)
    phi_sign : (float or NoneType)
        Sign change determined by the relative location of the interferometer
        to the radar or None to calculate (default=None)
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
    assert isinstance(asep, float) or asep is None, \
        logging.error('the asep should be a float or NoneType')
    assert isinstance(ecor, float) or ecor is None, \
        logging.error('the ecor should be a float or NoneType')
    assert isinstance(phi_sign, float) or phi_sign is None, \
        logging.error('the phi_sign should be a float or NoneType')
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
        phi0_e = [np.nan for p in phi0]

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

    # If desired, calculate the radar specific variables
    if asep is None or ecor is None or phi_sign is None:
        # Calculate the elevation angle correction due to differences in
        # altitude between the interferometer and the radar and determine
        # whether the interferometer is in front or behind the radar
        asep = np.sqrt(np.dot(hard.interfer, hard.interfer)) # meters
        phi_sign = 1.0 if hard.interfer[1] > 0.0 else -1.0
        ecor = phi_sign * hard.phidiff * np.arcsin(hard.interfer[2] / asep)

    # Calculate two of the error coefficients for the interferometer location
    ecor_coef = phi_sign * hard.phidiff / asep
    asin_ecor = np.sqrt(1.0 - (hard.interfer[2] / asep)**2)

    #-------------------------------------------------------------------------
    # Calculate the beam-specific variables
    #
    # Phi is the beam direction off the radar boresite assuming an elevation
    # angle of zero.  This is calculated by the hardware routine 'beamToAzim'
    # located in pydarn.radar.radStruct
    bmaz = hard.beamToAzim(beam.bmnum)
    cos_phi = np.cos(np.radians(bmaz - hard.boresite))

    # k is the wavenumber in radians per meter
    k = 2.0 * np.pi * beam.prm.tfreq * 1.0e3 / scicon.c

    # Calculate the phase shift due to the radar cables
    del_chi = -np.pi * beam.prm.tfreq * tdiff * 2.0e-3

    # Find the maximum possible phase shift
    chimax = phi_sign * k * asep * cos_phi
    chimin = chimax - (alias + 1.0) * phi_sign * 2.0 * np.pi
    
    #-------------------------------------------------------------------------
    # Calculate the elevation for each value of phi0
    for i,p0 in enumerate(phi0):
        #---------------------------------------------------------------------
        # Use only data where the angular drift between signals is not
        # identically zero with an error of zero, since this could either be a
        # sloppy flag denoting no data or an actual measurement.
        if p0 != 0.0 or np.isnan(phi0_e[i]) or phi0_e[i] != 0.0:
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
                phi_temp += phi_sign * 2.0 * np.pi
                amb_temp += phi_sign

            while abs(phi_temp) < abs(chimin):
                phi_temp += phi_sign * 2.0 * np.pi
                amb_temp += phi_sign

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
                cos_theta = phi_temp / (k * asep)
                sin2_delta = cos_phi**2 - cos_theta**2

                if sin2_delta >= 0.0:
                    sin_delta = np.sqrt(sin2_delta)
                    if sin_delta <= 1.0:
                        # Calculate the elevation
                        new_elv = np.degrees(np.arcsin(sin_delta) + ecor)
                        elv[i] = new_elv
                        phase_amb[i] = int(amb_temp)

                        # Now that the elevation was calculated, attempt to
                        # find the elevation error, using the propagation of
                        # error to propagate all possible uncertainties
                        asin_der = 1.0 / np.sqrt(sin2_delta - sin2_delta**2)

                        # Calculate the error terms for beam azimuth and
                        # boresite
                        term_bmaz = 0.0
                        term_bore = 0.0
                        if((not np.isnan(bmaz_e) and bmaz_e > 0.0) or
                           (not np.isnan(boresite_e) and boresite_e > 0.0)):
                            sin_phi = np.sin(np.radians(bmaz - hard.boresite))

                            if not np.isnan(bmaz_e) and bmaz_e > 0.0:
                                temp = (-bmaz * sin_phi * cos_phi * asin_der)**2
                                term_bmaz = bmaz_e * bmaz_e * temp
                            if not np.isnan(boresite_e) and boresite_e > 0.0:
                                temp = (hard.boresite * sin_phi * cos_phi *
                                        asin_der)**2
                                term_bore = boresite_e * boresite_e * temp

                        # Calculate the error terms for the interferometer
                        # location
                        term_x = 0.0
                        term_y = 0.0
                        term_z = 0.0
                        if((not np.isnan(ix_e) and ix_e > 0.0) or
                           (not np.isnan(iy_e) and iy_e > 0.0)):
                            temp = (cos_theta * cos_theta * asin_der +
                                    ecor_coef * hard.interfer[2] /
                                    (asep * asep * asin_ecor))

                            if not np.isnan(ix_e) and ix_e > 0.0:
                                term_x = (ix_e * hard.interfer[0] * temp)**2

                            if not np.isnan(iy_e) and iy_e > 0.0:
                                term_y = (iy_e * hard.interfer[1] * temp)**2

                        if not np.isnan(iz_e) and iz_e > 0.0:
                            temp = (cos_theta**2 * asin_der * hard.interfer[2]
                                    / (asep * asep) - ecor_coef * asin_ecor)
                            term_z = iz_e * iz_e * temp * temp
                        
                        # Calculate the error terms for tdiff
                        term_tdiff = 0.0
                        if not np.isnan(tdiff_e) and tdiff_e > 0.0:
                            temp = (2.0 * np.pi * beam.prm.tfreq * cos_theta /
                                    (1000.0 * asep * k * asin_der))**2
                            term_tdiff = temp * tdiff_e * tdiff_e

                        # Calculate the error term for phase lag
                        term_phi0 = 0.0
                        if not np.isnan(phi0_e[i]) and phi0_e[i] > 0.0:
                            temp = cos_theta * asin_der / (k * asep)
                            term_phi0 = (phi0_e[i] * temp)**2

                        # Calculate the elevation error, adding in quadrature
                        temp = np.sqrt(term_phi0 + term_tdiff + term_z + term_y
                                       + term_x + term_bore + term_bmaz)

                        # If the elevation error is identically zero, assume
                        # that no error could be obtained
                        elv_e[i] = np.nan if temp == 0.0 else temp

    return elv, elv_e, phase_amb, hard, asep, ecor, phi_sign


#---------------------------------------------------------------------------
def calc_elv_list(phi0, phi0_e, fovflg, cos_phi, tfreq, asep, ecor, phi_sign,
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
    cos_phi : (list of floats)
        Cosine of the azimuthal angle between the beam and the radar boresite
    tfreq : (list of floats)
        Transmission frequency (kHz)
    asep : (float)
        Antenna separation in meters or None to calculate
    ecor : (float)
        Elevation correction in radians based on the altitude difference between
        the radar and the interferometer
    phi_sign : (float)
        Sign change determined by the relative location of the interferometer
        to the radar
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

    if isinstance(ecor, int):
        ecor = float(ecor)
    elif not isinstance(ecor, float):
        logging.error("the elevation correction must be a float")
        return elv

    if isinstance(phi_sign, int):
        phi_sign = float(phi_sign)
    elif not isinstance(phi_sign, float):
        logging.error("the phase lag sign must be a float")
        return elv

    if isinstance(asep, int):
        asep = float(asep)
    elif not isinstance(asep, float):
        logging.error("the interferometer distance must be a float")
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

            # Find the maximum possible phase shift
            chimax = phi_sign * k * asep * cos_phi[i]
            chimin = chimax - (alias + 1.0) * phi_sign * 2.0 * np.pi
    
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
            phi_temp = (fovflg[i] * (p0 - del_chi)) % (2.0 * np.pi)

            # Ensure that phi_temp falls within the proper limits
            while phi_temp > max(chimax, chimin):
                phi_temp += phi_sign * 2.0 * np.pi

            while abs(phi_temp) < abs(chimin):
                phi_temp += phi_sign * 2.0 * np.pi

            #--------------------------
            # Evaluate the phase shift
            if phi_temp > max(chimax, chimin):
                estr = "BUG: can't fix phase shift [{:f} not ".format(phi_temp)
                estr = "{:s}between {:f},{:f}] for".format(estr, chimin, chimax)
                estr = "{:s} index [{:d}]".format(i)
                logging.critical(estr)
                elv.append(np.nan)
            else:
                # Calcualte the elevation angle and set if realistic
                cos_theta = phi_temp / (k * asep)
                sin2_delta = (cos_phi[i] * cos_phi[i]) - (cos_theta * cos_theta)

                if sin2_delta >= 0.0:
                    sin_delta = np.sqrt(sin2_delta)
                    if sin_delta <= 1.0:
                        new_elv = np.arcsin(sin_delta) + ecor
                        elv.append(new_elv)
                    else:
                        elv.append(np.nan)
                else:
                    elv.append(np.nan)
        else:
            # Pad the elevation and phase ambiguity arrays if insufficient data
            # is available to calculate the elevation
            elv.append(np.nan)

    return elv
