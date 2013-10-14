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

from distutils.core import setup, Extension
import os


dmap = Extension("dmapio",sources=["src/dmapio.c","src/rtime.c","src/dmap.c","src/convert.c"],include_dirs = ["src"])

aacgm = Extension("aacgmlib",sources=["src/aacgmlib.c","src/aacgm.c","src/altitude_to_cgm.c",
                    "src/cgm_to_altitude.c","src/coeff.c","src/convert_geo_coord.c","src/math.c",
                    "src/rylm.c","src/AstAlg_apparent_obliquity.c","src/AstAlg_apparent_solar_longitude.c", 
                    "src/AstAlg_dday.c","src/AstAlg_equation_of_time.c","src/AstAlg_geometric_solar_longitude.c", 
                    "src/AstAlg_jde.c","src/AstAlg_jde2calendar.c", "src/AstAlg_lunar_ascending_node.c", 
                    "src/AstAlg_mean_lunar_longitude.c", "src/AstAlg_mean_obliquity.c", "src/AstAlg_mean_solar_anomaly.c", 
                    "src/AstAlg_mean_solar_longitude.c", "src/AstAlg_nutation_corr.c", "src/AstAlg_solar_declination.c", 
                    "src/AstAlg_solar_right_ascension.c","src/mlt.c","src/shval3.c","src/dihf.c", 
                    "src/interpshc.c","src/extrapshc.c","src/fft.c","src/nrfit.c", \
                    "src/magcmp.c", "src/igrfcall.c", "src/getshc.c", ],)

# dmap = Extension("dmapio",
#                   sources=["dmap/convert.c"],
#                       include_dirs = ["dmap"],
#                    #                   ],
#        )
# test = Extension("ajtest",
#                   sources=["test.c"],
#                       # include_dirs = ["dmap",
#                    #                   ],
#        )

setup (name = "rst",
       version = "1.0",
       description = "lib to read dmap files",
       author = "AJ Ribeiro based on pydmap lib by Jef Spaleta",
       author_email = "ribeiro@vt.edu",
       ext_modules = [aacgm,dmap]
       )
       
       