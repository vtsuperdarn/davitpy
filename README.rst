.. image:: https://travis-ci.org/scivision/davitpy.svg
    :target: https://travis-ci.org/scivision/davitpy

========
DaViT-py
========

Welcome to the Data and Visualization Toolkit-Python.  This code base is designed to allow you to access and visualize SuperDARN (Super Dual Auroral Radar Network) data, as well as other relevant space phyics/space weather data sets and models. As such, DaViT-py includes code for reading and plotting SuperDARN data (iqdata, rawacf, fitacf, and convection maps) and python wrappers for various fortran based models (AACGM, HWM14, IGRF11, IRI11, NRLMSISE00, IGRF2008, and RayDARN HF raytracing).  This code is an international collaboration of many institutions and contributors.

DaViTPy pulls in datasets and models from a variety of data suppliers and model authors.  
All users are requested to properly cite the ORIGINAL supplier of the data or models used when presenting or publishing work.  
Furthermore, it is often important to contact the original data provider for assistance in data interpretation and to arrange for proper attribution.

`Virginia Tech SuperDARN Page <http://vt.superdarn.org>`_

Davit-py Users
--------------
While git can be very useful for managing and updating software, users are encouraged to join the davitpy-users Google group (https://groups.google.com/forum/#!forum/davitpy-users) to keep in e-mail contact.  Announcements (not too often) will be made about changes to the software and you will be able to post questions or browse for help.  Bug reports should still go through github, but anything else can be addressed here.  Active developers of DaViTpy should refer to the DaViTpy-dev group with instructions at the bottom of this file.


Install
=======
We recommend using Ubuntu 14.04 with this version of DaViTPy.  Although Macintosh install scripts are provided, more active development, testing, and use occurs in the Linux environment.  We do not currently offer any Windows support.

::

    git clone https://github.com/vtsuperdarn/davitpy.git

    cd davitpy

    python setup.py develop


Prereqs
-------

* Python 2.7. `Miniconda <>`_ is strongly suggested.
* fortran compiler e.g. ``gfortran``

Linux
~~~~~
::

    apt install git libopenmpi-dev libssl-dev gfortran g++


Mac
~~~
::

    brew install gcc openmpi

davitpyrc
---------
Settings pertaining to server addresses and passwords, data file directory structure, and other global parameters are stored in a run control file called davitpyrc.  
For most users, the default values in this file should be satisfactory., stored in ``davitpy/davitpy/davitpyrc``.  
After making a change, re-run the ``python setup.py install`` script to copy the run control file to the appropriate system location.
    

Usage
=====
To test davitpy and learn more about some of its functionality, please look at the included Jupyter notebooks.  To run these::

    cd docs/notebook
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

If you report a bug or issue, please include as much information as possible. 
If a developer can't reproduce your problem, they can't help you solve it very easily! At a bare minimum, it is very helpful to include the following information: 1) operating system, 2) code executed that produced the error, and 3) any and all error messages/logs that you received.

As of DaViTPy release 0.5, we switched to using the logging module for reporting information. 
Before submitting a bug, to help give developers as much information as possible, please do the following before running your code::

    import davitpy
    davitpy.rcParams['verbosity'] = "debug-annoying"

and then execute the code you used to produce the bug. 
The above code tells DaViTPy to output all information to the terminal.


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
