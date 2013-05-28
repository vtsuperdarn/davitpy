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

First, you will need RST to read standard SuperDARN dmap files. You will find a strpped down version of RST here: https://github.com/vtsuperdarn/RSTLite

Then, clone this repository:

    git clone https://github.com/vtsuperdarn/davitpy.git
    
Then cd into the cloned directory:

    cd davitpy
    
Then run thes install scripts specific to your system 

Ubuntu

    cd install/linux/
    sudo sh python_install_linux.sh
    sh set_paths_linux.sh
    
MacOS

    cd install/mac
    sudo sh python_install_mac.sh
    sh set_paths_mac.sh

    
Next, either restart the terminal, open a new one, or source your .bashrc, e.g.

    source ~/.bashrc
    
You may have to recompile the binaries:

    cd ../..
    ./mastermake
    
Now you are ready to go. From anywhere on your machine just type:

    davitpy

or 

    davitpy-notebook

or
 
    davitpy-qtconsole
    
And code away!

### Notes

* you will need basemap v1.0.3 or newer. You can clone and install it from <https://github.com/matplotlib/basemap>.
