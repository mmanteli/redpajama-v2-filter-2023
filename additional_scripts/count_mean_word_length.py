import sys
import json

value = 0
docs =0

for line in sys.stdin:
    try:
        j = json.loads(line)
        q = j["quality_signals"]
        value+= q["rps_doc_mean_word_length"][0][2]
        docs+=1
    except:
        continue
    
print(value/docs)
