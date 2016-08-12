from technodeminer.persistence.graph import connect_to_arango, get_technode_graph
from pattern.vector import Model, Document
from pattern.search import search
from pattern.en import parsetree, singularize
from collections import Counter
import unicodedata
import csv
import farmhash

MIN_NGRAM_LENGTH = 3

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


# a/an/the/etc - not news articles!
# assumes lowercase
def remove_articles(str):
    STOPWORDS = ['a', 'an', 'the', 'this']
    if any(str.startswith(stopword) for stopword in STOPWORDS):
        str = " ".join(str.split(" ")[1:])
    return str


def regularise_key(str):
    str = str.lower()
    str = remove_articles(str)
    str = singularize(str)
    return str


# this counts noun phrases in 1 document
# counts ngrams > 2, return as dict
# if it starts with one of the stopwords (articles), require it be 1 word longer
# regularise keys (lowercase + singularize)
def count_noun_phrases(nphrases, text, minlength=MIN_NGRAM_LENGTH):

    np_dict = {}
    for np in nphrases:
        # if NP is long enough
        if len(np.words) >= minlength:
            keystr = regularise_key(np.string)
            if len(keystr.split(" ")) >= minlength: # if still long enough after regularisation?
                np_dict[keystr] = text.count(np.string)
    return np_dict


# add input to output; given dictionaries where key = ngram, value = count (int)
def add_countdict(outputdict, inputdict):
    for k in inputdict.keys():
        if k in outputdict:
            outputdict[k] += inputdict[k]
        else:
            outputdict[k] = inputdict[k]
    return outputdict


# regularise dictionary
def clean_dict(dict):
    for k in dict.keys():
        cleankey = regularise_key(k)
        if k != cleankey:
            if cleankey in dict:
                dict[cleankey] += dict[k]
                del dict[k]
            else:
                dict[cleankey] = dict[k]
                del dict[k]
    return dict


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

# Mmm hash-browns!
def get_hash_for_key(key):
    return str(farmhash.hash64(key.encode('ascii','ignore')))


def dict_to_list_of_dicts(dict_of_counts):
    term_list = []
    for k in dict_of_counts.keys():
        item = {}
        item['count'] = dict_of_counts[k]
        item['term'] = k
        item['_key'] = get_hash_for_key(k)
        term_list.append(item)
    return term_list


# input is a list of dicts
def terms_to_arango(terms):
    db = connect_to_arango()
    col = db.col("tech_terms")
    for term in terms:
        col.create_document(term)


def bootstrap_techterms():
    contract_list = build_contract_list()
    np_counts = count_nps(contract_list[0:500], 'abstract')
    hicounts = remove_low_count_words(np_counts)
    terms = dict_to_list_of_dicts(hicounts)
    terms_to_arango(terms)


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

