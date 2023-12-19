import sys
import os
import json
import warnings

"""
This file creates a json-file for filtering rules from quantile extraction results.
Run as 
    python parse_quantiles.py {path to dir that has results for all languages} > rules.json
"""

selection_index = {"number_of_words":[[0],[">"]],
                   "number_of_lines":[[0],[">"]],
                   "number_of_characters":[[0],[">"]],
                   "language_identification":[[0],[">"]],
                   "perplexity":[[3],["<"]],
                   "stop_words":[[0],[">"]],
                   "special_characters":[[3],["<"]],
                   "flagged_words":[[3],["<"]],
                   "words_per_line":[[0],[">"]],
                   "words_per_line_mean":[[0],[">"]],
                   "short_line_ratio":[[3],["<"]],
                   "character_repetition10":[[3],["<"]],  #TODO: think if 0<x<3 better
                   "character_repetition5":[[3],["<"]],   #TODO: same
                   "word_repetition":[[0,3],[">","<"]],
                   "unigram_entropy":[[0,3],[">","<"]],
                   "lines_end_in_punct":[[0],[">"]]
                   }

results = {}

dir = sys.argv[1]
warnings.warn("WARNING: Remember to check the selection index dictionary. Different indices are needed for 10,25,75,90 quantiles and 10,20,...,90 quantiles.")

for file in os.listdir(dir):
    if ".txt" in file:
        with open(dir+file, 'r') as f:
            lines = f.readlines()
            lang = "_".join(file.split("_")[:1])
            results[lang] = {}
            for line in lines:
                if "json.gz" not in line and line!="\n":
                    l = line.replace("\n","").split("\t")
                    key = l[0].replace(": ", "")
                    results[lang][key] = {}
                    value = eval(l[1])
                    selection_values = selection_index[key]
                    thrshl_ind = selection_values[0]
                    thrshl_dir = selection_values[1]
                    for v,k in zip(thrshl_ind, thrshl_dir):
                        #print(f'results {lang} {key} {k} = {value} {v}')
                        results[lang][key][k] = str(value[v])
                    

print(json.dumps(results, indent=4))