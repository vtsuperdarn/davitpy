from distutils.core import setup, Extension

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
                                     "/rst/include/superdarn",
                                     "/rst/include/analysis",
                                     "/rst/include/base",
                                     "/rst/include/general",
                                     ],
                                library_dirs = [
                                     "/usr/local/lib64/",
                                     "/rst/lib/"],
				libraries=["m","z","rtime.1","dmap.1", "rcnv.1"]),]
       )

