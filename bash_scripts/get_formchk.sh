#!/bin/bash 

path=$1 

cd $path 

echo "Extracting fchk in folder $(pwd)"

module load Gaussian

for file in $(ls *.chk); do 
name=$(basename $file .chk)
formchk $file ${name}.fchk
done 
