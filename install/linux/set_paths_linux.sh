# Sets path and fundamental environment variables for DaViT-py

tmp="`echo $(which davitpy)`"
tmpdavitpy="`echo ${tmp%%davitpy/*}`"/davitpy
if [ "" == "$DAVITPY" ]
then
	echo "# DaViTpy environment variables" >> ~/.bashrc
        echo "export DAVITPY='"${tmpdavitpy}"'" >> ~/.bashrc
	echo "export PATH="${DAVITPY}"/bin:\${PATH}" >> ~/.bashrc
fi
