import os
import glob

os.environ['DISTUTILS_DEBUG'] = "1"

from setuptools import setup, Extension
from setuptools.command import install as _install


# hwmfiles = ['models/hwm/makefile','models/hwm/README.md','models/hwm/apexcord.f90', \
#             'models/hwm/dwm07b.f90','models/hwm/hwm07e.f90','models/hwm/hwm07.pyf'] + \
#             [x for x in os.listdir(os.path.join('models','hwm')) if '.dat' in x]
# igrffiles = ['models/igrf/makefile','models/igrf/README.md',"models/igrf/igrf11.f90", \
#             'models/igrf/igrf11.pyf']
# irifiles = ['models/iri/README.md','models/iri/makefile','models/iri/irisub.for', \
#             'models/iri/irifun.for', 'models/iri/iriflip.for', 'models/iri/iritec.for', \
#             'models/iri/igrf.for', 'models/iri/cira.for', 'models/iri/iridreg.for', \
#             'models/iri/iri.pyf'] + ['models/iri/'+x for x in os.listdir(os.path.join('models','iri')) if '.dat' in x] + \
#             ['models/iri/'+x for x in os.listdir(os.path.join('models','iri')) if '.asc' in x]
# msisfiles = ['models/msis/README.md','models/msis/makefile',"models/msis/nrlmsise00_sub.for", \
#             'models/msis/nrlmsis.pyf']
# tsygfiles = ['models/tsyganenko/README.md','models/tsyganenko/makefile','models/tsyganenko/T02.f', \
#              'models/tsyganenko/T96.f', 'models/tsyganenko/geopack08.for','models/tsyganenko/geopack08.pyf']
# raydarnfiles = ['models/raydarn/Makefile','models/raydarn/MPIutils.f90', 'models/raydarn/constants.f90', \
#                 'models/raydarn/raytrace_mpi.f90', 'models/raydarn/Inputs_tpl.inp']


# dmap = Extension("dmapio",sources=["pydarn/rst/src/dmapio.c","pydarn/rst/src/rtime.c", 
#                     "pydarn/rst/src/dmap.c","pydarn/rst/src/convert.c"],include_dirs = ["src"])

dmap = Extension("dmapio",
    sources=glob.glob('pydarn/rst/src/*.c'),)

aacgm = Extension("aacgm",
    sources=glob.glob('models/aacgm/*.c'),)

scripts = glob.glob('install/*.sh')
print scripts

################################################################################
# get a list of all source files
pwd = os.getcwd()
sources = []
for root, dirs, files in os.walk(pwd):
    if '__init__.py' in files:
        sources.append('davitpy.'+'.'.join(
            root.replace(pwd,'').strip('/').split('/')
            ))
print sources
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
      ext_modules = [dmap,aacgm],
      install_requires=['ipython','numpy','scipy',
                        'matplotlib','basemap','h5py', 
                        'tornado','paramiko','pymongo',
                        'mechanize','jinja2'],
      data_files=[#('models/iri', irifiles),
                  # ('models/hwm', hwmfiles),
                  # ('models/msis', msisfiles),
                  # ('models/igrf', igrffiles),
                  # ('models/tsyganenko', tsygfiles),
                  # ('models/raydarn',raydarnfiles)
                  ('install',['install/readme']),
                  'profile.bash','profile.mac'],
      scripts = scripts,
      classifiers = [
            "Development Status :: 4 - Beta",
            "Topic :: Scientific/Engineering",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Natural Language :: English",
            "Programming Language :: Python"
            ],
      )

