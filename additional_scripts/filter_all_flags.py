import sys
import json
import gzip
import numpy as np
from datasets import disable_caching
disable_caching()

# words per line removed as it is not needed to filter => mean and short line ratio are used
# "words_per_line",
METRICS = ["number_of_words", "number_of_lines", "number_of_characters","language_identification","perplexity","stop_words","special_characters", "flagged_words",  "words_per_line_mean", "short_line_ratio", "character_repetition10", "character_repetition5","word_repetition", "unigram_entropy", "lines_end_in_punct"]

CACHE = "/scratch/project_462000086/data/redpajama-v2/datasets_cache"
# see end of metric_analysis.ipynb for these values
short_line_limit = {"en":100/5.16533,
                     "de":100/6.4507,
                     "fr":100/5.44505,
                     "it":100/5.54443,
                     "es":100/5.25742
                    }


def parse_quality_signals(signals, language):
    results={}
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
    for m in METRICS:
        results[str(m)] = eval(m)
    
    return results

def wrap_filter(rules, language):
    def filter(j):
        """
        Return True, if instance j passes all the rules. Else returns False.
        """
        # parse the signals e.g. calculate means of some measures
        signals = parse_quality_signals(j["quality_signals"], language)

        j["keep"]=True
        j["ut1"] =str(j["quality_signals"]["rps_doc_ut1_blacklist"][0][2])
        for m in METRICS:
            for key,value in rules[m].items():
                filt = lambda x : eval("x"+key+"="+value)
                #print(m, ":",str(signals[m])+key+"="+value)
                j[m] = filt(signals[m])
                if not filt(signals[m]):
                    j["keep"] =False   # one "summary" flag for easy removal
        return j
    return filter


    


# ############## START HERE ##################

language = sys.argv[1]
path_to_random_sample = sys.argv[2]
f = open("/scratch/project_462000086/data/redpajama-v2/quality_thresholds.json")
rules = json.load(f)[language]

"""
# PIPED INPUT
for line in sys.stdin:
    j = json.loads(line)
    j = filter(j,rules)
    print(json.dumps({"id":j["id"], "id_int":j["id_int"], "keep":j["keep"]}))
"""



# datasets
import datasets
text_list = []
signal_list = []
with open(path_to_random_sample, 'r') as f:
    for line in f:
        r = line.split()[0].replace("lang", language)   # select the correct language and remove \n
        signal_list.append(r)
        # remove "signals." and replace quality as texts
        text_list.append(r.replace("quality-2023-14", "texts-2023-14").replace("signals.", ""))

texts=[]
limit=35
if language=="en":
    limit=10
for t in text_list[:limit]:
    with gzip.open(t, 'rt') as f:
        for line in f:
            j = json.loads(line)
            texts.append({"raw_content":j["raw_content"]})


dataset_texts = datasets.Dataset.from_list(texts)
del texts

signals=[]
for t in signal_list[:limit]:
    with gzip.open(t, 'rt') as f:
        for line in f:
            j = json.loads(line)
            signals.append({"id":j["id"], "url":j["metadata"]["url"], "quality_signals":j["quality_signals"]})

dataset_signals = datasets.Dataset.from_list(signals)
del signals

dataset = datasets.concatenate_datasets([dataset_texts,dataset_signals],axis=1)
del dataset_texts
del dataset_signals


dataset = dataset.map(wrap_filter(rules, language))
dataset.save_to_disk("en_test_data.hf")






