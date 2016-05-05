# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""Mass Spectrometer and Incoherent Scatter

Functions
------------------
msis.msisFort.gtd7
------------------

Parameters
----------
IYD :
    year and day as YYDDD (day of year from 1 to 365 (or 366))
    (Year ignored in current model)
SEC :
    UT (SEC)
ALT :
    altitude (KM)
GLAT :
    geodetic latitude (DEG)
GLONG :
    geodetic longitude (DEG)
STL :
    local aparent solar time (HRS; see Note below)
F107A :
    81 day average of F10.7 flux (centered on day DDD)
F107 :
    daily F10.7 flux for previous day
AP :
    magnetic index (daily) OR when SW(9)=-1., array containing:
    * (1) daily AP
    * (2) 3 HR AP index FOR current time
    * (3) 3 HR AP index FOR 3 hrs before current time
    * (4) 3 HR AP index FOR 6 hrs before current time
    * (5) 3 HR AP index FOR 9 hrs before current time
    * (6) average of height 3 HR AP indices from 12 TO 33 HRS prior to current time
    * (7) average of height 3 HR AP indices from 36 TO 57 HRS prior to current time
MASS :
    mass number (only density for selected gass is calculated. MASS 0 is temperature.
    MASS 48 for ALL. MASS 17 is Anomalous O ONLY.)

Returns
-------
D(1) :
    HE number density(CM-3)
D(2) :
    O number density(CM-3)
D(3) :
    N2 number density(CM-3)
D(4) :
    O2 number density(CM-3)
D(5) :
    AR number density(CM-3)                       
D(6) :
    total mass density(GM/CM3)
D(7) :
    H number density(CM-3)
D(8) :
    N number density(CM-3)
D(9) :
    Anomalous oxygen number density(CM-3)
T(1) :
    exospheric temperature
T(2) :
    temperature at ALT
  
"""
import logging

try:
    from msisFort import *
except Exception as e:
    logging.exception(__file__ + ' -> models.msis: ' + str(e))


def getF107Ap(mydatetime=None):
    """
    Obtain F107 and AP required for MSIS input from tabulated values in IRI data.

    Parameters
    ----------
    mydatetime : Optional[datetime]
        defaults to last tabulated value

    Returns
    -------
    dictOut : dict
      containing:
      * datetime: the date and time as a python datetime object
      * f107: daily f10.7 flux for previous day
      * f107a: 81 day average of f10.7 flux (centered on date)
      * ap: magnetic index containing:
        * (1) daily AP
        * (2) 3 HR AP index for current time
        * (3) 3 HR AP index for 3 hours before current time
        * (4) 3 HR AP index for 6 hours before current time
        * (5) 3 HR AP index for 9 hours before current time
        * (6) Average of eight 3 hour AP indicies from 12 to 33 hrs prior to current time
        * (7) Average of eight 3 hour AP indicies from 36 to 57 hrs prior to current time

    """
    from davitpy.models import iri
    from datetime import datetime
    from numpy import mean, floor

    # Get current path to IRI module
    path = iri.__file__.partition('__init__.py')[0]

    # open apf107.dat file
    with open('{}apf107.dat'.format(path), 'r') as fileh:
        data = []
        for line in fileh:
            data.append(line)

    # read into array
    # (cannot use genfromtext because some columns are not separated by anything)
    tdate = []
    tap = []
    tapd = []
    tf107 = []
    tf107a = []
    tf107y = []
    for ldat in data:
        yy = int(ldat[1:3])
        year = 1900 + yy if (yy >= 58) else 2000 + yy
        tdate.append(datetime(year, int(ldat[4:6]), int(ldat[7:9])).date())
        ttap = []
        for iap in xrange(8):
            ttap.append(int(ldat[9 + 3 * iap:9 + 3 * iap + 4]))
        tap.append(ttap)
        tapd.append(int(ldat[33:36]))
        tf107.append(float(ldat[39:44]))
        tf107a.append(float(ldat[44:49]))
        tf107y.append(float(ldat[49:54]))

    # Get required datetime
    dictOut = {}
    if mydatetime is None:
        dictOut['datetime'] = datetime(
            tdate[-1].year, tdate[-1].month, tdate[-1].day)
    elif mydatetime.date() <= tdate[-1]:
        dictOut['datetime'] = mydatetime
    else:
        logging.error('Invalid date {}'.format(mydatetime))
        logging.error(
            'Date must be in range {} to {}'.format(tdate[0], tdate[-1]))
        return

    # Find entry for date
    dtInd = tdate.index(dictOut['datetime'].date())
    # Find hour index
    hrInd = int(floor(dictOut['datetime'].hour / 3.))

    # f107 output
    dictOut['f107'] = tf107[dtInd - 1]
    dictOut['f107a'] = tf107a[dtInd]

    # AP output
    ttap = [tap[dtInd][hrInd - i] for i in range(hrInd + 1)]
    for id in xrange(3):
        for ih in xrange(8):
            ttap.append(tap[dtInd - id - 1][-ih - 1])
    dictOut['ap'] = [tapd[dtInd],
                     ttap[0],
                     ttap[1],
                     ttap[2],
                     ttap[3],
                     mean(ttap[4:13]),
                     mean(ttap[13:26])
                     ]

    return dictOut
