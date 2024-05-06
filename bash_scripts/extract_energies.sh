#!/bin/bash 

#This script is extracting component parts of SCF?
#https://gaussian.com/faq1/
#It is extracting lines  ET = 1414.828655 EV = -3843.476430  EJ =849.492336 EK = -74.206791 ENuc = 238.494946
# ENTVJ = -1340.660494 Ex = -74.112334 Ec = -2.536856 ETotM2e = -2251.9606613255 ETot = -1417.3096838703
#Saving it into an array, and saving into a csv file


extract_energy(){
 ###Function to extract DFT energies from a file. Including XC_energies 
 local file=$1
 output1=($(awk -v pattern1="ENuc" -v pattern2="EJ" '$0 ~ pattern1 && $0 ~ pattern2 {print $2, $4, $6, $8, $10}' $file))
 output2=($(awk -v pattern1="ENTVJ" -v pattern2="ETot" '$0 ~ pattern1 && $0 ~ pattern2 {print $2, $4, $6, $8, $10}' $file))
 output=(${output1[@]} ${output2[@]})
 echo ${output[@]}
 }

path_to_folder=$1 

cd $path_to_folder 

file_name="$(basename $(pwd)).csv"
touch ${file_name}

echo "Field,ET,EV,EJ,EK,ENuc,ENTVJ,Ex,Ec,ETotM2e,ETot" > $file_name 

#Extracting it from the files with the negative fields.
for file in $(ls -1rv *.log | grep "Z-"); 
do values=$(extract_energy $file)
final_vect=("$file" $values)
printf -v joined '%s,' "${final_vect[@]}"
echo "${joined%,}" >> $file_name
done 

#Extracting from positive files and 0
for file in $(ls -1v *.log | grep "Z+"); 
do values=$(extract_energy $file)
final_vect=("$file" $values)
printf -v joined '%s,' "${final_vect[@]}"
echo "${joined%,}" >> $file_name
done
