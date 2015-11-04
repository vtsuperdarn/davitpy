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
        lon_list = [0.,45.,-85.8,-76.2,122.5]
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
          output.append(gspToGcar(X_list[i],Y_list[i],Z_list[i],inverse=True))
        assert_array_almost_equal(output, expected,decimal=3)

    def test_gcarToLcar(self):
        from numpy import array
        from numpy.testing import assert_array_almost_equal
        X_list = [10.1,29.4,74.3,22.2,56.2]
        Y_list = [410.1,221.4,-374.3,222.2,956.2]
        Z_list = [80.1,42.4,374.3,762.2,-756.2]
        lat_list = [52., -52., 46.5, -80., 33.333]
        lon_list = [0.,45.,-85.8,-76.2,122.5]
        re_list = [6378.1,6378.1,6378.1,6378.1,6378.1]
        expected = [(X_list[i],Y_list[i],Z_list[i]) for i in range(5)]

        output = list()
        for i in range(len(lat_list)):
          output.append(gcarToLcar(X_list[i],Y_list[i],Z_list[i],lat_list[i],lon_list[i],re_list[i],inverse=False))

        X_list = [x[0] for x in output]
        Y_list = [x[1] for x in output]
        Z_list = [x[2] for x in output]

        output = list()
        for i in range(len(X_list)):
          output.append(gcarToLcar(X_list[i],Y_list[i],Z_list[i],lat_list[i],lon_list[i],re_list[i],inverse=True))
        assert_array_almost_equal(output, expected,decimal=3)

    def test_lspToLcar(self):
        from numpy import array
        from numpy.testing import assert_array_almost_equal
        r_list = [52., 52., 46.5, 80., 33.333]
        el_list = [0.,45.,85.8,76.2,32.5]
        az_list = [22.11,47.2,-121.32,38.9,-141.12]
        expected = [(r_list[i],el_list[i],az_list[i]) for i in range(5)]

        output = list()
        for i in range(len(r_list)):
          output.append(lspToLcar(r_list[i],el_list[i],az_list[i],inverse=True))

        X_list = [x[0] for x in output]
        Y_list = [x[1] for x in output]
        Z_list = [x[2] for x in output]

        output = list()
        for i in range(len(X_list)):
          output.append(lspToLcar(X_list[i],Y_list[i],Z_list[i],inverse=False))
        assert_array_almost_equal(output, expected,decimal=3)

    def test_calcDistPnt(self):
        from numpy import array
        from numpy.testing import assert_array_almost_equal
        lat_list = [52., -52., 46.5, -80., 33.333]
        lon_list = [0.,45.,-85.8,-76.2,122.5]
        re_list = [6378.1,6378.1,6378.1,6378.1,6378.1]
        dist_list = [22.11,47.2,121.32,38.9,141.12]
        el_list = [0.,45.,85.8,76.2,32.5]
        az_list = [22.11,47.2,-121.32,38.9,-141.12]
        expected = [(52.091937359015823, 0.060647668612696243, 6378.0857244761773),
                    (-51.898823786915756, 45.177235405131974, 6411.5558883635795),
                    (46.481235000226803, -85.848916437100286, 6499.1049363992561),
                    (-79.967972807748083, -76.050933616564549, 6415.8846381328785),
                    (32.918406120330644, 122.103236254511, 6454.6180688827299)]

        temp = list()
        for i in range(len(lat_list)):
          temp.append(calcDistPnt(lat_list[i],lon_list[i],re_list[i],dist=dist_list[i],el=el_list[i],az=az_list[i]))

        output = [(temp[i]['distLat'],temp[i]['distLon'],temp[i]['distAlt']) for i in range(5)]

        assert_array_almost_equal(output, expected,decimal=3)

    def test_greatCircleMove(self):
        from numpy import array
        from numpy.testing import assert_array_almost_equal
        lat_list = [52., -52., 46.5, -80., 33.333]
        lon_list = [0.,45.,-85.8,-76.2,122.5]
        az_list = [22.11,47.2,-121.32,38.9,-141.12]
        dist_list = [2432.11,21.2,156.32,89.9,945.12]

        expected = [(array([ 70.69627228]), array([ 25.0980127])),
                    (array([-51.87024249]), array([ 45.22656326])),
                    (array([ 45.75619724]), array([-87.52136696])),
                    (array([-79.35880316]), array([-73.44961841])),
                    (array([ 26.57298858]), array([ 116.54583168]))]

        output = list()
        for i in range(len(lat_list)):
          output.append(greatCircleMove(lat_list[i],lon_list[i],dist_list[i],az_list[i]))

        assert_array_almost_equal(output, expected,decimal=3)

    def test_greatCircleAzm(self):
        from numpy import array
        from numpy.testing import assert_array_almost_equal
        lat_list = [52., -52., 46.5, -80., 33.333]
        lon_list = [0.,45.,-85.8,-76.2,122.5]
        lat2_list = [42., -32., 86.5, -82., 17.333]
        lon2_list = [10.,-75.,-15.8,-7.2,32.5]

        expected = [141.92928739300785,
                    -131.96126816607148,
                    4.8799014206022431,
                    133.39365975918201,
                    -75.38530121386124]

        output = list()
        for i in range(len(lat_list)):
          output.append(greatCircleAzm(lat_list[i],lon_list[i],lat2_list[i],lon2_list[i]))

        assert_array_almost_equal(output, expected,decimal=3)

    def test_greatCircleDist(self):
        from numpy import array
        from numpy.testing import assert_array_almost_equal
        lat_list = [52., -52., 46.5, -80., 33.333]
        lon_list = [0.,45.,-85.8,-76.2,122.5]
        lat2_list = [42., -32., 86.5, -82., 17.333]
        lon2_list = [10.,-75.,-15.8,-7.2,32.5]

        expected = [0.21083308521623639,
                    1.4136231996540889,
                    0.74011037711462302,
                    0.17977244958303099,
                    1.406345223574035]

        output = list()
        for i in range(len(lat_list)):
          output.append(greatCircleDist(lat_list[i],lon_list[i],lat2_list[i],lon2_list[i]))

        assert_array_almost_equal(output, expected,decimal=3)