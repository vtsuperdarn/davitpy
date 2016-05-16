import unittest

from datetime import datetime
from davitpy.utils.timeUtils import dateToYyyymmdd
from davitpy.utils.timeUtils import yyyymmddToDate
from davitpy.utils.timeUtils import timeYrsecToDate
from davitpy.utils.timeUtils import julToDatetime
from davitpy.utils.timeUtils import datetimeToEpoch
from davitpy.utils.timeUtils import dateToDecYear
from davitpy.utils.timeUtils import parseDate
from davitpy.utils.timeUtils import parseTime

class TestCoordConv(unittest.TestCase):

    def test_dateToYyyymmdd(self):
        expected = '20121123'
        output = dateToYyyymmdd(datetime(2012,11,23))
        self.assertEqual(output, expected)

    def test_yyyymmddToDate(self):
        expected = datetime(2012, 11, 23)
        output = dateToYyyymmdd('20121123')
        self.assertEqual(output, expected)

    def test_timeYrsecToDate(self):
        expected = datetime(2012, 1, 14, 22, 48, 24)
        output = timeYrsecToDate(1205304,2012)
        self.assertEqual(output, expected)

    def test_julToDatetime(self):
        expected = datetime(2012, 7, 10, 0, 0)
        output = julToDatetime(2456118.5)
        self.assertEqual(output, expected)

    def test_datetimeToEpoch(self):
        expected = 1341878400.0
        output = datetimeToEpoch(datetime(2012,7,10))
        self.assertEqual(output, expected)

    def test_dateToDecYear(self):
        expected = 2012.5218579234972
        output = dateToDecYear(datetime(2012,7,10))
        self.assertEqual(output, expected)

    def test_parseDate1(self):
        expected = [2012, 11, 23]
        output = parseDate('20121123')
        self.assertEqual(output, expected)

    def test_parseDate2(self):
        expected = '20121123'
        output = parseDate([2012, 11, 23])
        self.assertEqual(output, expected)

    def test_parseTime1(self):
        expected = [6,50,22]
        output = parseTime('065022')
        self.assertEqual(output, expected)

    def test_parseTime2(self):
        expected = '065022'
        output = parseTime([6,50,22])
        self.assertEqual(output, expected)