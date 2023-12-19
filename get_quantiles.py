import sys
import json
import gzip
import numpy as np

Q1 = 10  # best according to CulturaX
Q2 = 25
Q3 = 75
Q4 = 90  # best according to CulturaX

METRICS = ["number_of_words", "number_of_lines", "number_of_characters","language_identification","perplexity","stop_words","special_characters", "flagged_words", "words_per_line", "words_per_line_mean", "short_line_ratio", "character_repetition10", "character_repetition5","word_repetition", "unigram_entropy", "lines_end_in_punct"]


# see end of metric_analysis.ipynb for these values
short_line_limit = {"en":100/5.16533,
                     "de":100/6.4507,
                     "fr":100/5.44505,
                     "it":100/5.54443,
                     "es":100/5.25742
                    }


results={key:[] for key in METRICS}

def flatten(matrix):
    """ Flattening that works for both nested lists and unnested lists """
    return [item for row in matrix for item in (row if isinstance(row,np.ndarray) or isinstance(row, list) else [row])]


def calculate_quantiles(arr):
    #try:
        # Sorting the array
        arr = flatten(arr)
        sorted_arr = [i for i in arr if i!=None] 
        #sorted_arr = np.sort([i for i in arr if i!=None])    # apparently, no sorting is needed
        # Calculating quantiles (np.quantile and np.percentile identical)
        percentile_Q1 = np.percentile(sorted_arr, Q1)
        percentile_Q2 = np.percentile(sorted_arr, Q2)
        percentile_Q3 = np.percentile(sorted_arr, Q3)
        percentile_Q4 = np.percentile(sorted_arr, Q4)
        return percentile_Q1, percentile_Q2, percentile_Q3, percentile_Q4
    #except:
        return "failed", "calculation","",""


def quality_signals(signals, results, language):
   
    # word_count
    number_of_words=signals["rps_doc_word_count"][0][2]
    
    # line count
    number_of_lines=signals["ccnet_nlines"][0][2]
    
    # character count
    number_of_characters=signals["ccnet_length"][0][2]
    
    # certainty of language
    language_identification=signals["ccnet_language_score"][0][2]
    
    # perplexity
    perplexity=signals["ccnet_perplexity"][0][2]
    
    # fraction of stop words vs all words
    stop_words=signals["rps_doc_stop_word_fraction"][0][2]
    
    # number of words that are non-aplhabetic
    special_characters=signals["rps_doc_frac_no_alph_words"][0][2]
    
    # fraction of flagged words to all words
    flagged_words=signals["rps_doc_ldnoobw_words"][0][2]
    
    # words per line => used to calculate two other measures
    words_per_line = np.array(signals["rps_lines_num_words"])[:,2]
    
    # mean words per line
    words_per_line_mean=np.mean(words_per_line)
    
    # lines that have <100 chars (approximated by mean words length per language)
    short_line_ratio=np.count_nonzero(words_per_line<short_line_limit[language])/number_of_lines
    
    #short_line_length_ratio ??????
    
    # charactes in duplicate 10 grams
    character_repetition10=signals["rps_doc_frac_chars_dupe_10grams"][0][2]
    
    # ... in duplicate 5 grams
    character_repetition5=signals["rps_doc_frac_chars_dupe_5grams"][0][2]
    
    # fraction of unique words => hypothesis: remove both quantiles, as both
    # repetitive content and just a list of words is bad
    word_repetition=signals["rps_doc_frac_unique_words"][0][2]
    
    # unigram entropy
    unigram_entropy=signals["rps_doc_unigram_entropy"][0][2]
    
    # lines that end in punctuation / all words => can be used to filter online shops etc.
    lines_end_in_punct=np.count_nonzero(np.array(signals["rps_lines_ending_with_terminal_punctution_mark"])[:,2]==1)/number_of_lines

    # add all to results
    for k,v in results.items():
        v.append(eval(k))
    
    return results
    

# starting here
# read which files are included in random sample
path_to_random_sample = sys.argv[1]
language = sys.argv[2]   # as "en" or "de"
random_sample = []  
with open(path_to_random_sample, 'r') as f:
    for line in f:
        random_sample.append(line.split()[0])
#print("Read files: ", random_sample[0] , "...\n")
    
# loop over selected files
for file_path in random_sample:   
    with gzip.open(file_path, 'rt') as gz_file:
        for line in gz_file:
            j = json.loads(line)
            signals = j["quality_signals"]
            results = quality_signals(signals, results, language)
            
print(f'Read {len(results["number_of_lines"])} lines from {random_sample[0]} ... \n')

# print results   
for k,v in results.items():
    q1, q2, q3, q4 = calculate_quantiles(v)
    print(f'{k}: \t [{q1}, {q2}, {q3}, {q4}]')
