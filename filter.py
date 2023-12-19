import sys
import json
import numpy as np


# TL;DR:
# this is the final iteration of the filtering scripts. 
# Speed optimisations implemented.
# I made sure it works by running 0000/it_*.json.gz
# against the old iterations => works the same.
# Basically, this reads the "rules" file (json) as a dict
# and the quality signals of the data instance.
# if the rules are passed, the id of the data instance
# is printed.


METRICS = ["number_of_words", "number_of_lines", "number_of_characters","language_identification","perplexity","stop_words","special_characters", "flagged_words",  "words_per_line_mean", "short_line_ratio", "character_repetition10", "character_repetition5","word_repetition", "unigram_entropy", "lines_end_in_punct"]

# see end of metric_analysis.ipynb for these values
# this approximates 100 chars for each language as words
# e.g. English has apprx. 20 words in 100 chars
short_line_limit = {"en":100/5.16533,
                     "de":100/6.4507,
                     "fr":100/5.44505,
                     "it":100/5.54443,
                     "es":100/5.25742
                    }


def parse_rule(m, rule):
    """
    Goes over the rules dict. Reads the condition, and returns
    True if both > and < condition are fulfilled, else False.
    Both conditions are not required, most metrics only have < or >.
    """
    for eq, limit in rule.items():
        #print(m, eq, limit)
        if eq == ">":
            if not m >= float(limit):
                return False
        elif eq == "<":
            if not m <= float(limit):
                return False
    return True


def filter(signals, language, rules):
    """
    Goes over all metrics and returns False immediately if one fails.
    Else returns True.
    """

    # word_count
    number_of_words=signals["rps_doc_word_count"][0][2]
    if not parse_rule(number_of_words, rules["number_of_words"]):
        return False
    
    # line count
    number_of_lines=signals["ccnet_nlines"][0][2]
    if not parse_rule(number_of_lines, rules["number_of_lines"]):
        return False
    
    # character count
    number_of_characters=signals["ccnet_length"][0][2]
    if not parse_rule(number_of_characters, rules["number_of_characters"]):
        return False
    
    # certainty of language
    language_identification=signals["ccnet_language_score"][0][2]
    if not parse_rule(language_identification, rules["language_identification"]):
        return False
    
    # perplexity
    perplexity=signals["ccnet_perplexity"][0][2]
    if not parse_rule(perplexity, rules["perplexity"]):
        return False
    
    # fraction of stop words vs all words
    stop_words=signals["rps_doc_stop_word_fraction"][0][2]
    if not parse_rule(stop_words, rules["stop_words"]):
        return False
    
    # number of words that are non-aplhabetic
    special_characters=signals["rps_doc_frac_no_alph_words"][0][2]
    if not parse_rule(special_characters, rules["special_characters"]):
        return False
    
    # fraction of flagged words to all words
    flagged_words=signals["rps_doc_ldnoobw_words"][0][2]
    if not parse_rule(flagged_words, rules["flagged_words"]):
        return False
    
    # charactes in duplicate 10 grams
    character_repetition10=signals["rps_doc_frac_chars_dupe_10grams"][0][2]
    if not parse_rule(character_repetition10, rules["character_repetition10"]):
        return False
    
    # ... in duplicate 5 grams
    character_repetition5=signals["rps_doc_frac_chars_dupe_5grams"][0][2]
    if not parse_rule(character_repetition5, rules["character_repetition5"]):
        return False
    
    # fraction of unique words => hypothesis: remove both quantiles, as both
    # repetitive content and just a list of words is bad
    word_repetition=signals["rps_doc_frac_unique_words"][0][2]
    if not parse_rule(word_repetition, rules["word_repetition"]):
        return False
    
    # unigram entropy
    unigram_entropy=signals["rps_doc_unigram_entropy"][0][2]
    if not parse_rule(unigram_entropy, rules["unigram_entropy"]):
        return False
    
    # THESE ↓ require calculations, thus they are last 
    # => if something above fails, no need to calculate these
    
    # words per line => used to calculate two other measures
    words_per_line = np.array(signals["rps_lines_num_words"])[:,2]
    
    # mean words per line
    words_per_line_mean=np.mean(words_per_line)
    if not parse_rule(words_per_line_mean, rules["words_per_line_mean"]):
        return False
    
    # lines that have <100 chars (approximated by mean words length per language,
    # see the dict at the beginning of file)
    short_line_ratio=np.count_nonzero(words_per_line<short_line_limit[language])/number_of_lines
    if not parse_rule(short_line_ratio, rules["short_line_ratio"]):
        return False
        
    # lines that end in punctuation / all words => can be used to filter online shops etc.
    lines_end_in_punct=np.count_nonzero(np.array(signals["rps_lines_ending_with_terminal_punctution_mark"])[:,2]==1)/number_of_lines
    if not parse_rule(lines_end_in_punct, rules["lines_end_in_punct"]):
        return False
    
    # FINALLY if all passed
    return True


# ############## START HERE ##################


# f (below)  is the rule file. It should contain data like this:
"""
{
"en":{
      "number_of_words":{">":"65.0"},
      ...
     }
"fr":{
      "number_of_words":{">":"59.0"},
      ...
     }
...
}
"""
# there can also be both > and < given, like for word_repetition both are given.


# give language as "en", "fr", "de", "it" or "es"
language = sys.argv[1]
f = open("/scratch/project_462000086/data/redpajama-v2/quality_thresholds.json")
rules = json.load(f)[language]

# PIPED INPUT
for line in sys.stdin:
    j = json.loads(line)
    try:
        keep = filter(j["quality_signals"], language, rules)
        if keep:
            print(json.dumps({"id":j["id"]}))
    except:
        continue # if calculation fails, we assume problems with quality signals => problems overall
