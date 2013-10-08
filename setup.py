from setuptools import setup
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




setup(name='davitpy',
       version = "0.1",
       description = "data visualization toolkit-python",
       author = "VT SuperDARN Lab and friends",
       author_email = "ajribeiro86@gmail.com",
       url = "https://github.com/vtsuperdarn/davitpy",
       packages=[x.replace(os.getcwd()+'/','') for x in sources],
       install_requires=['ipython','numpy','scipy','matplotlib','tornado', \
                        'paramiko','pymongo','h5py','mechanize','basemap']
      )



# sudo apt-get install libfreetype6-dev
# sudo apt-get install libpng-dev
# apt-get install -y mpich2
# apt-get install -y gfortran


