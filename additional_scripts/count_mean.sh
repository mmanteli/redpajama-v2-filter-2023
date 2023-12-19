#!/bin/bash

# this script runs count_mean_word_length.py 
# => calculates the mean word length per language

lang=$1

# Read each line from "paths" file
while IFS= read -r file_path; do
    # Use 'cat' to concatenate the contents of the files
    zcat "$file_path" | python count_mean_word_length.py >> ${lang}_means.txt
done < "samples/${lang}_full_100_sample.txt"


file=${lang}_means.txt
# Check if the file exists
if [ ! -f "$file" ]; then
    echo "File $file not found."
    exit 1
fi

# Calculate the mean using awk
mean=$(awk '{ total += $1; count++ } END { if (count > 0) print total / count }' "$file")

if [ ! -z "$mean" ]; then
    echo "Mean: $mean"
else
    echo "No numbers found in the file."
fi

rm ${lang}_means.txt