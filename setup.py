import os
import glob

# Output debugging information while installing
os.environ['DISTUTILS_DEBUG'] = "1"

# NEED TO HAVE aacgm_coeffs installed with software
#davitpy_dir = os.path.dirname(os.path.abspath(__file__))
#os.environ['DAVITPY'] = davitpy_dir
#os.environ['AACGM_DAVITPY_DAT_PREFIX'] = os.path.join(davitpy_dir,"tables/aacgm/aacgm_coeffs")

from setuptools.command import install as _install
# Need to use the enhanced version of distutils packaged with
# numpy so that we can compile fortran extensions
from numpy.distutils.core import Extension, setup

# Fortran extensions
hwm = Extension('hwm07',sources=['davitpy/models/hwm/apexcord.f90','davitpy/models/hwm/dwm07b.f90','davitpy/models/hwm/hwm07e.f90','davitpy/models/hwm/hwm07.pyf'])
igrf = Extension("igrf",sources=["davitpy/models/igrf/igrf11.f90",'davitpy/models/igrf/igrf11.pyf'])
iri = Extension('iri',sources=['davitpy/models/iri/irisub.for', 'davitpy/models/iri/irifun.for', 'davitpy/models/iri/iriflip.for', \
                    'davitpy/models/iri/iritec.for', 'davitpy/models/iri/igrf.for', 'davitpy/models/iri/cira.for', 'davitpy/models/iri/iridreg.for', \
                    'davitpy/models/iri/iri.pyf'])
msis = Extension("msisFort",sources=["davitpy/models/msis/nrlmsise00_sub.for",'davitpy/models/msis/nrlmsis.pyf'])
tsyg = Extension('tsygFort',sources=['davitpy/models/tsyganenko/T02.f', 'davitpy/models/tsyganenko/T96.f', \
                    'davitpy/models/tsyganenko/geopack08.for','davitpy/models/tsyganenko/geopack08.pyf'])

# C extensions
dmap = Extension("dmapio", sources=glob.glob('davitpy/pydarn/rst/src/*.c'),)
aacgm = Extension("aacgm", sources=glob.glob('davitpy/models/aacgm/*.c'),)

# Get a list of all Python source files
pwd = os.getcwd()
sources = []
source_dirs = ['davitpy']
for s in source_dirs:
    for root, dirs, files in os.walk(pwd+'/'+s):
        if '__init__.py' in files:
            sources.append('.'.join(
                root.replace(pwd,'').strip('/').split('/')
                ))
#Get a list of all the AACGM tables
data_files = []
for f in os.listdir('tables/aacgm'):
    data_files.append(('tables/aacgm',[os.path.join('tables/aacgm',f)]))

#Make sure we include the davitpyrc file
data_files.append(('davitpy',['davitpy/davitpyrc']))
################################################################################
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
################################################################################

# Now execute the setup
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
        'davitpy.models.iri': ['*.dat','*.asc'],
        'davitpy.models.hwm': ['*.mod','*.dat']
      },
      data_files=data_files,
      py_modules = ['davitpy'],#,'pydarn','models','gme','utils'],
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

if os.environ['DISTUTILS_DEBUG'] == "1":
    print 'Sources',sources

print ""
print "****************************************************************"
print ""
print "****************************************************************"
print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
print "****************************************************************"
print "If you wish to install a 'davitpy' executable to automagically  "
print "startup an ipython session with the davitpy library imported,   "
print "please see the README file in the 'bin' directory on the DaViTpy"
print "github repository."
print "****************************************************************"
print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
print "****************************************************************"
print ""
print "****************************************************************"
print ""
