#!/usr/bin/env python
import os
import glob
from setuptools import find_packages
from setuptools.command import install as _install
from numpy.distutils.core import Extension, setup
from numpy.distutils import exec_command

req = ['numpy','matplotlib','pandas','netcdf4','basemap']

#%% Output debugging information while installing
os.environ['DISTUTILS_DEBUG'] = "1"

#%% check we are executing setup.py from root davitpy directory
assert os.path.isfile('setup.py'),(
    "You must execute setup.py from within the davitpy root directory.")

#############################################################################
# define a read function for using README.md for long_description
#############################################################################


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#############################################################################
# Next let's compile raydarn using its makefile.
# 'exec_command' is supposed to work on win32
# according to its documentation.
#############################################################################
command = 'FC=mpif90 make -C "davitpy/models/raydarn/"'
exec_command.exec_command(command)

#############################################################################
# Now we must define all of our C and Fortran extensions
#############################################################################
# Fortran extensions
#############################################################################
hwm = Extension('hwm14', sources=['davitpy/models/hwm/hwm14.f90',
                                  'davitpy/models/hwm/hwm14.pyf'])
igrf = Extension("igrf", sources=['davitpy/models/igrf/igrf11.f90',
                                  'davitpy/models/igrf/igrf11.pyf'])
iri = Extension('iri', sources=['davitpy/models/iri/irisub.for',
                                'davitpy/models/iri/irifun.for',
                                'davitpy/models/iri/iriflip.for',
                                'davitpy/models/iri/iritec.for',
                                'davitpy/models/iri/igrf.for',
                                'davitpy/models/iri/cira.for',
                                'davitpy/models/iri/iridreg.for',
                                'davitpy/models/iri/iri.pyf'])
msis = Extension("msisFort", sources=['davitpy/models/msis/nrlmsise00_sub.for',
                                      'davitpy/models/msis/nrlmsis.pyf'])
tsyg = Extension('tsygFort',
                 sources=['davitpy/models/tsyganenko/T02.f',
                          'davitpy/models/tsyganenko/T96.f',
                          'davitpy/models/tsyganenko/geopack08.for',
                          'davitpy/models/tsyganenko/geopack08.pyf'])

#############################################################################
# C extensions
#############################################################################
dmap = Extension("dmapio",
                 sources=glob.glob('davitpy/pydarn/dmapio/rst/src/*.c'),)
aacgm = Extension("aacgm",
                  sources=glob.glob('davitpy/models/aacgm/*.c'),)

#############################################################################
# And now get a list of all Python source files
#############################################################################
# pwd = os.getcwd()
# sources = []
# source_dirs = ['davitpy']
# for s in source_dirs:
#     for root, dirs, files in os.walk(pwd+'/'+s):
#         if '__init__.py' in files:
#             sources.append('.'.join(
#                 root.replace(pwd,'').strip('/').split('/')
#                 ))
#############################################################################
# And a list of all the AACGM tables
#############################################################################
data_files = []
for f in os.listdir('tables/aacgm'):
    data_files.append(('tables/aacgm',
                       [os.path.join('tables/aacgm', f)]))

#############################################################################
# Include the davitpyrc file
#############################################################################
data_files.append(('davitpy', ['davitpy/davitpyrc']))

#############################################################################
# Include the necessary raydarn files
#############################################################################
data_files.append(('davitpy/models/raydarn',
                   ['davitpy/models/raydarn/rtFort']))
data_files.append(('davitpy/models/raydarn',
                   ['davitpy/models/raydarn/constants.mod']))
data_files.append(('davitpy/models/raydarn',
                   ['davitpy/models/raydarn/mpiutils.mod']))

#############################################################################
# Include the necessary HWM files
#############################################################################
data_files.append(('davitpy/models/hwm',
                   ['davitpy/models/hwm/hwm123114.bin']))

#############################################################################
# Now execute the setup
#############################################################################
setup(name='davitpy',
      version = "0.7",
      description = "Space Science Toolkit",
      author = "VT SuperDARN Lab and friends",
      author_email = "ajribeiro86@gmail.com",
      url = "http://davit.ece.vt.edu/davitpy/",
      download_url = "https://github.com/vtsuperdarn/davitpy",
      packages = find_packages(),
      long_description = read('README.rst'),
      zip_safe = False,
      ext_modules = [dmap, aacgm, tsyg, hwm, msis, igrf, iri],
      package_data={
        'davitpy.models.iri': ['*.dat', '*.asc'],
        'davitpy.models.hwm': ['*.dat']
      },
      data_files=data_files,
      py_modules = ['davitpy'],
      install_requires = req,
      classifiers = [
            "Development Status :: 4 - Beta",
            "Topic :: Scientific/Engineering",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Natural Language :: English",
            "Programming Language :: Python"
            ],
      )

if os.environ['DISTUTILS_DEBUG'] == "1":
    print((find_packages()))
