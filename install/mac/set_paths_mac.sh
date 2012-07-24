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