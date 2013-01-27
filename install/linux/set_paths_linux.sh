#!/bin/bash

# Sets path and fundamental environment variables for DaViT-py

# *********************************
# Modify this part if needed
# *********************************
TMP_RST=/davit/lib/rst/rst
TMP_DAVITPY=/davitpy
TMP_PYPLOTS=/data/pyplots

# *********************************
# You probably do not need to modify the following part
# *********************************
# Set path to DAVITPY
if [ "" == "${DAVITPY}" ]
then
  echo "# DaViTpy environment variables:" >> ~/.bashrc
	echo "export DAVITPY='"$TMP_DAVITPY"'" >> ~/.bashrc
	echo "export PATH=\${DAVITPY}/bin:\${PATH}" >> ~/.bashrc
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi
# Set path to DAVITPY
if [ "" == "${PYTHONPATH}" ]
then
	echo "export PTHONPATH=$PYTHONPATH:$DAVITPY" >> ~/.bashrc
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi
# Set RSTPATH
if [ "" == "${RSTPATH}" ]
then
  echo "# RST environment variables:" >> ~/.bashrc
	echo "export RSTPATH='"${TMP_RST}"'" >> ~/.bashrc
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi

# Set PYPLOTS
if [ "" == "${PYPLOTS}" ]
then
  echo "# Plotting directory:" >> ~/.bashrc
	echo "export PYPLOTS='"${TMP_PYPLOTS}"'" >> ~/.bashrc
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi

# Set Database users
if [ '' == "${DBREADUSER}" ]
then
  echo "#db read user" >> ~/.bashrc
	echo "export DBREADUSER='sd_dbread'" >> ~/.bashrc
	echo "export DBREADPASS='5d'" >> ~/.bashrc
fi

# Set Database users
if [ '' == "${DBWRITEUSER}" ]
then
	echo "#db write user" >> ~/.bashrc
	echo "export DBWRITEUSER=''" >> ~/.bashrc
	echo "export DBWRITEPASS=''" >> ~/.bashrc
	echo "must manually set DBWRITEUSER and DBWRITEPASS in .bashrc for writing to db (must obtain password from admins)"
fi

# Set Database users
if [ '' == "${SDDB}" ]
then
	echo "#mongodb address" >> ~/.bashrc
	echo "export SDDB='sd-work9.ece.vt.edu:27017'" >> ~/.bashrc
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi

# Set SFTP DATABASE
if [ '' == "${VTDB}" ]
then
	echo "#sftp server address" >> ~/.bashrc
	echo "export VTDB='sd-data.ece.vt.edu'" >> ~/.bashrc
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi
