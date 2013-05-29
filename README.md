## DaViT-py

This is the ongoing development of a python alternative to the Data Visualization Toolkit for SuperDARN data analysis and visualization.

* Project page
http://vtsuperdarn.github.com/davitpy/

* Project wiki
https://github.com/vtsuperdarn/davitpy/wiki

* Project documentation
http://davit.ece.vt.edu/davitpy/

* Project Trello (ToDos)
https://trello.com/b/djb82luC

If you get a Bus Error when using radDataRead() and/or radDataReadRec() functions, you probably have to recompile the dmapio library on your local computer.  This can be done by going to davitpy/pydarn/dmapio and typing 'make clean' followed by 'make'.

### Install instructions

Note that we have developed using python 2.7.  If you use a different version, the code will probably not work.

You will need RST to read standard SuperDARN dmap files. You will find a stripped down version of RST here: https://github.com/vtsuperdarn/RSTLite

If you have a Mac, make sure you have macports installed.

Then, clone this repository:

    git clone https://github.com/vtsuperdarn/davitpy.git
    
Then cd into the cloned directory:

    cd davitpy
    
Then run the dependency install scripts specific to your system 

Note:  If you are running openSUSE, you need to install gcc

Ubuntu

    cd install/linux/
    sudo sh python_install_dependencies_ubuntu.sh
    
MacOS

    cd install/mac
    sudo sh python_install_dependencies_mac.sh

If you are not running Ubuntu or MacOS, you can manually install the dependencies listed in the python_install_*.sh, and set the environment variables in set_paths_*.sh.  Alternatively, you could write a script for your specific OS, and send it to us so that we can add it to the repository!

Next, run the environment variable scripts

Linux

    sh set_paths_linux.sh

MacOS

    sh set_paths_mac.sh
    

You will need basemap v1.0.3 or newer. You can clone and install it from <https://github.com/matplotlib/basemap>.

Next, either restart the terminal, open a new one, or source your .bashrc, e.g.

    source ~/.bashrc
    
    
You may have to recompile the binaries:

    cd ../..
    ./mastermake
    
Now you are ready to go. From anywhere on your machine just type:

    davitpy

for the interactive terminal, or 

    davitpy-notebook

for the notebook, or
 
    davitpy-qtconsole
    
for the QT console.
And code away!


### Using the example notebooks

In `docs/notebook` you will find a small collection of notebooks demonstrating the main modules of DaViTpy (see also the documentation: http://davit.ece.vt.edu/davitpy/).
Go to that directory and run

    davitpy-notebook


### Issues and Bug reporting

Please report any problems/comments using the Issues tab of the davitpy GitHub page, or use this link: https://github.com/vtsuperdarn/davitpy/issues

