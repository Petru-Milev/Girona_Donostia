#!/bin/bash

#this file is restating jobs in a folder where chk files are being 
#formated to fchk files and then chk are deleted
#it will automatically format all existing chk to fchk, and then
#do the calculation for files which have not been computed and 
#convert new chk to fchk and delete chk

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

for file in \$(ls *.chk); do
name=\$(basename \$file .chk)
formchk \$file \${name}.fchk
done 

origin_file=\$(ls *+0.com)

if [ -z \$origin_file ]
then
    echo "No File with zero field"
else
    if [ -e \$origin_file ]
    then
    	for i in \$(grep "%chk=" \$origin_file | cut -d '=' -f 2); do
	random_var=\$(basename \$i .chk)
	name_fchk=\${random_var}.fchk
	if [ -f \$name_fchk ]
	then 
		echo "Found fchk file for \$origin_file , not computing it"
	else
        	g16 < \$origin_file > "\$(basename \$origin_file .com)".log 
        	echo "File \$origin_file submitted"
	fi
	done
    fi
fi

to_save="empty_file.chk"
to_delete="empty_file.chk"

for file in \$(ls -1v *.com | grep -v '+0.com'); do
for i in \$(grep "%chk=" \$file | cut -d '=' -f 2); do
random_var=\$(basename \$i .chk)
name_formchk=\${random_var}.fchk
if  [ -f \${name_formchk} ]
then
echo "Found fchk file \${name_formchk} for \$file . Not computing it."
else
g16 < \$file > "\$(basename \$file .com)".log
echo "File \$file submitted"
formchk \$(basename \$file .com).chk \$(basename \$file .com).fchk
to_delete=\${to_save}
rm \${to_delete}
echo "removed \${to_delete}"
to_save=\$(basename \$file .com).chk
fi
done
done

eof

sbatch restart.job
