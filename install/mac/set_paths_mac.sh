# Sets path and fundamental environment variables for DaViT-py

tmp="`echo $(which davitpy)`"
tmpdavitpy="`echo ${tmp%%davitpy/*}`"/davitpy
if [ "" == "$DAVITPY" ]
then
        echo "export DAVITPY="$tmpdavitpy >> ~/.bash_profile
fi