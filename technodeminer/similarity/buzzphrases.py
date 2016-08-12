from technodeminer.persistence.graph import connect_to_arango, get_technode_graph
from pattern.vector import Model, Document
from pattern.search import search
from pattern.en import parsetree, singularize
from collections import Counter
import unicodedata
import csv

def build_contract_list():
    db = connect_to_arango()
    contracts = db.col('contracts')
    contract_list = []
    for r2 in contracts.all():
        contract_lite = {}
        if 'contract' in r2:
            contract_lite['contract'] = r2['contract']
        if 'award_title' in r2:
            contract_lite['award_title'] = r2['award_title']
        if 'abstract' in r2:
            contract_lite['abstract'] = r2['abstract']
        contract_list.append(contract_lite)

    return contract_list
#np_counts = count_nps(contract_list[0:500], 'abstract')

# there's a minor bug in pattern..
def regularise_key(str):
    str = fix_comma(str)
    str = str.lower()
    str = singularize(str)
    return str


# counts ngrams > 2, return as dict
# if it starts with one of the stopwords (articles), require it be 1 word longer
# regularise keys (lowercase + singularize)
def count_noun_phrases(nphrases, text, minlength=2):
    stopwords = ['a', 'an', 'the', 'this']
    #text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    np_dict = {}
    for np in nphrases:
        this_string = np.string
        # if NP is long enough
        if len(np.words) > minlength:
            # if it starts with an article..
            if any(this_string.startswith(stopword) for stopword in stopwords):
                if len(np.words) > (minlength+1):
                    np_dict[regularise_key(this_string)] = text.count(this_string)
            else:
                np_dict[regularise_key(this_string)] = text.count(this_string)
    return np_dict

# add input to output; given dictionaries where key = ngram, value = count (int)
def add_countdict(outputdict, inputdict):
    for k in inputdict.keys():
        if k in outputdict:
            outputdict[k] += inputdict[k]
        else:
            outputdict[k] = inputdict[k]
    return outputdict


# count n-grams >2, given list of dicts, with key referencing the key in the dict that contains the text
def count_nps(list, key):
    np_counts = {}
    for item in list:
        try:
            pt = parsetree(item[key])
            noun_phrases = search('NP', pt)
            #noun_phrases = [np.string for np in noun_phrases]
            this_np_count = count_noun_phrases(noun_phrases, pt.string)
            np_counts = add_countdict(np_counts, this_np_count)
        except TypeError as e:
            print repr(e)
            if 'contract' in item:
                print "Error processing %s." % (item['contract'])
        except KeyError as e:
            print repr(e)
            if 'contract' in item:
                print "Error processing %s." % (item['contract'])
    return np_counts

def remove_low_count_words(inputdict):
    for item in inputdict.keys():
        if inputdict[item] <= 1:
            del inputdict[item]
    return inputdict

def save_countdict_to_csv(dict, filename):
    tuplelist = dict_to_tuple_list(dict)
    tuplelist_to_csv(tuplelist, filename)

def dict_to_tuple_list(dict_of_counts):
    count_list = []
    for k in dict_of_counts.keys():
        count_list.append((k, dict_of_counts[k]))
    return count_list

def tuplelist_to_csv(data, filename):
    # FIXME: should make this output unicode, being lazy..
    normalized_data = []
    for tuple in data:
        normalized_data.append((unicodedata.normalize('NFC',tuple[0]).encode('ascii','ignore'), tuple[1]))
    with open(filename,'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['ngram','count'])
        for row in normalized_data:
            csv_out.writerow(row)

