## DaViT-py

Welcome to the Data and Visualization Toolkit-Python.  This code base is designed to allow you to access and visualize SuperDARN (Super Dual Auroral Radar Network) data, as well as other relevant space phyics/space weather data sets and models.  This code is an international collaboration of many institutions and contributors.

This version of the code is based on the "setup" branch, and is designed to make installation easier by more properly conforming to standard python setup/installation practices.  This code is still very much in the development phase, and should not be considered stable.

DaViTPy pulls in datasets and models from a variety of data suppliers and model authors.  All users are requested properly cite the ORIGINAL supplier of the data or models used when presenting or publishing work.  Furthermore, it is often important to contact the original data provider for assistance in data interpration and to arrange for proper attriution

* Project page
http://vtsuperdarn.github.com/davitpy/

* Project wiki
https://github.com/vtsuperdarn/davitpy/wiki

* Project documentation
http://davit.ece.vt.edu/davitpy/

* Project Milestones
https://github.com/vtsuperdarn/davitpy/issues/milestones

If you get a Bus Error when using radDataRead() and/or radDataReadRec() functions, you probably have to recompile the dmapio library on your local computer.  This can be done by going to davitpy/pydarn/dmapio and typing 'make clean' followed by 'make'.

### Install instructions

We recommend using Ubuntu 14.04 with this DaViTPy.  Although Macintosh install scripts are provided, more active development, testing, and use occurs in the Linux environment.  We do not currently offer any Windows support, although you are more than welcome to try and make it work in any environment you choose.  Please be aware that much of the included code (especially the models) is fortran code  (i.e. MSIS, IRI, IGRF, etc...) wrapped with python wrappers. This means that these models must be compiled with a fortran compiler on your machine before running.  This is normally taken care of in the installation process listed below, but it is useful to know that this is a potential source of problems for making DaViTPy work.

####Ubuntu
Please use Ubuntu 14.04.  Older versions may not install compatible versions of the dependencies.

Open a terminal window.  Make sure git is installed:

    sudo apt-get install git

Now download DaViTPy:

    git clone https://github.com/vtsuperdarn/davitpy.git
    
This will create a new directory called 'davitpy' in your current directory (probably your home directory).  If you do not want DaViTPy installed in ~/davitpy, you may move the file to a different directory now.  Next, change to your davitpy directory:

    cd davitpy

We need to install some dependencies using a script that makes calls to apt-get and pip.  To run this script:

    sudo ./install/debian_dependencies.sh

Note that this script also modifies your ~/.bashrc file to set environment variables identifying the DaViTPy installation location, the SuperDARN database access information, and others.  Because of this, please close your terminal and open a new session to refresh your environment variables.

Now, run the high-level Makefile to make the fortran code and SuperDARN read routines happy.  Do NOT run make as sudo.

    cd davitpy
    make

If your system is up-to-date and everything was compiled using the default compiler (true on most computers), this will run without any problems.  If it didn't work, there's still hope!  If you have an older system, you may need to specify which compilers to use.  If you have a REALLY old system, you may still be able to complile by removing some of the optional (but desireable) flags.  For example, one could run:

    make F77=/usr/local/bin/gfortran44 FC=/usr/local/bin/gfortran44 F77_FLAGS="-O2 -fbacktrace -fPIC"

Next, do the actual davitpy install (from in the davitpy directory):

    sudo python setup.py install

Now, you can run make one more time just to be safe:

    make

That should be it!  You may want to restart your terminal once more just to make sure the environment variables are refreshed.


####MacOS
It is easiest to have either homebrew (http://brew.sh/) or MacPorts (http://www.macports.org/) installed on your system.

Next, follow the instructions for Ubuntu, but for the dependencies script, choose one of the following:

    sudo ./python_install_mac_brew.sh
    sudo ./python_install_mac_port.sh

(**note**: you may encounter some errors because sometimes macport will install binaries with the python version as an extension in their name, so f2py becomes f2py-2.7. If this happens, you will have to manually create symbolic links to the *-2.7 binaries or specify the extended name when calling the makefile)
    
####Usage
To test davitpy and learn more about some of its functionality, please look at the included iPython notebooks.  To run these:

    cd davitpy/docs/notebook
    davitpy-notebook

This command will launch a web broswer with an interface that will allow you to run python code directly in a browsing window.  The browser should show a list of the demonstration notebooks.  If you do not see the demonstration notebooks, please make sure you are in the davitpy/doc/notebook/ directory before running the davitpy-notebook command.  To run code within a cell, place your cursor in the cell and press shift-enter.

A number of scripts are provided to bring up a python environment with davitpy functionality pre-loaded:

    davitpy
    davitpy-notebook
    davitpy-qtconsole
    
### Issues and Bug reporting

This version of davitpy does not support ray tracing.  For this functionality, please see https://github.com/vtsuperdarn/davitpy/releases/tag/0.2-master_with_ray_tracing.

Please report any problems/comments using the Issues tab of the davitpy GitHub page, or use this link: https://github.com/vtsuperdarn/davitpy/issues

###  Developers

Please help us develop this code!  Important instructions can be found in docs/development instructions.  Also, please join our development Google group, davitpy-dev (https://groups.google.com/forum/#!forum/davitpy).
