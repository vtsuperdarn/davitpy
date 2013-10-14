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

aacgm = Extension("aacgmlib",sources=["pydarn/rst/src/aacgmlib.c","pydarn/rst/src/aacgm.c","pydarn/rst/src/altitude_to_cgm.c",
                "pydarn/rst/src/cgm_to_altitude.c","pydarn/rst/src/coeff.c","pydarn/rst/src/convert_geo_coord.c","pydarn/rst/src/math.c",
                "pydarn/rst/src/rylm.c","pydarn/rst/src/AstAlg_apparent_obliquity.c","pydarn/rst/src/AstAlg_apparent_solar_longitude.c", 
                "pydarn/rst/src/AstAlg_dday.c","pydarn/rst/src/AstAlg_equation_of_time.c","pydarn/rst/src/AstAlg_geometric_solar_longitude.c", 
                "pydarn/rst/src/AstAlg_jde.c","pydarn/rst/src/AstAlg_jde2calendar.c", "pydarn/rst/src/AstAlg_lunar_ascending_node.c", 
                "pydarn/rst/src/AstAlg_mean_lunar_longitude.c", "pydarn/rst/src/AstAlg_mean_obliquity.c", "pydarn/rst/src/AstAlg_mean_solar_anomaly.c", 
                "pydarn/rst/src/AstAlg_mean_solar_longitude.c", "pydarn/rst/src/AstAlg_nutation_corr.c", "pydarn/rst/src/AstAlg_solar_declination.c", 
                "pydarn/rst/src/AstAlg_solar_right_ascension.c","pydarn/rst/src/mlt.c","pydarn/rst/src/shval3.c","pydarn/rst/src/dihf.c", 
                "pydarn/rst/src/interpshc.c","pydarn/rst/src/extrapshc.c","pydarn/rst/src/fft.c","pydarn/rst/src/nrfit.c", \
                "pydarn/rst/src/magcmp.c", "pydarn/rst/src/igrfcall.c", "pydarn/rst/src/getshc.c"],
                include_dirs = ["pydarn/rst/src"])

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


