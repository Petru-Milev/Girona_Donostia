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
        path_to_file=${OPTARG}
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
echo "path to file: ${path_to_file}"
echo "cpu: ${cpu}"
echo "memory: ${memory}"
echo "partition: ${partition}"

path_to_folder=$(dirname $path_to_file)
input=$(basename $path_to_file)
cd $path_to_folder

cat << eof > single_file.job
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

g16 < $input > "\$(basename $input .com)".log 

eof

sbatch single_file.job
