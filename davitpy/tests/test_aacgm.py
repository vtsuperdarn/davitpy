import unittest

from datetime import datetime
from davitpy.models.aacgm import aacgmConv
from davitpy.models.aacgm import aacgmConvArr
from davitpy.models.aacgm import mltFromEpoch
from davitpy.models.aacgm import mltFromYmdhms
from davitpy.models.aacgm import mltFromYrsec


class TestAacgmConv(unittest.TestCase):
    # Note to devs: I compared our AACGM with 
    # http://ccmc.gsfc.nasa.gov/requests/instant/instant1.php?model=AACGM&type=1
    # using: lat = 52, lon = 270, altitude = 0 and year = 1995 
    # (website defaults to 1995) and we the same output. At the
    # time I tested, website gave (63.05985, 338.8920) for result.
    # asreimer: 2 Aug, 2015

    def test_aacgmConv_0km_1995(self):
        expected = (63.05985085868462, -21.107952843174143, 1.0)
        output = aacgmConv(52., 270., 0., 1995, 0, coeff_prefix=None)
        self.assertEqual(output, expected)

    def test_aacgmConv_600km_2002(self):
        expected = (63.93808095365087, -20.75649127199887, 1.0)
        output = aacgmConv(52., 270., 600., 2002, 0, coeff_prefix=None)
        self.assertEqual(output, expected)

    def test_aacgmConv_600km_2002_from_aacgm_to_geo(self):
        expected = (52.11664067502611, -90.10968620918827, 1.0)
        output = aacgmConv(63.93808095365087, -20.75649127199887, 600., 2002, 1, coeff_prefix=None)
        self.assertEqual(output, expected)

class TestAacgmConvArr(unittest.TestCase):

    def test_aacgmConvArr_0km_1995_len1_input(self):
        expected = ([63.05985085868462], [-21.107952843174143], [1.0])
        output = aacgmConvArr([52.], [270.], [0.], 1995, 0, coeff_prefix=None)
        self.assertEqual(output, expected)

    def test_aacgmConvArr_2008_len7_input(self):
        lat_out = [-74.10124102798503, -44.70853865311321, -33.69911395909726, 
                    12.274024563452556, 41.94993340926247,  49.57374504212498, 
                    83.16843219337686]
        lon_out = [18.913239494175702, -32.98087936041418, 8.583539421920076, 
                   31.274073489784715, 76.848898337102, 133.36685772530652,  
                   171.88003168447253]
        conv_out = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        expected = (lat_out,lon_out, conv_out)

        lats = [-90,-52,-45,0,45,52,90]
        lons = [-180,-120,-60,-43.1,0,60,120]
        heights = [0,100,200,300,400,500,600]
        output = aacgmConvArr(lats,lons,heights, 2008, 0, coeff_prefix=None)
        self.assertEqual(output, expected)

class TestMltFromEpoch(unittest.TestCase):

    def test_mltFromEpoch_mlon220(self):
        expected = 15.560846722604682
        # epoch made from:
        # (datetime(2010,10,1,5,30,10)-datetime(1970,1,1)).total_seconds()
        epoch = 1285911010.0
        output = mltFromEpoch(epoch,220)
        self.assertEqual(output, expected)

    def test_mltFromEpoch_mlon45(self):
        expected = 3.8941800559380155
        # epoch made from:
        # (datetime(2010,10,1,5,30,10)-datetime(1970,1,1)).total_seconds()
        epoch = 1285911010.0
        output = mltFromEpoch(epoch,45)
        self.assertEqual(output, expected)

class TestMltFromYmdhms(unittest.TestCase):

    def test_mltFromYmdhms_mlon220(self):
        expected = 15.560846722604682
        output = mltFromYmdhms(2010,10,1,5,30,10,220)
        self.assertEqual(output, expected)

    def test_mltFromYmdhms_mlon45(self):
        expected = 3.8941800559380155
        output = mltFromYmdhms(2010,10,1,5,30,10,45)
        self.assertEqual(output, expected)

class TestMltFromYrsec(unittest.TestCase):

    def test_mltFromYrsec_mlon220(self):
        expected = 15.560846722604682
        # yrsec made from:
        # (datetime(2010,10,1,5,30,10)-datetime(2010,1,1)).total_seconds()
        output = mltFromYrsec(2010,23607010,220)
        self.assertEqual(output, expected)

    def test_mltFromYrsec_mlon45(self):
        expected = 3.8941800559380155
        # yrsec made from:
        # (datetime(2010,10,1,5,30,10)-datetime(2010,1,1)).total_seconds()
        epoch = 1285932610.0
        output = mltFromYrsec(2010,23607010,45)
        self.assertEqual(output, expected)
