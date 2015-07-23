## Ipython Profile and 'davitpy' Executable
This README.md should contain instructions on how to setup a custom ipython configuration to automagically import the davitpy library when starting an ipython session. It should also contain instructions on how to install a 'davitpy' executable file (bash script) if you wish to do so. If this README doesn't contain this information, make a pull request to add it!

### Ipython Profiles

The following has only been tested in linux (but should work in OS X, because bash).

To install the davitpy ipython profile, one simply needs to copy the 'profile_davitpy' directory in the bin folder of the davitpy repository into the ipython configuration directory. For example on Ubuntu 14.04, the ipython configuration directory is located in the home directory. For example:

    /home/ashtonsethreimer/.ipython

so for my example, one simply needs to copy the 'profile_davitpy' directory into the '/home/ashtonsethreimer/.ipython' directory. To use this profile when using ipython, one simply executes the following command:

    ipython --profile=davitpy

Awesome!

### 'davitpy' Executable

The following has only been tested in linux (but should work in OS X, because bash). Also, it is important to note that the executable requires that you have followed the steps detailed above in the Ipython Profiles section of this README.

To install the davitpy executable, you will need to copy the davitpy file from the bin directory in the davitpy repository to some place on your computer. For the purposes of these instructions, we'll install it to a bin directory in your home folder. On my machine the path is '/home/ashtonsethreimer/bin/'. Be sure to make check that the davitpy file is executable. I would do that with the following command:

    chmod +x /home/ashtonsethreimer/bin/davitpy

Next you need to inform your shell that you would like it search the bin directory for executable files. In bash, we edit the .bashrc file in the home directory. In tcshell, we edit the .tcshrc file in the home directory. For bash, we need to add the following line to the end of the .bashrc file:

    export PATH=$PATH:/path/to/davitpy/file/

For me:

    export PATH=$PATH:/home/ashtonsethreimer/bin/

Once you have added this line to your shell config file (the .bashrc or .tcshrc or whatever you have) you can start a new shell to test if it worked. You should simply have to type: davitpy and hit enter.

Alternatively, one may instead create an alias in the .bashrc (or .tcshrc or...) file (probably the best method). To do this in bash, one simply needs to add the following line to the .bashrc:

    alias davitpy='ipython --profile=davitpy'

Enjoy!

### Bug reporting

Please report any problems/comments using the Issues tab of the davitpy GitHub page, or use this link: https://github.com/vtsuperdarn/davitpy/issues

###  Developers

Please help us develop this code!  Important instructions can be found in docs/development instructions.  Also, please join our development Google group, davitpy-dev (https://groups.google.com/forum/#!forum/davitpy).
