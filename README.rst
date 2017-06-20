========
DaViT-py
========

Welcome to the Data and Visualization Toolkit-Python.  This code base is designed to allow you to access and visualize SuperDARN (Super Dual Auroral Radar Network) data, as well as other relevant space physics/space weather data sets and models.  This code is an international collaboration of many institutions and contributors.

DaViTPy pulls in datasets and models from a variety of data suppliers and model authors.  All users are requested properly cite the ORIGINAL supplier of the data or models used when presenting or publishing work.  Furthermore, it is often important to contact the original data provider for assistance in data interpretation and to arrange for proper attribution.

`Virginia Tech SuperDARN Page <http://vt.superdarn.org>`_

Install
=======
We recommend using Ubuntu 14.04 with this version of DaViTPy.  Although Macintosh install scripts are provided, more active development, testing, and use occurs in the Linux environment.  We do not currently offer any Windows support.


Prereqs
-------

* Python
* fortran compiler e.g. ``gfortran``


davitpyrc
---------
Settings pertaining to server addresses and passwords, data file directory structure, and other global parameters are stored in a run control file called davitpyrc.  
For most users, the default values in this file should be satisfactory., stored in ``davitpy/davitpy/davitpyrc``.  
After making a change, re-run the ``python setup.py install`` script to copy the run control file to the appropriate system location.

Linux
-----
::

    apt install git

    git clone https://github.com/vtsuperdarn/davitpy.git

    cd davitpy

    ./install/debian_dependencies.sh

    python setup.py install

Close and reopen Terminal to use DaViTPy.
    
MacOS
-----
It is easiest to have either homebrew (http://brew.sh/) or MacPorts (http://www.macports.org/) installed on your system.

Next, follow the instructions for Ubuntu, but for the dependencies script, choose one of the following::

    ./python_install_mac_brew.sh
   
    ./python_install_mac_port.sh

preferably after checking the dependencies to see if you already have them installed.

(**note**: you may encounter some errors because sometimes MacPorts will install binaries with the python version as an extension in their name, so f2py becomes f2py-2.7. If this happens, you will have to manually create symbolic links to the *-2.7 binaries or specify the extended name when running setup.py)

Usage
=====
To test davitpy and learn more about some of its functionality, please look at the included Jupyter notebooks.  To run these::

    cd davitpy/docs/notebook
    jupyter notebook

This command will launch a web browser with an interface that will allow you to run python code directly in a browsing window.  
The browser should show a list of the demonstration notebooks.  

If you do not see the demonstration notebooks, please make sure you are in the davitpy/doc/notebook/ directory before running the davitpy-notebook command.  
To run code within a cell, place your cursor in the cell and press shift-enter.

Jupyter Profile and 'davitpy' Executable
----------------------------------------
Please refer to the README in the ``bin`` directory of this repository for instructions on how to setup a custom Jupyter configuration to automatically import the davitpy library when starting an Jupyter session. 
The README also contains instructions on how to install a 'davitpy' executable Bash script if you wish to do so.

Issues and Bug reporting
========================

raytracing
----------
You must build the raytracing routines separately from the standard davitpy installation procedure.  
Please see the Makefile in davitpy/davitpy/raydarn.

Please report any problems/comments using the Issues tab of the davitpy GitHub page, or use this link: https://github.com/vtsuperdarn/davitpy/issues

Compile your own IRI, HWM, etc.
-------------------------------

If you want to compile IRI, HWM, RayDarn, and Tsygananko using a locally specified compiler (say, the Intel Fortran compiler) and user-specified compilation flags you could run something like::

    FC=ifort F77_FLAGS="-O2 -fbacktrace -fPIC" make


Developers
==========

Please help us develop this code!  Important instructions can be found in docs/development instructions.  Also, please join our development Google group, davitpy-dev (https://groups.google.com/forum/#!forum/davitpy).
