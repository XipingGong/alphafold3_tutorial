#!/bin/bash
#SBATCH --job-name=af3                # Job name
##SBATCH --partition=franklin_gpu     # GPU Partition (queue) name (franklin_gpu is for teaching)
#SBATCH --partition=gpu_p             # GPU Partition (queue) name (gpu_p is for UGA Sapelo2). It specifies the GPU node.
#SBATCH --gres=gpu:1                  # Requests one GPU device 
#SBATCH --ntasks=1                    # Run a single task	
#SBATCH --cpus-per-task=32            # Number of CPU cores per task
#SBATCH --mem=40gb                    # Job memory request
#SBATCH --time=10:00:00               # Time limit hrs:min:sec
#SBATCH --output=%x.%j.out            # Standard output log
#SBATCH --error=%x.%j.out             # Redirect stderr to the same file as stdout

# Check argument
if [ $# -lt 1 ]; then
    echo "Usage: sbatch af3.sh <input_json_file>"
    exit 1
fi
json_file=$1 # it must have a json file input in the current directory

SECONDS=0 # Reset
echo "# Starting >>"
echo ""

#af3_param_dir='/work/mibo8110/instructor_data/alphafold3' # You have to request the parameters file to run AF3
af3_param_dir='/home/xg69107/program/alphafold3' # You have to request the parameters file to run AF3 from Google DeepMind.
work_dir=`pwd` # using the current directory to submit jobs

echo "$ cat $work_dir/$json_file"
        cat $work_dir/$json_file
echo ""

echo "$ nvidia-smi # Showing the GPU to use"
        nvidia-smi
echo ""

# In the UGA Sapelo2 (this tells where you installed AF3)
echo "Running af3 model >>" # Check where to install and how to use
singularity exec \
     --nv \
     --bind $work_dir:/root/af_input \
     --bind $work_dir:/root/af_output \
     --bind $af3_param_dir:/root/models \
     --bind /db/AlphaFold3/20241114:/root/public_databases \
     /apps/singularity-images/alphafold-3.0.0-CCDpatched.sif \
     python /app/alphafold/run_alphafold.py \
     --json_path=/root/af_input/$json_file \
     --model_dir=/root/models \
     --db_dir=/root/public_databases \
     --output_dir=/root/af_output

# In the teaching franklin_gpu node
#singularity exec \
#     --nv \
#     --bind $work_dir:/root/af_input \
#     --bind $work_dir:/root/af_output \
#     --bind $af3_param_dir:/root/models \
#     --bind /db/AlphaFold3/20250822:/root/public_databases \
#     /apps/singularity-images/alphafold-3.0.0-CCDpatched.sif \
#     python /app/alphafold/run_alphafold.py \
#     --json_path=/root/af_input/$json_file \
#     --model_dir=/root/models \
#     --db_dir=/root/public_databases \
#     --output_dir=/root/af_output

echo "# Elapsed time: $SECONDS seconds"

