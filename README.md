Instructions:

1. Choose the metrics that seems intuitively good (from total 40), but incorporate at least the metrics used in Cultura X (12 different metrics), preferably more to obtain better data
2. Follow example by Cultura X and use the distributions of the metrics to choose appropriate threshold for each metric per language
    2a. Extract the values
    2b. Compute p-quantiles -> Q1 for thresholds that favor high values, Q3 for thresholds that favor low values -> p maybe needs to be adjusted depending on the distribution
3. Filter the data with found thresholds


GENERAL DIR STRUCTURE:

- everything in amanda/ is something that is currently used
- additional_scripts contains backups and old code
- logs, samples, results are self evident (hopefully); some of these include README clarification.
- test_datasets contains hf-dataset with flags for which metrics each text passed etc. => these used in filter_analysis


ANALYSIS SCRIPTS

metric_analysis.ipynb:

- contains the choises made
- contains instructions on how to run
- contains the script to make the rule-file.

filter_analysis.ipynb:

- contains analysis of filter results, how many passed
- which metrics where used alone, which together
    - runs slowly, sorry

DATA COLLECTION SCRIPTS

generate_sample_paths.sh

- generates a file of random files to read in get_quantiles.py

get_quantiles.py and get_10th_quantiles.py

- reads random sample of files, collects the chosen metrics, and calculates quantiles
- get_quantiles calculates 10,25,75 and 90, get_10th_quantiles 10,20,...,90.

sl-quantiles.sh

- used to run generate_sample_paths.sh and get_quantiles.py on LUMI

parse_quantiles.py

- transforms results of get_quantiles and get_10th_quantiles to a json-file that is needed used for filtering.

FILTER

filter.py:

- final of 4 scripts (older can be found in old_scripts), faster than previous
- prints the id as json object if the document passes
- assumes the rule file (see above) is in data/redpajama-v2/
- the old versions do the filtering a bit slower and they return the results in different forms
    - e.g. hf-dataset 

sl-filter.sh:

- runs filter.py on LUMI



