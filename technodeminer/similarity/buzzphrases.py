from arango.exceptions import DocumentCreateError
from technodeminer.persistence.graph import connect_to_arango, get_technode_graph
from pattern.vector import Model, Document
from pattern.search import search
from pattern.en import parsetree, singularize
from collections import Counter
import unicodedata
import csv
import farmhash

MIN_NGRAM_LENGTH = 3


# Build list of contracts (dicts)
def bootstrap_keyphrases_contracts():
    db = connect_to_arango()
    graph = get_technode_graph(db)
    col_contracts = db.col('contracts')
    col_keyphrases = db.col('key_phrases')
    contract_list = []
    for r2 in col_contracts.all():
        contract_lite = {}
        if 'contract' in r2:
            contract_lite['contract'] = r2['contract']
        if 'award_title' in r2:
            contract_lite['award_title'] = r2['award_title']
        if 'abstract' in r2:
            contract_lite['abstract'] = r2['abstract']
        contract_lite['_id'] = r2['_id']
        contract_list.append(contract_lite)
    for contract in contract_list[0:500]:
        # process contract
        # extract all noun phrases
        keyphrases = extract_keyphrases_from_doc(contract, 'abstract')
        # take list of keyphrases and create records for each one
        keyphrasedocs = make_keyphrasedocs(keyphrases, contract)
        for kpd in keyphrasedocs:
            try:
                kpd_id = col_keyphrases.create_document(kpd)['_id']
                graph.create_edge("keyphrase_contract_relations", {"keyphrase": kpd['term'], "_from": kpd_id,
                                                                   "_to": contract['_id']})
            except DocumentCreateError: # no need to create duplicate doc unless we want to store extra stuff..
                existing_kpdoc = col_keyphrases[kpd['_key']]
                kpd_id = existing_kpdoc['_id']
                new_list = existing_kpdoc['related_docs'] + kpd['related_docs']
                current_link_count = existing_kpdoc['num_linkedcontracts']
                col_keyphrases.update_document(kpd['_key'], {"related_docs": new_list, "num_linkedcontracts": (current_link_count+1)})
                graph.create_edge("keyphrase_contract_relations", {"keyphrase": kpd['term'], "_from": kpd_id,
                                                                   "_to": contract['_id']})
                pass

                #print "Found existing key %s" % (kpd['_key'])

# Build list of contracts (dicts)
def bootstrap_keyphrases_r2s():
    db = connect_to_arango()
    graph = get_technode_graph(db)
    col_r2s = db.col('r2_exhibits')
    col_keyphrases = db.col('key_phrases')
    r2_list = []
    for r2 in col_r2s.all():
        r2_lite = {}
        if 'program_desc' in r2:
            r2_lite['program_desc'] = r2['program_desc']
        r2_lite['_id'] = r2['_id']
        r2_list.append(r2_lite)
    for r2 in r2_list:
        # process contract
        # extract all noun phrases
        try:
            keyphrases = extract_keyphrases_from_doc(r2, 'program_desc')
            # take list of keyphrases and create records for each one
            keyphrasedocs = make_keyphrasedocs(keyphrases, r2)
            for kpd in keyphrasedocs:
                try:
                    kpd_id = col_keyphrases.create_document(kpd)['_id']
                    graph.create_edge("keyphrase_r2_relations", {"keyphrase": kpd['term'], "_from": kpd_id,
                                                                       "_to": r2['_id']})
                except DocumentCreateError:  # no need to create duplicate doc unless we want to store extra stuff..
                    existing_kpdoc = col_keyphrases[kpd['_key']]
                    kpd_id = existing_kpdoc['_id']
                    new_list = existing_kpdoc['related_docs'] + kpd['related_docs']
                    current_link_count = existing_kpdoc['num_linkedcontracts']
                    col_keyphrases.update_document(kpd['_key'], {"related_docs": new_list,
                                                                 "num_linkedcontracts": (current_link_count + 1)})
                    graph.create_edge("keyphrase_r2_relations", {"keyphrase": kpd['term'], "_from": kpd_id,
                                                                 "_to": r2['_id']})
                    pass
        except TypeError:
            pass
                    # print "Found existing key %s" % (kpd['_key'])


# Mmm hash-browns!
def get_hash_for_key(key):
    return str(farmhash.hash64(key.encode('ascii','ignore')))


def make_keyphrasedocs(phrases, item):
    np_docs = []
    for phrase in phrases:
        np_doc = {}
        np_doc['term'] = phrase
        np_doc['_key'] = get_hash_for_key(phrase)
        np_doc['related_docs'] = []
        np_doc['related_docs'].append(item['_id'])
        np_doc['num_linkedcontracts'] = 1
        np_docs.append(np_doc)
    return np_docs

def extract_keyphrases_from_doc(item, key):
    # build parsetree, extract NP's

    pt = parsetree(item[key])
    noun_phrases = search('NP', pt)
    # convert np matches to unicode list
    noun_phrases = [np.string for np in noun_phrases]
    # remove ones too short, lemmatize, etc..
    cleankeys = regularise_keys(noun_phrases)
    return cleankeys


# a/an/the/etc - not news articles!
# assumes lowercase
def remove_articles(str):
    STOPWORDS = ['a', 'an', 'the', 'this']
    if any(str.startswith(stopword) for stopword in STOPWORDS):
        str = " ".join(str.split(" ")[1:])
    return str

def regularise_keys(keylist):
    trimmed_keys = []
    for key in keylist:
        cleankey = regularise_key(key)
        if len(cleankey.split(" ")) >= MIN_NGRAM_LENGTH:
            trimmed_keys.append(cleankey)
    return trimmed_keys

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


# input is a list of dicts
def terms_to_arango(terms):
    db = connect_to_arango()
    col = db.col("tech_terms")
    for term in terms:
        col.create_document(term)


def bootstrap_techterms():
    contract_list = build_contract_list()
    key_phrases = extract_keyphrases(contract_list[0:500], 'abstract')
    hicounts = remove_low_count_words(np_counts)
    terms = dict_to_list_of_dicts(hicounts)
    terms_to_arango(terms)
