#!/bin/bash

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

cat << eof > jobfile.job
#!/bin/bash
#SBATCH --partition=${partition}
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
        g16 < \$origin_file > "\$(basename \$origin_file .com)".log 
        echo "File \$origin_file submitted"
    fi
fi

for file in \$(ls -1v *.com | grep -v '+0.com'); do
g16 < \$file > "\$(basename \$file .com)".log
echo "File \$file submitted"
done

eof

sbatch jobfile.job
