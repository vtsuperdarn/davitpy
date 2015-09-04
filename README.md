## DaViT-py

Welcome to the Data and Visualization Toolkit-Python.  This code base is designed to allow you to access and visualize SuperDARN (Super Dual Auroral Radar Network) data, as well as other relevant space phyics/space weather data sets and models.  This code is an international collaboration of many institutions and contributors.

DaViTPy pulls in datasets and models from a variety of data suppliers and model authors.  All users are requested properly cite the ORIGINAL supplier of the data or models used when presenting or publishing work.  Furthermore, it is often important to contact the original data provider for assistance in data interpration and to arrange for proper attribution.

*  Virginia Tech SuperDARN Page
http://vt.superdarn.org

### Install instructions

We recommend using Ubuntu 14.04 with this version of DaViTPy.  Although Macintosh install scripts are provided, more active development, testing, and use occurs in the Linux environment.  We do not currently offer any Windows support, although you are more than welcome to try and make it work in any environment you choose.  Please be aware that much of the included code (especially the models) is fortran code  (i.e. MSIS, IRI, IGRF, etc...) wrapped with python wrappers. This means that these models must be compiled with a fortran compiler on your machine before running.  This is normally taken care of in the installation process listed below, but it is useful to know that this is a potential source of problems for making DaViTPy work.

#### davitpyrc
Settings pertaining to sevrer addresses and passwords, data file directory structure, and other global parameters are stored in a run control file called davitpyrc.  For most users, the default values in this file should be satisfactory.  However, you may make changes to this file if necessary.  It is stored in davitpy/davitpy/davitpyrc.  After making a change, re-run the setup.py install script (described below) to copy the run control file to the appropriate system location.

####Ubuntu
Please use Ubuntu 14.04 or newer.  Older versions may not install compatible versions of the dependencies.

Open a terminal window.  Make sure git is installed:

    sudo apt-get install git

Now download DaViTPy:

    git clone https://github.com/vtsuperdarn/davitpy.git
    
This will create a new directory called 'davitpy' in your current directory (probably your home directory).  If you do not want DaViTPy installed in ~/davitpy, you may move the file to a different directory now.  Next, change to your davitpy directory:

    cd davitpy

We need to install some dependencies using a script that makes calls to apt-get and pip.  You can either look through this file and install the necessary dependencies yourself (especially if you're on a different flavor of linux/unix or don't use apt-get and pip) or run the script.  To run this script:

    sudo ./install/debian_dependencies.sh

Note that this script also modifies your ~/.bashrc file to set environment variables identifying the DaViTPy installation location, the SuperDARN database access information, and others.  Because of this, please source your ~/.bashrc file (or close and reopen a new terminal window) to refresh your environment variables.

Next, do the actual davitpy install (from in the davitpy directory):

    sudo python setup.py install
    
If you are installing davitpy locally, or have other specific requirements you can use different command line options such as:

    python setup.py install --user

If your system is up-to-date and everything was compiled using the default compiler (true on most computers), this should be it!  You may want to restart your terminal once more just to make sure the environment variables are refreshed.

If it didn't work, there's still hope.  If you have an older system, you may need to specify which compilers to use in your ~/.bashrc file.  If you have a REALLY old system, you may still be able to complile by removing some of the optional (but desireable) flags in the indivdual model Makefiles.  Also, if you don't want to install davitpy but still want to use the python wrappers for the different models, you can compile several of these models using either the local makefiles or the upper level makefile.  For example, if you want to compile IRI, HWM, RayDarn, and Tsygananko using a locally specified compiler and user-specified compilation flags you could run:

make F77=/usr/local/bin/gfortran44 FC=/usr/local/bin/gfortran44 F77_FLAGS="-O2 -fbacktrace -fPIC"

####MacOS
It is easiest to have either homebrew (http://brew.sh/) or MacPorts (http://www.macports.org/) installed on your system.

Next, follow the instructions for Ubuntu, but for the dependencies script, choose one of the following:

    sudo ./python_install_mac_brew.sh
    sudo ./python_install_mac_port.sh

preferably after checking the dependicies to see if you already have them installed.

(**note**: you may encounter some errors because sometimes macport will install binaries with the python version as an extension in their name, so f2py becomes f2py-2.7. If this happens, you will have to manually create symbolic links to the *-2.7 binaries or specify the extended name when running setup.py)

####Usage
To test davitpy and learn more about some of its functionality, please look at the included iPython notebooks.  To run these:

    cd davitpy/docs/notebook
    ipython notebook

This command will launch a web broswer with an interface that will allow you to run python code directly in a browsing window.  The browser should show a list of the demonstration notebooks.  If you do not see the demonstration notebooks, please make sure you are in the davitpy/doc/notebook/ directory before running the davitpy-notebook command.  To run code within a cell, place your cursor in the cell and press shift-enter.

####Ipython Profile and 'davitpy' Executable
Please refer to the README.md in the bin directory of this repository for instructions on how to setup a custom ipython configuration to automagically import the davitpy library when starting an ipython session. The README also contains instructions on how to install a 'davitpy' executable file (bash script) if you wish to do so.

### Issues and Bug reporting

To use raytracing, you must build the raytracing routines separately from the standard davitpy installation procedure.  Please see the Makefile in davitpy/davitpy/raydarn.

Please report any problems/comments using the Issues tab of the davitpy GitHub page, or use this link: https://github.com/vtsuperdarn/davitpy/issues

###  Developers

Please help us develop this code!  Important instructions can be found in docs/development instructions.  Also, please join our development Google group, davitpy-dev (https://groups.google.com/forum/#!forum/davitpy).
