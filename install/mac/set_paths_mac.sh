# Sets path and fundamental environment variables for DaViT-py

tmp="`echo $(which davitpy)`"
tmpdavitpy="`echo ${tmp%%davitpy/*}`"/davitpy
if [ "" == "$DAVITPY" ]
then
        echo "export DAVITPY="$tmpdavitpy >> ~/.bash_profile
fi

# Add ipython_dir to the environment variables
if [ "" == "$IPYTHON_DIR" ]
then
        echo "export IPYTHON_DIR=~/.ipython" >> ~/.bash_profile
fi