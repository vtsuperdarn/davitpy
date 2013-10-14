from numpy.distutils.core import setup, Extension
import os

readmes = []
for x in os.listdir(os.getcwd()):
    if os.path.isdir(x) and 'README.md' in os.listdir(x):
        readmes.append(x+'/README.md')
print readmes

hwm = Extension('hwm',sources=['models/hwm/apexcord.f90','models/hwm/dwm07b.f90','models/hwm/hwm07e.f90','models/hwm/hwm07.pyf'])
igrf = Extension("igrf",sources=["models/igrf/igrf11.f90",'models/igrf/igrf11.pyf'])
iri = Extension('iri',sources=['models/iri/irisub.for', 'models/iri/irifun.for', 'models/iri/iriflip.for', \
                    'models/iri/iritec.for', 'models/iri/igrf.for', 'models/iri/cira.for', 'models/iri/iridreg.for', \
                    'models/iri/iri.pyf'])
msis = Extension("msis",sources=["models/msis/nrlmsise00_sub.for",'models/msis/nrlmsis.pyf'])
tsyg = Extension('tsyg',sources=['models/tsyganenko/T02.f', 'models/tsyganenko/T96.f', \
                    'models/tsyganenko/geopack08.for','models/tsyganenko/geopack08.pyf'])

parent=os.path.abspath(os.path.join(os.getcwd(), os.pardir))

raydarn = Extension('raydarn',sources=[parent+'/models/iri/irisub.for', parent+'/models/iri/irifun.for', parent+'/models/iri/iriflip.for', \
                    parent+'/models/iri/iritec.for', parent+'/models/iri/igrf.for', parent+'/models/iri/cira.for', parent+'/models/iri/iridreg.for', \
                    parent+'/models/iri/iri.pyf','models/raydarn/MPIutils.f90', 'models/raydarn/constants.f90', 'models/raydarn/raytrace_mpi.f90'])

aacgm = Extension("aacgm",sources=["models/aacgm/aacgmlib.c","models/aacgm/aacgm.c","models/aacgm/altitude_to_cgm.c",
                    "models/aacgm/cgm_to_altitude.c","models/aacgm/coeff.c","models/aacgm/convert_geo_coord.c","models/aacgm/math.c",
                    "models/aacgm/rylm.c","models/aacgm/AstAlg_apparent_obliquity.c","models/aacgm/AstAlg_apparent_solar_longitude.c", 
                    "models/aacgm/AstAlg_dday.c","models/aacgm/AstAlg_equation_of_time.c","models/aacgm/AstAlg_geometric_solar_longitude.c", 
                    "models/aacgm/AstAlg_jde.c","models/aacgm/AstAlg_jde2calendar.c", "models/aacgm/AstAlg_lunar_ascending_node.c", 
                    "models/aacgm/AstAlg_mean_lunar_longitude.c", "models/aacgm/AstAlg_mean_obliquity.c", "models/aacgm/AstAlg_mean_solar_anomaly.c", 
                    "models/aacgm/AstAlg_mean_solar_longitude.c", "models/aacgm/AstAlg_nutation_corr.c", "models/aacgm/AstAlg_solar_declination.c", 
                    "models/aacgm/AstAlg_solar_right_ascension.c","models/aacgm/mlt.c","models/aacgm/shval3.c","models/aacgm/dihf.c", 
                    "models/aacgm/interpshc.c","models/aacgm/extrapshc.c","models/aacgm/fft.c","models/aacgm/nrfit.c", \
                    "models/aacgm/magcmp.c", "models/aacgm/igrfcall.c", "models/aacgm/getshc.c", ],)

sources = []

################################################################################
# get a list of all source files
def get_files(dir):
        for f in os.listdir(dir):
                if os.path.isdir(dir+'/'+f) and '__init__.py' in os.listdir(dir+'/'+f):
                        sources.append(dir+'/'+f)
                        get_files(dir+'/'+f)
get_files(os.getcwd())
################################################################################

print [x.replace(os.getcwd()+'/','') for x in sources]

setup(name='davitpy',
        version = "0.2",
        description = "data visualization toolkit-python",
        author = "VT SuperDARN Lab and friends",
        author_email = "ajribeiro86@gmail.com",
        url = "https://github.com/vtsuperdarn/davitpy",
        # packages=[x.replace(os.getcwd()+'/','') for x in sources],
        ext_modules = [hwm,igrf,iri,msis,tsyg,aacgm],
        data_files=[('readmes', readmes),
                    ('iriFiles', ['models/iri/'+x for x in os.listdir('models/iri') if '.dat' in x] + 
                    ['models/iri/'+x for x in os.listdir('models/iri') if '.asc' in x]),
                    ('hwmFiles', ['models/hwm/'+x for x in os.listdir('models/hwm') if '.dat' in x]),
                    ('raydarnFiles',['models/raydarn/Inputs_tpl.inp','models/raydarn/rtFort'])],
        )



# sudo apt-get install libfreetype6-dev
# sudo apt-get install libpng-dev
# apt-get install -y mpich2
# apt-get install -y gfortran


