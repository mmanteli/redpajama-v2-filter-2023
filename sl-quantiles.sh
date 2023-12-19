#!/bin/bash
#SBATCH --job-name=quantiles
#SBATCH --account=project_462000086
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=15G
#SBATCH --partition=small
#SBATCH -o logs/%x_%j.out
#SBATCH -e logs/%x_%j.err


# en de fr es it
lang=$1
if [ "$lang" = "en" ]; then
  sample_size=30
else
  sample_size=100
fi

data_path="samples/samples-for-higher-shortline-definition"
results_path="results/all_10th_quantiles"

echo ${data_path}/${lang}_full_${sample_size}_sample.txt

# I HAVE DONE THIS PREVIOUSLY ALREADY; UNCOMMENT IF YOU WANT NEW SPLITS
# generate for head bucket
#./generate_sample_paths.sh ${lang}_head $sample_size > samples/${lang}_head_${sample_size}_sample.txt
# generate for middle bucket
#./generate_sample_paths.sh ${lang}_middle $sample_size > samples/${lang}_middle_${sample_size}_sample.txt
# concatenate them
#cat samples/${lang}_*_${sample_size}_sample.txt | shuf > samples/${lang}_full_${sample_size}_sample.txt
# remove extras to avoid later confusion
#rm samples/${lang}_head_${sample_size}_sample.txt
#rm samples/${lang}_middle_${sample_size}_sample.txt

srun python3 get_10th_quantiles.py ${data_path}/${lang}_full_${sample_size}_sample.txt $lang > ${results_path}/${lang}_2x${sample_size}_results.txt

sacct -j $SLURM_JOBID
