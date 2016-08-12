from technodeminer.persistence.graph import connect_to_arango
from technodeminer.similarity.buzzphrases import get_hash_for_key
def get_term_collection():
    db = connect_to_arango()
    return db.col('tech_terms')


def mark_as_known_techterm(term):
    hash = get_hash_for_key(term)
    tech_terms = get_term_collection()
    tech_terms.update_document(hash, {"is_tech": True})


training_is_tech = ["tm-doped fiber laser",
                    "cusnzns solar cell",
                    "multi-beam x-band subarray",
                    "ballistic missile defense system",
                    "solid oxide fuel cell",
                    "digital image correlation",
                    "header compression algorithm",
                    "precision agriculture project",
                    "terahertz imaging system"
                    "split ring resonator"
                    ""

]