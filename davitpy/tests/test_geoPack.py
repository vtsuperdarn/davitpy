import unittest

from datetime import datetime
from davitpy.utils.geoPack import *

class TestGeoPack(unittest.TestCase):

    def test_geodToGeoc(self):
        expected = [(51.813136179892048, 120.0, 6364.9228823421126),
                    (-51.813136179892048, 120.0, 6364.9228823421126),
                    (46.307802046976398, 120.0, 6366.9525263943424),
                    (-79.933977203198339, 120.0, 6357.4248369757761),
                    (33.156545131905837, 120.0, 6371.7403935506254),
                    (52.186560415893936, 120.0, 6364.8552356794999),
                    (-52.186560415893936, 120.0, 6364.8552356794999),
                    (46.692130399759805, 120.0, 6366.8808941848438),
                    (-80.065607376332267, 120.0, 6357.4164219502463),
                    (33.509924957403911, 120.0, 6371.679879126943)]
        in_list = [52., -52., 46.5, -80., 33.333]
        output = list()
        for i in in_list:
          output.append(geodToGeoc(i,120.,inverse=False))
        for i in in_list:
          output.append(geodToGeoc(i,120.,inverse=True))
        self.assertEqual(output, expected)

    def test_geodToGeocAzEl(self):
        expected = [(51.813136179892048, 120.0, 6364.9228823421126, 0.0, -0.18686382010795197),
                    (-51.813136179892048, 120.0, 6364.9228823421126, 45.023460473924743, 10.132105681240274),
                    (46.307802046976398, 120.0, 6366.9525263943424, -85.729428949967186, 20.205805708209525),
                    (-79.933977203198339, 120.0, 6357.4248369757761, -76.270741407447744, 47.815709065950657),
                    (33.156545131905837, 120.0, 6371.7403935506254, 120.67938597777399, 85.326444546687256),
                    (52.186560415893936, 120.0, 6364.8552356794999, 0.0, 0.18656041589393624),
                    (-52.186560415893936, 120.0, 6364.8552356794999, 44.976900496890487, 9.8680552143411724),
                    (46.692130399759805, 120.0, 6366.8808941848438, -85.870606083219897, 20.233953233026078),
                    (-80.065607376332267, 120.0, 6357.4164219502463, -76.129763626131989, 47.784311392228048),
                    (33.509924957403911, 120.0, 6371.679879126943, 124.2541238274226, 85.136653900529424)]
        lat_list = [52., -52., 46.5, -80., 33.333]
        az_list = [0.,45.,274.2,-76.2,122.5]
        el_list = [0.,10.,20.22,47.8,85.234]
        output = list()
        for i in range(len(lat_list)):
          output.append(geodToGeocAzEl(lat_list[i],120.,az_list[i],el_list[i],inverse=False))
        for i in range(len(lat_list)):
          output.append(geodToGeocAzEl(lat_list[i],120.,az_list[i],el_list[i],inverse=True))
        self.assertEqual(output, expected)

    def test_gspToGcar(self):
        from numpy import array
        from numpy.testing import assert_array_almost_equal
        lat_list = [52., -52., 46.5, -80., 33.333]
        lon_list = [0.,45.,274.2,-76.2,122.5]
        re_list = [6378.1,6378.1,6378.1,6378.1,6378.1]
        expected = [(lat_list[i],lon_list[i],re_list[i]) for i in range(5)]

        output = list()
        for i in range(len(lat_list)):
          output.append(gspToGcar(lat_list[i],lon_list[i],re_list[i],inverse=False))

        X_list = [x[0] for x in output]
        Y_list = [x[1] for x in output]
        Z_list = [x[2] for x in output]

        output = list()
        for i in range(len(X_list)):
          output.append(gspToGcar(X_list[i],Y_list[i],Y_list[i],inverse=True))
        assert_array_almost_equal(output, expected,decimal=3)





