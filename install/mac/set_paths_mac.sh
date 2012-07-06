# Sets path and fundamental environment variables for DaViT-py

tmp="`echo $(which davitpy)`"
tmpdavitpy="`echo ${tmp%%davitpy/*}`"/davitpy
if [ "" == "$DAVITPY" ]
then
        echo "# DaViTpy environment variables:" >> ~./bash_profile
	echo "export DAVITPY='"$tmpdavitpy"'" >> ~/.bash_profile
	echo "export PATH="${DAVITPY}"/bin:\${PATH}" >> ~/.bash_profile
fi
