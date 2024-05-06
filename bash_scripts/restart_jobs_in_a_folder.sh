#!/bin/bash

#This file is restarting jobs which have chk files 
#For very big jobs were chk are transformed into fchk check 
#restart_very_long_jobs..

name="name"
memory=10
cpu=5
partition="regular"

while getopts ":n:m:p:c:q:" options; do


    case "${options}" in
    n)
       name=${OPTARG}
        ;;
    m) 
        memory=${OPTARG}
        ;;
    p) 
        path_to_folder=${OPTARG}
        ;;
    c) 
        cpu=${OPTARG}
        ;;
    q) 
        partition=${OPTARG}
        ;;
    esac
done

echo "name: ${name}"
echo "path: ${path_to_folder}"
echo "cpu: ${cpu}"
echo "memory: ${memory}"
echo "partition: ${partition}"

cd $path_to_folder
echo "Moving to $(pwd)"

cat << eof > restart.job
#!/bin/bash
#SBATCH --qos=${partition}
#SBATCH --job-name=${name}
#SBATCH --cpus-per-task=${cpu}
#SBATCH --mem=${memory}gb
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --output=%x-%j.out

echo "Job ID: \$SLURM_JOBID"
echo "Job Name: \$SLURM_JOB_NAME"
echo "Submit Directory: \$SLURM_SUBMIT_DIR"
echo "Submit Host: \$SLURM_SUBMIT_HOST"
echo "Number of CPUs is: \$SLURM_CPUS_PER_TASK"
echo "Memory is: \$SLURM_MEM_PER_NODE"

## Do not touch:
export SCRATCH_DIR=\$SLURM_SUBMIT_DIR/g16_\$SLURM_JOBID
mkdir -p \$SCRATCH_DIR


echo "Scratch Directory: \$SCRATCH_DIR"

module load Gaussian/16
export GAUSS_SCRDIR=\$SCRATCH_DIR

# Insert nodes and cores in the header of the input file

origin_file=\$(ls *+0.com)

if [ -z \$origin_file ]
then
    echo "No File with zero field"
else
    if [ -e \$origin_file ]
    then
    	for i in \$(grep "%chk=" \$origin_file | cut -d '=' -f 2); do
	if [ -f \$i ]
	then 
		echo "Found chk file for \$origin_file , not computing it"
	else
        	g16 < \$origin_file > "\$(basename \$origin_file .com)".log 
        	echo "File \$origin_file submitted"
	fi
	done
    fi
fi

for file in \$(ls -1v *.com | grep -v '+0.com'); do
for i in \$(grep "%chk=" \$file | cut -d '=' -f 2); do
if  [ -f \$i ]
then
echo "Found chk file \$i for \$file . Not computing it."
else
g16 < \$file > "\$(basename \$file .com)".log
echo "File \$file submitted"
fi
done
done

eof

sbatch restart.job
