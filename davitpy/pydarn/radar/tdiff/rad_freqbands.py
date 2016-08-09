#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# rad_freqbands.py, Angeline G. Burrell (AGB), UoL
#
# Comments: Routines to define and retrieve frequency bands for the SuperDARN
#           radars.  These would be better saved and accessed through a table,
#           so as to allow for temporal updates.
#-----------------------------------------------------------------------------
'''Define and retrieve transmission frequency bands for the SuperDARN radars.

Parameters
----------------------------------------------------------------------------
rad_band_num : (dict)
rad_min : (dict)
rad_max : (dict)
id_to_code : (dict)
---------------------------------------------------------------------------

Classes
----------------------------------------------------------------------------
radFreqBands
----------------------------------------------------------------------------

Moduleauthor
------------
Angeline G. Burrell (AGB), 25 July 2016, University of Leicester (UoL)
'''
import logging

# Define the frequency bands for different radars
#
# The radar band numbers allow new frequency bands to be added in numerical
# order whilst maintaining backward compatibility
rad_band_num = {
    'ade':[0,1,2,3,4,5,6,7,8],
    'adw':[0,1,2,3,4,5,6,7,8],
    'cly':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
           25,26],
    'han': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14],
    'inv': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
            25,26,27],
    'mcm':[0,1,2,3,4,5,6,7,8],
    'pgr': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
            25,26,27],
    'pyk': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
    'rkn': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
            25,26,27],
    'sas': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],
    'sto': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,
            23,24,25,26],}

# Radar frequencies saved in kHz
rad_min = {
    'ade':[10400, 10900, 12000, 13000, 14500, 15000, 16000, 17000, 18000],
    'adw':[10400, 10900, 12000, 13000, 14500, 15000, 16000, 17000, 18000],
    'cly':[8000, 8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500,
           13000, 13469, 13929, 14500, 15040, 15500, 16000, 16500, 17000, 17500,
           18000, 18500, 19000, 19500, 20040, 20500],
    'han':[8305, 8965, 9900, 11075, 11550, 12370, 13200, 15010, 16210, 16555,
           17970, 18850, 19415, 19705, 19800],
    'inv':[8000, 8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500,
           13000,  13500, 14000, 14500, 15000, 15500, 16000, 16500, 17000,
           17500, 18000, 18500, 19000,19500,20000,20500,21000,21500],
    'mcm':[10100, 10700, 11400, 12500, 13700, 14400, 15200, 17000, 18400],
    'pgr':[8000, 8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500,
           13000,  13500, 14000, 14500, 15000, 15500, 16000, 16500, 17000,
           17500, 18000, 18500, 19000,19500,20000,20500,21000,21500],
    'pyk':[8000, 8430, 8985, 10155, 10655, 11290, 11475, 12105, 12305, 12590,
           13360, 13875, 14400, 15805, 16500, 16820, 18175, 18835, 19910,
           10155],
    'rkn':[8000, 8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500,
           13000,  13419, 14000, 14500, 15000, 15500, 16000, 16500, 17000,
           17500, 18000, 18500, 19000,19500,20000,20500,21000,21500],
    'sas':[8000, 8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500,
           13000, 13500, 14000, 14500, 15000, 15500, 16000, 16500, 17000, 17500,
           18000, 18500, 19000, 19500, 20000],
    'sto': [8202, 8357, 8857, 8974, 9150, 9450, 10025, 11181, 11274, 11458,
            11940, 12240, 12300, 12515, 12539, 13285, 13340, 15022, 16370,
            16689, 16720,  16799, 17910, 17982, 18778, 18890, 19674],}

rad_max = {
    'ade':[10700, 11200, 12300, 13300, 14800, 15300, 16300, 17300, 18300],
    'adw':[10700, 11200, 12300, 13300, 14800, 15300, 16300, 17300, 18300],
    'cly':[8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500, 13000,
           13469, 13929, 14500, 15040, 15500, 16000, 16500, 17000, 17500, 18000,
           18500, 19000, 19500, 20040, 20500, 21000],
    'han':[8335, 9040, 9985, 11275, 11600, 12415, 13260, 15080, 16360, 16615,
           18050, 18865, 19680, 19755, 19990],
    'inv':[8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500,
           13000,  13500, 14000, 14500, 15000, 15500, 16000, 16500, 17000,
           17500, 18000, 18500, 19000,19500,20000,20500,21000,21500,22000],
    'mcm':[10400, 11000, 11700, 12800, 14000, 14700, 15500, 17300, 18700],
    'pgr':[8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500,
           13000,  13500, 14000, 14500, 15000, 15500, 16000, 16500, 17000,
           17500, 18000, 18500, 19000,19500,20000,20500,21000,21500,22000],
    'pyk':[8195, 8850, 9395, 10655, 11175, 11450, 11595, 12235, 12510, 13280,
           13565, 13995, 15015, 16365, 16685, 17475, 18770, 18885, 20000,
           11175],
    'rkn':[8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500,
           13000,  13419, 14000, 14500, 15000, 15500, 16000, 16500, 17000,
           17500, 18000, 18500, 19000,19500,20000,20500,21000,21500,22000],
    'sas':[8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500, 13000,
           13500, 14000, 14500, 15000, 15500, 16000, 16500, 17000, 17500,
           18000, 18500, 19000, 19500, 20000, 20500],
    'sto': [8297, 8423, 8931, 8980, 9450, 9750, 10037, 11188, 11286, 11469,
            12514, 12300, 12240, 12525, 12585, 13313, 13352, 15028, 16455,
            16700, 16748, 16815, 17953, 17990, 18830, 18905, 19686],}

