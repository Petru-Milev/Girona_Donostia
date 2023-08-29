#!/bin/bash

name="name"
memory=10
cpu=5

while getopts ":n:m:p:c:" options; do


    case "${options}" in
    n)
       name=${OPTARG}
        ;;
    m) memory=${OPTARG}
        ;;
    p) path_to_folder=${OPTARG}
        ;;
    c) cpu=${OPTARG}
    esac
done

#SBATCH --partition=regular
#SBATCH --job-name=${name}
#SBATCH --cpus-per-task=${cpu}
#SBATCH --mem=${memory}gb
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --output=%x-%j.out
#SBATCH --time=48:00:00

echo "SBATCH --job-name=${name}"
echo "SBATCH --cpus-per-task=${cpu}"
echo "SBATCH --mem=${memory}gb"
echo "Specified path is $path_to_folder"

# Load environment for Gaussian
module load Gaussian/16

# Insert nodes and cores in the header of the input file

cd $path_to_folder

working_dir=$(pwd)
echo "Working directory is $working_dir"

origin_file=$(ls *+0.com)

if [ -z $origin_file ]
then
    echo "No File with zero field"
else
    if [ -e $origin_file ]
    then
        echo "$origin_file exists"
        g16 < $origin_file > ${origin_file%.com}.log
        echo "File $origin_file submitted"
    fi
fi

for file in $(ls -1v *.com | grep -v '+0.com'); do
g16 < $file > ${file%.com}.log
echo "File $file submitted"
done