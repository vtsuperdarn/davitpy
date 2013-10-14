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


igrf = Extension("igrf",sources=["igrf/igrf11.f90",'igrf/igrf11.pyf'])
msis = Extension("msis",sources=["msis/nrlmsise00_sub.for",'msis/nrlmsis.pyf'])
tsyg = Extension('tsyg',sources=['tsyganenko/T02.f', 'tsyganenko/T96.f', \
                    'tsyganenko/geopack08.for','tsyganenko/geopack08.pyf'])
iri = Extension('iri',sources=['iri/irisub.for', 'iri/irifun.for', 'iri/iriflip.for', \
                    'iri/iritec.for', 'iri/igrf.for', 'iri/cira.for', 'iri/iridreg.for', \
                    'iri/iri.pyf'])
hwm = Extension('hwm',sources=['hwm/apexcord.f90','hwm/dwm07b.f90','hwm/hwm07e.f90','hwm/hwm07.pyf'])

setup(name = "models",
        description = "a module with several space science models",
        author = "VT SuperDARN Lab, mostly Sebastien",
        ext_modules = [hwm],
        data_files=[('readmes', ['igrf/README.md', 'msis/README.md','tsyganenko/README.md']),
                    ('iriFiles', ['iri/*.asc','iri/*.dat']),
                    ('hwmFiles', ['hwm/*.dat'])],
       )
       
       