import sys
import os
import json
import warnings

"""
This file creates a json-file for filtering rules from quantile extraction results.
Run as 
    python parse_quantiles.py {path to dir that has results for all languages} > rules.json

Note the indices and modify them here:
Qs = [10,25,75,90]
       0  1  2  3
Qs = [1,2,5,7,10,20,30,40,50,60,70,80,90,93,95,98,99] 
      0 1 2 3  4  5  6  7  8  9 10 11 12 13 14 15 16
"""

selection_index = {"number_of_words":[[7],[">"]],
                   "number_of_lines":[[7],[">"]],
                   "number_of_characters":[[7],[">"]],
                   "language_identification":[[7],[">"]],
                   "perplexity":[[9],["<"]],
                   "stop_words":[[7],[">"]],
                   "special_characters":[[9],["<"]],
                   "flagged_words":[[9],["<"]],
                   "words_per_line":[[7],[">"]],
                   "words_per_line_mean":[[7],[">"]],
                   "short_line_ratio":[[9],["<"]],
                   "character_repetition10":[[9],["<"]],  #TODO: think if 0<x<3 better
                   "character_repetition5":[[9],["<"]],   #TODO: same
                   "word_repetition":[[7,9],[">","<"]],
                   "unigram_entropy":[[7,9],[">","<"]],
                   "lines_end_in_punct":[[7],[">"]]
                   }

results = {}

dir = sys.argv[1]
warnings.warn("WARNING: Remember to check the selection index dictionary. Different indices are needed for 10,25,75,90 quantiles and 10,20,...,90 quantiles.")

for file in os.listdir(dir):
    if ".txt" in file:
        with open(dir+file, 'r') as f:
            lines = f.readlines()
            #lang = "_".join(file.split("_")[:1])
            lang = file.split(".")[0]
            if lang == "en":
                continue
            elif lang=="large_en":
                lang = "en"
            results[lang] = {}
            for line in lines:
                if ".gz" not in line and line!="\n" and "..." not in line:
                    #print(line)
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