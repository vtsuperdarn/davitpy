import unittest

from datetime import datetime
from davitpy.models.hwm import *
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

class TestHWM(unittest.TestCase):

    def test_hwm(self):
        tempfile = 'test.txt'
        test_file =  "{:s}/davitpy/tests/hwm14_test_output.txt".format(rcParams['DAVITPY_PATH'])

        # Read the expected output from the expected output file.
        with open(test_file, "r") as myfile:
            expected=myfile.read().replace('\n',' ')

        # Capture the output of the checkhwm14 function.
        with open(tempfile,'w') as f:
            with stdchannel_redirected(sys.stdout, f):
                checkhwm14()

        # Read the output from checkhwm14()
        with open(tempfile, "r") as myfile:
            output=myfile.read().replace('\n',' ')

        os.remove(tempfile)

        #print expected
        #print output
        self.assertEqual(output, expected)
