#!/bin/bash

filetype=$1
num=$2

# Function to generate a random number between 0 and 4999
generate_random_number() {
    printf "%04d\n" $((RANDOM % 5000))
}

# Initialize an empty array to collect file paths
file_paths=()

# Loop to generate 10 random numbers and collect file paths
for ((i=0; i<$num; i++)); do
    random_number=$(generate_random_number)
    file_path="/scratch/project_462000086/data/redpajama-v2/quality-2023-14/${random_number}/${filetype}.signals.json.gz"
    
    # Check if the file exists before adding its path to the array
    if [ -f "$file_path" ]; then
        file_paths+=("$file_path")
    fi
done

# Display collected file paths
printf '%s\n' "${file_paths[@]}"


