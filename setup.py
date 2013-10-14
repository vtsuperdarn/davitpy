from setuptools import setup
from distutils.core import Extension
import os

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


dmap = Extension("dmapio",sources=["pydarn/rst/src/dmapio.c","pydarn/rst/src/rtime.c","pydarn/rst/src/dmap.c","pydarn/rst/src/convert.c"],
                                    include_dirs = ["pydarn/rst/src"])

aacgm = Extension("aacgmlib",sources=["models/aacgm/aacgmlib.c","models/aacgm/aacgm.c","models/aacgm/altitude_to_cgm.c",
                "models/aacgm/cgm_to_altitude.c","models/aacgm/coeff.c","models/aacgm/convert_geo_coord.c","models/aacgm/math.c",
                "models/aacgm/rylm.c","models/aacgm/AstAlg_apparent_obliquity.c","models/aacgm/AstAlg_apparent_solar_longitude.c", 
                "models/aacgm/AstAlg_dday.c","models/aacgm/AstAlg_equation_of_time.c","models/aacgm/AstAlg_geometric_solar_longitude.c", 
                "models/aacgm/AstAlg_jde.c","models/aacgm/AstAlg_jde2calendar.c", "models/aacgm/AstAlg_lunar_ascending_node.c", 
                "models/aacgm/AstAlg_mean_lunar_longitude.c", "models/aacgm/AstAlg_mean_obliquity.c", "models/aacgm/AstAlg_mean_solar_anomaly.c", 
                "models/aacgm/AstAlg_mean_solar_longitude.c", "models/aacgm/AstAlg_nutation_corr.c", "models/aacgm/AstAlg_solar_declination.c", 
                "models/aacgm/AstAlg_solar_right_ascension.c","models/aacgm/mlt.c","models/aacgm/shval3.c","models/aacgm/dihf.c", 
                "models/aacgm/interpshc.c","models/aacgm/extrapshc.c","models/aacgm/fft.c","models/aacgm/nrfit.c", \
                "models/aacgm/magcmp.c", "models/aacgm/igrfcall.c", "models/aacgm/getshc.c"],
                include_dirs = ["pydarn/rst/src","models/aacgm"])

setup(name='davitpy',
        version = "0.2",
        description = "data visualization toolkit-python",
        author = "VT SuperDARN Lab and friends",
        author_email = "ajribeiro86@gmail.com",
        url = "https://github.com/vtsuperdarn/davitpy",
        packages=[x.replace(os.getcwd()+'/','') for x in sources],
        #install_requires=['ipython','numpy','scipy','matplotlib','tornado', \
        #                'paramiko','pymongo','h5py','mechanize','basemap'],
        ext_modules = [aacgm]
        )



# sudo apt-get install libfreetype6-dev
# sudo apt-get install libpng-dev
# apt-get install -y mpich2
# apt-get install -y gfortran


