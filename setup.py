import os

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

dmap = Extension("dmapio",sources=['pydarn/rst/src/'+ x for x in os.listdir('pydarn/rst/src') if '.c' in x],)


aacgm = Extension("aacgm",sources=['models/aacgm/'+ x for x in os.listdir('models/aacgm') if '.c' in x and 'c~' not in x])

sources = []

scripts = ['install/'+ x for x in os.listdir('install') if 'readme' not in x]
print scripts

################################################################################
# get a list of all source files
sources = []
def get_files(dir):
        for f in os.listdir(dir):
                if os.path.isdir(dir+'/'+f) and '__init__.py' in os.listdir(dir+'/'+f):
                        sources.append(dir+'/'+f)
                        get_files(dir+'/'+f)
get_files(os.getcwd())
sources = [x.replace(os.getcwd()+'/','').replace('/','.') for x in sources]
print sources
################################################################################


setup(name='davitpy',
        version = "0.2",
        description = "data visualization toolkit-python",
        author = "VT SuperDARN Lab and friends",
        author_email = "ajribeiro86@gmail.com",
        url = "https://github.com/vtsuperdarn/davitpy",
        packages = sources,
        zip_safe = False,
        ext_modules = [dmap,aacgm],
        install_requires=['ipython','numpy','scipy','matplotlib','basemap','h5py', \
                            'tornado','paramiko','pymongo','mechanize','jinja2'],
        data_files=[#('models/iri', irifiles),
                    # ('models/hwm', hwmfiles),
                    # ('models/msis', msisfiles),
                    # ('models/igrf', igrffiles),
                    # ('models/tsyganenko', tsygfiles),
                    # ('models/raydarn',raydarnfiles)
                    ('install',['install/readme']),
                    'profile.bash','profile.mac'],
        scripts = scripts
        )

