# NOTE TO DEVS: This needs to be completed but it requires us to 
# update the calcSun.py routines (some of them are not accurate).

import unittest

from datetime import datetime
from davitpy.utils.calcSun import *

class TestCalcSun(unittest.TestCase):
    # Note to devs: From http://aa.usno.navy.mil/data/docs/JulianDate.php
    # The Julian date for CE 2015 August  4 00:00:00.0 UT is JD 2457238.500000

    def test_getJD(self):
        expected = [1721486.0,2451545.0,2457238.5]
        in_list = [datetime(1,3,2,12),datetime(2000,1,1,12),datetime(2015,8,4)]
        #equal to [100 gregorian years,
        output = list()
        for i in in_list:
          output.append(getJD(i))
        self.assertEqual(output, expected)

    def test_calcTimeJulianCent(self):
        expected = [0.0,1.0,-67.11964407939767,-4.172046543463381]
        in_list = [2451545.0,2488070.0,0.0,2299161.0]
        #equal to [100 gregorian years,
        output = list()
        for i in in_list:
          output.append(calcTimeJulianCent(i))
        self.assertEqual(output, expected)

    def test_calcGeomMeanLongSun(self):
        expected = [280.46646,281.23659320000297,242.97481621801853,203.5844062185788]
        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
        #equal to [100 gregorian years,
        output = list()
        for i in in_list:
          output.append(calcGeomMeanLongSun(i))
        self.assertEqual(output, expected)

    def test_calcGeomMeanAnomalySun(self):
        expected = [357.52911,36356.5792463,-2415886.605976803,-149832.18689565687]
        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
        #equal to [100 gregorian years,
        output = list()
        for i in in_list:
          output.append(calcGeomMeanAnomalySun(i))
        self.assertEqual(output, expected)

    def test_calcEccentricityEarthOrbit(self):
        expected = [0.016708634,0.0166664703,0.018959353071241226,0.016881808983849455]
        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
        #equal to [100 gregorian years,
        output = list()
        for i in in_list:
          output.append(calcEccentricityEarthOrbit(i))
        self.assertEqual(output, expected)

    def test_calcSunEqOfCenter(self):
        expected = [-0.084301489437196453,-0.11637321218668388,2.0986174512791456,-1.8534353463202775]
        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
        #equal to [100 gregorian years,
        output = list()
        for i in in_list:
          output.append(calcSunEqOfCenter(i))
        self.assertEqual(output, expected)

    def test_calcSunTrueLong(self):
        expected = [280.38215851056276,281.12021998781631,245.07343366929769,201.73097087225852]
        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
        #equal to [100 gregorian years,
        output = list()
        for i in in_list:
          output.append(calcSunTrueLong(i))
        self.assertEqual(output, expected)

#    def test_calcSunTrueAnomaly(self):
#        expected = []
#        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
#        #equal to [100 gregorian years,
#        output = list()
#        for i in in_list:
#          output.append(calcSunTrueAnomaly(i))
#        self.assertEqual(output, expected)

#    def test_calcSunRadVector(self):
#        expected = []
#        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
#        #equal to [100 gregorian years,
#        output = list()
#        for i in in_list:
#          output.append(calcSunRadVector(i))
#        self.assertEqual(output, expected)

#    def test_calcSunApparentLong(self):
#        expected = []
#        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
#        #equal to [100 gregorian years,
#        output = list()
#        for i in in_list:
#          output.append(calcSunApparentLong(i))
#        self.assertEqual(output, expected)

#    def test_calcMeanObliquityOfEcliptic(self):
#        expected = []
#        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
#        #equal to [100 gregorian years,
#        output = list()
#        for i in in_list:
#          output.append(calcMeanObliquityOfEcliptic(i))
#        self.assertEqual(output, expected)

#    def test_calcObliquityCorrection(self):
#        expected = []
#        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
#        #equal to [100 gregorian years,
#        output = list()
#        for i in in_list:
#          output.append(calcObliquityCorrection(i))
#        self.assertEqual(output, expected)

#    def test_calcSunRtAscension(self):
#        expected = []
#        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
#        #equal to [100 gregorian years,
#        output = list()
#        for i in in_list:
#          output.append(calcSunRtAscension(i))
#        self.assertEqual(output, expected)

#    def test_calcSunDeclination(self):
#        expected = []
#        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
#        #equal to [100 gregorian years,
#        output = list()
#        for i in in_list:
#          output.append(calcSunDeclination(i))
#        self.assertEqual(output, expected)

#    def test_calcEquationOfTime(self):
#        expected = []
#        in_list = [0.0,1.0,-67.11964407939767,-4.172046543463381]
#        #equal to [100 gregorian years,
#        output = list()
#        for i in in_list:
#          output.append(calcEquationOfTime(i))
#        self.assertEqual(output, expected)



