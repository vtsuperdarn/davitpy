import unittest

default_test_modules = [
    'davitpy.tests.test_aacgm',
    'davitpy.tests.test_coordUtils',
    'davitpy.tests.test_geoPack',
    'davitpy.tests.test_hwm'
#    'davitpy.tests.test_calcSun'
    ]



def suite():
    # define a test suite for all tests defined in default_test_modules
    # largely copied from http://stackoverflow.com/questions/1732438/how-to-run-all-python-unit-tests-in-a-directory
    # Thanks to Ned Batchelder.
   
    suite = unittest.TestSuite()

    for t in default_test_modules:
        try:
            # If the module defines a suite() function, call it to get the suite.
            mod = __import__(t, globals(), locals(), ['suite'])
            suitefn = getattr(mod, 'suite')
            suite.addTest(suitefn())
        except (ImportError, AttributeError):
            # else, just load all the test cases from the module.
            suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))
    
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())


