# Sets path and fundamental environment variables for DaViT-py

# *********************************
# Modify this part if needed
# *********************************
TMP_RST=/davit/lib/rst/rst
TMP_DAVITPY=/davitpy

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
# Set RSTPATH
if [ "" == "${RSTPATH}" ]
then
    echo "# RST environment variables:" >> ~/.bashrc
	echo "export RSTPATH='"${TMP_RST}"'" >> ~/.bashrc
	echo "You can now check ~/.bash_profile to make sure the path has been updated, then restart your terminal."
fi