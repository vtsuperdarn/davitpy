# -*- coding: utf-8 -*-
'''Virtual height models

Functions
-----------
standard_vhm : Standard virtual height model
chisham_vhm : Chisham virtual height model

References
------------
Chisham, G., T. K. Yeoman, and G. J. Sofko (2008), doi:10.5194/angeo-26-823-2008
'''
import numpy as np

def standard_vhm(slant_range, adjusted_sr=True, max_vh=400.0, hop=0.5,
                 alt=None, elv=None):
    '''Standard virtual height model

    Parameters
    ------------
    slant_range : (float)
        slant range in km
    adjusted_sr : (bool)
        This model requires a slant range that has been adjusted by hop.  If
        the slant range is the total measured slant range, set this to False.
        (default=True)
    max_vh : (float)
        Maximum allowable virtual height in km (default=400)
    hop : (float)
        Backscatter hop (default=0.5)
    alt : (float/NoneType)
        Altitude estimate (km).  If None (and no elv) defaults to 300 km
        (default=None).
    elv : (float/NoneType)
        Elevation angle (degrees), used if alt is None (default=None).

    Returns
    ---------
    vheight : (float)
        Virtual height in km.
    '''
    from davitpy.utils import Re

    vheight = np.nan

    # Adjust slant range, if necessary
    if not adjusted_sr:
        slant_range /= 2.0 * hop

    # Set the altitude, if not provided    
    if alt is None:
        if elv is None:
            # Set default altitude to 300 km
            alt = 300.0
        else:
            # If you have elevation but not altitude, then you calculate
            # altitude, and elevation will be adjusted anyway
            alt = np.sqrt(Re**2 + slant_range**2 + 2.0 * slant_range * Re
                          * np.sin(np.radians(elv))) - Re

    # Model divides data by near and far range.  
    if slant_range < 150.0:
        vheight = (slant_range / 150.0) * 115.0
    else:
        # Model divides data by ionospheric (0.5, 1.5) and ground (1.0, 2.0)
        if hop != np.floor(hop):
            # Ionospheric virtual heights are defined up to slant ranges of 800
            if slant_range <= 600.0:
                vheight = 115.0
            elif slant_range <= 800.0:
                vheight = 115.0 + (slant_range - 600.0) / 200.0 * (alt - 115.0)
            else:
                vheight = max_vh
        else:
            # Ground virtual heights are defined up to slant ranges of 500 km.
            if slant_range <= 300.0:
                vheight = 115.0
            elif slant_range <= 500.0:
                vheight = 115.0 + (slant_range - 300.0) / 200.0 * (alt - 115.0)
            else:
                vheight = max_vh

    # The virtual height at this point is correct for half hop ionospheric and
    # one hop ground backscatter.  Adjust virtual heights for more hops to
    # return straight-line virtual height for ionospheric backscatter and
    # straight-line path to the last refraction point for groundscatter
    if hop > 1.0 and not np.isnan(vheight):
        vheight *= 2.0 * hop if hop != np.floor(hop) else 2.0 * (hop - 0.5)
        
    return vheight

def chisham_vhm(slant_range, vhmtype=None, hop_output=False):
    '''Chisham virtual height model, only handles ionospheric backscatter

    Parameters
    ------------
    slant_range : (float)
        Total measured slant range in km
    vhmtype : (str/NoneType)
        Model type, including "E1"=.5-hop E, "F1"=.5-hop F, "F3"=1.5-hop F,
        and None=use slant range to decide propagation path. (default=None)
    hop_output : (bool)
        Output hop (as decided by slant range and/or model type) (default=False)

    Returns
    ---------
    vheight : (float)
        Virtual height in km.
    hop : (float)
        If hop_output is True, hop will also be output
    '''
    vout = [np.nan, 0] if hop_output else [np.nan] 
    srange_2 = slant_range * slant_range

    if vhmtype is None:
        if slant_range <= 787.5:
            vhmtype = "E1"
        elif slant_range > 787.5 and slant_range <= 2137.5:
            vhmtype = "F1"
        elif slant_range > 2137.5:
            vhmtype = "F3"
            
    if vhmtype == "E1":
        # .5-hop E-region
        vout[0] = 108.974 + 0.0191271 * slant_range + 6.68283e-5 * srange_2
        if hop_output:
            vout[1] = 0.5
    elif vhmtype == "F1":
        # .5-hop F-region
        vout[0] = 384.416 - 0.178640 * slant_range + 1.81405e-4 * srange_2
        if hop_output:
            vout[1] = 0.5
    elif vhmtype == "F3":
        # 1.5 hop F-region
        vout[0] = 1098.28 - 0.354557 * slant_range + 9.39961e-5 * srange_2
        if hop_output:
            vout[1] = 1.5
 
    return vout if len(vout) > 1 else vout[0]
