import os
import glob

os.environ['DISTUTILS_DEBUG'] = "1"

from setuptools import setup, Extension
from setuptools.command import install as _install
from numpy.distutils.core import setup, Extension


# Fortran extensions
hwm = Extension('hwm07',sources=['models/hwm/apexcord.f90','models/hwm/dwm07b.f90','models/hwm/hwm07e.f90','models/hwm/hwm07.pyf'])
igrf = Extension("igrf",sources=["models/igrf/igrf11.f90",'models/igrf/igrf11.pyf'])
iri = Extension('iri',sources=['models/iri/irisub.for', 'models/iri/irifun.for', 'models/iri/iriflip.for', \
                    'models/iri/iritec.for', 'models/iri/igrf.for', 'models/iri/cira.for', 'models/iri/iridreg.for', \
                    'models/iri/iri.pyf'])
msis = Extension("msisFort",sources=["models/msis/nrlmsise00_sub.for",'models/msis/nrlmsis.pyf'])
tsyg = Extension('tsygFort',sources=['models/tsyganenko/T02.f', 'models/tsyganenko/T96.f', \
                    'models/tsyganenko/geopack08.for','models/tsyganenko/geopack08.pyf'])


#C extensions
dmap = Extension("dmapio", sources=glob.glob('pydarn/rst/src/*.c'),)
aacgm = Extension("aacgm", sources=glob.glob('models/aacgm/*.c'),)


################################################################################
# get a list of all source files
pwd = os.getcwd()
sources = []
source_dirs = ['pydarn','gme','utils','models']
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

