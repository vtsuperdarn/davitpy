# Sets path and fundamental environment variables for DaViT-py

# *********************************
# Modify this part if needed
# *********************************
TMP_RST=/Users/sebastien/rst/VT_RST3
TMP_DAVITPY=/Users/sebastien/davitpy

# *********************************
# You probably do not need to modify the following part
# *********************************
# Set path to DAVITPY
if [ "" == "${DAVITPY}" ]
then
    echo "# DaViTpy environment variables:" >> ~/.bash_profile
	echo "export DAVITPY='"$TMP_DAVITPY"'" >> ~/.bash_profile
	echo "export PATH=\${DAVITPY}/bin:\${PATH}" >> ~/.bash_profile
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi
# Set RSTPATH
if [ "" == "${RSTPATH}" ]
then
    echo "# RST environment variables:" >> ~/.bash_profile
	echo "export RSTPATH='"${TMP_RST}"'" >> ~/.bash_profile
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi

# Set PYPLOTS
if [ "" == "${PYPLOTS}" ]
then
  echo "# Plotting directory:" >> ~/.bash_profile
	echo "export PYPLOTS='"${TMP_PYPLOTS}"'" >> ~/.bash_profile
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi

# Set Database users
if [ '' == "${DBREADUSER}" ]
then
  echo "#db read user" >> ~/.bash_profile
	echo "export DBREADUSER='sd_dbread'" >> ~/.bash_profile
	echo "export DBREADPASS='5d'" >> ~/.bash_profile
fi

# Set Database users
if [ '' == "${DBWRITEUSER}" ]
then
	echo "#db write user" >> ~/.bash_profile
	echo "export DBWRITEUSER=''" >> ~/.bash_profile
	echo "export DBWRITEPASS=''" >> ~/.bash_profile
	echo "must manually set DBWRITEUSER and DBWRITEPASS in .bashrc for writing to db (must obtain password from admins)"
fi

# Set Database users
if [ '' == "${SDDB}" ]
then
	echo "#mongodb address" >> ~/.bash_profile
	echo "export SDDB='sd-work9.ece.vt.edu:27017'" >> ~/.bash_profile
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi

# Set SFTP DATABASE
if [ '' == "${VTDB}" ]
then
	echo "#sftp server address" >> ~/.bash_profile
	echo "export VTDB='sd-data.ece.vt.edu'" >> ~/.bash_profile
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi
