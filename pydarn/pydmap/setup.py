from distutils.core import setup, Extension

setup (name = "pydmap",
       version = "0.1",
       description = "python bindings for dmap files",
       author = "Jef Spaleta",
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

       ext_modules = [Extension("pydmap",
                                sources=["pydmap.c"],
                                include_dirs = [
                                     "/usr/local/include/pydarn",
                                     ],
                                library_dirs = [
                                     "/usr/local/lib64/"],
				libraries=["m","z","rtime","dmap", "rcnv"]),]
       )

