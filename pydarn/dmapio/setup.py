from distutils.core import setup, Extension

setup (name = "dmapio",
       version = "0.2",
       description = "python bindings for dmap files",
       author = "Jef Spaleta with edits by AJ",
       author_email = "jspaleta@gi.alaska.edu",
       url = "http://wwwfe",
       long_description =
"""The pydmap module provides functions to interact with dmap based files and is part of the collection of python tools for working with the SuperDARN datasets and C language based RST and ROS codebase.  
""",
       classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: (BSD)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Science'
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

