from arango.exceptions import DocumentCreateError
from technodeminer.persistence.graph import connect_to_arango, get_technode_graph
from pattern.search import search
from pattern.en import parsetree, singularize
import farmhash
from spacy.en import English
from textacy import preprocess_text
from technodeminer.config import *

# process an arbitrary document for keyphrases, doc_key is the key of the document (dict) we process for keywords
def process_doc_for_keyphrases(nlp, db, graph, edge_collection, doc_text, doc_id):

    try:
        keyphrases = extract_keyphrases_from_text(doc_text, nlp)
        # process each keyphrase (for each contract)
        store_keyphrases_for_doc(db, graph, edge_collection, keyphrases, doc_id)
    except TypeError as e:
        print repr(e)
        pass
    except UnicodeError as e:
        print repr(e)
        print doc_id
        pass

def store_keyphrases_for_doc(db, graph, edge_collection, keyphrases, doc_id, vetted=False):
    for keyphrase in keyphrases:
        kp_id = put_keyphrase(keyphrase, db, vetted)
        try:
            graph.create_edge(edge_collection, {"keyphrase": keyphrase, "_from": kp_id,
                                                "_to": doc_id})
        except DocumentCreateError as e:  # no need to create duplicate doc unless we want to store stuff like counts..
            print repr(e)
            pass


# process all contracts for keyphrases
def bootstrap_keyphrases_contracts():
    db = connect_to_arango()
    graph = get_technode_graph(db)
    nlp = English()
    col_documents = db.col(CONTRACT_COLLECTION)
    docs_lite = []
    for document in col_documents.all():
        doc_lite = {}
        doc_lite['_id'] = document['_id']
        if 'keywords' in document:
            doc_lite['keywords'] = document['keywords']
        if 'abstract' in document:
            doc_lite['abstract'] = document['abstract']
            docs_lite.append(doc_lite)
    for document in docs_lite:
        process_doc_for_keyphrases(nlp, db, graph, KEYPHRASE_CONTRACT_RELATIONS, document['abstract'], document['_id'])
        if 'keywords' in document:
            store_keyphrases_for_doc(db, graph, KEYPHRASE_CONTRACT_RELATIONS, document['keywords'], document['_id'])

# process all contracts for keyphrases
def bootstrap_keyphrases_solicitations():
    db = connect_to_arango()
    graph = get_technode_graph(db)
    nlp = English()
    col_documents = db.col(SOLICITATION_COLLECTION)
    docs_lite = []
    for document in col_documents.all():
        doc_lite = {}
        doc_lite['_id'] = document['_id']
        if 'keywords' in document:
            doc_lite['keywords'] = document['keywords']
        if 'description' in document:
            doc_lite['description'] = document['description']
            docs_lite.append(doc_lite)
    # FIXME: creating mini-array rather than just straight-iterating over cursor
    # doing it this way to avoid cursor timeout issues, may no longer be needed in arango 3
    for document in docs_lite:
        if 'description' in document:
            process_doc_for_keyphrases(nlp, db, graph, KEYPHRASE_SOLICITATION_RELATIONS, document['description'], document['_id'])
        if 'keywords' in document:
            store_keyphrases_for_doc(db, graph, KEYPHRASE_SOLICITATION_RELATIONS, document['keywords'], document['_id'], vetted=True)



# process all contracts for keyphrases
def bootstrap_keyphrases_r2s():
    db = connect_to_arango()
    graph = get_technode_graph(db)
    nlp = English()
    col_documents = db.col(R2_COLLECTION)
    docs_lite = []
    for document in col_documents.all():
        doc_lite = {}
        doc_lite['_id'] = document['_id']
        if 'program_desc' in document:
            doc_lite['program_desc'] = document['program_desc']
        if 'projects' in document:
            doc_lite['projects'] = document['projects']
        docs_lite.append(doc_lite)
    # FIXME: creating mini-array rather than just straight-iterating over cursor
    # doing it this way to avoid cursor timeout issues, may no longer be needed in arango 3

    for document in docs_lite:
        if 'program_desc' in document:
            process_doc_for_keyphrases(nlp, db, graph, KEYPHRASE_R2_RELATIONS, document['program_desc'], document['_id'])
        if 'projects' in document:
            for project in document['projects']:
                if 'accomp_planned' in document['projects'][project]:
                    # accomps are stored as a list, turn it into a long string.
                    # some are 0-length; for whatever reason
                    if len(document['projects'][project]['accomp_planned']) > 0:
                        accomp_str = "".join(document['projects'][project]['accomp_planned'])
                        process_doc_for_keyphrases(nlp, db, graph, KEYPHRASE_R2_RELATIONS, accomp_str, document['_id'])
                if 'mission_desc' in document['projects'][project]:
                    process_doc_for_keyphrases(nlp, db, graph, KEYPHRASE_R2_RELATIONS,
                                               document['projects'][project]['mission_desc'], document['_id'])

# Create the keyphrase doc (dict) from phrase
def make_keyphrasedoc(phrase, vetted=False):
    kp_doc = {}
    kp_doc['term'] = phrase
    kp_doc['_key'] = get_hash_for_key(phrase)
    if vetted:
        kp_doc['vetted'] = vetted
    return kp_doc


# Put keyphrase into database, return ID (idempotent)
def put_keyphrase(keyphrase, db, vetted=False):
    doc = make_keyphrasedoc(keyphrase, vetted)
    col_keyphrases = db.col(KEYPHRASE_COLLECTION)
    try:
        kpd_id = col_keyphrases.create_document(doc)['_id']
    except DocumentCreateError:
        kpd_id = col_keyphrases[doc['_key']]['_id']
        if vetted:
            col_keyphrases.update_document(doc['_key'], {"vetted": True})
    return kpd_id


# Mmm hash-browns!
def get_hash_for_key(key):
    return str(farmhash.hash64(key.encode('ascii','ignore')))


# where the magic happens (spaCy implementation)
def extract_keyphrases_from_text(text, spacy_en):
    str = preprocess_text(text, fix_unicode=True, lowercase=True, transliterate=True, no_punct=True)
    noun_phrases = [np.text for np in spacy_en(str).noun_chunks]
    # remove ones too short, lemmatize, etc..
    cleankeys = regularise_keys(noun_phrases)
    return cleankeys


# where the magic happens (pattern implementation)
def extract_keyphrases_from_doc_pattern(item, key):
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
    # FIXME: this is english-only (language-specific)
    ARTICLES = ['a', 'an', 'the', 'this']
    if any(str.startswith(article) for article in ARTICLES):
        str = " ".join(str.split(" ")[1:])
    return str

# dedupes too!
def regularise_keys(keylist):
    trimmed_keys = set()
    for key in keylist:
        cleankey = regularise_key(key)
        if len(cleankey.split(" ")) >= MIN_NGRAM_LENGTH:
            trimmed_keys.add(cleankey)
    return list(trimmed_keys)

def regularise_key(str):
    str = remove_articles(str)
    str = singularize(str)
    return str
