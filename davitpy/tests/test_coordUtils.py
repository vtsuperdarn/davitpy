import unittest

from datetime import datetime
from davitpy.utils.coordUtils import coordConv
from davitpy.utils.coordUtils import coord_conv

class TestCoordConv(unittest.TestCase):

    in_coords = ['geo','mag','mlt']
    out_coords = ['geo','mag','mlt']

    def test_coordConv_redirection(self):
        expected = (50.700000000000003, 34.5)
        output = coordConv(50.7,34.5,300.,"geo","geo",dateTime=datetime(2012, 1, 1, 0, 2))
        self.assertEqual(output, expected)

    def test_coord_conv(self):
        expected = [(50.700000000000003, 34.5),
                    (123.7164261636343, 31.582924632749936),
                    (45.700127390504122, 31.582924632749936),
                    (-30.807065991648678, 36.659072072769803),
                    (50.700000000000003, 34.5),
                    (-27.3162987731302, 34.5),
                    (55.576765818891992, 37.377580578236319),
                    (128.71629877313018, 34.5),
                    (50.700000000000003, 34.5)]
        output = list()
        for i in self.in_coords:
          for o in self.out_coords:
            output.append(coord_conv(50.7,34.5,i,o,date_time=datetime(2012, 1, 1, 0, 2),altitude=300.0))
        self.assertEqual(output, expected)

    def test_coord_conv_list(self):
        expected = [([50.700000000000003], [34.5]),
                    ([123.7164261636343], [31.582924632749936]),
                    ([45.700127390504122], [31.582924632749936]),
                    ([-30.807065991648678], [36.659072072769803]),
                    ([50.700000000000003], [34.5]),
                    ([-27.3162987731302], [34.5]),
                    ([55.576765818891992], [37.377580578236319]),
                    ([128.71629877313018], [34.5]),
                    ([50.700000000000003], [34.5])]
        output = list()
        for i in self.in_coords:
          for o in self.out_coords:
            output.append(coord_conv([50.7],[34.5],i,o,date_time=datetime(2012, 1, 1, 0, 2),altitude=300.0))
        self.assertEqual(output, expected)

    def test_coord_conv_array(self):
        from numpy import array
        expected = [(array([ 50.7]), array([ 34.5])),
                    (array([ 123.7164261636343]), array([ 31.582924632749936])),
                    (array([ 45.700127390504122]), array([ 31.582924632749936])),
                    (array([-30.807065991648678]), array([ 36.659072072769803])),
                    (array([ 50.700000000000003]), array([ 34.5])),
                    (array([-27.3162987731302]), array([ 34.5])),
                    (array([ 55.576765818891992]), array([ 37.377580578236319])),
                    (array([ 128.71629877313018]), array([ 34.5])),
                    (array([ 50.700000000000003]), array([ 34.5]))]
        output = list()
        for i in self.in_coords:
          for o in self.out_coords:
            output.append(coord_conv(array([50.7]),array([34.5]),i,o,date_time=datetime(2012, 1, 1, 0, 2),altitude=300.0))
        self.assertEqual(output, expected)

    def test_coord_conv_mxn_array(self):
        from numpy import array
        from numpy.testing import assert_array_almost_equal
        expected = (array([[-130.65999039, -120.89269136],
                           [-139.26450185, -149.12386912]]), 
                    array([[ 31.58292463,  42.81408443], 
                           [ 18.42380165,  36.68788184]]))
        output = coord_conv(array([[50.7, 60.1],[42.4, 32.1]]),
                            array([[34.5, 45.6],[21.1, 40.4]]),"geo","mlt",date_time=datetime(2013,7,23,12,6,34),altitude=300.0)
        
        assert_array_almost_equal(output, expected,decimal=8)

    def test_coord_conv_mlt_altitudes(self):
        expected = (50.672783138859778, 53.443261761838208)
        output = coord_conv(50.7, 53.8,"mlt","mlt",altitude=300.,end_altitude=200.,
                            date_time=datetime(2013, 7, 23, 12, 6, 34))
        self.assertEqual(output, expected)

    def test_coord_conv_wrong_input(self):
        with self.assertRaises(AssertionError):
            coord_conv(50.7, 53.8,"abc","geo")
        with self.assertRaises(AssertionError):
            coord_conv(50.7, 53.8,"geo","mlt",altitude=300.,date_time=None)
        with self.assertRaises(AssertionError):
            coord_conv(50.7, 53.8,"geo","mlt",altitude=None,date_time=datetime(2013, 7, 23, 12, 6, 34))


