import os
import glob

os.environ['DISTUTILS_DEBUG'] = "1"

from setuptools import setup, Extension
from setuptools.command import install as _install
from numpy.distutils.core import setup, Extension


# Fortran extensions
hwm = Extension('hwm07',sources=['davitpy/models/hwm/apexcord.f90','davitpy/models/hwm/dwm07b.f90','davitpy/models/hwm/hwm07e.f90','davitpy/models/hwm/hwm07.pyf'])
igrf = Extension("igrf",sources=["davitpy/models/igrf/igrf11.f90",'davitpy/models/igrf/igrf11.pyf'])
iri = Extension('iri',sources=['davitpy/models/iri/irisub.for', 'davitpy/models/iri/irifun.for', 'davitpy/models/iri/iriflip.for', \
                    'davitpy/models/iri/iritec.for', 'davitpy/models/iri/igrf.for', 'davitpy/models/iri/cira.for', 'davitpy/models/iri/iridreg.for', \
                    'davitpy/models/iri/iri.pyf'])
msis = Extension("msisFort",sources=["davitpy/models/msis/nrlmsise00_sub.for",'davitpy/models/msis/nrlmsis.pyf'])
tsyg = Extension('tsygFort',sources=['davitpy/models/tsyganenko/T02.f', 'davitpy/models/tsyganenko/T96.f', \
                    'davitpy/models/tsyganenko/geopack08.for','davitpy/models/tsyganenko/geopack08.pyf'])


#C extensions
dmap = Extension("dmapio", sources=glob.glob('davitpy/pydarn/rst/src/*.c'),)
aacgm = Extension("aacgm", sources=glob.glob('davitpy/models/aacgm/*.c'),)


################################################################################
# get a list of all source files
pwd = os.getcwd()
sources = []
source_dirs = ['davitpy','davitpy/pydarn','davitpy/gme','davitpy/utils','davitpy/models']
for s in source_dirs:
    for root, dirs, files in os.walk(pwd+'/'+s):
        if '__init__.py' in files:
            sources.append('.'.join(
                root.replace(pwd,'').strip('/').split('/')
                ))
print 'sources',sources
################################################################################

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='davitpy',
      version = "0.2",
      description = "Space Science Toolkit",
      author = "VT SuperDARN Lab and friends",
      author_email = "ajribeiro86@gmail.com",
      url = "",
      download_url = "https://github.com/vtsuperdarn/davitpy",
      packages = sources,
      long_description = read('README.md'),
      zip_safe = False,
      ext_modules = [dmap,aacgm,tsyg,hwm,msis,igrf,iri],
      package_data={
        'models.iri': ['*.dat','*.asc'],
        'models.hwm': ['*.mod','*.dat']
      },
      install_requires=[],
      classifiers = [
            "Development Status :: 4 - Beta",
            "Topic :: Scientific/Engineering",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Natural Language :: English",
            "Programming Language :: Python"
            ],
      )

