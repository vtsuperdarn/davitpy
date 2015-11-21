import unittest

from datetime import datetime
from davitpy.models.msis import checkmsis
from davitpy import rcParams
from cStringIO import StringIO
import contextlib
import sys
import os

# Thanks to http://stackoverflow.com/questions/977840/redirecting-fortran-called-via-f2py-output-in-python
# and http://stackoverflow.com/questions/14197009/how-can-i-redirect-print-output-of-a-function-in-python
# for this solution!
@contextlib.contextmanager
def stdchannel_redirected(stdchannel, file):
    """
    A context manager to temporarily redirect stdout or stderr

    e.g.:


    with stdchannel_redirected(sys.stderr, os.devnull):
        if compiler.has_function('clock_gettime', libraries=['rt']):
            libraries.append('rt')
    """

    try:
        oldstdchannel = os.dup(stdchannel.fileno())
        dest_file = file
        os.dup2(dest_file.fileno(), stdchannel.fileno())

        yield
    finally:
        if oldstdchannel is not None:
            os.dup2(oldstdchannel, stdchannel.fileno())

class TestMSIS(unittest.TestCase):

    def test_msis(self):
        tempfile = 'test.txt'
        test_file =  "{:s}/davitpy/tests/nrlmsise00_test_output.txt".format(rcParams['DAVITPY_PATH'])

        # Read the expected output from the expected output file.
        with open(test_file, "r") as myfile:
            expected=myfile.read().replace('\n',' ')

        # Capture the output of the checkmsis function.
        with open('test.txt','w') as f:
            with stdchannel_redirected(sys.stdout, f):
                checkmsis()

        # Read the output from checkmsis()
        with open(tempfile, "r") as myfile:
            output=myfile.read().replace('\n',' ')

        os.remove(tempfile)

        self.assertEqual(output, expected)
