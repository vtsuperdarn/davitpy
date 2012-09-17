from distutils.core import setup, Extension

setup (name = "aagcmlib",
       version = "0.1",
       description = "wrapper to call c AACGM code in RST3",
       author = "AJ Ribeiro",
       author_email = "ribeiro@vt.edu",
       url = "",
       long_description =
"""
""",
       classifiers=[
  ],

       ext_modules = [Extension("aacgmlib",
                                sources=["aacgmlib.c"],
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
				libraries=["mlt.1","aacgm.1","astalg.1","rtime.1","radar.1","dmap.1","rpos.1","igrf.1"]),]
       )

