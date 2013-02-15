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

rst = os.environ['RSTPATH']
setup (name = "dmapio",
       version = "0.2",
       description = "lib to read dmap files",
       author = "AJ Ribeiro based on pydmap lib by Jef Spaleta",
       author_email = "ribeiro@vt.edu",
       url = "",
       long_description =
"""
""",
       classifiers=[
  ],

       ext_modules = [Extension("dmapio",
                                sources=["dmapio.c"],
                                include_dirs = [
                                     "/usr/local/include/pydarn",
                                     rst+"/include/superdarn",
                                     rst+"/include/analysis",
                                     rst+"/include/base",
                                     rst+"/include/general",
                                     ],
                                library_dirs = [
                                     "/usr/local/lib64/",
                                     rst+"/lib/"],
				libraries=["m","z","rtime.1","dmap.1", "rcnv.1"]),]
       )

