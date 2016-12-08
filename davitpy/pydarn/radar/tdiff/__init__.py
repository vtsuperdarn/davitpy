# -*- coding: utf-8 -*-
# 2016 University of Leicester
"""
Subpackage
----------
pydarn.radar.tdiff
    This subpackage contains routines to estimate the tdiff value for each
    radar at a specified frequency band.

Modules
-------
bscatter_distribution
    Routines to find the distribution about a known locaiton
calc_tdiff
    Routines to select data and estimate tdiff
rad_freqbands
    Defines frequency bands for the radars
simplex
    Simplex minimizaiton routine
"""

import rad_freqbands
import simplex
import bscatter_distribution
import calc_tdiff
import test_tdiff
