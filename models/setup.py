# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from numpy.distutils.core import setup, Extension
import os

readmes = []
for x in os.listdir(os.getcwd()):
    if os.path.isdir(x) and 'README.md' in os.listdir(x):
        readmes.append(x+'/README.md')
print readmes

hwm = Extension('hwm',sources=['hwm/apexcord.f90','hwm/dwm07b.f90','hwm/hwm07e.f90','hwm/hwm07.pyf'])
igrf = Extension("igrf",sources=["igrf/igrf11.f90",'igrf/igrf11.pyf'])
iri = Extension('iri',sources=['iri/irisub.for', 'iri/irifun.for', 'iri/iriflip.for', \
                    'iri/iritec.for', 'iri/igrf.for', 'iri/cira.for', 'iri/iridreg.for', \
                    'iri/iri.pyf'])
msis = Extension("msis",sources=["msis/nrlmsise00_sub.for",'msis/nrlmsis.pyf'])
tsyg = Extension('tsyg',sources=['tsyganenko/T02.f', 'tsyganenko/T96.f', \
                    'tsyganenko/geopack08.for','tsyganenko/geopack08.pyf'])

parent=os.path.abspath(os.path.join(os.getcwd(), os.pardir))

raydarn = Extension('raydarn',sources=[parent+'/iri/irisub.for', parent+'/iri/irifun.for', parent+'/iri/iriflip.for', \
                    parent+'/iri/iritec.for', parent+'/iri/igrf.for', parent+'/iri/cira.for', parent+'/iri/iridreg.for', \
                    parent+'/iri/iri.pyf','raydarn/MPIutils.f90', 'raydarn/constants.f90', 'raydarn/raytrace_mpi.f90'])

aacgm = Extension("aacgm",sources=["aacgm/aacgmlib.c","aacgm/aacgm.c","aacgm/altitude_to_cgm.c",
                    "aacgm/cgm_to_altitude.c","aacgm/coeff.c","aacgm/convert_geo_coord.c","aacgm/math.c",
                    "aacgm/rylm.c","aacgm/AstAlg_apparent_obliquity.c","aacgm/AstAlg_apparent_solar_longitude.c", 
                    "aacgm/AstAlg_dday.c","aacgm/AstAlg_equation_of_time.c","aacgm/AstAlg_geometric_solar_longitude.c", 
                    "aacgm/AstAlg_jde.c","aacgm/AstAlg_jde2calendar.c", "aacgm/AstAlg_lunar_ascending_node.c", 
                    "aacgm/AstAlg_mean_lunar_longitude.c", "aacgm/AstAlg_mean_obliquity.c", "aacgm/AstAlg_mean_solar_anomaly.c", 
                    "aacgm/AstAlg_mean_solar_longitude.c", "aacgm/AstAlg_nutation_corr.c", "aacgm/AstAlg_solar_declination.c", 
                    "aacgm/AstAlg_solar_right_ascension.c","aacgm/mlt.c","aacgm/shval3.c","aacgm/dihf.c", 
                    "aacgm/interpshc.c","aacgm/extrapshc.c","aacgm/fft.c","aacgm/nrfit.c", \
                    "aacgm/magcmp.c", "aacgm/igrfcall.c", "aacgm/getshc.c", ],)

setup(name = "models",
        description = "a module with several space science models",
        author = "VT SuperDARN Lab, mostly Sebastien",
        ext_modules = [hwm,igrf,iri,msis,tsyg,aacgm],
        data_files=[('readmes', readmes),
                    ('iriFiles', ['iri/'+x for x in os.listdir('iri') if '.dat' in x] + 
                    ['iri/'+x for x in os.listdir('iri') if '.asc' in x]),
                    ('hwmFiles', ['hwm/'+x for x in os.listdir('hwm') if '.dat' in x]),
                    ('raydarnFiles',['raydarn/Inputs_tpl.inp','rtFort'])],
       )
       
       