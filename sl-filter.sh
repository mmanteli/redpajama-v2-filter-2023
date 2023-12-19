#!/bin/bash
#SBATCH --job-name=filter
#SBATCH --account=project_462000086
#SBATCH --partition=small
#SBATCH --time=15:30:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=1G
#SBATCH -o logs/%x_%j.out
#SBATCH -e logs/%x_%j.err


module load parallel


lang=$1
#split="*"
path="/scratch/project_462000086/data/redpajama-v2/quality-2023-14"


echo "${path}/*/${lang}_*.json.gz" 
echo "start time: $(date)"

srun zcat ${path}/*/${lang}_*.json.gz | parallel --pipe -j32 -k --block 10M python3 filter.py $lang | pigz > results/${lang}.jsonl.gz

echo "end time: $(date)"

#seff $SLURM_JOBID
sacct $SLURM_JOBID