# Allow use of both 3-letter code and numerical IDs
id_to_code = {
    5:'sas', 6:'pgr', 8:'sto', 9:'pyk', 10:'han', 20:'mcm', 64:'inv', 65:'rkn',
    209:'ade', 208:'adw',}

#-----------------------------------------------------------------------------
class radFreqBands(object):
    '''Contains the transmission frequency bands for a given radar

    Parameters
    ------------
    rad : (str or int)
       3-character radar code or numerical ID number

    Attributes
    ------------
    rad_code : (str)
        Radar 3-character code (lowercase only)
    stid : (int)
        Radar numerical ID
    tbands : (list)
        Transmision frequency band numbers
    tmins : (list)
        List of transmission frequency band lower boundaries (kHz)
    tmaxs : (list)
        List of transmission frequency band upper boundaries (kHz)

    Methods
    ---------
    get_tband_max_min
    get_mean_tband_freq
    get_tfreq_band_num

    written by AGB 25/07/16
    '''
    def __init__(self, rad=None):

        # Assign the radar IDs
        if id_to_code.has_key(rad):
            self.rad_code = id_to_code[rad]
            self.stid = rad
        else:
            self.rad_code = rad
            self.stid = None

            if rad is not None:
                for stid in id_to_code.keys():
                    if id_to_code[stid] is rad.lower():
                        self.stid = stid
                        break
                    
        # Assign the frequency bands
        try:
            self.tbands = rad_band_num[self.rad_code]
            self.tmins = rad_min[self.rad_code]
            self.tmaxs = rad_max[self.rad_code]
        except:
            self.tbands = list()
            self.tmins = list()
            self.tmaxs = list()

    def __str__(self):
        '''Object string representation

        Parameters
        ----------
        None

        Returns
        --------
        ostr : (str)
            Formatted output denoting the radar, the number of frequency bands,
            and the frequency bands in MHz

        Example
        --------
        In[1]: fb = davitpy.pydarn.radar.tdiff.rad_freqbands.radFreqBands(10)
        In[2]: print fb
        Radar transmission frequency bands:
            Code: han       ID: 10
            Number of frequency bands spanning 8.305-19.990 MHz: 15
                Band Min_Freq-Max_Freq (MHz)
                00 8.305-8.335
                01 8.965-9.040
                02 9.900-9.985
                03 11.075-11.275
                04 11.550-11.600
                05 12.370-12.415
                06 13.200-13.260
                07 15.010-15.080
                08 16.210-16.360
                09 16.555-16.615
                10 17.970-18.050
                11 18.850-18.865
                12 19.415-19.680
                13 19.705-19.755
                14 19.800-19.990
        '''
        ostr = "Radar transmission frequency bands:\n"
        # Add radar name
        ostr = "{:s}\tCode: {:s}\tID: {:d}\n".format(ostr, self.rad_code,
                                                     self.stid)
        # Add number of frequency bands
        ostr = "{:s}\tNumber of frequency bands spanning ".format(ostr)
        ostr = "{:s}{:.3f}-{:.3f} ".format(ostr, min(self.tmins) * 1.0e-3,
                                           1.0e-3 * max(self.tmaxs))
        ostr = "{:s}MHz: {:d}\n".format(ostr, len(self.tbands))
        # Add the frequency bands
        ostr = "{:s}\t\tBand Min_Freq-Max_Freq (MHz)\n".format(ostr)
        for i,mm in enumerate(self.tmins):
            ostr = "{:s}\t\t{:02d} {:.3f}-{:.3f}\n".format(ostr, self.tbands[i],
                                                           mm * 1.0e-3, 1.0e-3 *
                                                           self.tmaxs[i])
        return ostr

    #--------------------------------------------------------------------------
    def get_tband_max_min(self, tfreq):
        '''Return the maximum and minimum frequency for the band that the
        supplied frequency falls into

        Parameters
        -------------
        tfreq : (int)
            Transmision frequency in kHz

        Returns
        -----------
        min_freq : (int)
            Minimum frequency in kHz, -1 if unavailable
        max_freq : (int)
            Maximum frequency in kHz, -1 if unavailable
        '''
        #------------------------------------------------
        # Cycle through the transmission frequency bands
        for i,t in enumerate(self.tmins):
            if tfreq - t >= 0 and self.tmaxs[i] - tfreq >= 0:
                return(t, self.tmaxs[i])
        
        logging.warn("Unknown transmission freq [{:d} kHz]".format(tfreq))
        return(-1, -1)

    def get_mean_tband_freq(self, tband):
        ''' Return the maximum and minimum frequency for the band that the
        supplied frequency falls into

        Parameters
        -------------
        tband : (int)
            Transmision band number

        Returns
        -----------
        mean_freq : (int)
            Mean frequency in kHz, -1 if unavailable
        '''
        mean_freq = -1
            
        #--------------------------------------------
        # Ensure that band information is available
        if len(self.tmins) > tband:
            mean_freq = int((self.tmaxs[tband] + self.tmins[tband])
                            / 2.0)
        else:
            estr = "unknown transmission freq band [{:}]".format(tband)
            logging.warn(estr)

        return mean_freq

    def get_tfreq_band_num(self, tfreq):
        ''' Retrieve the transmision frequency band number for a specified
        frequency

        Parameters
        -----------
        tfreq : (int)
            Transmission frequency in kHz

        Returns
        ---------
        tband : (int)
            Transmission frequency band number, -1 if unavailable
        '''
        #--------------------------------------------
        # Cycle through the different frequency bands
        for i,t in enumerate(self.tmins):
            if t <= tfreq and tfreq <= self.tmaxs[i]:
                return(self.tbands[i])
        
        logging.warn("no band for frequency [{:} kHz]".format(tfreq))
        return(-1)
