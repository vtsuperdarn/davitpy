import unittest

from datetime import datetime
from davitpy.utils.coordUtils import coordConv
from davitpy.utils.coordUtils import coord_conv

class TestCoordConv(unittest.TestCase):

    def test_coordConv_redirection(self):
        expected = (50.700000000000003, 34.5)
        output = coordConv(50.7, 34.5, 300., "geo", "geo",dateTime=datetime(2012, 1, 1, 0, 2))
        self.assertEqual(output, expected)

    def test_coord_conv_geo_to_geo(self):
        expected = (50.700000000000003, 34.5)
        output = coord_conv(50.7, 34.5, "geo","geo",date_time=datetime(2012, 1, 1, 0, 2))
        self.assertEqual(output, expected)

    def test_coord_conv_geo_to_geo_with_altitude(self):
        expected = (50.700000000000003, 34.5)
        output = coord_conv(50.7, 34.5, "geo","geo",date_time=datetime(2012, 1, 1, 0, 2),altitude=300.0)
        self.assertEqual(output, expected)
