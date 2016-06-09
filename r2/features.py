from pattern.en import parsetree
from pattern.search import search

SEMANTIC_PATTERNS = ['JJ NP', 'NN NNS', 'JJ NN NNS']

def terms_in_txt(text, semantic_patterns):
    pt = parsetree(text)
    techterms = set()
    for pattern in SEMANTIC_PATTERNS:
        techterms.add(search(pattern, pt).string)
    return techterms
